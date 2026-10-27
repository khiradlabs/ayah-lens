import XCTest
@testable import AyahLensCore

final class RecognitionTests: XCTestCase {
    let verses = [
        Verse(id: "1:1", arabic: "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ", translation: ""),
        Verse(id: "1:2", arabic: "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ", translation: ""),
        Verse(id: "1:3", arabic: "ٱلرَّحْمَٰنِ ٱلرَّحِيمِ", translation: ""),
        Verse(id: "1:4", arabic: "مَٰلِكِ يَوْمِ ٱلدِّينِ", translation: "")
    ]

    func testMatchesUnvowelledFragmentWithoutChangingCanonicalText() {
        let matcher = VerseMatcher(verses: verses)
        XCTAssertEqual(matcher.match("الحمد لله رب العالمين", previous: nil), "1:2")
        XCTAssertEqual(verses[1].arabic, "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ")
    }

    func testAmbiguousSharedPhraseNeedsEstablishedSequence() {
        let matcher = VerseMatcher(verses: verses)
        XCTAssertNil(matcher.match("الرحمن الرحيم", previous: nil))
        XCTAssertEqual(matcher.match("الرحمن الرحيم", previous: "1:2"), "1:3")
    }

    func testRollingTranscriptSelectsLatestEvidenceAndAllowsRepeats() {
        let matcher = VerseMatcher(verses: verses)
        XCTAssertEqual(matcher.match("الحمد لله رب العالمين مالك يوم الدين", previous: "1:2"), "1:4")
        XCTAssertEqual(matcher.match("الحمد لله رب العالمين", previous: "1:4"), "1:2")
    }

    func testShortUnrelatedAndNonArabicSpeechDoesNotLock() {
        let matcher = VerseMatcher(verses: verses)
        for text in ["", "الله", "hello world", "افتح النافذة من فضلك", "الرحمن"] {
            XCTAssertNil(matcher.match(text, previous: nil), text)
        }
    }

    func testWindowsAreBoundedUseRealSampleRateAndResetOnRouteChange() {
        var windows = RecognitionWindows()
        XCTAssertNil(windows.append([Float](repeating: 1, count: 4_000), sampleRate: 1_000))
        XCTAssertEqual(windows.append([Float](repeating: 2, count: 1_000), sampleRate: 1_000)?.count, 5_000)
        XCTAssertNil(windows.append([Float](repeating: 3, count: 500), sampleRate: 1_000))
        let next = windows.append([Float](repeating: 4, count: 500), sampleRate: 1_000)
        XCTAssertEqual(next?.count, 5_000)
        XCTAssertEqual(next?.first, 1)
        XCTAssertEqual(next?.last, 4)
        XCTAssertNil(windows.append([1, 2], sampleRate: 2_000))
    }

    func testCTCBlankSeparatesRepeatedCharactersAndFiltersOtherScripts() {
        let decoder = ArabicCTC(pieces: [nil, nil, nil, nil, " ", "ا", "ب", "x"])
        XCTAssertEqual(decoder.decode(ids: [5, 5, 1, 5, 4, 6, 6, 7]), "اا ب")
        XCTAssertFalse(decoder.allowedIDs.contains(7))
        XCTAssertTrue(decoder.allowedIDs.contains(1))
    }

    func testAllSevenVersesAgainstBundledCanonicalReference() throws {
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        let reference = try JSONDecoder().decode([Verse].self, from: Data(contentsOf: root.appendingPathComponent("App/Resources/verses.json")))
        let matcher = VerseMatcher(verses: reference)
        let fragments = ["بسم الله الرحمن الرحيم", "الحمد لله رب العالمين", "الرحمن الرحيم",
                         "مالك يوم الدين", "إياك نعبد وإياك نستعين", "اهدنا الصراط المستقيم", "ولا الضالين"]
        var previous: String?
        for (index, text) in fragments.enumerated() {
            let id = "1:\(index + 1)"
            XCTAssertEqual(matcher.match(text, previous: previous), id)
            previous = id
        }
    }
}
