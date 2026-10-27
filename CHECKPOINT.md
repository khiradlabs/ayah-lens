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
