import XCTest
@testable import AyahLensCore

final class LensReadingWindowTests: XCTestCase {
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
