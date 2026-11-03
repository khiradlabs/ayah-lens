# Next Ayah Lens task

Status: Full video v0.6 now contains completed OpenAI Marin narration. Current review master: build/video-v0.6/Ayah-Lens-Demo-v0.6.mp4.

## Remaining production work

Replace the labelled 1:00–1:30 masjid fill with suitable approved footage. Human final review should check pronunciation, delivery, pacing and the complete cut before release. The generated narration is complete; do not treat the old Daniel guide as current. Preserve the 179.900-second duration and all earlier exports.

The masjid slot remains a six-second placeholder followed by 24 seconds of labelled phone reference. It is not completed continuous masjid proof. Recheck picture/audio duration and source labels after replacement. Final public links, publishing, submission and the production-bound repository merge retain existing approval boundaries. Do not ask again for approval of the hook, integration or OpenAI provider choice.

## Current evidence and reproduction

- Implementation f8835f6 generated 16 consistent Marin clips. All 260 normalized approved words were verified against actual generated-English audio.
- The full output is 179.900 seconds, 5,397 frames, 1080p30fps, 48kHz stereo and -3dBFS peak. Genuine source audio at 0–8, 30–38 and 60–90 retains timing and speed.
- Ten tests, full decode, protected audio, source picture, caption and provenance checks passed. Independent spec, quality and sampled visual reviews passed. Actual OpenAI audio-model analysis found no material defect; human listening remains unverified.
- Run python3 tools/test_openai_narration.py and python3 tools/openai_narration.py --check for read-only verification. Generation/render options require --note. Source instructions are in submission/OPENAI-NARRATION-V0.6-SPEC.md and the narration manifest.
- Private receipts and auditions live under build/video-v0.6/. The approximate USD0.266544 total is a planning estimate, not invoice actuals. No more generation is required unless Faraz requests changes.

## Credential and access boundaries

OPENAI_API_KEY is configured in the user-authorized private file /Users/farazsyed/.secrets/ayah-lens-openai.env, mode600. Never print it or put it in arguments, commits or logs. Use that file only for the requested API work. An optional vault backup was auto-review rejected and never executed. Do not retry cloud-vault storage without explicit approval.

The user explicitly changed narration provider to OpenAI. The earlier Muse API-example question and ElevenLabs alternative are superseded. Do not reopen that investigation unless asked. A prior Muse UI response read was rejected because unrelated private history was present; do not retry or bypass that route.

## Persistent constraints

- App version 0.3.0 Build 40 was installed, metadata-verified and launched. Video numbering is separate from app numbering.
- Existing demonstration footage predates Build 40 and does not establish its larger text readability. The English switch passed the wearer check in Build 31.
- The 59-test app receipt is build/logs/core-tests.log. Do not rerun app tests for video-only edits.
- Audio-buffer investigation remains explicitly deferred. Faraz confirmed the phone stayed open and unlocked when the error occurred. Do not repeat that question or restart work without direction.
- Keep QuickTime stopped. Do not start new recording without a requested capture. Keep raw clips, private diagnostics and all media outputs ignored.
- A failed recording is not reliable proof footage. Preserve genuine long-passage following and distinguish native camera/display composites from optical lens filming.
- The implementation draft PR is https://github.com/khiradlabs/ayah-lens/pull/1. Reviewed implementation must reach the public default branch before final submission.
- The recorded deadline is November 4 at 8 PM America/Chicago. Recheck the platform before submitting. Two personal Meta API opinion ratings remain Faraz's choice.

## Artwork and source rights

Faraz reported sending the Meta asset exception request on November 2. The request copy is build/meta-display-page-review/meta-asset-exception-request.txt. Permission remains pending. Do not resend. Keep official Meta website images, frames and models out of exports and the public repository until actual approval covers reuse. Original Muse-generated listener artwork has its private prompt, usage and hash receipt under build/video-v0.4-opening/assets/.

The supplied YouTube motion reference is https://www.youtube.com/watch?v=uIHJvUVaB34. Primary captions and sampled example review live under build/reference-uIHJvUVaB34/. Apply argument-led scene transformation, recurring motifs, layered artwork and narration-led timing. No paid reference presets or third-party media were acquired.
