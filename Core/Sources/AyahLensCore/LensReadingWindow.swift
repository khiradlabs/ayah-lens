public struct LiveLensFrame: Sendable, Equatable {
    public let verseID: String
    public let firstPortion: Int
    public let lastPortion: Int
    public let totalPortions: Int
    public let page: LensPage
    public var header: String {
        let span = firstPortion == lastPortion ? "\(firstPortion + 1)" : "\(firstPortion + 1)–\(lastPortion + 1)"
        return "Quran \(verseID) · \(span)/\(totalPortions)"
    }
}
public enum LensReadingWindow {
    public static func frame(verseID: String, cards: [LensPage], index: Int) -> LiveLensFrame? {
        guard cards.indices.contains(index) else { return nil }
        let current = cards[index]
        var last = index, page = current
        if cards.indices.contains(index + 1), let firstArabic = current.arabic, let nextArabic = cards[index + 1].arabic,
           (current.translation == nil) == (cards[index + 1].translation == nil) {
            let arabic = firstArabic + nextArabic
            let english = current.translation.map { $0 + (cards[index + 1].translation ?? "") }
            if arabic.count <= 84 && (english?.count ?? 0) <= 150 {
                last += 1
                page = LensPage(arabic: arabic, translation: english, label: "Current + upcoming")
            }
        }
        return LiveLensFrame(verseID: verseID, firstPortion: index, lastPortion: last, totalPortions: cards.count, page: page)
    }
}
