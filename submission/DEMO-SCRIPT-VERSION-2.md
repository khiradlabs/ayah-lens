# Ayah Lens demo script Version 2

Three-minute submission video. Device baseline: version 0.3.0, Build 28. Rubric-led script revision; footage pending; translation switch pending implementation.

Lead with the population and listening need while showing the real glasses. Make automatic following visible before explaining the implementation.

The source timeline is demo-timeline.json. Run python3 tools/render_demo_script.py after changing timing or narration. Production checks and source claims are in CAPTURE-LIST.md and CLAIMS.md.

## 0:00 to 0:24 Establish the listening need

Spoken narration

About two billion people are Muslim. Recitation is part of five daily prayers. For many of us, Arabic is not our everyday language. We hear the recitation, but following its meaning takes another step. What if that meaning could stay in view, while we listen?

Picture

Begin with a person wearing the real glasses while recitation plays softly beneath narration. Show the population caption briefly. Reveal a legible actual-lens sample before the product introduction. Keep the phone preview separately labelled.

On screen

About 2 billion Muslims
Pew Research Center · 2020 estimate, published 2025

## 0:24 to 0:43 Introduce the Meta experience

Spoken narration

Meet Ayah Lens. Built for Meta Ray-Ban Display glasses, powered by Muse Voice and Muse Spark. It listens to Quran recitation and brings the Arabic and published English meaning into view. Start listening, then follow hands free.

Picture

Show the actual glasses, then the real app starting a Muse session. Establish the external recitation source. Put the real optical sample beside a readable phone preview, with labels attached to each.

On screen

Ayah Lens
Meta glasses + Muse Voice + Muse Spark

## 0:43 to 0:58 Connect prayer and home listening

Spoken narration

One possibility is following the recitation during Salat, Muslim prayer. Another is listening to a reciter on television. In either setting, the goal is to follow the meaning without holding a phone.

Picture

Show a proposed prayer-listening scene with the disclaimer readable for the full scene. Then show actual external-reciter listening from a television or second device, using footage and audio cleared for publication. The scene proposes a use, without asserting religious approval.

On screen

Technology demonstration only. This does not establish religious permissibility for use during prayer.

## 0:58 to 1:28 Prove automatic following

Spoken narration

No voiceover. Keep the real recitation audible.

Picture

Keep 30 seconds continuous with real recitation audible and no voiceover or music. Show at least three automatic changes inside the same long passage. Hands stay away from the phone after Start. Use the proven 73:20 or 2:102 setup and label the optical view and phone preview separately.

On screen

Actual glasses display | Live phone preview
Continuous recording · automatic passage following

## 1:28 to 1:59 Explain what Meta AI contributes

Spoken narration

Muse Voice turns audio from the glasses into Arabic text. Muse Spark helps pair Arabic phrases with corresponding portions of a published English translation. That makes long passages manageable on a small display. Spark can also help resolve uncertain passage matches. The glasses, speech model, and reasoning model each serve the same experience: following the meaning as you listen.

Picture

Animate the actual pipeline: glasses audio, live Muse Voice transcript, local passage tracker, Spark-assisted paired portions, lens. Show real source-boundary evidence. Label Spark plans Cached for the filmed passages. Distinguish bounded candidate assistance from the normal direct-match path. Avoid a fake live request counter.

On screen

Muse Voice · live transcription
Muse Spark · bilingual pairing and ambiguity assistance
Filmed phrase plans cached

## 1:59 to 2:27 Make the engineering visible

Spoken narration

A long passage cannot fit on the lens at once. Our software tracks the recitation within that passage and updates the relevant portion automatically. It validates source boundaries and preserves the published wording. The reference library contains the complete Quran. Fifty-two automated tests cover core matching, source preservation, and display scheduling.

Picture

Use a readable close-up of the same passage changing portions. Show the phone Lens preview beside the optical sample, then a short source-validation graphic, the actual test result and event-dated implementation history. Keep full reference coverage separate from recognition accuracy.

On screen

Automatic movement within long passages
114 surahs · 6,236 reference ayahs
52 core tests passed · original event implementation

## 2:27 to 2:45 Show listener choice

Spoken narration

Listeners can choose Arabic alone, or keep the English meaning beside it. The goal is to let each person follow in the way that helps them. This prototype brings that choice into a wearable listening experience.

Picture

After the translation switch is implemented and verified, film the actual control changing the lens and phone preview. Keep the recognized position unchanged. Until then, replace this segment with the supplied fallback narration and genuine working bilingual footage.

On screen

Arabic only | Arabic with English meaning

## 2:45 to 3:00 Close on the benefit

Spoken narration

The next step is broader testing across reciters and listening environments. The ambition is simple: help people connect what they hear with what it means. Ayah Lens. Hear the recitation. Follow the meaning.

Picture

Return to the real wearer and working glasses. End with the project name and public repository address. Keep any future-language claims out of the working-feature footage.

On screen

Ayah Lens
Hear the recitation. Follow the meaning.

## Recording notes

Total narration: 293 words. The timeline reserves 30 seconds for unvoiced live recitation proof. Aim for a calm delivery and preserve those proof sections.

The prayer scene presents a possible use. Keep its religious-permissibility disclaimer readable beside the scene and repeat it in the final video description.

The listener-choice scene requires the requested translation switch to work on both phone preview and lens. It has not been implemented in Build 28.

If the switch is unavailable, use this replacement narration for 2:27–2:45: "Here, the phone preview mirrors the selected lens window. The full passage remains available on the phone. The glasses keep a compact portion in view while the listener follows the recitation hands free."

The source text is published Tanzil Arabic and Pickthall English. Spark supplies paired source boundaries; it does not author the displayed translation.

The filmed long-passage plans are cached. Voice transcription is live. Complete reference coverage is not a full-Quran accuracy result.

The population estimate comes from Pew Research Center: https://www.pewresearch.org/short-reads/2025/06/10/islam-was-the-worlds-fastest-growing-religion-from-2010-to-2020/

## Rubric priorities

Impact 30%: establish the recurring listening need, show two understandable situations, and return to the wearer. Do not equate population with adoption.

Meta tooling 25%: name the hardware and both models early, then demonstrate their distinct contributions. Hardware complements model use; model count earns no stated automatic bonus.

Technical execution 20%: show within-passage tracking, source preservation, actual event work and verified tests. Keep timing and accuracy claims within measured evidence.

Demo 25%: reveal working output early, retain 30 seconds of uncut proof, use readable labels and let the ending return to the human benefit.

