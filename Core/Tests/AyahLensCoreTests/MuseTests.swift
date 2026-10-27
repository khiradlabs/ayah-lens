import XCTest
@testable import AyahLensCore

final class MuseTests: XCTestCase {
    func testHandshakeSelectsMuseArabicAndCumulativeRealtimePCM() throws {
        let data = try MuseProtocol.handshake(apiKey: "synthetic-test-key")
        let object = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
        XCTAssertEqual(object["model"] as? String, "muse-voice-transcribe-1.0")
        XCTAssertEqual(object["audioEncoding"] as? String, "PCM_24KHZ")
        XCTAssertEqual(object["partialMode"] as? String, "CUMULATIVE")
        XCTAssertEqual(object["languageBias"] as? [String], ["Arabic"])
        XCTAssertEqual(object["emitAudioProgress"] as? Bool, true)
        XCTAssertEqual((object["authorization"] as? [String: String])?["accessToken"], "Bearer synthetic-test-key")
    }

    func testCumulativePartialsReplaceRatherThanAppendAndLateTurnIsIgnored() throws {
        var state = MuseTranscriptState()
        _ = try state.consume(#"{"type":"speechStart","turnId":1}"#)
        XCTAssertEqual(try state.consume(#"{"type":"transcript","transcript":"الحمد"}"#), "الحمد")
        XCTAssertEqual(try state.consume(#"{"type":"transcript","transcript":"الحمد لله"}"#), "الحمد لله")
        _ = try state.consume(#"{"type":"speechStart","turnId":2}"#)
        XCTAssertNil(try state.consume(#"{"type":"speechComplete","turnId":1,"transcript":"old turn"}"#))
        XCTAssertEqual(try state.consume(#"{"type":"speechComplete","turnId":2,"transcript":"الرحمن الرحيم"}"#), "الرحمن الرحيم")
        XCTAssertNil(try state.consume(#"{"type":"futureEvent"}"#))
    }

    func testProviderErrorDoesNotBecomeRecitationText() {
        var state = MuseTranscriptState()
        XCTAssertThrowsError(try state.consume(#"{"type":"error","message":"synthetic provider error"}"#))
    }

    func testPCMEncoderProducesMonoInt16AndResamplesContinuousChunks() throws {
        for rate in [16000.0, 24000.0, 48000.0] {
            let encoder = MusePCMEncoder()
            var bytes = Data()
            for _ in 0..<10 {
                bytes.append(try encoder.encode([Float](repeating: 0.25, count: Int(rate / 10)), sampleRate: rate))
            }
            XCTAssertEqual(Double(bytes.count / 2), 24000, accuracy: 240)
            XCTAssertEqual(bytes.count % 2, 0)
        }
    }

    func testInvalidPCMDoesNotReachMuse() {
        let encoder = MusePCMEncoder()
        XCTAssertThrowsError(try encoder.encode([.nan], sampleRate: 24000))
        XCTAssertThrowsError(try encoder.encode([0], sampleRate: 0))
    }

    func testMuseProcessingGapUsesSentAudioAndRejectsInvalidProgress() {
        XCTAssertEqual(MuseAudioProgress.gapMilliseconds(sentBytes: 48000, processedMilliseconds: 400), 600)
        XCTAssertEqual(MuseAudioProgress.gapMilliseconds(sentBytes: 48000, processedMilliseconds: 1200), 0)
        XCTAssertNil(MuseAudioProgress.gapMilliseconds(sentBytes: 48000, processedMilliseconds: -1))
    }
}
