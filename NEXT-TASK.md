# Next Ayah Lens task

Status: The approved opening is integrated into full video v0.5. The current review master is build/video-v0.5/Ayah-Lens-Demo-v0.5.mp4.

## Narration provider choice

Faraz requested Meta Muse voice generation with emotion. Official documentation and the account model catalog confirm no Muse speech-synthesis model is available. No narration generation occurred. The availability evidence and emotional directions are under build/meta-voice-recon/.

Pending choice: may we use ElevenLabs v3 through the existing fal setup for two expressive hook samples, capped at USD1 outside Meta credits? Do not perform alternative-provider paid calls until Faraz answers. Existing fal credentials were checked for presence only. If approved, use the maintained tools/fal/fal.py helper with --note and correct cost logging. Audition the approved hook first, then update full narration and sync while retaining the 180-second cap. Do not clone a real voice or replace genuine recitation.

## Remaining production work

Replace the labelled 1:00–1:30 masjid fill with suitable approved footage and finish narration. The current master runs 179.900 seconds. Preserve its three-minute limit and all earlier exports. Do not ask again for opening or integration approval; Faraz already approved both.

The masjid slot remains a six-second placeholder followed by 24 seconds of labelled phone reference. It is not completed continuous masjid proof. Narration remains temporary local Daniel, and captions are approximate. Recheck the full picture/audio duration and source labels after any replacement.

Public video/repository links, final form submission and the production-bound repository merge retain their existing approval boundaries. Final links must work while signed out.

## Current evidence and reproduction

- Implementation b813cc9 integrates the accepted opening at 0–38 and retimes only the editorial product section into 38–48. Original footage after 48 seconds retains timing and speed.
- Full output is 179.900 seconds, 5,397 frames, 1920×1080/30fps and 48kHz stereo. Peak is -3dBFS. Input hashes stayed unchanged.
- Six tests, full decode, source/audio/caption comparisons and independent visual, specification and quality reviews passed. Uninterrupted human playback and pronunciation were not assessed.
- Use python3 tools/test_full_demo_assembly.py and python3 tools/assemble_full_demo.py --check for read-only verification. Rebuild with python3 tools/assemble_full_demo.py. The separate submission/full-video-v0.5.json manifest keeps older renderer assumptions intact.
- The editorial video-version badge is replaced only within the documented header rectangle from 38 seconds onward. Pillow renders this post-production label because FFmpeg drawtext is unavailable.
- Private reviews and receipts are under build/video-v0.5/. The original Muse artwork was reused with zero new generation spend.

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
