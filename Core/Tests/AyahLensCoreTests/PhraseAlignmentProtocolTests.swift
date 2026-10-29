import XCTest
@testable import AyahLensCore

final class PhraseAlignmentProtocolTests: XCTestCase {
    let verse = Verse(id: "fixture", arabic: "كلمات أولى كلمات ثانية", translation: "First source words. Second source words.")
    func testSparkReceivesSourceWordsAndReturnsOnlyBoundaries() throws {
        let data = try SparkPhraseProtocol.request(verse: verse)
        let body = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
        XCTAssertEqual(body["model"] as? String, "muse-spark-1.3")
        let format = try XCTUnwrap(body["response_format"] as? [String: Any])
        let schema = try XCTUnwrap(format["json_schema"] as? [String: Any])
        XCTAssertEqual(schema["strict"] as? Bool, true)
        XCTAssertLessThan(data.count, 40000)
    }
    func testResponseMustCoverEverySourceWordAndRespectDisplayLimits() throws {
        let content = #"{"segments":[{"arabic_end":2,"english_end":3},{"arabic_end":4,"english_end":6}]}"#
        let response = try JSONSerialization.data(withJSONObject: ["choices": [["finish_reason": "stop", "message": ["content": content]]]])
        XCTAssertEqual(try SparkPhraseProtocol.decision(response: response, verse: verse).cards(for: verse).count, 2)
        let bad = try JSONSerialization.data(withJSONObject: ["choices": [["finish_reason": "length", "message": ["content": content]]]])
        XCTAssertThrowsError(try SparkPhraseProtocol.decision(response: bad, verse: verse))
    }
}
