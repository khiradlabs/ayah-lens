#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
mkdir -p build/quran-probe
xcrun swiftc -swift-version 6 -O -parse-as-library \
  Core/Sources/AyahLensCore/Recognition.swift Core/Sources/AyahLensCore/QuranIndex.swift \
  tools/probe_quran.swift -o build/quran-probe/probe
build/quran-probe/probe
