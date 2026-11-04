import XCTest
@testable import AyahLensCore

final class LivePortionFollowerTests: XCTestCase {
    func testSameVerseMovesPortionsAndUnrelatedTextHoldsPosition() throws {
        let verse = Verse(id: "test", arabic: "واتبعوا ما تتلو الشياطين على ملك سليمان وما كفر سليمان ولكن الشياطين كفروا يعلمون الناس السحر وما انزل على الملكين ببابل هاروت وماروت", translation: String(repeating: "source translation ", count: 30))
        var follower = LivePortionFollower()
        let first = follower.update(verse: verse, transcript: "واتبعوا ما تتلو الشياطين", alignment: nil)
        let middle = follower.update(verse: verse, transcript: "وما انزل على الملكين ببابل هاروت وماروت", alignment: nil)
        XCTAssertGreaterThan(middle.index, first.index)
        XCTAssertEqual(middle.word, 22)
        XCTAssertFalse(middle.paired)
        let hold = follower.update(verse: verse, transcript: "افتح النافذة من فضلك", alignment: nil)
        XCTAssertEqual(hold.index, middle.index)
        let repeatPhrase = follower.update(verse: verse, transcript: "واتبعوا ما تتلو الشياطين", alignment: nil)
        XCTAssertEqual(repeatPhrase.index, first.index)
        XCTAssertTrue(repeatPhrase.changed)
    }
    func testLateAlignmentAppliesAtCurrentWordAndCannotReplaceDifferentVerse() {
        let verse = Verse(id: "test", arabic: "كلمات أولى كلمات ثانية", translation: "First source words. Second source words.")
        let plan = PhraseAlignment(verse: verse, boundaries: [.init(arabicEnd: 2, englishEnd: 3), .init(arabicEnd: 4, englishEnd: 6)])
        var follower = LivePortionFollower()
        _ = follower.update(verse: verse, transcript: "كلمات أولى كلمات ثانية", alignment: nil)
        let paired = follower.update(verse: verse, transcript: "", alignment: plan)
        XCTAssertEqual(paired.index, 1)
        XCTAssertTrue(paired.paired)
        let other = Verse(id: "different", arabic: "نص مختلف", translation: "Other text.")
        let reset = follower.update(verse: other, transcript: "", alignment: plan)
        XCTAssertEqual(reset.index, 0)
        XCTAssertEqual(reset.cards.first?.translation, other.translation)
    }
    func testBundledLongAyahPlansFollowEachPortionWithoutManualNavigation() throws {
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        let verses = try JSONDecoder().decode([Verse].self, from: Data(contentsOf: root.appendingPathComponent("App/Resources/verses.json")))
        let plans = try JSONDecoder().decode([PhraseAlignment].self, from: Data(contentsOf: root.appendingPathComponent("App/Resources/phrase-alignments.json")))
        XCTAssertEqual(Set(plans.map(\.verseID)), ["2:102", "73:20", "2:255"])
        for plan in plans {
            let verse = try XCTUnwrap(verses.first { $0.id == plan.verseID })
            let words = verse.arabic.split(whereSeparator: \.isWhitespace)
            let cards = try plan.cards(for: verse)
            XCTAssertEqual(cards.compactMap(\.arabic).joined(), verse.arabic)
            XCTAssertEqual(cards.compactMap(\.translation).joined(), verse.translation)
            var follower = LivePortionFollower()
            for (index, boundary) in plan.boundaries.enumerated() {
                let transcript = words.prefix(boundary.arabicEnd).joined(separator: " ")
                let update = follower.update(verse: verse, transcript: transcript, alignment: plan)
                XCTAssertEqual(update.index, index, "\(verse.id) portion \(index + 1)")
                XCTAssertTrue(update.paired)
                XCTAssertTrue(update.cards.allSatisfy { ($0.arabic?.count ?? 0) <= 56 && ($0.translation?.count ?? 0) <= 100 })
            }
        }
    }

}
