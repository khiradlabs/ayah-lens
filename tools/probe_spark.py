#!/usr/bin/env python3
"""Probe the real Spark HTTP client against a local synthetic server. No Meta calls."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import subprocess
import threading

root = Path(__file__).resolve().parents[1]
output = root / "build/spark-probe"
output.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer")
subprocess.run(["xcrun", "swiftc", "-swift-version", "6", "-parse-as-library",
                "Core/Sources/AyahLensCore/Recognition.swift", "Core/Sources/AyahLensCore/MuseSpark.swift",
                "tools/probe_spark.swift", "-o", str(output / "probe")], cwd=root, env=env, check=True)
failures = []
requests = []

class Server(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_POST(self):
        try:
            size = int(self.headers["Content-Length"])
            assert size <= 16000
            assert self.headers["Authorization"] == "Bearer synthetic-test-key"
            request = json.loads(self.rfile.read(size))
            assert request["model"] == "muse-spark-1.3"
            schema = request["response_format"]["json_schema"]
            assert schema["strict"] is True
            assert set(schema["schema"]["properties"]["verse_id"]["enum"]) == {"1:2", "37:182", "abstain"}
            assert request["max_completion_tokens"] == 512
            assert request["reasoning_effort"] == "minimal"
            selected = ["37:182", "999:999", "abstain"][len(requests)]
            requests.append(request["model"])
            body = json.dumps({"choices": [{"finish_reason": "stop", "message": {"content": json.dumps({"verse_id": selected})}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:
            failures.append(str(exc))
            self.send_error(500)

server = HTTPServer(("127.0.0.1", 0), Server)
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    result = subprocess.run([str(output / "probe"), f"http://127.0.0.1:{server.server_port}/chat/completions"],
                            capture_output=True, text=True, timeout=30)
    (output / "result.log").write_text(result.stdout + result.stderr)
    print(result.stdout.strip())
    assert result.returncode == 0, "Spark probe failed; see build/spark-probe/result.log"
    assert not failures and len(requests) == 3, failures
    print("PASS: local HTTP server verified Standard Muse Spark, strict schema and request bounds")
finally:
    server.shutdown()
    server.server_close()
