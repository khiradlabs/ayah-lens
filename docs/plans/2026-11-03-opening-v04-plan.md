# Opening v0.4 execution plan

Base commit 37affd5. User requested this revision; routine implementation and bounded Muse calls are authorized. Existing master and media stay untouched.

One implementation task owns tools/muse_image.py, tools/test_muse_image.py, tools/problem-opening/*, tools/render_problem_opening.py and necessary submission opening documentation. Implement bounded Muse Image generation with required --note and private costs.jsonl, validation, secret-safe receipts, no auto-retry. Generate original text-free supporting artwork only after the controller's cold story critique passes. Remove conceptual phone scene and provenance phone inset. Implement listener and sound-frame transition into genuine source crop with exact same recitation replay. Preserve v0.3 outputs; render to new v0.4 path. Update cache/timing/captions to measured real narration. Use appropriate focused tests first for meaningful parsing/source/timing invariants, not cosmetic implementation assertions.

Commands: python3 tools/test_muse_image.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/render_problem_opening.py --check; full render with local Chrome/speech access; ffprobe/full decode; source-crop correspondence. Done when user can review a 36-second new proof, Muse artwork was genuinely generated and used, and numeric/source/audio checks pass.

Follow independent read-only spec review, then independent quality/visual final review. Controller reruns commands and checks rendered output receipts. Update CHECKPOINT/NEXT after completion. No publish or master replacement.
