#!/usr/bin/env python3
"""One continuous stage: question → source meaning → actual replay → glasses.
No paid calls. --check inspects the existing encoded sample only.
"""
import argparse,array,hashlib,json,math,re,subprocess,sys,wave
from functools import lru_cache
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageStat
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'build/continuity-proof';ASSET=WORK/'assets';OUT=WORK/'Ayah-Lens-Continuity-Proof.mp4'
FPS=30;W=1920;H=1080
PAPER='#F3EFE5';INK='#1A1A18';BLUE='#465D79';RED='#B94B37';MUTED='#69675F';RULE='#D4D0C6'
VOICE_START=22.6;VOICE_END=36.85
REPLAY_START=VOICE_END-VOICE_START+.15
REPLAY_SECONDS=10.2;NATIVE_FRAMES=round(REPLAY_SECONDS*FPS)
PRODUCT_START=REPLAY_START+REPLAY_SECONDS
FRAMES=math.ceil((PRODUCT_START+10.8+.3)*FPS);DURATION=FRAMES/FPS
MEANING_START=26.22-VOICE_START
CAPTION_Y=938
ARABIC='قُلْ هُوَ ٱللَّهُ أَحَدٌ';ENGLISH='Say: He is Allah, the One!'
BASE=ROOT/'build/video-v0.5-opening/Ayah-Lens-Opening-v0.5.mp4'
RAW_NATIVE=ROOT/'tools/problem-opening/public/media/native.mp4'
OPENING=ROOT/'build/video-v0.9/narration/opening.wav';PRODUCT=ROOT/'build/video-v0.9/narration/product.wav'
GLASSES=ROOT/'build/video-v0.2/3d/revision-0/glasses-turntable.mp4'
INPUTS=[BASE,RAW_NATIVE,OPENING,PRODUCT,GLASSES,ROOT/'App/Resources/verses.json']
CAPTIONS=[(.2,MEANING_START,'What if your glasses became your personal Quran translator?'),(MEANING_START,28.96-VOICE_START,'The meaning, right in front of your eyes.'),(28.96-VOICE_START,32.18-VOICE_START,'The text follows the recitation automatically.'),(32.18-VOICE_START,34.46-VOICE_START,'No scrolling. No tapping.'),(34.46-VOICE_START,REPLAY_START,'Just listen. And understand.'),(PRODUCT_START,PRODUCT_START+4.18,'Meet Ayah Lens: Meta Ray-Ban Display,'),(PRODUCT_START+4.18,PRODUCT_START+6.56,'Muse Voice and Muse Spark,'),(PRODUCT_START+6.56,PRODUCT_START+10.8,'bringing Quran recitation and its published English meaning into view.')]
def run(args,**kw):return subprocess.run([str(x) for x in args],check=True,**kw)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ease(t,start,duration):
 p=max(0,min(1,(t-start)/duration));return p*p*(3-2*p)
def mix(a,b,p):return tuple(x+(y-x)*p for x,y in zip(a,b))
def window_rect(t):
 small=(100,455,1120,280);large=(128,330,1664,416);end=(100,552,1000,250)
 if t<REPLAY_START:return mix(small,large,ease(t,REPLAY_START-.8,.8))
 if t<PRODUCT_START:return large
 return mix(large,end,ease(t,PRODUCT_START,1.2))
def meaning_opacity(t):return ease(t,MEANING_START-.55,.55)
def native_index(t):return min(NATIVE_FRAMES-1,max(0,round((t-REPLAY_START)*FPS)))
def caption_at(t):return next((s for a,b,s in CAPTIONS if a<=t<b),'')
@lru_cache(maxsize=50)
def font(size,bold=False):return ImageFont.truetype('/System/Library/Fonts/Supplemental/'+('Arial Bold.ttf' if bold else 'Arial.ttf'),size)
def text(im,xy,s,size=38,color=INK,bold=False,width=None):
 d=ImageDraw.Draw(im);y=xy[1]
 for para in s.split('\n'):
  words=para.split();lines=[];line=''
  for word in words:
   trial=(line+' '+word).strip()
   if line and width and d.textlength(trial,font=font(size,bold))>width:lines.append(line);line=word
   else:line=trial
  lines.append(line)
  for line in lines:
   d.text((xy[0],y),line,font=font(size,bold),fill=color);y+=size*1.17
 return y
@lru_cache(maxsize=250)
def native_frame(n):return Image.open(ASSET/'native'/f'{n+1:04}.png').convert('RGB')
@lru_cache(maxsize=30)
def glasses_frame(n):return Image.open(ASSET/'glasses'/f'{n+1:04}.jpg').convert('RGB')
@lru_cache(maxsize=1)
def arabic_image():return Image.open(ASSET/'arabic.png').convert('RGBA')
def clean_card(t):
 im=Image.new('RGB',(1120,280),'#FFFFFF');d=ImageDraw.Draw(im)
 text(im,(32,18),'112:1 / PUBLISHED SOURCE EXCERPT',21,BLUE,True)
 a=arabic_image();im.paste(a,(25,55),a)
 # Real English meaning occupies a stable readable line, not a label or abstract bar.
 if meaning_opacity(t):
  layer=Image.new('RGB',im.size,'#FFFFFF');text(layer,(36,192),ENGLISH,45,INK,True)
  # Blend only the English band; do not clear the Arabic/reference.
  box=(20,180,1100,270);im.paste(Image.blend(im.crop(box),layer.crop(box),meaning_opacity(t)),(20,180))
 else:text(im,(36,199),'Its meaning, in view.',34,MUTED)
 return im

def question_lines(t):return ["What if your glasses became your", "personal Quran translator?"]
def side_opacity(t):
 if t<PRODUCT_START:return 1-ease(t,REPLAY_START-1.8,.8)
 return ease(t,PRODUCT_START+1.2,.8)

def picture(t):
 im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
 text(im,(100,35),'CONTINUITY SAMPLE / MIDDLE OF THE APPROVED OPENING',22,MUTED)
 text(im,(1485,35),'B / AI ENGLISH VOICE',20,MUTED)
 # The same question becomes the persistent heading; it is never replaced by a blank frame.
 q=ease(t,2.9,1.0);question_size=round(72-28*q);question_y=130-45*q
 text(im,(100,question_y),'\n'.join(question_lines(t)),question_size,INK,True)
 # Original geometry enters on the same stage and remains an anchor.
 gp=ease(t,PRODUCT_START,1.2)
 gx=round(1250-180*gp);gy=round(235-40*gp);gw=round(560+230*gp);gh=round(gw*9/16)
 idx=75+round(min(1,max(0,t-PRODUCT_START)/10.8)*284) if t>=PRODUCT_START else 75
 glass=glasses_frame(idx).resize((gw,gh),Image.Resampling.LANCZOS)
 side=Image.new('RGBA',(W,H));side.paste(glass,(gx,gy))
 if t<PRODUCT_START:
  text(side,(1250,575),'The same passage.\nIts meaning stays with you.',31,BLUE,True,width=560)
  if t>=28.96-VOICE_START:text(side,(1250,694),'Follows automatically',31,INK,True,width=560);ImageDraw.Draw(side).line((1218,710,1226,718,1240,699),fill=BLUE,width=4)
  if t>=32.18-VOICE_START:text(side,(1250,750),'No scrolling',31,INK,True,width=560);ImageDraw.Draw(side).line((1218,766,1226,774,1240,755),fill=BLUE,width=4)
  if t>=33.28-VOICE_START:text(side,(1250,800),'No tapping',31,INK,True,width=560);ImageDraw.Draw(side).line((1218,816,1226,824,1240,805),fill=BLUE,width=4)
 else:
  brand=Image.new('RGBA',(W,H));bp=ease(t,PRODUCT_START+.4,.4);text(brand,(100,245-20*bp),'Ayah Lens',100,INK,True,width=1000);brand.putalpha(brand.getchannel('A').point(lambda a:round(a*bp)));im.paste(brand,(0,0),brand)
  if t>=PRODUCT_START+2.2:text(im,(105,360),'Meta Ray-Ban Display',37,BLUE,True,width=1000)
  if t>=PRODUCT_START+4.1:text(im,(105,420),'Muse Voice + Muse Spark',34,INK,width=1000)
 alpha=side.getchannel('A').point(lambda value:round(value*side_opacity(t)));side.putalpha(alpha);im.paste(side,(0,0),side)
 # One window, continuous coordinates and aspect ratio, carries exact word state.
 x,y,w,h=map(round,window_rect(t))
 if t<REPLAY_START:
  card=clean_card(t);blend=ease(t,REPLAY_START-.65,.65)
  if blend:card=Image.blend(card,native_frame(0).resize((1120,280),Image.Resampling.LANCZOS),blend)
 else:card=native_frame(native_index(t))
 im.paste(card.resize((w,h),Image.Resampling.LANCZOS),(x,y))
 d=ImageDraw.Draw(im);d.rectangle((x-3,y-3,x+w+3,y+h+3),outline=BLUE,width=3)
 if t<REPLAY_START-.65:
  text(im,(x,y+h+18),'Published Arabic excerpt + Pickthall English / explanatory view, not recorded lens pixels',22,MUTED,width=1720)
 elif t<REPLAY_START:text(im,(128,800),'The same passage moves into the actual recorded display.',27,BLUE,width=1664)
 elif t<PRODUCT_START:text(im,(128,800),'ACTUAL RECORDED DISPLAY / ORIGINAL RECITATION / 1× SPEED',24,BLUE,True,width=1664)
 else:text(im,(100,835),'Recorded display / last source frame held after replay',23,MUTED,width=1720)
 # A stable caption zone, separate from the English meaning in the source window.
 d.line((100,915,1820,915),fill=RULE,width=2)
 cap=caption_at(t)
 if cap:text(im,(100,CAPTION_Y),cap,35,INK,False,width=1720)
 elif REPLAY_START<=t<PRODUCT_START:text(im,(100,CAPTION_Y),'Original recitation / read its published meaning in the recorded display above.',27,MUTED,width=1720)
 return im

def assets():
 ASSET.mkdir(parents=True,exist_ok=True)
 corpus=json.loads((ROOT/'App/Resources/verses.json').read_text());row=next(x for x in corpus if x['id']=='112:1')
 assert ARABIC in row['arabic'] and row['translation']==ENGLISH
 for kind in ['native','glasses']:(ASSET/kind).mkdir(exist_ok=True)
 if len(list((ASSET/'native').glob('*.png')))!=NATIVE_FRAMES:
  run(['ffmpeg','-v','error','-y','-i',RAW_NATIVE,'-t',REPLAY_SECONDS,'-vf','fps=30,crop=576:144:208:832,scale=1664:416','-frames:v',NATIVE_FRAMES,ASSET/'native/%04d.png'])
 if len(list((ASSET/'glasses').glob('*.jpg')))!=360:
  run(['ffmpeg','-v','error','-y','-i',GLASSES,'-vf','fps=30','-q:v','2',ASSET/'glasses/%04d.jpg'])
 if not (ASSET/'arabic.png').exists():
  html=ASSET/'arabic.html';html.write_text('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;width:1070px;height:120px;background:transparent;overflow:hidden}div{font-family:Arial,sans-serif;font-size:78px;line-height:120px;text-align:center;color:#1A1A18;direction:rtl}</style><div>'+ARABIC+'</div>')
  log=(ASSET/'chrome-render.log').open('w')
  run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless','--disable-gpu','--no-first-run','--hide-scrollbars','--default-background-color=00000000','--user-data-dir='+str(ASSET/'chrome-profile'),'--window-size=1070,120','--screenshot='+str(ASSET/'arabic.png'),html.as_uri()],stdout=log,stderr=log)
  log.close()

def audio():
 samples=FRAMES*1600
 chain=(f'[0:a]atrim=start={VOICE_START}:end={VOICE_END},asetpts=PTS-STARTPTS,loudnorm=I=-23:TP=-3:LRA=11,aresample=48000,asetpts=N/SR/TB,apad=whole_len={round(REPLAY_START*48000)},atrim=end_sample={round(REPLAY_START*48000)}[a];'
 f'[1:a]atrim=start=0:end={REPLAY_SECONDS},asetpts=PTS-STARTPTS,volume=16.4dB,aresample=48000,asetpts=N/SR/TB[b];'
 f'[2:a]loudnorm=I=-23:TP=-3:LRA=11,aresample=48000,asetpts=N/SR/TB,apad=whole_len={samples-round(PRODUCT_START*48000)},atrim=end_sample={samples-round(PRODUCT_START*48000)}[c];'
 '[a][b][c]concat=n=3:v=0:a=1[out]')
 run(['ffmpeg','-v','error','-y','-i',OPENING,'-i',RAW_NATIVE,'-i',PRODUCT,'-filter_complex',chain,'-map','[out]','-ar','48000','-ac','2','-c:a','pcm_s16le',WORK/'audio.wav'])
def render():
 assets();before={str(x.relative_to(ROOT)):sha(x) for x in INPUTS}
 picturefile=WORK/'picture.mp4'
 args=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',FPS,'-i','-','-an','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','fast','-crf','17','-threads','3',picturefile]
 p=subprocess.Popen([str(x) for x in args],stdin=subprocess.PIPE)
 try:
  for frame in range(FRAMES):p.stdin.write(picture(frame/FPS).tobytes())
 finally:p.stdin.close()
 if p.wait():raise RuntimeError('Picture encode failed')
 audio()
 run(['ffmpeg','-v','error','-y','-i',picturefile,'-i',WORK/'audio.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-t',DURATION,'-movflags','+faststart',OUT])
 assert before=={str(x.relative_to(ROOT)):sha(x) for x in INPUTS}
 manifest={'output':str(OUT.relative_to(ROOT)),'sha256':sha(OUT),'duration_seconds':DURATION,'frames':FRAMES,'voice_source_bounds':[VOICE_START,VOICE_END],'replay_start':REPLAY_START,'replay_seconds':REPLAY_SECONDS,'recitation_gain_db':16.4,'natural_source_quiet_from':9.967234,'product_start':PRODUCT_START,'published_reference':'112:1','arabic_excerpt':ARABIC,'published_english':ENGLISH,'translation_visible_from':MEANING_START,'captions_burned_in':True,'continuous_canvas':True,'new_generation_cost_usd':0,'inputs':before,'scope':'Middle-of-approved-opening continuity sample, not replacement full script'}
 (WORK/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
 qa();result=check();(WORK/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

def pcm(path,start=0,length=None):
 args=['ffmpeg','-v','error','-ss',start,'-i',path]
 if length is not None:args+=['-t',length]
 raw=subprocess.check_output([str(x) for x in args+['-ar','48000','-ac','1','-f','s16le','-']]);a=array.array('h');a.frombytes(raw);return a

def correlation(a,b):
 a=a[::8];b=b[::8];n=min(len(a),len(b));a=a[:n];b=b[:n];ma=sum(a)/n;mb=sum(b)/n
 return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
def check():
 m=json.loads((WORK/'manifest.json').read_text());assert sha(OUT)==m['sha256']
 p=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(OUT)]))
 v=next(x for x in p['streams'] if x['codec_type']=='video');a=next(x for x in p['streams'] if x['codec_type']=='audio')
 assert (v['width'],v['height'],int(v['nb_read_frames']))==(W,H,FRAMES)
 assert abs(float(v['duration'])-DURATION)<.002 and abs(float(a['duration'])-DURATION)<.03
 r=run(['ffmpeg','-hide_banner','-i',OUT,'-af','volumedetect','-f','null','-'],capture_output=True,text=True)
 peak=float(re.search(r'max_volume: ([-0-9.]+) dB',r.stderr).group(1));assert peak<0
 c=correlation(pcm(OUT),pcm(WORK/'audio.wav'));assert c>.999
 actual_recitation=pcm(OUT,REPLAY_START,REPLAY_SECONDS);gain=10**(16.4/20);expected_recitation=array.array('h',(round(x*gain) for x in pcm(RAW_NATIVE,0,REPLAY_SECONDS)));rec=correlation(actual_recitation,expected_recitation);assert rec>.995
 n=min(len(actual_recitation),len(expected_recitation));gain_ratio=math.sqrt(sum(x*x for x in actual_recitation[:n])/sum(x*x for x in expected_recitation[:n]));assert .98<gain_ratio<1.02
 for path,hash in m['inputs'].items():assert sha(ROOT/path)==hash
 return dict(output=str(OUT),sha256=m['sha256'],duration_seconds=DURATION,frames=FRAMES,full_decode='pass',peak_dbfs=peak,encoded_audio_correlation=c,original_recitation_correlation=rec,recitation_gain_db=16.4,gain_adjusted_rms_ratio=gain_ratio,source_pair='112:1 exact published excerpt',captions='burned into exported frames',inputs_unchanged=True,new_cost_usd=0)
def qa():
 folder=WORK/'qa';folder.mkdir(exist_ok=True)
 times=[0,1,3.4,4,6.5,9.7,12,13.8,REPLAY_START,REPLAY_START+4,REPLAY_START+7.8,PRODUCT_START,PRODUCT_START+.5,PRODUCT_START+1.2,PRODUCT_START+4,PRODUCT_START+9,DURATION-.2]
 sheet=Image.new('RGB',(4*480,math.ceil(len(times)/4)*300),PAPER)
 for n,t in enumerate(times):
  path=folder/f'frame-{t:.2f}.jpg';run(['ffmpeg','-v','error','-y','-ss',t,'-i',OUT,'-frames:v','1','-q:v','2',path]);im=Image.open(path);im.thumbnail((480,270));x=n%4*480;y=n//4*300;sheet.paste(im,(x,y));text(sheet,(x+6,y+274),f'{t:.2f} seconds',18)
 sheet.save(folder/'chronological.jpg')
 for label,t in [('meaning',MEANING_START),('replay',REPLAY_START),('product',PRODUCT_START)]:
  run(['ffmpeg','-v','error','-y','-ss',max(0,t-.6),'-i',OUT,'-t','1.8','-vf','fps=10,scale=960:540',folder/f'{label}-%02d.png'])
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 if args.check:print(json.dumps(check(),indent=2))
 else:render()
