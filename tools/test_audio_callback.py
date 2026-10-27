#!/usr/bin/env python3
"""Run the app's actual tap closure on a worker queue under Swift 6 isolation checks.

The device-only audio route is stubbed; buffer allocation and callback execution
use AVFoundation. This checks callback isolation, not Bluetooth availability.
"""
from pathlib import Path
import os
import subprocess

root = Path(__file__).resolve().parents[1]
source = (root / "App/GlassesMicrophone.swift").read_text()
start = source.index(" {", source.index("engine.inputNode.installTap("))
end = source.index("\n            tapInstalled = true", start)
callback = source[start:end].strip()
fixture = '''import AVFoundation
import Dispatch

// AVAudioSession routing is iOS-only. Always expose a synthetic HFP route here.
struct AVAudioSession {
    enum Port { case bluetoothHFP }
    struct Input { let portType = Port.bluetoothHFP }
    struct Route { let inputs = [Input()] }
    static func sharedInstance() -> Self { Self() }
    let currentRoute = Route()
}
struct CallbackBox: @unchecked Sendable {
    let callback: AVAudioNodeTapBlock
}
@MainActor
func makeCallback(onLevel: @escaping @Sendable (AudioLevel) -> Void) -> AVAudioNodeTapBlock {
    return CALLBACK
}
@main struct Probe {
    @MainActor static func main() {
        let completed = DispatchSemaphore(value: 0)
        let box = CallbackBox(callback: makeCallback { level in
            precondition(level.sampleCount == 4)
            precondition(level.decibels == 0)
            print("PASS: app tap processed four samples on a worker queue")
        })
        DispatchQueue.global().async {
            let format = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!
            let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: 4)!
            buffer.frameLength = 4
            for index in 0..<4 { buffer.floatChannelData![0][index] = 1 }
            box.callback(buffer, AVAudioTime(sampleTime: 0, atRate: 16000))
            completed.signal()
        }
        precondition(completed.wait(timeout: .now() + 5) == .success)
    }
}
'''.replace("CALLBACK", callback)
output = root / "build/audio-callback-probe"
output.mkdir(parents=True, exist_ok=True)
probe = output / "probe.swift"
probe.write_text(fixture)
env = dict(os.environ, DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer")
subprocess.run(["xcrun", "swiftc", "-swift-version", "6", "-parse-as-library",
                str(probe), str(root / "Core/Sources/AyahLensCore/AudioLevel.swift"),
                "-o", str(output / "probe")], env=env, check=True)
result = subprocess.run([str(output / "probe")], capture_output=True, text=True)
(output / "result.log").write_text(result.stdout + result.stderr)
print(result.stdout.strip())
if result.returncode:
    print(f"FAIL: worker-queue tap exited {result.returncode}; see build/audio-callback-probe/result.log")
passed = result.returncode == 0 and "PASS: app tap processed four samples" in result.stdout
if result.returncode == 0 and not passed:
    print("FAIL: the tap never delivered measured samples")
raise SystemExit(0 if passed else 1)
