# Next: locate Muse recognition-to-display delay

Status: Timing diagnostics are implemented and verified locally. Check private action gates and build/logs/muse-test-approval.json for the current physical validation result and remaining authorization scope. Do not rely on historical pending-approval text in older checkpoint sections.

## First action

Obtain the response to the question: did the phone transcript lag too, or only the lens? A new build adds a Muse timing disclosure with provider audio-processing gap, matcher duration and lens-send completion duration. These values remain after Stop. Obtain actual phone readings before choosing a latency change.

The deterministic matcher benchmark was about 9.9 ms on the Mac in an unoptimized build. This does not explain a large delay by itself, nor prove the phone matches at that speed. The app already uses cumulative partials, so it does not intentionally wait for a final transcript. Provider progress is relative audio processed, not a word timestamp. Lens timing is SDK send completion, not observed pixels.

Do not start another paid session without checking authorization. Never treat a prior bounded single-test approval as ongoing spend. A user may choose to run another test after a clear cost/audio-transfer disclosure. Keep consent, personal feedback and provider traces private.

## Checks

- bash tools/test.sh: twenty-one core tests plus actual PCM callback probe passed.
- python3 tools/probe_muse.py: real WebSocket client processed synthetic audio-progress events, PCM, partials and clean endStream.
- Signed device build passed. Check the latest install/launch receipts for the phone state.

Device Keychain setup is complete. Do not provision the key again without evidence of a credential problem. Apple agreement, device registration, Meta AI Developer Mode and glasses component are complete.
