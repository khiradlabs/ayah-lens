# Next Ayah Lens task

Read SPEC.md and the latest CHECKPOINT.md entry. Version 0.2.0, Build 21 is installed and launched. The runtime key is already in device-only Keychain. Do not repeat provisioning or hardware setup without evidence of a new failure.

## Immediate validation

1. Test Build 21 on the wearer with Muse Spark enabled. Observe phone transcript, candidate decision status and physical lens across selected passages. Check repeats, passage changes and long-page navigation.
2. A bounded Muse validation was authorized on October 28; consult the private gate rather than asking for the same spending approval again.
3. Check an external reciter source with permission.
4. Build scoring evidence and the three-minute video around verified behavior and clear model roles.

Standard Muse Spark provider validation passed three synthetic cases using the actual adapter. The matcher abstained on all three; Spark recovered noisy 1:6 in 3.28 seconds and correctly abstained twice. One shared-opening case bypassed the app's suppression as an adapter control. This is a selected diagnostic, not a representative accuracy benchmark. See ignored build/spark-evaluation/live.json.

## Current implementation

All 114 surahs and 6,236 aligned ayahs are bundled. Global retrieval runs outside the UI actor. Muse Voice supplies realtime transcripts. Spark is opt-in, supplies only a retrieved ID or abstention, and permits at most three calls per run. Long ayahs use manual bounded pages. Source availability is not all-ayah recognition validation.

Thirty-five core tests, callback regression, synthetic WebSocket/HTTP probes and a global-query host probe passed. Signed installation and device version verification passed. Physical tests for this new whole-Quran build remain pending. Keep paid-test consent, real audio and wearer-specific observations out of public commits.
