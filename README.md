# Ayah Lens

A hackathon prototype that follows Quran recitation and displays canonical Arabic and Pickthall English on Meta Ray-Ban Display glasses.

## Current build

Version 0.2.0, Build 22 contains the complete reference: 114 surahs and 6,236 aligned ayahs. Global passage lookup requires no surah selection.

Muse Voice Transcribe supplies realtime Arabic partial transcripts. An indexed matcher retrieves candidates outside the phone UI actor. Muse Spark 1.3 can resolve ambiguous candidates using the transcript and recent verified position. Spark returns a supplied verse ID or abstention. Only the attributed reference supplies displayed Quran text and translation.

Spark is an explicit opt-in and permits at most three requests per run. Requests are bounded, deduplicated and cancelled or rejected when superseded. Strong reference matches update immediately. Identical shared phrases can remain unresolved until distinguishing evidence arrives.

Long ayahs have separate Arabic and Pickthall pages with manual Previous/Next controls. These pages preserve every source character. They do not claim word alignment.

The separately labelled local fallback uses Meta Omnilingual CTC-300M through a prepared CoreML export. It uses five-second windows. Muse mode sends audio to Meta; local fallback performs recognition on the phone. The app saves no audio recordings.

## Verified and pending

Thirty-five core tests passed, including corpus coverage, global retrieval, shared-phrase abstention, Spark bounds and response validation, and exact page reconstruction. Actual Swift clients passed local synthetic WebSocket and HTTP integration probes. The PCM callback passed its worker-queue regression. Signed build, installation, installed-version verification and application launch passed.

Whole-Quran index queries were measured on a Mac. This is a host performance probe, not phone or visible-lens latency. Full corpus availability and selected passing cases do not establish accuracy for every ayah.

Real Standard Muse Spark validation passed three synthetic cases: one noisy phrase recovered from matcher abstention and two shared phrases correctly left unresolved. The recovery took 3.28 seconds; abstentions took 0.71 and 1.39 seconds. One abstention case is an adapter control that the app correctly suppresses before calling Spark. This small diagnostic does not establish representative accuracy or live user benefit. Selected live passage changes, external-reciter testing and long-page readability remain pending. Hardware observations and approval records are maintained privately.

## Check and build

Requires a compatible Swift 6 toolchain, Xcode, an iPhone, Meta AI Developer Mode and the glasses developer component.

```bash
bash tools/test.sh
python3 tools/probe_muse.py
python3 tools/probe_spark.py
bash tools/probe_quran.sh
python3 tools/evaluate_spark.py  # offline preflight only
```

The local fallback requires the prepared model. Download the [CoreML five-second export](https://huggingface.co/aufklarer/Omnilingual-ASR-CTC-300M-CoreML-INT8), then run the preparation helper with sentencepiece installed:

```bash
python3 tools/prepare_model.py /path/to/Omnilingual-ASR-CTC-300M-CoreML-INT8
bash tools/build.sh unsigned
```

To regenerate the Quran reference, supply aligned Tanzil Uthmani and Pickthall source files to `tools/prepare_quran.py`. The helper validates all IDs and round-trips exact strings. See its command-line help.

For device work, set AYAH_DEVICE_ID from Xcode's physical device list and configure your signing team.

```bash
bash tools/build.sh signed
python3 tools/device.py install
python3 tools/device.py verify
python3 tools/device.py launch
```

The build helper increments the build number. The app shows version/build in its header and timing panel. Device verification compares the installed version with the signed artifact.

## Live testing

Register glasses inside Ayah Lens. Use the manual display and microphone checks to verify hardware first. With the runtime credential installed and a bounded paid test approved, tap **Start Muse live Quran**. Each Muse stream permits two minutes of audio. Spark has a separate opt-in toggle and sends transcript fragments to Meta.

Observe the phone transcript, selected verse and actual lens. Try distinctive passages, pauses and a passage change. Short shared phrases may require more context. Use an external reciter source only with permission.

The Muse timing panel exposes provider processing gap, first text after audio starts, first match after text, matching time and SDK send completion. Startup silence is included. These diagnostics do not measure word-to-visible-pixel delay.

Keys stay outside the bundle and Git in device-only Keychain. The private provisioning helper supports a dry-run and one-time handoff. Never include keys in source, logs or chat.

## Provenance and scope

Implementation began October 26, 2026 after organizer clarification. The kickoff build window ends November 4. See [CONTRIBUTIONS.md](CONTRIBUTIONS.md), [SPEC.md](SPEC.md) and [ATTRIBUTION.md](ATTRIBUTION.md).

Original code is MIT licensed. Third-party SDKs, models and reference content retain their own notices. Preparation and existing models are distinguished from event work. Downloaded weights, credentials, recordings and local evidence are excluded from Git.

This is a foreground hackathon prototype. Battery endurance, production accounts and App Store delivery are deferred. The next scoring milestone is evidence of useful Spark decisions, followed by a three-minute video showing real behavior.

The repeatable synthetic comparison uses `python3 tools/evaluate_spark.py --live` only with paid-call authorization. It loads the private runtime credential, makes exactly three requests without retries, and records decisions under ignored build/spark-evaluation. It sends no audio.

Build 22 adds numeric stream diagnostics separating successful audio sends, provider-progress events and transcript updates. The private app snapshot contains no raw text, audio or credentials. Retrieve it with `python3 tools/read_muse_diagnostics.py` after setting AYAH_DEVICE_ID. This instrumentation has 37 passing core tests; it is not evidence that a stalled stream is fixed. Cumulative passage changes also have a known retrieval issue under investigation.
