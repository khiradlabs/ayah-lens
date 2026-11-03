# Problem opening v0.3

A standalone36-second review proof. It does not modify the full master or app.

Run from the app root:

```sh
cd /Users/farazsyed/data/khirad/apps/ayah-lens
npm ci --prefix tools/problem-opening --ignore-scripts --no-audit --no-fund
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_problem_opening.py --check
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_problem_opening.py --storyboard-only
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_problem_opening.py
```

The wrapper resolves paths from its own location. Local Chrome and a localhost server need sandbox access. macOS Daniel speech needs local speech-service access. Verify positive AIFF duration; a sandboxed `say` can return an empty file with exit0.

Outputs, source copies and local guide audio stay in ignored `build/video-v0.3-opening/` and ignored `tools/problem-opening/public/`. Never stage those directories. No remote media or paid service is required. The free Remotion license applies to this solo company; recheck eligibility for a larger team.

`timing.json` owns scene boundaries and narration placements. The Python timing checks cover editorial order and exact first-eight-second source selection. Layout is verified using rendered storyboards and motion, rather than unit tests that copy graphics.

The guide words match the current opening brief. macOS Daniel produces sentence clips, slightly accelerated1.03× to fit the20-second narration phase. `approximate-captions.srt` is approximate, not word-aligned. Narration never overlays the two genuine-recitation intervals.

The replay uses first source frames at original speed in both native camera/display composite and enlarged crop. Crop bounds come from `submission/video-edit.json` and are208,832,576,144. No Arabic or English source words are recreated. The native source footage predates the current app build.

Primary implementation references:

- [Remotion renderer](https://www.remotion.dev/docs/renderer/render-media)
- [Remotion CLI](https://www.remotion.dev/docs/cli/render)
- [License](https://www.remotion.dev/docs/license/pricing)

Review proof only. No publication, Meta website assets, new recording, model calls or app changes.
