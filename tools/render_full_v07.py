#!/usr/bin/env python3
"""Complete measured v0.7 editorial rebuild. --check is offline and read-only.

Inputs are immutable recordings and receipted synthetic English. No old master is
used for rendering. Every source runs at 1x; no scripture is reconstructed.
"""
import argparse, difflib, hashlib, importlib.util, json, math, re, shutil, subprocess, wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; WORK=ROOT/'build/video-v0.7'; VO=WORK/'narration'; FPS=30
MANIFEST=ROOT/'submission/full-video-v0.7.json'; OUT=WORK/'Ayah-Lens-Demo-v0.7.mp4'
def configure_version(version='0.7'):
 global WORK,VO,MANIFEST,OUT
 if version not in ('0.7','0.8'):raise ValueError('Unsupported full-cut version')
 WORK=ROOT/f'build/video-v{version}';VO=WORK/'narration'
 MANIFEST=ROOT/f'submission/full-video-v{version}.json';OUT=WORK/f'Ayah-Lens-Demo-v{version}.mp4'

NATIVE=ROOT/'recordings/version-3/native-display-recognition-candidate.mp4'
PHONE=ROOT/'recordings/version-3/muzzammil-following-24s-candidate.mp4'
CLEAN=ROOT/'build/video-v0.2.1/assets/within-card-clean.mp4'
def run(args,**kw):return subprocess.run([str(x) for x in args],check=True,**kw)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def duration(p):return float(probe(p)['format']['duration'])
def q(t):return math.ceil(t*FPS-1e-7)/FPS
def make_timeline(ds):
 t={'listen':[0,6]}; end=6.13
 for k in ('hook','human_context'):
  t[k]=[q(end),q(end+ds[k])];end=t[k][1]+.15
 t['native_proof']=[q(end),q(end)+12.5];end=t['native_proof'][1]+.15
 t['long_verse_cue']=[q(end),60]
 if end+ds['long_verse_cue']+.10>60:raise ValueError('Measured complete pre-slot paragraphs do not fit; trim copy explicitly, never tempo-fit')
 t['masjid_reservation']=[60,66];t['phone_reference']=[66,90];end=90.17
 for k in ('following','mechanism','choice_and_use','foundation','close'):
  t[k]=[q(end),q(end+ds[k]+(.65 if k=='close' else .28))];end=t[k][1]
 if end>179.9:raise ValueError('Measured frame-derived edit exceeds 179.9 seconds')
 return t

def validate_audio_windows(rows):
 for i,(kind,a,b) in enumerate(rows):
  if a<0 or b<=a:raise ValueError('Invalid audio window')
  for kind2,c,d in rows[:i]:
   if a<d-1e-6 and b>c+1e-6:raise ValueError('English or independent reciters overlap')
def validate_source(s,d,w,h):
 x,y,cw,ch=s['crop']
 if s['speed']!=1 or not 0<=s['start_seconds']<=s['end_seconds']<=d+1e-6 or min(x,y,cw,ch)<0 or x+cw>w or y+ch>h:raise ValueError('Source rate, crop or duration is unsafe')
def canonical(s):
 s=s.lower().replace('’',"'")
 for a,b in [(r"qur['-]?an|koran",'quran'),(r'\b(?:aya(?:h)?\s*len[sz]|eye\s+a\s+len[sz]|ilens|iolens)\b','ayah lens'),(r'\b(?:hifts|hyphs)\b','hifz'),(r'\bsuras\b','surahs'),(r'\btwo billion\b','2 billion'),(r'\btwenty[ -]twenty\b','2020')]:s=re.sub(a,b,s)
 return re.findall('[a-z0-9]+',s)
def words_equal(a,b):return canonical(a)==canonical(b)
def receipt_valid(path,take):
 r=json.loads(path.with_suffix('.json').read_text())
 if any(r.get(k)!=take[k] for k in ('model','voice','text','instructions','speed')) or r.get('provider')!='OpenAI' or r.get('sha256')!=sha(path):raise ValueError('Cached generation identity or hash mismatch')
 return r

def prepare(note):
 VO.mkdir(parents=True,exist_ok=True); scenes=json.loads(MANIFEST.read_text())['scenes']; voice=json.loads((ROOT/'submission/narration-v0.7.json').read_text())
 instructions=voice['instructions'].replace('Read only the supplied script exactly once, all words through the final word moment.','Read only the supplied script exactly once, including every final word.').replace('Start the question with sincere curiosity, then let the explanation become a little quicker and more animated.','Let the explanation flow with engaged curiosity.').replace('Ease off naturally near stay with the moment.','Ease off naturally at the paragraph end.')+' Pronounce Ayah Lens as eye-ah lens, Hifz as hifz, Salat as suh-laat, Muse as myooz. Keep names as written, without spoken pronunciation notes.'
 spec=importlib.util.spec_from_file_location('narration',ROOT/'tools/openai_narration.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n);n.WORK=VO
 clips=[];failures=[]
 for scene in scenes:
  if not scene['narration']:continue
  name=scene['id'];path=VO/(name+'.wav');take={'model':voice['model'],'voice':voice['voice'],'text':scene['narration'],'instructions':voice['instructions'] if name=='hook' else instructions,'speed':1,'output':str(path.relative_to(ROOT))}
  save(path.with_suffix('.take.json'),take)
  if name=='hook' and not path.exists():
   old=ROOT/voice['approved_audition'];receipt_valid(old,take);shutil.copyfile(old,path);shutil.copyfile(old.with_suffix('.json'),path.with_suffix('.json'))
   # Independent acoustic transcription already exists; validate it against the exact hash.
   oldwords=json.loads(old.with_suffix('.words.json').read_text())
   if oldwords.get('source_sha256')==sha(path) and oldwords.get('provider')=='OpenAI':save(path.with_suffix('.words.json'),oldwords)
  if not path.exists():run(['node',ROOT/'tools/realtime_narration.cjs',path.with_suffix('.take.json'),'--note',note+' '+name])
  r=receipt_valid(path,take);asr=n.transcribe(path,note+' independent English word verification '+name)
  good=words_equal(scene['narration'],asr['text']);verified_text=asr['text'];verification_basis='Independent Whisper transcription'
  alternate=path.with_suffix('.second-asr.json')
  if not good and alternate.exists():
   second=json.loads(alternate.read_text())
   if second.get('source_sha256')!=sha(path) or second.get('provider')!='OpenAI' or second.get('model') not in ('gpt-4o-transcribe','gpt-audio-1.5'):raise ValueError('Alternate ASR receipt invalid')
   good=words_equal(scene['narration'],second['text'])
   if good:verified_text=second['text'];verification_basis='Independent actual-audio second recognizer; primary homophone retained separately'
  check={'id':name,'expected':scene['narration'],'recognized':verified_text,'primary_recognized':asr['text'],'verification_basis':verification_basis,'alternate_receipt':str(alternate.relative_to(ROOT)) if alternate.exists() else None,'exact_after_known_aliases':good,'source_sha256':sha(path),'difference':list(difflib.ndiff(canonical(scene['narration']),canonical(asr['text']))) if not good else []};save(path.with_suffix('.wordcheck.json'),check)
  if not good:failures.append(name)
  clips.append({'id':name,'path':str(path.relative_to(ROOT)),'duration':duration(path),'sha256':sha(path),'word_count':len(scene['narration'].split()),'text':scene['narration']})
  print(f'Measured {name}: {clips[-1]["duration"]:.3f}s, complete words verified',flush=True)
 if failures:raise ValueError('Independent transcription requires review: '+', '.join(failures))
 timeline=make_timeline({c['id']:c['duration'] for c in clips});windows=[('quran',0,6),('quran',*timeline['native_proof']),('quran',66,90)]
 for c in clips:c['start']=timeline[c['id']][0];windows.append(('english',c['start'],c['start']+c['duration']))
 validate_audio_windows(windows)
 data={'clips':clips,'timeline':timeline,'audio_windows':windows,'frames':round(timeline['close'][1]*FPS),'fps':FPS,'duration':timeline['close'][1],'no_time_stretching':True,'native_source':str(NATIVE.relative_to(ROOT)),'phone_source':str(PHONE.relative_to(ROOT))}
 save(WORK/'measured-edit.json',data);(WORK/'spoken-script.txt').write_text('\n\n'.join(c['text'] for c in clips)+'\n')
 m=json.loads(MANIFEST.read_text());m['source_proof_receipt']={'native':{'sha256':sha(NATIVE),'seconds':12.5,'frames':375,'speed':1,'crop':[208,832,576,144]},'phone':{'sha256':sha(PHONE),'seconds':24,'frames':720,'speed':1,'crop':[48,1232,984,1116]},'clean_card_mask':'build/video-v0.2.1/assets/card-mask.json'};m['measured_timing_receipt']={'path':str((WORK/'measured-edit.json').relative_to(ROOT)),'timeline':timeline,'duration_seconds':data['duration'],'frames':data['frames'],'speech_words':sum(c['word_count'] for c in clips)};MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
 return data

def pcm(path):
 return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ar','48000','-ac','2','-'])
def audio_track(edit):
 import array
 total=round(edit['duration']*48000);mix=array.array('f',[0])*(total*2);receipts=[]
 inputs=[('listen',NATIVE,0,6),('native_proof',NATIVE,edit['timeline']['native_proof'][0],12.5),('phone_reference',PHONE,66,24)]+[(c['id'],ROOT/c['path'],c['start'],c['duration']) for c in edit['clips']]
 for name,path,start,length in inputs:
  measure=run(['ffmpeg','-hide_banner','-i',path,'-af','loudnorm=I=-23:TP=-3:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True)
  met=json.JSONDecoder().raw_decode(measure.stderr[measure.stderr.rfind('{'):])[0];gain=-23-float(met['input_i']);factor=10**(gain/20)
  spoken=name not in ('listen','native_proof','phone_reference');audio_source=path
  if spoken:
   audio_source=WORK/'processed-English'/f'{name}.wav';audio_source.parent.mkdir(exist_ok=True)
   run(['ffmpeg','-v','error','-y','-i',path,'-af',f'volume={gain}dB,alimiter=limit=0.707946:attack=5:release=70:level=false:latency=true','-ar','48000','-ac','2','-c:a','pcm_s24le',audio_source]);factor=1
  a=array.array('f');a.frombytes(pcm(audio_source));count=min(round(length*48000)*2,len(a));offset=round(start*48000)*2
  for j in range(count):mix[offset+j]=a[j]*factor
  receipts.append({'id':name,'source':str(path.relative_to(ROOT)),'start':start,'duration':length,'gain_db':gain,'input_lufs':met['input_i'],'input_peak_dbfs':met['input_tp'],'speed':1,'fades':'none; original complete word tails retained','peak_limiter':{'ceiling_dbfs':-3,'attack_ms':5,'release_ms':70,'latency_compensated':True,'automatic_makeup_gain':False} if spoken else None,'processed_source':str(audio_source.relative_to(ROOT))})
 raw=WORK/'mix.f32';raw.write_bytes(mix.tobytes());run(['ffmpeg','-v','error','-y','-f','f32le','-ar','48000','-ac','2','-i',raw,'-c:a','pcm_s24le',WORK/'mix.wav']);raw.unlink();save(WORK/'receipts/audio-mix.json',receipts)
 # One English-only continuous file for private listening, never real recitation upload.
 args=['ffmpeg','-v','error','-y'];labels=[]
 for i,c in enumerate(edit['clips']):args+=['-i',WORK/'processed-English'/f'{c["id"]}.wav'];labels.append(f'[{i}:a]')
 run(args+['-filter_complex',''.join(labels)+f'concat=n={len(labels)}:v=0:a=1,aresample=24000[a]','-map','[a]','-c:a','pcm_s16le',WORK/'English-only.wav'])

def extract_sources():
 # Original and clean-card streams have identical frame indices and source text.
 mask=json.loads((CLEAN.parent/'card-mask.json').read_text());assert mask['source_sha256']==sha(PHONE) and mask['min_mask_start']>=965
 for name,path in [('native',NATIVE),('phone',PHONE),('card',CLEAN)]:
  folder=WORK/'frames'/name;folder.mkdir(parents=True,exist_ok=True)
  expected=375 if name=='native' else 720
  if len(list(folder.glob('*.jpg')))!=expected:run(['ffmpeg','-v','error','-y','-i',path,'-an','-q:v','2',folder/'%04d.jpg'])

def source_frame(t,start,count):
 return min(count-1,max(0,round((t-start)*FPS)))

def following_last_frame(timeline):
 start,end=timeline['following']
 return min(719,max(0,round(end*FPS)-1-round(start*FPS)))

def scene_at(timeline,t):
 return max((k for k,(a,b) in timeline.items() if a<=t),key=lambda k:timeline[k][0])

def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def scene_exit_opacity(scene,t,next_start):
 if scene not in ('hook','human_context','long_verse_cue','mechanism','choice_and_use','foundation'):return 1
 return 1-ease((t-(next_start-.3))/.3)

def ending_stage(enabled,local,cues):
 if not enabled or local>=cues[1]:return 'resolve'
 return 'population' if local<cues[0] else 'meaning'

def lerp(a,b,p):return tuple(round(x+(y-x)*p) for x,y in zip(a,b))

def render_picture(edit, frame_range=None):
 from PIL import Image,ImageDraw,ImageFont
 extract_sources(); scenes=json.loads(MANIFEST.read_text())['scenes'];byid={s['id']:s for s in scenes};timeline=edit['timeline'];clips={c['id']:c for c in edit['clips']}
 fonts={n:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',n) for n in (22,24,28,30,34,38,44,54,68,92)}
 bg='#F3F0E8';ink='#252B2D';blue='#597E94';muted='#637078';large=(730,370,1070,268);small=(1450,240,340,85);phonebox=(730,190,660,749)
 cache={}
 def source(name,index):
  key=(name,index)
  if key not in cache:
   if len(cache)>12:cache.clear()
   cache[key]=Image.open(WORK/'frames'/name/f'{index+1:04d}.jpg').convert('RGB')
  return cache[key]
 def text(im,words,xy,size=34,color=ink,width=1500):
  d=ImageDraw.Draw(im);x,y=xy;line=''
  for word in words.split():
   if d.textlength((line+' '+word).strip(),font=fonts[size])>width and line:d.text((x,y),line,font=fonts[size],fill=color);y+=int(size*1.3);line=word
   else:line=(line+' '+word).strip()
  if line:d.text((x,y),line,font=fonts[size],fill=color)
  return y+size*1.3
 def paste(im,pic,box,opacity=1):
  x,y,w,h=box
  if w>0 and h>0:
   scaled=pic.resize((w,h),Image.Resampling.LANCZOS)
   if opacity<1:scaled=Image.blend(Image.new('RGB',(w,h),bg),scaled,opacity)
   im.paste(scaled,(x,y));ImageDraw.Draw(im).rectangle((x-1,y-1,x+w,y+h),outline='#B5BFC1',width=2)
 def node(im,label,x,y,w=360,h=110,active=True,opacity=1):
  layer=Image.new('RGBA',im.size,(0,0,0,0));y+=round(12*(1-opacity));d=ImageDraw.Draw(layer);d.rounded_rectangle((x,y,x+w,y+h),18,fill='#E2E8E8' if active else bg,outline=blue if active else '#B6C1C4',width=3);text(layer,label,(x+22,y+20),28,width=w-40)
  layer.putalpha(layer.getchannel('A').point(lambda alpha:round(alpha*opacity)));im.paste(layer,(0,0),layer)
 def cue(name,phrase,default):
  words=json.loads((ROOT/clips[name]['path']).with_suffix('.words.json').read_text())['words'];wanted=canonical(phrase)
  for i in range(len(words)):
   if canonical(' '.join(w['word'] for w in words[i:i+len(wanted)]))==wanted:return float(words[i]['start'])
  return default
 techcues=[cue('mechanism',p,d) for p,d in [('Muse Voice',0),('Local software',4),('Muse Spark',8),('cached pairing',13),('Local checks',16)]]
 choicecues=[cue('choice_and_use',p,d) for p,d in [('For Hifz',5),('We are also exploring',10.8)]]
 foundationcues=[cue('foundation',p,d) for p,d in [('The reference library',5),('Our core tests',9),('Teaching support',13.4)]]
 contextcue=cue('human_context','The Quran',7)
 impact=byid['close'].get('impact_ending',False)
 closecues=[cue('close','For listeners',7),cue('close','Ayah Lens',13)] if impact else []
 def frame(t,transitions=True):
  key=scene_at(timeline,t)
  a,b=timeline[key];local=max(0,t-a);p=ease(local/.5);protected=[];im=Image.new('RGB',(1920,1080),bg);d=ImageDraw.Draw(im)
  text(im,'Ayah Lens',(120,64),44);text(im,'PROTOTYPE / SELECTED WORKING DEMONSTRATIONS',(1030,80),22,muted,width=770)
  d.line((120,850,1800,850),fill='#BBC5C5',width=3);marker=120+1680*t/edit['duration'];d.ellipse((marker-7,843,marker+7,857),fill=blue)
  english=any(c['start']<=t<c['start']+c['duration'] for c in edit['clips'])
  if english:text(im,'AI-generated English narration',(120,1014),22,muted)
  native_idx=source_frame(t,a,375) if key=='native_proof' else source_frame(t,0,180) if key=='listen' else 179 if key in ('hook','human_context') else 374
  native=source('native',native_idx);nc=native.crop((208,832,784,976))
  if key in ('listen','native_proof'):
   box=large if key=='listen' else lerp(small,large,p)
   full_opacity=min(1,p) if key=='native_proof' else 1
   next_start=timeline['long_verse_cue'][0] if key=='native_proof' else timeline['hook'][0]
   full_opacity=min(full_opacity,ease((next_start-t)/.5));paste(im,native,(120,180,490,651),full_opacity);paste(im,nc,box)
   text(im,'Native camera + display recording',(120,875),28)
   text(im,'Enlarged same-frame display crop / not optical lens footage',(730,690),24,muted,width=1070)
   text(im,'Earlier prototype'+(' / complete 12.5 second replay' if key=='native_proof' else ''),(120,924),24,muted)
  elif key in ('hook','human_context','long_verse_cue','close'):
   box=lerp(large,small,p) if key in ('hook','long_verse_cue') else lerp(small,large,p) if key=='close' else small
   if key=='close' and impact:box=small if local<closecues[1] else lerp(small,large,ease((local-closecues[1])/.5))
   source_opacity=ease((60-t)/.3) if key=='long_verse_cue' and t>59.7 else 1
   paste(im,nc,box,source_opacity);protected.append((box[0]-2,box[1]-2,box[0]+box[2]+2,box[1]+box[3]+80));text(im,'Held recorded frame / earlier prototype',(box[0],box[1]+box[3]+16),22,muted,width=box[2]+30)
  if key=='hook' and local>=.5:
   text(im,'Your personal Quran translator?',(120,200),68,width=1200)
   text(im,'Hear the recitation.\nFollow the meaning.'.replace('\n',' '),(120,425),44,width=1050)
   node(im,'Arabic source',120,640,380);node(im,'Published English meaning',560,640,560)
   d.rounded_rectangle((1450+round(110*p),530,1580+round(110*p),760),18,outline=blue,width=4);text(im,'Phone aside',(1420,782),24,muted)
  elif key=='human_context':
   if local<contextcue:
    text(im,'About 2 billion',(120,210),92);text(im,'Muslims / roughly one quarter of humanity',(120,340),38,width=1120)
    for j in range(4):d.rounded_rectangle((120+j*265,470,345+j*265,530),8,fill=blue if j==0 else '#D3DCDD')
    text(im,'Pew Research Center / 2020 estimate, published June 2025',(120,610),28,muted,width=1200)
   else:
    text(im,'For listeners seeking English meaning',(120,210),54,width=1200)
    node(im,'Arabic recitation',120,440,460);node(im,'Published English meaning',670,440,590);d.line((580,495,670,495),fill=blue,width=5)
    text(im,'Ayah Lens / Meta Ray-Ban Display',(120,665),38,width=1250)
  elif key=='long_verse_cue' and local>=.5:
   text(im,'One long verse. Changing portions.',(120,210),54,width=1250)
   for j in range(7):d.rounded_rectangle((120+j*165,460,265+j*165,555),10,fill='#DDE4E4')
   x=120+round(650*min(1,local/6));d.rectangle((x,440,x+340,575),outline=blue,width=5)
   text(im,'Explanatory reading-window diagram',(120,615),28,muted)
   text(im,'Masjid slot reserved / phone reference follows',(120,740),30)
  elif key=='masjid_reservation':
   handoff=ease((local-5.6)/.4);rx,ry,rw,rh=lerp((120,190,1680,605),phonebox,handoff)
   cardshade=tuple(round(243+(32-243)*handoff) for _ in range(3));phoneshade=tuple(round(243*(1-handoff)) for _ in range(3))
   d.rounded_rectangle((rx,ry,rx+rw,ry+rh),24,fill=cardshade,outline=blue,width=3)
   if handoff>0:d.rectangle((120,170,424,831),fill=phoneshade)
   layer=Image.new('RGBA',im.size,(0,0,0,0));text(layer,'MASJID RECORDING / RESERVED',(190,295),54,width=1450);text(layer,'Fresh masjid footage is not available',(190,440),44,width=1450);text(layer,'Phone reference follows',(190,570),38,muted)
   layer.putalpha(layer.getchannel('A').point(lambda alpha:round(alpha*(1-handoff))));im.paste(layer,(0,0),layer);d=ImageDraw.Draw(im)
   if handoff>0:text(im,'MASJID RECORDING / RESERVED',(120,130),24,muted)
  elif key in ('phone_reference','following'):
   si=min(719,round(local*30));phone=source('phone',si).copy();card=source('card',si);phone.paste(card,(48,1232))
   left_opacity=ease((timeline['mechanism'][0]-t)/.3) if key=='following' else 1
   paste(im,phone,(120,170,304,661),left_opacity);paste(im,card,phonebox)
   text(im,'73:20',(1460,200),54);text(im,'One ayah, changing portions',(1450,285),30,width=340)
   text(im,'PHONE REFERENCE / earlier prototype / not masjid footage' if key=='phone_reference' else 'SILENT REPLAY / earlier phone prototype',(120,855),24,width=540)
   if key=='following':text(im,'No manual paging',(1450,530),34,blue,width=340)
  elif key=='mechanism':
   paste(im,source('card',following_last_frame(timeline)),lerp(phonebox,(1490,190,300,340),p))
   if local>=.5:
    titlelayer=Image.new('RGBA',im.size,(0,0,0,0));text(titlelayer,'From sound to published meaning',(120,150),54,width=1250);titlelayer.putalpha(titlelayer.getchannel('A').point(lambda alpha:round(alpha*ease((local-.5)/.35))));im.paste(titlelayer,(0,0),titlelayer)
   labels=['Muse Voice: live Arabic transcript','Local passage + position tracker','Muse Spark: source pairing','Cached pairing plans','Local source-word validation'];positions=[(120,365),(660,365),(120,575),(660,575),(1200,575)]
   routes=[[(560,430),(660,430)],[(880,495),(880,535),(340,535),(340,575)],[(560,640),(660,640)],[(1100,640),(1200,640)]]
   for i,route in enumerate(routes):
    if local>=techcues[i+1]:
     growth=ease((local-techcues[i+1])/.5);lengths=[math.dist(x,y) for x,y in zip(route,route[1:])];remaining=growth*sum(lengths);tip=route[0]
     for x,y,length in zip(route,route[1:],lengths):
      portion=min(1,max(0,remaining/length));tip=lerp(x,y,portion);d.line((*x,*tip),fill=blue,width=4);remaining-=length
      if remaining<=0:break
     d.ellipse((tip[0]-6,tip[1]-6,tip[0]+6,tip[1]+6),fill=blue)
   for i,(label,pos) in enumerate(zip(labels,positions)):
    if local>=techcues[i]:node(im,label,*pos,440,130,opacity=ease((local-techcues[i])/.5))
   text(im,'Published Tanzil Arabic / Pickthall English',(120,745),28,muted,width=1100)
   if local>=techcues[2]:text(im,'Uncertain match: supplied candidates or abstain',(730,735),24,muted,width=1000)
  elif key=='choice_and_use':
   text(im,'Meaning when you need it',(120,200),54)
   if local<choicecues[0]:
    d.rounded_rectangle((120,350,960,720),24,outline=blue,width=4);text(im,'TV listening',(185,440),54);text(im,'Possible setting',(185,545),30,muted)
   elif local<choicecues[1]:
    text(im,'Hifz / Quran memorization',(120,330),44);node(im,'Arabic reference',120,460,590,170);node(im,'Arabic + English meaning',790,460,700,170)
    text(im,'Explanatory mode diagram / not filmed switch proof',(120,705),28,muted,width=1550)
    text(im,'Show English meaning / implemented switch',(120,760),28,blue,width=1500)
   else:text(im,'Possible Salat use / Muslim prayer',(120,400),54,width=1600)
  elif key=='foundation':
   if local<foundationcues[0]:
    text(im,'Built during this hackathon',(120,230),54);node(im,'Glasses integration',120,440,650,160);node(im,'Automatic following',880,440,720,160)
   elif local<foundationcues[1]:
    text(im,'Complete reference library',(120,220),54);text(im,'114 surahs / 6,236 ayahs',(120,410),68)
    text(im,'Reference coverage, not verified recognition accuracy',(120,590),34,muted,width=1650)
   elif local<foundationcues[2]:
    text(im,'59 core tests passed',(120,220),68);text(im,'Recorded November 2 receipt / build/logs/core-tests.log',(120,380),30,muted,width=1600)
    text(im,'Matching / source preservation / display scheduling',(120,490),38,width=1600)
    text(im,'Selected software tests, not a whole-Quran accuracy study',(120,650),30,muted,width=1600)
   else:
    text(im,'Future teaching support',(120,250),68);text(im,'Further development and extensive testing required',(120,440),38,width=1600)
  elif key=='close' and impact and ending_stage(impact,local,closecues)!='resolve':
   if ending_stage(impact,local,closecues)=='population':
    text(im,'Potential impact',(120,205),68,width=1200)
    text(im,'Roughly one quarter of humanity',(120,335),44,width=1200)
    for j in range(4):d.rounded_rectangle((120+j*265,470,345+j*265,530),8,fill=blue if j==0 else '#D3DCDD')
    text(im,'Pew Research Center / 2020 estimate, published June 2025',(120,610),28,muted,width=1250)
    text(im,'Population context / potential reach',(120,690),28,muted,width=1250)
   else:
    text(im,'For listeners seeking English meaning',(120,205),54,width=1250)
    node(im,'Daily recitation',120,440,460);node(im,'Hands-free meaning',670,440,590)
    d.line((580,495,670,495),fill=blue,width=5)
    text(im,'Potential benefit / understanding not measured',(120,665),30,muted,width=1250)
  elif key=='close':
   text(im,'Hear the recitation.',(120,205),54,width=1100);text(im,'Follow the meaning.',(120,280),54,width=1100)
   text(im,'Stay with the moment.',(120,740),44,width=1300)
  if key in ('long_verse_cue','masjid_reservation','phone_reference') or (key=='choice_and_use' and local>=choicecues[1]):
   text(im,'Technology demonstration only. This does not establish religious permissibility for use during prayer.',(120,962),24,muted,width=1680)
  # Separate exit and entry phases prevent old/new glyph superposition.
  # Sources, their labels, the header, rail and footer never enter this layer.
  if transitions:
   internal=([contextcue] if key=='human_context' else choicecues if key=='choice_and_use' else foundationcues if key=='foundation' else closecues if key=='close' and impact else [])
   factor=1.;slide=0
   for boundary in internal:
    delta=local-boundary
    if -.225<=delta<0:factor=min(factor,1-ease((delta+.225)/.225))
    elif 0<=delta<.225:factor=min(factor,ease(delta/.225));slide=round(12*(1-factor))
   intro=.5 if key in ('hook','long_verse_cue') else 0
   if key in ('hook','human_context','long_verse_cue','choice_and_use','foundation','close') and intro<=local<intro+.3:
    factor=min(factor,ease((local-intro)/.3));slide=round(12*(1-factor))
   ordered=list(timeline);index=ordered.index(key);next_start=timeline[ordered[index+1]][0] if index+1<len(ordered) else edit['duration']
   factor=min(factor,scene_exit_opacity(key,t,next_start))
   if factor<1:
    original=im.copy();region=(100,140,1820,815);body=im.crop(region);body=Image.blend(Image.new('RGB',body.size,bg),body,factor);ImageDraw.Draw(im).rectangle(region,fill=bg);im.paste(body,(100,140+slide))
    for rect in protected:im.paste(original.crop(rect),(rect[0],rect[1]))
  if key=='human_context' and timeline['native_proof'][0]-.3<=t<timeline['native_proof'][0]:text(im,'Next: complete 12.5 second native replay',(120,924),24,muted)
  if key=='close' and t>edit['duration']-.4:im=Image.blend(im,Image.new('RGB',im.size,bg),ease((t-(edit['duration']-.4))/.4))
  return im
 picture=WORK/('patch-reservation.mp4' if frame_range else 'picture.mp4')
 log=(WORK/'receipts/picture-render.log').open('w');process=subprocess.Popen(['ffmpeg','-v','warning','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-pix_fmt','yuv420p',str(picture)],stdin=subprocess.PIPE,stderr=log)
 qa=WORK/'qa';qa.mkdir(exist_ok=True)
 try:
  for i in range(*(frame_range or (0,edit['frames']))):
   im=frame(i/30);process.stdin.write(im.tobytes())
   if i%900==0:print(f'Picture rendered {i}/{edit["frames"]} frames',flush=True)
   if i in [round((a+.75)*30) for a,b in timeline.values()]:im.resize((960,540)).save(qa/f'frame-{i:04d}.jpg')
 finally:process.stdin.close()
 if process.wait()!=0:raise RuntimeError('Picture encoder failed; see log')
 if frame_range:return
 run(['ffmpeg','-v','error','-y','-i',WORK/'picture.mp4','-i',WORK/'mix.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t',edit['duration'],'-movflags','+faststart',OUT])
 save(WORK/'receipts/visual-cues.json',{'mechanism_relative_word_cues':techcues,'source_card_mask':json.loads((CLEAN.parent/'card-mask.json').read_text()),'source_geometry':{'native_crop':list(large),'phone_crop':list(phonebox)},'rail_y':850,'transition_seconds':.5})

def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
def caption_chunks(text,words):
 # Caption spelling comes from the verified script; recognition supplies timing.
 # Merge only the documented phonetic product-name spelling; keep raw ASR intact.
 aligned=[];i=0
 while i<len(words):
  if i+2<len(words) and [w['word'].lower().strip('.,:') for w in words[i:i+3]]==['eye','a','lens']:
   aligned.extend([dict(word='Ayah',start=words[i]['start'],end=words[i+1]['end']),words[i+2]]);i+=3
  else:aligned.append(words[i]);i+=1
 words=aligned
 tokens=[row for row in words for token in canonical(row['word'])];script=text.split();counts=[len(canonical(word)) for word in script]
 if len(tokens)!=sum(counts):raise ValueError('Caption lexical alignment differs; inspect verified word receipts')
 rows=[];offset=0
 for i in range(0,len(script),10):
  end=offset+sum(counts[i:i+10]);rows.append((tokens[offset]['start'],tokens[end-1]['end'],' '.join(script[i:i+10])));offset=end
 return rows

def captions(edit):
 rows=[]
 for c in edit['clips']:
  words=json.loads((ROOT/c['path']).with_suffix('.words.json').read_text())['words']
  rows.extend((c['start']+a,c['start']+b,s) for a,b,s in caption_chunks(c['text'],words))
 (WORK/'captions.srt').write_text('\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}\n' for i,(a,b,s) in enumerate(rows)))

def check():
 """Offline validation. Writes no files, reads no key, and opens no network."""
 import array
 from PIL import Image,ImageChops,ImageStat
 e=json.loads((WORK/'measured-edit.json').read_text());m=json.loads(MANIFEST.read_text());report={};errors=[]
 def require(ok,label):
  if not ok:errors.append(label)
 inventory=json.loads((WORK/'receipts/input-inventory.json').read_text())
 report['immutable_inputs']={r['path']:sha(ROOT/r['path'])==r['sha256'] for r in inventory};require(all(report['immutable_inputs'].values()),'Source or previous master hash changed')
 validate_audio_windows(e['audio_windows']);require(e['timeline']['masjid_reservation']==[60,66] and e['timeline']['phone_reference']==[66,90],'Fixed reservation/reference boundary')
 require(e['frames']/30==e['duration'] and e['duration']<=179.9,'Frame-derived duration limit')
 for s in m['scenes']:
  src=s.get('source')
  if src and 'path' in src:
   native='native' in src['path'];validate_source(src,12.5 if native else 24,976 if native else 1080,1296 if native else 2348)
 report['word_checks']={}
 for c in e['clips']:
  p=ROOT/c['path'];r=json.loads(p.with_suffix('.json').read_text());a=json.loads(p.with_suffix('.words.json').read_text());w=json.loads(p.with_suffix('.wordcheck.json').read_text());good=words_equal(c['text'],a['text'])
  if not good and p.with_suffix('.second-asr.json').exists():
   alt=json.loads(p.with_suffix('.second-asr.json').read_text());good=alt.get('provider')=='OpenAI' and alt.get('model') in ('gpt-4o-transcribe','gpt-audio-1.5') and alt.get('source_sha256')==sha(p) and words_equal(c['text'],alt['text'])
  receipt_valid(p,json.loads(p.with_suffix('.take.json').read_text()))
  good=good and a.get('model')=='whisper-1' and sha(p)==c['sha256']==r['sha256'] and r['text']==c['text'] and r['model']=='gpt-realtime-2.1' and r['voice']=='cedar' and a['source_sha256']==sha(p) and a['provider']=='OpenAI'
  report['word_checks'][c['id']]=good;require(good,'Unverified English words: '+c['id'])
 decode=run(['ffmpeg','-v','error','-xerror','-i',OUT,'-f','null','-'],capture_output=True,text=True);report['full_stream_decode']=decode.returncode==0
 p=probe(OUT);v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio');report['streams']={'frames':int(v['nb_frames']),'video_duration':float(v['duration']),'audio_duration':float(a['duration']),'width':v['width'],'height':v['height'],'sample_rate':a['sample_rate'],'channels':a['channels']}
 require(int(v['nb_frames'])==e['frames'] and v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='30/1','Frame count or video format');require(a['sample_rate']=='48000' and a['channels']==2 and abs(float(a['duration'])-e['duration'])<.03,'Audio duration/format')
 vol=run(['ffmpeg','-hide_banner','-i',OUT,'-af','volumedetect','-f','null','-'],capture_output=True,text=True);peak=float(re.search(r'max_volume: ([-\d.]+)',vol.stderr)[1]);report['peak_dbfs']=peak;require(peak<=-1,'Mix peak exceeds -1 dBFS')
 mixed=array.array('f');mixed.frombytes(pcm(OUT));report['source_audio_correlation']={}
 for name,path,start,length in [('listen',NATIVE,0,6),('native_proof',NATIVE,e['timeline']['native_proof'][0],12.5),('phone_reference',PHONE,66,24)]:
  original=array.array('f');original.frombytes(pcm(path));offset=round(start*48000)*2;count=min(len(original),round(length*48000)*2);aa=bb=ab=0.
  for j in range(100,count-100,98):x=original[j];y=mixed[offset+j];aa+=x*x;bb+=y*y;ab+=x*y
  corr=ab/math.sqrt(aa*bb);report['source_audio_correlation'][name]=corr;require(corr>.98,'Source audio correspondence '+name)
 report['english_audio_correspondence']={}
 for c in e['clips']:
  processed=WORK/'processed-English'/f'{c["id"]}.wav';original=array.array('f');original.frombytes(pcm(processed));offset=round(c['start']*48000)*2;count=min(len(original),round(c['duration']*48000)*2);aa=bb=ab=0.
  for j in range(100,count-100,98):x=original[j];y=mixed[offset+j];aa+=x*x;bb+=y*y;ab+=x*y
  corr=ab/math.sqrt(aa*bb);report['english_audio_correspondence'][c['id']]=corr;require(corr>.98,'Final English waveform correspondence '+c['id'])
 # SSIM compares decoded source-card pixels at source speed after inverse layout scaling.
 report['source_crop_ssim']={}
 for name,path,start,length,kind in [('listen',NATIVE,0,6,'native'),('native_proof',NATIVE,e['timeline']['native_proof'][0],12.5,'native'),('phone_reference',CLEAN,66,24,'card')]:
  for at in (.75,length/2,length-.75):
   crop='crop=1070:268:730:370,scale=576:144' if kind=='native' else 'crop=660:749:730:190,scale=984:1116'
   ref='crop=576:144:208:832' if kind=='native' else 'null'
   command=['ffmpeg','-hide_banner','-ss',start+at,'-i',OUT,'-ss',at,'-i',path,'-filter_complex',f'[0:v]{crop},format=yuv420p[a];[1:v]{ref},format=yuv420p[b];[a][b]ssim','-frames:v','1','-an','-f','null','-'];r=run(command,capture_output=True,text=True);vals=re.findall(r'All:([\d.]+)',r.stderr);value=float(vals[-1]);report['source_crop_ssim'][f'{name}/{at:.2f}']=value;require(value>.91,'Source crop SSIM '+name)
 def image_at(t):
  b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1','-f','image2pipe','-vcodec','png','-']);import io;return Image.open(io.BytesIO(b)).convert('RGB')
 report['transition_metrics']={}
 boundaries=[e['timeline']['native_proof'][1],60,66,90,e['timeline']['mechanism'][0],e['timeline']['choice_and_use'][0]]
 for boundary in boundaries:
  frames=[image_at(boundary+i/30) for i in range(-3,16)];mad=[sum(ImageStat.Stat(ImageChops.difference(x,y)).mean)/3 for x,y in zip(frames,frames[1:])];sample=round(boundary*48000)*2;edge=max(abs(mixed[j]-mixed[j-2]) for j in range(max(2,sample-960),min(len(mixed),sample+960),2))
  report['transition_metrics'][str(boundary)]={'consecutive_frames':len(frames),'mean_absolute_picture_change':mad,'maximum_sample_edge':edge};require(max(mad)<70,'Abrupt picture discontinuity '+str(boundary));require(edge<.25,'Audio edge discontinuity '+str(boundary))
 # The six-second reservation must stay silent even after AAC encode.
 reserved=mixed[round(60.05*48000)*2:round(65.95*48000)*2];rms=math.sqrt(sum(x*x for x in reserved)/len(reserved));report['reservation_rms']=rms;require(rms<1e-5,'Reservation is not quiet')
 report['errors']=errors;report['pass']=not errors;print(json.dumps(report,indent=2));
 if errors:raise SystemExit(1)
 return report

def qa_artifacts():
 """Private review windows from the exact encoded master, including internal cues."""
 e=json.loads((WORK/'measured-edit.json').read_text());captions(e);timeline=e['timeline'];qa=WORK/'qa/motion';qa.mkdir(parents=True,exist_ok=True)
 windows={'native-to-cue':timeline['long_verse_cue'][0],'reservation-to-phone':66,'phone-to-following':90,'following-to-mechanism':timeline['mechanism'][0],'mechanism-to-choice':timeline['choice_and_use'][0],'choice-to-foundation':timeline['foundation'][0],'foundation-to-close':timeline['close'][0]}
 for name,phrase,fallback in [('human_context','The Quran',7),('choice_and_use','For Hifz',5),('foundation','Our core tests',9),('mechanism','Muse Spark',8)]:
  c=next(c for c in e['clips'] if c['id']==name);words=json.loads((ROOT/c['path']).with_suffix('.words.json').read_text())['words'];wanted=canonical(phrase);relative=fallback
  for i in range(len(words)):
   if canonical(' '.join(w['word'] for w in words[i:i+len(wanted)]))==wanted:relative=words[i]['start'];break
  windows[name+'-internal-cue']=c['start']+relative
 for label,boundary in windows.items():
  start=max(0,boundary-.6);run(['ffmpeg','-v','error','-y','-ss',start,'-i',OUT,'-t','1.4','-c:v','libx264','-crf','17','-preset','veryfast','-c:a','aac',qa/(label+'.mp4')]);folder=qa/label;folder.mkdir(exist_ok=True)
  run(['ffmpeg','-v','error','-y','-ss',start,'-i',OUT,'-t','1.4','-an','-q:v','2',folder/'%03d.jpg'])
 if json.loads(MANIFEST.read_text())['scenes'][-1].get('impact_ending'):
  run(['ffmpeg','-v','error','-y','-ss',timeline['close'][0]-.6,'-i',OUT,'-c:v','libx264','-crf','17','-preset','veryfast','-c:a','aac',qa/'complete-impact-ending.mp4'])
  folder=qa/'complete-impact-ending';folder.mkdir(exist_ok=True)
  run(['ffmpeg','-v','error','-y','-ss',timeline['close'][0]-.6,'-i',OUT,'-an','-q:v','2',folder/'%03d.jpg'])
 save(qa/'windows.json',{'encoded_master':str(OUT.relative_to(ROOT)),'master_sha256':sha(OUT),'boundaries':windows,'seconds_before':.6,'seconds_after':.8,'consecutive_fps':30})
 print(json.dumps({'qa':str(qa),'windows':len(windows),'master_sha256':sha(OUT)},indent=2))

def patch_reservation():
 e=json.loads((WORK/'measured-edit.json').read_text());render_picture(e,(1800,1980))
 run(['ffmpeg','-v','error','-y','-i',WORK/'picture.mp4','-i',WORK/'patch-reservation.mp4','-filter_complex','[0:v]split=2[x][y];[x]trim=end_frame=1800,setpts=PTS-STARTPTS[a];[y]trim=start_frame=1980,setpts=PTS-STARTPTS[b];[a][1:v][b]concat=n=3:v=1:a=0[v]','-map','[v]','-c:v','libx264','-preset','veryfast','-threads','8','-crf','17','-pix_fmt','yuv420p',WORK/'corrected-picture.mp4'])
 (WORK/'corrected-picture.mp4').replace(WORK/'picture.mp4')
 run(['ffmpeg','-v','error','-y','-i',WORK/'picture.mp4','-i',WORK/'mix.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t',e['duration'],'-movflags','+faststart',OUT])

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--version',choices=('0.7','0.8'),default='0.7');parser.add_argument('--check',action='store_true');parser.add_argument('--prepare',action='store_true');parser.add_argument('--qa',action='store_true');parser.add_argument('--patch-reservation',action='store_true');parser.add_argument('--note');args=parser.parse_args()
 configure_version(args.version)
 if args.check:return check()
 if args.qa:return qa_artifacts()
 if not args.note:parser.error('Rendering or generation requires --note for spend provenance')
 WORK.mkdir(parents=True,exist_ok=True)
 if args.prepare:return prepare(args.note)
 if args.patch_reservation:return patch_reservation()
 edit=prepare(args.note);audio_track(edit);render_picture(edit);captions(edit);print(json.dumps({'output':str(OUT),'seconds':edit['duration'],'frames':edit['frames']},indent=2))
if __name__=='__main__':main()
