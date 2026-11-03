# Ayah Lens video v0.2 editorial motion

This is the private v0.2 review design. The installed app and v0.1 footage remain separate artifacts.

## Design

Warm paper `#F3EFE5`, near-black `#1A1A18`, red `#D34B38`, muted blue `#53749B`, and yellow `#EDC84B`. Arial provides large, direct editorial headings; Times italic introduces a quieter listening/source voice. Flat rules and source marks replace dashboard cards. Type enters through a clipped vertical reveal. Lines trace causal relationships. Diagrams transform information while source footage plays unchanged.

No new recording, generated image, paid service, cloud narration, or publishing is part of this renderer. Waveforms and content bars are explicitly explanatory graphics. They do not represent measured acoustic word timing or fabricated device output.

## Renderer contract

`tools/editorial_motion.py` exposes:

- `keyframe(index, t, plan=None, product_frame=None)`: a full-HD RGB Pillow image at scene-local seconds.
- `preview_keyframes(plan=None)`: writes all-scene storyboard and population/technical semantic stage sheets. Returns the storyboard path.
- `render_scene(index, destination, plan=None, *, start=0, duration=None, fps=30)`: renders a silent motion base. Returns the output path.
- `check(plan=None)`: validates the timeline, population progression, causal stages, source example and semantic frame differences.

Scene indices are zero based. The plan contains the existing eleven `segments` with unchanged 0–180 second boundaries. The default plan loads `submission/video-edit.json`; the integration renderer can supply its updated v0.2 plan directly. `verified_core_tests` supplies the existing test receipt count. Graphics use the v0.2 badge regardless of the v0.1 plan badge.

Canonical outputs: `build/video-v0.2/motion/scene-00.mp4` through `scene-10.mp4`, 1920×1080, 30 frames per second, silent H.264. These are motion bases for the assembler. They do not replace the source footage or soundtrack.

Scene 3 reads `build/video-v0.2/assets/glasses-turntable.mp4` when present. It decodes the full-frame warm-paper 3D clip first and draws the editorial type above it. The product occupies the right side around `(1320,590)`. The left `x=90–740` is reserved for type. Do not composite the old native recording into scene 3. If the product clip arrives after scene 3 was rendered, rerender scene 3. Without that asset, the preview shows an explicitly labelled placement note; it is not an accepted final product scene.

The assembler owns these unchanged source windows:

| Scene | Source window | Start within scene |
| --- | --- | --- |
| 1 | Native at `(1185,145)`, 635×844 | 0 seconds |
| 1 | Same recording crop at `(92,530)`, 960×240 | 0 seconds |
| 5 | Phone at `(1060,138)`, 770×873 | 6 seconds |
| 6 | Phone at `(1060,138)`, 770×873 | 0 seconds |
| 10 | Native at `(1210,148)`, 610×810 | 0 seconds |

All source labels sit outside those rectangles. Existing footage predates Build 40 and does not prove its font changes.

## Story and motion

| Scene | Time | Editorial sequence |
| --- | --- | --- |
| 0 | 0–8 | The clipped listening headline appears over a travelling explanatory sound envelope. |
| 1 | 8–16 | Headline and traced underline introduce two correctly labelled views of the same real recording. |
| 2 | 16–36 | 100 marks arrive. Twenty-five turn red progressively. The same marks physically regroup into four equal groups. The comparison lands on “about one quarter” and “1 in 4.” |
| 3 | 36–48 | The original 3D turntable runs continuously beside staggered product and stack names. |
| 4 | 48–60 | Two listening settings share moving audio envelopes and a traced connective rule. The prayer disclaimer remains present. |
| 5 | 60–90 | The single reserved masjid slot remains explicit. Existing phone reference appears after six seconds. A slot-duration rail advances below the copy. |
| 6 | 90–112 | A highlighted source window advances over abstract word positions while the genuine changing source card plays on the right. |
| 7 | 112–138 | Sound representation becomes transcript, canonical word position, published source and lens window. A travelling red evidence marker and staged rail guide attention. Spark opens as a blue conditional branch, with validation and cached paired-source plans. The branch reads “MUSE SPARK · WHEN NEEDED” throughout its visible interval. |
| 8 | 138–152 | The Arabic reference schematic gains published English meaning as a labelled explanatory mode change. It is not a filmed toggle or tajweed grader. |
| 9 | 152–168 | The 114-surah, 6,236-reference-ayah and 59-test figures build separately. A yellow future-teaching insert appears with the required development/testing qualification. |
| 10 | 168–180 | The listening motif returns beside the real native recording and repository address. |

The population caption remains visible: Pew Research Center, 2020 estimate, published 2025. The underlying estimate is 25.6%. The 25-of-100 chart is a rounded comparison, not an exact 25.0% census or a claim that the entire population needs the product.

Sources: [Muslim population change](https://www.pewresearch.org/religion/2025/06/09/muslim-population-change/) and [global religious landscape](https://www.pewresearch.org/religion/2025/06/09/how-the-global-religious-landscape-changed-from-2010-to-2020/).

The technical source example is read verbatim from `App/Resources/verses.json`, Pickthall 1:3: “The Beneficent, the Merciful.” The diagram makes no acoustic word-timestamp claim. Muse Voice transcribes; local software matches and tracks; published Arabic/Pickthall supplies the displayed wording. Spark assists bounded ambiguity and paired-source plans conditionally. Validated source plans are cached. No generated translation is implied.

## Verification

The population and causal timeline checks were written first. The empty population implementation failed the partial-build assertion. After that function passed, the initial causal-stage implementation failed its five-stage assertion. Both implementations then passed.

Graphics use the task-authorized visual verification path instead of screenshot-mirroring unit tests. The check compares semantic content regions rather than badges or footer progress. It verifies substantial changes between population and technical stages, then verifies that every scene changes within its content region.

Run:

```sh
python3 tools/editorial_motion.py --check
python3 tools/editorial_motion.py --preview
python3 tools/editorial_motion.py --render
python3 tools/editorial_motion.py --render --scene 3
```

`--preview` writes `preview/storyboard.jpg`, `preview/stages-02.jpg`, `preview/stages-07.jpg`, full-resolution keyframes, `preview/population-motion.mp4` and `preview/technical-motion.mp4`. The two motion proofs are 12 and 24 seconds at 30 frames per second. All generated artifacts stay in ignored `build/video-v0.2/`.

The storyboard and stage sheets were visually inspected by the motion-renderer agent. The population regrouping, type hierarchy and source caption were legible. The first technical inspection found a connector crossing the explanation; the branch was moved into its own band before final preview generation. The final assembled footage, audio mix, complete 180-second playback and actual 3D silhouette remain integration checks.
