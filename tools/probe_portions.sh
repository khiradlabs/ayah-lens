#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
mkdir -p build/portion-probe
xcrun swiftc -swift-version 6 -O -parse-as-library \
  Core/Sources/AyahLensCore/Recognition.swift \
  Core/Sources/AyahLensCore/QuranIndex.swift \
  Core/Sources/AyahLensCore/VersePagination.swift \
  Core/Sources/AyahLensCore/LensReadingWindow.swift \
  Core/Sources/AyahLensCore/RecitationPortions.swift \
  Core/Sources/AyahLensCore/MuseSpark.swift \
  tools/probe_portions.swift -o build/portion-probe/probe
build/portion-probe/probe
