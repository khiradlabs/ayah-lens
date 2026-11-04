@MainActor
public protocol SessionHardware: AnyObject {
    func startAudio() async throws
    func startDisplay() async throws
    func stopDisplay()
    func stopAudio()
}

@MainActor
public final class SessionSequence {
    private let hardware: any SessionHardware
    public init(hardware: any SessionHardware) { self.hardware = hardware }
    public func start() async throws {
        try await hardware.startAudio()
        do {
            try await hardware.startDisplay()
        } catch {
            stop()
            throw error
        }
    }
    public func stop() {
        hardware.stopDisplay()
        hardware.stopAudio()
    }
}
