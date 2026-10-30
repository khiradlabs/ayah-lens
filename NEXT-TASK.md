# Next Ayah Lens task

Version 0.3.0 Build 31 is installed and wearer-verified for the English-meaning switch. Read SPEC.md and the latest CHECKPOINT entry. The runtime key is already in device-only Keychain; no provisioning repeat is needed.

## Current script direction

Faraz named the impact-led proposal Version 1, requested rubric-led Version 2, then requested an attention-grabbing Version 3. All three are preserved in submission/. DEMO-SCRIPT.md and demo-timeline.json contain Version 3. VERSION-3-CONCEPT.md explains the opening meaning reveal, matched scenes and within-passage reveal. The 180-second timeline contains 250 spoken words and a separate 30-second continuous proof section.

Version 3 proposes 94:5 as the short emotional opening. Its published translation was source-checked. Actual device recognition/output for that opening has not been verified. Use the proven passage if needed. An optional prepared-excerpt selection surprise remains conditional on successful physical acquisition checks.

The requested Show English meaning switch is implemented in Build 31. All 55 core tests and the audio-callback probe passed. The wearer confirmed English hides/restores on phone and glasses while Arabic keeps following. Version 3 capture is now the priority.

## Capture paused

Faraz asked to stop QuickTime. The app was terminated and both saved originals were verified present. Keep capture paused until Faraz asks to resume. The settled third take remains outstanding.

Version 3 now introduces Hifz, Quran memorization practice, in the 2:18–2:32 Arabic-only scene. The switch provides a source reference while rehearsing. The engineering segment now mentions Quran teaching as future work requiring further development and extensive testing.

## Immediate priority: capture and complete the submission

Draft 1 is ready in submission/. Start with FORM-ANSWERS.md, DEMO-SCRIPT.md and CAPTURE-LIST.md. The 180-second timeline contains 250 spoken words. python3 tools/check_submission.py passed timeline, pacing, file-link and 13-field coverage checks.

1. Finish and save the first QuickTime phone-screen recording under recordings/version-3/. Then obtain a 35–45-second continuous external-reciter proof take and a 5–10-second actual-lens sample. Use the same working passage and permitted audio. Store raw footage only under ignored recordings/.
2. Assemble the three-minute cut, preserving at least 25 seconds of continuous genuine proof. Distinguish actual lens footage, phone preview and overlays. Label cached Spark source plans accurately.
3. Review the draft at https://github.com/khiradlabs/ayah-lens/pull/1 and merge only after authorization, before submitting the root public repository URL. The default branch currently has initial docs only.
4. Have Faraz select his own two Meta API opinion ratings. Finish the accessible video URL and accepted contributor details. Do not submit the form or publish social posts without explicit authorization.

The authenticated participant guide was verified October 29. Weights remain Impact 30%, Meta tooling 25%, Technical execution 20%, Demo 25%. Current form fields are from October 29 screenshots. The deadline remains November 4, 9 PM Eastern, or 8 PM America/Chicago. No authentication details belong in project files.

The core demo candidate is version 0.3.0 Build 31, wearer-verified. Keep its feature scope frozen while capturing Version 3.

## Current implementation

Full reference: 114 surahs, 6,236 aligned rows. Muse Voice supplies realtime transcripts. Global retrieval identifies the passage; the actor-isolated follower locates source-word position and changes compact portions within it. Spark supplies bounded candidate decisions and validated Arabic/Pickthall boundary plans. Automatic Arabic works across the full corpus. Accepted paired plans are cached; uncached alignment is bounded to three new verses per run. Full translation stays on the phone until a valid paired plan is available.

Fifty-two core tests, actual callback probe, 52 supported portion transitions through global lookup/actor and the Swift WebSocket probe passed. The bundled 2:102 and 73:20 plans have 20 paired portions each; 2:255 has 14, with its shared opening left unresolved until distinguishing evidence. Preserve canonical text, no invented translation or acoustic timing claims.

## Verification baseline

Current artifact: version 0.3.0 Build 31. Fifty-five tests, callback probe and selected global/follower integration transitions passed. Wearer confirmation closes the immediate core-loop check. Private receipts and observations remain under ignored build/logs and private action gates.

## Focused later regression

Source-only preflight: 94:5 identifies correctly, but a subsequent exact 94:6 query retained 94:5. Do not present that transition as verified. Keep the current capture on the proven long passage; investigate the near-identical pair after capture without broad feature changes.
