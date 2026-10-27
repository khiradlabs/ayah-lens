import Foundation

public struct AudioLevel: Sendable {
    public let sampleCount: Int
    public let decibels: Double
    public static func measure(_ samples: [Float]) -> AudioLevel {
        let finite = samples.filter { $0.isFinite }
        let power = finite.reduce(0.0) { $0 + Double($1) * Double($1) }
        let mean = finite.isEmpty ? 0 : power / Double(finite.count)
        return AudioLevel(sampleCount: samples.count, decibels: mean > 0 ? max(-80, 10 * log10(mean)) : -80)
    }
}
