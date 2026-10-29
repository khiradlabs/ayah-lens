import Foundation

@main struct PortionProbe {
    static func main() async throws {
        let rows = try JSONDecoder().decode([Verse].self, from: Data(contentsOf: URL(fileURLWithPath: "App/Resources/verses.json")))
        let plans = try JSONDecoder().decode([PhraseAlignment].self, from: Data(contentsOf: URL(fileURLWithPath: "App/Resources/phrase-alignments.json")))
        let index = QuranIndex(verses: rows)
        let engine = RecitationPortionEngine()
        var transitions = 0
        var supported = 0
        for plan in plans {
            let verse = rows.first { $0.id == plan.verseID }!
            let words = verse.arabic.split(whereSeparator: \.isWhitespace)
            await engine.reset()
            var current: String?
            for (expected, boundary) in plan.boundaries.enumerated() {
                let transcript = words.prefix(boundary.arabicEnd).joined(separator: " ")
                let retrieval = index.retrieve(transcript, previous: current)
                current = retrieval.matchedID ?? current
                if current == nil && retrieval.matchedID == nil && retrieval.candidates.count > 1 {
                    print("HOLD: \(verse.id) portion \(expected + 1) opening shared across references")
                    continue
                }
                guard current == verse.id else {
                    print("FAIL: \(verse.id) portion \(expected + 1) global match=\(current ?? "none") candidates=\(retrieval.candidates.map(\.id))")
                    Foundation.exit(1)
                }
                let update = await engine.update(verse: verse, transcript: transcript, alignment: plan)
                precondition(update.index == expected && update.paired)
                precondition(update.cards.allSatisfy { ($0.arabic?.count ?? 0) <= 56 && ($0.translation?.count ?? 0) <= 100 })
                precondition(update.cards.compactMap(\.arabic).joined() == verse.arabic)
                precondition(update.cards.compactMap(\.translation).joined() == verse.translation)
                supported += 1
                if update.changed { transitions += 1 }
            }
            print("PASS: \(verse.id) · \(plan.boundaries.count) automatic paired portions through global lookup and actual follower actor")
        }
        precondition(transitions == supported)
        print("PASS: \(transitions) portion transitions without Next, generated display text or paid calls")
    }
}
