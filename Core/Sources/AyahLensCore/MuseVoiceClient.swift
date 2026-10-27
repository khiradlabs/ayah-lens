import Foundation

public struct MuseAudioChunk: Sendable {
    public let samples: [Float]
    public let sampleRate: Double
    public init(samples: [Float], sampleRate: Double) { self.samples = samples; self.sampleRate = sampleRate }
}

/// Foreground prototype client. The key is provided at runtime, never bundled.
public actor MuseVoiceClient {
    private let endpoint: URL
    private var socket: URLSessionWebSocketTask?
    private var reader: Task<Void, Never>?
    private var timeout: Task<Void, Never>?
    private var epoch = UUID()
    private var ready = false
    private var ending = false
    private var encoder = MusePCMEncoder()
    private var sentBytes = 0

    public init(endpoint: URL = URL(string: "wss://api.meta.ai/v1/asr/realtime")!) { self.endpoint = endpoint }

    public func connect(apiKey: String,
                        onTranscript: @escaping @Sendable (String) -> Void,
                        onFailure: @escaping @Sendable (String) -> Void) async throws -> UUID {
        cancel()
        let id = epoch
        var request = URLRequest(url: endpoint)
        request.timeoutInterval = 15
        let socket = URLSession.shared.webSocketTask(with: request)
        socket.maximumMessageSize = 1_048_576
        self.socket = socket
        socket.resume()
        timeout = Task { [weak self] in
            do { try await Task.sleep(for: .seconds(10)) } catch { return }
            await self?.cancelIfCurrent(id)
        }
        do {
            // Meta authenticates the first JSON frame, not the HTTP upgrade headers.
            let handshake = try MuseProtocol.handshake(apiKey: apiKey)
            try await socket.send(.string(String(decoding: handshake, as: UTF8.self)))
            guard case .string(let acknowledgement) = try await socket.receive(),
                  let object = try JSONSerialization.jsonObject(with: Data(acknowledgement.utf8)) as? [String: Any],
                  let session = object["sessionId"] as? String, !session.isEmpty,
                  epoch == id else { throw MuseError.rejected }
            timeout?.cancel(); timeout = nil
            ready = true
            reader = Task { [weak self] in
                await self?.readEvents(socket: socket, id: id, onTranscript: onTranscript, onFailure: onFailure)
            }
            return id
        } catch {
            cancelIfCurrent(id)
            throw MuseError.rejected
        }
    }

    public func sendAudio(_ chunk: MuseAudioChunk, sessionID: UUID) async throws {
        guard ready, !ending, epoch == sessionID, let socket else { throw MuseError.notConnected }
        let data = try encoder.encode(chunk.samples, sampleRate: chunk.sampleRate)
        guard sentBytes + data.count <= 24000 * 2 * 120 else { throw MuseError.testLimit }
        sentBytes += data.count
        if !data.isEmpty { try await socket.send(.data(data)) }
    }

    public func finish(sessionID: UUID) async {
        guard epoch == sessionID, ready, !ending, let socket else { return }
        ending = true
        ready = false
        try? await socket.send(.string("{\"type\":\"endStream\"}"))
        // Continue reading final results. Bound cleanup if the server never closes.
        guard epoch == sessionID else { return }
        timeout = Task { [weak self] in
            do { try await Task.sleep(for: .seconds(3)) } catch { return }
            await self?.cancelIfCurrent(sessionID)
        }
    }

    private func readEvents(socket: URLSessionWebSocketTask, id: UUID,
                            onTranscript: @escaping @Sendable (String) -> Void,
                            onFailure: @escaping @Sendable (String) -> Void) async {
        var state = MuseTranscriptState()
        do {
            while !Task.isCancelled, epoch == id {
                let frame = try await socket.receive()
                guard epoch == id else { return }
                if case .string(let message) = frame, let text = try state.consume(message) { onTranscript(text) }
            }
        } catch {
            guard epoch == id else { return }
            let expected = ending
            cancel()
            if !expected { onFailure(MuseError.connection.localizedDescription) }
        }
    }

    private func cancelIfCurrent(_ id: UUID) { if epoch == id { cancel() } }
    private func cancel() {
        epoch = UUID(); ready = false; ending = false; sentBytes = 0
        encoder = MusePCMEncoder()
        reader?.cancel(); reader = nil
        timeout?.cancel(); timeout = nil
        socket?.cancel(with: .goingAway, reason: nil); socket = nil
    }
}
