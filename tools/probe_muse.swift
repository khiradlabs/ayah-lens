import Foundation

actor ProbeResults {
    var texts: [String] = []
    var failure: String?
    var gap: Double?
    func append(_ text: String) { texts.append(text) }
    func fail(_ message: String) { failure = message }
    func progress(_ gap: Double) { self.gap = gap }
}

@main
struct MuseProbe {
    static func main() async throws {
        let client = MuseVoiceClient(endpoint: URL(string: CommandLine.arguments[1])!)
        let results = ProbeResults()
        do {
            try await client.sendAudio(MuseAudioChunk(samples: [0], sampleRate: 24000), sessionID: UUID())
            fatalError("Audio must not be sent before acknowledgement")
        } catch MuseError.notConnected { print("PASS: audio blocked before Muse handshake") }
        let id = try await client.connect(apiKey: "synthetic-test-key", onTranscript: { text in
            Task { await results.append(text) }
        }, onFailure: { message in Task { await results.fail(message) } },
        onAudioGap: { gap in Task { await results.progress(gap) } })
        try await client.sendAudio(MuseAudioChunk(samples: [Float](repeating: 0.25, count: 2048), sampleRate: 16000), sessionID: id)
        for _ in 0..<100 {
            if await results.texts.count >= 2 { break }
            try await Task.sleep(for: .milliseconds(20))
        }
        let texts = await results.texts
        precondition(texts == ["الحمد", "الحمد لله رب العالمين"])
        let match = VerseMatcher(verses: [Verse(id: "1:2", arabic: "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ", translation: "")])
            .match(texts.last!, previous: nil)
        precondition(match == "1:2")
        let gap = await results.gap
        precondition(gap != nil && gap! >= 50 && gap! <= 200)
        print("PASS: real WebSocket client exposed audio processing progress")
        print("PASS: real WebSocket client received cumulative partials and selected canonical verse 1:2")
        await client.finish(sessionID: id)
        try await Task.sleep(for: .milliseconds(150))
        let failure = await results.failure
        precondition(failure == nil)
        print("PASS: endStream and normal server closure completed")
    }
}
