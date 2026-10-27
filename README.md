# Ayah Lens

A hackathon prototype for following Quran recitation with Arabic text and a published translation on Meta Ray-Ban Display glasses.

## Status

Implementation started October 26, 2026 after Faraz relayed organizer clarification and supplied the kickoff rules slide. The wearer confirmed Arabic/English lens output with simultaneous glasses microphone capture. The next build implements local Al-Fatihah recognition; the wearer reported most ayahs worked, with one or two missed in the first live test.

The kickoff rules state new work may be built October 26 through November 4. Competition code is identified separately from preparation and third-party dependencies. See [SPEC.md](SPEC.md).

## What we aim to demonstrate

- Listen to a reciter through a verified glasses microphone path.
- Identify the verse and show its Arabic text and a published translation.
- Follow a short passage without manual verse lookup.
- Handle selected pauses, repeated phrases and ambiguous matches.
- Demonstrate a useful, verifiable role for Meta models.

These are prototype goals, not claims of completed capabilities. All-day operation and production deployment are outside the hackathon scope.

## Planned approach

The native SwiftUI iPhone application connects through Meta's Wearables Device Access Toolkit. Meta Omnilingual ASR CTC-300M runs locally through the prepared CoreML INT8 export. Five-second windows update at one-second intervals when inference keeps up. A silence gate avoids inference below the prototype threshold. The Arabic-only CTC decoder feeds a deterministic verse matcher restricted to Al-Fatihah.

The matcher uses normalized recognition copies, edit distance and fragment length. Short, unrelated or ambiguous fragments hold the existing verse. Established verse order can distinguish the shared basmala phrase; repetition can move back to an earlier verse. These are heuristics, not calibrated confidence or proven recognition accuracy. A later Muse Voice Transcribe comparison and useful Muse Spark role remain pending.

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
# Before building live recognition, download the 5-second CoreML export below.
# Run this with a Python environment containing sentencepiece.
python tools/prepare_model.py /path/to/Omnilingual-ASR-CTC-300M-CoreML-INT8
bash tools/probe_model.sh
bash tools/build.sh unsigned
```

Model source: [CoreML 5-second export](https://huggingface.co/aufklarer/Omnilingual-ASR-CTC-300M-CoreML-INT8). Supply its compiled model, config.json and tokenizer.model to the preparation helper. The helper does not download or upload audio. Weights and generated vocabulary remain ignored by Git.

For a signed device build, set `AYAH_DEVICE_ID` from Xcode's current physical-device list and use your development team in the generated project settings.

```bash
bash tools/build.sh signed
python3 tools/device.py install
python3 tools/device.py launch
```

On the phone, register the app with the glasses. Check **Show selected verse on lens** first, then **Start microphone + lens**. Verify actual lens visibility and increasing sample count together. Report the result; this repository does not claim combined hardware success from unit tests alone.

For recognition, tap **Stop**, then **Start live Al-Fatihah**. Recite for 20–30 seconds and observe both the phone transcript and actual lens changes. The initial audio window takes five seconds; displayed inference time excludes that collection interval. Manual buttons remain separately labelled. Audio stays on the iPhone and is not saved.

October 26 verification: combined audio/display was confirmed by the wearer. Recognition core tests, worker-queue PCM callback check, local model inference/resampling at 16/24/48 kHz, signed device build and installation passed. The synthetic-audio model probe checks execution, not Quran accuracy. The wearer reported real live-recognition updates for most ayahs, with one or two missed. Exact accuracy and timing remain unmeasured.
