import Foundation

@main
struct ModelProbe {
    static func main() async throws {
        let directory = URL(fileURLWithPath: CommandLine.arguments[1])
        let recognizer = OmnilingualEngine()
        let start = ContinuousClock.now
        try await recognizer.load(directory: directory)
        print("PASS: local CoreML model loaded (CPU and Neural Engine)")
        for rate in [16000.0, 24000.0, 48000.0] {
            // A synthetic tone exercises the complete inference path without private recordings.
            let samples = (0..<Int(rate * 5)).map { Float(sin(Double($0) * 2 * .pi * 220 / rate) * 0.05) }
            let began = ContinuousClock.now
            let text = try await recognizer.transcribe(samples, sampleRate: rate)
            precondition(text.count < 1000)
            print("PASS: \(Int(rate)) Hz → model prediction → Arabic CTC decode; \(text.count) characters; \(began.duration(to: .now))")
        }
        do {
            _ = try await recognizer.transcribe([0], sampleRate: 16000)
            fatalError("Invalid audio should have been rejected")
        } catch RecognitionError.invalidAudio {
            print("PASS: invalid audio rejected")
        }
        print("Model probe completed in \(start.duration(to: .now)). This is not a recitation accuracy test.")
    }
}
