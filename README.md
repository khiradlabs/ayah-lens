# Ayah Lens

A hackathon prototype for following Quran recitation with Arabic text and a published translation on Meta Ray-Ban Display glasses.

## Status

Repository and project documentation established on October 26, 2026. Application implementation has not started. Physical glasses audio and display validation is in progress using Meta's existing sample applications.

The participant guide lists October 27 through November 4 as the building period. Competition application code will be identified separately from pre-event preparation and third-party dependencies.

## What we aim to demonstrate

- Listen to a reciter through a verified glasses microphone path.
- Identify the verse and show its Arabic text and a published translation.
- Follow a short passage without manual verse lookup.
- Handle selected pauses, repeated phrases and ambiguous matches.
- Demonstrate a useful, verifiable role for Meta models.

These are prototype goals, not claims of completed capabilities. All-day operation and production deployment are outside the hackathon scope.

## Planned approach

An iPhone companion application connects through Meta's Wearables Device Access Toolkit. We will compare Meta Muse Voice Transcribe with Meta Omnilingual ASR before choosing the prototype recognition path. A verse matcher selects canonical text. Muse Spark may help resolve ambiguity or select source-backed answers after its contribution is validated.

Arabic and published translations come from attributed sources. Generative models will not author replacement Quran text or translations.

## Verification priorities

1. Prove real glasses audio capture and actual lens output.
2. Demonstrate a correct short live passage.
3. Record verse-match accuracy, false matches and time to stable text on a small documented evaluation.
4. Rehearse a repeatable three-minute demonstration.

The microphone test includes an external reciter because hearing the wearer does not establish that the glasses can follow someone else.

## Project provenance and licensing

See [CONTRIBUTIONS.md](CONTRIBUTIONS.md) for the event-work boundary and dependency attribution.

Original code in this repository is MIT licensed. Third-party models, SDKs, datasets, fonts and translations retain their own licences. Dataset access does not establish permission to redistribute recordings or upload participants' voices to another service.

Secrets, private recordings, datasets, downloaded model weights and local evaluation artifacts must not be committed.
