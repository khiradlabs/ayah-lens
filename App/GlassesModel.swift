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
    var sparkEnabled = false
    var sparkStatus = "Muse Spark ready for ambiguity checks"
    var sparkRequests = 0
    var lastResolution = "Reference match"
    var phraseStatus = "Automatic recitation portions"
    var liveLensFrame: LiveLensFrame?
    var lensMetrics = LensSendMetrics()
    @ObservationIgnored private var liveLensSender: LatestLensSender<LiveLensFrame>?
    var phraseRequests = 0
    var lensPageIndex = 0
    private(set) var lensPages: [LensPage] = []
    var transcript = ""
    var recognitionStatus = "Manual verse selection"
    var inferenceMilliseconds = 0.0
    var museGapMilliseconds: Double?
    var matcherMilliseconds: Double?
    var lensSendMilliseconds: Double?
    var museLatency = MuseLatencyTrace()
    var streamTrace = MuseStreamTrace()
    @ObservationIgnored private var lastTraceWrite = 0.0
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
    @ObservationIgnored private let quran = QuranRecognitionEngine()
    @ObservationIgnored private let spark = MuseSparkClient()
    @ObservationIgnored private let portionEngine = RecitationPortionEngine()
    @ObservationIgnored private let phraseClient = MusePhraseClient()
    @ObservationIgnored private var phraseTask: Task<Void, Never>?
    @ObservationIgnored private var phraseAttempted: Set<String> = []
    @ObservationIgnored private var phraseCache: [String: PhraseAlignment] = [:]
    @ObservationIgnored private var sparkGate = SparkGate()
    @ObservationIgnored private var sparkTask: Task<Void, Never>?
    @ObservationIgnored private var sparkRequestID = UUID()
    @ObservationIgnored private var transcriptTask: Task<Void, Never>?
    @ObservationIgnored private var pendingTranscript: String?
    @ObservationIgnored private var latestCandidateIDs: Set<String> = []
    @ObservationIgnored private var decisionRevision = 0
    @ObservationIgnored private var recentIDs: [String] = []
    @ObservationIgnored private var versePositions: [String: Int] = [:]

    var verse: Verse? { verses.indices.contains(selectedIndex) ? verses[selectedIndex] : nil }
    var recognitionSource: String { museActive ? "Muse Voice Transcribe" : "Local Omnilingual fallback" }
    var hasLiveMatch: Bool { matchedID != nil }

    init() {
        museConfigured = (try? MuseCredential.read()) != nil
        do {
            try Wearables.configure()
            displaySelector = AutoDeviceSelector(wearables: Wearables.shared, filter: { $0.supportsDisplay() })
            guard let url = Bundle.main.url(forResource: "verses", withExtension: "json") else {
                throw PrototypeError.message("The attributed verse resource is missing.")
            }
            verses = try JSONDecoder().decode([Verse].self, from: Data(contentsOf: url))
            versePositions = Dictionary(uniqueKeysWithValues: verses.enumerated().map { ($0.element.id, $0.offset) })
            if let first = verses.first { lensPages = VersePagination.pages(for: first) }
            loadPhraseCache()
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
            await self.portionEngine.reset()
            self.phraseAttempted.removeAll(); self.phraseRequests = 0
            self.liveLensFrame = nil; self.lensMetrics = LensSendMetrics()
            self.status = "Preparing the complete Quran index…"
            await self.quran.prepare(verses: self.verses)
            try Task.checkCancellation()
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
            self.status = "Complete-Quran local recognition active. Recite at a natural pace."
        }
    }

    func startMuse() {
        run { [self] in
            self.stopHardware()
            self.museGapMilliseconds = nil
            self.matcherMilliseconds = nil
            self.lensSendMilliseconds = nil
            self.museLatency = MuseLatencyTrace()
            self.streamTrace = MuseStreamTrace()
            self.lastTraceWrite = 0
            self.sparkGate = SparkGate()
            self.sparkRequests = 0
            self.sparkStatus = "Muse Spark waiting for ambiguous evidence"
            self.lastResolution = "Reference match"
            guard let key = try MuseCredential.read() else {
                throw PrototypeError.message("Muse credentials are not provisioned on this phone yet.")
            }
            await self.portionEngine.reset()
            self.phraseAttempted.removeAll(); self.phraseRequests = 0
            self.liveLensFrame = nil; self.lensMetrics = LensSendMetrics()
            self.status = "Preparing the complete Quran index…"
            await self.quran.prepare(verses: self.verses)
            try Task.checkCancellation()
            self.status = "Connecting to Muse Voice Transcribe…"
            let epoch = self.recognitionEpoch
            let id = try await self.muse.connect(apiKey: key, onTranscript: { [weak self] text in
                Task { @MainActor in
                    guard let self, self.recognitionEpoch == epoch, self.museActive else { return }
                    self.queueTranscript(text)
                }
            }, onFailure: { [weak self] message in
                Task { @MainActor in
                    guard let self, self.recognitionEpoch == epoch else { return }
                    self.stop(); self.error = message
                }
            }, onAudioGap: { [weak self] gap in
                Task { @MainActor in
                    guard let self, self.recognitionEpoch == epoch, self.museActive else { return }
                    self.streamTrace.providerUpdate(at: ProcessInfo.processInfo.systemUptime)
                    self.persistStreamTrace()
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
            self.recognitionStatus = "Muse connected · identifying the recited passage"
            let (chunks, continuation) = AsyncStream<MuseAudioChunk>.makeStream(bufferingPolicy: .bufferingOldest(8))
            self.museContinuation = continuation
            let muse = self.muse
            self.museSender = Task { [weak self] in
                do {
                    for await chunk in chunks {
                        try Task.checkCancellation()
                        try await muse.sendAudio(chunk, sessionID: id)
                        guard let self, self.recognitionEpoch == epoch else { return }
                        self.streamTrace.sent(samples: chunk.samples.count, rate: chunk.sampleRate, at: ProcessInfo.processInfo.systemUptime)
                        self.persistStreamTrace()
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

    private func queueTranscript(_ text: String) {
        streamTrace.transcript(characters: text.count, at: ProcessInfo.processInfo.systemUptime)
        persistStreamTrace(force: true)
        transcript = text
        if !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            museLatency.partial(at: ProcessInfo.processInfo.systemUptime * 1000)
        }
        pendingTranscript = text
        guard transcriptTask == nil else { return }
        let epoch = recognitionEpoch
        transcriptTask = Task { [weak self] in
            guard let self else { return }
            defer { if self.recognitionEpoch == epoch { self.transcriptTask = nil } }
            do {
                while let latest = self.pendingTranscript, self.recognitionEpoch == epoch {
                    self.pendingTranscript = nil
                    try Task.checkCancellation()
                    try await self.applyTranscript(latest)
                }
            } catch is CancellationError { }
            catch {
                guard self.recognitionEpoch == epoch else { return }
                self.stop(); self.error = "The recognized verse could not be sent to the lens."
            }
        }
    }

    private func persistStreamTrace(force: Bool = false) {
        let now = ProcessInfo.processInfo.systemUptime
        guard force || now - lastTraceWrite >= 1 else { return }
        lastTraceWrite = now
        do {
            let snapshot = try JSONSerialization.jsonObject(with: JSONEncoder().encode(streamTrace.snapshot(at: now)))
            let record: [String: Any] = [
                "version": Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "unknown",
                "build": Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") as? String ?? "unknown",
                "microphoneSamples": sampleCount, "displayReady": displayReady,
                "museActive": museActive, "hasVerseMatch": matchedID != nil,
                "sparkRequests": sparkRequests, "phraseRequests": phraseRequests,
                "lensPortion": lensPageIndex, "lensPortions": lensPages.count,
                "lensDelivery": try JSONSerialization.jsonObject(with: JSONEncoder().encode(lensMetrics)), "stream": snapshot
            ]
            let url = try FileManager.default.url(for: .libraryDirectory, in: .userDomainMask, appropriateFor: nil, create: true)
                .appendingPathComponent("muse-diagnostics.json")
            try JSONSerialization.data(withJSONObject: record, options: [.sortedKeys]).write(to: url, options: .atomic)
            try FileManager.default.setAttributes([.posixPermissions: 0o600], ofItemAtPath: url.path)
        } catch { /* Diagnostics must not interrupt live recitation. */ }
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
        let epoch = recognitionEpoch
        if museActive, !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            museLatency.partial(at: ProcessInfo.processInfo.systemUptime * 1000)
        }
        if !museActive { transcript = text }
        let result = await quran.retrieve(text, previous: matchedID)
        try Task.checkCancellation()
        guard recognitionEpoch == epoch, recognitionActive else { return }
        matcherMilliseconds = elapsedMilliseconds(since: began)
        latestCandidateIDs = Set(result.candidates.map(\.id))
        if let id = result.matchedID {
            decisionRevision += 1
            sparkTask?.cancel(); sparkTask = nil; sparkRequestID = UUID()
            sparkStatus = "Muse Spark idle · reference matched"
            try await acceptMatch(id, resolution: "Reference match", text: text)
            return
        }
        if let current = matchedID { try await updateLivePortion(id: current, text: text) }
        recognitionStatus = "Identifying passage · holding the last verified verse"
        guard museActive, sparkEnabled, result.sparkEligible, sparkTask == nil,
              sparkGate.reserve(transcript: text, candidateIDs: result.candidates.map(\.id), previous: matchedID,
                                at: ProcessInfo.processInfo.systemUptime),
              let key = try MuseCredential.read() else { return }
        sparkRequests = sparkGate.requests
        sparkStatus = "Muse Spark checking \(result.candidates.count) candidates · \(sparkRequests)/3"
        let revision = decisionRevision
        let requestID = UUID()
        sparkRequestID = requestID
        let recent = recentIDs
        let spark = spark
        sparkTask = Task { [weak self] in
            defer { if self?.sparkRequestID == requestID { self?.sparkTask = nil } }
            do {
                let selected = try await spark.resolve(transcript: text, candidates: result.candidates, recentIDs: recent, apiKey: key)
                try Task.checkCancellation()
                guard let self, self.recognitionEpoch == epoch, self.decisionRevision == revision else { return }
                guard let id = selected else { self.sparkStatus = "Muse Spark abstained · waiting for more evidence"; return }
                guard SparkGate.canApply(requested: text, latest: self.transcript, selectedID: id, latestCandidateIDs: self.latestCandidateIDs) else {
                    self.sparkStatus = "Muse Spark result superseded by newer evidence"; return
                }
                self.sparkStatus = "Muse Spark selected \(id)"
                self.decisionRevision += 1
                try await self.acceptMatch(id, resolution: "Muse Spark selection", text: self.transcript)
            } catch is CancellationError { }
            catch {
                guard let self, self.recognitionEpoch == epoch, self.sparkRequestID == requestID else { return }
                self.sparkStatus = "Muse Spark unavailable · waiting for a reference match"
            }
        }
    }

    private func acceptMatch(_ id: String, resolution: String, text: String) async throws {
        guard let index = versePositions[id] else { return }
        recognitionStatus = "Matched Quran \(id) · \(resolution)"
        if museActive { museLatency.match(at: ProcessInfo.processInfo.systemUptime * 1000) }
        let changedVerse = matchedID != id
        if changedVerse { recentIDs = Array((recentIDs + [id]).suffix(3)) }
        matchedID = id; lastResolution = resolution; selectedIndex = index
        try await updateLivePortion(id: id, text: text, force: changedVerse)
        preparePhraseAlignment(for: verses[index])
    }

    private func updateLivePortion(id: String, text: String, force: Bool = false) async throws {
        guard let position = versePositions[id] else { return }
        let epoch = recognitionEpoch
        let result = await portionEngine.update(verse: verses[position], transcript: text, alignment: phraseCache[id])
        try Task.checkCancellation()
        guard recognitionActive, recognitionEpoch == epoch, matchedID == id else { return }
        lensPages = result.cards; lensPageIndex = result.index
        phraseStatus = result.paired ? "Following part \(result.index + 1)/\(result.cards.count) · Arabic + Pickthall"
            : "Following Arabic part \(result.index + 1)/\(result.cards.count) · full translation on phone"
        if force || result.changed {
            try await sendVerse()
        }
    }

    private func loadPhraseCache() {
        var urls: [URL] = []
        if let bundled = Bundle.main.url(forResource: "phrase-alignments", withExtension: "json") { urls.append(bundled) }
        if let library = FileManager.default.urls(for: .libraryDirectory, in: .userDomainMask).first {
            urls.append(library.appendingPathComponent("phrase-alignments.json"))
        }
        for url in urls {
            guard let data = try? Data(contentsOf: url), let plans = try? JSONDecoder().decode([PhraseAlignment].self, from: data) else { continue }
            for plan in plans {
                guard let index = versePositions[plan.verseID], (try? plan.cards(for: verses[index])) != nil else { continue }
                phraseCache[plan.verseID] = plan
            }
        }
    }

    private func preparePhraseAlignment(for verse: Verse) {
        guard museActive, sparkEnabled, phraseCache[verse.id] == nil,
              verse.arabic.count > 56 || verse.translation.count > 100,
              phraseTask == nil, phraseRequests < 3, !phraseAttempted.contains(verse.id),
              let key = try? MuseCredential.read() else { return }
        phraseAttempted.insert(verse.id); phraseRequests += 1
        let epoch = recognitionEpoch
        let client = phraseClient
        phraseTask = Task { [weak self] in
            defer { if self?.recognitionEpoch == epoch { self?.phraseTask = nil } }
            do {
                let plan = try await client.align(verse: verse, apiKey: key)
                try Task.checkCancellation()
                guard let self, self.recognitionEpoch == epoch else { return }
                self.phraseCache[verse.id] = plan
                if let url = FileManager.default.urls(for: .libraryDirectory, in: .userDomainMask).first?.appendingPathComponent("phrase-alignments.json"),
                   let data = try? JSONEncoder().encode(Array(self.phraseCache.values)) {
                    try? data.write(to: url, options: .atomic)
                    try? FileManager.default.setAttributes([.posixPermissions: 0o600], ofItemAtPath: url.path)
                }
                if self.matchedID == verse.id {
                    do { try await self.updateLivePortion(id: verse.id, text: self.transcript) }
                    catch {
                        self.stop()
                        self.error = "The paired portion could not be sent to the lens."
                    }
                }
            } catch is CancellationError { }
            catch { /* Keep automatic Arabic following when source alignment is unavailable. */ }
        }
    }

    private func elapsedMilliseconds(since start: ContinuousClock.Instant) -> Double {
        let duration = start.duration(to: .now).components
        return Double(duration.seconds) * 1000 + Double(duration.attoseconds) / 1e15
    }

    func nextVerse() {
        guard !verses.isEmpty else { return }
        selectedIndex = (selectedIndex + 1) % verses.count
        lensPageIndex = 0
        lensPages = VersePagination.pages(for: verses[selectedIndex])
        if displayReady { showSelectedVerse() }
    }

    func stepLensPage(_ delta: Int) {
        guard !recognitionActive, displayReady, lensPages.count > 1 else { return }
        run {
            self.lensPageIndex = (self.lensPageIndex + delta + self.lensPages.count) % self.lensPages.count
            try await self.sendVerse()
        }
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
        if museActive {
            sparkStatus = "Muse Spark stopped"
            persistStreamTrace(force: true)
        }
        phraseTask?.cancel(); phraseTask = nil
        transcriptTask?.cancel(); transcriptTask = nil; pendingTranscript = nil
        sparkTask?.cancel(); sparkTask = nil; sparkRequestID = UUID()
        decisionRevision += 1
        latestCandidateIDs.removeAll(); recentIDs.removeAll()
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
                MWDATDisplay.Text("Ayah Lens · Quran", style: .heading)
                MWDATDisplay.Text("Listening for recitation…", style: .body)
                MWDATDisplay.Text(museActive ? "Muse Voice Transcribe · live audio" : "Local Omnilingual · five-second audio window", style: .meta, color: .secondary)
            }.padding(24))
            return
        }
        guard lensPages.indices.contains(lensPageIndex) else { throw PrototypeError.message("The lens page is unavailable.") }
        let page = lensPages[lensPageIndex]
        if recognitionActive {
            guard let frame = LensReadingWindow.frame(verseID: verse.id, cards: lensPages, index: lensPageIndex) else { return }
            liveLensFrame = frame
            if liveLensSender == nil {
                let epoch = recognitionEpoch
                liveLensSender = LatestLensSender<LiveLensFrame>(send: { [weak self] frame in
                    guard let self, self.recognitionEpoch == epoch, self.displayReady else { throw CancellationError() }
                    try await display.send(FlexBox(direction: .column, spacing: 8) {
                        MWDATDisplay.Text(frame.header, style: .meta, color: .secondary)
                        if let arabic = frame.page.arabic { MWDATDisplay.Text(arabic, style: .body) }
                        if let english = frame.page.translation { MWDATDisplay.Text(english, style: .body) }
                        else { MWDATDisplay.Text("Translation on phone", style: .meta, color: .secondary) }
                    }.padding(12))
                }, onFailure: { [weak self] _ in
                    guard let self, self.recognitionEpoch == epoch else { return }
                    self.stop()
                    self.error = "The current reading window could not be sent to the lens."
                }, onMetrics: { [weak self] metrics in
                    guard let self, self.recognitionEpoch == epoch else { return }
                    self.lensMetrics = metrics
                    self.lensSendMilliseconds = metrics.sdkMilliseconds
                    self.persistStreamTrace()
                })
            }
            liveLensSender?.enqueue(frame)
            return
        }
        try await display.send(
            FlexBox(direction: .column, spacing: 16) {
                MWDATDisplay.Text("Ayah Lens · \(verse.id) · \(lensPageIndex + 1)/\(lensPages.count)", style: .meta, color: .secondary)
                if !page.label.isEmpty { MWDATDisplay.Text(page.label, style: .meta, color: .secondary) }
                if let arabic = page.arabic { MWDATDisplay.Text(arabic, style: page.translation == nil ? .body : .heading) }
                if let translation = page.translation { MWDATDisplay.Text(translation, style: .body) }
                MWDATDisplay.Text(recognitionActive ? "Pickthall · \(lastResolution)" : "Pickthall · Manual display check", style: .meta, color: .secondary)
                if lensPages.count > 1 {
                    ButtonGroup {
                        MWDATDisplay.Button(label: "Previous", onClick: { @Sendable [weak self] in
                            Task { @MainActor in self?.stepLensPage(-1) }
                        })
                        MWDATDisplay.Button(label: "Next", onClick: { @Sendable [weak self] in
                            Task { @MainActor in self?.stepLensPage(1) }
                        })
                    }
                }
            }.padding(24)
        )
    }

    func stopDisplay() {
        liveLensSender?.stop(); liveLensSender = nil
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
