# Ayah Lens

A hackathon prototype that follows Quran recitation and displays canonical Arabic and Pickthall English on Meta Ray-Ban Display glasses.

## Submission drafts

The [submission guide](submission/README.md) links the judging evidence, timed demo script, capture list and exact form answers. The current draft uses Build 28. Final footage, the video URL and entrant ratings remain open.

## Current build

Version 0.3.0, Build 28 contains the complete reference: 114 surahs and 6,236 aligned ayahs. Global passage lookup requires no surah selection.

Muse Voice Transcribe supplies realtime Arabic partial transcripts. An indexed matcher retrieves candidates outside the phone UI actor. Muse Spark 1.3 can resolve ambiguous candidates using the transcript and recent verified position. Spark returns a supplied verse ID or abstention. Only the attributed reference supplies displayed Quran text and translation.

Spark is an explicit opt-in. Ambiguous-verse resolution permits at most three requests per run; source alignment has a separate three-new-verse limit. Requests are bounded, deduplicated and cancelled or rejected when superseded. Strong reference matches update immediately. Identical shared phrases can remain unresolved until distinguishing evidence arrives.

Live long ayahs now follow recitation automatically inside the ayah. An actor tracks the supported source-word position from Muse transcripts and selects a compact portion. The listening lens has no Next/Previous controls.

Muse Spark can pair consecutive source-word ranges from the Arabic and published Pickthall reference. Independent checks reject reordered, incomplete, oversized or source-mismatched plans. The app displays only exact source slices. Accepted plans are cached. The bundle includes 20 paired portions each for 2:102 and 73:20, plus 14 for 2:255. Other long ayahs follow Arabic immediately while an uncached paired translation is prepared, with at most three new alignment requests per run. The full translation stays on the phone when no valid alignment is available. This is transcript-based phrase following, not acoustic word timing. Manual pagination remains a separate stopped-session display test.

The separately labelled local fallback uses Meta Omnilingual CTC-300M through a prepared CoreML export. It uses five-second windows. Muse mode sends audio to Meta; local fallback performs recognition on the phone. The app saves no audio recordings.

## Verified and pending

Fifty-two core tests passed, including corpus coverage, global retrieval, shared-phrase abstention, Spark bounds and response validation, and exact page reconstruction. Actual Swift clients passed local synthetic WebSocket and HTTP integration probes. The PCM callback passed its worker-queue regression. Signed build, installation, installed-version verification and application launch passed.

Whole-Quran index queries were measured on a Mac. This is a host performance probe, not phone or visible-lens latency. Full corpus availability and selected passing cases do not establish accuracy for every ayah.

Real Standard Muse Spark validation passed three synthetic cases: one noisy phrase recovered from matcher abstention and two shared phrases correctly left unresolved. The recovery took 3.28 seconds; abstentions took 0.71 and 1.39 seconds. One abstention case is an adapter control that the app correctly suppresses before calling Spark. This small diagnostic does not establish representative accuracy or live user benefit. Build 23 physical verse advancement passed. The new automatic within-ayah lens layout and external-reciter accuracy still need physical validation. Hardware observations and approval records are maintained privately.

## Check and build

Requires a compatible Swift 6 toolchain, Xcode, an iPhone, Meta AI Developer Mode and the glasses developer component.

```bash
bash tools/test.sh
python3 tools/probe_muse.py
python3 tools/probe_spark.py
bash tools/probe_quran.sh
python3 tools/evaluate_spark.py  # offline preflight only
bash tools/probe_portions.sh
python3 tools/prepare_phrase_alignments.py  # offline/cache validation only
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

Build 22 adds numeric stream diagnostics separating successful audio sends, provider-progress events and transcript updates. The private app snapshot contains no raw text, audio or credentials. Retrieve it with `python3 tools/read_muse_diagnostics.py` after setting AYAH_DEVICE_ID. This instrumentation has 37 passing core tests; it is not evidence that a stalled stream is fixed. Build 23 corrects a reproduced cumulative passage-change issue by checking globally unique recent exact evidence before older-context ranking. The cumulative Al-Fatihah-to-Al-Ikhlas regression passed all four transitions; removing the correction reproduced all four failures. Physical verse advancement was subsequently confirmed. Spark labels also reset after Stop and direct reference matches.

## Automatic portion verification

Fifty-two core tests passed, including all-corpus Arabic size/source preservation, same-ayah movement, middle entry, repeated/unrelated phrases, late cache application and every bundled paired portion. The optimized integration probe passed 52 supported transitions through global lookup and the actual follower actor. Two shared opening portions of 2:255 correctly remained unresolved until distinguishing evidence arrived. These host checks do not establish physical clipping, recitation accuracy or acoustic latency.

Individual aligned portions remain bounded to 56 Arabic grapheme clusters and 100 English characters. The live reading window includes the current plus next portion when their combined size fits 84 Arabic grapheme clusters and 150 English characters. It has a compact header and no navigation buttons. Screen fit requires the actual glasses test. The separate prepare_phrase_alignments.py --live command makes up to three paid source-only Spark requests when authorized; cache hits make no call.

Build 28 mirrors the selected window on the phone, with Full ayah separately expandable. Its newest-frame sender keeps one display send in flight and one latest pending window. Recognition processing no longer awaits each SDK send. Stop invalidates pending frames. Diagnostics separately report queue wait, SDK completion, peak SDK duration and superseded frames. These changes passed controlled async tests; actual lens delay and the larger window's physical fit require a wearer check.
