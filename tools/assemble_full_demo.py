#!/usr/bin/env python3
"""Integrate the accepted v0.5 opening without moving the masjid slot.

Run normally to assemble and save private receipts. --check only reads inputs
and the existing export, prints fresh verification, and never renders media.
"""
import argparse,array,hashlib,json,math,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PLAN=json.loads((ROOT/'submission/full-video-v0.5.json').read_text())
OUT=ROOT/PLAN['output'];WORK=OUT.parent

def run(args,**kw):return subprocess.run([str(x) for x in args],check=True,**kw)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))
def source_at(t):
    for s in PLAN['segments']:
        if s['output_start']<=t<s['output_end']:
            return s['source'],s['source_start']+(t-s['output_start'])*s['speed']
    raise ValueError('Outside the full demo timeline')
def stamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
def seconds(s):
    h,m,tail=s.split(':');sec,ms=tail.split(',');return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
def parse_srt(text):
    cues=[]
    for block in re.split(r'\n\s*\n',text.strip()):
        lines=block.splitlines()
        if len(lines)<3:continue
        a,b=lines[1].split(' --> ');cues.append((seconds(a),seconds(b),'\n'.join(lines[2:])))
    return cues

def srt_text(cues):
    for i,(a,b,text) in enumerate(cues):
        if not 0<=a<b<=PLAN['duration_seconds']:raise ValueError('Caption outside timeline')
        if i and a<cues[i-1][1]:raise ValueError('Caption overlap')
    return '\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{text}\n' for i,(a,b,text) in enumerate(cues))
def merge_captions(opening,old):
    cues=list(opening)
    for a,b,text in old:
        if a<36:
            if b>36:raise ValueError('Caption crosses replacement boundary')
            continue
        if a<48:
            if b>48:raise ValueError('Caption crosses retime boundary')
            cues.append((38+(a-36)/1.2,38+(b-36)/1.2,text))
        else:cues.append((a,b,text))
    return cues

def inputs():
    found={}
    for name,entry in PLAN['inputs'].items():
        path=ROOT/entry['path'];actual=sha(path)
        assert actual==entry['sha256'],f'Input changed: {name}'
        found[name]=path
    return found

def badge_image(path):
    from PIL import Image,ImageDraw,ImageFont
    x,y,w,h=PLAN['editorial_badge']['rectangle']
    im=Image.new('RGB',(w,h),'#F3EFE5')
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',23)
    ImageDraw.Draw(im).text((10,10),PLAN['editorial_badge']['text'],font=font,fill='#69675F')
    im.save(path)

def assemble():
    paths=inputs();WORK.mkdir(parents=True,exist_ok=True);(WORK/'receipts').mkdir(exist_ok=True)
    norm='fps=30,scale=1920:1080,format=yuv420p,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709,settb=AVTB'
    anorm='aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo'
    filters=[
      f'[0:v]trim=start=0:end=38,setpts=PTS-STARTPTS,{norm}[v0]',
      '[1:v]split=2[p][t]',
      f'[p]trim=start=36:end=48,setpts=(PTS-STARTPTS)/1.2,{norm}[v1]',
      f'[t]trim=start=48:end=179.9,setpts=PTS-STARTPTS,{norm}[v2]',
      f'[0:a]atrim=start=0:end=38,asetpts=PTS-STARTPTS,{anorm}[a0]',
      '[1:a]asplit=2[pa][ta]',
      f'[pa]atrim=start=36:end=48,asetpts=PTS-STARTPTS,atempo=1.2,apad,atrim=duration=10,{anorm}[a1]',
      f'[ta]atrim=start=48:end=179.9,asetpts=PTS-STARTPTS,{anorm}[a2]',
      '[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]']
    badge=PLAN['editorial_badge'];x,y,w,h=badge['rectangle']
    badge_path=WORK/'editorial-version-badge.png';badge_image(badge_path)
    filters.append(f"[v][2:v]overlay=x={x}:y={y}:enable='gte(t,38)':shortest=1[vb]")
    with (WORK/'receipts/render.log').open('w') as log:
        run(['ffmpeg','-hide_banner','-y','-reinit_filter','0','-i',paths['opening'],'-reinit_filter','0','-i',paths['master'],'-loop','1','-framerate','30','-i',badge_path,'-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[vb]','-map','[a]','-c:v','libx264','-preset','fast','-crf','17','-threads','4','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t','179.9','-movflags','+faststart','-map_metadata','-1',OUT],stdout=log,stderr=log)
    opening=parse_srt((paths['opening'].parent/'approximate-captions.srt').read_text())
    old=parse_srt((paths['master'].parent/'guide-narration.srt').read_text())
    (WORK/'approximate-captions.srt').write_text(srt_text(merge_captions(opening,old)))
    (WORK/'assembly-manifest.json').write_text(json.dumps(PLAN,indent=2)+'\n')
    (WORK/'viewing-notes.txt').write_text('FULL VIDEO v0.5 REVIEW CUT\n179.900 seconds, under the three-minute limit.\nAccepted opening0–38; editorial product scene retimed12→10seconds at38–48; old tail48–179.9 retains original timing and speed.\nGenuine listening proof is not accelerated.\nMasjid slot remains60–90: labelled placeholder/reference fill, not completed masjid proof.\nNarration is temporary local Daniel. Captions are approximate.\nEditorial version badge is replaced only in rectangle1420,30,460,48 from38seconds onward. Source comparisons exclude exactly that rectangle.\nOriginal Muse listener artwork is reused; zero new generation spend.\nEarlier exports and source recordings remain unchanged. No app change, new recording, API call, Meta website asset or publication.\n')
    result=check();(WORK/'receipts/verification.json').write_text(json.dumps(result,indent=2)+'\n');contact_sheet();return result

def pcm(path,start,length,tempo=1):
    f=f'atrim=duration={length},asetpts=PTS-STARTPTS'+(f',atempo={tempo}' if tempo!=1 else '')
    data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(path),'-af',f,'-ar','48000','-ac','1','-f','s16le','-'])
    values=array.array('h');values.frombytes(data);return values[::8]
def corr(a,b):
    n=min(len(a),len(b));a=a[:n];b=b[:n];ma=sum(a)/n;mb=sum(b)/n
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
def frame_ssim(t,path,source_t):
    mask=''
    if t>=PLAN['editorial_badge']['start_seconds']:
        x,y,w,h=PLAN['editorial_badge']['rectangle'];mask=f',drawbox=x={x}:y={y}:w={w}:h={h}:color=black:t=fill'
    filters=f'[0:v]trim=end_frame=1,setpts=PTS-STARTPTS{mask}[a];[1:v]trim=end_frame=1,setpts=PTS-STARTPTS{mask}[b];[a][b]ssim'
    r=run(['ffmpeg','-hide_banner','-ss',t,'-i',OUT,'-ss',source_t,'-i',path,'-lavfi',filters,'-frames:v','1','-f','null','-'],capture_output=True,text=True)
    return float(re.findall(r'All:([0-9.]+)',r.stderr)[-1])
def check():
    paths=inputs();p=probe(OUT);v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'30/1',5397)
    assert (a['sample_rate'],a['channels'])==('48000',2)
    for stream in (v,a):assert abs(float(stream['duration'])-179.9)<.025 and float(stream['duration'])<=180
    r=run(['ffmpeg','-hide_banner','-i',OUT,'-af','volumedetect','-f','null','-'],capture_output=True,text=True)
    assert 'Error' not in r.stderr,'Full decode reported an error'
    peak=float(re.search(r'max_volume: ([-0-9.]+) dB',r.stderr).group(1));assert peak<0
    visuals={}
    for t in (2,17,31,37,39,43,47,49,60.5,67,89.5,93,120,170,179.5):
        name,source_t=source_at(t);visuals[str(t)]=frame_ssim(t,paths[name],source_t)
    assert min(visuals.values())>.96,f'Source video mismatch: {visuals}'
    audio={
      'opening':corr(pcm(OUT,0,38),pcm(paths['opening'],0,38)),
      'retimed_product':corr(pcm(OUT,38,10),pcm(paths['master'],36,12,1.2)),
      'tail':corr(pcm(OUT,48,131.9),pcm(paths['master'],48,131.9)),
      'masjid':corr(pcm(OUT,60,30),pcm(paths['master'],60,30))}
    assert min(audio.values())>.995,f'Audio source mismatch: {audio}'
    product=pcm(OUT,38,10);reference=pcm(paths['master'],36,12,1.2)
    speech_tail=corr(product[6*6000:int(8.6*6000)],reference[6*6000:int(8.6*6000)])
    assert speech_tail>.995,'Product narration final words changed'
    expected=merge_captions(parse_srt((paths['opening'].parent/'approximate-captions.srt').read_text()),parse_srt((paths['master'].parent/'guide-narration.srt').read_text()))
    assert (WORK/'approximate-captions.srt').read_text()==srt_text(expected),'Captions differ from source remapping'
    return {'output_sha256':sha(OUT),'duration_seconds':float(v['duration']),'audio_duration_seconds':float(a['duration']),'frames':int(v['nb_read_frames']),'resolution':[v['width'],v['height']],'fps':v['r_frame_rate'],'sample_rate':a['sample_rate'],'channels':a['channels'],'peak_dbfs':peak,'full_decode':'pass','inputs_unchanged':{n:sha(p) for n,p in paths.items()},'source_frame_ssim':visuals,'audio_correlations':audio,'product_final_words_correlation':speech_tail,'captions':'source-remapped and boundary-checked','masjid_slot':[60,90],'editorial_badge':PLAN['editorial_badge'],'new_generation_cost_usd':0}

def contact_sheet():
    from PIL import Image,ImageDraw
    qa=WORK/'qa';qa.mkdir(exist_ok=True);times=[37,37.8,38,38.5,39,42,45,47.8,48,48.5,59.5,60,60.5,65.9,66.1,89.8,90,90.5,120,150,179.5]
    sheet=Image.new('RGB',(1440,300*math.ceil(len(times)/3)),'#F3EFE5');draw=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        path=qa/f'join-{t}.png';run(['ffmpeg','-v','error','-y','-ss',t,'-i',OUT,'-frames:v','1',path])
        with Image.open(path) as im:sheet.paste(im.resize((480,270)),((i%3)*480,(i//3)*300+30))
        draw.text(((i%3)*480+12,(i//3)*300+8),f'{t:.1f} seconds',fill='black')
    sheet.save(qa/'encoded-join-contact-sheet.jpg',quality=92)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    result=check() if a.check else assemble();print(json.dumps(result,indent=2))
if __name__=='__main__':main()
