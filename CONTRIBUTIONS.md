# Contributions and provenance

## Event work

October 26, 2026: repository setup and project documentation only. No application code or successful physical-device test is claimed by this initial commit.

October 26, 2026: Faraz relayed organizer clarification and provided the kickoff rules slide stating new work may be built October 26 through November 4. Application implementation began after that clarification. The earlier guide's October 27 start is superseded by the kickoff clarification.

First application milestone: original native SwiftUI phone interface, manual canonical-verse display, glasses-only microphone capture, audio-first session sequencing and cleanup, and build/install tooling. Four core tests passed after observed failing tests. The first signed app installed and launched on the test iPhone. Actual Arabic readability and combined audio/display remain pending wearer confirmation at this milestone.

## Existing preparation

Before the event, local evaluation explored Tilawa, Meta Omnilingual ASR and a CoreML conversion. Dataset filtering and feasibility research also predate the event. Those inputs are preparation, not new application functionality built during the hackathon.

## Third-party components under evaluation

| Component | Role | Source |
|---|---|---|
| Meta Wearables Device Access Toolkit | Glasses connection, audio and display | https://github.com/facebook/meta-wearables-dat-ios |
| Meta Omnilingual ASR | Candidate local recognition engine | https://github.com/facebookresearch/omnilingual-asr |
| Meta Muse Voice Transcribe | Realtime hosted recognition engine | https://dev.meta.ai/docs/speech-to-text |
| Meta Muse Spark | Opt-in candidate resolver | https://dev.meta.ai/docs/models |
| Tilawa | Evaluated recognition fallback | https://github.com/yazinsai/tilawa |

Listing a component does not claim integration or change its licence. Confirm exact versions and licences before incorporating or distributing artifacts. Tilawa package code and its model assets have different licences.

October 26 recognition slice: original serial CoreML adapter, bounded microphone windows, Arabic decoding restriction, normalized Al-Fatihah fragment matching, sequence-based ambiguity handling and native live-mode UI were built during the event. Existing Meta model weights and third-party conversion are credited separately in ATTRIBUTION.md. Wearer confirmed the earlier combined hardware loop; the wearer reported most ayahs recognized in the first live test, with one or two missed. Exact accuracy remains unmeasured.

October 26 Muse client preparation: original Swift realtime transport, continuous PCM encoder, transcript reducer, canonical matcher handoff, explicit Muse/fallback controls and runtime Keychain provisioning helper. Twenty core tests and local WebSocket probe passed; live Muse speech inference remains pending paid-test approval. No Muse weights or keys are committed.

## Complete-Quran and Spark milestone, October 27

Original event work now includes full-reference preparation/validation, an inverted trigram index, contextual candidate matching, and bounded lens pagination. The reference text itself is existing attributed material.

An original Muse Spark 1.3 HTTP adapter uses strict structured output with supplied IDs or abstention. App integration limits calls, discards superseded results and looks up unchanged source text. Thirty-five core tests and local client probes passed. Real Standard Spark inference subsequently passed three synthetic cases on October 28, including one recovery after matcher abstention. Representative live benefit remains pending. No model weights are claimed as original work.

October 29: original within-ayah word-position tracking, automatic compact source portions, actor-isolated follower state, strict Spark phrase-boundary client, validated alignment cache and live glasses integration. Boundary plans for 2:102, 73:20 and 2:255 were produced through Standard Muse Spark and independently checked for source coverage and size. The app renders existing reference text, not model-authored scripture or translation.
