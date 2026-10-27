import AVFoundation
import CoreML
import Foundation

public enum RecognitionError: Error { case missingModel, invalidAudio, invalidLogits }

/// Serial, local inference. No audio files or network requests are created.
public actor OmnilingualEngine {
    private var model: MLModel?
    private var decoder: ArabicCTC?
    public init() {}

    public func load(directory: URL) throws {
        guard model == nil else { return }
        let vocabulary = directory.appendingPathComponent("vocabulary.json")
        guard FileManager.default.fileExists(atPath: vocabulary.path) else { throw RecognitionError.missingModel }
        let pieces = try JSONDecoder().decode([String?].self, from: Data(contentsOf: vocabulary))
        guard pieces.count == 10288 else { throw RecognitionError.invalidLogits }
        let configuration = MLModelConfiguration()
        configuration.computeUnits = .cpuAndNeuralEngine
        let loaded = try MLModel(contentsOf: directory.appendingPathComponent("model.mlmodelc"), configuration: configuration)
        decoder = ArabicCTC(pieces: pieces)
        model = loaded
    }

    public func transcribe(_ samples: [Float], sampleRate: Double) throws -> String {
        guard let model, let decoder else { throw RecognitionError.missingModel }
        guard sampleRate.isFinite, sampleRate >= 1000, sampleRate <= 192000,
              samples.count == Int(sampleRate * 5), samples.allSatisfy(\.isFinite) else { throw RecognitionError.invalidAudio }
        let waveform = try Self.resample(samples, from: sampleRate)
        guard waveform.count == 80000 else { throw RecognitionError.invalidAudio }
        let input = try MLMultiArray(shape: [1, 80000], dataType: .float32)
        let pointer = input.dataPointer.bindMemory(to: Float.self, capacity: 80000)
        let count = Float(waveform.count)
        let mean = waveform.reduce(0, +) / count
        let variance = waveform.reduce(Float(0)) { $0 + ($1 - mean) * ($1 - mean) } / count
        let scale = 1 / sqrt(variance + 1e-5)
        for index in waveform.indices { pointer[index] = (waveform[index] - mean) * scale }
        let provider = try MLDictionaryFeatureProvider(dictionary: ["audio": input])
        let output = try model.prediction(from: provider)
        guard let logits = output.featureValue(for: "logits")?.multiArrayValue,
              logits.shape.count == 3, logits.shape[0].intValue == 1,
              logits.shape[2].intValue == 10288 else { throw RecognitionError.invalidLogits }
        let frames = logits.shape[1].intValue
        let timeStride = logits.strides[1].intValue
        let tokenStride = logits.strides[2].intValue
        var ids: [Int] = []
        for frame in 0..<frames {
            var best = 1
            var maximum = -Float.infinity
            for token in decoder.allowedIDs {
                let offset = frame * timeStride + token * tokenStride
                let value: Float
                switch logits.dataType {
                case .float32: value = logits.dataPointer.assumingMemoryBound(to: Float.self)[offset]
                case .float16: value = Float(logits.dataPointer.assumingMemoryBound(to: Float16.self)[offset])
                default: throw RecognitionError.invalidLogits
                }
                if value > maximum { maximum = value; best = token }
            }
            ids.append(best)
        }
        return decoder.decode(ids: ids)
    }

    private static func resample(_ samples: [Float], from rate: Double) throws -> [Float] {
        if rate == 16000 { return samples }
        guard let source = AVAudioFormat(standardFormatWithSampleRate: rate, channels: 1),
              let destination = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1),
              let converter = AVAudioConverter(from: source, to: destination),
              let input = AVAudioPCMBuffer(pcmFormat: source, frameCapacity: AVAudioFrameCount(samples.count)),
              let output = AVAudioPCMBuffer(pcmFormat: destination, frameCapacity: 80000) else { throw RecognitionError.invalidAudio }
        input.frameLength = AVAudioFrameCount(samples.count)
        samples.withUnsafeBufferPointer { input.floatChannelData![0].update(from: $0.baseAddress!, count: samples.count) }
        var supplied = false
        var error: NSError?
        let status = converter.convert(to: output, error: &error) { _, state in
            if supplied { state.pointee = .endOfStream; return nil }
            supplied = true
            state.pointee = .haveData
            return input
        }
        if let error { throw error }
        guard status != .error, output.frameLength == 80000 else { throw RecognitionError.invalidAudio }
        return Array(UnsafeBufferPointer(start: output.floatChannelData![0], count: Int(output.frameLength)))
    }
}
