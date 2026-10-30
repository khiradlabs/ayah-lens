# Next Ayah Lens task

Version 0.3.0 Build 28 is the automatic within-ayah artifact. Read SPEC.md and the latest CHECKPOINT entry. The runtime key is already in device-only Keychain; no provisioning repeat is needed.

## Immediate priority: scoring evidence and presentation

Build 28 was confirmed working after the context-window and display-sender refinements. Freeze it as the core demo candidate. Additional testing should address specific failures or missing demo evidence. Do not repeat basic setup, provisioning or general live-loop tests.

1. Verify the current official judging criteria and submission requirements; map each to a real product behavior and evidence. Do not invent scoring weights or model-count bonuses.
2. Draft the short demo story: user problem, real glasses/external-reciter demonstration, within-ayah Arabic/Pickthall following, meaningful Muse Voice and Spark roles, impact and prototype limits. Source any demographic/need claims.
3. Prepare a capture list for genuine phone preview and physical glasses output. Obtain suitable live footage using permitted audio. Distinguish actual lens footage from any explanatory overlay.
4. Assemble the video and submission materials; make the public repository entry clear and reproducible. Fix concrete demonstration blockers only.

The user confirmation does not establish controlled word-to-lens latency, no clipping across all content, or all-Quran recognition accuracy. Keep those limits in claims and documentation.

## Current implementation

Full reference: 114 surahs, 6,236 aligned rows. Muse Voice supplies realtime transcripts. Global retrieval identifies the passage; the actor-isolated follower locates source-word position and changes compact portions within it. Spark supplies bounded candidate decisions and validated Arabic/Pickthall boundary plans. Automatic Arabic works across the full corpus. Accepted paired plans are cached; uncached alignment is bounded to three new verses per run. Full translation stays on the phone until a valid paired plan is available.

Fifty-two core tests, actual callback probe, 52 supported portion transitions through global lookup/actor and the Swift WebSocket probe passed. The bundled 2:102 and 73:20 plans have 20 paired portions each; 2:255 has 14, with its shared opening left unresolved until distinguishing evidence. Preserve canonical text, no invented translation or acoustic timing claims.

## Verification baseline

Current artifact: version 0.3.0 Build 28. Fifty-two tests, callback probe and selected global/follower integration transitions passed. Wearer confirmation closes the immediate core-loop check. Private receipts and observations remain under ignored build/logs and private action gates.
