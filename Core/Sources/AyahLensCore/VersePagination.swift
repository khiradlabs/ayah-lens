public struct LensPage: Sendable, Equatable {
    public let arabic: String?
    public let translation: String?
    public let label: String
    public init(arabic: String?, translation: String?, label: String) {
        self.arabic = arabic; self.translation = translation; self.label = label
    }
}

public enum VersePagination {
    public static func pages(for verse: Verse) -> [LensPage] {
        if verse.arabic.count <= 100 && verse.translation.count <= 220 {
            return [LensPage(arabic: verse.arabic, translation: verse.translation, label: "")]
        }
        let arabic = split(verse.arabic, limit: 110)
        let english = split(verse.translation, limit: 220)
        return arabic.enumerated().map { LensPage(arabic: $0.element, translation: nil, label: "Arabic \($0.offset + 1)/\(arabic.count)") }
            + english.enumerated().map { LensPage(arabic: nil, translation: $0.element, label: "Pickthall \($0.offset + 1)/\(english.count)") }
    }

    private static func split(_ text: String, limit: Int) -> [String] {
        var pages: [String] = []
        var start = text.startIndex
        while start < text.endIndex {
            let bound = text.index(start, offsetBy: limit, limitedBy: text.endIndex) ?? text.endIndex
            let end = bound == text.endIndex ? bound : text[start..<bound].lastIndex(where: \.isWhitespace).map { text.index(after: $0) } ?? bound
            pages.append(String(text[start..<end]))
            start = end
        }
        return pages
    }
}
