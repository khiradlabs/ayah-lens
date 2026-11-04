public struct MuseStreamSnapshot: Codable, Sendable {
    public var sentBatches = 0
    public var sentAudioSeconds = 0.0
    public var providerUpdates = 0
    public var transcriptUpdates = 0
    public var transcriptCharacters = 0
    public var audioSendAgeSeconds: Double?
    public var providerAgeSeconds: Double?
    public var transcriptAgeSeconds: Double?
}

public struct MuseStreamTrace: Sendable {
    private var value = MuseStreamSnapshot()
    private var lastSend: Double?
    private var lastProvider: Double?
    private var lastTranscript: Double?
    public init() {}
    public mutating func sent(samples: Int, rate: Double, at seconds: Double) {
        guard samples > 0, rate.isFinite, rate > 0, seconds.isFinite else { return }
        value.sentBatches += 1
        value.sentAudioSeconds += Double(samples) / rate
        lastSend = seconds
    }
    public mutating func providerUpdate(at seconds: Double) {
        guard seconds.isFinite else { return }
        value.providerUpdates += 1
        lastProvider = seconds
    }
    public mutating func transcript(characters: Int, at seconds: Double) {
        guard characters >= 0, seconds.isFinite else { return }
        value.transcriptUpdates += 1
        value.transcriptCharacters = characters
        lastTranscript = seconds
    }
    public func snapshot(at seconds: Double) -> MuseStreamSnapshot {
        var result = value
        result.audioSendAgeSeconds = lastSend.map { max(0, seconds - $0) }
        result.providerAgeSeconds = lastProvider.map { max(0, seconds - $0) }
        result.transcriptAgeSeconds = lastTranscript.map { max(0, seconds - $0) }
        return result
    }
}
