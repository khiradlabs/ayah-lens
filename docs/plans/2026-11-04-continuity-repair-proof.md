# Ayah Lens continuity repair: proof before full rebuild

## Failure demonstrated

Faraz rejected the v0.9 presentation as disconnected, abrupt and missing a clear text/meaning sequence. Its isolated-slide renderer erases each visual thought to paper and concatenates finished scenes. The technical overlay also hides the published English source example. Narration captions are an external sidecar, not visible in the exported video. The requested three recording spaces are not the explanation for these non-demo defects.

Read-only investigation: code at render_restored_v09.py71–73,180–183,187–188,223,330–337; original source excerpt at editorial_motion.py232–239. Actual encoded blank resets at13.000,16.660,53.000s; nearblank at63.967,114.467,146.167. Exact English appears mainly45–53s and150–155s, not during the spoken meaning promise. Chapter/progress resets are a separate concrete consequence of passing scene index0 for every source layout.

## Corrective proof scope

Produce only a roughly33-second continuity proof first. Preserve all old masters and approved B recordings. Use the sentence-complete B excerpt beginning What if your glasses... at about22.8s within opening.wav, through36.85s; original8second recitation/replay; complete10.8second product paragraph. A small safe leading/tail allowance is allowed to preserve complete words. Do not change approved words, voice, speed, native recitation or generate new narration/images.

The proof is a middle-of-opening transition sample, not a replacement opening or newly shortened approved script. It must not be mistaken for the full video.

## Visual design contract

- Use one continuous visual stage and one persistent reading window. Preserve approved paper/ink/mutedblue/red and original glasses illustration/listener art where helpful. No whole-frame blank-paper wipes between ideas.
- Start with the complete translator question. Let that question develop into the same reading window rather than disappear into an unrelated title card.
- Use actual matching112:1 published text, not an unrelated verse: Arabic contiguous excerpt قُلْ هُوَ ٱللَّهُ أَحَدٌ; English exactly Say: He is Allah, the One! Confirm against corpus. Reference labels remain clear. Re-typeset text must be labeled Published source excerpt / not recorded lens pixels.
- When B says The meaning, right in front of your eyes, the actual English meaning must be visible and readable alongside Arabic. It must remain through the automatic-following/hands-free explanation. Abstract bars or the word Meaning are insufficient.
- Let the same window expand/reposition into the actual recorded replay. Original source/native footage stays distinct and correctly labeled. First8s of its existing replay advances112:1→112:2→112:3 with matching English. Never replace source pixels with an invented live UI.
- Carry the last same reading window into the product/glasses reveal, maintaining an anchor while original3D illustration and product labels enter. Narration/audio changes at natural phrase boundaries; no narration over Quran audio. Complete the reading/narration before removing a text element.
- Include readable burned-in English narration captions in a stable safe lower band, timed to the actual B phrase words. They must not cover the Quran English meaning or source words. No caption during recitation unless it is actual published meaning from the source.
- Source card/quote and narration captions have different visual roles. Real translated meaning must not be replaced by narration subtitles.

## Execution

Task1 implementer owns tools/render_continuity_proof.py, tools/test_continuity_proof.py and build/continuity-proof/ only. No v0.9 source edits or full video rebuild. Read eng-rules and systematic-debugging. Tests should reproduce absence of blank resets/translation visibility/continuous window geometry and complete audio/sample timing, not just duration checks. Verify actual encoded proof with chronological motion inspection. Script uses existing data only and is maintained/re-runnable. Commit owned source only.

Controller owns this plan, failure diagnosis, CLAUDE gotcha and project state. Independent critic reviews the actual proof chronologically, not isolated preselected boundary snapshots. Report precise successes and failures. Human visual feedback on this focused sample precedes another full-cut attempt per the project’s existing short-proof guidance. Do not ask Faraz to reapprove the script or pick another voice.

## Evidence-led proof refinements

Actual first proof exposed text reflow when a font resized across wrap thresholds, a growing reading window occluding benefit labels, and a missing checkbox glyph. Fix with fixed-line layer transforms, group fade before overlap and drawn vector ticks. These are specific corrections within the same continuity design, not another visual direction.

Audio investigation found that the inherited 8-second replay ends during active audio. The original raw native clip reaches sustained low-level tail fromabout9.967seconds, verified with a threshold appropriate to the quiet original recording. The corrective sample may therefore use0–10.2seconds of that same native clip, at1x and actual crop208:832:576:144, to preserve the full recitation and a natural quiet tail before product narration. This increases the proof to about35.7seconds. Hold the actual final source state after this longer passage; do not force it back to112:3 or112:1. The full approved script and B recordings remain unchanged.
