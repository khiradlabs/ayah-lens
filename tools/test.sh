#!/bin/bash
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
mkdir -p build/logs
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
set +e
swift test --package-path Core > build/logs/core-tests.log 2>&1
result=$?
set -e
tail -25 build/logs/core-tests.log
if [ "$result" -ne 0 ]; then exit "$result"; fi
python3 tools/test_audio_callback.py
