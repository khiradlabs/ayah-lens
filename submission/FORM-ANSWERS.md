# Ayah Lens form answers Draft 1

Paste-ready copy for the fields shown in the October 29 submission screenshots. The live participant guide was also verified October 29. The final video link and two personal ratings remain open.

## Team Name

Ayah Lens

## Team Members

Keep Faraz Syed as shown. Add anyone else who actually contributed before final submission.

## Which track are you submitting to

Indie Developer Track

This matches the recorded application.

## Which problem statement did you build towards

Build for Your World

## Most Viral Track X post link

Leave blank unless a project post is published and entered for that award. No post is part of this draft.

## Project Description

Ayah Lens brings Quran recitation and its meaning into view on Meta Ray-Ban Display glasses. It is built for listeners who want English meaning alongside Arabic without looking down at a phone.

Quran recitation is part of daily worship. Five daily prayers give this a recurring context. The wider community includes about two billion Muslims, using Pew’s 2020 estimate. Our initial audience is people with compatible glasses who want English meaning.

The prototype listens through the glasses microphone, identifies the passage and follows supported phrases within an ayah. Compact Arabic and published Pickthall English windows advance automatically, including within long ayahs, without a Next button.

During the hackathon, we built the native iPhone/glasses integration, live Muse client, retrieval, phrase tracking and display scheduling. The full reference includes 114 surahs and 6,236 ayahs. Selected physical demonstrations worked with an external reciter. Broader reciter accuracy and comprehension benefits remain to be evaluated.

## Public GitHub Repository

https://github.com/khiradlabs/ayah-lens

Before submission, ensure the reviewed implementation is on the default branch. The current implementation review branch is feat/within-ayah-following.

## 3 Minute Demo Video

Add the final accessible video URL after capture and export. Do not paste a placeholder into the actual form.

## Describe your use of Meta products to build the submitted project

Meta Wearables Device Access Toolkit 1.0.1 connects the native Swift iPhone app to Meta Ray-Ban Display glasses. The app uses the glasses microphone and sends reading windows to the display.

Muse Voice Transcribe, through Meta Model API’s realtime WebSocket endpoint, supplies streaming Arabic transcripts. A local Quran index and source-word tracker identify the passage and supported position within it.

Muse Spark 1.3 has two roles. It can resolve uncertain retrieved verse candidates using constrained IDs or abstention. It also pairs Arabic source-word spans with corresponding ranges in the published Pickthall translation. We validate source identity, complete coverage and display bounds before using a plan, then cache it. The app displays only original reference slices.

The prototype also includes a separately labelled local fallback using Meta Omnilingual ASR through an attributed CoreML conversion. The core demo uses Muse Voice and Spark. Existing models, SDKs and reference texts are credited separately from our event implementation.

## Why are Meta models important to your solution

The core interaction starts with speech. Muse Voice Transcribe provides live Arabic partials so the application can follow recitation instead of requiring manual verse lookup.

Meaning must also fit a small display. Muse Spark pairs consecutive Arabic and published English source spans, helping the interface present relevant meaning as the listener moves through a long ayah. Accepted plans are cached, so the app does not need another alignment request for each display update. Spark also supports bounded decisions when retrieved verse candidates are uncertain.

These model roles connect the audio to the listening experience. Local code validates decisions, tracks position and selects unchanged source text. The glasses keep that text visible while the listener’s hands remain free.

## Provide feedback from your experience using partner technologies

Not applicable. The submitted prototype uses Meta Model API directly, without Fireworks, Modal or Baseten serving its inference.

## How likely are you to build with Meta Model API

Faraz’s choice required. Select one of Very likely, Somewhat likely, Neutral, Somewhat unlikely or Very unlikely.

## How would you describe your overall opinion of Meta Model API

Faraz’s choice required. Select one of Very favorable, Somewhat favorable, Neutral, Somewhat unfavorable or Very unfavorable.

## Before final submission

The video URL must be real and accessible. The repository root must expose the reviewed source. Contributor and opinion fields need the entrant’s final check. This draft has not been entered or submitted.

Population and prayer references are in CLAIMS.md. The two subjective ratings are intentionally not chosen on the entrant’s behalf.
