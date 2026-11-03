# Problem opening v0.5

Standalone 38-second review proof with the approved personal Quran translator hook and animated benefits. Earlier v0.4, v0.3 and full v0.2.1 exports are preserved.

From the app root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/problem-opening/test_timing.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_problem_opening.py --check
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_problem_opening.py --storyboard-only
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_problem_opening.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/problem-opening/verify_media.py
```

Local Chrome and macOS Daniel speech require local-service access. Verify positive AIFF durations. Sandboxed say can exit zero with empty audio. Dependencies remain pinned in package-lock.json.

## Timing and benefits

The first eight seconds use genuine recitation. The shortened setup explains the language gap and sourced population context. Nine measured spoken beats run from 8.100 to 29.257 seconds. The voice setting is 165 words per minute with 1.03 tempo and 130ms gaps. The 36-second target had insufficient room for the exact approved hook and pauses; the proof therefore uses the permitted two-second extension.

The personal Quran translator question starts at 15.491 seconds. Meaning in view starts at 19.084, automatic following at 21.739, no scrolling at 24.786, no tapping at 25.877, just listen at 26.957 and understand at 28.104. A genuine static source preview fills the expanding sound frame from 29.2 seconds. The same source starts moving with its matching audio at 30 seconds and continues for eight seconds. Benefits describe automatic following once listening has started, rather than hands-free app launch.

Timing and actual measured sentence durations live in timing.json. Sentence count, starts and durations must match. The renderer handles all nine spoken beats without hard-coded five-sentence loops. The guide remains temporary local Daniel narration. Captions are approximate. No narration overlays either genuine recitation section.

## Artwork and source

The original Muse Image listener scene is reused from ignored build/video-v0.4-opening/assets/. Its original receipt remains unchanged. A reuse receipt under the new output identifies that source and records new generation cost as zero. The original generation cost was estimated at $0.01; no new API request occurred for v0.5. Media stays ignored.

The genuine replay uses source frames 0–239 at original speed. Crop x208, y832, width 576, height 144 comes from the supplied 976×1296 native camera + display composite. No source words are recreated. The footage predates the current app build and does not establish Build40 readability or overall accuracy. The camera background remains part of the unaltered source crop and is clearly identified. Encoded crop correspondence and actual-art checks are recorded privately by verify_media.py.

No conceptual phone, companion-phone inset, official Meta website asset, app change, new capture, full-master replacement or publication.
