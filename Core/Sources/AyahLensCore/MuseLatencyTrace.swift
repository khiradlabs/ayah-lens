public struct MuseLatencyTrace: Sendable {
    public private(set) var firstTranscriptMilliseconds: Double?
    public private(set) var firstMatchAfterTranscriptMilliseconds: Double?
    public private(set) var peakAudioGapMilliseconds: Double?
    private var audioStart: Double?
    private var firstPartial: Double?
    public init() {}
    public mutating func audio(at milliseconds: Double) {
        if audioStart == nil, milliseconds.isFinite { audioStart = milliseconds }
    }
    public mutating func partial(at milliseconds: Double) {
        guard firstPartial == nil, let audioStart, milliseconds.isFinite, milliseconds >= audioStart else { return }
        firstPartial = milliseconds
        firstTranscriptMilliseconds = milliseconds - audioStart
    }
    public mutating func match(at milliseconds: Double) {
        guard firstMatchAfterTranscriptMilliseconds == nil, let firstPartial,
              milliseconds.isFinite, milliseconds >= firstPartial else { return }
        firstMatchAfterTranscriptMilliseconds = milliseconds - firstPartial
    }
    public mutating func gap(_ milliseconds: Double) {
        guard milliseconds.isFinite, milliseconds >= 0 else { return }
        peakAudioGapMilliseconds = max(peakAudioGapMilliseconds ?? 0, milliseconds)
    }
}
