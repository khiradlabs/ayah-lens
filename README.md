# Ayah Lens

A hackathon prototype for following Quran recitation with Arabic text and a published translation on Meta Ray-Ban Display glasses.

## Status

Implementation started October 26, 2026 after Faraz relayed organizer clarification and supplied the kickoff rules slide. Separate stock-sample checks established wearer-observed lens output and audio playback. Combined operation and Arabic rendering are the first application milestone.

The kickoff rules state new work may be built October 26 through November 4. Competition code is identified separately from preparation and third-party dependencies. See [SPEC.md](SPEC.md).

## What we aim to demonstrate

- Listen to a reciter through a verified glasses microphone path.
- Identify the verse and show its Arabic text and a published translation.
- Follow a short passage without manual verse lookup.
- Handle selected pauses, repeated phrases and ambiguous matches.
- Demonstrate a useful, verifiable role for Meta models.

These are prototype goals, not claims of completed capabilities. All-day operation and production deployment are outside the hackathon scope.

## Planned approach

An iPhone companion application connects through Meta's Wearables Device Access Toolkit. We will compare Meta Muse Voice Transcribe with Meta Omnilingual ASR before choosing the prototype recognition path. A verse matcher selects canonical text. Muse Spark may help resolve ambiguity or select source-backed answers after its contribution is validated.
The first application is native SwiftUI. The current hardware-check build uses manual verse selection and a real microphone meter; speech recognition is not connected yet.

Arabic and published translations come from attributed sources. Generative models will not author replacement Quran text or translations.

## Verification priorities

1. Prove real glasses audio capture and actual lens output.
2. Demonstrate a correct short live passage.
3. Record verse-match accuracy, false matches and time to stable text on a small documented evaluation.
4. Rehearse a repeatable three-minute demonstration.

The microphone test includes an external reciter because hearing the wearer does not establish that the glasses can follow someone else.

## Project provenance and licensing

See [CONTRIBUTIONS.md](CONTRIBUTIONS.md) for the event-work boundary and dependency attribution.

Original code in this repository is MIT licensed. Third-party models, SDKs, datasets, fonts and translations retain their own licences. Dataset access does not establish permission to redistribute recordings or upload participants' voices to another service.

Secrets, private recordings, datasets, downloaded model weights and local evaluation artifacts must not be committed.

## Build and check

Requires Xcode 27.1 or a compatible Swift 6 toolchain, a connected iPhone, Meta AI Developer Mode, and the glasses developer component.

```bash
bash tools/test.sh
bash tools/build.sh unsigned
```

For a signed device build, set `AYAH_DEVICE_ID` from Xcode's current physical-device list and use your development team in the generated project settings.

```bash
bash tools/build.sh signed
python3 tools/device.py install
python3 tools/device.py launch
```

On the phone, register the app with the glasses. Check **Show selected verse on lens** first, then **Start microphone + lens**. Verify actual lens visibility and increasing sample count together. Report the result; this repository does not claim combined hardware success from unit tests alone.

October 26 first-build verification: four core tests passed; signed device build, provisioning verification, installation and app launch succeeded. Arabic lens readability and simultaneous audio/display are awaiting wearer confirmation. No live recognition result is claimed.
