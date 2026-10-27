# Next: prove the first original glasses loop

Status: IN PROGRESS. Updated discovery fix installed. Launch was blocked by the locked iPhone. The wearer reported registration success but no eligible display devices in the preceding build.

## First action

Read `CHECKPOINT.md`. Unlock the phone and open Ayah Lens, or use the maintained launch helper. Observe whether the status becomes “Display glasses available.” Then retry the lens action. If it remains waiting, inspect discovery/transport evidence before another code change. Do not claim the hardware issue is fixed without wearer confirmation.

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
