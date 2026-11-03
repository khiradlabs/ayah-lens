# Ayah Lens submission drafts

Script Version 3 uses a cinematic before-and-after reveal, followed by a genuine continuous demonstration. Version 2 preserves the rubric-led script. Version 1 preserves the impact-led direction. The device baseline is Build 31 after the English switch passed the wearer check.

- [JUDGING.md](JUDGING.md) maps the four weighted criteria to available proof and remaining gaps.
- [DEMO-SCRIPT.md](DEMO-SCRIPT.md) contains Version 3, with timed narration and the visual plan.
- [VERSION-3-CONCEPT.md](VERSION-3-CONCEPT.md) describes the visual reveals and optional demonstration surprise.
- [DEMO-SCRIPT-VERSION-2.md](DEMO-SCRIPT-VERSION-2.md) preserves the rubric-led script.
- [DEMO-SCRIPT-VERSION-1.md](DEMO-SCRIPT-VERSION-1.md) preserves the impact-led opening and proposed sequence.
- [DEMO-SCRIPT-INITIAL-DRAFT.md](DEMO-SCRIPT-INITIAL-DRAFT.md) preserves the earlier submission draft before these named versions.
- [CAPTURE-LIST.md](CAPTURE-LIST.md) gives the minimum footage and continuous proof requirements.
- [FORM-ANSWERS.md](FORM-ANSWERS.md) matches the supplied submission form.
- [CLAIMS.md](CLAIMS.md) records source wording and implementation limits.
- [REVIEW.md](REVIEW.md) records checks and remaining release work.
- [VIDEO-REVIEW.md](VIDEO-REVIEW.md) describes editorial demo video v0.2, based on script Version 3, and its reserved masjid slot.

The maintained timing source is demo-timeline.json. Regenerate the script with python3 tools/render_demo_script.py, then run python3 tools/check_submission.py.

Video v0.2 rebuilds the local review cut with warm-paper motion graphics, a one-in-four population comparison, original 3D hardware geometry and an animated causal diagram. Temporary local guide narration and the single reserved masjid slot remain. It is not the final submission video. The public repository default branch still needs the reviewed implementation. Personal opinion ratings and final submission remain with the entrant.

Version 3 includes a proposed listener-choice scene and an opening passage requiring a physical check. The Arabic-only switch is implemented and wearer-verified in Build 31. A working-build narration alternative is included.

The [implementation draft review](https://github.com/khiradlabs/ayah-lens/pull/1) targets main and remains unmerged.

The installed app remains version 0.3.0 Build 40. Source footage predates its typography changes. Video v0.1 remains unchanged under build/video-v0.1/. The v0.2 master and private review receipts live under build/video-v0.2/. See [VIDEO-V0.2-SPEC.md](VIDEO-V0.2-SPEC.md), [EDITORIAL-DESIGN.md](EDITORIAL-DESIGN.md) and [GLASSES-3D.md](GLASSES-3D.md).

Video v0.2 was rendered and independently passed sampled visual review for user review. Technical checks verified 179.900 seconds of full picture, 5,397 frames, stereo 48 kHz audio and zero clipped samples. Local guide narration, approximate original 3D geometry and the reserved masjid replacement remain disclosed.


The v0.2.1 opening-order revision is rendering for review under build/video-v0.2.1/. It plays Just listen at 0:00–0:08, population scale at 0:08–0:28, then Now follow the meaning at 0:28–0:36. The product reveal still begins at 0:36. Every later boundary remains unchanged. The accepted v0.2 master is preserved. This revision reuses its narration and source audio without changing the words or speed. Run python3 tools/test_video_opening_order.py to check order, semantic content, native overlays and audio association.
