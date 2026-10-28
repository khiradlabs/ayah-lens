import XCTest
@testable import AyahLensCore

final class QuranIndexTests: XCTestCase {
    func corpus() throws -> [Verse] {
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent()
        return try JSONDecoder().decode([Verse].self, from: Data(contentsOf: root.appendingPathComponent("App/Resources/verses.json")))
    }

    func testCompleteCorpusContainsAlignedNonemptyUniqueRows() throws {
        let verses = try corpus()
        XCTAssertEqual(verses.count, 6236)
        XCTAssertEqual(Set(verses.map(\.id)).count, 6236)
        XCTAssertEqual(Set(verses.compactMap { $0.id.split(separator: ":").first }).count, 114)
        XCTAssertTrue(verses.allSatisfy { !$0.arabic.isEmpty && !$0.translation.isEmpty })
    }

    func testGlobalEntryAcrossDifferentSurahsAndMiddleOfLongAyah() throws {
        let index = QuranIndex(verses: try corpus())
        for (text, id) in [
            ("الله لا اله الا هو الحي القيوم لا تاخذه سنة ولا نوم", "2:255"),
            ("لا تاخذه سنة ولا نوم له ما في السماوات", "2:255"),
            ("سلام قولا من رب رحيم", "36:58"),
            ("انا اعطيناك الكوثر", "108:1"),
            ("قل هو الله احد", "112:1"),
            ("قل اعوذ برب الفلق", "113:1"),
            ("قل اعوذ برب الناس", "114:1")
        ] {
            let result = index.retrieve(text, previous: nil)
            XCTAssertEqual(result.matchedID, id, text)
            XCTAssertLessThanOrEqual(result.candidates.count, 8)
        }
    }

    func testSharedPhraseAbstainsWithoutContextAndRecoversWithContext() throws {
        let index = QuranIndex(verses: try corpus())
        XCTAssertNil(index.retrieve("بسم الله الرحمن الرحيم", previous: nil).matchedID)
        XCTAssertNil(index.retrieve("بسم الله", previous: nil).matchedID)
        // This opening is shared by 2:255 and 3:2; more evidence is necessary.
        XCTAssertNil(index.retrieve("الله لا اله الا هو الحي القيوم", previous: nil).matchedID)
        XCTAssertNil(index.retrieve("فباي الاء ربكما تكذبان", previous: nil).matchedID)
        XCTAssertEqual(index.retrieve("فباي الاء ربكما تكذبان", previous: "55:12").matchedID, "55:13")
        XCTAssertEqual(index.retrieve("بسم الله الرحمن الرحيم الحمد لله رب العالمين", previous: nil).matchedID, "1:2")
    }

    func testPassageChangeAndUnrelatedSpeech() throws {
        let index = QuranIndex(verses: try corpus())
        XCTAssertEqual(index.retrieve("قل هو الله احد", previous: "2:255").matchedID, "112:1")
        XCTAssertEqual(index.retrieve("قل اعوذ برب الناس", previous: "114:3").matchedID, "114:1")
        for text in ["", "الله", "open the window", "افتح النافذة من فضلك"] {
            XCTAssertNil(index.retrieve(text, previous: nil).matchedID)
        }
    }
}
