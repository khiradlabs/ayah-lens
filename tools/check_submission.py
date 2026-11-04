#!/usr/bin/env python3
"""Check maintained submission drafts; optionally inspect an exported video."""
import argparse
import json
from pathlib import Path
import re
import subprocess

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--video', type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
folder=root/'submission'
data=json.loads((folder/'demo-timeline.json').read_text())
script=(folder/'DEMO-SCRIPT.md').read_text()
assert data['duration_seconds']==180
last=0
words=0
for segment in data['segments']:
    assert segment['start']==last and segment['end']>last, 'Timeline gap or overlap'
    last=segment['end']
    speech=segment['narration']
    words+=len(speech.split())
    assert not speech or speech in script, 'Rendered narration is stale'
    rate=len(speech.split())*60/(segment['end']-segment['start'])
    assert rate<=160, f"Narration is too fast: {segment['title']}"
    assert all(len(s.split())<25 for s in re.split(r'(?<=[.!?])\s+',speech)), 'Long narration sentence'
    assert not re.search(r'one[- ]third|100\s*%|production[- ]ready|all[- ]day battery',speech,re.I), 'Unsupported spoken claim'
assert last==180
assert any(not x['narration'] and x['end']-x['start']>=25 for x in data['segments']), 'Missing continuous live proof interval'
required=['JUDGING.md','DEMO-SCRIPT.md','CAPTURE-LIST.md','CLAIMS.md','FORM-ANSWERS.md','REVIEW.md','README.md']
for name in required:
    text=(folder/name).read_text()
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if target.startswith(('http:','https:','mailto:','#')):
            continue
        assert (folder/target.split('#')[0]).exists(), f'Broken local link in {name}: {target}'
form=(folder/'FORM-ANSWERS.md').read_text()
fields=['Team Name','Team Members','Which track','Which problem statement','Most Viral Track','Project Description','Public GitHub','3 Minute Demo Video','Describe your use of Meta products','Why are Meta models','Provide feedback','How likely','How would you describe your overall opinion']
for field in fields:
    assert f'## {field}' in form, f'Missing form field: {field}'
assert form.count('Faraz’s choice required.')==2, 'The two personal ratings must remain unselected'
print(f'PASS: contiguous 180-second timeline; {words} narration words; every section <=160 words/minute')
print('PASS: continuous proof interval, rendered narration and local document links')
print('PASS: all 13 form fields covered; two personal ratings remain unselected')
if args.video:
    result=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(args.video.resolve())],capture_output=True,text=True,check=True)
    media=json.loads(result.stdout)
    duration=float(media['format']['duration'])
    assert 179<=duration<=180, f'Expected final export of 179–180 seconds, got {duration:.3f}'
    kinds={stream['codec_type'] for stream in media['streams']}
    assert {'video','audio'}<=kinds, 'Final cut needs both video and audio streams'
    print(f'PASS: exported video is {duration:.3f} seconds with audio and video')
else:
    print('NOT CHECKED: final video, footage authenticity, published links or entrant ratings')
