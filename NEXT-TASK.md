# Next Ayah Lens task

Version 0.3.0 Build 28 is the automatic within-ayah artifact. Read SPEC.md and the latest CHECKPOINT entry. The runtime key is already in device-only Keychain; no provisioning repeat is needed.

## Immediate priority: capture and complete the submission

Draft 1 is ready in submission/. Start with FORM-ANSWERS.md, DEMO-SCRIPT.md and CAPTURE-LIST.md. The 180-second timeline contains 247 spoken words. python3 tools/check_submission.py passed timeline, pacing, file-link and 13-field coverage checks.

1. Obtain a 35–45-second continuous external-reciter proof take and a 5–10-second actual-lens sample. Use the same working passage and permitted audio. Store raw footage only under ignored recordings/.
2. Assemble the three-minute cut, preserving at least 25 seconds of continuous genuine proof. Distinguish actual lens footage, phone preview and overlays. Label cached Spark source plans accurately.
3. Review the draft at https://github.com/khiradlabs/ayah-lens/pull/1 and merge only after authorization, before submitting the root public repository URL. The default branch currently has initial docs only.
4. Have Faraz select his own two Meta API opinion ratings. Finish the accessible video URL and accepted contributor details. Do not submit the form or publish social posts without explicit authorization.

The authenticated participant guide was verified October 29. Weights remain Impact 30%, Meta tooling 25%, Technical execution 20%, Demo 25%. Current form fields are from October 29 screenshots. The deadline remains November 4, 9 PM Eastern, or 8 PM America/Chicago. No authentication details belong in project files.

The core demo candidate remains version 0.3.0 Build 28, confirmed working. Keep its feature scope frozen while producing the video.

## Current implementation

Full reference: 114 surahs, 6,236 aligned rows. Muse Voice supplies realtime transcripts. Global retrieval identifies the passage; the actor-isolated follower locates source-word position and changes compact portions within it. Spark supplies bounded candidate decisions and validated Arabic/Pickthall boundary plans. Automatic Arabic works across the full corpus. Accepted paired plans are cached; uncached alignment is bounded to three new verses per run. Full translation stays on the phone until a valid paired plan is available.

Fifty-two core tests, actual callback probe, 52 supported portion transitions through global lookup/actor and the Swift WebSocket probe passed. The bundled 2:102 and 73:20 plans have 20 paired portions each; 2:255 has 14, with its shared opening left unresolved until distinguishing evidence. Preserve canonical text, no invented translation or acoustic timing claims.

## Verification baseline

Current artifact: version 0.3.0 Build 28. Fifty-two tests, callback probe and selected global/follower integration transitions passed. Wearer confirmation closes the immediate core-loop check. Private receipts and observations remain under ignored build/logs and private action gates.
