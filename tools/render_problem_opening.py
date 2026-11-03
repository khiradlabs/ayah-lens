#!/usr/bin/env python3
"""Reproducible local Remotion proof. Run from any directory; all paths resolve here."""
import argparse, array, hashlib, importlib.util, json, math, os, re, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'tools/problem-opening'
MEDIA=SRC/'public/media'
MASTER=ROOT/'build/video-v0.2.1/Ayah-Lens-Demo-v0.2.1.mp4'
MASTER_HASH='a23d319e234c5c71a40600cc37294572dea7666e14211b91b0c330a7572871e5'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
spec=importlib.util.spec_from_file_location('timing',SRC/'timing.py');timing=importlib.util.module_from_spec(spec);spec.loader.exec_module(timing)
OUT=ROOT/f"build/video-{timing.TIMELINE['version']}-opening"
FINAL=OUT/f"Ayah-Lens-Opening-{timing.TIMELINE['version']}.mp4"
ART_SOURCE=ROOT/'build/video-v0.4-opening/assets'
cache_spec=importlib.util.spec_from_file_location('voice_cache',SRC/'voice_cache.py');voice_cache=importlib.util.module_from_spec(cache_spec);cache_spec.loader.exec_module(voice_cache)
def run(args,**kw):
    return subprocess.run([str(a) for a in args],check=True,**kw)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def probe(p):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
def duration(p): return float(probe(p)['format']['duration'])
def pcm(path,start=0,length=8,filters=None):
    b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(path),'-t',str(length),*(['-af',filters] if filters else []),'-ar','48000','-ac','1','-f','s16le','-'])
    a=array.array('h');a.frombytes(b);return a[::8]
def correlation(a,b):
    n=min(len(a),len(b));a=a[:n];b=b[:n];ma=sum(a)/n;mb=sum(b)/n
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
def check():
    run([sys.executable,SRC/'test_timing.py'],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    assert sha(MASTER)==MASTER_HASH,'existing full master changed'
    previous=ROOT/'build/video-v0.3-opening/Ayah-Lens-Opening-v0.3.mp4'
    assert sha(previous)=='85cde1b7f662e91f553eed5f5d81c44a02cdcf9ece83622ccb134e5b8aa4ba33','previous v0.3 proof changed'
    v04=ROOT/'build/video-v0.4-opening/Ayah-Lens-Opening-v0.4.mp4'
    assert sha(v04)=='29b10f0be23cd4273603a86fb8db2b9463f3ebba1acbbecb00189394857ae4b5','previous v0.4 proof changed'
    assert timing.source_frame(timing.REPLAY_FRAME)==0 and timing.source_frame(timing.FRAMES-1)==239
    measured=json.loads((OUT/'receipts/voice-durations.json').read_text())
    windows=timing.narration_windows(measured)
    receipts={'previous_v04_unchanged_sha256':sha(v04),'previous_v03_unchanged_sha256':sha(previous),'master_unchanged_sha256':sha(MASTER),'narration_words':len(timing.NARRATION.split()),'frames':timing.FRAMES,'fps':timing.FPS,'duration_seconds':timing.DURATION,'narration_windows':windows,'replay_start_seconds':timing.REPLAY_START,'new_generation_cost_usd':0}
    for source in timing.audio_sources():
        p=ROOT/source
        assert sha(p)==sha(MEDIA/p.name),f'accepted audio copy differs: {p.name}'
        receipts[source]=sha(p)
    receipts['native_source_sha256']=sha(MEDIA/'native.mp4')
    receipts['accepted_vs_original_recitation_correlation']=correlation(pcm(MEDIA/'00.wav'),pcm(MEDIA/'native.mp4',filters='volume=20dB,highpass=f=90,lowpass=f=7000,afade=t=in:d=0.08,afade=t=out:st=7.8:d=0.2'))
    assert receipts['accepted_vs_original_recitation_correlation']>.995
    final=FINAL
    if final.exists():
        p=probe(final);v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
        assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'30/1',timing.FRAMES)
        assert (a['sample_rate'],a['channels'])==('48000',2)
        assert abs(float(v['duration'])-timing.DURATION)<.001 and abs(float(a['duration'])-timing.DURATION)<.03
        run(['ffmpeg','-v','error','-i',final,'-f','null','-'],stdout=subprocess.DEVNULL)
        receipts['output_sha256']=sha(final);receipts['video_stream']=v;receipts['audio_stream']=a;receipts['full_decode']='pass'
        receipts['opening_vs_replay_correlation']=correlation(pcm(final),pcm(final,timing.REPLAY_START))
        receipts['encoded_opening_vs_accepted_correlation']=correlation(pcm(final),pcm(MEDIA/'00.wav'))
        assert receipts['opening_vs_replay_correlation']>.995 and receipts['encoded_opening_vs_accepted_correlation']>.995
        peak=subprocess.run(['ffmpeg','-hide_banner','-i',str(final),'-af','volumedetect','-f','null','-'],capture_output=True,text=True,check=True).stderr
        (OUT/'receipts/final-audio-peak.log').write_text(peak)
        receipts['encoded_max_volume_db']=float(re.search(r'max_volume: ([-0-9.]+) dB',peak).group(1))
        assert receipts['encoded_max_volume_db']<0
    (OUT/'receipts/verification.json').write_text(json.dumps(receipts,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipts.items() if not isinstance(v,dict)},indent=2))
def prepare():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'receipts').mkdir(exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    assets=json.loads((ROOT/'submission/video-edit.json').read_text())['source_assets']
    shutil.copyfile(ROOT/assets['native'],MEDIA/'native.mp4')
    for source in timing.audio_sources(): shutil.copyfile(ROOT/source,MEDIA/Path(source).name)
    (OUT/'assets').mkdir(exist_ok=True)
    for name in ('listener-muse.png','listener-muse.receipt.json','listener-prompt.txt'):
        shutil.copyfile(ART_SOURCE/name,OUT/'assets'/name)
    shutil.copyfile(ART_SOURCE/'listener-muse.png',MEDIA/'listener-muse.png')
    (OUT/'assets/reuse.json').write_text(json.dumps({'original_generation_receipt':str(ART_SOURCE/'listener-muse.receipt.json'),'new_generation_cost_usd':0,'sha256':sha(MEDIA/'listener-muse.png')},indent=2)+'\n')
    run(['ffmpeg','-v','error','-y','-i',MEDIA/'native.mp4','-vf','crop=576:144:208:832','-frames:v','1',MEDIA/'native-crop-frame0.png'])
    sentences=timing.narration_sentences()
    def generate(path,text,voice,rate): run(['say','-v',voice,'-r',str(rate),'-o',path,text])
    measured=[]
    for i,sentence in enumerate(sentences):
        p=OUT/f'voice-{i}.aiff'
        voice_cache.ensure_voice(p,sentence,'Daniel',timing.TIMELINE['voice_rate'],generate,duration)
        measured.append(duration(p))
    (OUT/'receipts/voice-durations.json').write_text(json.dumps(measured,indent=2)+'\n')
    timing.narration_windows(measured)
    inputs=[]
    for i in range(len(sentences)): inputs+=['-i',OUT/f'voice-{i}.aiff']
    filters=[]
    for i,start in enumerate(timing.TIMELINE['narration_starts']):
        filters.append(f"[{i}:a]atempo={timing.TIMELINE['tempo']},aresample=48000,aformat=channel_layouts=stereo,adelay={round((start-8)*1000)}:all=1[a{i}]")
    filters.append(''.join(f'[a{i}]' for i in range(len(sentences)))+f'amix=inputs={len(sentences)}:normalize=0,apad,atrim=duration={timing.REPLAY_START-8}[out]')
    run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(filters),'-map','[out]','-c:a','pcm_s16le',OUT/'narration.wav'])
    run(['ffmpeg','-v','error','-y','-i',MEDIA/'00.wav','-i',OUT/'narration.wav','-i',MEDIA/'02.wav','-filter_complex','[0:a]apad,atrim=duration=8[a];[2:a]apad,atrim=duration=8[c];[a][1:a][c]concat=n=3:v=0:a=1[out]','-map','[out]','-ar','48000','-ac','2','-c:a','pcm_s16le',OUT/'audio.wav'])
    (OUT/'script.txt').write_text(f'0–8: Genuine recitation, no narration.\n\n8–{timing.REPLAY_START:g}: Temporary local Daniel guide.\n'+timing.NARRATION+f'\n\n{timing.REPLAY_START:g}–{timing.DURATION:g}: Same genuine recitation, no narration.\n')
    def stamp(t):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    caps=[(0,4.4,'Quran recitation · Just listen.'),(4.4,8,'Can you follow its meaning?')]
    caps += [(s,s+d/timing.TIMELINE['tempo'],t) for s,d,t in zip(timing.TIMELINE['narration_starts'],measured,sentences)]
    caps += [(timing.REPLAY_START,timing.DURATION,'The same words. Now with meaning.\nActual glasses display · same passage replayed')]
    (OUT/'approximate-captions.srt').write_text('\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{t}\n' for i,(a,b,t) in enumerate(caps)))
    (OUT/'viewing-notes.txt').write_text(f'REVIEW DRAFT: opening v0.5 only.\n{timing.DURATION:g} seconds, reused original Muse Image illustration plus local Remotion motion.\nApproved personal Quran translator hook is verbatim.\nBenefits are animated on measured spoken cues. Hands-free refers to automatic following after start.\nNew generation spend: $0.00. Original v0.4 artwork generation estimate: $0.01.\nNo phone concept or companion-phone inset.\nLocal Daniel temporary guide at 165 words per minute; approximate captions.\nActual source crop x208,y832,w576,h144 is unchanged and replayed at original speed.\nNative camera + display recording, not optical lens capture.\nEarlier footage does not prove Build 40 readability or overall recognition accuracy.\nStatic genuine frame0 preview appears during the final 0.8 seconds before moving replay.\nPew 2020 estimate published 2025; scale does not imply everyone needs translation.\nNo Meta website assets, app changes, new recording or publication. Earlier exports preserved.\n')

def storyboard_sheet():
    from PIL import Image,ImageDraw
    frames=sorted(int(p.stem.split('-')[-1]) for p in OUT.glob('storyboard-*.png'))
    canvas=Image.new('RGB',(1920,320*((len(frames)+3)//4)),'#F3EFE5');d=ImageDraw.Draw(canvas)
    for i,f in enumerate(frames):
        im=Image.open(OUT/f'storyboard-{f}.png').convert('RGB').resize((480,270));x=i%4*480;y=i//4*320
        canvas.paste(im,(x,y+35));d.text((x+15,y+10),f'{f/30:.1f} seconds',fill='#1A1A18')
    canvas.save(OUT/'storyboard.jpg',quality=93)
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--storyboard-only',action='store_true');args=p.parse_args()
    if args.check: check();return
    prepare();check()
    run(['node','render.mjs',*(['--storyboard-only'] if args.storyboard_only else [])],cwd=SRC,timeout=1200)
    if args.storyboard_only: storyboard_sheet();return
    run(['ffmpeg','-v','error','-y','-i',OUT/'picture.mp4','-i',OUT/'audio.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t',str(timing.DURATION),'-movflags','+faststart',FINAL])
    check()
if __name__=='__main__': main()
