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

struct Verse: Decodable, Identifiable {
    let id: String
    let arabic: String
    let translation: String
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

    var verse: Verse? { verses.indices.contains(selectedIndex) ? verses[selectedIndex] : nil }

    init() {
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
        try await microphone.start { [weak self] level in
            Task { @MainActor in
                guard let self, self.listening else { return }
                self.sampleCount += level.sampleCount
                self.decibels = level.decibels
            }
        }
        try Task.checkCancellation()
        sampleRate = microphone.sampleRate
        listening = true
    }

    func stopAudio() {
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
        try await display.send(
            FlexBox(direction: .column, spacing: 16) {
                MWDATDisplay.Text("Ayah Lens · \(verse.id)", style: .meta, color: .secondary)
                MWDATDisplay.Text(verse.arabic, style: .heading)
                MWDATDisplay.Text(verse.translation, style: .body)
                MWDATDisplay.Text("Pickthall · Manual display check", style: .meta, color: .secondary)
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
