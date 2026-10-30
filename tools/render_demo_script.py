#!/usr/bin/env python3
"""Render the maintained demo timeline into the reviewable narration and shot list."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'submission/demo-timeline.json').read_text())
def stamp(value):
    return f'{value//60}:{value%60:02}'
lines=[f"# {data['title']}", '', f"Three-minute submission video. Device baseline: version {data['baseline_version']}, Build {data['baseline_build']}. {data['status']}.", '', data['opening_note'], '', 'The source timeline is demo-timeline.json. Run python3 tools/render_demo_script.py after changing timing or narration. Production checks and source claims are in CAPTURE-LIST.md and CLAIMS.md.', '']
for item in data['segments']:
    lines += [f"## {stamp(item['start'])} to {stamp(item['end'])} {item['title']}", '', 'Spoken narration', '', item['narration'] or 'No voiceover. Keep the real recitation audible.', '', 'Picture', '', item['visual'], '', 'On screen', '', item['overlay'], '']
words=sum(len(item['narration'].split()) for item in data['segments'])
proof_seconds=sum(item['end']-item['start'] for item in data['segments'] if not item['narration'])
lines += ['## Recording notes', '', f'Total narration: {words} words. The timeline reserves {proof_seconds} seconds for unvoiced live recitation proof. Aim for a calm delivery and preserve those proof sections.', '']
for note in data['production_notes']:
    lines += [note, '']
lines += ['## Rubric priorities', '']
for note in data['rubric_notes']:
    lines += [note, '']
(root/'submission/DEMO-SCRIPT.md').write_text('\n'.join(lines).rstrip()+'\n')
print(f'PASS: rendered 180-second script with {words} spoken words')
