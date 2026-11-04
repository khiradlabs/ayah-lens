# Ayah Lens presentation claims and sources

Use the wording below in the video and submission. Keep the date and scope attached to each number.

## Impact claims

| Claim | Supported wording | Source and boundary |
|---|---|---|
| Global context | About two billion Muslims, roughly a quarter of humanity. | Pew's 2020 estimate, published June 2025: 2.0 billion and 25.6%. Show the estimate year on screen. This is population context, not product demand or adoption. |
| Recurring practice | Islam prescribes five daily prayers. | Islamic Relief's prayer guide. This does not claim every Muslim observes every prayer or would use glasses. |
| Audible recitation | Three daily congregational prayers include passages recited aloud. | Darul Ifta Deoband describes Fajr and the first two rakahs of Maghrib and Isha. Keep the congregational context. |
| Intended user | Listeners who want help following English meaning alongside Arabic recitation. | Product target. Do not assign a global percentage to Arabic comprehension. |
| User benefit | Follow supported recitation portions without pressing Next. | Implemented behavior confirmed in selected physical testing. Comprehension gains and broader usefulness remain unmeasured. |

Sources:

- [Pew Research Center, June 10, 2025](https://www.pewresearch.org/short-reads/2025/06/10/islam-was-the-worlds-fastest-growing-religion-from-2010-to-2020/).
- [Islamic Relief UK prayer guide](https://www.islamic-relief.org.uk/resources/knowledge-base/five-pillars-of-islam/salah/how-to-pray-salah/).
- [Darul Ifta Deoband on congregational recitation](https://darulifta-deoband.com/home/en/Salah-Prayer/50381).

## Implementation claims

| Claim | Proof | Limit to retain |
|---|---|---|
| Muse Voice Transcribe supplies live Arabic | MuseProtocol.swift, MuseVoiceClient.swift and selected physical tests. | Audio is sent to Meta. This is not local-only recognition. |
| Muse Spark resolves candidate decisions | MuseSpark.swift and three provider diagnostic cases. | One selected noisy recovery and two abstentions do not establish a general accuracy gain. |
| Spark pairs Arabic and Pickthall source spans | MusePhraseAlignment.swift, source-boundary plans and validation. | Paired demonstration plans are cached. Boundary validation does not certify semantic equivalence as expert-reviewed. |
| Display text comes from attributed sources | Original Tanzil Arabic, Pickthall English, strict source slicing and attribution notices. | Do not call displayed translations newly generated or claim a religious interpretation service. |
| Full reference contains 114 surahs and 6,236 ayahs | Corpus and alignment tests. | This is reference coverage, not verified recognition of every ayah. |
| Within-ayah following works in selected tests | LivePortionFollower, integration replay and physical confirmation. | No claim of perfect reciter, noise, dialect or passage coverage. |
| 52 automated tests passed | Build 28 verification receipts and source tests. | Automated tests are not 52 users or a field accuracy study. |
| Display delivery avoids waiting-frame buildup | LatestLensSender and controlled async tests. | SDK send completion does not establish the instant pixels became visible. |
| Implementation was built during the event | Event Git history and CONTRIBUTIONS.md. | Models, SDKs, reference texts, research and prior preparation are existing inputs. |

Official model references:

- [Meta models](https://dev.meta.ai/docs/models).
- [Muse speech to text](https://dev.meta.ai/docs/speech-to-text), including partials and the lack of word-level timestamps.
- [Meta structured output](https://dev.meta.ai/docs/structured-output).

## Wording to leave out

Avoid global Arabic-comprehension percentages, all-day operation, production readiness, a perfect accuracy percentage, acoustic word synchronization and a measured comprehension improvement. None is established by this prototype.

Use the population estimate for scale. Keep the initial hardware and English-language audience concrete. Do not multiply population by daily prayers to present an adoption or usage forecast.

## Evidence status

Working selected behavior and source preservation have evidence. Final video footage, a public video URL and a signed-out submission-link check remain outstanding. Source checking covered the public Meta page, supplied form screenshots and authenticated participant guide on October 29. The live guide confirms the rubric weights, public repository requirement, three-minute video and November 4 deadline.
