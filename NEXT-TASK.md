# Next Ayah Lens task

Version 0.3.0 Build 26 is the automatic within-ayah artifact. Read SPEC.md and the latest CHECKPOINT entry. The runtime key is already in device-only Keychain; no provisioning repeat is needed.

## Immediate physical check

Test long-ayah listening with 2:102 or 73:20. Confirm the displayed Arabic and English portions follow the recitation inside the same ayah, fit the actual lens, and require no Next button. Check a pause and a repeated phrase. These plans are bundled, so this test does not need a new phrase-alignment API call.

Build 23's basic phone-and-lens advancement passed. The new compact layout and within-ayah behavior still need physical validation. Consult private gates and receipts before asking for the same setup or spending approval again.

## Current implementation

Full reference: 114 surahs, 6,236 aligned rows. Muse Voice supplies realtime transcripts. Global retrieval identifies the passage; the actor-isolated follower locates source-word position and changes compact portions within it. Spark supplies bounded candidate decisions and validated Arabic/Pickthall boundary plans. Automatic Arabic works across the full corpus. Accepted paired plans are cached; uncached alignment is bounded to three new verses per run. Full translation stays on the phone until a valid paired plan is available.

Forty-eight core tests, actual callback probe, 52 supported portion transitions through global lookup/actor and the Swift WebSocket probe passed. The bundled 2:102 and 73:20 plans have 20 paired portions each; 2:255 has 14, with its shared opening left unresolved until distinguishing evidence. Preserve canonical text, no invented translation or acoustic timing claims.

## After the physical check

Resolve concrete clipping/matching defects if observed. Collect a small accuracy/latency evaluation, then scoring evidence and the three-minute video. Keep actual wearer observations, consent, credentials, audio and private diagnostic receipts out of public commits.
