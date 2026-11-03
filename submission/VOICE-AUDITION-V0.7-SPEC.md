# Conversational voice auditions v0.7

Faraz preferred the13.8-second Realtime Cedar sample and requested more natural, conversational parameter tuning. Preserve its voice, model and40-word script. Compare two continuous takes: A uses relaxed delivery around155 words per minute; B uses more engaged delivery around175. These are requested delivery targets, not guaranteed measured rates. Both keep output speed at1.0 because the API speed setting changes playback rather than spoken composition.

Generate only these two short English samples. No automatic retry, microphone input, voice cloning, source recitation upload, full video replacement or release. Reuse the private credential without exposing it. Log request settings, returned token usage and cost estimates with a note. Preserve all earlier samples.

Verify exact normalized words against a separate waveform transcription and decode each complete WAV. Reject missing words. Human feedback chooses the performance; automated checks cannot establish naturalness.

Maintained runner: tools/realtime_narration.cjs. Private take manifests and receipts: build/video-v0.7-study/realtime-audition/. --dry-run validates settings without loading credentials or making a request. Existing output prevents another charge.

Official guidance: https://developers.openai.com/api/docs/guides/voice-prompting and https://developers.openai.com/api/reference/resources/realtime/client-events.

## Verification receipt

Both requested calls completed. Independent waveform transcription matched40 of40 words in each, and full WAV decoding passed. A is12.55seconds; B is13.65seconds. Targets155 and175 words per minute were directions rather than achieved measurements. Actual complete-take rates are approximately191 and176 words per minute. Existing-output checks rejected another generation before credential access. Naturalness remains a human judgment.

## Follow-up blended take

Faraz preferred A naturalness and B impact. One additional same-script C take targets conversational flow with selective energy on the opening and reveal. C is13.25seconds; independent waveform transcription matched40 of40 words and full decode passed. Human review remains pending. Private C manifest, usage, cost and verification are adjacent to the WAV. No full video changed.
