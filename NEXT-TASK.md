# Next Ayah Lens task

Read SPEC.md and the latest CHECKPOINT.md entry. Version 0.2.0 Build 22 is the diagnostic artifact. Verify its device installation receipt before the next run. The runtime key is already in device-only Keychain. Do not repeat provisioning or hardware setup without evidence of a new failure.

## Immediate validation

1. Reproduce the stalled Muse transcript with diagnostic Build 22. Consult private build/logs/stalled-recitation-investigation.md for the current observation.
2. Retrieve numeric boundary counters with AYAH_DEVICE_ID set and python3 tools/read_muse_diagnostics.py. Compare successful audio sends, provider updates and transcript updates before changing recognition behavior. Do not copy raw audio or transcript.
3. Resolve the localized failure with a failing regression and check the same physical symptom.
4. Separately fix the reproduced cumulative passage-change retrieval defect. Full Al-Fatihah followed by Al-Ikhlas can omit the new surah from candidates. See private build/logs/stalled-recitation-investigation.md and build/spark-evaluation/replay.swift.
5. Resume selected live passages, long-page navigation, external reciter and scoring/video work after the stream is stable.

Muse validation spending was authorized October 28. Do not repeat that approval request within the bounded validation. Standard Spark passed three synthetic provider cases; real wearer benefit remains unverified.

## Current implementation

All 114 surahs and 6,236 aligned ayahs are bundled. Global retrieval runs outside the UI actor. Muse Voice supplies realtime transcripts. Spark is opt-in, supplies only a retrieved ID or abstention, and permits at most three calls per run. Long ayahs use manual bounded pages. Source availability is not all-ayah recognition validation.

Thirty-seven core tests, callback regression, synthetic WebSocket/HTTP probes and a global-query host probe passed. Signed installation and device version verification passed. Physical tests for this new whole-Quran build remain pending. Keep paid-test consent, real audio and wearer-specific observations out of public commits.
