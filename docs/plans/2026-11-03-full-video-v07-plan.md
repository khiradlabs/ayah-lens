# Complete Ayah Lens v0.7 — Implementation Plan

**Goal:** Rewrite and render the complete hackathon demo with selected B narration and smooth picture/audio transitions under three minutes.
**Architecture:** A new standalone script and shot manifest drive continuous Realtime Cedar paragraph performances. Measured narration determines the edit; genuine device recordings retain source timing, wording and synchronized audio. One global visual language and motivated scene handoffs replace the disjointed earlier cut.
**Tech stack:** Python/Pillow, FFmpeg, existing local Node ws dependency, OpenAI Realtime2.1 Cedar.
**Execution:** use the execute-plan skill to implement this task-by-task. Current build authorization includes this complete revision; do not stop for another script approval.

Base: b0ba8cd. Tree was clean after saving selected-voice work. Preserve all earlier masters. Internal planning limits: two implementation tasks, review after each, target45minutes, at mostUSD1 in new speech/transcription estimates. No external message, publication, new camera recording or Meta website asset use.

### Task1 — Rewrite the whole narrative and storyboard
**Goal:** Create a connected, conversational script and concrete shot plan covering all four rubric criteria.
**Files:** Create submission/DEMO-SCRIPT-V0.7.md and submission/full-video-v0.7.json.
**Depends on:** none.
**Touches:** only those two files.
**Steps:**
1. Read selected B settings, judging and claims files plus current media inventory.
2. Write a complete270–330-word target script, preserving the personal Quran translator idea. Use fewer connected paragraphs, not chopped slogans. Explain the problem for a non-Muslim judge. About2billion/quarter is dated Pew2020 context, not a market-size claim. No unsupported comprehension percentage or personal biography.
3. Pair each paragraph with a specific visual transformation and sound handoff. Genuine proof precedes technical explanation. Include Meta glasses, Muse Voice, Spark source-span pairing and ambiguity assistance, local validation, within-ayah following, published source words, English toggle, Salat possibility, television listening, Hifz practice, full reference114/6236 and59-test recorded receipt. Teaching is future, requires testing. Keep cached demo phrase plans honest.
4. Keep60–90seconds reserved for masjid replacement:6seconds clearly labelled reservation followed by24seconds explicitly labelled phone reference. Never present it as completed masjid footage.
5. Design original coherent neutral editorial visuals; remove rigid generated-man hold and abrupt fake-product turntable detour. Use actual native display crop208,832,576,144 and phone crop48,1232,984,1116. No fake Quran/lens output. Show source labels and identify earlier prototype. Avoid excessive boilerplate; required prayer disclaimer and synthetic-English disclosure remain legible.
6. Save JSON with named paragraphs, nominal story order and meaningful transitions. Timing outside the reserved slot remains provisional until voice measured. Ensure pre-slot narration plausibly fits60seconds with6-second opening recitation and12.5-second native proof.
7. Verify syntax and word count with python3; run git diff --check. Commit only the two owned files.
**Done when:** python3 -m json.tool submission/full-video-v0.7.json >/dev/null succeeds; all named script paragraphs and transition cues are present; controller and independent spec then cold-viewer editorial review pass before generation spend.

### Task2 — Produce B narration and the complete revised cut
**Goal:** Render a complete reviewable video from the rewritten script with motivated visual transitions and smooth sound handoffs.
**Files:** Create tools/render_full_v07.py, tools/test_full_v07.py; modify submission/full-video-v0.7.json only for measured timing/source receipts; outputs under build/video-v0.7/.
**Depends on:** task1 and its reviews.
**Touches:** those three tracked files and private build/video-v0.7/ only. Existing tools/realtime_narration.cjs and tools/openai_narration.py may be imported/called read-only.
**Steps:**
1. Write meaningful failing checks for timing under180seconds, reserved60–90slot, source-word-preserving crop coordinates, narration/recitation separation and continuous source playback without speed changes. Do not test cosmetic constants or mirror drawing code.
2. Observe failures before implementation.
3. Generate continuous English paragraphs using exact B model/voice/delivery direction from submission/narration-v0.7.json. Remove only sample-specific last-phrase pacing instructions when necessary. Use existing runner, --note and private key file; never print a key or send raw recitation. Reuse the accepted B hook audio if its words occur unchanged. No tempo fitting or fragmented-word splices. Every new call has a receipt and cost. If a take omits words, retry the whole paragraph at most once within the planning cap.
4. Independently transcribe generated English waveform with maintained helper. Normalize only documented spelling/number aliases. Reject missing clauses; do not patch artificial closing snippets. Keep the performance flow intact.
5. Build measured edit around the audio. If it does not fit, shorten copy and regenerate the affected paragraph, never accelerate source recitation or force voice into old grid times. Retain60–90reserved slot. Export ends naturally at or before179.9seconds.
6. Render1920x1080/30fps with synchronized48kHz stereo. Use coherent typography/palette and motivated transformations;0.3–0.6s visual handoffs where appropriate. Maintain readable real output. Avoid slides popping to unrelated layouts. Technical evidence travels through a visibly connected animated diagram, accurately identifying live versus cached work. Labels cannot cover source words.
7. Mix continuous paragraphs with small natural gaps and gentle sound handoffs. No overlapping independent recitations, no narration over audible scripture, no new music requirement, no word clipping. Apply small sample-edge fades/level matching, not per-clause voice cutting. Preserve genuine recitation words/timing/speed. Synthetic-English disclosure applies only to English narration.
8. Render captions and plain script. Verify all words, picture/audio durations, complete decode, source/crop identity at sampled times, labels, frame continuity and audio peaks. Verify three full-master boundaries with consecutive frames and audio windows, not only distant stills. Read-only --check must avoid credentials and paid calls. Preserve old export hashes.
9. Run python3 tools/test_full_v07.py and python3 tools/render_full_v07.py --check. Commit owned tracked files. Controller independently reruns checks, then spec review, code-quality review and private motion review. Fix concrete issues with at most2loops per stage.
**Done when:** tests pass; --check passes; complete build/video-v0.7/Ayah-Lens-Demo-v0.7.mp4 decodes under180seconds with the full new B script, no missing words, correct source labels, accurately reserved masjid slot and reviewed picture/audio transitions. Human creative approval is explicitly not inferred from technical checks.

After task2, independent final phase review covers base through task commits. Update checkpoint/NEXT and return the complete cut and rewritten script. No publishing or app change.
