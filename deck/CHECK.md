# Deck check, 2026-11-04

Built to `deck/SPEC.md`. Tested in Google Chrome (real binary, driven by playwright-core already on this Mac) from `file://`. Safari was not machine-tested.

## Open
- Deck: `open -a "Google Chrome" "file:///Users/farazsyed/data/khirad/apps/ayah-lens/deck/index.html"`
- Notes: press `N` in the deck (opens a popup), or `open -a "Google Chrome" "file:///Users/farazsyed/data/khirad/apps/ayah-lens/deck/notes.html"`
- QA corner readout: add `?debug=1`. Other QA flags: `start=1` (skip the Space gate), `slide=4&step=2` (jump on load), `qa=1` (transitions off), `toggle=off` or `toggle=media/<file>.mp4` (replace the slide 5 clip).
- QA hooks in the console: `__deck.state()`, `__deck.seek(t)` (pause the current clip at t seconds), `__deck.jump(n)`, `__deck.qa()` (layout and media report).

## Keys
Space / Right / PageDown next step. Left / PageUp previous step. Home, End. 1-7 jump to a slide (5 is ignored while the Hifz slide is absent). F fullscreen. M sound on/off. R restart the current clip. N notes window. The first Space, Right or digit also starts the show; the browser will not autoplay sound before a key press, so the deck waits on a "Press Space to start" screen.

## What was verified, and how
1. Keys. Playwright pressed every key on a real page: gate ignores Left and R; Space starts slide 1 with sound playing (muted=false, time advancing); Right x2 reaches step 2, Right moves to slide 2, Left returns to slide 1 at its last step; 4 jumps, R resets the clip to about 0.1 s, M and M again toggle mute, 5 is ignored, End goes to 7.1, Home to 1.0, PageDown/PageUp step, F enters and leaves fullscreen, a digit at the gate starts at that slide, 12 rapid Right and 30 rapid Left end on 7.1 and 1.0.
2. Clips. Slide entry starts the clip, leaving pauses it. Slide 7 clip ended at 4.80 s with ended=true and held its last frame; R restarted it. Slide 2 phone clip starts when it appears (step 2). Phone clips are muted, glasses clips carry sound. Durations: glasses-open 10.0, phone-lookup 19.0, phone-73-20 24.0, glasses-2-282 15.3, glasses-arrival 4.8 s.
3. Ribbon against the lens (slide 4). The clock is `video.currentTime`, read every animation frame and on timeupdate, seeked, seeking, play, ended. I seeked to each of the 7 table times plus 0.12 s and compared the Arabic on the lens with the lit words by eye: all 7 match (10-14, 13-18, 15-22, 19-24, 23-27, 25-30, 28-34). I also seeked 0.07 s either side of each of the 6 step boundaries and read the lens counter burned into the footage: the lens counter and the ribbon step changed together on all 6 (12 of 12 states agree). The lit span crosses line breaks correctly.
4. Arabic. UthmanicHafs, right-to-left, joined letters and marks shaped by the browser; checked in 1:1 screenshot crops (`rcA.png`, `rcB.png`). All 128 words present; the ribbon wraps to 6 lines (y 584 to 1040).
5. Layout and size. `__deck.qa()` walked all 27 slide states (24 without slide 5) at 1920x1080, 1280x720, 1000x760 and 1920x1080 with slide 5 off. It checks every text line box: nothing outside the 1920x1080 stage, no two text blocks overlapping, minimum font 40 px (the Arabic ribbon is 42 px). Result: 0 issues in all four runs.
6. Spec strings. 35 on-screen labels and lines were compared with the spec text after collapsing whitespace: 0 mismatches.
7. Notes window (QA round 2). Keys pressed in the notes window drive the deck: ArrowRight, ArrowLeft, Space, PageUp, PageDown, Home, End and 1-7 are sent over BroadcastChannel, window.postMessage and a localStorage event (deduped by id). Tested: each key moved the deck and the notes window followed; 5 is ignored while Hifz is absent; the Previous and Next buttons send ArrowLeft and ArrowRight; a standalone notes page does not move on its own. M, R, F and N work only in the deck window. The header (slide, title, step, clock, and the line "Keys here drive the deck.") is sticky; "Slide 5 is skipped (no clip)." shows once at the top of the page. If the deck window never had a key press, a Space from the notes window will not start it (browser sound rule) and the deck shows a toast; headless Chrome cannot exercise that guard.
8. Console. With `toggle.mp4` present (tested with a stand-in clip) and with `toggle=off`: no console messages of any type. With `toggle.mp4` absent and the plain URL: exactly one Chrome line, "Failed to load resource ... toggle.mp4 ERR_FILE_NOT_FOUND". That is the existence probe. No JavaScript error.

Screenshots (all in `/private/tmp/claude-501/-Users-farazsyed-data-khirad/c7eaf108-8164-4363-a893-9c5201f123a3/scratchpad/deckqa/final/`): `w1920-s{n}-st{k}.png` and `w1280-s{n}-st{k}.png` for every slide and step (slide 5 shown with `glasses-112.mp4` standing in). Also in `.../deckqa/shots/`: `v-gate.png`, `v-s2-count.png`, `v-s6-count.png` (count-ups mid-way), `rc0-6.png` (lens vs ribbon), `notes-pop.png`.

## Where the deck differs from SPEC.md, and why
- Glasses clips are 814x1080 portrait, phone clips 496x1080. Slides 1, 5, 7 show the clip full height, centred and pillar-boxed on paper, never stretched, instead of edge to edge. Labels and captions sit in the paper side panels so they never cover the lens text.
- Slide 4: the 820 px window shows a 440 px high band of the portrait frame (the lens text), so the ribbon can sit under it. Tune `--crop-top` in `deck.css` (`#s4 .win4 video`) if the band needs to move. The ribbon is the full verse wrapped over 6 lines, because 128 words at 42 px do not fit on one line.
- Slide 3: the five nodes stack top to bottom on the left, not across, because the node text at 40 px or more does not fit in five columns. Phone clip on the right.
- Slide 4 counter reads "Portion 4-5 of 36 on the lens": both numbers of the observed counter state are shown, so QA can match the lens text.
- The phone-lookup clip on slide 2 starts when it appears (step 2), not at slide entry.
- Slide 5 is absent because `media/toggle.mp4` does not exist yet. Numbering stays (6 and 7 keep their numbers). It appears on its own once the file is there, no edit needed.
- `glasses-112.mp4` and `phone-stream-faraz.mp4` are in `media/` but no slide in the spec uses them.
- `verse-2-282.json` and `ribbon-2-282.json` are embedded in `deck.js`, because Chrome cannot `fetch` local JSON from `file://`. If either file changes, regenerate the block between the "EMBEDDED DATA" markers. With `debug=1` over http the page re-reads both files and reports match or DIFFERENT.
- The slide 2 phone clip carries the label "Phone screen recording" like slide 3. Ribbon dim words are ink at 65%.
- Notes wording: slide 7 says the 2:282 verse arrives with Arabic first and translation on the phone (no English claimed). Slide 1 says "laptop" as the spec does (the script draft says television); slide 4 uses 2:282 (draft 5 still says 73:20 there).
