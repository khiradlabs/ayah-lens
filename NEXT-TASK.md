# Next: validate earlier matching of distinctive openings

Status: An exact short-opening path is implemented and locally verified. Twenty-five tests, callback and synthetic WebSocket probes passed. Inspect the latest build/install receipts for phone state. Consult private action gates and build/logs/muse-latency-investigation.md for actual timing observations and authorization scope.

## First action

A screenshot supplied the expanded timing values. Do not ask for the same old metrics again. Source investigation reproduced an avoidable rule: complete unique openings shorter than eight letters did not match. The correction accepts only exact complete two-word openings with six/seven normalized letters, unique in Al-Fatihah, preserving word boundaries and dagger-alif spelling aliases. The existing fuzzy floor and ambiguity handling are unchanged.

Have the wearer test the corrected matcher only after a clear paid/audio-transfer disclosure and their choice to run. Start reciting when the listening card appears; initial silence is included in the first-text timing. Compare First match after text plus observed correctness of verse changes. Exact partials were not captured in the prior run, so do not attribute its whole evidence wait to the eight-letter rule or promise a particular time reduction. Provider first-text delay is a separate component.

## Limits and checks

- Twenty-five core tests passed, including complete short openings, incomplete words, altered word splits, duplicate/ambiguous reference prefixes, and prior regressions.
- Removing the correction reproduced four assertion failures, restoring returned green.
- bash tools/test.sh and python3 tools/probe_muse.py passed.
- No additional paid API request was started by the agent. Check private gates before any billed request.
- Keep personal observations, consent, screenshots and provider traces out of public commits.

Device Keychain and hardware setup are complete. Do not repeat provisioning or registration without new evidence. First-text time is initial-session timing, not per-ayah latency; lens timing measures SDK completion, not visible pixels.

## Latest installation identity

Version 0.1.0, Build 18 was rebuilt, installed and verified against device metadata. Automatic launch was blocked by the locked phone. The wearer can unlock/open Ayah Lens and confirm the visible Build 18 label near the top. Do not infer a new test from duplicated timing screenshots; use a fresh user-chosen run and check first-match timing. tools/device.py verify is the maintained installed-build check.

The latest labelled build is version 0.1.0, Build 18. It installed, passed device-version verification and launched successfully. Version/build also appear inside Muse timing, so new diagnostic screenshots can identify the tested artifact.
