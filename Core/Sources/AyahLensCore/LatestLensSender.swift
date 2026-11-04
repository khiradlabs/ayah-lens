import Foundation

public struct LensSendMetrics: Codable, Sendable {
    public var requested = 0
    public var completed = 0
    public var superseded = 0
    public var queueMilliseconds = 0.0
    public var sdkMilliseconds = 0.0
    public var maxSDKMilliseconds = 0.0
    public init() {}
}

@MainActor public final class LatestLensSender<Frame: Sendable> {
    public private(set) var metrics = LensSendMetrics()
    private var pending: (Frame, Double)?
    private var task: Task<Void, Never>?
    private var generation = 0
    private let send: @MainActor (Frame) async throws -> Void
    private let onFailure: @MainActor (Error) -> Void
    private let onMetrics: @MainActor (LensSendMetrics) -> Void
    public init(send: @escaping @MainActor (Frame) async throws -> Void,
                onFailure: @escaping @MainActor (Error) -> Void,
                onMetrics: @escaping @MainActor (LensSendMetrics) -> Void = { _ in }) {
        self.send = send; self.onFailure = onFailure; self.onMetrics = onMetrics
    }
    public func enqueue(_ frame: Frame) {
        metrics.requested += 1
        if pending != nil { metrics.superseded += 1 }
        pending = (frame, ProcessInfo.processInfo.systemUptime)
        onMetrics(metrics)
        guard task == nil else { return }
        let generation = generation
        task = Task { [weak self] in
            guard let self else { return }
            defer { if self.generation == generation { self.task = nil } }
            while let (frame, selectedAt) = self.pending, self.generation == generation {
                self.pending = nil
                let began = ProcessInfo.processInfo.systemUptime
                self.metrics.queueMilliseconds = max(0, (began - selectedAt) * 1000)
                do {
                    try Task.checkCancellation()
                    try await self.send(frame)
                    try Task.checkCancellation()
                    guard self.generation == generation else { return }
                    self.metrics.completed += 1
                    self.metrics.sdkMilliseconds = max(0, (ProcessInfo.processInfo.systemUptime - began) * 1000)
                    self.metrics.maxSDKMilliseconds = max(self.metrics.maxSDKMilliseconds, self.metrics.sdkMilliseconds)
                    self.onMetrics(self.metrics)
                } catch is CancellationError { return }
                catch {
                    guard self.generation == generation else { return }
                    self.pending = nil
                    self.onFailure(error)
                    return
                }
            }
        }
    }
    public func stop() {
        generation += 1
        pending = nil
        task?.cancel(); task = nil
    }
}
