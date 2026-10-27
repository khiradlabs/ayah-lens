import Foundation
import MWDATCore
import MWDATDisplay
import Observation

enum PrototypeError: LocalizedError {
    case message(String)
    var errorDescription: String? {
        switch self { case .message(let text): text }
    }
}

@Observable
@MainActor
final class GlassesModel: SessionHardware {
    var status = "Register the glasses to begin."
    var error: String?
    var busy = false
    var registered = false
    var hasDisplayDevice = false
    var displayReady = false
    var listening = false
    var sampleCount = 0
    var decibels = -80.0
    var sampleRate = 0.0
    var selectedIndex = 0
    var recognitionActive = false
    var museActive = false
    var museConfigured = false
    var transcript = ""
    var recognitionStatus = "Manual verse selection"
    var inferenceMilliseconds = 0.0
    var museGapMilliseconds: Double?
    var matcherMilliseconds: Double?
    var lensSendMilliseconds: Double?
    var museLatency = MuseLatencyTrace()
    private(set) var verses: [Verse] = []

    @ObservationIgnored private let microphone = GlassesMicrophone()
    @ObservationIgnored private var displaySelector: AutoDeviceSelector?
    @ObservationIgnored private var deviceDiscoveryTask: Task<Void, Never>?
    @ObservationIgnored private var deviceSession: DeviceSession?
    @ObservationIgnored private var display: Display?
    @ObservationIgnored private var displayToken: AnyListenerToken?
    @ObservationIgnored private var registrationTask: Task<Void, Never>?
    @ObservationIgnored private var sessionErrorTask: Task<Void, Never>?
    @ObservationIgnored private var sessionStateTask: Task<Void, Never>?
    @ObservationIgnored private var deadlineTask: Task<Void, Never>?
    @ObservationIgnored private var operationTask: Task<Void, Never>?
    @ObservationIgnored private let recognizer = OmnilingualEngine()
    @ObservationIgnored private var windows = RecognitionWindows()
    @ObservationIgnored private var recognitionTask: Task<Void, Never>?
    @ObservationIgnored private var recognitionEpoch = UUID()
    @ObservationIgnored private var matchedID: String?
    @ObservationIgnored private let muse = MuseVoiceClient()
    @ObservationIgnored private var museSessionID: UUID?
    @ObservationIgnored private var museContinuation: AsyncStream<MuseAudioChunk>.Continuation?
    @ObservationIgnored private var museSender: Task<Void, Never>?

    var verse: Verse? { verses.indices.contains(selectedIndex) ? verses[selectedIndex] : nil }
    var recognitionSource: String { museActive ? "Muse Voice Transcribe" : "Local Omnilingual fallback" }

    init() {
        museConfigured = (try? MuseCredential.read()) != nil
        do {
            try Wearables.configure()
            displaySelector = AutoDeviceSelector(wearables: Wearables.shared, filter: { $0.supportsDisplay() })
            guard let url = Bundle.main.url(forResource: "verses", withExtension: "json") else {
                throw PrototypeError.message("The attributed verse resource is missing.")
            }
            verses = try JSONDecoder().decode([Verse].self, from: Data(contentsOf: url))
        } catch { self.error = error.localizedDescription }
        if let selector = displaySelector {
            deviceDiscoveryTask = Task { [weak self] in
                for await identifier in selector.activeDeviceStream() {
                    guard let self, !Task.isCancelled else { return }
                    self.hasDisplayDevice = identifier != nil
                    if self.registered && !self.busy && !self.displayReady {
                        self.status = self.hasDisplayDevice
                            ? "Display glasses available. Ready for the lens check."
                            : "Registered. Waiting for the display glasses to connect."
                    }
                }
            }
        }
        registrationTask = Task { [weak self] in
            for await state in Wearables.shared.registrationStateStream() {
                guard let self, !Task.isCancelled else { return }
                self.registered = state == .registered
                if self.registered {
                    self.status = self.hasDisplayDevice
                        ? "Display glasses available. Ready for the lens check."
                        : "Registered. Waiting for the display glasses to connect."
                }
                else if state == .registering { self.status = "Complete the connection in Meta AI." }
                else if self.displayReady || self.listening { self.stop() }
            }
        }
    }

    func register() {
        run {
            try await Wearables.shared.startRegistration()
        }
    }

    func handleURL(_ url: URL) {
        guard URLComponents(url: url, resolvingAgainstBaseURL: false)?.queryItems?.contains(where: { $0.name == "metaWearablesAction" }) == true else { return }
        Task {
            do { _ = try await Wearables.shared.handleUrl(url) }
            catch { self.error = error.localizedDescription }
        }
    }

    func showSelectedVerse() {
        run {
            if !self.displayReady { try await self.startDisplay() }
            else { try await self.sendVerse() }
            self.status = "Selected verse sent. Manual lens check."
        }
    }

    func startCombined() {
        run {
            self.stopHardware()
            self.sampleCount = 0
            try await SessionSequence(hardware: self).start()
            self.status = "Combined check active. Speak while viewing the selected verse."
        }
    }

    func startRecognition() {
        run {
            self.stopHardware()
            self.museGapMilliseconds = nil
            self.status = "Loading Meta Omnilingual on this iPhone…"
            guard let directory = Bundle.main.url(forResource: "Omnilingual", withExtension: nil) else {
                throw PrototypeError.message("The local recognition model is missing. Prepare the model and rebuild.")
            }
            try await self.recognizer.load(directory: directory)
            try Task.checkCancellation()
            self.sampleCount = 0
            self.transcript = ""
            self.matchedID = nil
            self.recognitionActive = true
            self.recognitionStatus = "Listening · waiting for five seconds of audio"
            try await SessionSequence(hardware: self).start()
            self.status = "Live Al-Fatihah recognition active. Recite at a natural pace."
        }
    }

    func startMuse() {
        run { [self] in
            self.stopHardware()
            self.museGapMilliseconds = nil
            self.matcherMilliseconds = nil
            self.lensSendMilliseconds = nil
            self.museLatency = MuseLatencyTrace()
            guard let key = try MuseCredential.read() else {
                throw PrototypeError.message("Muse credentials are not provisioned on this phone yet.")
            }
            self.status = "Connecting to Muse Voice Transcribe…"
            let epoch = self.recognitionEpoch
            let id = try await self.muse.connect(apiKey: key, onTranscript: { [weak self] text in
                Task { @MainActor in
                    guard let self, self.recognitionEpoch == epoch, self.museActive else { return }
                    do { try await self.applyTranscript(text) }
                    catch { self.stop(); self.error = "The Muse verse could not be sent to the lens." }
                }
            }, onFailure: { [weak self] message in
                Task { @MainActor in
                    guard let self, self.recognitionEpoch == epoch else { return }
                    self.stop(); self.error = message
                }
            }, onAudioGap: { [weak self] gap in
                Task { @MainActor in
                    guard let self, self.recognitionEpoch == epoch, self.museActive else { return }
                    self.museGapMilliseconds = gap
                    self.museLatency.gap(gap)
                }
            })
            self.museSessionID = id
            try Task.checkCancellation()
            self.recognitionActive = true
            self.museActive = true
            self.sampleCount = 0
            self.transcript = ""
            self.matchedID = nil
            self.recognitionStatus = "Muse connected · listening for Al-Fatihah"
            let (chunks, continuation) = AsyncStream<MuseAudioChunk>.makeStream(bufferingPolicy: .bufferingOldest(8))
            self.museContinuation = continuation
            let muse = self.muse
            self.museSender = Task { [weak self] in
                do {
                    for await chunk in chunks {
                        try Task.checkCancellation()
                        try await muse.sendAudio(chunk, sessionID: id)
                    }
                } catch is CancellationError { }
                catch {
                    guard let self, self.recognitionEpoch == epoch else { return }
                    self.stop(); self.error = error is MuseError ? error.localizedDescription : "The Muse audio connection failed."
                }
            }
            try await SessionSequence(hardware: self).start()
            self.status = "Muse live recognition active · two-minute test limit"
        }
    }

    private func receiveSamples(_ samples: [Float], sampleRate: Double) {
        if museActive {
            guard displayReady else { return }
            museLatency.audio(at: ProcessInfo.processInfo.systemUptime * 1000)
            if case .dropped = museContinuation?.yield(MuseAudioChunk(samples: samples, sampleRate: sampleRate)) {
                stop()
                error = "Muse could not keep up with live audio. Stopped instead of building a delayed queue."
            }
            return
        }
        guard recognitionActive, displayReady,
              let window = windows.append(samples, sampleRate: sampleRate), recognitionTask == nil else { return }
        guard AudioLevel.measure(window).decibels > -45 else {
            recognitionStatus = "Quiet · holding the current verse"
            return
        }
        let epoch = recognitionEpoch
        let recognizer = recognizer
        recognitionTask = Task { [weak self] in
            let began = ContinuousClock.now
            defer { if self?.recognitionEpoch == epoch { self?.recognitionTask = nil } }
            do {
                let text = try await recognizer.transcribe(window, sampleRate: sampleRate)
                try Task.checkCancellation()
                guard let self, self.recognitionActive, self.recognitionEpoch == epoch else { return }
                let duration = began.duration(to: .now).components
                self.inferenceMilliseconds = Double(duration.seconds) * 1000 + Double(duration.attoseconds) / 1e15
                try await self.applyTranscript(text)
            } catch is CancellationError { }
            catch {
                guard let self, self.recognitionEpoch == epoch else { return }
                self.stop()
                self.error = "Recognition stopped: \(error.localizedDescription)"
            }
        }
    }

    private func applyTranscript(_ text: String) async throws {
        let began = ContinuousClock.now
        if museActive, !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            museLatency.partial(at: ProcessInfo.processInfo.systemUptime * 1000)
        }
        transcript = text
        let candidate = VerseMatcher(verses: verses).match(text, previous: matchedID)
        matcherMilliseconds = elapsedMilliseconds(since: began)
        guard let id = candidate,
              let index = verses.firstIndex(where: { $0.id == id }) else {
            recognitionStatus = "Uncertain · holding the current verse · \(recognitionSource)"
            return
        }
        recognitionStatus = "Matched Al-Fatihah \(id) · \(recognitionSource)"
        if museActive { museLatency.match(at: ProcessInfo.processInfo.systemUptime * 1000) }
        if matchedID != id {
            matchedID = id
            selectedIndex = index
            let sendBegan = ContinuousClock.now
            try await sendVerse()
            lensSendMilliseconds = elapsedMilliseconds(since: sendBegan)
        }
    }

    private func elapsedMilliseconds(since start: ContinuousClock.Instant) -> Double {
        let duration = start.duration(to: .now).components
        return Double(duration.seconds) * 1000 + Double(duration.attoseconds) / 1e15
    }

    func nextVerse() {
        guard !verses.isEmpty else { return }
        selectedIndex = (selectedIndex + 1) % verses.count
        if displayReady { showSelectedVerse() }
    }

    func stop() {
        operationTask?.cancel()
        operationTask = nil
        stopHardware()
        busy = false
        status = "Stopped."
    }

    private func stopHardware() {
        stopDisplay()
        stopAudio()
    }

    func startAudio() async throws {
        status = "Starting glasses microphone…"
        try await microphone.start(onLevel: { [weak self] level in
            Task { @MainActor in
                guard let self, self.listening else { return }
                self.sampleCount += level.sampleCount
                self.decibels = level.decibels
            }
        }, onSamples: { [weak self] samples, rate in
            Task { @MainActor in
                guard let self, self.listening else { return }
                self.receiveSamples(samples, sampleRate: rate)
            }
        })
        try Task.checkCancellation()
        sampleRate = microphone.sampleRate
        listening = true
    }

    func stopAudio() {
        museContinuation?.finish(); museContinuation = nil
        museSender?.cancel(); museSender = nil
        if let id = museSessionID {
            let muse = muse
            Task { await muse.finish(sessionID: id) }
        }
        museSessionID = nil
        museActive = false
        recognitionEpoch = UUID()
        recognitionTask?.cancel()
        recognitionTask = nil
        recognitionActive = false
        recognitionStatus = "Manual verse selection"
        windows = RecognitionWindows()
        matchedID = nil
        listening = false
        microphone.stop()
        decibels = -80
    }

    func startDisplay() async throws {
        guard registered else { throw PrototypeError.message("Register this app with your glasses first.") }
        guard deviceSession == nil else { throw PrototypeError.message("Stop the existing session before starting another.") }
        guard let selector = displaySelector else { throw PrototypeError.message("Display discovery could not be configured.") }
        status = "Waiting for the display glasses…"
        deadlineTask = Task { [weak self] in
            do { try await Task.sleep(for: .seconds(12)) } catch { return }
            guard let self else { return }
            self.error = "Timed out waiting for the glasses display connection."
            self.operationTask?.cancel()
            self.stopHardware()
        }
        defer { deadlineTask?.cancel(); deadlineTask = nil }
        _ = try await DisplayReadiness.firstAvailable(in: selector.activeDeviceStream())
        try Task.checkCancellation()
        status = "Connecting lens…"
        let session = try Wearables.shared.createSession(deviceSelector: selector)
        deviceSession = session
        sessionErrorTask = Task { [weak self] in
            for await failure in session.errorStream() {
                guard let self, !Task.isCancelled else { return }
                self.error = failure.localizedDescription
                self.stopHardware()
            }
        }
        let states = session.stateStream()
        do {
            try session.start()
            var started = false
            for await state in states {
                try Task.checkCancellation()
                if state == .started { started = true; break }
                if state == .stopped { break }
            }
            guard started else { throw PrototypeError.message("The glasses session ended before the display started.") }
            let capability = try session.addDisplay()
            display = capability
            let (displayStates, continuation) = AsyncStream.makeStream(of: DisplayState.self)
            displayToken = capability.statePublisher.listen { continuation.yield($0) }
            capability.start()
            var ready = false
            for await state in displayStates {
                try Task.checkCancellation()
                if state == .started { ready = true; break }
                if state == .stopped { break }
            }
            guard ready else { throw PrototypeError.message("The lens display did not become ready.") }
            displayReady = true
            sessionStateTask = Task { [weak self] in
                for await state in session.stateStream() {
                    guard let self, !Task.isCancelled else { return }
                    if state == .stopped {
                        self.error = "The glasses ended the active session."
                        self.stopHardware()
                        return
                    }
                }
            }
            try await sendVerse()
        } catch {
            stopDisplay()
            throw error
        }
    }

    private func sendVerse() async throws {
        guard let display, displayReady, let verse else { throw PrototypeError.message("No active lens or selected verse.") }
        if recognitionActive && matchedID == nil {
            try await display.send(FlexBox(direction: .column, spacing: 16) {
                MWDATDisplay.Text("Ayah Lens · Al-Fatihah", style: .heading)
                MWDATDisplay.Text("Listening for recitation…", style: .body)
                MWDATDisplay.Text(museActive ? "Muse Voice Transcribe · live audio" : "Local Omnilingual · five-second audio window", style: .meta, color: .secondary)
            }.padding(24))
            return
        }
        try await display.send(
            FlexBox(direction: .column, spacing: 16) {
                MWDATDisplay.Text("Ayah Lens · \(verse.id)", style: .meta, color: .secondary)
                MWDATDisplay.Text(verse.arabic, style: .heading)
                MWDATDisplay.Text(verse.translation, style: .body)
                MWDATDisplay.Text(recognitionActive ? "Pickthall · \(recognitionSource)" : "Pickthall · Manual display check", style: .meta, color: .secondary)
            }.padding(24)
        )
    }

    func stopDisplay() {
        deadlineTask?.cancel()
        sessionErrorTask?.cancel()
        sessionStateTask?.cancel()
        sessionErrorTask = nil
        sessionStateTask = nil
        display?.stop()
        displayToken = nil
        display = nil
        deviceSession?.stop()
        deviceSession = nil
        displayReady = false
    }

    private func run(_ action: @escaping @MainActor () async throws -> Void) {
        guard !busy else { return }
        busy = true
        error = nil
        operationTask = Task { [weak self] in
            guard let self else { return }
            defer { self.busy = false }
            do { try await action() }
            catch is CancellationError { self.stopHardware() }
            catch { self.error = error.localizedDescription; self.stopHardware() }
        }
    }
}
