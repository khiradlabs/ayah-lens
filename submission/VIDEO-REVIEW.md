# Ayah Lens full demo video v0.6

The current review master is build/video-v0.6/Ayah-Lens-Demo-v0.6.mp4. It replaces the local guide with OpenAI-generated English narration using gpt-4o-mini-tts and built-in Marin. Full v0.5 remains preserved.

## Narration and disclosure

The approved words are unchanged. The expressive hook reuses one coherent generated performance, sliced at verified phrase timestamps and fitted to the existing animation cues. Remaining sections use consistent Marin narration with warmer delivery directions. The AI-generated English narration disclosure appears during synthetic-English ranges. It shares the original version header at x1420, y30, width460, height48. Recorded-source labels below it remain unobstructed. Genuine Quran recitation is neither generated nor labelled synthetic.

The generation pipeline caught a real omission of short final clauses. Two raw paragraph generations omitted Hands free and Nobody is turning a page. Their separately generated same-voice endings were appended with a short natural gap. The final fitted-English-only transcript matches all260 normalized approved words. Proper-name spelling normalization is documented. Human pronunciation and emotional approval remain unverified. OpenAI audio-model analysis assessed the actual final English-only waveform. It found a clear consistent voice, natural transitions, complete clauses and no material defects. Emotion was restrained rather than dramatic.

Genuine audio at0–8,30–38 and60–90 retains its source timing and speed. Old English guide audio is removed from narration ranges. The video remains179.900seconds, with the same scenes and the reserved masjid fill at1:00–1:30. The masjid slot is still a labelled placeholder/reference fill, not completed masjid proof.

## Reproduction and evidence

Use python3 tools/test_openai_narration.py and python3 tools/openai_narration.py --check. Generation and rebuilding use --prepare --render --note, with the private key loaded inside the process. The input script and overrides are in submission/narration-v0.6.json. No credential or media file is tracked. An instruction-aware cache prevents unintended repeat charges.

Provider, model, voice, actual waveform hashes, phrase sources, timings and cost estimates are recorded privately under build/video-v0.6/. Speech WAV streaming headers are normalized using actual PCM bytes, not advertised placeholder lengths. Estimates include unused auditions, narration takes, transcription and audio-model QA; they are not invoice actuals. One raw-audit request timed out and its billing status remains unknown, with a conservative reserve recorded. There were no automatic network retries.

The old master, source recordings and app remain unchanged. No new capture, official Meta website asset or publication occurred. The Speech API is used only for this one-off media generation before its documented shutdown date.

## Preserved full v0.5 history


Faraz approved the v0.5 opening and its integration into the full video. The current review master is build/video-v0.5/Ayah-Lens-Demo-v0.5.mp4. Video numbering is separate from installed app 0.3.0 Build 40.

## Current assembly

The accepted opening plays at 0:00–0:38. Its exact personal Quran translator hook and timed benefits remain intact. Original Muse Image artwork is reused, with no new generation spend. The genuine recorded source replay stays at its original speed.

The editorial product and Meta stack scene is retimed from twelve seconds to ten seconds, placing it at 0:38–0:48. The existing temporary narration uses pitch-preserving tempo. No words or Meta stack names are cut. This scene is an original approximate 3D illustration, not genuine listening proof.

Every original scene from 0:48 onward keeps its original absolute time and speed. The only visual replacement is the editorial video-version badge at x1420, y30, width 460, height 48, enabled from 38 seconds. It now reads VIDEO v0.5 / GUIDE VOICE. Source comparisons mask exactly that rectangle in both frames and compare all other regions. Genuine device text is outside the rectangle.

The output target is 179.900 seconds, 5,397 frames, 1920×1080 at 30fps with 48kHz stereo. The accepted opening and earlier full master remain unchanged.

## Reserved masjid recording and remaining work

The single 30-second replacement slot stays exactly at 1:00–1:30. Its six-second placeholder and 24-second phone reference remain labelled throughout. This fill is not completed continuous masjid proof. Narration remains the temporary local macOS Daniel voice. Captions are approximate. This is a private review artifact, not a public release.

The prayer disclaimer remains visible. The 73:20 sequence preserves source text, crop, masking and playback speed. Hifz uses a labelled reference-mode graphic. Teaching remains future work requiring development and extensive testing. Existing footage predates Build 40 and does not establish its larger text readability.

## Reproduction and evidence

Run python3 tools/test_full_demo_assembly.py, then python3 tools/assemble_full_demo.py. The separate submission/full-video-v0.5.json manifest identifies accepted input hashes and source/output mappings. It does not change the older renderer's plan.

Run python3 tools/assemble_full_demo.py --check for fresh read-only verification. It checks input hashes, full decode, picture/audio duration, frame count, peak level, captions and numerical source correspondence. Product speech is compared against the same pitch-preserving reference tempo, including its final words. The maintained helper uses a Pillow badge PNG because this FFmpeg build lacks drawtext.

Private captions, viewing notes, assembly manifest, technical receipts and encoded join samples live under build/video-v0.5/. Independent reviews are recorded under its qa/ directory. Technical comparisons and sampled visual inspection do not establish uninterrupted human playback, pronunciation quality, physical glasses readability or recognition accuracy.

## Historical export evidence

The following sections describe preserved earlier exports, not the current assembly.

## v0.2 verification and remaining review

The rendered v0.2 master passed technical checks and independent sampled visual review for user review. It contains 5,397 full-HD frames at 30 fps and runs 179.900 seconds with stereo 48 kHz audio. Complete decoding passed. Audio peaked at −2.977 dBFS with zero clipped samples. The final picture was extracted at 177 and 179 seconds.

The independent reviewer inspected all 31 supplied full-HD samples, decoded seven master excerpts at two-second intervals and checked exact 60-, 66- and 90-second boundaries. This was sampled decoded-motion review, not uninterrupted playback or an every-frame visual audit. The private report is build/video-v0.2/qa/master-visual-review.txt. Technical and visual receipts are beside the master. The original v0.1 master remained byte-identical. Human review remains necessary for guide pronunciation, pacing and recitation synchronization. Existing footage predates Build 40 and does not establish its larger font’s readability. No app, audio-buffer, new capture or publication work is included.


## v0.2.1 opening-order revision

The v0.2.1 master passed full technical and independent source-quality checks. Independent sampled visual review passed. It covered the 33-frame master contact sheet, full-HD opening boundaries and 18 decoded opening-preview samples. It did not assess perceived audio or uninterrupted playback. The revised master target is build/video-v0.2.1/Ayah-Lens-Demo-v0.2.1.mp4. The accepted v0.2 master remains unchanged.

The opening order is Just listen at 0:00–0:08, the population and understanding gap at 0:08–0:28, then Now follow the meaning at 0:28–0:36. Narration, scene durations, source text, crops, masking and playback speed remain the same. The product reveal remains at 0:36–0:48. The reserved masjid slot remains exactly 1:00–1:30.

Each moved scene retains its visual identity, native overlays and audio. Footer chapters follow the physical order. The badge reads v0.2.1. The existing 3D illustration and every scene after the opening retain their approved content.

Reproduce with python3 tools/render_demo_video.py --reuse-audio-from build/video-v0.2/audio after copying the accepted assets/glasses-turntable.mp4, assets/within-card-clean.mp4 and assets/card-mask.json into build/video-v0.2.1/assets/. The reused WAVs are copied by original scene identity. They preserve the accepted local narration and source recitation. Run python3 tools/test_video_opening_order.py and python3 tools/editorial_motion.py --check for the semantic regression checks.


Technical verification decoded the complete master without errors. Picture and audio cover 179.900 seconds. The export has 5,397 frames at 1920×1080 and 30 fps, with stereo 48 kHz audio. Exact picture transitions at 0:08, 0:28 and 0:36 passed. The peak was −2.978 dBFS with zero clipped samples. All 11 WAVs, the accepted 3D clip and the masked phone asset remained byte-identical. The encoded 0:28–0:36 source recitation matched the old 0:08–0:16 replay with correlation 0.99994. The accepted v0.2 master retained its original SHA-256. The 33-frame contact sheet, technical receipt and 36-second opening preview live beside the new master. Independent source-quality review found no material findings.
