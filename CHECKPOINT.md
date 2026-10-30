# Ayah Lens implementation checkpoint

October 26, 2026. Wearer confirmed the corrected combined check: app stayed open, lens text remained visible, and microphone sample count increased while speaking. The core simultaneous audio/display milestone passed. A local recognition slice is implemented and installed. The wearer reported it worked for most of Al-Fatihah, with one or two ayahs missed. This is a partial live-recognition pass; the wearer identified Ar-Rahman ir-Rahim, likely 1:3, as a missed phrase.

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
- Manual hardware controls remain labelled separately. A new Start live Al-Fatihah control connects local recognition; the microphone meter uses actual captured samples.
- Prototype scope excludes battery endurance and broad production hardening. Prioritize the rubric and a repeatable three-minute demonstration.

## Display startup correction

- The original integration created AutoDeviceSelector inside display startup and immediately created a session. Meta SDK AGENTS.md explicitly requires retained selection or waiting for a non-nil active device.
- The selector now lives from app startup, the controls reflect display eligibility, and session creation waits for discovery. Cancellation and a bounded timeout release hardware.
- Seven core tests passed with zero failures. Removing the readiness fix reproduced two failures; restoring it returned all seven to green. Receipts: `build/logs/display-readiness-red.log`, `display-readiness-reverse-red.log`, `core-tests.log`.
- Updated signed build: BUILD SUCCEEDED. Signature/profile checks and installation passed. Launch failed because the iPhone was locked.
- Local SDK evidence also contained transport errors. The wearer subsequently confirmed lens text works. Transport errors alone did not establish a remaining display blocker.

## Combined-mode crash correction

- Wearer confirmed text works, then reported that combined mode closes the app and returns.
- The retrieved phone crash report identified an actor-isolation trap in the AVAudioEngine tap on its worker queue.
- Marked the tap closure explicitly `@Sendable`; the UI still receives measured values on its actor.
- `tools/test_audio_callback.py` executes the actual app closure with AVFoundation buffers on a worker queue. Bluetooth routing is synthetic in this host test. The original closure trapped with signal 5; the corrected closure processed four samples at the expected level. Removing the fix reproduced the trap, and restoring it passed.
- All seven core tests passed. Updated signed build and installation passed. Relaunch was blocked by the locked phone. The wearer subsequently confirmed the app stayed open, lens text remained visible, and the sample counter increased while speaking.

## Pending

- Stop/restart behavior has core test coverage but no explicit wearer confirmation. Longer operation, directional robustness and recognition accuracy were not established by this check.
- Retest the identified Ar-Rahman ir-Rahim miss after the bounded transition correction. End-to-end latency, false locks and repeat/stop behavior still need measurement. A measured engine comparison, narrow Spark contribution, user-benefit evaluation and video production remain pending.
- No paid API call or cloud audio upload occurred in this milestone.

## Files and conventions

- `SPEC.md`: scope and acceptance.
- `App/`: hardware/UI adapters and attributed reference content.
- `Core/`: testable session ordering and audio levels.
- `tools/test.sh`, `tools/build.sh`, `tools/device.py`: repeatable verification and device workflow.
- Keep build outputs, device identifiers, provisioning files, recordings and credentials outside Git. Local receipts under ignored `build/` are not public artifacts.

## Local recognition implementation

- Added the prepared Meta Omnilingual CTC-300M 5-second CoreML INT8 export to the local development bundle, outside Git. CPU/Neural Engine inference runs on a serial actor.
- Verified HFP PCM and its actual sample rate feed bounded five-second windows with one-second hops. Quiet windows are skipped. Inference does not queue a backlog; Stop invalidates pending results.
- Arabic-only greedy CTC transcripts feed the original Al-Fatihah fragment matcher. It uses normalized copies, approximate suffix matching, minimum evidence and established verse order for shared phrases. Published display text is unchanged.
- Unsupported/short/ambiguous fragments hold the current verse. This is heuristic evidence, not calibrated model confidence.
- Observed RED before implementation: six new behavior tests yielded ten assertion failures. Final suite: fourteen tests, zero failures. All seven bundled verses, repeated/ambiguous phrases, unrelated/short input, window bounds and CTC blank handling are covered.
- Worker-queue probe passed actual callback sample and rate delivery.
- Actual local CoreML model probe passed at 16/24/48 kHz using synthetic tones; inference and resampling took approximately 28–36 ms per window on this Mac, after model load. This establishes execution only, not phone latency or recitation accuracy. Local receipt: build/logs/model-probe.log.
- Signed iPhone build, signature/profile verification and installation passed. Launch was blocked by the locked phone. The wearer was asked to unlock/open, select Start live Al-Fatihah and recite for 20–30 seconds.
- Model/source attribution and reproducible preparation instructions are in ATTRIBUTION.md and README.md. Generated model/vocabulary artifacts and all local evidence stay outside Git. No paid call, external audio upload or audio recording was used in this slice.

## First live-recognition observation

The wearer reported: “it worked for the most part” with “one or two missed ayats.” This establishes real recitation-driven lens updates, not a complete seven-ayah accuracy pass. Asked which ayahs or phrases were missed before changing recognition behavior. No latency or exact miss count was measured. The model probe timings above are Mac-only execution timings.

## Ar-Rahman ir-Rahim transition correction

- Wearer identified Ar-Rahman ir-Rahim as a likely miss; its exact ASR transcript was not captured.
- Reproduced one matcher defect: a rolling transcript ending “رب العالمين الرحمن الرحيم مالك” after 1:2 returned nil, although 1:3 was supported. The isolated repeated phrase already matched correctly with established sequence.
- If a direct match fails, the matcher can now trim a bounded 3–6-letter tail only when it matches the following ayah’s opening and the remaining transcript independently supports the expected verse. Existing direct later-verse matches win. Unrelated tails or missing sequence remain rejected.
- Fifteen tests passed. The new case failed before implementation, failed again when the fix was temporarily removed, and passed when restored. PCM callback regression remained green. Signed build succeeded.
- This is a reproduced integration defect, not proof of the exact cause of the wearer’s miss. Actual glasses retest remains required. No model, cadence, global threshold or canonical display text changed.
- Local investigation: build/logs/rahman-investigation.md.

Installation of the transition correction passed signature/profile checks and completed. Automatic launch was blocked by the locked iPhone. Open the installed app manually after unlocking for the pending normal-pace retest.

## Muse priority correction

Faraz explicitly required Muse tools on October 26. Current code uses local Meta Omnilingual and DAT; no Muse API is integrated. Updated SPEC.md and NEXT-TASK.md to make Muse Voice Transcribe the next core integration, with local Omnilingual retained as an explicitly labelled fallback. A useful Spark role remains a separate measured milestone.

Verified the official Muse speech protocol and pricing pages. Project credentials contain HF_TOKEN only. Proton Pass connection worked; no matching Meta/Muse/Ayah credential titles were found in the Khirad deployment or business vaults. No secret values were printed. API-key access and bounded paid/cloud-audio test authorization remain required before live Muse verification. No additional app code changed during this clarification.

## Muse credential and client preparation

- Faraz pasted META_API_KEY into the private project credentials file. Its value was never printed. File permissions remain 0600.
- A read-only GET /v1/models accepted the key and listed muse-voice-transcribe-1.0 plus Standard Spark 1.3/1.2/1.1. This establishes authentication/catalog access, not active credits or paid speech success.
- Implemented the native Muse WebSocket client, Arabic-biased handshake authentication, continuous 24 kHz int16 PCM conversion, cumulative partial replacement and turn-aware completion. Actual transcripts feed the existing canonical matcher.
- Added distinct Start Muse live Al-Fatihah and Start local fallback controls. Muse remains disabled until runtime credentials are provisioned. There is no silent automatic fallback.
- Each Muse stream has a two-minute audio cap, bounded audio queue, explicit endStream and bounded final-response cleanup. Keys are loaded from device-only Keychain; tools/provision_muse_key.py supports a private one-time handoff and app restart without including the value in argv or logs. Only its dry-run ran.
- Twenty core tests passed. The five new Muse tests were observed RED first with fourteen assertions failing before implementation. Callback regression passed PCM/sample-rate handoff.
- python3 tools/probe_muse.py passed the actual URLSession WebSocket client against a local synthetic server: no authorization upgrade header; handshake model/Arabic/PCM checked; audio blocked before acknowledgement; binary PCM delivered; synthetic partials selected canonical 1:2; endStream/normal closure passed. No Meta connection or real audio was used by this probe.
- Signed Muse build and installation passed. Keychain import and live Muse transcription/lens behavior are not verified. No live Muse session, paid inference or cloud recitation upload has occurred.
- A compile check caught missing isolation for the Keychain dictionary and await inside a probe assertion; these were corrected before installation. Explicit outer closure capture clears new ownership warnings.
- Next gate: approve one test of up to two minutes using Faraz’s own recitation audio, at most $0.01 under the published $0.18/hour rate. Then provision the key, run live Muse and record actual matching/latency.

## Paused by Faraz

October 26: Faraz requested resuming tomorrow. Working tree was clean at 517dd2c and the prototype branch was pushed. Muse client is installed; the Meta key passed read-only authentication. Device Keychain provisioning has not run. The paid two-minute Muse test remains unapproved. No live Muse speech session or cloud recitation upload occurred. Resume with the pending approval, not another hardware setup sequence.

## Resumed October 27

Faraz requested resuming. The registered physical iPhone was listed as available. The private credential preflight passed without copying the key or contacting Meta. Presented the still-pending approval for one two-minute recitation test costing at most $0.01. No paid session or cloud audio upload has started.

## Muse device setup completed October 27

Faraz asked how to test. Completed the reversible setup without starting inference: privately provisioned the saved key, restarted Ayah Lens successfully, and verified that the temporary Library/muse-key.once handoff no longer exists. App code removes it only after successful Keychain storage. No paid session or audio upload was initiated by the agent. The wearer receives instructions disclosing the small cost and audio transfer before choosing the Muse start button. Earlier notes deferring key setup until paid-test approval were a workflow choice, not a requirement for this non-billable setup. Live Muse result remains unverified.

## Muse timing diagnostics

The current engineering focus is locating recognition-to-display delay. Physical test outcomes and authorization limits are maintained in private local records and action gates; check those before requesting another approval or starting billed tests.

A local benchmark using the bundled reference measured approximately 9.9 ms per matcher call in an unoptimized host build. This is not phone or end-to-end latency. Added provider audio-progress gap, actual matcher duration and lens SDK send-completion duration under the phone’s Muse timing disclosure. Diagnostic values remain visible after Stop. Audio-progress gap is not word timing; send completion does not prove the lens became visible at that instant.

Twenty-one core tests passed after observed diagnostic-test failures. The actual WebSocket client passed a synthetic progress-frame probe. Signed build passed. No model, matching threshold or audio capture cadence changed in this diagnostic slice. New tests ran locally without paid inference. Actual phone timing readings are still needed before choosing a latency fix.

## First-text and peak timing extension

Current-gap snapshots cannot establish cumulative transcript latency or rule out an earlier backlog. Added a monotonic trace for the first nonempty transcript after the first audio buffer, the first supported match after that partial, and peak provider audio gap. The trace persists after Stop and resets for a new Muse session. The first-text interval includes pre-recitation silence; it is not word-aligned end-to-end latency. No audio or transcript is saved by this trace.

Twenty-three tests passed after the two new trace cases were observed failing. PCM and real-WebSocket synthetic probes passed. Signed build passed. The actual screenshot and wearer observations remain in private local investigation notes. No new paid API request was initiated by the agent. Matching thresholds, model and streaming cadence are unchanged.

## Exact short-opening recognition

The source required at least eight letters even for a complete, distinctive two-word opening in the selected passage. Added an exact-match path for unique six/seven-letter opening aliases, retaining word boundaries and accounting for Uthmani dagger-alif recognition spelling. The approximate matcher’s threshold remains unchanged. Shared, incomplete or wrongly split fragments remain rejected, and longer supported suffixes retain precedence. Canonical display content is unchanged.

Twenty-five tests passed after the new opening assertions were observed failing. Reverting the matcher reproduced four failures; restoring the fix returned green. The callback and real-WebSocket synthetic probes passed. Private observations and interpretation remain in build/logs/muse-latency-investigation.md. The actual first partial was not captured, so a physical retest is required before claiming a latency gain. This change does not alter provider first-text emission or stream cadence.

## Visible build identity and installation verification

Build helper now sets an increasing CFBundleVersion using the larger of source revision count or the preceding local artifact plus one. The phone UI shows the bundle version below the subtitle. tools/device.py verify compares installed app metadata with the signed local artifact and fails on mismatch.

A fresh signed build succeeded with the latest short-opening matcher and visible version label. Installation passed, and the device query reported version 0.1.0, build 17, matching the artifact. Earlier device metadata reported build 1. Automatic launch was blocked by the locked phone. No paid Muse request was started. Syntax checks and the actual installed-version probe passed; recognition logic was unchanged from the last twenty-five-test pass.

## Build identity in diagnostic screenshots

Version and build are now shown both in the app header and inside expanded Muse timing. Signed build succeeded; device metadata verified version 0.1.0, build 18 against the newly built artifact. Installation and app launch succeeded. Recognition logic is unchanged. No paid session was started by the agent.

## Full-Quran scope and Spark priority

The target is the complete Quran. Current Build 18 bundles seven Al-Fatihah ayahs and uses Muse Voice Transcribe; Muse Spark is not integrated. The next delivery is complete-corpus indexed retrieval plus a measured, bounded Spark ambiguity resolver. SPEC.md was rewritten as the current scope and NEXT-TASK.md now prioritizes this milestone over individual short-surah additions.

Audited existing prepared sources: both Arabic and Pickthall contain 6,236 unique, nonempty, aligned rows, contiguous within all 114 surahs. This establishes source readiness only. No full corpus was bundled, global recognizer shipped or Spark inference called during this scope clarification.

## Complete-Quran and Spark build, October 27

Current branch: feat/full-quran-muse. Current artifact: Version 0.2.0, Build 21. Signed build, installation, installed-version comparison and application launch passed.

All 6,236 aligned Arabic/Pickthall rows are bundled verbatim. tools/prepare_quran.py verified source equality and corpus IDs. Retrieval uses an immutable trigram index on a separate actor, then detailed matching on bounded candidates. Repeated phrases require context. Selected global passage, backtracking and ambiguity regressions passed.

Muse Spark 1.3 is wired as an opt-in resolver. Strict JSON limits output to retrieved IDs or abstention. Three requests per run, bounded excerpts, cooldown, deduplication, cancellation and stale-result checks limit the integration. No real Spark inference has occurred. Its decision benefit is unproven.

Long ayahs use verbatim, bounded Arabic/Pickthall pages and manual Previous/Next controls. Physical page navigation and readability remain unverified.

Verification: 35 core tests passed after observed failing feature tests; actual worker-queue PCM callback passed; real Swift WebSocket and HTTP clients passed local synthetic-server probes. Optimized global-query probe passed 40 selected queries. Host timings were approximately 27 ms median and 36 ms p95; these are not phone latency.

Receipts remain ignored under build/logs, build/muse-probe, build/spark-probe and build/quran-probe. The Xcode build had no application warnings; its AppIntents extraction warning reflects no AppIntents dependency.

Next: approved provider validation, measurable matcher-only/Spark comparison, selected live passages and long-page check, then scoring evidence and video. Private authorization and observations remain outside public documentation.

## Muse Spark provider validation, October 28

Ran tools/evaluate_spark.py --live through the actual MuseSparkClient against Standard muse-spark-1.3. Three synthetic transcript fixtures were used; no audio was uploaded by this evaluation. All expected decisions were returned.

- Noisy guidance request: local matcher abstained between 1:6 and 37:118; Spark selected 1:6 in 3.283 seconds.
- Shared praise without context: local matcher abstained; Spark also abstained in 0.711 seconds.
- Shared opening without context: local matcher abstained; Spark also abstained in 1.395 seconds. This was an adapter control; app eligibility correctly suppresses Spark for this identical phrase.

This establishes real provider execution and one selected synthetic recovery. It is a three-case diagnostic, not a representative accuracy benchmark or physical lens test. Spark latency supports using it only on uncertain evidence. No application code changed; the installed artifact remains version 0.2.0 Build 21. Live fixture receipts remain ignored under build/spark-evaluation.

Next: wearer tests Build 21 with Muse Spark enabled across selected passages, observes resolver status and lens behavior, then checks long-page navigation. Private spending authorization is recorded separately. Do not request it again within the authorized bounded validation.

## Muse boundary diagnostics, October 28

Version 0.2.0 Build 22 adds separate successful-audio-send, provider-progress and transcript-update counters with event ages. A numeric-only snapshot is written to Library/muse-diagnostics.json in the private app container. It includes no raw transcript, audio or credential. tools/read_muse_diagnostics.py retrieves the snapshot to ignored build/logs.

Two new tests were observed RED with eight assertions failing. All 37 core tests and the actual worker-queue callback subsequently passed. Signed Build 22 succeeded. This is instrumentation, not a claimed fix for a stalled stream. Device installation/verification and wearer reproduction must be checked before drawing conclusions.

An independent synthetic replay exposed a retrieval defect: after long cumulative Al-Fatihah text, recent Al-Ikhlas evidence can be excluded from the candidate set. It does not explain a transcript that stops updating. Track and fix it separately with a regression.

Build 22 signature/profile checks, installation and device version comparison passed. Launch was blocked because the iPhone was locked. Unlock and open Ayah Lens manually for the diagnostic reproduction. No live Muse session was started by the agent.

## Cumulative passage retrieval correction, October 28

Reproduced a source-level defect: the cumulative Al-Fatihah-to-Al-Ikhlas sequence returned no match for all four Al-Ikhlas ayahs. Older text dominated candidate ranking. A globally unique recent complete-word suffix is now checked against the entire reference before approximate retrieval. Shared phrases remain subject to ambiguity/context rules. Published text is unchanged.

Regression was observed failing four assertions, passed after correction, failed all four again with the correction removed, then was restored. The full suite passed 38 tests before final artifact verification. Direct reference matches and Stop now replace the obsolete Spark checking status; this small label correction was reviewed by diff and build.

This source-level reproduction does not establish the exact cause of a particular physical display failure. The corrected artifact still requires the same wearer passage test. No new provider calls or audio uploads were made during this correction.

Final verification: 38 core tests and actual PCM callback passed; optimized global index probe passed 40 queries and shared-opening abstention; local Spark HTTP probe passed. Signed Version 0.2.0 Build 23 built, installed, matched device metadata and launched successfully. The same physical recitation sequence is pending.

## Build 23 physical milestone, October 28

The focused phone-and-lens verse-advancement check passed on Build 23. This establishes the live end-to-end loop for the tested run. It does not establish every ayah was recognized, a representative accuracy rate, word-aligned latency, long-page readability or external-reciter performance. Detailed observations and device receipts remain private under ignored build/logs.

Next work: external-reciter evaluation with permission, long-ayah page navigation, then scoring evidence and the demo video. Do not repeat the resolved stopped-label or basic advancement investigation without a new failure.

## Automatic within-ayah following, October 29

Version 0.3.0 Build 26 replaces manual listening pages with compact portions that follow the supported word position inside the ayah. Same-ayah transcript updates can now move the lens. The live layout has one header, Arabic and the paired Pickthall source span when available, without Next/Previous controls. Manual paging remains separate while stopped.

New actor-isolated follower supports mid-ayah entry, repeats, source-matched late alignment, holding on unrelated/ambiguous evidence and cache-safe passage changes. Arabic slices are bounded to 56 grapheme clusters; English to 100 characters. These are conservative content bounds, not physical pixel-fit proof.

Standard Muse Spark supplies paired exclusive source-word boundaries. Independently validated plans preserve every source word and reject incomplete, reordered, oversized or source-mismatched slices. The app never displays model-authored scripture or translation. Three source-only preparation calls produced cached plans for 2:102 and 73:20 with 20 portions each, and 2:255 with 14 portions. These are model-assisted phrase correspondences, not certified word translation alignment or acoustic timestamps.

For other long ayahs, Arabic follows immediately. With Spark assistance enabled, the app can prepare up to three new verse alignments per run and cache successful plans. The full English remains on the phone if a paired plan is unavailable. No retry loop is added. Late results only update the current session/verse.

Tests: source preservation and Arabic bounds across all 6,236 rows; within-ayah word tracking; same-ayah progression; repeats/unrelated evidence; strict protocol validation; late-plan/current-source checks; every bundled portion. New feature tests were observed RED first. Final suite: 48 passed, zero failures; actual worker-queue PCM callback passed.

The optimized global-lookup/follower-actor probe passed 52 supported automatic transitions, including all 20 parts of both 2:102 and 73:20. It deliberately held the first two shared-opening portions of 2:255 until the passage was identifiable. The first probe incorrectly demanded an early unique ID; corrected that expectation rather than guessing a surah. Actual Swift WebSocket probe passed. Signed Build 26 succeeded, installed and matched device version metadata. Check the following entry for launch outcome. Physical no-clipping/automatic-following validation remains pending.

Private receipts: build/logs/within-ayah-final-tests.log, portion-probe.log, portion-muse-probe.log, within-ayah-final-build.log and build/phrase-alignments/live.log. No new audio recording or personal transcript logging was added.

Build 26 launch was blocked by the locked phone. Signed artifact contents confirm version 0.3.0, build 26 and byte-identical bundled source-boundary plans. Unlock and open Ayah Lens manually for the pending physical test.

## Reading context and nonblocking lens sender, October 29

Current artifact: Version 0.3.0 Build 28. A reading window includes the current plus next source portion when their combined Arabic fits 84 grapheme clusters and English fits 150 characters. This adds upcoming context without moving the recognized position or changing source text. Alignment-plan bounds remain 56/100 per individual portion. The phone now previews the same window and keeps full reference text under Full ayah.

A MainActor newest-frame sender decouples recitation processing from SDK display.send. It permits one in-flight and one latest pending frame, replaces superseded pending frames and invalidates pending work on Stop. Numeric metrics separate queue waiting from SDK completion, retaining completed/requested/superseded counts and peak send duration. SDK completion is not proof of visible pixels.

New context-window tests were observed RED with three assertions; delayed-send/cancellation tests were observed RED with five assertions. All 52 core tests and the actual PCM callback passed after implementation. The integration probe passed 52 supported transitions, with upcoming context in 49 bounded windows and expected shared-opening abstention. Signed Build 28 built, installed and matched device metadata. Launch was blocked by the locked phone.

Physical context fit and relative lens lag remain unverified for Build 28. This removes a confirmed processing/display coupling; it does not establish the cause or size of any perceived physical delay. No paid API calls or audio uploads were performed by this refinement. Private receipts: build/logs/context-sender-final-tests.log, context-window-probe.log, context-sender-final-build.log and lens-lag-investigation.md.

## Build 28 working confirmation, October 29

The wearer confirmed the updated build is working after the context-window/newest-frame changes. Treat Build 28 as the current core-demo candidate. Do not restart broad hardware or recognition testing without a new specific failure. The confirmation is not a controlled latency measurement, a zero-clipping guarantee for every source, or a full-Quran accuracy benchmark. Detailed observations remain private.

Next priority: map current judging criteria to concrete evidence, prepare the demo narrative and capture list, then assemble the video and submission materials. Reuse the current artifact and fix only demonstrated blockers. Public claims must distinguish full reference coverage, selected live checks, actual Voice/Spark roles and unvalidated long-tail performance.

## Submission drafts prepared October 29

Draft 1 is in submission/. It contains the weighted judging evidence map, source claims, exact form answers, capture list, timed script and author review. The timeline is exactly 180 seconds with 247 spoken words and a 35-second continuous proof section. The script generator and submission checker passed.

The four weights came from the participant guide supplied in chat: Impact 30%, Meta tooling 25%, Technical execution 20%, Demo 25%. The public Meta page was checked for deadline/themes/tracks. Current field requirements were checked against the three screenshots supplied October 29. An authenticated guide reread was not completed; the public page and supplied guide remain the sources for requirements. Account-authentication details are not part of this repository.

The repository is public, but main still contains only the initial documentation. A draft implementation review is the next release step; merging remains pending. No final video exists, no form was submitted, and personal opinion ratings remain unselected. Build 28 code and device artifact were unchanged. No model calls were needed for this drafting work.

The next physical dependency is a 35–45-second continuous external-reciter take and a short actual-lens sample. Raw footage belongs under ignored recordings/. Further checks should target the final cut and concrete failures, not restart the broad hardware test cycle.

Draft implementation review created and verified open: https://github.com/khiradlabs/ayah-lens/pull/1, targeting main. It remains a draft and was not merged. Submission draft checks passed after the final save. The form-answer editor open request was queued by the desktop app; direct file links remain available.

## Live participant guide verified October 29

Authenticated access succeeded and the guide was read at https://cerebralvalley.ai/e/meta-ai-developer-hackathon/details. The current rubric matches the drafts: Impact 30%, Use of Meta AI Tooling 25%, Technical Depth and Execution 20%, Demo 25%. The guide confirms a three-minute demo, publicly accessible repository/video, one project submission per team, and November 4 at 9 PM Eastern. In America/Chicago that is November 4 at 8 PM.

Minor changes from the supplied snapshot include 30-minute workshop listings and a $100 Fireworks credit request instead of $25. These do not change the current direct-Meta prototype or submission draft. The guide still prints October 27–November 4 for building; retain the existing organizer/kickoff October 26 clarification and provenance in CONTRIBUTIONS.md. Do not imply that line changed.

Submission source notes and review status were updated from pending to verified. No form fields were entered, no project was submitted, and no app/model code changed. Authentication values were not saved in project files.
