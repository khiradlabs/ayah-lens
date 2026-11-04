import Foundation

public struct Verse: Codable, Identifiable, Sendable {
    public let id: String
    public let arabic: String
    public let translation: String
    public init(id: String, arabic: String, translation: String) {
        self.id = id; self.arabic = arabic; self.translation = translation
    }
}

public struct VerseMatcher: Sendable {
    private let verses: [(id: String, letters: [Character], opening: [Character], shortOpenings: Set<String>)]
    public init(verses: [Verse], shortOpeningCounts: [String: Int]? = nil) {
        self.verses = verses.map {
            let firstWords = $0.arabic.split(whereSeparator: \.isWhitespace).prefix(2)
            // Uthmani dagger-alif and ordinary ASR spelling share a recognition alias.
            let aliases: Set<String> = firstWords.count == 2
                ? [firstWords.map { Self.normalize(String($0)) }.joined(separator: " "),
                   firstWords.map { Self.normalize(String($0).replacingOccurrences(of: "ٰ", with: "ا")) }.joined(separator: " ")] : []
            return ($0.id, Array(Self.normalize($0.arabic)),
                    Array(Self.normalize(String($0.arabic.split(separator: " ").first ?? ""))),
                    Set(aliases.filter { shortOpeningCounts == nil || shortOpeningCounts?[$0] == 1 }))
        }
    }

    // Only recognition copies are normalized. Published display strings stay verbatim.
    public static func normalize(_ text: String) -> String {
        var result = ""
        for scalar in text.unicodeScalars {
            var value = scalar.value
            if [0x622, 0x623, 0x625, 0x671].contains(value) { value = 0x627 }
            if value == 0x649 || value == 0x6CC { value = 0x64A }
            if value == 0x629 { value = 0x647 }
            if (0x621...0x63A).contains(value) || (0x641...0x64A).contains(value) {
                result.unicodeScalars.append(Unicode.Scalar(value)!)
            }
        }
        return result
    }

    public func match(_ transcript: String, previous: String?) -> String? {
        let query = Array(Self.normalize(transcript))
        if let direct = matchSuffix(query, previous: previous) { return direct }
        // Complete, exact two-word openings can be distinctive before eight letters.
        // Keep the fuzzy threshold intact; reject shared or unfinished openings.
        let tailWords = transcript.split(whereSeparator: \.isWhitespace).suffix(2).map { Self.normalize(String($0)) }
        if tailWords.count == 2, tailWords.allSatisfy({ !$0.isEmpty }) {
            let prefix = tailWords.joined()
            if (6...7).contains(prefix.count) {
                let candidates = verses.filter { $0.shortOpenings.contains(tailWords.joined(separator: " ")) }
                if candidates.count == 1 { return candidates[0].id }
            }
        }
        guard let previous, let expectedID = Self.successor(previous), let followingID = Self.successor(previous, by: 2),
              let expected = verses.first(where: { $0.id == expectedID }),
              let following = verses.first(where: { $0.id == followingID })?.opening, query.count >= 11 else { return nil }
        // A sampled window may finish inside the following ayah's first word.
        // Require actual evidence for the expected verse and the following opening.
        for count in 3...min(6, query.count - 8) {
            let tail = Array(query.suffix(count))
            let openingMatches = following.indices.contains { end in
                let length = end + 1
                return abs(count - length) <= 1 && Self.distance(tail, Array(following.prefix(length))) <= 1
            }
            if openingMatches, matchSuffix(Array(query.dropLast(count)), previous: previous) == expected.id {
                return expected.id
            }
        }
        return nil
    }

    private static func successor(_ id: String, by distance: Int = 1) -> String? {
        let parts = id.split(separator: ":")
        guard parts.count == 2, let ayah = Int(parts[1]) else { return nil }
        return "\(parts[0]):\(ayah + distance)"
    }

    private static func distance(_ left: [Character], _ right: [Character]) -> Int {
        var row = Array(0...right.count)
        for (i, letter) in left.enumerated() {
            var next = [i + 1]
            for (j, target) in right.enumerated() {
                next.append(min(next[j] + 1, row[j + 1] + 1, row[j] + (letter == target ? 0 : 1)))
            }
            row = next
        }
        return row.last!
    }

    private func matchSuffix(_ query: [Character], previous: String?) -> String? {
        guard query.count >= 8 else { return nil }
        var scores: [(id: String, evidence: Int)] = []
        for verse in verses {
            var best = 0
            // The latest suffix matters when a rolling window spans several ayahs.
            for length in 8...max(8, min(query.count, verse.letters.count + 2)) {
                let suffix = Array(query.suffix(length))
                var row = [Int](repeating: 0, count: verse.letters.count + 1)
                for (i, letter) in suffix.enumerated() {
                    var next = [i + 1]
                    for (j, target) in verse.letters.enumerated() {
                        next.append(min(next[j] + 1, row[j + 1] + 1, row[j] + (letter == target ? 0 : 1)))
                    }
                    row = next
                }
                let distance = row.min() ?? length
                if Double(distance) / Double(length) <= 0.2 {
                    best = max(best, length - 3 * distance)
                }
            }
            if best >= 8 { scores.append((verse.id, best)) }
        }
        guard let best = scores.map(\.evidence).max() else { return nil }
        let tied = scores.filter { best - $0.evidence <= 1 }
        if tied.count == 1 { return tied[0].id }
        // A known sequence can resolve the repeated basmala phrase, never missing evidence.
        if let previous {
            if tied.contains(where: { $0.id == previous }) { return previous }
            if let next = Self.successor(previous), tied.contains(where: { $0.id == next }) {
                return next
            }
        }
        return nil
    }
}

public struct RecognitionWindows: Sendable {
    private var buffer: [Float] = []
    private var rate: Double = 0
    private var sinceWindow = 0
    public init() {}
    public mutating func append(_ samples: [Float], sampleRate: Double) -> [Float]? {
        guard sampleRate.isFinite, sampleRate >= 1_000, sampleRate <= 192_000 else { return nil }
        if rate != sampleRate { buffer.removeAll(); sinceWindow = 0; rate = sampleRate }
        buffer.append(contentsOf: samples)
        sinceWindow += samples.count
        let window = Int(rate * 5)
        if buffer.count > window { buffer.removeFirst(buffer.count - window) }
        guard buffer.count == window, sinceWindow >= Int(rate) else { return nil }
        sinceWindow = 0
        return buffer
    }
}

public struct ArabicCTC: Sendable {
    public let allowedIDs: [Int]
    private let pieces: [String?]
    public init(pieces: [String?]) {
        self.pieces = pieces
        allowedIDs = pieces.indices.filter { index in
            if index < 4 { return true }
            guard let text = pieces[index] else { return false }
            return !text.isEmpty && text.unicodeScalars.allSatisfy {
                $0.value == 0x20 || $0.value == 0x2581 || (0x600...0x6FF).contains($0.value)
                    || (0x750...0x77F).contains($0.value) || (0xFB50...0xFDFF).contains($0.value)
                    || (0xFE70...0xFEFF).contains($0.value)
            }
        }
    }
    public func decode(ids: [Int]) -> String {
        let allowed = Set(allowedIDs)
        var previous = -1
        var text = ""
        for id in ids {
            defer { previous = id }
            if id != previous, id >= 4, allowed.contains(id), let piece = pieces[id] { text += piece }
        }
        return text.replacingOccurrences(of: "▁", with: " ").trimmingCharacters(in: .whitespaces)
    }
}
