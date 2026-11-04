import Foundation
@main struct PreparePhraseAlignments {
    static func main() async throws {
        let live = CommandLine.arguments.contains("--live")
        let rows = try JSONDecoder().decode([Verse].self, from: Data(contentsOf: URL(fileURLWithPath: "App/Resources/verses.json")))
        var plans: [PhraseAlignment] = []
        let destination = URL(fileURLWithPath: "App/Resources/phrase-alignments.json")
        if let data = try? Data(contentsOf: destination), let existing = try? JSONDecoder().decode([PhraseAlignment].self, from: data) { plans = existing }
        for id in ["2:102", "73:20", "2:255"] {
            let verse = rows.first { $0.id == id }!
            let request = try SparkPhraseProtocol.request(verse: verse)
            if plans.contains(where: { $0.verseID == id && (try? $0.cards(for: verse)) != nil }) {
                print("CACHE: validated paired source portions for \(id)"); continue
            }
            guard live else { print("PREFLIGHT: \(id) request \(request.count) bytes; no API call"); continue }
            do {
                let began = ContinuousClock.now
                let plan = try await MusePhraseClient().align(verse: verse, apiKey: ProcessInfo.processInfo.environment["META_API_KEY"] ?? "")
                let cards = try plan.cards(for: verse)
                plans.removeAll { $0.verseID == id }; plans.append(plan)
                let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
                try encoder.encode(plans).write(to: destination, options: .atomic)
                print("PASS: \(id) · \(cards.count) paired source portions · \(began.duration(to: .now))")
            } catch {
                print("FAIL: \(id) provider call or boundary validation failed; no automatic retry")
                Foundation.exit(1)
            }
        }
    }
}
