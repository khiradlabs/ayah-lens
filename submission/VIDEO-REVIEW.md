# Ayah Lens demo video v0.2

Video v0.2 rebuilds approved script Version 3 with warm-paper editorial motion. The video version is separate from installed app 0.3.0 Build 40.

The review cut retains genuine native glasses and phone-preview footage. Its narrator is the temporary local macOS Daniel voice. It is a private review artifact.

## Reserved masjid recording

The single 30-second replacement slot stays exactly at 1:00–1:30. Its six-second placeholder and 24-second phone reference remain labelled throughout. This fill is not completed continuous masjid proof.

## Editorial sequence

The population graphic builds 100 marks, highlights 25 and regroups them into four equal groups. It states about 2 billion Muslims and about one quarter of the world’s population. The caption identifies Pew’s 2020 estimate, published 2025, with underlying share 25.6%. This is no comprehension statistic.

The product scene uses original 3D geometry approximating the black Meta Ray-Ban Display. It is labelled 3D illustration. The lenses contain no invented output. The geometry is an editorial approximation, not official manufacturer CAD.

The technical diagram advances glasses audio through Muse Voice transcription, local matching and portion tracking, published source and lens output. Spark branches conditionally for bounded ambiguity and validated cached paired-source plans. It does not author the displayed translation.

The opening replays the same recorded audio with its genuine display content. The enlargement comes from the same native frames. The 73:20 sequence preserves source text, crop, mask and playback speed. Hifz uses a labelled reference-mode graphic, since the supplied footage does not show the actual toggle. Teaching remains future work requiring development and extensive testing. The prayer disclaimer remains visible.

## Local artifacts and reproduction

The master is build/video-v0.2/Ayah-Lens-Demo-v0.2.mp4. Approximate guide captions, viewing notes, technical receipt and private QA samples live beside it. The previous v0.1 master remains unchanged.

Run python3 tools/render_demo_video.py to render motion bases and assemble the review cut. Run with --assemble-only to use existing motion bases. Run with --storyboard-only for the full assembled storyboard, including an actual 3D frame. Run with --audio-only to prepare guide and source audio. Speech generation requires access to the local macOS speech service; positive audio duration must be verified. No paid or cloud narration is required.

Run python3 tools/check_submission.py --video build/video-v0.2/Ayah-Lens-Demo-v0.2.mp4 for timeline, document and picture/audio checks. Independent visual review covers the assembled storyboard and master in motion. Technical checks cover 1920×1080/30fps, 179–180 seconds, at least 5,397 picture frames, stereo 48 kHz audio, late picture and numerical audio level.

## v0.2 verification and remaining review

The rendered v0.2 master passed technical checks and independent sampled visual review for user review. It contains 5,397 full-HD frames at 30 fps and runs 179.900 seconds with stereo 48 kHz audio. Complete decoding passed. Audio peaked at −2.977 dBFS with zero clipped samples. The final picture was extracted at 177 and 179 seconds.

The independent reviewer inspected all 31 supplied full-HD samples, decoded seven master excerpts at two-second intervals and checked exact 60-, 66- and 90-second boundaries. This was sampled decoded-motion review, not uninterrupted playback or an every-frame visual audit. The private report is build/video-v0.2/qa/master-visual-review.txt. Technical and visual receipts are beside the master. The original v0.1 master remained byte-identical. Human review remains necessary for guide pronunciation, pacing and recitation synchronization. Existing footage predates Build 40 and does not establish its larger font’s readability. No app, audio-buffer, new capture or publication work is included.


## v0.2.1 opening-order revision

The v0.2.1 master was rendered. Full technical and independent visual review are pending. The revised master target is build/video-v0.2.1/Ayah-Lens-Demo-v0.2.1.mp4. The accepted v0.2 master remains unchanged.

The opening order is Just listen at 0:00–0:08, the population and understanding gap at 0:08–0:28, then Now follow the meaning at 0:28–0:36. Narration, scene durations, source text, crops, masking and playback speed remain the same. The product reveal remains at 0:36–0:48. The reserved masjid slot remains exactly 1:00–1:30.

Each moved scene retains its visual identity, native overlays and audio. Footer chapters follow the physical order. The badge reads v0.2.1. The existing 3D illustration and every scene after the opening retain their approved content.

Reproduce with python3 tools/render_demo_video.py --reuse-audio-from build/video-v0.2/audio after copying the accepted assets/glasses-turntable.mp4, assets/within-card-clean.mp4 and assets/card-mask.json into build/video-v0.2.1/assets/. The reused WAVs are copied by original scene identity. They preserve the accepted local narration and source recitation. Run python3 tools/test_video_opening_order.py and python3 tools/editorial_motion.py --check for the semantic regression checks.
