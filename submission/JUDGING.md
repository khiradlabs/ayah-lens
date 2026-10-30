# Ayah Lens judging evidence Draft 1

Build 28 is the demo baseline. The strongest submission shows a listener following a long recitation on real glasses without page controls. Make that behavior visible before explaining the architecture.

The submitted application names the Indie Developer track and Build for Your World theme. The public Meta event page confirms those tracks and themes. Keep this positioning unless the accepted participant profile says otherwise.

## Judging weights and proof

The weights below come from the participant guide supplied in this chat. The authenticated guide still needs a current check. The public Meta page was checked on October 29.

| Criterion | Weight | What Ayah Lens demonstrates | Evidence to show | Remaining gap |
|---|---:|---|---|---|
| Impact | 30% | Meaning stays in view while a person listens without handling a phone. The initial audience is compatible-glasses users who want English meaning alongside Arabic recitation. | Founder problem statement, real listening scene, source-labelled demographic context. | No measured comprehension improvement, adoption or representative user study. Add a genuine brief reaction only if captured. |
| Use of Meta AI Tooling | 25% | Muse Voice supplies Arabic transcripts. Spark 1.3 resolves bounded candidate choices and pairs reference-word spans for automatic bilingual portions. | Architecture, one readable paired source window, real API/client evidence and accurate cached-plan label. | The recorded demo must distinguish cached phrase plans from live inference. A selected synthetic recovery is not a general accuracy benchmark. |
| Technical Depth and Execution | 20% | Glasses-only audio route, global retrieval, within-ayah word tracking, canonical source preservation, bounded frames, cancellation and newest-frame delivery. | Original modules, event Git history, the 52-test result and short live continuous take. | No acoustic word timestamps, controlled visible-lens latency or full-Quran accuracy result. |
| Demo | 25% | Real external recitation drives verse and within-ayah changes on phone and glasses without Next. | At least 25 seconds of continuous genuine proof, with a legible phone preview and separate actual-lens label. | Final footage and an accessible three-minute video are still missing. |

Weights total 100%. Each criterion is scored by judges from 0 to 10. Weighted points are 3 × Impact + 2.5 × Meta tooling + 2 × Technical execution + 2.5 × Demo. Do not invent self-scores or a bonus for counting models.

## What earns attention

Open with the product working. Within the first eight seconds, show Arabic and English changing with the recitation. Explain the human need, then return to a continuous live take.

Show the difficult case: the verse ID stays the same while its displayed portion changes. This makes the contribution clearer than a sequence of short ayah lookups.

Explain Spark through the user benefit. It selects source-word boundaries that let English meaning travel with an Arabic passage. Local validation preserves complete coverage and compact spans. The original published text supplies the display.

Keep the full-reference claim precise: 114 surahs and 6,236 ayahs are bundled. Paired plans for the three demonstration references are cached. Other long ayahs can follow Arabic while an English plan is prepared. These are availability statements, not universal accuracy claims.

## Submission requirements

| Requirement | Current evidence | Next action |
|---|---|---|
| Meta model use and theme fit | Muse clients, real provider checks and working selected listening demonstrations. | Explain model roles and the recurring listening problem in the video. |
| Public code | Repository is public. Implementation is on feat/within-ayah-following. | Land reviewed implementation on main before giving judges the root repository URL. |
| Three-minute demo | Timed script covers exactly 180 seconds. | Capture genuine footage and assemble the final cut. |
| Accessible video and repository links | Public repository verified; no final video link exists. | Check both while signed out before submission. |
| New work identifiable | Event-dated application commits begin October 26. CONTRIBUTIONS.md distinguishes preparation and third-party materials. | Include a short new-work card and keep attribution visible in the repository. |
| Correct entrant details | Application record says Indie Developer and Build for Your World. | Check the accepted profile and list every actual contributor in the final form. |
| Deadline | Public Meta page says November 4, 9 PM Eastern. | Plan for November 4, 8 PM America/Chicago; submit earlier and recheck the platform. |

## Highest priority remaining work

1. Capture the continuous listening proof and a short legible actual-lens sample.
2. Assemble and review the three-minute video against this evidence map.
3. Merge the reviewed implementation, finish the form and check signed-out links.

A brief human reaction can strengthen Impact if readily available. Describe what the person actually experienced. Do not manufacture a testimonial or delay the core video for a broad study.

## Bonus prizes

The supplied guide names separate open-weight, creative, agentic and community awards. Omnilingual fallback alone does not establish eligibility for its Muse Glimmer or Muse Spark Open bonus. The current product does not establish the Muse Image or Muse Wonder creative-build requirement. Main-rubric evidence takes priority over new integrations. Social posting remains a separate approval step.

## Sources

- Participant guide supplied by Faraz, sections 7–9, linked at [Cerebral Valley event details](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/details). Authenticated October 29 reread remains pending.
- [Meta event page](https://dev.meta.ai/events/global-hackathon), checked October 29, for track descriptions, themes and deadline.
- [CLAIMS.md](CLAIMS.md) for the impact sources and implementation limits.
- [CONTRIBUTIONS.md](../CONTRIBUTIONS.md) and [CHECKPOINT.md](../CHECKPOINT.md) for provenance and technical evidence.
