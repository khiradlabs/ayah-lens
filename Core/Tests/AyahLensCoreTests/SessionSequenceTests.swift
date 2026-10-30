import XCTest
@testable import AyahLensCore

@MainActor
final class SessionSequenceTests: XCTestCase {
    func testAudioStartsBeforeDisplayAndStopReleasesBoth() async throws {
        let hardware = ProbeHardware()
        let sequence = SessionSequence(hardware: hardware)
        try await sequence.start()
        XCTAssertEqual(hardware.events, ["audio.start", "display.start"])
        sequence.stop()
        XCTAssertEqual(hardware.events.suffix(2), ["display.stop", "audio.stop"])
    }

    func testDisplayFailureReleasesAudioAndPreservesFailure() async {
        let hardware = ProbeHardware()
        hardware.failDisplay = true
        let sequence = SessionSequence(hardware: hardware)
        do {
            try await sequence.start()
            XCTFail("Display failure must reach the caller")
        } catch {
            XCTAssertEqual(error as? ProbeFailure, .displayUnavailable)
        }
        XCTAssertEqual(hardware.events, ["audio.start", "display.start", "display.stop", "audio.stop"])
    }
}

enum ProbeFailure: Error { case displayUnavailable }

@MainActor
final class ProbeHardware: SessionHardware {
    var events: [String] = []
    var failDisplay = false
    func startAudio() async throws { events.append("audio.start") }
    func startDisplay() async throws {
        events.append("display.start")
        if failDisplay { throw ProbeFailure.displayUnavailable }
    }
    func stopDisplay() { events.append("display.stop") }
    func stopAudio() { events.append("audio.stop") }
}
