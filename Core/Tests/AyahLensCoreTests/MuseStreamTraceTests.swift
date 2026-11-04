import XCTest
@testable import AyahLensCore

final class MuseStreamTraceTests: XCTestCase {
    func testTraceSeparatesAudioSendProviderResponseAndTranscript() {
        var trace = MuseStreamTrace()
        trace.sent(samples: 2400, rate: 24000, at: 10)
        trace.sent(samples: 4800, rate: 48000, at: 11)
        trace.providerUpdate(at: 12)
        trace.transcript(characters: 22, at: 13)
        let snapshot = trace.snapshot(at: 20)
        XCTAssertEqual(snapshot.sentBatches, 2)
        XCTAssertEqual(snapshot.sentAudioSeconds, 0.2, accuracy: 0.0001)
        XCTAssertEqual(snapshot.providerUpdates, 1)
        XCTAssertEqual(snapshot.transcriptUpdates, 1)
        XCTAssertEqual(snapshot.transcriptCharacters, 22)
        XCTAssertEqual(snapshot.audioSendAgeSeconds, 9)
        XCTAssertEqual(snapshot.providerAgeSeconds, 8)
        XCTAssertEqual(snapshot.transcriptAgeSeconds, 7)
    }

    func testMissingEventsStayUnknownAndSnapshotContainsNoTranscriptOrCredential() throws {
        let snapshot = MuseStreamTrace().snapshot(at: 20)
        XCTAssertNil(snapshot.audioSendAgeSeconds)
        XCTAssertNil(snapshot.providerAgeSeconds)
        XCTAssertNil(snapshot.transcriptAgeSeconds)
        let object = try XCTUnwrap(JSONSerialization.jsonObject(with: JSONEncoder().encode(snapshot)) as? [String: Any])
        XCTAssertEqual(Set(object.keys), ["sentBatches", "sentAudioSeconds", "providerUpdates", "transcriptUpdates", "transcriptCharacters"])
    }
}
