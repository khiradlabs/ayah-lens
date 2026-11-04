# Ayah Lens demo script Draft 1

Three-minute submission video. Baseline: version 0.3.0, Build 28. Narration is ready for review; live footage remains to be captured.

Lead with the working glasses. Keep the main recitation proof continuous. Use the matching phone Lens preview for legibility and label it separately from actual lens footage.

The source timeline is demo-timeline.json. Run python3 tools/render_demo_script.py after changing timing or narration. Production checks and source claims are in CAPTURE-LIST.md and CLAIMS.md.

## 0:00 to 0:08 Show the working glasses first

Spoken narration

No voiceover. Keep the real recitation audible.

Picture

Actual glasses output and the live phone Lens preview, with the same recitation audible. Keep this opening continuous.

On screen

Ayah Lens · Follow the meaning

## 0:08 to 0:34 Establish the human need

Spoken narration

About two billion people are Muslim, roughly a quarter of humanity. Five daily prayers make recitation a recurring part of worship. Three include passages recited aloud in congregation. For listeners who do not understand Arabic, following the meaning can mean looking away from the recitation.

Picture

Faraz on camera, then a simple population card and a listener wearing the glasses. Use everyday listening footage, without staging a claim of formal-prayer approval.

On screen

About 2 billion Muslims · Pew 2020 estimate, published 2025
Five daily prayers · recurring listening context

## 0:34 to 0:48 Introduce the product

Spoken narration

Ayah Lens listens through Meta Ray-Ban Display glasses and brings the Arabic and published English meaning into view. Start listening once, then follow hands free.

Picture

Show version 0.3.0 Build 28, the external recitation source and Start Muse live Quran. Establish that the phone stays foregrounded.

On screen

Glasses microphone → live recitation following

## 0:48 to 1:23 Prove automatic following

Spoken narration

No voiceover. Keep the real recitation audible.

Picture

One continuous external-reciter take of 73:20 or 2:102. Show actual lens output and the matching Lens preview. Keep at least 25 seconds uncut and retain recitation audio. Capture at least three automatic window changes without touching Next.

On screen

Actual glasses display | Live phone preview
Keep each label attached to its own view.

## 1:23 to 1:41 Explain within ayah following

Spoken narration

The hard part is following a long ayah. The display moves through the relevant portion automatically, with a little upcoming context. No page turning is needed as the recitation continues.

Picture

Continue the same passage. Point out the same verse ID while the source portion changes. An explanatory close-up can follow the continuous proof take.

On screen

Same ayah · automatic portion changes

## 1:41 to 2:11 Show what Muse contributes

Spoken narration

Muse Voice Transcribe supplies the live Arabic transcript. Muse Spark helps resolve uncertain verse candidates, and pairs Arabic phrases with ranges from the published Pickthall translation. We validate those boundaries and cache them. Local code tracks the position and selects the source text. Spark’s contribution is visible here: usable meaning alongside a moving recitation.

Picture

Use a simple architecture diagram, then show one real paired source window. Label cached phrase plans accurately. If showing candidate-resolution evidence, identify the selected synthetic diagnostic separately from the live take.

On screen

Muse Voice Transcribe · live Arabic
Muse Spark 1.3 · candidate decisions and paired source portions
Phrase plan cached · displayed text from attributed sources

## 2:11 to 2:30 Explain source trust and scope

Spoken narration

The display uses unchanged Tanzil Arabic and Pickthall English. The full reference covers 114 surahs and 6,236 ayahs. This prototype identifies passages and follows supported phrases; shared openings can wait for more evidence.

Picture

Show the source attribution, one canonical-reference lookup and an unchanged source slice. Distinguish full reference coverage from measured recognition accuracy.

On screen

114 surahs · 6,236 reference ayahs
Arabic: Tanzil · English: Pickthall

## 2:30 to 2:44 Make the new work visible

Spoken narration

Built during the hackathon: the glasses integration, live Muse client, verse retrieval, phrase tracking, and automatic display. Fifty-two automated tests cover core matching, source preservation, and display scheduling.

Picture

Show real event-dated Git history, original source modules and the existing 52-test result. Keep credentials and private test receipts out of this view.

On screen

Original event implementation · October 26–29
52 automated tests passed

## 2:44 to 2:55 State the next milestone

Spoken narration

Today, the prototype supports selected hands-free listening demonstrations. Next comes broader reciter testing and language support, with reliable meaning in view as the goal.

Picture

Return to Faraz and the working device. Treat broader reciters and additional languages as future work.

On screen

Working prototype · English meaning
Next: broader reciter evaluation

## 2:55 to 3:00 Close on the user benefit

Spoken narration

Ayah Lens. Hear the recitation. Follow the meaning.

Picture

End with the working glasses and a readable project/repository address. Add the final accessible video/submission link only when available.

On screen

Ayah Lens
Hear the recitation. Follow the meaning.

## Recording notes

Total narration: 247 words. The timeline reserves 43 seconds for unvoiced live recitation proof. Aim for a calm delivery and preserve those proof sections.

Use source-labelled population figures. Five daily prayers describes the recurring context; it is not a claim that every Muslim would use this product. Keep all-day operation, universal accuracy and measured latency out of the narration.

Do not imply that every live frame triggers Spark. The paired plans for the filmed long ayahs are cached. The footage should demonstrate the resulting behavior, with the model role explained accurately.
