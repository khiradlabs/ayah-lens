# Ayah Lens demo script Version 3

Three-minute submission video. Device baseline: version 0.3.0, Build 31. Video v0.1 in production from script Version 3; guide narration and reserved masjid slot.

Let viewers experience unfamiliar recitation, then reveal its meaning through genuine output. Explain the population and Meta implementation after that experience. Keep the uninterrupted proof section intact.

The source timeline is demo-timeline.json. Run python3 tools/render_demo_script.py after changing timing or narration. Production checks and source claims are in CAPTURE-LIST.md and CLAIMS.md.

## 0:00 to 0:08 Let the viewer hear before explaining

Spoken narration

No voiceover. Keep the real recitation audible.

Picture

Open on a dark designed frame with Just listen. Play eight seconds of the actual supplied recitation. No narrator or music competes with the source audio.

On screen

Just listen.

## 0:08 to 0:16 Reveal the meaning

Spoken narration

No voiceover. Keep the real recitation audible.

Picture

Replay the same eight-second excerpt as a native camera-plus-display recording, beside an enlargement from the same frames. Label both views accurately. Keep the edit apparent; this is not optical camera-through-lens footage.

On screen

Now follow the meaning.
Native glasses recording | Enlarged display from the same recording

## 0:16 to 0:36 Make the experience universal

Spoken narration

If Arabic is unfamiliar, you just felt the gap between hearing words and following their meaning. About two billion people are Muslim. For many of us, that gap is part of everyday listening. What if the meaning could stay with us?

Picture

Return to the same listener. Let the population figure appear briefly beside real human footage. The number gives scale after the viewer has experienced the need. Keep the small population source caption readable.

On screen

About 2 billion Muslims
Pew Research Center · 2020 estimate, published 2025

## 0:36 to 0:48 Name the product and Meta stack

Spoken narration

Meet Ayah Lens. Meta glasses, Muse Voice, and Muse Spark, working together to bring Quran recitation and its English meaning into view.

Picture

A crisp product shot of the actual glasses. Introduce each Meta component as its name is spoken, then return to the working phone and glasses. Add all words in post.

On screen

Ayah Lens
Meta glasses + Muse Voice + Muse Spark

## 0:48 to 1:00 Carry one listening experience between settings

Spoken narration

During Salat, Muslim prayer, it could help listeners follow the recitation. At home, it can follow a reciter playing on television. Hands free.

Picture

Match the wearer’s position across a proposed prayer scene and the television listening scene. Let the same frame composition connect the settings. Keep the religious-permissibility disclaimer visible for the entire prayer scene. Use cleared recitation footage and audio.

On screen

Technology demonstration only. This does not establish religious permissibility for use during prayer.

## 1:00 to 1:30 Prove the live experience without cuts

Spoken narration

No voiceover. Keep the real recitation audible.

Picture

Reserve this30-second block for the forthcoming masjid recording. The review cut uses a six-second placeholder card and24 seconds of existing within-73:20 phone footage, persistently labelled as reference footage awaiting replacement. The final masjid take should preserve genuine continuous recitation and automatic following.

On screen

MASJID RECORDING / RESERVED
Reference footage / replace with masjid take

## 1:30 to 1:52 Reveal the difficult part hiding in plain sight

Spoken narration

Now look closer. We are still inside the same passage. A long verse cannot fit on this lens. Ayah Lens follows the recitation through it, showing the relevant portion as the words continue. Nobody is turning a page.

Picture

Freeze the passage identifier for emphasis while the genuine captured portions continue to change. Briefly show a full-source reference beside the compact display window, labelled Explanatory graphic. Keep the real device footage visible. Show the challenge at a glance rather than teaching verse numbering.

On screen

Same passage · changing portions
No manual paging

## 1:52 to 2:18 Explain the actual AI and tracking work

Spoken narration

Muse Voice converts the glasses’ audio into Arabic text. Muse Spark helps pair Arabic phrases with portions of a published English translation. It can also assist with uncertain passage matches. Our software tracks the position, validates the source boundaries, and sends the current portion to the glasses.

Picture

Build a clean exploded diagram around a product shot. Audio enters Muse Voice; the live transcript reaches our passage tracker; Spark-assisted paired source spans supply the display portions. Show cached plans on a separate branch, with bounded ambiguity assistance as another branch. Reassemble the diagram into the actual lens/preview footage.

On screen

Muse Voice · live transcription
Muse Spark · source pairing and ambiguity assistance
Filmed phrase plans cached

## 2:18 to 2:32 Show memorization practice and listener choice

Spoken narration

Hifz means memorizing the Quran. Arabic-only mode offers a reference while rehearsing. Turn English back on whenever you want to follow the meaning.

Picture

Use a labelled explanatory graphic showing Arabic-only reference mode for Hifz and Arabic with English for following meaning. The feature passed the wearer test, but no supplied clip shows an actual toggle interaction. Do not substitute the brief unpaired-translation gap as switch proof.

On screen

Hifz · Quran memorization practice
Arabic reference | Arabic with English meaning

## 2:32 to 2:48 Establish the working foundation

Spoken narration

The reference covers all 114 surahs. We built the glasses integration and automatic following during this hackathon. Fifty-nine tests cover matching, source preservation, and display scheduling. With further development and extensive testing, future versions could support Quran teaching.

Picture

Keep the working product prominent. Show brief readable inserts of the actual source library, event-dated Git history and verified test result. Then introduce a short card labelled Future: teaching support, requires extensive testing. Complete reference coverage remains separate from recognition accuracy; the teaching card describes future work.

On screen

Complete reference library · original event work · 59 core tests passed
Then: Future: teaching support · requires extensive testing

## 2:48 to 3:00 Return to the opening experience

Spoken narration

The words were already there. Ayah Lens brings their meaning into view. Hear the recitation. Follow the meaning.

Picture

Return to the exact opening composition, now with the genuine readable display sample. End on the project name and public repository address. Give the final line room to land.

On screen

Ayah Lens
Hear the recitation. Follow the meaning.

## Recording notes

Total narration: 250 words. The timeline reserves 46 seconds for unvoiced live recitation proof. Aim for a calm delivery and preserve those proof sections.

The opening is an edited listen/reveal replay. The review cut reserves1:00–1:30 for masjid footage; its current fill is explicitly labelled reference footage, not completed30-second masjid proof.

The review opening uses the supplied native112:1–4 excerpt. Its first eight seconds are replayed in the meaning reveal. Keep real source audio and display labels accurate.

The viewer condition matters: say “If Arabic is unfamiliar.” Do not assume that every judge is unfamiliar with Arabic or claim that all Muslims lack understanding.

The prayer scene presents a possible use. Keep its religious-permissibility disclaimer readable beside the scene and repeat it in the final video description.

The Show English meaning switch is implemented in Build 31. The wearer confirmed English disappears and returns on phone and glasses while Arabic keeps following. Capture the actual control in a separate take.

If the translation switch is unavailable, replace the 2:18–2:32 narration with: “The phone preview mirrors the selected lens window. The full passage remains available on the phone. The glasses keep a compact portion in view as the recitation continues.”

The source text is published Tanzil Arabic and Pickthall English. Spark supplies paired source boundaries; it does not author the displayed translation.

The filmed long-passage plans are cached. Voice transcription is live. Complete reference coverage is not a full-Quran accuracy result.

The population estimate comes from Pew Research Center: https://www.pewresearch.org/short-reads/2025/06/10/islam-was-the-worlds-fastest-growing-religion-from-2010-to-2020/

Create text, diagrams and labels in post. Do not generate scripture text inside imagery. Preserve the original published wording.

Any enlarged phone preview or explanatory graphic remains labelled. Show the actual compact glasses display accurately.

Optional stretch reveal: a second person selects a prepared recitation excerpt while hands stay off the phone. Film only after successful acquisition/recovery checks. Do not call this any-verse or blind full-Quran accuracy proof.

Present Hifz as using an Arabic reference while rehearsing. Demonstrate the existing visibility switch and recitation-following behavior.

Quran teaching is a future direction requiring dedicated development and extensive evaluation with qualified teachers. The current implementation uses pretrained Muse models; no specialized teaching model has been trained or validated.

## Rubric priorities

Impact 30%: turn an unfamiliar-language listening experience into something the viewer can personally recognize, then establish population scale and prayer/home use.

Meta tooling 25%: connect the glasses, live speech model and Spark-assisted source pairing to the visible experience. Explain cached plans honestly.

Technical execution 20%: make within-passage movement the second reveal, followed by source preservation, actual implementation evidence and tests.

Demo 25%: use the edited opening reveal, a genuine 30-second continuous take, matched scenes and a closing return to the original image.
