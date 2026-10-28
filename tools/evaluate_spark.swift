import Foundation

// Synthetic transcript comparison. --live permits exactly three provider requests.
@main struct SparkEvaluation {
    static func main() async throws {
        let live = CommandLine.arguments.contains("--live")
        let key = ProcessInfo.processInfo.environment["META_API_KEY"] ?? ""
        if live && key.isEmpty { throw SparkError.invalidRequest }
        let rows = try JSONDecoder().decode([Verse].self, from: Data(contentsOf: URL(fileURLWithPath: "App/Resources/verses.json")))
        let index = QuranIndex(verses: rows)
        let cases: [(name: String, text: String, expected: String?)] = [
            ("noisy-guidance-request", "اهدنا صراط المستقيم", "1:6"),
            ("shared-praise-without-context", "والحمد لله رب العالمين", nil),
            ("shared-opening-without-context", "الله لا اله الا هو الحي القيوم", nil)
        ]
        var results: [[String: Any]] = []
        for item in cases {
            let reference = index.retrieve(item.text, previous: nil)
            guard reference.matchedID == nil, reference.candidates.count > 1 else { throw SparkError.invalidRequest }
            let body = try SparkProtocol.request(transcript: item.text, candidates: reference.candidates, recentIDs: [])
            var record: [String: Any] = ["case": item.name, "expected": item.expected as Any? ?? NSNull(),
                "matcher": NSNull(), "candidate_ids": reference.candidates.map(\.id),
                "app_spark_eligible": reference.sparkEligible, "request_bytes": body.count]
            if live {
                let start = ContinuousClock.now
                do {
                    let decision = try await MuseSparkClient().resolve(transcript: item.text, candidates: reference.candidates, recentIDs: [], apiKey: key)
                    let elapsed = start.duration(to: .now).components
                    record["spark"] = decision as Any? ?? NSNull()
                    record["correct"] = decision == item.expected
                    record["seconds"] = Double(elapsed.seconds) + Double(elapsed.attoseconds) / 1e18
                } catch {
                    record["error"] = "Provider request or validation failed; no automatic retry"
                    results.append(record)
                    emit(results, live: live)
                    Foundation.exit(1)
                }
            }
            results.append(record)
        }
        emit(results, live: live)
    }
    static func emit(_ results: [[String: Any]], live: Bool) {
        let object: [String: Any] = ["mode": live ? "live-provider" : "offline-preflight", "model": "muse-spark-1.3", "synthetic_text_only": true, "cases": results]
        let data = try! JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
        print(String(decoding: data, as: UTF8.self))
    }
}
