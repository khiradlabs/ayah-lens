import XCTest
@testable import AyahLensCore

final class SparkTests: XCTestCase {
    let candidates = [Verse(id: "1:2", arabic: "الحمد لله رب العالمين", translation: ""),
                      Verse(id: "37:182", arabic: "والحمد لله رب العالمين", translation: "")]

    func testRequestUsesStandardMuseAndStrictSmallIDSchema() throws {
        let data = try SparkProtocol.request(transcript: "الحمد لله رب العالمين", candidates: candidates, recentIDs: ["37:181"])
        let request = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
        XCTAssertEqual(request["model"] as? String, "muse-spark-1.3")
        let format = try XCTUnwrap(request["response_format"] as? [String: Any])
        let schema = try XCTUnwrap(format["json_schema"] as? [String: Any])
        XCTAssertEqual(schema["strict"] as? Bool, true)
        let body = try XCTUnwrap(schema["schema"] as? [String: Any])
        let properties = try XCTUnwrap(body["properties"] as? [String: [String: Any]])
        XCTAssertEqual(Set(properties["verse_id"]?["enum"] as? [String] ?? []), ["1:2", "37:182", "abstain"])
        XCTAssertLessThanOrEqual(data.count, 16000)
    }

    func response(_ id: String, finish: String = "stop") throws -> Data {
        let content = String(decoding: try JSONSerialization.data(withJSONObject: ["verse_id": id]), as: UTF8.self)
        return try JSONSerialization.data(withJSONObject: ["choices": [["finish_reason": finish, "message": ["content": content]]]])
    }

    func testOnlyRetrievedIDsMayBeAppliedAndAbstentionRemainsEmpty() throws {
        XCTAssertEqual(try SparkProtocol.decision(response: response("37:182"), allowedIDs: ["1:2", "37:182"]), "37:182")
        XCTAssertNil(try SparkProtocol.decision(response: response("abstain"), allowedIDs: ["1:2"]))
        XCTAssertThrowsError(try SparkProtocol.decision(response: response("999:999"), allowedIDs: ["1:2"]))
        XCTAssertThrowsError(try SparkProtocol.decision(response: response("1:2", finish: "length"), allowedIDs: ["1:2"]))
    }

    func testCallsAreDeduplicatedThrottledAndCapped() {
        var gate = SparkGate()
        XCTAssertTrue(gate.reserve(transcript: "first fragment", candidateIDs: ["1:2", "37:182"], previous: nil, at: 0))
        XCTAssertFalse(gate.reserve(transcript: "first fragment", candidateIDs: ["1:2", "37:182"], previous: nil, at: 3))
        XCTAssertFalse(gate.reserve(transcript: "second fragment", candidateIDs: ["1:2", "37:182"], previous: nil, at: 1))
        XCTAssertTrue(gate.reserve(transcript: "second fragment", candidateIDs: ["1:2", "37:182"], previous: nil, at: 3))
        XCTAssertTrue(gate.reserve(transcript: "third fragment", candidateIDs: ["1:2", "37:182"], previous: nil, at: 6))
        XCTAssertFalse(gate.reserve(transcript: "fourth fragment", candidateIDs: ["1:2", "37:182"], previous: nil, at: 9))
        XCTAssertEqual(gate.requests, 3)
    }

    func testStaleOrNoLongerRetrievedDecisionIsDiscarded() {
        XCTAssertTrue(SparkGate.canApply(requested: "الحمد لله", latest: "الحمد لله رب العالمين", selectedID: "1:2", latestCandidateIDs: ["1:2"]))
        XCTAssertFalse(SparkGate.canApply(requested: "الحمد لله", latest: "قل هو الله احد", selectedID: "1:2", latestCandidateIDs: ["1:2"]))
        XCTAssertFalse(SparkGate.canApply(requested: "الحمد لله", latest: "الحمد لله رب العالمين", selectedID: "999:999", latestCandidateIDs: ["1:2"]))
    }
}
