import XCTest
@testable import AyahLensCore

final class AudioLevelTests: XCTestCase {
    func testKnownWaveformHasCorrectLevelAndSampleCount() {
        let level = AudioLevel.measure([0.5, -0.5, 0, 0])
        XCTAssertEqual(level.sampleCount, 4)
        XCTAssertEqual(level.decibels, -9.0309, accuracy: 0.001)
    }

    func testSilenceAndInvalidSamplesNeverProduceNonFiniteLevels() {
        for samples: [Float] in [[], [0, 0], [.nan, .infinity]] {
            let level = AudioLevel.measure(samples)
            XCTAssertEqual(level.decibels, -80)
        }
    }
}
