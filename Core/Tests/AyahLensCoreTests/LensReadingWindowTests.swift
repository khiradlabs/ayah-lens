import XCTest
@testable import AyahLensCore

final class LensReadingWindowTests: XCTestCase {
    func testLargerTextKeepsDensePairedWindowsToOneSourcePortion() throws {
        let first = LensPage(arabic: String(repeating: "ك", count: 30), translation: String(repeating: "a", count: 60), label: "")
        let second = LensPage(arabic: String(repeating: "ل", count: 30), translation: String(repeating: "b", count: 60), label: "")
        for showTranslation in [true, false] {
            let frame = try XCTUnwrap(LensReadingWindow.frame(verseID: "test", cards: [first, second], index: 0, showTranslation: showTranslation))
            XCTAssertEqual(frame.lastPortion, 0)
            XCTAssertEqual(frame.page.arabic, first.arabic)
            XCTAssertEqual(frame.page.translation, showTranslation ? first.translation : nil)
            let next = try XCTUnwrap(LensReadingWindow.frame(verseID: "test", cards: [first, second], index: 1, showTranslation: showTranslation))
            XCTAssertEqual(next.page.arabic, second.arabic)
        }
    }

    func testMeaningVisibilityPreservesArabicWindowAndPositionAndCanBeRestored() throws {
        let pages = [LensPage(arabic: "أول الكلام ", translation: "First meaning. ", label: ""),
                     LensPage(arabic: "ثم الكلام ", translation: "Second meaning. ", label: ""),
                     LensPage(arabic: "آخر الكلام", translation: "Last meaning.", label: "")]
        let shown = try XCTUnwrap(LensReadingWindow.frame(verseID: "test", cards: pages, index: 1))
        let hidden = try XCTUnwrap(LensReadingWindow.frame(verseID: "test", cards: pages, index: 1, showTranslation: false))
        XCTAssertNil(hidden.page.translation)
        XCTAssertEqual(hidden.page.arabic, shown.page.arabic)
        XCTAssertEqual(hidden.header, shown.header)
        XCTAssertEqual(hidden.firstPortion, shown.firstPortion)
        XCTAssertEqual(hidden.lastPortion, shown.lastPortion)
        XCTAssertEqual(hidden.totalPortions, shown.totalPortions)
        XCTAssertEqual(LensReadingWindow.frame(verseID: "test", cards: pages, index: 1, showTranslation: true), shown)
        XCTAssertEqual(pages[1].translation, "Second meaning. ", "Visibility must not erase source meaning")
    }

    func testArabicOnlyKeepsSameWindowEvenWhenEnglishPreventsMerging() throws {
        let pages = [LensPage(arabic: "كلمات أولى ", translation: String(repeating: "a", count: 90), label: ""),
                     LensPage(arabic: "كلمات ثانية", translation: String(repeating: "b", count: 90), label: "")]
        let hidden = try XCTUnwrap(LensReadingWindow.frame(verseID: "test", cards: pages, index: 0, showTranslation: false))
        XCTAssertNil(hidden.page.translation)
        XCTAssertEqual(hidden.lastPortion, 0, "Changing visibility must not change the selected source span")
        XCTAssertEqual(hidden.page.arabic, pages[0].arabic)
        XCTAssertNil(LensReadingWindow.frame(verseID: "test", cards: [], index: 0, showTranslation: false))
    }

    func testWindowIncludesUpcomingContextWithoutChangingSourceOrCurrentPosition() {
        let pages = [LensPage(arabic: "كلمات أولى ", translation: "First meaning. ", label: ""),
                     LensPage(arabic: "كلمات ثانية ", translation: "Second meaning. ", label: ""),
                     LensPage(arabic: "كلمات ثالثة", translation: "Third meaning.", label: "")]
        let frame = LensReadingWindow.frame(verseID: "test", cards: pages, index: 0)
        XCTAssertEqual(frame?.page.arabic, "كلمات أولى كلمات ثانية ")
        XCTAssertEqual(frame?.page.translation, "First meaning. Second meaning. ")
        XCTAssertEqual(frame?.firstPortion, 0)
        XCTAssertEqual(frame?.lastPortion, 1)
        XCTAssertEqual(LensReadingWindow.frame(verseID: "test", cards: pages, index: 2)?.page.arabic, "كلمات ثالثة")
    }
    func testWindowDoesNotMergeOversizedOrUnpairedSourceSpans() {
        let paired = LensPage(arabic: String(repeating: "ك", count: 50), translation: String(repeating: "x", count: 90), label: "")
        XCTAssertEqual(LensReadingWindow.frame(verseID: "test", cards: [paired, paired], index: 0)?.lastPortion, 0)
        let arabicOnly = LensPage(arabic: "كلمات أخرى", translation: nil, label: "")
        XCTAssertEqual(LensReadingWindow.frame(verseID: "test", cards: [paired, arabicOnly], index: 0)?.lastPortion, 0)
        XCTAssertNil(LensReadingWindow.frame(verseID: "test", cards: [], index: 0))
    }
}
