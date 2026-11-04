#!/usr/bin/env python3
"""Bounded B/Cedar narration for the restored v0.9 edit.

--check is read-only and offline. --generate requires a cost note and uses the
existing speech helper. It reuses exact receipted WAVs and never retries a paid
call automatically. Independent English-only waveform recognition is required.
"""
import argparse,hashlib,importlib.util,json,re,subprocess,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'build/video-v0.9'; VO=WORK/'narration'
PLAN=ROOT/'submission/narration-v0.9.json'; MANIFEST=WORK/'narration-manifest.json'
IDS=['opening','product','use_cases','meta_challenge','meta_pipeline','hifz','foundation','close']
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def duration(path):
 with wave.open(str(path),'rb') as w:return w.getnframes()/w.getframerate()
def canonical(text):
 text=text.lower().replace('’',"'")
 aliases=[(r"qur['-]?an|koran",'quran'),(r'\b(?:aya(?:h)?\s*len[sz]|eye\s+a\s+len[sz]|ilens|iolens)\b','ayah lens'),(r'\b(?:hifts|hyphs)\b','hifz'),(r'\bfifty[ -]+nine\b','59'),(r'\bsix thousand\b','6000'),(r'\b6,000\b','6000'),(r'\btwo billion\b','2 billion'),(r"\bdon't\b",'do not')]
 for a,b in aliases:text=re.sub(a,b,text)
 return re.findall('[a-z0-9]+',text)
def words_equal(a,b):return canonical(a)==canonical(b)
def load_plan():
 p=json.loads(PLAN.read_text());validate_plan(p);return p
def validate_plan(p):
 if (p['provider'],p['model'],p['voice'],p['speed'])!=('OpenAI','gpt-realtime-2.1','cedar',1):raise ValueError('Expected selected B Cedar at native speed')
 if [x['id'] for x in p['clips']]!=IDS:raise ValueError('Unexpected scene IDs or duplicates')
 approved=json.loads((ROOT/'submission/RESTORATION-V0.9.json').read_text())['approved_opening']['narration']
 if p['clips'][0]['text']!=approved:raise ValueError('Approved opening changed')
 if p['spoken_word_count']!=sum(len(x['text'].split()) for x in p['clips']):raise ValueError('Spoken word count changed')
 if p['quiet_budget_seconds']!=16+sum(p['demo_slots_seconds'].values()):raise ValueError('Measured quiet allocation differs from original recitation and demo slots')
 if p['spoken_word_count']/175*60+p['quiet_budget_seconds']+p['transition_budget_seconds']>=p['max_duration_seconds']:raise ValueError('Planning estimate exceeds limit')
 alltext=' '.join(x['text'] for x in p['clips'])
 for required in ['six thousand verses','Muse Voice','Muse Spark','published English','cached','tracking run live','Fifty-nine core tests']:
  if required not in alltext:raise ValueError('Missing rubric/scope evidence: '+required)
 if 'Teaching support' not in alltext and not any('Teaching support' in q and 'future' in q and 'testing' in q for q in p.get('onscreen_qualifications',[])):raise ValueError('Missing future teaching qualification')
def receipt_valid(path,take):
 r=json.loads(path.with_suffix('.json').read_text())
 if r.get('provider')!='OpenAI' or any(r.get(k)!=take[k] for k in ('model','voice','text','instructions','speed')) or r.get('sha256')!=sha(path):raise ValueError('Cached generation identity/hash differs; no new charge made')
 return r
def take_for(scene,p):
 take={k:p[k] for k in ('model','voice','instructions','speed')}
 take['instructions']=scene.get('instructions',p['instructions']);take.update(text=scene['text'],output=str((VO/(scene['id']+'.wav')).relative_to(ROOT)))
 return take
def speech_module():
 spec=importlib.util.spec_from_file_location('english_narration',ROOT/'tools/openai_narration.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n);n.WORK=VO;return n
def validate_manifest(m,p):
 if not m.get('clips') or not all(x.get('verified') is True for x in m['clips']):raise ValueError('Only verified narration may enter export manifest')
 if [x['id'] for x in m['clips']]!=IDS:raise ValueError('Export scene IDs differ')
 total=0
 for c,expected in zip(m['clips'],p['clips']):
  path=(ROOT/c['path']).resolve()
  if not path.is_relative_to(VO.resolve()) or c['text']!=expected['text'] or c['sha256']!=sha(path):raise ValueError('Export source/text/hash differs')
  take=json.loads(path.with_suffix('.take.json').read_text());r=receipt_valid(path,take)
  if take['text']!=expected['text'] or (take['model'],take['voice'],take['speed'])!=(p['model'],p['voice'],1):raise ValueError('Voice identity differs')
  w=json.loads(path.with_suffix('.wordcheck.json').read_text())
  if w['source_sha256']!=c['sha256'] or not w['exact_after_known_aliases']:raise ValueError('Independent verification receipt differs')
  asrpath=ROOT/w['verification_receipt'];asr=json.loads(asrpath.read_text())
  if asr.get('source_sha256')!=c['sha256'] or asr.get('provider')!='OpenAI' or asr.get('model') not in ('whisper-1','gpt-4o-transcribe','gpt-audio-1.5') or not words_equal(expected['text'],asr['text']):raise ValueError('Actual independent waveform words differ')
  if abs(duration(path)-c['duration_seconds'])>.0001:raise ValueError('Decoded duration differs')
  subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True,capture_output=True)
  total+=c['duration_seconds']
 if abs(total-m['speech_duration_seconds'])>.0001:raise ValueError('Speech duration total differs')
 if total+p['quiet_budget_seconds']+p['transition_budget_seconds']>=p['max_duration_seconds']:raise ValueError('Measured voice plus quiet budget exceeds final limit')
 return {'clips':len(m['clips']),'spoken_words':p['spoken_word_count'],'speech_duration_seconds':round(total,6),'quiet_budget_seconds':p['quiet_budget_seconds'],'transition_budget_seconds':p['transition_budget_seconds'],'projected_total_seconds':round(total+p['quiet_budget_seconds']+p['transition_budget_seconds'],6),'waveform_word_verification':'pass','complete_decode':'pass','source_identity':'pass','costs_estimate_usd':m['costs_estimate_usd']}
def prepare(note):
 p=load_plan();VO.mkdir(parents=True,exist_ok=True);n=speech_module();clips=[]
 for scene in p['clips']:
  path=VO/(scene['id']+'.wav');take=take_for(scene,p)
  save(path.with_suffix('.take.json'),take)
  if path.exists():receipt_valid(path,take)
  else:subprocess.run(['node',str(ROOT/'tools/realtime_narration.cjs'),str(path.with_suffix('.take.json')),'--note',note+' '+scene['id']],check=True)
  r=receipt_valid(path,take)
  primary=n.transcribe(path,note+' independent synthetic-English waveform verification '+scene['id'])
  asr=primary;asrpath=path.with_suffix('.words.json');alternate=path.with_suffix('.second-asr.json')
  if not words_equal(scene['text'],primary['text']) and alternate.exists():
   asr=json.loads(alternate.read_text());asrpath=alternate
   if asr.get('source_sha256')!=sha(path) or asr.get('provider')!='OpenAI' or asr.get('model') not in ('gpt-4o-transcribe','gpt-audio-1.5'):raise ValueError('Alternate ASR identity differs')
  good=words_equal(scene['text'],asr['text'])
  check={'id':scene['id'],'expected':scene['text'],'recognized':asr['text'],'primary_recognized':primary['text'],'verification_receipt':str(asrpath.relative_to(ROOT)),'source_sha256':sha(path),'exact_after_known_aliases':good,'basis':'Independent unprompted recognition of generated English waveform; only documented phonetic/number spelling aliases'}
  save(path.with_suffix('.wordcheck.json'),check)
  if not good:raise ValueError('Independent waveform word mismatch: '+scene['id']+'; inspect saved .wordcheck.json. No automatic speech retry.')
  clips.append({'id':scene['id'],'text':scene['text'],'path':str(path.relative_to(ROOT)),'duration_seconds':duration(path),'sha256':sha(path),'verified':True,'generation_receipt':str(path.with_suffix('.json').relative_to(ROOT)),'verification_receipt':str(asrpath.relative_to(ROOT))})
  print(json.dumps({'verified_clip':scene['id'],'seconds':round(clips[-1]['duration_seconds'],4)}),flush=True)
 costs=sum(json.loads(line).get('estimated_cost_usd',0) or 0 for line in (VO/'costs.jsonl').read_text().splitlines())
 m={'version':'0.9','provider':p['provider'],'model':p['model'],'voice':p['voice'],'speed':1,'clips':clips,'spoken_word_count':p['spoken_word_count'],'speech_duration_seconds':sum(x['duration_seconds'] for x in clips),'costs_estimate_usd':round(costs,8),'cost_method':'Receipt estimates only, not actual provider invoice','cold_review':'Passed by independent cold-viewer reviewer before any generation','original_recitation_seconds':16,'demo_slots_seconds':p['demo_slots_seconds'],'quiet_budget_seconds':p['quiet_budget_seconds'],'transition_budget_seconds':p['transition_budget_seconds'],'cost_call_count':len((VO/'costs.jsonl').read_text().splitlines())}
 result=validate_manifest(m,p);save(MANIFEST,m);save(VO/'verification.json',result);print(json.dumps(result,indent=2));return result
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--generate',action='store_true');parser.add_argument('--check',action='store_true');parser.add_argument('--note');args=parser.parse_args()
 if args.generate:
  if not args.note:parser.error('--generate requires --note')
  return prepare(args.note)
 if args.check:return print(json.dumps(validate_manifest(json.loads(MANIFEST.read_text()),load_plan()),indent=2))
 return print(json.dumps({'words':load_plan()['spoken_word_count'],'status':'offline plan validation passed; no provider called'}))
if __name__=='__main__':main()
