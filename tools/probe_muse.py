#!/usr/bin/env python3
"""Exercise the real Muse WebSocket client against a local synthetic server.

No Meta connection, credential access, paid inference or private recordings.
"""
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import struct
import subprocess
import threading

root = Path(__file__).resolve().parents[1]
output = root / "build/muse-probe"
output.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer")
subprocess.run(["xcrun", "swiftc", "-swift-version", "6", "-parse-as-library",
                "Core/Sources/AyahLensCore/MuseProtocol.swift", "Core/Sources/AyahLensCore/MuseVoiceClient.swift",
                "Core/Sources/AyahLensCore/Recognition.swift", "tools/probe_muse.swift",
                "-o", str(output / "probe")], cwd=root, env=env, check=True)
failures = []


class Server(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_):
        pass

    def read_frame(self):
        first, second = self.rfile.read(2)
        length = second & 127
        if length == 126:
            length = struct.unpack("!H", self.rfile.read(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self.rfile.read(8))[0]
        assert length <= 100000, "Unexpected frame size"
        mask = self.rfile.read(4) if second & 128 else None
        data = self.rfile.read(length)
        if mask:
            data = bytes(value ^ mask[i % 4] for i, value in enumerate(data))
        return first & 15, data

    def send_frame(self, opcode, data):
        header = bytes([128 | opcode])
        header += bytes([len(data)]) if len(data) < 126 else bytes([126]) + struct.pack("!H", len(data))
        self.wfile.write(header + data)
        self.wfile.flush()

    def event(self, payload):
        self.send_frame(1, json.dumps(payload, ensure_ascii=False).encode())

    def do_GET(self):
        try:
            assert "Authorization" not in self.headers, "API key must not be in upgrade headers"
            accept = base64.b64encode(hashlib.sha1((self.headers["Sec-WebSocket-Key"] + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
            self.send_response(101)
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.send_header("Sec-WebSocket-Accept", accept)
            self.end_headers()
            opcode, data = self.read_frame()
            assert opcode == 1
            request = json.loads(data)
            assert request["authorization"]["accessToken"] == "Bearer synthetic-test-key"
            assert request["model"] == "muse-voice-transcribe-1.0"
            assert request["audioEncoding"] == "PCM_24KHZ" and request["languageBias"] == ["Arabic"]
            self.event({"sessionId": "synthetic-session"})
            opcode, audio = self.read_frame()
            assert opcode == 2 and 1000 < len(audio) < 32000 and len(audio) % 2 == 0
            self.event({"type": "speechStart", "turnId": 1})
            self.event({"type": "transcript", "transcript": "الحمد", "final": False})
            self.event({"type": "transcript", "transcript": "الحمد لله رب العالمين", "final": False})
            opcode, data = self.read_frame()
            assert opcode == 1 and json.loads(data) == {"type": "endStream"}
            self.send_frame(8, struct.pack("!H", 1000))
        except Exception as exc:
            failures.append(type(exc).__name__ + ": " + str(exc))
        finally:
            self.close_connection = True


server = HTTPServer(("127.0.0.1", 0), Server)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    result = subprocess.run([str(output / "probe"), f"ws://127.0.0.1:{server.server_port}/realtime"], capture_output=True, text=True, timeout=20)
    (output / "result.log").write_text(result.stdout + result.stderr)
    print(result.stdout.strip())
    assert result.returncode == 0, "Swift WebSocket probe failed; see build/muse-probe/result.log"
    assert not failures, failures
    print("PASS: local server verified handshake, mono PCM and clean end-of-input")
finally:
    server.shutdown()
    server.server_close()
