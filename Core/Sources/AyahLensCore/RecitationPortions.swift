import Foundation

public struct PhraseBoundary: Codable, Sendable, Equatable {
    public let arabicEnd: Int
    public let englishEnd: Int
    public init(arabicEnd: Int, englishEnd: Int) { self.arabicEnd = arabicEnd; self.englishEnd = englishEnd }
}
public struct PhraseAlignment: Codable, Sendable, Equatable {
    public let verseID: String
    public let arabicSource: String
    public let englishSource: String
    public let boundaries: [PhraseBoundary]
    public init(verse: Verse, boundaries: [PhraseBoundary]) {
        verseID = verse.id; arabicSource = verse.arabic; englishSource = verse.translation; self.boundaries = boundaries
    }
    public func cards(for verse: Verse) throws -> [LensPage] {
        guard verse.id == verseID, verse.arabic == arabicSource, verse.translation == englishSource,
              !boundaries.isEmpty else { throw SparkError.invalidResponse }
        let arabic = SourceWords(arabicSource), english = SourceWords(englishSource)
        var a = 0, e = 0
        var cards: [LensPage] = []
        for (index, boundary) in boundaries.enumerated() {
            guard boundary.arabicEnd > a, boundary.arabicEnd <= arabic.words.count,
                  boundary.englishEnd > e, boundary.englishEnd <= english.words.count else { throw SparkError.invalidResponse }
            let ar = arabic.slice(a, boundary.arabicEnd), en = english.slice(e, boundary.englishEnd)
            guard ar.count <= 56, en.count <= 100 else { throw SparkError.invalidResponse }
            cards.append(LensPage(arabic: ar, translation: en, label: "Part \(index + 1)/\(boundaries.count)"))
            a = boundary.arabicEnd; e = boundary.englishEnd
        }
        guard a == arabic.words.count, e == english.words.count else { throw SparkError.invalidResponse }
        return cards
    }
    public func portion(forWord word: Int) -> Int {
        boundaries.firstIndex { word < $0.arabicEnd } ?? max(0, boundaries.count - 1)
    }
}
// Keep source whitespace so joining all slices reproduces the reference exactly.
struct SourceWords: Sendable {
    let text: String
    let words: [String]
    private let starts: [String.Index]
    init(_ text: String) {
        self.text = text
        let pieces = text.split(whereSeparator: \.isWhitespace)
        words = pieces.map(String.init)
        starts = pieces.enumerated().map { $0.offset == 0 ? text.startIndex : $0.element.startIndex }
    }
    func slice(_ start: Int, _ end: Int) -> String {
        String(text[starts[start]..<(end == words.count ? text.endIndex : starts[end])])
    }
}

public struct AutomaticPortions: Sendable {
    public let cards: [LensPage]
    private let ends: [Int]
    public init(arabic: String) {
        let source = SourceWords(arabic)
        var cards: [LensPage] = [], ends: [Int] = []
        var start = 0
        while start < source.words.count {
            var end = start + 1
            while end < source.words.count && source.slice(start, end + 1).count <= 56 { end += 1 }
            cards.append(LensPage(arabic: source.slice(start, end), translation: nil, label: "Arabic portion"))
            ends.append(end)
            start = end
        }
        self.cards = cards; self.ends = ends
    }
    public func portion(forWord word: Int) -> Int {
        ends.firstIndex { word < $0 } ?? max(0, ends.count - 1)
    }
}

public struct AyahWordLocator: Sendable {
    private let letters: [Character]
    private let wordEnds: [Int]
    public init(arabic: String) {
        let words = arabic.split(whereSeparator: \.isWhitespace)
        var letters: [Character] = [], ends: [Int] = []
        for word in words {
            letters += Array(VerseMatcher.normalize(String(word)))
            ends.append(letters.count)
        }
        self.letters = letters; wordEnds = ends
    }
    public func locate(_ transcript: String, previous: Int?) -> Int? {
        let text = Array(VerseMatcher.normalize(transcript).suffix(48))
        guard text.count >= 8, !letters.isEmpty else { return nil }
        var scores: [Int: Int] = [:]
        let lengths = Set(Array(stride(from: 8, through: text.count, by: 4)) + [text.count])
        for length in lengths {
            let query = text.suffix(length)
            var row = [Int](repeating: 0, count: letters.count + 1)
            for (i, character) in query.enumerated() {
                var next = [Int](repeating: 0, count: letters.count + 1)
                next[0] = i + 1
                for j in letters.indices {
                    next[j + 1] = min(next[j] + 1, row[j + 1] + 1, row[j] + (character == letters[j] ? 0 : 1))
                }
                row = next
            }
            for (word, end) in wordEnds.enumerated() {
                let distance = row[end]
                if Double(distance) / Double(length) <= 0.18 {
                    scores[word] = max(scores[word, default: 0], length - 3 * distance)
                }
            }
        }
        guard let best = scores.values.max(), best >= 8 else { return nil }
        let tied = scores.keys.filter { best - scores[$0, default: 0] <= 1 }
        if tied.count == 1 { return tied[0] }
        if let previous {
            if tied.contains(previous) { return previous }
            let nearby = tied.filter { $0 > previous && $0 <= previous + 3 }
            if nearby.count == 1 { return nearby[0] }
        }
        return nil
    }
}

public struct LivePortionUpdate: Sendable {
    public let cards: [LensPage]
    public let index: Int
    public let word: Int?
    public let paired: Bool
    public let changed: Bool
}
public struct LivePortionFollower: Sendable {
    private var verseID: String?
    private var locator: AyahWordLocator?
    private var automatic: AutomaticPortions?
    private var word: Int?
    private var cards: [LensPage] = []
    private var index = 0
    private var paired = false
    private var currentAlignment: PhraseAlignment?
    public init() {}
    public mutating func update(verse: Verse, transcript: String, alignment: PhraseAlignment?) -> LivePortionUpdate {
        let oldID = verseID, oldIndex = index, oldCards = cards
        if verseID != verse.id {
            verseID = verse.id; word = nil; index = 0
            locator = AyahWordLocator(arabic: verse.arabic)
            automatic = AutomaticPortions(arabic: verse.arabic)
            currentAlignment = nil
        }
        if let alignment, let validated = try? alignment.cards(for: verse) {
            currentAlignment = alignment; cards = validated; paired = true
        } else if verse.arabic.count <= 56 && verse.translation.count <= 100 {
            cards = [LensPage(arabic: verse.arabic, translation: verse.translation, label: "")]
            paired = true
        } else {
            currentAlignment = nil; cards = automatic?.cards ?? []; paired = false
        }
        if let located = locator?.locate(transcript, previous: word) { word = located }
        index = word.map { currentAlignment?.portion(forWord: $0) ?? automatic?.portion(forWord: $0) ?? 0 } ?? 0
        if cards.count == 1 { index = 0 }
        return LivePortionUpdate(cards: cards, index: index, word: word, paired: paired,
                                 changed: oldID != verseID || oldIndex != index || oldCards != cards)
    }
}

public actor RecitationPortionEngine {
    private var follower = LivePortionFollower()
    public init() {}
    public func update(verse: Verse, transcript: String, alignment: PhraseAlignment?) -> LivePortionUpdate {
        follower.update(verse: verse, transcript: transcript, alignment: alignment)
    }
    public func reset() { follower = LivePortionFollower() }
}
