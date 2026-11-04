import Foundation

@main struct SparkProbe {
    static func main() async throws {
        let client = MuseSparkClient(endpoint: URL(string: CommandLine.arguments[1])!)
        let candidates = [Verse(id: "1:2", arabic: "الحمد لله رب العالمين", translation: ""),
                          Verse(id: "37:182", arabic: "والحمد لله رب العالمين", translation: "")]
        let first = try await client.resolve(transcript: "الحمد لله رب العالمين", candidates: candidates, recentIDs: ["37:181"], apiKey: "synthetic-test-key")
        precondition(first == "37:182")
        print("PASS: actual Spark HTTP client accepted a retrieved ID from the synthetic server")
        do {
            _ = try await client.resolve(transcript: "الحمد لله رب العالمين", candidates: candidates, recentIDs: [], apiKey: "synthetic-test-key")
            fatalError("Out-of-candidate ID must be rejected")
        } catch SparkError.invalidResponse { print("PASS: HTTP response with an unlisted ID rejected") }
        let abstention = try await client.resolve(transcript: "الحمد لله رب العالمين", candidates: candidates, recentIDs: [], apiKey: "synthetic-test-key")
        precondition(abstention == nil)
        print("PASS: synthetic provider abstention preserved")
    }
}
