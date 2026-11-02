# Next Ayah Lens task

Version 0.3.0 Build 40 is installed, metadata-verified and launched. The English-meaning switch was wearer-verified in Build 31. Read SPEC.md and the latest CHECKPOINT entry. The runtime key is already in device-only Keychain; no provisioning repeat is needed.

## Current script direction

Faraz named the impact-led proposal Version 1, requested rubric-led Version 2, then requested an attention-grabbing Version 3. All three are preserved in submission/. DEMO-SCRIPT.md and demo-timeline.json contain Version 3. VERSION-3-CONCEPT.md explains the opening meaning reveal, matched scenes and within-passage reveal. The 180-second timeline contains 250 spoken words and a separate 30-second continuous proof section.

Version 3 proposes 94:5 as the short emotional opening. Its published translation was source-checked. Actual device recognition/output for that opening has not been verified. Use the proven passage if needed. An optional prepared-excerpt selection surprise remains conditional on successful physical acquisition checks.

The requested Show English meaning switch is implemented in Build 31. All 55 core tests and the audio-callback probe passed. The wearer confirmed English hides/restores on phone and glasses while Arabic keeps following. Version 3 capture is now the priority.

## QuickTime stopped and native clips under review

Faraz asked to stop QuickTime. Keep it stopped unless he asks to resume it. He later supplied a native glasses recording through Downloads. A private copy and a clean 12.5-second display-composite candidate are saved under recordings/version-3/. Review the remaining native recordings before requesting more filming. The longer continuous within-ayah proof remains outstanding.

Version 3 now introduces Hifz, Quran memorization practice, in the 2:18–2:32 Arabic-only scene. The switch provides a source reference while rehearsing. The engineering segment now mentions Quran teaching as future work requiring further development and extensive testing.

## Current review video

The Version 3 review cut is ready at build/video-review/Ayah-Lens-Version-3-Review.mp4. It is 179.900 seconds at 1920×1080, with stereo audio and a temporary local Daniel guide voice. Picture and audio both span the full duration. The final visual review passed.

One masjid replacement slot is reserved at 1:00–1:30. Its current fill is a labelled placeholder plus 24 seconds of existing phone footage. Replace this block when Faraz supplies the masjid recording. Keep QuickTime stopped. The Hifz choices are explained with a graphic; the old alleged switch clip does not show toggle interaction and must not be used as switch proof.

Reproduce with python3 tools/render_demo_video.py. Source plan: submission/video-edit.json. Guide captions and viewing notes sit beside the MP4. Review artifacts and source media remain ignored by Git.

## Current accuracy investigation

Faraz supplied another recording and reported missed ayahs. Private evidence is in build/accuracy-review/ and recordings/version-3/take-04-receipt.json. A long live hold is confirmed. Exact-text matching and a recorded-audio Muse replay both passed the later references, so the original failure is not yet reproduced. Do not tune thresholds or claim a fix.

A question is pending for the exact red error shown at the end of the clip. The original live Muse partials were not retained. A controlled same-passage comparison with native display recording off/on is the next useful physical check if the error does not localize it. QuickTime stays stopped. Keep the review cut as a draft and the masjid slot reserved.

## Immediate priority: investigate live reliability, then complete the submission

Draft 1 is ready in submission/. Start with FORM-ANSWERS.md, DEMO-SCRIPT.md and CAPTURE-LIST.md. The 180-second timeline contains 250 spoken words. python3 tools/check_submission.py passed timeline, pacing, file-link and 13-field coverage checks.

1. Review the assembled Version 3 cut and adjust pacing/narration as directed. Keep the masjid slot reserved.
2. Replace the 1:00–1:30 block with the selected masjid recording. Recheck source labels, audio, full picture duration and slot boundaries. Do not present the reference fill as finished continuous masjid proof.
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

## Native display capture correction, October 30

Faraz asked to record directly from the glasses with Arabic visible. Verified Meta’s current official Wearables FAQ: Record display supports DAT content. Prefer a ten-second native display-recording check before arranging external optical filming. The button is in glasses settings or the Meta AI action cards below the glasses overview. Actual recording with Ayah Lens live audio remains unverified. QuickTime stays stopped.

## First native clip reviewed, October 31

Downloads/IMG_4525.MP4 is 36.233 seconds, 976×1296, with stereo audio. The clean 17.5–30.0-second interval shows readable Arabic and English across 112:1–4 in a camera-plus-display composite. It does not show 30 seconds or long-ayah tracking. The candidate is native-display-recognition-candidate.mp4. Native capture is now observed in supplied footage; it is not an optical camera-through-lens recording. Audio signal is present and quiet; synchronization and perceptual clarity remain unchecked.

## Immediate physical check, November 2

Build 39 extends only the prototype audio allowance and adds its phone countdown. Run Start Muse live Quran for at least three minutes with the phone unlocked and glasses worn. Confirm Audio time remaining appears near the build label and verses continue beyond the old two-minute boundary. Use native Display Recording off for this first comparison. Report any stall separately with the exact phone status/error. Do not claim the previous hold is fixed from a successful cap check alone. The masjid slot stays reserved.

## Immediate readability check, November 2

Build 40 uses larger heading-style Arabic and English in the live lens, with denser windows kept to one source portion. Wear glasses and tap Start Muse live Quran with English on. Confirm both languages are readable and fully visible during a short passage and 73:20. The ten-minute cap from Build 39 remains; combine this with the pending three-minute test if convenient. Actual font readability and the original missed-ayah stall are not established by automated checks.

## Deferred error investigation

The latest screenshot shows the local audio-buffer overflow guard, not the session allowance. Use the private Build 40 investigation under build/accuracy-review/build40-backpressure/. Faraz deferred this investigation on November 2. Do not request the foreground/unlocked observation or further reproduction unless this issue is resumed. Preserve the bounded audio queue until evidence justifies a specific change. Build 40 remains installed; no speculative fix has been made.

## Active priority after deferral

Return to Version 3 demo-video review and finalization. Keep the single 1:00–1:30 masjid slot reserved. The audio-buffer issue remains unresolved and does not block editing. Do not describe the full failed take as reliable following.
