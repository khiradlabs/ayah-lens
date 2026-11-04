import Foundation

@main struct QuranProbe {
    static func main() throws {
        let rows = try JSONDecoder().decode([Verse].self, from: Data(contentsOf: URL(fileURLWithPath: "App/Resources/verses.json")))
        precondition(rows.count == 6236)
        let started = ContinuousClock.now
        let index = QuranIndex(verses: rows)
        print("PASS: complete Quran index constructed in \(started.duration(to: .now))")
        let queries = [("بسم الله الرحمن الرحيم الحمد لله رب العالمين", "1:2"),
                       ("الله لا اله الا هو الحي القيوم لا تاخذه سنة ولا نوم", "2:255"),
                       ("قل هو الله احد", "112:1"), ("قل اعوذ برب الناس", "114:1")]
        var durations: [Double] = []
        for _ in 0..<10 {
            for (text, expected) in queries {
                let start = ContinuousClock.now
                let result = index.retrieve(text, previous: nil)
                let time = start.duration(to: .now).components
                durations.append(Double(time.seconds) * 1000 + Double(time.attoseconds) / 1e15)
                precondition(result.matchedID == expected && result.candidates.count <= 8)
            }
        }
        durations.sort()
        print(String(format: "PASS: 40 global lookups; median %.2f ms, p95 %.2f ms (optimized host proxy)", durations[durations.count / 2], durations[Int(Double(durations.count - 1) * 0.95)]))
        precondition(index.retrieve("بسم الله", previous: nil).matchedID == nil)
        print("PASS: shared opening remains unresolved without passage context")
    }
}
