import Foundation

public struct QuranRetrieval: Sendable {
    public let matchedID: String?
    public let candidates: [Verse]
    public let sparkEligible: Bool
    public init(matchedID: String?, candidates: [Verse], sparkEligible: Bool = false) {
        self.matchedID = matchedID; self.candidates = candidates; self.sparkEligible = sparkEligible
    }
}

public struct QuranIndex: Sendable {
    private let verses: [Verse]
    private let positions: [String: Int]
    private let normalized: [String]
    private let pairs: [String]
    private let postings: [String: [Int]]
    private let shortCounts: [String: Int]

    public init(verses: [Verse]) {
        self.verses = verses
        positions = Dictionary(uniqueKeysWithValues: verses.enumerated().map { ($0.element.id, $0.offset) })
        normalized = verses.map { VerseMatcher.normalize($0.arabic) }
        var pairs: [String] = []
        var postings: [String: [Int]] = [:]
        var shortCounts: [String: Int] = [:]
        for (index, verse) in verses.enumerated() {
            let previous = index > 0 && verse.id.split(separator: ":").first == verses[index - 1].id.split(separator: ":").first
                ? String(normalized[index - 1].suffix(96)) : ""
            let pair = previous + normalized[index]
            pairs.append(pair)
            for gram in Self.grams(pair) { postings[gram, default: []].append(index) }
            let words = verse.arabic.split(whereSeparator: \.isWhitespace).prefix(2)
            if words.count == 2 {
                let aliases: Set<String> = [words.map { VerseMatcher.normalize(String($0)) }.joined(separator: " "),
                    words.map { VerseMatcher.normalize(String($0).replacingOccurrences(of: "ٰ", with: "ا")) }.joined(separator: " ")]
                for alias in aliases { shortCounts[alias, default: 0] += 1 }
            }
        }
        self.pairs = pairs; self.postings = postings; self.shortCounts = shortCounts
    }

    private static func grams(_ text: String) -> Set<String> {
        let letters = Array(text)
        guard letters.count >= 3 else { return [] }
        return Set((0..<(letters.count - 2)).map { String(letters[$0...($0 + 2)]) })
    }

    // Search the newest complete-word suffix against the entire reference first.
    // Older cumulative text must not exclude a newly recited short passage.
    private func uniqueRecentMatch(_ transcript: String) -> Int? {
        let words = transcript.split(whereSeparator: \.isWhitespace).suffix(12)
        guard words.count >= 2 else { return nil }
        for count in 2...words.count {
            let query = VerseMatcher.normalize(words.suffix(count).joined(separator: " "))
            guard query.count >= 8 else { continue }
            let queryGrams = Self.grams(query)
            guard let smallest = queryGrams.compactMap({ postings[$0] }).min(by: { $0.count < $1.count }) else { continue }
            let exact = smallest.filter { normalized[$0].contains(query) }
            if exact.count == 1 { return exact[0] }
        }
        return nil
    }

    public func retrieve(_ transcript: String, previous: String?) -> QuranRetrieval {
        if let position = uniqueRecentMatch(transcript) {
            return QuranRetrieval(matchedID: verses[position].id, candidates: [verses[position]])
        }
        let query = String(VerseMatcher.normalize(transcript).suffix(96))
        guard query.count >= 6 else { return QuranRetrieval(matchedID: nil, candidates: []) }
        let grams = Self.grams(query)
        var scores: [Int: Double] = [:]
        var hits: [Int: Int] = [:]
        for gram in grams {
            guard let entries = postings[gram] else { continue }
            let weight = log(1 + Double(verses.count) / Double(entries.count))
            for index in entries { scores[index, default: 0] += weight; hits[index, default: 0] += 1 }
        }
        var ranked = scores.keys.filter { Double(hits[$0, default: 0]) / Double(max(1, grams.count)) >= 0.25 }
            .sorted { scores[$0] == scores[$1] ? $0 < $1 : scores[$0, default: 0] > scores[$1, default: 0] }
        ranked = Array(ranked.prefix(24))
        if let previous, let position = positions[previous] {
            for index in max(0, position - 1)...min(verses.count - 1, position + 2) {
                if !ranked.contains(index) { ranked.append(index) }
            }
        }
        let supported = ranked.filter {
            VerseMatcher(verses: [verses[$0]], shortOpeningCounts: shortCounts).match(transcript, previous: nil) != nil
        }
        if supported.count == 1 {
            let verse = verses[supported[0]]
            return QuranRetrieval(matchedID: verse.id, candidates: [verse])
        }
        if !supported.isEmpty {
            let contextual = supported.map { Verse(id: verses[$0].id, arabic: pairs[$0], translation: "") }
            if let id = VerseMatcher(verses: contextual, shortOpeningCounts: [:]).match(transcript, previous: previous) {
                return QuranRetrieval(matchedID: id, candidates: [verses[positions[id]!]])
            }
        }
        let selected = Array((supported.isEmpty ? ranked : supported).prefix(8))
        let candidates = selected.map { verses[$0] }
        let identicalEvidence = previous == nil && selected.count > 1 && selected.allSatisfy { normalized[$0].contains(query) }
        return QuranRetrieval(matchedID: nil, candidates: candidates,
                              sparkEligible: candidates.count > 1 && query.count >= 12 && !identicalEvidence)
    }
}

public actor QuranRecognitionEngine {
    private var index: QuranIndex?
    public init() {}
    public func prepare(verses: [Verse]) { if index == nil { index = QuranIndex(verses: verses) } }
    public func retrieve(_ text: String, previous: String?) -> QuranRetrieval {
        index?.retrieve(text, previous: previous) ?? QuranRetrieval(matchedID: nil, candidates: [])
    }
}
