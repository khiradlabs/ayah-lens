# Next: complete-Quran retrieval and Muse Spark integration

Status: Full-Quran scope is explicit. The next milestone is the complete 114-surah, 6,236-ayah corpus plus a useful Muse Spark ambiguity layer. Do not substitute a sequence of extra short-surah demos. Build 18 remains the installed seven-ayah baseline.

## First action

Read SPEC.md and CHECKPOINT.md. Start the full-corpus implementation plan from the existing prepared sources: ../ayah-lens-prep/assets/text/quran-uthmani.txt and en.pickthall.txt. Both have 6,236 unique aligned IDs and contiguous ayah numbers across 114 surahs; this was checked October 27. Preserve canonical strings and existing attribution.

Build a local retrieval index and a bounded candidate matcher outside the UI actor. The current seven-row scan is not appropriate to run over every ayah for every partial. Reuse existing normalization and regression cases where applicable. Check short-opening uniqueness globally; repeated basmala text must not force a false surah lock.

Integrate Muse Spark over ambiguous retrieved candidates with recent verified context. Strictly constrain/validate supplied IDs or abstention; never render model-authored scripture or translation. Strong matches should remain local and immediate. Test stale-response cancellation, invalid IDs and identical-phrase abstention. Compare with matcher-only decisions before claiming value.

## Implementation order

1. Generate and validate the complete aligned reference bundle.
2. Implement/test indexed global retrieval, candidate matching and contextual following.
3. Implement/test the bounded Spark adapter and ambiguity decision flow.
4. Build/install with a distinct visible version/build and verify the physical artifact.
5. Conduct approved live validation across selected different passages and an external reciter source.
6. Collect impact evidence and make the three-minute video.

Consult private gates before billed requests. Voice Transcribe and its runtime key are already set up. Spark access was listed by the model catalog but the app has not made Spark calls. No earlier single-test approval authorizes new Spark spend.

## Existing baseline

Build 18 contains Muse Voice Transcribe, explicit local Omnilingual fallback, Al-Fatihah matching, source-grounded display, latency diagnostics and visible version/build labels. Twenty-five core tests and the PCM/WebSocket probes passed. Actual wearer results are private; check build/logs/latest-muse-observation.json and action gates. Do not repeat version verification questions or hardware setup without new evidence.
