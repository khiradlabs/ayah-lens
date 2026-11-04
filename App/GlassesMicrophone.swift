import AVFoundation

@MainActor
final class GlassesMicrophone {
    private let engine = AVAudioEngine()
    private var tapInstalled = false
    private(set) var sampleRate: Double = 0

    func start(onLevel: @escaping @Sendable (AudioLevel) -> Void,
               onSamples: @escaping @Sendable ([Float], Double) -> Void) async throws {
        let allowed = await withCheckedContinuation { continuation in
            AVAudioApplication.requestRecordPermission { continuation.resume(returning: $0) }
        }
        guard allowed else { throw PrototypeError.message("Allow microphone access in iPhone Settings to run this check.") }
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playAndRecord, mode: .videoRecording, options: [.allowBluetoothHFP, .mixWithOthers])
            try session.setActive(true)
            guard let input = session.availableInputs?.first(where: { $0.portType == .bluetoothHFP }) else {
                throw PrototypeError.message("No glasses Bluetooth microphone is available. Connect the glasses first.")
            }
            try session.setPreferredInput(input)
            guard session.currentRoute.inputs.contains(where: { $0.portType == .bluetoothHFP }) else {
                throw PrototypeError.message("The glasses microphone route did not activate. The phone microphone was not substituted.")
            }
            let format = engine.inputNode.outputFormat(forBus: 0)
            guard format.sampleRate > 0, format.channelCount > 0 else {
                throw PrototypeError.message("The glasses microphone returned an invalid audio format.")
            }
            sampleRate = format.sampleRate
            let inputRate = format.sampleRate
            engine.inputNode.installTap(onBus: 0, bufferSize: 2048, format: format) { @Sendable buffer, _ in
                guard AVAudioSession.sharedInstance().currentRoute.inputs.contains(where: { $0.portType == .bluetoothHFP }) else { return }
                guard let channel = buffer.floatChannelData?[0] else { return }
                let samples = Array(UnsafeBufferPointer(start: channel, count: Int(buffer.frameLength)))
                onLevel(AudioLevel.measure(samples))
                onSamples(samples, inputRate)
            }
            tapInstalled = true
            engine.prepare()
            try engine.start()
        } catch {
            stop()
            throw error
        }
    }

    func stop() {
        engine.stop()
        if tapInstalled { engine.inputNode.removeTap(onBus: 0); tapInstalled = false }
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }
}
