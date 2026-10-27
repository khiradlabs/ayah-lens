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
| Meta Muse Voice Transcribe | Candidate hosted recognition engine | https://dev.meta.ai/docs/speech-to-text |
| Meta Muse Spark | Candidate reasoning component | https://dev.meta.ai/docs/models |
| Tilawa | Evaluated recognition fallback | https://github.com/yazinsai/tilawa |

Listing a component does not claim integration or change its licence. Confirm exact versions and licences before incorporating or distributing artifacts. Tilawa package code and its model assets have different licences.
