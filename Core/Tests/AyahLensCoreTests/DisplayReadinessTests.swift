import XCTest
@testable import AyahLensCore

final class DisplayReadinessTests: XCTestCase {
    func testWaitsPastAnEmptyDiscoveryUpdateForAnActualDevice() async {
        let (updates, continuation) = AsyncStream<String?>.makeStream()
        continuation.yield(nil)
        let pending = Task { try await DisplayReadiness.firstAvailable(in: updates) }
        await Task.yield()
        continuation.yield("synthetic-display")
        continuation.finish()
        do {
            let result = try await pending.value
            XCTAssertEqual(result, "synthetic-display")
        } catch { XCTFail("Discovery must wait for the eligible device, not fail on its initial nil update: \(error)") }
    }

    func testAClosedStreamWithoutDevicesFails() async {
        let updates = AsyncStream<String?> { $0.yield(nil); $0.finish() }
        do {
            _ = try await DisplayReadiness.firstAvailable(in: updates)
            XCTFail("An absent device must not be treated as ready")
        } catch { XCTAssertEqual(error as? DisplayReadinessError, .unavailable) }
    }

    func testCancelledDiscoveryDoesNotContinueToSessionStartup() async {
        let (updates, continuation) = AsyncStream<String?>.makeStream()
        let pending = Task { try await DisplayReadiness.firstAvailable(in: updates) }
        pending.cancel()
        do {
            _ = try await pending.value
            XCTFail("Cancelled discovery must throw")
        } catch { XCTAssertTrue(error is CancellationError) }
        continuation.finish()
    }
}
