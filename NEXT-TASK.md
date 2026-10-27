# Next: prove the first original glasses loop

Status: IN PROGRESS. Wearer confirmed lens text works. Combined action crashed in the audio callback. The verified callback correction is installed; the phone was locked at launch.

## First action

Read `CHECKPOINT.md`. Unlock and open Ayah Lens. Tap Start microphone + lens while wearing the glasses. Confirm that the app stays open, the microphone counter increases while speaking, and the lens text remains visible. If it fails, retrieve the new crash report or exact on-screen error before changing anything else.

The requested sequence is Register glasses → Show selected verse on lens → Start microphone + lens. The wearer should see readable Arabic and English while the phone sample counter increases.

## Definition of done

- Registration succeeds for the original app.
- Arabic and the attributed translation are readable in the actual lens.
- Both remain visible during real microphone capture.
- Stop releases the session, and the observed result is recorded with its limitations.

If there is a failure, capture the displayed error and local SDK evidence before changing code. Stock display/audio results do not establish combined-mode success.

Once this passes, implement recognition for one short passage. Keep the canonical text and translation unchanged; match to identifiers. Use only cleared audio sources for external inference, and obtain spending approval before paid calls.

## Setup already complete

Apple agreement acceptance, development-device registration approval, Meta AI Developer Mode, and glasses developer-component installation were completed. Do not request them again.

Use `tools/device.py launch` with the currently selected AYAH_DEVICE_ID if the user asks to reopen the app. The phone must be unlocked.
