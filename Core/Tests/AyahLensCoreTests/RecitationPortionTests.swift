import XCTest
@testable import AyahLensCore

final class RecitationPortionTests: XCTestCase {
    func testWordPositionFollowsInsideSameAyahAndSupportsMiddleEntryAndRepeat() {
        let locator = AyahWordLocator(arabic: "واتبعوا ما تتلو الشياطين على ملك سليمان وما كفر سليمان ولكن الشياطين كفروا يعلمون الناس السحر")
        XCTAssertEqual(locator.locate("واتبعوا ما تتلو الشياطين", previous: nil), 3)
        XCTAssertEqual(locator.locate("ولكن الشياطين كفروا يعلمون الناس السحر", previous: nil), 15)
        XCTAssertEqual(locator.locate("واتبعوا ما تتلو الشياطين", previous: 15), 3)
        XCTAssertNil(locator.locate("افتح النافذة من فضلك", previous: 3))
        XCTAssertNil(locator.locate("الله", previous: 3))
    }

    func testAmbiguousRepeatedPhraseDoesNotInventPosition() {
        let locator = AyahWordLocator(arabic: "يعلمون الناس السحر وبعد ذلك يعلمون الناس السحر")
        XCTAssertNil(locator.locate("يعلمون الناس السحر", previous: nil))
    }

    func testPairedBoundariesPreserveSourceAndRejectInvalidCoverage() throws {
        let verse = Verse(id: "test", arabic: "كلمات أولى كلمات ثانية", translation: "First source words. Second source words.")
        let plan = PhraseAlignment(verse: verse, boundaries: [.init(arabicEnd: 2, englishEnd: 3), .init(arabicEnd: 4, englishEnd: 6)])
        let cards = try plan.cards(for: verse)
        XCTAssertEqual(cards.compactMap(\.arabic).joined(), verse.arabic)
        XCTAssertEqual(cards.compactMap(\.translation).joined(), verse.translation)
        XCTAssertEqual(plan.portion(forWord: 3), 1)
        XCTAssertThrowsError(try PhraseAlignment(verse: verse, boundaries: [.init(arabicEnd: 2, englishEnd: 3)]).cards(for: verse))
        XCTAssertThrowsError(try PhraseAlignment(verse: verse, boundaries: [.init(arabicEnd: 4, englishEnd: 6), .init(arabicEnd: 2, englishEnd: 3)]).cards(for: verse))
        XCTAssertThrowsError(try plan.cards(for: Verse(id: "test", arabic: "different source", translation: verse.translation)))
    }

    func testAutomaticArabicCardsBoundEveryReferenceAndPreserveWords() throws {
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        let verses = try JSONDecoder().decode([Verse].self, from: Data(contentsOf: root.appendingPathComponent("App/Resources/verses.json")))
        for verse in verses {
            let plan = AutomaticPortions(arabic: verse.arabic)
            XCTAssertEqual(plan.cards.compactMap(\.arabic).joined(), verse.arabic, verse.id)
            XCTAssertTrue(plan.cards.allSatisfy { ($0.arabic?.count ?? 0) <= 56 }, verse.id)
            XCTAssertEqual(plan.portion(forWord: 0), 0)
        }
    }
    func testReportedLongAyahsFollowDistinctiveInteriorPhrases() throws {
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        let verses = try JSONDecoder().decode([Verse].self, from: Data(contentsOf: root.appendingPathComponent("App/Resources/verses.json")))
        for id in ["2:102", "73:20"] {
            let verse = try XCTUnwrap(verses.first { $0.id == id })
            let words = verse.arabic.split(whereSeparator: \.isWhitespace)
            let locator = AyahWordLocator(arabic: verse.arabic)
            for end in [8, words.count / 2, words.count] {
                let fragment = words[(end - 7)..<end].joined(separator: " ")
                XCTAssertEqual(locator.locate(fragment, previous: nil), end - 1, "\(id): \(fragment)")
            }
        }
    }

}
