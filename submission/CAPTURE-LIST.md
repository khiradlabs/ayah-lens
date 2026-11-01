# Ayah Lens demo footage capture list

Capture Build 31 working with a permitted recitation source. Use the same setup and passage that already worked. The main take should prove automatic following inside one long ayah.

Save raw footage under the ignored recordings folder in the Ayah Lens repository. Raw footage stays out of public Git.

## Version 3 scenes

Version 3 opens with eight seconds of recitation and an eight-second meaning reveal. The population/listening narration follows. The proposed 94:5 opener requires an actual-device check; use a proven passage if needed. The opening is edited, while the later 30-second proof remains continuous. The prayer scene presents a possible use and carries this readable caption: Technology demonstration only. This does not establish religious permissibility for use during prayer. Repeat it in the final video description.

Build 31 contains the Show English meaning switch. The wearer confirmed it hides and restores English on phone and glasses while Arabic keeps following. Capture the on/off/on behavior separately from the continuous proof take.

The final Version 3 timeline keeps 30 seconds of continuous proof. Capture the full 35–45-second take for editing margin.

## Native display recording

Meta’s current Wearables FAQ confirms native recording of Device Access Toolkit content. On the glasses, use the Record display button in settings. In Meta AI, find Record display in the action cards below the glasses overview. Source: https://developers.meta.com/wearables/faq/

Try a ten-second recording with Ayah Lens active and Arabic visible. Check the saved clip for the actual displayed text, usable audio and continuing recognition. A supplied native recording now shows Ayah Lens with bilingual verse updates. Verify each new take rather than assuming the whole source is usable. Keep Ayah Lens foregrounded; using the glasses settings avoids switching the phone app. Once verified, native display recording is the preferred way to obtain the displayed-Arabic shot. External optical filming remains a fallback.

The native display recording and ordinary outward-camera video are different capture modes. Label the saved native output accurately, including any device-generated composite view.

## Minimum footage

| Take | What to capture | Length | Save as |
|---|---|---:|---|
| Actual lens sample | A legible view of text emitted by the glasses display, filmed through the lens if feasible. | 5–10 seconds | recordings/lens-sample.mov |
| Continuous listening proof | External source audible, phone Lens preview following, hands away after Start. Show at least three window changes within 73:20 or 2:102. | 35–45 seconds | recordings/hero-phone.mov |
| Device context | Faraz wearing the actual glasses while the external source plays. Keep hands visible and avoid touching page controls. | 10–15 seconds | recordings/wearer.mov |
| Founder narration | Read the narration from DEMO-SCRIPT.md in a quiet room, with a short pause between sections. | About 2 minutes | recordings/narration.mov or .wav |

Start with a five-second lens sample before spending time on a full optical recording. Getting a readable display image can require a second camera and careful alignment. The eyewear's outward camera should not be assumed to capture its own lens display.

If optical text cannot be captured legibly, use the phone preview labelled Live phone preview and retain genuine device-context footage. Explain that it mirrors the selected display window. Never label the preview or a recreated overlay as actual lens footage.

## Main take

1. Open Ayah Lens and show version 0.3.0 Build 31 briefly.
2. Use your own recorded recitation, or another source cleared for inclusion in the public video. Play it from a second device.
3. Enable Muse Spark assistance and tap Start Muse live Quran once.
4. Play 73:20 from its start, or reuse the proven 2:102 passage. Keep the source volume and device position consistent with the working test.
5. Record 35–45 seconds continuously. Keep the verse ID and Arabic/English window legible. Keep at least 25 seconds uncut in the final video.
6. Stop and save the raw take. A failed take can be recorded again; do not edit a missed transition into apparent success.

The bundled phrase plans for these passages are cached. A new alignment call is unnecessary for the take. Voice transcription is live. Leave the phone foregrounded, as required by the current prototype.

## Framing and sound

Prefer landscape footage for the main demonstration. Use the best readable resolution available, with 1080p at 30 frames per second as a useful target. Keep the verse text large enough to read in the final landscape frame.

Retain actual recitation in the proof section. Do not put voiceover or music over it. Voiceover can resume when the technical explanation begins. Music is optional; do not rely on it for impact.

Keep the scene focused on the demonstration and remove unrelated notifications from the recording. For the founder shot, use a stable camera and soft light facing the speaker.

## Labels in the edit

Use Actual glasses display only for an optical or verified device-display capture. Use Live phone preview for the app's selected window. Use Explanatory overlay for a reconstructed diagram. Keep each label attached to its own view.

Label Spark phrase plans Cached when explaining the filmed precomputed plans. Show real code or a saved source-boundary example for the model explanation. An API key or private provider response is unnecessary.

## Additional proof already available

The editor can show event-dated Git commits, the source modules, corpus coverage and the existing 55-test result. Use public technical files or fresh offline checks. Keep private receipts, consent notes, credentials and personal diagnostics out of the footage.

## Capture acceptance

The hero take has audible external recitation and at least three automatic window changes. Arabic and English remain legible. No Next control is used. The same ayah stays identified during the within-ayah sequence. Actual lens and preview labels are truthful.

The final cut targets 180 seconds. Preserve a continuous proof interval before trimming decorative shots. Use the final media checker described in REVIEW.md after assembling the video.

## Capture session progress

Build 31 passed the wearer’s English-switch check. Two private phone-screen originals have been saved. A 12-second switch candidate and a 24-second within-73:20 candidate are available under recordings/version-3/. The latter shows six automatic window changes and no observed phone-card clipping, but does not meet the planned 30-second continuous proof interval. A settled retake is next. These are phone-preview captures; actual optical and wearer shots remain pending.

Run bash tools/inspect_capture.sh /absolute/path/to/take.mov for read-only duration, stream and audio-level checks. Use bash tools/extract_capture.sh INPUT START_SECONDS DURATION_SECONDS OUTPUT.mp4 to export a continuous phone-preview interval without replacing the original. Save private per-take reviews and source intervals in the ignored capture manifest.

## Native clip available

The first supplied native glasses recording contains a clean 12.5-second camera-plus-display excerpt with Arabic and English across 112:1–4. Use the label Native glasses display recording. It can support the reveal or short device demonstration. It is not long-ayah following or a 30-second proof. Originals and private per-take reviews remain under recordings/version-3/. Review remaining supplied clips before requesting another shoot.
