# Ayah Lens submission copy Draft 1

## Project

Ayah Lens

## Track and theme

Indie Developer. Build for Your World.

These match the recorded application. Reconfirm the accepted participant profile before submitting.

## One sentence

Ayah Lens follows Quran recitation on Meta Ray-Ban Display glasses and brings the relevant Arabic and published English meaning into view automatically.

## Problem and impact

Quran recitation is part of daily worship. For listeners who do not understand Arabic, a translation on a phone can compete with attention to the reciter. Ayah Lens explores a hands-free way to keep meaning in view.

The wider context is a Muslim population estimated at about two billion in 2020. Our initial audience is narrower: compatible-glasses users who want English meaning alongside recitation. The prototype has been tested in selected listening demonstrations; comprehension improvement and adoption have not been measured.

## What we built

During the event, we built a native iPhone app connecting the glasses microphone and display to live Muse transcription. A full-Quran reference index identifies the passage. A word-position tracker follows supported phrases within long ayahs, and compact reading windows advance automatically without a Next button.

The reference bundles 114 surahs and 6,236 ayahs. Display text comes from unchanged Tanzil Arabic and the published Pickthall translation. Reference coverage is broader than the set of passages validated live.

## Meta model contribution

Muse Voice Transcribe supplies streaming Arabic. Muse Spark 1.3 supports bounded candidate selection and pairs source-word ranges from Arabic with the published English reference. We validate coverage, source identity and size before using a plan, then cache it.

For a cached demonstration passage, the display uses that accepted plan while local code follows the current recitation position. Other long ayahs can follow Arabic while a paired translation plan is prepared. The models do not supply replacement scripture for the display.

## Technical execution

The app preserves the glasses microphone route, processes bounded evidence, discards stale decisions, and keeps only the newest pending display frame. Fifty-two automated tests cover core matching, source preservation, portions and scheduling. This is a foreground prototype; broader reciter accuracy and visible-lens latency remain unmeasured.

## Original work and existing inputs

Original event work includes the app integration, Muse clients, retrieval, source-word tracking, phrase-boundary validation, cache and display scheduling. Existing models, SDKs and reference texts are attributed in CONTRIBUTIONS.md and ATTRIBUTION.md. Pre-event preparation is identified separately.

## Links and final fields

Repository: https://github.com/khiradlabs/ayah-lens

Implementation review branch: https://github.com/khiradlabs/ayah-lens/tree/feat/within-ayah-following

Video URL: add only after the final three-minute cut is uploaded and checked while signed out.

Entrant and contributor fields: copy the accepted profile and list all actual contributors. Do not guess legal acceptance fields or submit this draft automatically.
