# OpenAI narration for full video v0.6

Faraz authorized OpenAI APIs for the requested emotional narration. Preserve full video v0.5 and its exact approved script. Create a new full v0.6 review cut, at most179.900seconds, retaining the reserved masjid block60–90. No app changes, new recording, public release or Meta app reads.

## Provider and credential

Use the documented OpenAI Speech API POST https://api.openai.com/v1/audio/speech with gpt-4o-mini-tts, voice marin, response_format wav and explicit delivery instructions. The API is still available for this one-off November2026 render; its documented January2027 shutdown is irrelevant to the resulting media file. Do not build a production service dependency on it. The recommended new Realtime workflow is unnecessary for this bounded offline render. If the requested model is inaccessible, report the actual error before selecting another model.

Load OPENAI_API_KEY inside the process from /Users/farazsyed/.secrets/ayah-lens-openai.env or environment. The user reported saving the key. Never print it, place it in argv/logs, embed it in scripts or commit it. A dedicated API-key connector is unavailable. Do not use Codex authentication as an API credential.

Start with a short hook sample as a real access/quality probe. Preserve audition receipts. Generate only approved English narration, never scripture or a cloned real voice. Keep explicit provider/model/voice/text/instructions/duration/hash receipts and costs.jsonl using a maintained tools helper and required --note. No automatic network retries. Bound first-pass generation to the small narration job and at most USD1 estimated spend. Rate inputs/outputs accurately where possible; if no token usage is returned, record the estimation method instead of claiming actual invoice costs.

## Words, emotion and timing

Reuse the exact nine opening narration sentences from tools/problem-opening/timing.py and starts in timing.json. Keep the approved personal Quran translator hook verbatim. Warm curiosity for the question; clear confident benefits; crisp No scrolling / No tapping beats; a slower sincere Just listen / And understand ending. No theatrical sadness, shouting, forced accents, added words, music or sound effects. Use a consistent Marin voice throughout. Cedar was auditioned first; the complete Marin take was selected after the expressive Cedar take omitted its final phrase.

Reuse the remaining narration text from submission/video-edit.json segments3,4,6,7,8,9,10. Product now occupies38–48, uses48–60, long-ayah explanation90–112, technical112–138, Hifz138–152, foundation152–168 and close168–179.9. Start each with a small margin. Preserve words and all Meta stack names. Pronunciation instructions should guide Ayah Lens, Quran, ayah, surah, Salat, Hifz and Muse without changing caption wording.

Measure every generated clip before fitting it to its assigned window. Trim only detected edge silence, preserving phonemes. Use pitch-preserving tempo adjustment only when needed; keep changes modest. Regenerate with clearer pacing if large speed changes would flatten delivery. Fail on missing/zero audio, count mismatch, overlap, clipped words or spill into genuine recitation. Keep benefit starts aligned to existing animation cues; adjust only within clear pacing allowances if necessary and document them. Do not synthesize a whole un-timed three-minute read and hope it fits.

## Assemble and disclose

Use full v0.5 picture as the source. Remove the old English guide narration entirely in narration windows. Preserve genuine audio exactly from source intervals0–8,30–38 and60–90, including the existing reserved-slot fill. Rebuild the rest with the new narration and explicit silence, then mix without changing genuine recitation speed. Verify protected audio correspondence.

Add a small clear AI-generated English narration disclosure while English synthetic narration is present. Do not label genuine Quran recitation as generated. Update the editorial video-version badge to v0.6 within the already documented header region. Preserve actual device text, published scripture, all source labels and other visuals. Keep masjid placeholder labels honest. Update approximate captions for measured new speech windows.

Output build/video-v0.6/Ayah-Lens-Demo-v0.6.mp4 plus an audible hook sample, narration stems, full script, captions, timing/provider/cost receipts and viewing notes. Media and credentials stay ignored. Earlier exports retain hashes.

## Verification

Run meaningful tests for credential redaction, request schema, cache identity including instructions, clip-window fitting, protected-window rejection and source mapping. Actual API output must validate as positive-duration audio. Full export must have179.9seconds/5397frames/1080p30fps/48kstereo, full decode and non-clipping peaks. Check no old guide speech remains in narration windows; verify protected recitation correlation and picture correspondence outside explicit editorial badges. Check approved words against an actual generated-English-only transcription as well as text/caption provenance. Reject missing phrases, including the closing. Do not claim independent audible pronunciation or emotional quality unless actually assessed. Privately inspect disclosure/version overlays and join frames. Independent spec review must precede quality review.
