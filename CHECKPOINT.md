# Ayah Lens checkpoint

Updated November 4, 2026, 18:00. Final deliverable: the rendered film v1.2 (`build/video-v1.0/Ayah-Lens-Demo-v1.2.mp4`, 176.7 s): Faraz's on-camera opening with his own voice, title card, lens view, then Callum narration (ElevenLabs via fal) through sections 2 to 7 including the architecture diagram with API references (muse-voice-transcribe-1.0 realtime ASR, muse-spark-1.3 chat completions with strict JSON schema, DAT 1.0.1) and the 2:282 ribbon. Web encode live on release v1.0-hackathon. The live deck (`deck/`) was built and QA'd but not used. See NEXT-TASK.md. The v1.0 renderer (`tools/v1`, `build/video-v1.0`) and the v0.9 cut remain on disk as fallbacks; their MP4s are stale for scene one and must not be submitted.

## Deck state (verified)
- Built to `deck/SPEC.md`; builder's Playwright checks in `deck/CHECK.md`: all keys, all slides at 1920x1080 / 1280x720 / 1000x760, ribbon lit words = lens Arabic at 7 of 7 steps, 35 spec strings exact, no console errors except the optional `toggle.mp4` probe.
- Main session re-ran the deck's self-check in the browser pane over http://localhost:8765: every slide and step, zero issues, minimum font 40 px (ribbon 42). Independent QA subagent report pending at the time of writing.
- Footage: glasses recording of 2026-11-04 (desk, laptop stream, verse 2:282 with seven observed portion steps) and phone takes of Nov 2. The long verse is 2:282, not 73:20. No toggle clip exists; slide 5 is skipped.
- Honesty labels on screen: "What I see through the glasses", "Glasses display recording", "Phone screen recording", "prepared in advance", "Illustration, not in the app", "59 tests passed, Nov 2".

## Earlier state (v0.9 film), kept for reference

## Done and verified

- Review master: build/video-v0.9/Ayah-Lens-Demo-v0.9.mp4. Actual duration 178.633333 seconds, 5,359 frames, 1920×1080 at 30 fps, stereo AAC at 48 kHz. Final SHA256 25559eea06bef702262b8dd1626afce44353ebe798d951470434a9abb2deac5a.
- Original approved v0.5 listener artwork, product illustration, palette and scene order restored. Approved 87-word opening remained exact, including impact and Allah/meaning-lookup lines. B is Cedar delivery, never permission to substitute its audition dialogue.
- Vox-style motion includes population emphasis, narration-cued typography, source-window reveal, verse-reference search, position tracking and a progressive Meta pipeline. Spark assistance/cached pairing remains distinguished from live transcription/tracking.
- Eight full verified Cedar paragraphs: 306 spoken words, 125.4 seconds, native speed. No internal cuts, edge trims or acceleration. Foundation and close dropped repeated brand mentions after pronunciation checks; the verified product paragraph names Ayah Lens. Source recitation/replay remains 8+8 seconds at native speed.
- Three silent labeled spaces: TV 74.166667–92.166667, 18s; long verse 92.166667–103.166667, 11s; English toggle 155.433333–162.433333, 7s. All three decoded PCM peaks were zero. Masjid footage is cancelled.
- Controller ran python3 tools/test_v09_narration.py: 8 tests passed; python3 tools/test_restored_v09.py: 12 tests passed; python3 tools/prepare_v09_narration.py --check passed; python3 tools/render_restored_v09.py --check passed against the final SHA above. Receipt: build/video-v0.9/receipts/controller-final-check.json.
- Final checks covered complete decode, exact audio/frame duration, peak −3.0 dBFS, source-frame comparison, native recitation and all encoded voice waveforms. Four original source hashes remained unchanged. Source-frame RGB similarity minimum 0.974997; source audio correlation exceeded 0.999987; narration correlation exceeded 0.999983.
- Independent Task1 specification/quality reviews passed. Task2 specification and final sampled consecutive-frame motion reviews passed. Motion receipt: build/video-v0.9/receipts/motion-review/review.json. Final Task2 quality review passed. Human listening, pronunciation/emotion and creative acceptance remain unverified.
- Generation ledger includes 37 paid calls and rejected takes. Estimated total USD 0.422952, not an invoice total. Private receipts live under build/video-v0.9/narration/. No credential entered chat, logs or Git.

## Decisions

The latest user explicitly authorized building the rest with B and Vox-style animation while reserving three demo spaces. The accepted-content script has 415 words; the actual production timing cut has 306. Exact approved opening and substantive technical explanation remain. Repeated setup/closing wording was shortened outside the opening. Measured delivery required 18/11/7 spaces and 0.15-second paragraph gaps; this supersedes earlier 20/12/8 planning estimates. Keep longer raw recordings for selection.

No app code, hardware test, new imagery, official Meta website asset, publication, push, merge or submission occurred. QuickTime stayed stopped. Older video masters remain preserved; v0.7/v0.8 are history, not the accepted creative baseline.

## Remaining work

1. Faraz records TV following, 73:20 within-verse changes and actual English off/on. Instructions: submission/DEMO-RECORDING-CHECKLIST-V0.9.md. New files have not been received or inspected.
2. Integrate genuine original recordings into the measured spaces, preserve native timing and complete recitation words, then rerun encoded checks and actual motion/audio review.
3. Faraz reviews the real completed cut. Public links, source/repository release and hackathon submission remain separate release steps.

## Project and evidence limits

- Installed app last recorded as 0.3.0 Build 40; this video version is separate. No fresh install or device probe occurred. Larger-type wearer validation is not implied by video QA.
- The reference contains 114 surahs and 6,236 ayahs. Availability and selected successful tests do not establish universal recognition accuracy. Displayed Arabic/English comes from attributed published text. Spark pairing plans shown are cached; live ASR/tracking remain accurately labeled.
- Fifty-nine core tests refer to the November 2 build/logs/core-tests.log receipt, not new app testing or a user study. Future teaching requires development and extensive testing. Population context uses Pew’s 2020 estimate published in 2025, not adoption or measured comprehension improvement.
- Original native footage is a camera/display composite, not optical through-lens filming. Captions use sentence estimates from actual paragraph durations; they are not claimed word-timed.
- Audio-buffer investigation remains explicitly deferred. Faraz previously confirmed the app stayed open/unlocked; do not ask again or restart that diagnosis.
- Official Meta website asset permission remains pending after Faraz reported sending the exception request. Only existing original illustrations/artwork are used.
- Optional secret-vault backup and unrelated Muse UI-history reads were previously auto-review rejected. Do not retry without new authorization. They do not block current video work.
- Minor future guard: offline narration validation does not compare current planned delivery instructions with saved take instructions. Current artifact is unaffected: reviewer independently confirmed all eight match; generation-cache validation rejects changed instructions. Harden only when needed in a later change.

- Minor future color refinement: generated RGB editorial frames use the default matrix before BT709 tagging. Independent review found a modest red-accent shift and a one-unit paper difference. Original recorded source phases have explicit correct conversion. Current palette/readability passed; use explicit RGB→BT709 conversion on a later export.

## Pointers

- Production narration: submission/DEMO-SCRIPT-V0.9-TIMED.md and build/video-v0.9/spoken-script.txt.
- Accepted-content reference: submission/DEMO-SCRIPT-V0.9.md. It is not the final timing cut.
- Measured edit/captions/slots/receipts: build/video-v0.9/.
- Production manifest: submission/full-video-v0.9.json; restoration source/creative decisions: submission/RESTORATION-V0.9.json.
- Renderer/source tests: tools/render_restored_v09.py, tools/test_restored_v09.py. Voice preparation/tests: tools/prepare_v09_narration.py, tools/test_v09_narration.py.
- Source commits: a2f027e narration, fabf5d4 restored renderer, 7eb6150 original opening handoff. Plan: docs/plans/2026-11-04-restored-vox-v09-plan.md.
- Public repo https://github.com/khiradlabs/ayah-lens; draft PR https://github.com/khiradlabs/ayah-lens/pull/1. Current work is local, not newly published. Recorded deadline November4 at8PM America/Chicago; recheck before submission.
