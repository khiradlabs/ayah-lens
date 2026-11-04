#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
mkdir -p build/model-probe
xcrun swiftc -swift-version 6 -O -parse-as-library \
  Core/Sources/AyahLensCore/Recognition.swift \
  Core/Sources/AyahLensCore/OmnilingualEngine.swift \
  tools/probe_model.swift -o build/model-probe/probe
build/model-probe/probe App/Resources/Omnilingual
