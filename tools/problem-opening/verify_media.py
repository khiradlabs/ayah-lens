#!/usr/bin/env python3
"""Verify encoded source-crop correspondence and Muse-art usage for opening v0.5."""
import hashlib,json,re,subprocess
from pathlib import Path
from PIL import Image,ImageFilter
import timing
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/f"build/video-{timing.TIMELINE['version']}-opening";MEDIA=ROOT/'tools/problem-opening/public/media'
def frame(source,t,out,filter=None):
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(source),*(['-vf',filter] if filter else []),'-frames:v','1',str(out)],check=True)
def ssim(a,b):
    r=subprocess.run(['ffmpeg','-v','info','-i',str(a),'-i',str(b),'-lavfi','ssim','-f','null','-'],capture_output=True,text=True,check=True)
    return float(re.findall(r'All:([0-9.]+)',r.stderr)[-1])
def main():
    qa=OUT/'qa';qa.mkdir(exist_ok=True);movie=OUT/f"Ayah-Lens-Opening-{timing.TIMELINE['version']}.mp4";results={}
    for t in (timing.REPLAY_START+1,timing.REPLAY_START+3,timing.REPLAY_START+7):
        a=qa/f'encoded-crop-{t}.png';b=qa/f'source-crop-{t}.png'
        frame(movie,t,a,'crop=1664:416:128:450');frame(MEDIA/'native.mp4',t-timing.REPLAY_START,b,'crop=576:144:208:832,scale=1664:416')
        results[str(t)]=ssim(a,b)
    assert min(results.values())>.94,'encoded display no longer corresponds to original crop'
    # A textured face/coat patch checks actual visual use of the supplied Muse file.
    a=qa/'encoded-art-patch.png';b=qa/'muse-art-patch.png'
    frame(movie,2,a,'crop=260:380:1380:380')
    frame(MEDIA/'listener-muse.png',0,b,'scale=1920:1080,crop=260:380:1380:380')
    # Four-pixel blur tolerates the intentional subpixel scale/parallax animation.
    for p in (a,b):
        with Image.open(p) as im:im.filter(ImageFilter.GaussianBlur(4)).save(p.with_stem(p.stem+'-coarse'))
    art_ssim=ssim(a.with_stem(a.stem+'-coarse'),b.with_stem(b.stem+'-coarse'));assert art_ssim>.90,'Muse artwork not present in encoded scene'
    original=json.loads((OUT/'assets/listener-muse.receipt.json').read_text())
    assert original['sha256']==hashlib.sha256((MEDIA/'listener-muse.png').read_bytes()).hexdigest(),'render art differs from API receipt'
    frames=sorted(set([0,132]+[round(t*timing.FPS)+15 for t in timing.TIMELINE['narration_starts']]+[timing.REPLAY_FRAME-30,timing.REPLAY_FRAME-24,timing.REPLAY_FRAME-10,timing.REPLAY_FRAME-1,timing.REPLAY_FRAME,timing.REPLAY_FRAME+30,timing.REPLAY_FRAME+210]))
    sheet=Image.new('RGB',(1440,300*((len(frames)+2)//3)),'#F3EFE5')
    from PIL import ImageDraw
    draw=ImageDraw.Draw(sheet)
    for i,f in enumerate(frames):
        p=qa/f'decoded-{f}.png';frame(movie,f/30,p)
        with Image.open(p) as im:sheet.paste(im.resize((480,270)),((i%3)*480,(i//3)*300+30))
        draw.text(((i%3)*480+12,(i//3)*300+8),f'{f/30:.3f} seconds',fill='black')
    sheet.save(qa/'decoded-transition-sheet.jpg',quality=92)
    result={'crop_ssim':results,'encoded_muse_art_patch_coarse_ssim':art_ssim,'art_patch_comparison_blur_pixels':4,'new_generation_cost_usd':0,'replay_start_seconds':timing.REPLAY_START,'muse_asset_sha256':hashlib.sha256((MEDIA/'listener-muse.png').read_bytes()).hexdigest(),'decoded_frames':frames,'note':'Crop pixel correspondence and artwork use only; not optical display or recognition accuracy.'}
    (qa/'media-correspondence.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
