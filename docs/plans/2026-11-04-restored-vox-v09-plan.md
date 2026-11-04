# Restored Ayah Lens v0.9 — Implementation Plan

**Goal:** Build the complete non-demo video with selected B Cedar voice, Vox-style explanatory motion, original approved visual sequence and three clearly labeled silent demo spaces, under 180 seconds.
**Architecture:** Preserve original artwork/layouts and opening sequence from v0.5, extending its narration exactly as approved in the current script. Generate bounded verified Cedar paragraphs and time all editorial motion from actual performance; compose three silent inserts independently of narration. Keep old masters/source clips unchanged. No publishing or app changes.
**Tech stack:** Existing Python/FFmpeg/Pillow/Remotion tools and existing bounded OpenAI Realtime Cedar helper.
**Execution:** use the execute-plan skill to implement this task-by-task. User authorized the production in this turn. Tasks may scaffold concurrently only within disjoint ownership; final assembly depends on verified speech manifest. Controller integrates and runs fresh acceptance checks.

## Nonnegotiable acceptance

- Exact 87-word approved opening from submission/RESTORATION-V0.9.json. B is delivery, never audition dialogue.
- Original v0.5 approved artwork, glasses illustration and slide order; Vox-style typography, data animation and progressive technical explanation. No v0.7/v0.8 visual redesign, new images or Meta website assets.
- Explicit impact at start and close, Meta Voice/Spark roles, over-6,000-verse retrieval challenge and within-verse tracking; published sources and cached-plan scope retained.
- Content timing edit may remove repeated setup outside opening. Aim about 330 words, with about 20/12/8 seconds of silent placeholders for TV following, 73:20 tracking, and English off/on. Actual duration controls final layout. Preserve original opening recitation/replay at native speed where source phrase tails are complete. Never speed up genuine recitation or stretch narration to force fit.
- Cold-viewer script/storyboard review before paid generation. Existing user-approved provider and private credential path, no reapproval needed. Bounded API calls, no secret output, generation receipts and --note costs. Keep synth-English transfers limited to narration verification.
- Output: build/video-v0.9/Ayah-Lens-Demo-v0.9.mp4 plus captions, spoken text, measured edit/slot manifest and verification receipts. Demo spaces visibly say awaiting recording, are silent, and cannot be mistaken for working proof.
- Complete decode, voice completeness, original inputs unchanged, legible source labels/disclosures, no clipping, readable animation, <180 seconds. Human emotional/creative approval remains for actual finished cut.

### Task 1 — Timing edit and B narration
**Goal:** Produce verified B narration and measured manifest, preserving the approved opening and rubric details.
**Files:** Create submission/narration-v0.9.json; submission/DEMO-SCRIPT-V0.9-TIMED.md; tools/prepare_v09_narration.py if needed; tools/test_v09_narration.py; build/video-v0.9/narration/ and build/video-v0.9/narration-manifest.json.
**Depends on:** none.
**Touches:** Only the files listed above. Do not edit renderer, shared checkpoints or accepted-content script.
**Steps:**
1. Read current script, selected B receipt and helper; create timing cut and contract with scene IDs opening, product, use_cases, meta_challenge, meta_pipeline, hifz, foundation, close. Opening text is exact. No narrated demo setup repeats necessary; placeholder title can supply the cue.
2. Define tests for exact opening, Cedar selection, all rubric/scoping lines, duration planning and duplicate-charge safeguards. Run them failing before implementing helper behavior.
3. Before spend, send draft script and storyboard intent to controller for cold-viewer review; wait for that review verdict, not extra user permission.
4. Reuse verified matching cached full paragraphs where exact text matches. Generate only bounded changed paragraphs with selected B delivery, existing realtime_narration.cjs and --note. Never expose key. Keep natural speed1, no word/phrase slicing. Pricing estimate is not actual invoice.
5. Verify actual audio independently with speech recognition via existing tools; fix missing words using a complete paragraph take. Decode all WAVs, record hash, duration, text, provider and verification. Manifest contract: top-level clips list, each item id,text,path,duration_seconds,sha256,verified; plus spoken_word_count, speech_duration_seconds, costs_estimate_usd. Paths relative to project.
6. Run python3 tools/test_v09_narration.py and a read-only manifest check, then commit owned source files only.
**Done when:** all speech clips verified against actual waveform and manifested; tests pass; speech and fixed quiet allowances permit <180s without speedup. Report evidence and exact commit.

### Task 2 — Restored Vox renderer and export
**Goal:** Render original creative direction with explanatory motion, verified B narration and three silent insert spaces.
**Files:** Create tools/render_restored_v09.py; tools/test_restored_v09.py; submission/full-video-v0.9.json; build/video-v0.9/visuals/; build/video-v0.9/receipts/; final video/captions/measured timeline beneath build/video-v0.9/.
**Depends on:** Task1 manifest for final render; asset inspection and renderer scaffolding independent.
**Touches:** Only files listed above. Do not edit Task1 files or checkpoints.
**Steps:**
1. Inspect original v0.5 opening/full master, original render sources and artwork. Report text findings and input hashes; no images in main thread. Preserve approved pictures/order, not the later redesign. Read EDIT-HANDOFF-V0.9.md.
2. Write meaningful failing tests for exact opening preservation, source-frame offset rounding, correctly ordered separated silent demo slots, cache/live labels and <180s measured layout. Implement minimal reusable renderer; run tests green.
3. Build revised opening from original layers/assets, adding approved narration-timed impact text. Use four-part population proportion and sourced count, original listener/glasses artwork, original benefits, original product illustration. New words cannot be implied to match old guide timing.
4. Animate technical search/word-position explanation, actual-source preservation, and correct Spark assistance path. Motion must explain each spoken point, with readable holds. Preserve original palette/layout while making bold type/evidence highlights/connected transitions. No simulation passed off as actual footage.
5. Use silent 20s TV placeholder after use cases, silent12s same-verse placeholder before mechanism, silent8s English-toggle placeholder after hifz. Frames clearly label awaiting recording. Cue descriptions are editorial, not fake app output. Integrate these spaces into measured manifest with starts/ends/filenames.
6. Assemble verified Task1 narration at native speed, preserve genuine opening recitation/replay, smooth picture and audio handoffs, proper disclosure in bounded header. Generate complete captions and text from measured edit.
7. Render full cut. Run python3 tools/test_restored_v09.py and python3 tools/render_restored_v09.py --check. Inspect source continuity, timed diagram/benefits, transitions and silence; save contact sheets for reviewers only.
8. Commit owned source files only; report path, duration/frames, measured slots, costs/source limits, checks and commit.
**Done when:** actual encoded 1080p30 master exists, <180s, all speech complete, three slots silent/labeled, acceptance checks pass and original master/source hashes unchanged.

### Task 3 — Independent review and closeout
**Goal:** Verify specification, quality and encoded motion, fix concrete defects, save resumable state.
**Files:** Review only initially; controller owns CHECKPOINT.md and NEXT-TASK.md; private review receipts under build/video-v0.9/receipts/.
**Depends on:** Tasks1–2.
**Touches:** Review receipts and controller checkpoint only; fixes dispatched to responsible worker.
**Steps:** Conduct spec review before quality review, max2 repair loops. Run independent fresh checks against final encoded hash. Then review representative transitions and dense diagram sequence in consecutive frames. Controller reruns tests/check, commits checkpoints and updates the recording gate only if slot handoff changes.
**Done when:** reviewers report pass or concrete unresolved limits, controller fresh checks pass, final review cut and slot handoff are presented to Faraz, with final demo footage explicitly outstanding. No publication or submission.

## Measured production revision, November 4

Final verified B performances total 125.4 seconds across eight complete paragraphs and 306 spoken words. Exact approved 87-word opening and substantive technical pipeline remain unchanged. Repeated brand mentions were removed from foundation/close after pronunciation checks; product narration retains the verified brand. No further voice generation is required. To preserve every speech/source word at native speed under 180 seconds, current requirements supersede the planned 20/12/8 inserts: TV18s, long-verse11s, English-toggle7s, total36s. Original listening/replay remain8+8s. Paragraph padding is0.15s each, total1.2s before per-scene frame rounding. Estimated encoded duration is178.6–178.9seconds; actual encoded duration must be verified. No PCM silence trimming or speed fitting was used.
