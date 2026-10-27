import AVFoundation
import Foundation

public enum MuseError: Error, LocalizedError {
    case invalidAudio, rejected, notConnected, testLimit, connection
    public var errorDescription: String? {
        switch self {
        case .invalidAudio: "Muse received an invalid microphone format."
        case .rejected: "Muse rejected the session. Check API access and billing."
        case .notConnected: "Muse is not connected."
        case .testLimit: "The two-minute Muse test limit was reached."
        case .connection: "The Muse connection ended unexpectedly."
        }
    }
}

public enum MuseProtocol {
    public static func handshake(apiKey: String) throws -> Data {
        guard !apiKey.isEmpty else { throw MuseError.rejected }
        return try JSONSerialization.data(withJSONObject: [
            "authorization": ["accessToken": "Bearer " + apiKey],
            "model": "muse-voice-transcribe-1.0", "audioEncoding": "PCM_24KHZ",
            "mode": "ENDPOINTING", "partialMode": "CUMULATIVE",
            "languageBias": ["Arabic"], "emitAudioProgress": false
        ])
    }
}

public struct MuseTranscriptState: Sendable {
    private var activeTurn: Int?
    public init() {}
    public mutating func consume(_ message: String) throws -> String? {
        guard let event = try JSONSerialization.jsonObject(with: Data(message.utf8)) as? [String: Any] else { return nil }
        switch event["type"] as? String {
        case "error": throw MuseError.rejected
        case "speechStart": activeTurn = event["turnId"] as? Int; return nil
        case "transcript": return event["transcript"] as? String
        case "speechComplete":
            if let activeTurn, let turn = event["turnId"] as? Int, turn != activeTurn { return nil }
            return event["transcript"] as? String
        default: return nil
        }
    }
}

public final class MusePCMEncoder {
    private var converter: AVAudioConverter?
    private var rate: Double = 0
    public init() {}
    public func encode(_ samples: [Float], sampleRate: Double) throws -> Data {
        guard sampleRate.isFinite, (1000...192000).contains(sampleRate),
              !samples.isEmpty, samples.count <= Int(sampleRate), samples.allSatisfy(\.isFinite),
              let source = AVAudioFormat(standardFormatWithSampleRate: sampleRate, channels: 1),
              let target = AVAudioFormat(commonFormat: .pcmFormatInt16, sampleRate: 24000, channels: 1, interleaved: false)
        else { throw MuseError.invalidAudio }
        if rate != sampleRate {
            converter = AVAudioConverter(from: source, to: target)
            rate = sampleRate
        }
        guard let converter,
              let input = AVAudioPCMBuffer(pcmFormat: source, frameCapacity: AVAudioFrameCount(samples.count)),
              let output = AVAudioPCMBuffer(pcmFormat: target, frameCapacity: AVAudioFrameCount(ceil(Double(samples.count) * 24000 / sampleRate) + 128))
        else { throw MuseError.invalidAudio }
        input.frameLength = AVAudioFrameCount(samples.count)
        samples.withUnsafeBufferPointer { input.floatChannelData![0].update(from: $0.baseAddress!, count: samples.count) }
        var supplied = false
        var error: NSError?
        let status = converter.convert(to: output, error: &error) { _, state in
            if supplied { state.pointee = .noDataNow; return nil }
            supplied = true
            state.pointee = .haveData
            return input
        }
        if let error { throw error }
        guard status != .error, let pointer = output.int16ChannelData?[0] else { throw MuseError.invalidAudio }
        return Data(bytes: pointer, count: Int(output.frameLength) * 2)
    }
}
