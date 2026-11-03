#!/usr/bin/env python3
"""Reproducible local Remotion proof. Run from any directory; all paths resolve here."""
import argparse, array, hashlib, importlib.util, json, math, os, re, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'tools/problem-opening'
OUT=ROOT/'build/video-v0.3-opening'
MEDIA=SRC/'public/media'
MASTER=ROOT/'build/video-v0.2.1/Ayah-Lens-Demo-v0.2.1.mp4'
MASTER_HASH='a23d319e234c5c71a40600cc37294572dea7666e14211b91b0c330a7572871e5'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
spec=importlib.util.spec_from_file_location('timing',SRC/'timing.py');timing=importlib.util.module_from_spec(spec);spec.loader.exec_module(timing)
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
    assert timing.source_frame(840)==0 and timing.source_frame(1079)==239
    assert all(s+d/1.03<=28 for s,d in zip(timing.TIMELINE['narration_starts'],timing.TIMELINE['narration_durations']))
    receipts={'master_unchanged_sha256':sha(MASTER),'narration_words':len(timing.NARRATION.split()),'frames':1080,'fps':30}
    for source in timing.audio_sources():
        p=ROOT/source
        assert sha(p)==sha(MEDIA/p.name),f'accepted audio copy differs: {p.name}'
        receipts[source]=sha(p)
    receipts['native_source_sha256']=sha(MEDIA/'native.mp4')
    receipts['accepted_vs_original_recitation_correlation']=correlation(pcm(MEDIA/'00.wav'),pcm(MEDIA/'native.mp4',filters='volume=20dB,highpass=f=90,lowpass=f=7000,afade=t=in:d=0.08,afade=t=out:st=7.8:d=0.2'))
    assert receipts['accepted_vs_original_recitation_correlation']>.995
    final=OUT/'Ayah-Lens-Opening-v0.3.mp4'
    if final.exists():
        p=probe(final);v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
        assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'30/1',1080)
        assert (a['sample_rate'],a['channels'])==('48000',2)
        assert abs(float(v['duration'])-36)<.001 and abs(float(a['duration'])-36)<.03
        run(['ffmpeg','-v','error','-i',final,'-f','null','-'],stdout=subprocess.DEVNULL)
        receipts['output_sha256']=sha(final);receipts['video_stream']=v;receipts['audio_stream']=a;receipts['full_decode']='pass'
        receipts['opening_vs_replay_correlation']=correlation(pcm(final),pcm(final,28))
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
    sentences=timing.NARRATION.split('. ')
    def generate(path,text,voice,rate): run(['say','-v',voice,'-r',str(rate),'-o',path,text])
    measured=[]
    for i,sentence in enumerate(sentences):
        p=OUT/f'voice-{i}.aiff'
        voice_cache.ensure_voice(p,sentence.rstrip('.')+'.','Daniel',150,generate,duration)
        measured.append(duration(p))
    (OUT/'receipts/voice-durations.json').write_text(json.dumps(measured,indent=2)+'\n')
    assert all(s+d/1.03<=28 for s,d in zip(timing.TIMELINE['narration_starts'],measured)),'measured voice does not fit the narration phase'
    inputs=[]
    for i in range(5): inputs+=['-i',OUT/f'voice-{i}.aiff']
    filters=[]
    for i,start in enumerate(timing.TIMELINE['narration_starts']):
        filters.append(f'[{i}:a]atempo=1.03,aresample=48000,aformat=channel_layouts=stereo,adelay={round((start-8)*1000)}:all=1[a{i}]')
    filters.append(''.join(f'[a{i}]' for i in range(5))+'amix=inputs=5:normalize=0,apad,atrim=duration=20[out]')
    run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(filters),'-map','[out]','-c:a','pcm_s16le',OUT/'narration.wav'])
    run(['ffmpeg','-v','error','-y','-i',MEDIA/'00.wav','-i',OUT/'narration.wav','-i',MEDIA/'02.wav','-filter_complex','[0:a]apad,atrim=duration=8[a];[2:a]apad,atrim=duration=8[c];[a][1:a][c]concat=n=3:v=0:a=1[out]','-map','[out]','-ar','48000','-ac','2','-c:a','pcm_s16le',OUT/'audio.wav'])
    (OUT/'script.txt').write_text('0–8: Genuine recitation, no narration.\n\n8–28: Temporary local Daniel guide.\n'+timing.NARRATION+'\n\n28–36: Same genuine recitation, no narration.\n')
    def stamp(t):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    caps=[(0,4.4,'Quran recitation · Just listen.'),(4.4,8,'Can you follow its meaning?')]
    caps += [(s,s+d/1.03,t.rstrip('.')+'.') for s,d,t in zip(timing.TIMELINE['narration_starts'],measured,sentences)]
    caps += [(28,36,'The same words. Now with meaning.\nActual glasses display · same passage replayed')]
    (OUT/'approximate-captions.srt').write_text('\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{t}\n' for i,(a,b,t) in enumerate(caps)))
    (OUT/'viewing-notes.txt').write_text('REVIEW DRAFT: opening v0.3 only.\n36 seconds, local Remotion/React and original SVG illustration.\nNo music or new sound effects.\nLocal Daniel temporary narration; approximate captions.\nFirst and last eight seconds reuse accepted genuine recitation WAVs.\nLast scene replays source frames0–239, enlarged crop and native camera/display composite in sync.\nEarlier prototype footage does not prove Build40 readability or recognition accuracy.\nConcept phone is an original illustration, not app output.\nPopulation figure is supporting context, not a count of people needing translation.\nNo Meta website assets, paid services, app changes, new recording or publication.\nFull v0.2.1 master preserved.\nInspect question, lived problem, phone gaze shift, immediate replay answer.\n')
def storyboard_sheet():
    from PIL import Image,ImageDraw
    frames=[30,150,285,390,585,720,795,930]
    canvas=Image.new('RGB',(1920,640),'#F3EFE5');d=ImageDraw.Draw(canvas)
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
    run(['ffmpeg','-v','error','-y','-i',OUT/'picture.mp4','-i',OUT/'audio.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t','36','-movflags','+faststart',OUT/'Ayah-Lens-Opening-v0.3.mp4'])
    check()
if __name__=='__main__': main()
