#!/usr/bin/env python3
"""Restore the accepted pictures with measured Cedar narration and three honest insert spaces.

--check is read-only: decode and inspect the existing export; never render or spend.
"""
import argparse,array,hashlib,json,math,re,subprocess,sys
from functools import lru_cache
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parent))
import editorial_motion as original
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'build/video-v0.9'; VIS=WORK/'visuals'; RECEIPTS=WORK/'receipts'
OUT=WORK/'Ayah-Lens-Demo-v0.9.mp4'; MANIFEST=WORK/'narration-manifest.json'
RESTORE=json.loads((ROOT/'submission/RESTORATION-V0.9.json').read_text())
APPROVED_OPENING=RESTORE['approved_opening']['narration']
FPS=30; W,H=1920,1080; PAPER=original.PAPER; INK=original.INK; BLUE='#465D79'; RED='#B94B37'; MUTED=original.MUTED
PIPELINE=['GLASSES AUDIO','MUSE VOICE','OUR TRACKER','PUBLISHED SOURCE','LENS']
SOURCE_FILTER='fps=30,scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709'
CACHE_LABEL='Muse Spark assists uncertain matches / paired-source plans are cached'
LIVE_LABEL='Muse Voice transcription + passage tracking run live'
OPENING_CUES=[('problem','For many who don’t understand Arabic, the sound is familiar.'),('population','Two billion Muslims, roughly a quarter of humanity.'),('impact','The potential impact is enormous: helping listeners follow the meaning of a daily recitation, without interrupting it.'),('need','We want to understand what Allah is saying. But stopping to look up the meaning takes us away from the recitation.'),('hook','What if your glasses became your personal Quran translator?'),('meaning','The meaning, right in front of your eyes.'),('following','The text follows the recitation automatically.'),('hands_free','No scrolling. No tapping. Just listen. And understand.')]
SLOTS={'tv_demo':(18,'TV FOLLOWING / AWAITING RECORDING','Let the TV reciter play. Show automatic Arabic + English updates.','ayah-tv-following'), 'long_demo':(11,'LONG VERSE / AWAITING RECORDING','73:20 stays the same. The displayed portion changes automatically.','ayah-long-verse-73-20'),'toggle_demo':(7,'ENGLISH CHOICE / AWAITING RECORDING','English off. Arabic keeps following. English returns.','ayah-english-toggle')}

def run(args,**kw):return subprocess.run([str(x) for x in args],check=True,**kw)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
def source_frame(t,start,count):return min(count-1,max(0,round((t-start)*FPS)))
def ease(t,start=0,d=.5):
 p=max(0,min(1,(t-start)/d));return p*p*(3-2*p)
def validate_narration(m):
 clips=m['clips']; ids=[c['id'] for c in clips]
 expected=['opening','product','use_cases','meta_challenge','meta_pipeline','hifz','foundation','close']
 if ids!=expected:raise ValueError('Narration IDs/order differ from production contract')
 if clips[0]['text']!=APPROVED_OPENING:raise ValueError('The approved opening changed')
 if any(not c.get('verified') for c in clips):raise ValueError('Every narration clip must be waveform-verified')
 return sum(len(c['text'].split()) for c in clips)
def layout(m):
 words=validate_narration(m); clips={c['id']:c for c in m['clips']};scenes=[];pos=0
 def add(id,kind,seconds,**kw):
  nonlocal pos
  n=math.ceil(seconds*FPS-1e-7);scenes.append(dict(id=id,kind=kind,start_frame=pos,end_frame=pos+n,start_seconds=pos/FPS,end_seconds=(pos+n)/FPS,frames=n,speed=1,**kw));pos+=n
 def voice(id):
  c=clips[id];add(id,'voice',c['duration_seconds']+.15,audio=c['path'],duration_seconds=c['duration_seconds'],text=c['text'],audio_sha256=c['sha256'])
 def slot(id):
  sec,title,desc,filename=SLOTS[id];add(id,'slot',sec,label=title,description=desc,expected_file=filename)
 add('listen','source',8,source=RESTORE['approved_opening']['path'],source_start=0)
 voice('opening');add('meaning_reveal','source',8,source=RESTORE['approved_opening']['path'],source_start=30)
 voice('product');voice('use_cases');slot('tv_demo');slot('long_demo');voice('meta_challenge');voice('meta_pipeline');voice('hifz');slot('toggle_demo');voice('foundation');voice('close')
 if pos/FPS>=180:raise ValueError(f'Measured timeline {pos/FPS:.3f}s exceeds 180-second limit; edit repetitions, never stretch voice/source')
 return {'version':'0.9','fps':FPS,'resolution':[W,H],'frames':pos,'duration_seconds':pos/FPS,'spoken_word_count':words,'scenes':scenes,'demo_slots':[s for s in scenes if s['kind']=='slot'],'narration_playback_speed':1,'source_playback_speed':1,'status':'Non-demo review cut; three recordings pending'}
def inputs():
 result={}
 for k in ('picture_master','approved_opening'):
  entry=RESTORE[k];path=ROOT/entry['path'];actual=sha(path)
  if actual!=entry['sha256']:raise ValueError(f'Approved source changed: {k}')
  result[k]={'path':entry['path'],'sha256':actual}
 for name,path in [('listener','tools/problem-opening/public/media/listener-muse.png'),('original_3d','build/video-v0.2/3d/revision-0/glasses-turntable.mp4')]:result[name]={'path':path,'sha256':sha(ROOT/path)}
 return result

def badge(im,spoken=False):
 d=ImageDraw.Draw(im);d.rectangle((1415,25,1900,81),fill=PAPER)
 original.text(d,(1430,40),'v0.9 / AI ENGLISH VOICE' if spoken else 'v0.9 / REVIEW CUT',23,color=MUTED)
 return im
@lru_cache(maxsize=1)
def art():return Image.open(ROOT/'tools/problem-opening/public/media/listener-muse.png').convert('RGB').resize((W,H))
def artbase(opacity=1):return Image.blend(Image.new('RGB',(W,H),PAPER),art(),opacity)
def txt(im,xy,content,size=80,color=INK,width=1150,bold=True):return original.text(ImageDraw.Draw(im),xy,content,size,color,bold,width=width)
def headline(im,content,size=90,color=INK,y=190,width=1150):return txt(im,(100,y),content,size,color,width)
def sound(im,t,y=870,width=950):original.wave(ImageDraw.Draw(im),105,y,t,width=width,color=BLUE,height=25)
def crossfade_paper(im,t,duration):
 p=min(ease(t,0,.16),1-ease(t,duration-.18,.18))
 return Image.blend(Image.new('RGB',(W,H),PAPER),im,p) if p<1 else im

def tokens(text):
 text=text.lower().replace("’", "").replace("'", "")
 text=re.sub(r"(?<=\d),(?=\d)", "", text)
 aliases={'2':['two'],'2000000000':['two','billion'],'6000':['six','thousand']}
 out=[]
 for token in re.findall(r'[a-z0-9]+',text):out.extend(aliases.get(token,[token]))
 return out

def phrase_starts(words,phrases,context_before=None):
 expanded=[]
 for word in words:
  expanded.extend((token,float(word['start'])) for token in tokens(word['word']))
 names=[x[0] for x in expanded];result=[];cursor=0
 for phrase in phrases:
  target=tokens(phrase);found=None
  for n in range(cursor,len(names)-len(target)+1):
   if names[n:n+len(target)]==target:found=n;break
  if found is None:raise ValueError('Cannot align waveform phrase: '+phrase)
  result.append(expanded[max(0,found-(context_before or {}).get(phrase,0))][1]);cursor=found+len(target)
 return result

def word_cues(scene):
 path=(ROOT/scene['audio']).with_suffix('.words.json')
 if not path.exists():raise ValueError('Actual waveform word timing required: '+str(path))
 words=json.loads(path.read_text())['words']
 if scene['id']=='opening':
  phrases=['For many','Two billion Muslims','The potential impact','We want to understand','your glasses became','The meaning right in front','The text follows','No scrolling']
  return phrase_starts(words,phrases,{'your glasses became':2})
 if scene['id']=='meta_pipeline':
  phrases=['The glasses capture','voice turns that audio','Our software searches','helps resolve uncertain matches','published English meaning','Readable portions reach','Our software checks','pairing plans','Transcription and passage tracking']
  return phrase_starts(words,phrases)
 return []

def opening_stage(t,duration,cues=None):
 # Only editorial pictures are retimed. Actual audio is never resampled or spliced.
 if cues:
  i=max(0,max((i for i,at in enumerate(cues) if t>=at),default=0))
  start=0 if i==0 else cues[i];end=cues[i+1] if i+1<len(cues) else duration
  return OPENING_CUES[i][0],max(0,t-start),end-start
 total=sum(len(s.split()) for _,s in OPENING_CUES);at=0
 for i,(id,text) in enumerate(OPENING_CUES):
  length=duration*len(text.split())/total
  if t<at+length or i==len(OPENING_CUES)-1:return id,t-at,length
  at+=length
 raise AssertionError

@lru_cache(maxsize=1)
def native_preview():
 return Image.open(ROOT/'tools/problem-opening/public/media/native-crop-frame0.png').convert('RGB').resize((1664,416))

def opening_art_opacity(stage,t,duration):
 if stage=='hands_free':return 1-ease(t,max(0,duration-.8),.8)
 return .45 if stage in ('population','impact') else 1

def opening_image(t,duration,cues=None,handsfree=None):
 id,local,span=opening_stage(t,duration,cues);im=artbase(opening_art_opacity(id,t,duration));d=ImageDraw.Draw(im)
 # Original opening placement and type; approved additions use the same left editorial field.
 labels={'problem':'A familiar sound. An unfamiliar language.','population':'One listener. A worldwide community.','impact':'A daily need. A global opportunity.','need':'Understanding matters.','hook':'Ayah Lens','meaning':'01 / Meaning in view','following':'02 / Follows automatically','hands_free':'03 / Hands-free following'}
 txt(im,(100,65),labels[id],25,INK,1600)
 if id=='problem':
  headline(im,'You hear the words.',101,y=200);headline(im,'Can you follow\nthe meaning?',97,RED,y=360)
  txt(im,(100,720),'For many who do not understand Arabic,\nthe recitation is familiar.',31,width=1000,bold=False);sound(im,t)
 elif id=='population':
  headline(im,'2 billion',175,y=145);headline(im,'Muslims worldwide.',66,y=365)
  for n in range(40):
   x=110+n%10*99;y=485+n//10*78;q=ease(local,n*.013,.4)
   if q:
    col=BLUE if n<10 else INK;d.ellipse((x+6,y+2,x+30,y+26),fill=col);d.rounded_rectangle((x+1,y+31,x+35,y+68),radius=9,fill=col)
  txt(im,(100,840),'Roughly one quarter of humanity.',47,BLUE)
  txt(im,(100,980),'Pew Research Center / 2020 estimate, published 2025 / 25.6%',21,width=1700,bold=False)
 elif id=='impact':
  headline(im,'The potential impact\nis enormous.',101,y=185)
  p=ease(local,.7,1.2);d.rectangle((105,452,105+900*p,461),fill=BLUE)
  headline(im,'Follow the meaning.\nStay with the recitation.',63,BLUE,y=525)
  txt(im,(100,835),'For listeners seeking English meaning',28,MUTED,bold=False)
 elif id=='need':
  headline(im,'Understand what\nAllah is saying.',97,y=195)
  headline(im,'Without stopping\nto look it up.',75,BLUE,y=505);sound(im,t)
 elif id=='hook':
  headline(im,'What if your glasses\nbecame your personal\nQuran translator?',89,y=190)
  p=ease(local,.5,.9);d.rectangle((103,517,103+855*p,522),fill=BLUE);sound(im,t)
 elif id=='meaning':
  p=ease(local,0,.7);d.line((83,177,83+1035*p,177),fill=BLUE,width=3);d.line((83,607,83+1035*p,607),fill=BLUE,width=3)
  headline(im,'The meaning.',104,y=210);headline(im,'Right in front\nof your eyes.',85,BLUE,y=370)
 elif id=='following':
  headline(im,'The text follows\nthe recitation.',100,y=205);headline(im,'Automatically.',81,BLUE,y=470)
  p=ease(local,.2,max(.4,span-.4));d.rectangle((106,650,1031,659),fill=original.RULE);d.rectangle((106,650,106+925*p,659),fill=BLUE);d.ellipse((97+925*p,645,116+925*p,664),fill=BLUE)
 else:
  p=local/max(.01,span)
  show_scroll=t<handsfree[1] if handsfree else p<.23
  show_tap=t<handsfree[2] if handsfree else p<.46
  show_understand=t>=handsfree[3] if handsfree else p>.66
  if show_scroll:headline(im,'No scrolling.',108,y=195)
  elif show_tap:headline(im,'No tapping.',108,y=195)
  else:
   headline(im,'Just listen.',113,y=175)
   if show_understand:headline(im,'And understand.',101,BLUE,y=325)
  sound(im,t)
  # Restore the approved reading-window reveal: clip the genuine first source
  # frame into the expanding viewport at its natural aspect, never squeeze words.
  q=ease(t,max(0,duration-.8),.8)
  if q:
   x=round(100+28*q);y=round(855-405*q);w=round(950+714*q);h=round(70+346*q)
   preview=native_preview().crop((0,0,w,h));im.paste(preview,(x,y));ImageDraw.Draw(im).rectangle((x,y,x+w,y+h),outline=BLUE,width=3)
 badge(im,True)
 # A short clean paper dissolve at a cue boundary avoids doubled headings.
 if id!='problem':
  opacity=ease(local,0,.12) if id=='hands_free' else min(ease(local,0,.12),1-ease(local,max(0,span-.12),.12))
  if opacity<1:im=Image.blend(Image.new('RGB',(W,H),PAPER),im,opacity)
 return im

def original_frame(identity,t,duration,product=None):
 plan={'video_version':'0.9','verified_core_tests':59,'segments':[{'start':0,'end':duration,'visual_scene':identity}]}
 im=original.keyframe(0,t,plan,product);return badge(im,True)

def challenge_image(t,duration):
 im=original.base(6,t,duration,'0.9');d=ImageDraw.Draw(im)
 original.label(d,92,135,'FIND THE PASSAGE. THEN FIND YOUR PLACE.')
 original.reveal(im,(90,205),'Over 6,000 verses.',100,t,.1,bold=True)
 p=ease(t,.7,max(1,duration*.38));selected=31
 for i in range(72):
  row,col=divmod(i,12);x=105+col*83;y=410+row*42
  active_index=int(t*14)%72 if t<duration*.4 else selected
  active=(i==active_index)
  color=BLUE if active else original.RULE
  arrival=ease(t,(i%12)*.035+(i//12)*.075,.45)
  if arrival:d.rectangle((x,y,x+58*arrival,y+15),fill=color)
  if active:d.rectangle((x-4,y-4,x+62,y+19),outline=RED,width=2)
 if t>duration*.4:
  original.moving_line(d,(1030,520),(1160,520),t,duration*.4,.8,color=RED,width=5)
  txt(im,(1200,400),'One passage.',52,width=650)
  for j in range(9):d.rectangle((1195+j*62,520,1234+j*62,540),fill=BLUE if j<6 else original.RULE)
  q=ease(t,duration*.47,max(.8,duration*.35));x=1190+q*300
  d.rectangle((x,490,x+200,570),outline=RED,width=5)
  txt(im,(1200,625),'Position inside a verse',31,BLUE,width=650,bold=False)
 txt(im,(98,795),'Repeated phrases. Partial recitation. Mid-verse entry.',37,width=1750)
 txt(im,(98,900),'Explanatory search + reading-window graphic / not simulated app output',25,MUTED,width=1750,bold=False)
 return badge(im,True)

def pipeline_image(t,duration,cues=None):
 # Original diagram's stages follow the actual waveform phrase starts.
 if cues:
  anchors=list(zip(cues,[0,4,8,10,12,17,20,23,24]))+[(duration,25)]
  a,b=next(((a,b) for a,b in zip(anchors,anchors[1:]) if a[0]<=t<b[0]),(anchors[-2],anchors[-1]))
  semantic=a[1]+(b[1]-a[1])*max(0,min(1,(t-a[0])/max(.001,b[0]-a[0])))
 else:semantic=t/duration*25
 im=original_frame(7,semantic,25);d=ImageDraw.Draw(im)
 # Replace the legacy transient assist text with a permanent concise correct scope line.
 d.rectangle((90,690,1830,986),fill=PAPER)
 if semantic>=10:
  # Branch stops above the label, so the connector cannot strike through its text.
  d.line((906,630,906,680),fill=BLUE,width=3)
  original.label(d,590,705,'MUSE SPARK / CONDITIONAL ASSIST',BLUE)
  txt(im,(590,790),'Uncertain matches + published-source pairing',29,INK,width=1150,bold=False)
  txt(im,(590,840),'Pairing plans are cached for these demonstrations.',27,MUTED,width=1150,bold=False)
 else:
  txt(im,(590,840),'Published Arabic + English supply the displayed wording.',27,MUTED,width=1150,bold=False)
 txt(im,(98,925),LIVE_LABEL,27,BLUE,width=1750,bold=False)
 return im

def slot_image(scene,t):
 duration=scene['frames']/FPS;im=original.base(5,t,duration,'0.9');d=ImageDraw.Draw(im)
 txt(im,(98,135),'DEMO INSERT / '+str({'tv_demo':'01','long_demo':'02','toggle_demo':'03'}[scene['id']]),25,RED,width=1700)
 names={'tv_demo':'Follow a reciter\non television.','long_demo':'One long verse.\nChanging portions.','toggle_demo':'Choose Arabic only.\nBring English back.'}
 headline(im,names[scene['id']],90,y=230,width=1600)
 d.rectangle((100,545,1810,755),outline=BLUE,width=3)
 txt(im,(145,585),'AWAITING RECORDING',47,BLUE,width=1600)
 txt(im,(145,665),scene['description'],30,INK,width=1550,bold=False)
 txt(im,(100,850),f"Reserved: {duration:.0f} seconds / replace with {scene['expected_file']}",28,MUTED,width=1710,bold=False)
 txt(im,(100,915),'Silent editing space. No product demonstration is shown here.',25,MUTED,width=1710,bold=False)
 return badge(im,False)

@lru_cache(maxsize=40)
def product_image(index):return Image.open(VIS/'product'/f'{index+1:04}.jpg').convert('RGB')
def picture(scene,t):
 id=scene['id'];duration=scene['frames']/FPS
 if scene['kind']=='slot':return slot_image(scene,t)
 if id=='opening':im=opening_image(t,min(duration,scene['duration_seconds']),scene.get('cue_times'),scene.get('handsfree_times'))
 elif id=='product':
  frame=product_image(min(359,round(t/max(.01,duration)*359)))
  im=original_frame(3,t/duration*12,12,frame)
 elif id=='use_cases':im=original_frame(4,t/duration*12,12)
 elif id=='meta_challenge':im=challenge_image(t,duration)
 elif id=='meta_pipeline':im=pipeline_image(t,duration,scene.get('cue_times'))
 elif id=='hifz':im=original_frame(8,t/duration*14,14)
 elif id=='foundation':
  im=original_frame(9,t/duration*16,16);d=ImageDraw.Draw(im)
  txt(im,(1290,675),'Recorded Nov 2 / software tests',23,MUTED,width=520,bold=False)
 elif id=='close':
  im=original_frame(10,t/duration*12,12);d=ImageDraw.Draw(im)
  # The old close expected a native replay inset. Keep its reading motif as explanatory type.
  d.rectangle((1190,100,1835,930),fill=PAPER)
  txt(im,(1205,230),'Potential\nimpact',62,BLUE,width=620)
  txt(im,(1205,455),'Daily meaning,\nhands free.',48,INK,width=620)
  txt(im,(1205,745),'For listeners seeking\nEnglish meaning',29,MUTED,width=620,bold=False)
  d.rectangle((90,932,1830,985),fill=PAPER)
  txt(im,(98,947),'Prototype / published source text / three demonstration recordings pending',24,MUTED,width=1720,bold=False)
 else:raise ValueError(id)
 return im if id=='opening' else crossfade_paper(im,t,duration)

def extract_product():
 folder=VIS/'product';folder.mkdir(parents=True,exist_ok=True)
 if len(list(folder.glob('*.jpg')))!=360:
  run(['ffmpeg','-v','error','-y','-i',ROOT/'build/video-v0.2/3d/revision-0/glasses-turntable.mp4','-vf','fps=30','-q:v','2',folder/'%04d.jpg'])

def render_scene(s):
 path=VIS/f"{s['id']}.mp4";frames=s['frames'];duration=frames/FPS
 if s['kind']=='source':
  run(['ffmpeg','-v','error','-y','-ss',s['source_start'],'-i',ROOT/s['source'],'-t',duration,'-an','-vf',SOURCE_FILTER,'-c:v','libx264','-preset','fast','-crf','17','-threads','3',path])
 else:
  # 30 fps generated motion, with stable underlying source and text placement.
  args=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-vf','format=yuv420p,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','fast','-crf','18','-threads','3',path]
  p=subprocess.Popen([str(x) for x in args],stdin=subprocess.PIPE)
  try:
   for i in range(frames):p.stdin.write(picture(s,i/FPS).tobytes())
  finally:p.stdin.close()
  if p.wait():raise RuntimeError('Scene encode failed: '+s['id'])
 print('Rendered',s['id'],f'{duration:.3f}s',flush=True)
 return path

def normalization_filter(frames):
 samples=frames*1600
 return f'loudnorm=I=-23:TP=-3:LRA=11,aresample=48000,asetpts=N/SR/TB,apad=whole_len={samples},atrim=end_sample={samples}'

def audio_scene(s):
 path=VIS/f"{s['id']}.wav";duration=s['frames']/FPS
 if s['kind']=='slot':args=['-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',duration]
 elif s['kind']=='source':args=['-ss',s['source_start'],'-i',ROOT/s['source'],'-t',duration]
 else:args=['-i',ROOT/s['audio'],'-af',normalization_filter(s['frames'])]
 run(['ffmpeg','-v','error','-y',*args,'-vn','-ar','48000','-ac','2','-c:a','pcm_s16le',path])
 return path

def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
def captions(edit):
 cues=[]
 for s in edit['scenes']:
  if s['kind']!='voice':continue
  sentences=re.split(r'(?<=[.!?])\s+',s['text']);total=sum(len(x.split()) for x in sentences);pos=s['start_seconds']
  for sentence in sentences:
   length=s['duration_seconds']*len(sentence.split())/total
   cues.append((pos,pos+length,sentence));pos+=length
 return '\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{text}\n' for i,(a,b,text) in enumerate(cues))

def render():
 validate_inputs=inputs();WORK.mkdir(parents=True,exist_ok=True);VIS.mkdir(exist_ok=True);RECEIPTS.mkdir(exist_ok=True)
 m=json.loads(MANIFEST.read_text());edit=layout(m);extract_product()
 for scene in edit['scenes']:
  if scene['id'] in ('opening','meta_pipeline'):scene['cue_times']=word_cues(scene)
  if scene['id']=='opening':
   words=json.loads((ROOT/scene['audio']).with_suffix('.words.json').read_text())['words']
   scene['handsfree_times']=phrase_starts(words,['No scrolling','No tapping','Just listen','And understand'])
 for s in edit['scenes']:
  if s['kind']=='voice' and sha(ROOT/s['audio'])!=s['audio_sha256']:raise ValueError('Speech changed: '+s['id'])
  render_scene(s);audio_scene(s)
 (VIS/'picture-concat.txt').write_text(''.join(f"file '{s['id']}.mp4'\n" for s in edit['scenes']))
 (VIS/'audio-concat.txt').write_text(''.join(f"file '{s['id']}.wav'\n" for s in edit['scenes']))
 run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',VIS/'picture-concat.txt','-c','copy',VIS/'picture.mp4'])
 run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',VIS/'audio-concat.txt','-c:a','pcm_s16le',VIS/'full-audio.wav'])
 run(['ffmpeg','-v','error','-y','-i',VIS/'picture.mp4','-i',VIS/'full-audio.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t',edit['duration_seconds'],'-map_metadata','-1','-movflags','+faststart',OUT])
 edit['inputs']=validate_inputs;edit['output_sha256']=sha(OUT);edit['costs_estimate_usd']=m.get('costs_estimate_usd')
 (WORK/'measured-edit.json').write_text(json.dumps(edit,indent=2)+'\n')
 (WORK/'captions.srt').write_text(captions(edit));(WORK/'spoken-script.txt').write_text('\n\n'.join(s['text'] for s in edit['scenes'] if s['kind']=='voice')+'\n')
 (WORK/'demo-slots.json').write_text(json.dumps(edit['demo_slots'],indent=2)+'\n')
 (WORK/'viewing-notes.txt').write_text('Ayah Lens v0.9 non-demo review cut. Original approved direction and B Cedar. Three silent clearly marked recording spaces await replacement. Captions are sentence-level timing estimates from actual paragraph durations. No new actual demo proof or app test is claimed. Source recitation and narration playback speed1. Final creative/naturalness review is pending.\n')
 result=check();(RECEIPTS/'verification.json').write_text(json.dumps(result,indent=2)+'\n');qa(edit);return result

def read_pcm(path,start=0,length=None):
 args=['ffmpeg','-v','error','-ss',start,'-i',path]
 if length is not None:args+=['-t',length]
 raw=subprocess.check_output([str(x) for x in [*args,'-ar','48000','-ac','1','-f','s16le','-']]);a=array.array('h');a.frombytes(raw);return a

def corr(a,b):
 n=min(len(a),len(b));a=a[:n:8];b=b[:n:8];n=len(a);ma=sum(a)/n;mb=sum(b)/n
 den=sum((x-ma)**2 for x in a)*sum((x-mb)**2 for x in b)
 return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(den) if den else 0

def audio_peak(log):
 match=re.search(r'max_volume: ([-0-9.]+) dB',log)
 if match is None:raise ValueError('No encoded audio peak report')
 return float(match.group(1))

def check():
 edit=json.loads((WORK/'measured-edit.json').read_text());m=json.loads(MANIFEST.read_text());fresh=layout(m)
 assert [(s['id'],s['frames']) for s in fresh['scenes']]==[(s['id'],s['frames']) for s in edit['scenes']]
 assert inputs()==edit['inputs'],'Approved input changed'
 assert sha(OUT)==edit['output_sha256'],'Encoded master changed after measurement'
 p=probe(OUT);v=next(x for x in p['streams'] if x['codec_type']=='video');a=next(x for x in p['streams'] if x['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(W,H,'30/1',edit['frames'])
 assert float(v['duration'])<180 and abs(float(v['duration'])-edit['duration_seconds'])<.002
 assert a['sample_rate']=='48000' and a['channels']==2 and abs(float(a['duration'])-edit['duration_seconds'])<.03
 decode=run(['ffmpeg','-hide_banner','-i',OUT,'-af','volumedetect','-f','null','-'],capture_output=True,text=True)
 assert 'Error' not in decode.stderr
 peak=audio_peak(decode.stderr);assert peak<0
 silence={};source_audio={};voice_audio={};source_video={}
 for s in edit['scenes']:
  st=s['start_seconds'];dur=s['frames']/FPS
  if s['kind']=='slot':
   pcm=read_pcm(OUT,st+.08,dur-.16);silence[s['id']]=max(abs(x) for x in pcm);assert silence[s['id']]<=2
  elif s['kind']=='source':
   source_audio[s['id']]=corr(read_pcm(OUT,st,dur),read_pcm(ROOT/s['source'],s['source_start'],dur));assert source_audio[s['id']]>.995
   scores=[]
   for offset in (.1,dur*.5,dur-.1):
    filters='[0:v]trim=end_frame=1,setpts=PTS-STARTPTS,format=gbrp[a];[1:v]trim=end_frame=1,setpts=PTS-STARTPTS,format=gbrp[b];[a][b]ssim'
    metric=run(['ffmpeg','-hide_banner','-ss',st+offset,'-i',OUT,'-ss',s['source_start']+offset,'-i',ROOT/s['source'],'-lavfi',filters,'-frames:v','1','-f','null','-'],capture_output=True,text=True)
    scores.append(float(re.findall(r'All:([0-9.]+)',metric.stderr)[-1]))
   source_video[s['id']]=scores;assert min(scores)>.97
  else:
   assert sha(ROOT/s['audio'])==s['audio_sha256'];assert next(c for c in m['clips'] if c['id']==s['id'])['verified']
   voice_audio[s['id']]=corr(read_pcm(OUT,st,dur),read_pcm(VIS/f"{s['id']}.wav"));assert voice_audio[s['id']]>.995
 assert (WORK/'captions.srt').read_text()==captions(edit)
 return {'output':str(OUT),'sha256':sha(OUT),'duration_seconds':float(v['duration']),'frames':int(v['nb_read_frames']),'resolution':[W,H],'fps':'30/1','audio_sample_rate':48000,'channels':2,'peak_dbfs':peak,'full_decode':'pass','spoken_word_count':fresh['spoken_word_count'],'waveform_verified_clips':len(m['clips']),'silent_slot_peak_pcm':silence,'source_audio_correlation':source_audio,'source_frame_ssim':source_video,'encoded_voice_correlation':voice_audio,'inputs_unchanged':edit['inputs'],'demo_slots':[{'id':s['id'],'start':s['start_seconds'],'end':s['end_seconds']} for s in edit['demo_slots']],'narration_speed':1,'source_speed':1,'captions':'sentence estimates, actual paragraph durations','new_demo_recordings':'pending'}

def qa(edit):
 folder=RECEIPTS/'qa';folder.mkdir(parents=True,exist_ok=True)
 samples=[]
 for s in edit['scenes']:
  for offset in (.35,(s['frames']/FPS)*.5,max(.1,s['frames']/FPS-.4)):
   t=s['start_seconds']+offset;name=f'{s["id"]}-{offset:.2f}.jpg';run(['ffmpeg','-v','error','-y','-ss',t,'-i',OUT,'-frames:v','1','-q:v','2',folder/name]);samples.append((s['id'],t,folder/name))
 sheet=Image.new('RGB',(4*480,math.ceil(len(samples)/4)*300),PAPER);d=ImageDraw.Draw(sheet)
 for n,(id,t,path) in enumerate(samples):
  x=n%4*480;y=n//4*300;im=Image.open(path);im.thumbnail((480,270));sheet.paste(im,(x,y));original.text(d,(x+8,y+274),f'{t:.2f}s / {id}',18,width=470)
 sheet.save(folder/'contact-sheet.jpg')
 # Consecutive encoded frames around transitions for motion/source review.
 for s in edit['scenes'][1:]:
  st=max(0,s['start_seconds']-.2);run(['ffmpeg','-v','error','-y','-ss',st,'-i',OUT,'-t','0.6','-vf','fps=10,scale=640:360','-q:v','2',folder/f'transition-{s["id"]}-%02d.jpg'])

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--storyboard',action='store_true');args=parser.parse_args()
 if args.check:print(json.dumps(check(),indent=2))
 elif args.storyboard:
  VIS.mkdir(parents=True,exist_ok=True);extract_product();p=json.loads((ROOT/'submission/narration-v0.9.json').read_text());clips=[dict(c,path='pending',duration_seconds=len(c['text'].split())/175*60,sha256='pending',verified=True) for c in p['clips']];edit=layout({'clips':clips})
  for s in edit['scenes']:
   if s['kind']!='source':picture(s,s['frames']/FPS*.55).save(VIS/f'storyboard-{s["id"]}.png')
  print('Storyboard rendered from existing art only; no API calls or audio generated.')
 else:print(json.dumps(render(),indent=2))
