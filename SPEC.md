# Ayah Lens hackathon prototype specification

## Goal

Follow recitation from anywhere in the complete Quran through Meta glasses and display unchanged canonical Arabic plus a published English translation. The delivery target is all 114 surahs and 6,236 ayahs in the prepared reference, not a series of individually selected short-surah demos.

Al-Fatihah was the first integration slice for proving audio, live Muse transcription, matching and lens display. It is not the complete product scope.

The event build window is October 26 through November 4 after organizer clarification. The submission target is November 4, 8 PM Houston time. The implementation is native SwiftUI using Meta Wearables DAT 1.0.1.

## Current implementation

- Version 0.2.0, Build 23 bundles all 6,236 aligned Arabic/Pickthall rows across 114 surahs.
- Muse Voice Transcribe supplies realtime Arabic transcripts. Global indexed retrieval runs outside the UI actor.
- Muse Spark 1.3 is wired as an opt-in candidate resolver with strict supplied-ID validation, abstention and stale-response rejection.
- Spark is limited to three requests per run. Actual provider validation passed three synthetic cases, including one recovery after matcher abstention. Representative live benefit remains pending.
- Long ayahs use bounded, verbatim pages with manual Previous/Next controls. Physical readability and page navigation need testing.
- Thirty-eight core tests, the actual PCM callback, synthetic WebSocket and Spark HTTP probes passed. Signed build/install/version verification passed. Consult the latest checkpoint for Build 23 device launch status.
- Full reference availability and selected regression cases do not establish recognition accuracy for every ayah.

## Delivery requirements

### 1. Canonical corpus

Bundle the full aligned reference and preserve every displayed Arabic/translation string verbatim with existing attribution and notices. Normalize separate recognition copies only. Validate unique IDs, source alignment, nonempty text and complete corpus coverage. No model may author Quran text or a replacement translation.

### 2. Global retrieval

Identify the passage from incoming recitation without requiring the wearer to choose a surah. Use a fast local index to retrieve a small candidate set across the full corpus, then apply detailed matching only to those candidates. Run retrieval outside the UI actor. Do not scale the existing seven-row dynamic-programming scan directly to all rows on the main thread.

Use recent verified verse IDs to follow sequence, pauses, repeats, backtracking and passage changes. Preserve the current fast local path for strong, distinctive evidence. Short-opening shortcuts must be unique in the applicable retrieval context; uniqueness inside Al-Fatihah alone is insufficient for the whole corpus.

Shared basmala phrases and other identical text may remain unresolved until more context arrives. Keep the last verified display or show an identifying status. Do not invent a surah assignment to make the UI advance.

### 3. Muse Spark decision layer

Integrate Muse Spark as a bounded ambiguity resolver over retrieved candidates and recent verified context. It receives the ASR fragment as untrusted data, a small candidate list and recent position. Constrain output to supplied verse identifiers or abstention, then independently validate the identifier before canonical lookup.

Strong local matches should remain immediate. Invoke Spark only where its contribution is useful, not for every streaming partial. Deduplicate in-flight requests and discard stale responses after Stop or a newer passage decision. Identical phrases without distinguishing context require abstention; a model cannot supply missing evidence.

Measure matcher-only versus matcher-plus-Spark decisions on shared phrases and noisy fragments. Claim a benefit only after the comparison demonstrates one. Spark does not generate displayed Quran text, translations or unvalidated religious rulings.

## Acceptance

- All 6,236 Arabic and translation rows are bundled, aligned and unchanged.
- Global retrieval handles distinctive samples from different surahs and middle-of-surah entry without manual selection.
- Identical/shared fragments are handled as ambiguous when evidence is insufficient.
- A short live run samples more than the original passage, including an external recitation source with permission.
- Pauses, repeats and passage changes have regression tests and selected live checks.
- Spark protocol/response validation has local tests; a real approved Spark call and measured comparison establish actual integration.
- The phone and lens identify Muse versus local fallback. Every tested artifact shows version and build.
- Report measured initial-session timings separately from per-ayah or word-aligned display delay. SDK send completion does not prove visible pixels at that instant.

## Boundaries

This is a foreground hackathon prototype. Battery endurance, exhaustive background/locked-phone operation, production accounts, App Store release and broad environmental hardening remain deferred.

Keep a verified HFP-only microphone route; do not silently substitute the phone microphone. Retain audio-first display startup, bounded queues, cleanup and cancellation. No keys in the app bundle, source, chat or logs; the current key is provisioned privately into device-only Keychain.

Live paid calls and external audio transfer must fit the current private authorization scope. An earlier single Voice Transcribe test does not authorize ongoing spend, dataset upload or Spark calls. Prepare concrete testable code before requesting the final paid validation approval.

## Follow-on scoring work

After full-Quran retrieval and the meaningful Spark role are validated, collect a small user-benefit evaluation and produce the three-minute video with actual lens output, clear model roles, new-work provenance and honest evidence. Additional isolated-surah expansion is superseded by complete-corpus integration.
