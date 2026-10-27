# Next: locate Muse recognition-to-display delay

Status: Timing diagnostics are implemented and verified locally. Check private action gates and build/logs/muse-test-approval.json for the current physical validation result and remaining authorization scope. Do not rely on historical pending-approval text in older checkpoint sections.

## First action

Consult build/logs/muse-latency-investigation.md and private gates for the latest physical observations. The question about phone versus lens delay was answered; do not ask it again. The original snapshot fields do not establish first-transcript or end-to-end latency.

The expanded Muse timing disclosure adds First text after audio start, First match after text, and Peak audio gap. Obtain these values from a user-authorized run. Ask the wearer to begin reciting as soon as the listening card appears; initial silence is included in the first-text metric. The values remain after Stop. Avoid changing ASR/matching behavior before locating the delay.

Provider audio progress is not a word timestamp, and SDK send completion is not observed pixels. A low final gap can hide an earlier backlog; use the peak too. The first-text metric is an initial-session measurement, not per-ayah latency. No transcript or audio is persisted by the trace.

Do not initiate another paid session without checking authorization. Keep personal feedback, consent and actual provider traces private. Existing credentials and hardware setup are complete.

## Checks

- bash tools/test.sh: twenty-three core tests plus actual PCM callback probe passed.
- python3 tools/probe_muse.py: real WebSocket client processed synthetic audio-progress events, PCM, partials and clean endStream.
- Signed device build passed. Check the latest install/launch receipts for the phone state.

Device Keychain setup is complete. Do not provision the key again without evidence of a credential problem. Apple agreement, device registration, Meta AI Developer Mode and glasses component are complete.
