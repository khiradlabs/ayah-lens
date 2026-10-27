# Next: validate live Al-Fatihah recognition on the glasses

Status: Partial live pass. The wearer identified Ar-Rahman ir-Rahim as a likely miss. A bounded matcher transition correction passed fifteen tests and a signed build. Physical retest is pending.

## First action

Read CHECKPOINT.md. Retest Al-Fatihah at the wearer’s normal pace, especially the transition from Alhamdu lillahi rabbil alamin through Ar-Rahman ir-Rahim to Maliki yawmid-din. Confirm whether 1:3 appears. If it still misses, capture the phone transcript during that window before another change. Do not assume that the reproduced matcher case proves the exact cause of the original live miss.

Do not infer accuracy from the synthetic model probe or manually selected lens output. If there is a failure, capture the exact error, transcript or new crash report before changing code. Keep new phone observations and local evidence private unless explicitly cleared.

## Acceptance

- Actual glasses audio changes the matched ayah and its unchanged Arabic/Pickthall text without manual next-verse taps.
- Pauses and uncertain fragments hold the current verse; distinct repeats can return to an earlier ayah.
- Record initial text latency, wrong locks and misses from a short passage. Inference duration on screen excludes five seconds of collection.
- Stop/restart and an external reciter need explicit physical checks; they have not been established by this recognition build.

The current listener is local Meta Omnilingual ASR. Hosted Voice Transcribe comparison, a useful Spark contribution, evaluation and video remain later work. No paid inference or external audio upload is authorized by the hardware confirmation.

Apple agreement acceptance, device registration, Meta AI Developer Mode and glasses developer component are complete. Do not ask again. Use tools/device.py launch with the selected AYAH_DEVICE_ID when asked to reopen; the phone must be unlocked.
