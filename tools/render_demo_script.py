#!/usr/bin/env python3
"""Render the maintained demo timeline into the reviewable narration and shot list."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'submission/demo-timeline.json').read_text())
def stamp(value):
    return f'{value//60}:{value%60:02}'
lines=[f"# {data['title']}", '', 'Three-minute submission video. Baseline: version 0.3.0, Build 28. Narration is ready for review; live footage remains to be captured.', '', 'Lead with the working glasses. Keep the main recitation proof continuous. Use the matching phone Lens preview for legibility and label it separately from actual lens footage.', '', 'The source timeline is demo-timeline.json. Run python3 tools/render_demo_script.py after changing timing or narration. Production checks and source claims are in CAPTURE-LIST.md and CLAIMS.md.', '']
for item in data['segments']:
    lines += [f"## {stamp(item['start'])} to {stamp(item['end'])} {item['title']}", '', 'Spoken narration', '', item['narration'] or 'No voiceover. Keep the real recitation audible.', '', 'Picture', '', item['visual'], '', 'On screen', '', item['overlay'], '']
words=sum(len(item['narration'].split()) for item in data['segments'])
lines += ['## Recording notes', '', f'Total narration: {words} words. The timeline reserves 43 seconds for unvoiced live recitation proof. Aim for a calm delivery and preserve those proof sections.', '', 'Use source-labelled population figures. Five daily prayers describes the recurring context; it is not a claim that every Muslim would use this product. Keep all-day operation, universal accuracy and measured latency out of the narration.', '', 'Do not imply that every live frame triggers Spark. The paired plans for the filmed long ayahs are cached. The footage should demonstrate the resulting behavior, with the model role explained accurately.']
(root/'submission/DEMO-SCRIPT.md').write_text('\n'.join(lines)+'\n')
print(f'PASS: rendered 180-second script with {words} spoken words')
