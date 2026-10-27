# Resume October 27: approve and run the first real Muse test

Status: Faraz resumed October 27. The registered iPhone is available; the pending paid/audio-upload approval has been presented again. The saved private Meta key passed read-only authentication/catalog lookup. The native Muse client is implemented and installed, and its private key is now provisioned to the phone. The agent has not initiated paid inference or audio upload. Twenty core tests, callback regression, local synthetic WebSocket integration probe and signed build/install passed.

## First action

Read CHECKPOINT.md and SPEC.md. Obtain the pending spending/audio-upload approval for one Muse Voice Transcribe test of up to two minutes using Faraz’s own recitation, costing at most $0.01 at the published rate. Supplying the API key did not itself approve spending. No blocked status is warranted; the implementation and local checks are complete.

After approval: run tools/provision_muse_key.py with the approved AYAH_DEVICE_ID. This copies a temporary 0600 handoff, restarts the app, and leaves API sessions stopped. The app imports the key into device-only Keychain and deletes the phone plaintext handoff. Keep the key value out of chat, arguments, logs and Git. If restart fails because the phone is locked, ask for unlock or have the wearer open the app manually. Verify handoff deletion or the enabled Muse control before claiming credential import.

Ask the wearer to tap Start Muse live Al-Fatihah and recite at normal pace. Confirm the phone and lens explicitly say Muse Voice Transcribe. Observe automatic verse changes, especially 1:3. Record misses, wrong locks and initial-text latency. The stream is capped at two minutes; Stop ends input and cleans up. Silence must still be streamed in Muse mode.

## Limits

The local WebSocket server emits synthetic Quran fragments. Its pass is not live Muse proof. The model catalog proves key access only; credits and speech billing behavior remain unverified. Spark is not integrated and needs a separate useful evaluated role. Local Omnilingual remains an explicit fallback with a prior partial physical pass; its last 1:3 correction also awaits physical confirmation.

## Repeatable checks

- bash tools/test.sh
- python3 tools/probe_muse.py
- python3 tools/provision_muse_key.py --dry-run
- AYAH_DEVICE_ID=<selected-phone> bash tools/build.sh signed

Apple agreement, device registration, Meta AI Developer Mode and glasses developer component are complete. Do not ask again.

## Current phone state

October 27: tools/provision_muse_key.py completed, Ayah Lens restarted, and temporary key handoff deletion was verified. Do not provision again without reason. The wearer was given a cost/audio-transfer disclosure and can choose Start Muse live Al-Fatihah to perform the test, then Stop and report the result. The agent must not initiate a billed provider request without the separate approval.
