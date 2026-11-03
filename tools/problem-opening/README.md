# Problem opening v0.4

Standalone 36-second review proof. Earlier v0.3 and full v0.2.1 exports remain preserved.

From the app root:

```sh
python3 tools/test_muse_image.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_problem_opening.py --check
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_problem_opening.py --storyboard-only
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_problem_opening.py
python3 tools/problem-opening/verify_media.py
```

Local Chrome/localhost and macOS Daniel speech require local-service access. Verify positive AIFF duration; sandboxed say can exit 0 with empty audio. Dependencies remain pinned in package-lock.json.

The original Muse Image listener scene lives under ignored build/video-v0.4-opening/assets/. The maintained tools/muse_image.py helper generates one image per explicit call with required --note, disables built-in search and writes private prompt/hash/usage/cost receipts. It never retries automatically. Credentials load inside the process from the private secrets file. Official API documentation: https://dev.meta.ai/docs/image-generation. Documented price: $0.01 per returned image at https://dev.meta.ai/docs/pricing-rate-limits. Generated artwork and every source copy remain ignored, never staged.

No conceptual phone or companion-phone provenance inset appears. The listener scene carries the sound motif into the worldwide population field, then returns. A sound-line frame expands into a static genuine source-frame 0 preview from 27.2 seconds. The same source starts moving with its original audio at 28 seconds. This is an editorial transition, not a claim of optical lens filming.

Timing and actual measured sentence durations live in timing.json. The guide is temporary local Daniel narration. Captions remain approximate. Narration does not overlay either actual-recitation section. Both recitation sections reuse the exact accepted eight-second WAVs.

The genuine replay uses source frames 0–239 at original speed. Crop x208, y832, width 576, height 144 comes from the 976×1296 supplied native camera + display composite. No source words are recreated. The footage predates the current app build and does not establish Build 40 readability or overall accuracy. Source camera background remains part of the unaltered source crop. Encoded crop SSIM and actual-art patch checks are recorded privately by verify_media.py.

No Meta website assets, app changes, new capture, full-master replacement or publication.
