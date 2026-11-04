import XCTest
@testable import AyahLensCore

@MainActor final class LatestLensSenderTests: XCTestCase {
    func testSlowSendDoesNotBlockUpdatesAndOnlyNewestPendingFrameSurvives() async {
        let (started, startSignal) = AsyncStream<Void>.makeStream()
        let (release, releaseSignal) = AsyncStream<Void>.makeStream()
        let (finished, finishSignal) = AsyncStream<Int>.makeStream()
        var sent: [Int] = []
        let sender = LatestLensSender<Int>(send: { frame in
            sent.append(frame)
            if frame == 1 {
                startSignal.yield()
                var iterator = release.makeAsyncIterator()
                _ = await iterator.next()
            }
            finishSignal.yield(frame)
        }, onFailure: { _ in XCTFail("Unexpected sender failure") })
        sender.enqueue(1)
        var starts = started.makeAsyncIterator(); _ = await starts.next()
        sender.enqueue(2); sender.enqueue(3)
        for _ in 0..<5 { await Task.yield() }
        XCTAssertEqual(sent, [1], "SDK send must remain single-flight")
        releaseSignal.yield()
        var finishes = finished.makeAsyncIterator()
        while let frame = await finishes.next() { if frame == 3 { break } }
        for _ in 0..<5 { await Task.yield() }
        XCTAssertEqual(sent, [1, 3], "Frame 2 was superseded before delivery")
        XCTAssertEqual(sender.metrics.superseded, 1)
        XCTAssertEqual(sender.metrics.completed, 2)
        sender.stop()
    }

    func testStopInvalidatesPendingFramesAndSuppressesLateCompletion() async {
        let (started, startSignal) = AsyncStream<Void>.makeStream()
        let (release, releaseSignal) = AsyncStream<Void>.makeStream()
        var sent: [Int] = []
        var failures = 0
        let sender = LatestLensSender<Int>(send: { frame in
            sent.append(frame); startSignal.yield()
            var iterator = release.makeAsyncIterator(); _ = await iterator.next()
        }, onFailure: { _ in failures += 1 })
        sender.enqueue(1)
        var starts = started.makeAsyncIterator(); _ = await starts.next()
        sender.enqueue(2); sender.stop(); releaseSignal.yield()
        for _ in 0..<10 { await Task.yield() }
        XCTAssertEqual(sent, [1])
        XCTAssertEqual(failures, 0)
        XCTAssertEqual(sender.metrics.completed, 0)
    }
}
