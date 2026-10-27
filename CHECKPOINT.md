# Ayah Lens implementation checkpoint

October 26, 2026. The wearer reported successful registration but display startup failed with no eligible devices. A device-discovery startup race was corrected and the updated signed build installed. Relaunch was blocked because the phone was locked. Actual lens output remains unverified.

## Done and verified

- First implementation commit: `1afb04b` on `feat/glasses-loop`. Contains original SwiftUI interface, manual verse display, Bluetooth-HFP-only capture, session sequencing, core tests and tooling.
- `swift test --package-path Core` under Xcode's DEVELOPER_DIR: four tests passed, zero failures. Session ordering/cleanup and audio-level tests were observed failing before implementation. Local receipts: `build/logs/session-sequence-red.log`, `audio-meter-red.log`, `core-tests.log`.
- `bash tools/build.sh signed`, with the selected phone supplied through AYAH_DEVICE_ID: BUILD SUCCEEDED. Local receipt: `build/logs/build.log`.
- `python3 tools/device.py install`: signature and selected-team/device profile checks passed; installation succeeded. Receipt: `build/logs/install.json`.
- `python3 tools/device.py launch`: application launch succeeded. Receipt: `build/logs/launch.json`.
- Seven Al-Fatihah ayahs and Pickthall translations were compared verbatim against prepared source files. Original Tanzil copyright/usage notice is preserved and bundled. Plist/project configuration checks passed.
- Earlier stock-sample checks: wearer confirmed lens tutorial output, clear wearer audio and clear external-device recitation. External audio quality varied with head movement/direction.

## Decisions

- Organizer clarification and the kickoff slide permit new work October 26 through November 4. The earlier October 27 restriction is superseded.
- First iPhone prototype uses native SwiftUI directly on DAT 1.0.1. The earlier Expo bridge is deferred to reduce integration work.
- The current build explicitly labels manual verse selection and says recognition is not connected. The microphone meter uses actual captured sample data.
- Prototype scope excludes battery endurance and broad production hardening. Prioritize the rubric and a repeatable three-minute demonstration.

## Display startup correction

- The original integration created AutoDeviceSelector inside display startup and immediately created a session. Meta SDK AGENTS.md explicitly requires retained selection or waiting for a non-nil active device.
- The selector now lives from app startup, the controls reflect display eligibility, and session creation waits for discovery. Cancellation and a bounded timeout release hardware.
- Seven core tests passed with zero failures. Removing the readiness fix reproduced two failures; restoring it returned all seven to green. Receipts: `build/logs/display-readiness-red.log`, `display-readiness-reverse-red.log`, `core-tests.log`.
- Updated signed build: BUILD SUCCEEDED. Signature/profile checks and installation passed. Launch failed because the iPhone was locked.
- Local SDK evidence also contained transport errors. This correction addresses a confirmed integration race; it does not establish that every hardware blocker is resolved.

## Pending

- Wearer confirmation that Arabic/English are readable and remain visible while captured sample count increases. This needs physical glasses observation; unit tests cannot establish it.
- If native Arabic rendering fails, test a phone-rendered image fallback. If HFP/display coexistence fails, inspect the actual session error before choosing an in-stream PCM alternative.
- Recognition, a narrow Spark contribution, user-benefit evaluation and video production remain unimplemented.
- No paid API call or cloud audio upload occurred in this milestone.

## Files and conventions

- `SPEC.md`: scope and acceptance.
- `App/`: hardware/UI adapters and attributed reference content.
- `Core/`: testable session ordering and audio levels.
- `tools/test.sh`, `tools/build.sh`, `tools/device.py`: repeatable verification and device workflow.
- Keep build outputs, device identifiers, provisioning files, recordings and credentials outside Git. Local receipts under ignored `build/` are not public artifacts.
