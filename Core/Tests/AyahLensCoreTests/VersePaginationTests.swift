import XCTest
@testable import AyahLensCore

final class VersePaginationTests: XCTestCase {
    func testShortVerseKeepsArabicAndMeaningTogether() {
        let verse = Verse(id: "test", arabic: "نص قصير", translation: "A short source text.")
        let pages = VersePagination.pages(for: verse)
        XCTAssertEqual(pages.count, 1)
        XCTAssertEqual(pages.first?.arabic, verse.arabic)
        XCTAssertEqual(pages.first?.translation, verse.translation)
    }

    func testLongSourceIsBoundedAndReconstructsVerbatimWithSeparateLabels() {
        let verse = Verse(id: "test", arabic: String(repeating: "كلمة ", count: 80), translation: String(repeating: "source meaning ", count: 80))
        let pages = VersePagination.pages(for: verse)
        XCTAssertGreaterThan(pages.count, 2)
        XCTAssertEqual(pages.compactMap(\.arabic).joined(), verse.arabic)
        XCTAssertEqual(pages.compactMap(\.translation).joined(), verse.translation)
        for page in pages {
            XCTAssertTrue((page.arabic == nil) != (page.translation == nil))
            XCTAssertLessThanOrEqual(page.arabic?.count ?? 0, 110)
            XCTAssertLessThanOrEqual(page.translation?.count ?? 0, 220)
            XCTAssertFalse(page.label.isEmpty)
        }
    }
}
