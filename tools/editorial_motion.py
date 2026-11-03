#!/usr/bin/env python3
"""Render local editorial motion bases. All generated files stay under build/video-v0.2."""
import argparse
from functools import lru_cache
import json
import math
from pathlib import Path
import subprocess
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/video-v0.2'
W, H, FPS = 1920, 1080, 30
PAPER, INK, RED, BLUE, YELLOW = '#F3EFE5', '#1A1A18', '#D34B38', '#53749B', '#EDC84B'
MUTED, RULE = '#69675F', '#D4D0C6'
FONTROOT = Path('/System/Library/Fonts/Supplemental')


def load_plan():
    return json.loads((ROOT / 'submission/video-edit.json').read_text())


def population_count(t):
    return max(0, min(25, int((t - 3) / 7 * 25)))


def pipeline_stage(t):
    return sum(t >= boundary for boundary in (4, 8, 12, 17))


def ease(t, start=0, duration=1):
    v = max(0., min(1., (t-start)/duration))
    return v*v*(3-2*v)


@lru_cache(maxsize=64)
def font(size, bold=False, serif=False):
    filename = 'Times New Roman Italic.ttf' if serif else ('Arial Bold.ttf' if bold else 'Arial.ttf')
    return ImageFont.truetype(str(FONTROOT / filename), size)


def text(d, xy, content, size=38, color=INK, bold=False, serif=False, width=None, gap=1.12):
    x, y = xy
    f = font(size, bold, serif)
    for paragraph in content.split('\n'):
        lines, line = [], ''
        for word in paragraph.split():
            trial = f'{line} {word}'.strip()
            if width and d.textlength(trial, font=f) > width and line:
                lines.append(line)
                line = word
            else:
                line = trial
        lines.append(line)
        for line in lines:
            if width:
                assert d.textlength(line, font=f) <= width+2, f'Text overflows: {line}'
            d.text((round(x), round(y)), line, font=f, fill=color)
            y += size*gap
    return y


def reveal(img, xy, content, size, t, start=0, width=None, color=INK, bold=False, serif=False):
    """A clipped vertical typesetting reveal, rather than fading a completed slide."""
    if t <= start:
        return
    layer = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(layer)
    p = ease(t, start, .85)
    text(d, (xy[0], xy[1]+(1-p)*size*.55), content, size, color, bold, serif, width)
    mask = Image.new('L', (W,H))
    ImageDraw.Draw(mask).rectangle((xy[0]-2, xy[1], W, H), fill=255)
    layer.putalpha(ImageChops.multiply(layer.getchannel('A'),mask))
    img.paste(layer, (0,0), layer)


def arrow(d, a, b, color=INK, width=3):
    d.line((a,b), fill=color, width=width)
    ang = math.atan2(b[1]-a[1],b[0]-a[0])
    d.polygon([b]+[(b[0]-13*math.cos(ang+q),b[1]-13*math.sin(ang+q)) for q in (-.45,.45)],fill=color)


def moving_line(d, a, b, t, start, duration, color=RED, width=5):
    p = ease(t,start,duration)
    end = (a[0]+(b[0]-a[0])*p,a[1]+(b[1]-a[1])*p)
    if p:
        d.line((a,end),fill=color,width=width)


def wave(d, x, y, t, width=550, color=RED, height=70, speed=1):
    for n in range(int(width/16)):
        # A travelling amplitude envelope explains incoming sound; not measured audio.
        env = .25+.75*(.5+.5*math.sin(n*.32-t*speed*2))
        h = 5+height*env*(.45+.55*abs(math.sin(n*1.7+t*speed)))
        d.line((x+n*16,y-h,x+n*16,y+h), fill=color,width=5)


def base(index,t,duration,background=None):
    img = background.copy().convert('RGB') if background else Image.new('RGB',(W,H),PAPER)
    d = ImageDraw.Draw(img)
    text(d,(90,40),'AYAH LENS',24,bold=True)
    text(d,(1430,40),'VIDEO v0.2 / GUIDE VOICE',23,color=MUTED)
    d.line((90,88,1830,88),fill=INK,width=2)
    d.line((90,1014,1830,1014),fill=RULE,width=2)
    d.line((90,1014,90+1740*max(0,min(1,t/duration)),1014),fill=RED,width=3)
    text(d,(90,1032),'HEAR THE RECITATION. FOLLOW THE MEANING.',19,color=MUTED)
    text(d,(1770,1030),f'{index+1:02}',22,color=MUTED)
    return img


def label(d, x, y, content, color=RED):
    text(d,(x,y),content,23,color,bold=True)


@lru_cache(maxsize=1)
def source_example():
    return next(v for v in json.loads((ROOT/'App/Resources/verses.json').read_text()) if v['id']=='1:3')


def population(img,t):
    d = ImageDraw.Draw(img)
    label(d,92,130,'A QUESTION OF SCALE')
    reveal(img,(90,190),'About 2 billion',112,t,0,bold=True)
    reveal(img,(95,322),'Muslims worldwide.',57,t,.6)
    # 100 flat marks arrive, then 25 are selected. They regroup into four equal columns.
    regroup = ease(t,10.5,3)
    count = population_count(t)
    for n in range(100):
        oldx,oldy = 1040+(n%10)*68, 190+(n//10)*54
        group=n//25
        newx,newy=1035+group*192+(n%5)*29, 270+(n%25//5)*64
        x=oldx+(newx-oldx)*regroup
        y=oldy+(newy-oldy)*regroup
        arrival=ease(t,.8+n*.012,.55)
        fill=RED if n<count else RULE
        if arrival:
            d.rectangle((x,y+23*(1-arrival),x+44-19*regroup,y+30+23*(1-arrival)),fill=fill)
    if t>5:
        reveal(img,(96,460),'About one quarter',74,t,5,bold=True,width=900)
        reveal(img,(98,550),'of the world’s population.',45,t,5.6,width=850)
        moving_line(d,(98,640),(900,640),t,6.5,2,color=RED,width=8)
    if t>11:
        reveal(img,(1035,665),'1 in 4',100,t,11,bold=True)
        reveal(img,(1040,785),'25 of 100 shown for comparison',29,t,12,color=MUTED)
    reveal(img,(98,730),'A population estimate.\nNot a measure of who needs this product.',30,t,14,width=840,color=MUTED)
    text(d,(98,902),'Pew Research Center / 2020 estimate, published 2025',25,color=MUTED)
    text(d,(98,945),'Underlying estimate: 25.6% / comparison rounded to one quarter',25,color=MUTED)


def technical(img,t):
    d=ImageDraw.Draw(img)
    label(d,92,130,'FOLLOW ONE PIECE OF RECITATION EVIDENCE')
    reveal(img,(90,179),'From sound to source.',90,t,0,bold=True)
    xs=[92,440,788,1136,1484]
    stage=pipeline_stage(t)
    stage_starts=[0,4,8,12,17]
    titles=['GLASSES AUDIO','MUSE VOICE','LOCAL MATCHER','PUBLISHED SOURCE','LENS']
    sub=['Recitation captured','Arabic transcript','Passage + portion','Arabic + Pickthall','Current source window']
    # A connected causal rail. Evidence travels between concrete representations.
    y=435
    for n,x in enumerate(xs):
        introduced=ease(t,stage_starts[n],.65)
        col=INK if n<=stage else RULE
        text(d,(x,328),f'{n+1:02}',25,color=RED if n==stage else MUTED,bold=True)
        if n<4:
            d.line((x+252,y,x+330,y),fill=RULE,width=3)
            moving_line(d,(x+252,y),(x+330,y),t,stage_starts[n+1]-1.4,1.4,color=RED)
        # No dashboard cards: separate unboxed technical representations.
        if n==0:
            wave(d,x+12,y,t,width=218,color=col,height=50,speed=.8)
        elif n==1:
            for row in range(4):
                span=[211,175,224,142][row]*introduced
                d.rectangle((x+8,y-55+row*30,x+8+span,y-43+row*30),fill=col)
        elif n==2:
            d.line((x+13,y-75,x,y-75,x,y+75,x+13,y+75),fill=col,width=4)
            d.line((x+220,y-75,x+233,y-75,x+233,y+75,x+220,y+75),fill=col,width=4)
            for j in range(8):
                d.rectangle((x+25+j*23,y-10,x+41+j*23,y+10),fill=BLUE if j<=min(7,int(max(0,t-8)*.8)) else RULE)
            if stage==2:
                pos=(t-8)/9
                d.rectangle((x+22+min(.99,pos)*180,y-26,x+43+min(.99,pos)*180,y+26),outline=RED,width=4)
        elif n==3:
            for z in (12,0):
                d.rectangle((x+22+z,y-80-z,x+204+z,y+80-z),outline=col,width=3)
            for j in range(5):
                d.line((x+44,y-50+j*26,x+185,y-50+j*26),fill=BLUE if j<2 and n<=stage else col,width=6)
        else:
            # A lens-window section, explicitly explanatory.
            d.polygon([(x+3,y-67),(x+235,y-67),(x+215,y+68),(x+24,y+68)],outline=col,width=5)
            if n<=stage:
                for j,length in enumerate((156,170,126)):
                    d.rectangle((x+40,y-32+j*30,x+40+length*ease(t,17+j*.35,1),y-24+j*30),fill=BLUE)
        text(d,(x,550),titles[n],26,color=col,bold=True)
        text(d,(x,592),sub[n],23,color=col,width=300)
    # Highlight travels with a single evidence packet, then settles on the output.
    if t>=1:
        points=[(x+115,650) for x in xs]
        rail=min(4,max(0,(t-2)/4))
        a=min(3,int(rail));p=rail-a if rail<4 else 1
        px=points[a][0]+(points[a+1][0]-points[a][0])*p
        d.line((207,650,1599,650),fill=RULE,width=2)
        d.rectangle((px-11,639,px+11,661),fill=RED)
        label(d,92,850,['CAPTURE','TRANSCRIBE','LOCATE + TRACK','VALIDATE SOURCE','SEND THE PORTION'][stage])
    details=[
        'Glasses microphone → recitation audio',
        'Muse Voice converts the audio into an Arabic partial transcript.',
        'Local software locates the canonical passage and tracks source-word position.',
        'Displayed wording is read from published sources, never generated translation.',
        'Only the current validated source portion is sent to the lens.'
    ]
    text(d,(92,890),details[stage],31,width=1710)
    # Conditional assist branch opens under the local matching stage, then returns.
    if 9<=t<19:
        d.line((906,630,906,755,570,755),fill=BLUE,width=3)
        text(d,(590,712),'MUSE SPARK · WHEN NEEDED',25,color=BLUE,bold=True)
        text(d,(590,783),'Bounded ambiguity / paired-source plans / Validated source plans are cached.',25,color=MUTED)
        arrow(d,(906,755),(1110,755),BLUE)
        text(d,(1135,735),'Validate + cache',24,color=BLUE)
        moving_line(d,(906,630),(906,755),t,9,2,color=BLUE)
        if 10<t<16:
            q=((t-10)/6)%1
            xx=570+(906-570)*q
            d.rectangle((xx-8,747,xx+8,763),fill=BLUE)
    if t>=19:
        # A source excerpt, loaded verbatim rather than restated as model output.
        d.rectangle((90,700,1830,986),fill=PAPER)
        label(d,92,740,'SEND THE PORTION')
        text(d,(92,785),details[stage],31,width=1710)
        text(d,(92,858),'SOURCE EXAMPLE / 1:3 / PICKTHALL',22,color=BLUE,bold=True)
        text(d,(92,903),source_example()['translation'],40,serif=True)
        text(d,(1095,912),'Spark assists conditionally; cached plans are reused.',24,color=MUTED,width=720)


def keyframe(index,t,plan=None,product_frame=None):
    """Return a 1920×1080 PIL RGB frame at scene-local seconds. No source-footage overlay."""
    plan=plan or load_plan()
    duration=plan['segments'][index]['end']-plan['segments'][index]['start']
    t=max(0,min(float(t),duration-1/FPS))
    img=base(index,t,duration,product_frame if index==3 else None)
    d=ImageDraw.Draw(img)
    if index==0:
        reveal(img,(90,230),'Just listen.',168,t,.15,bold=True)
        wave(d,98,635,t,width=1380,height=65)
        reveal(img,(98,845),'The recitation comes first.',38,t,2.7,serif=True)
        text(d,(98,934),'Actual source audio / waveform is an explanatory graphic',23,color=MUTED)
    elif index==1:
        label(d,92,135,'THE SAME RECITATION, REPLAYED')
        reveal(img,(90,215),'Now follow\nthe meaning.',99,t,.1,bold=True,width=1000)
        moving_line(d,(92,486),(1050,486),t,.5,2,color=RED,width=7)
        text(d,(92,805),'Enlarged display from the same recording',28,color=MUTED)
        text(d,(1185,108),'Native glasses recording',26,color=RED)
        reveal(img,(92,876),'Same words. Meaning in view.',39,t,3,serif=True)
        text(d,(92,950),'Footage predates Build 40 typography.',23,color=MUTED)
    elif index==2:
        population(img,t)
    elif index==3:
        label(d,92,140,'MEET')
        reveal(img,(90,219),'Ayah\nLens',133,t,.1,bold=True,width=650)
        moving_line(d,(98,575),(700,575),t,1.2,2,color=RED,width=8)
        for j,s in enumerate(['Meta glasses','Muse Voice','Muse Spark']):
            reveal(img,(98,635+j*76),s,44,t,2+j*1.4,bold=j==0)
        text(d,(98,936),'3D illustration / original geometry, not official CAD',24,color=MUTED)
        if product_frame is None:
            text(d,(1090,900),'3D product turntable composites here',24,color=MUTED)
    elif index==4:
        label(d,92,133,'ONE LISTENING EXPERIENCE')
        reveal(img,(90,192),'Meaning, in the moment.',88,t,.2,bold=True)
        # Two settings share a moving sound rail and a common listening destination.
        for x,title,subtitle in [(98,'PRAYER LISTENING','A possible use during Salat'),(1030,'AT HOME','Follow a reciter on television')]:
            text(d,(x,625),title,36,bold=True)
            text(d,(x,690),subtitle,31,color=MUTED)
        d.arc((255,350,660,655),180,360,fill=INK,width=6)
        d.line((255,503,255,555),fill=INK,width=6)
        d.line((660,503,660,555),fill=INK,width=6)
        d.rectangle((1195,365,1640,585),outline=INK,width=6)
        d.line((1305,610,1530,610),fill=INK,width=6)
        for x in (112,1050):
            wave(d,x,470,t,width=110,height=30,color=BLUE)
        moving_line(d,(98,770),(1810,770),t,2,6,color=RED,width=5)
        text(d,(98,843),'Technology demonstration only.',31,bold=True)
        text(d,(98,894),'This does not establish religious permissibility for use during prayer.',31,width=1720)
    elif index==5:
        label(d,92,136,'MASJID RECORDING / RESERVED')
        reveal(img,(90,220),'The live\nlistening test.',91,t,.2,bold=True,width=870)
        text(d,(98,505),'ONE REPLACEMENT SLOT',27,color=RED,bold=True)
        text(d,(98,553),'1:00–1:30',72,bold=True)
        reveal(img,(98,700),'Existing capture shown as\nediting reference.',36,t,2,width=850)
        text(d,(98,856),'Replace with the approved masjid take.\nKeep genuine continuous recitation audible.',28,color=MUTED,width=830)
        text(d,(1060,104),'REFERENCE FOOTAGE / AWAITING MASJID TAKE',24,color=RED)
        if t<6:
            text(d,(1090,470),'MASJID TAKE',58,bold=True)
            text(d,(1090,550),'Reserved / reference starts at 1:06',30,width=720,color=MUTED)
        # No generated elements inside the live source window after six seconds.
        moving_line(d,(98,965),(900,965),t,0,30,color=RED,width=6)
    elif index==6:
        label(d,92,138,'WITHIN A SINGLE AYAH')
        reveal(img,(90,220),'Same passage.\nChanging\nportions.',85,t,.2,bold=True,width=890)
        text(d,(98,565),'73:20',64,color=RED,bold=True)
        # Abstract canonical words, with a moving source window. Never fake Quran text.
        for row in range(3):
            for j in range(10):
                d.rectangle((100+j*78,690+row*48,152+j*78,711+row*48),fill=RULE)
        pos=math.sin(t*.19-.8)*.5+.5
        left=98+pos*440
        d.rectangle((left,676,left+330,830),outline=BLUE,width=5)
        text(d,(98,863),'Source position → compact viewing window',29,color=BLUE)
        text(d,(98,914),'Explanatory graphic / no manual paging',26,color=MUTED)
        text(d,(1060,104),'Recorded phone preview / actual changing source card',24,color=RED)
    elif index==7:
        technical(img,t)
    elif index==8:
        label(d,92,135,'HIFZ / QURAN MEMORIZATION')
        reveal(img,(90,215),'A reference\nwhile rehearsing.',88,t,.2,bold=True,width=900)
        text(d,(98,640),'Choose the viewing mode.',35,serif=True)
        text(d,(98,837),'Reference use, not a tajweed grader.',30,color=MUTED)
        text(d,(98,905),'Explanatory mode graphic / not a filmed toggle',26,color=MUTED)
        x=1065
        text(d,(x,255),'ARABIC REFERENCE',35,bold=True)
        for row in range(3):
            d.rectangle((x,346+row*48,x+[650,590,520][row],363+row*48),fill=INK)
        moving_line(d,(x,540),(1770,540),t,6,2,color=RED,width=5)
        if t>6:
            reveal(img,(x,593),'+ ENGLISH MEANING',35,t,6,bold=True,color=BLUE)
            reveal(img,(x,690),source_example()['translation'],40,t,6.8,width=720,serif=True)
            text(d,(x,835),'Published source example / Pickthall 1:3',25,color=MUTED)
        else:
            text(d,(x,650),'Arabic-only viewing mode',31,color=MUTED)
    elif index==9:
        label(d,92,137,'BUILT DURING THE HACKATHON')
        reveal(img,(90,210),'A working foundation.',91,t,.2,bold=True)
        items=[(98,'114','SURAHS'),(685,'6,236','REFERENCE AYAHS'),(1290,str(plan.get('verified_core_tests',59)),'CORE TESTS PASSED')]
        for n,(x,num,title) in enumerate(items):
            reveal(img,(x,430),num,123,t,1+n*1.1,bold=True)
            reveal(img,(x,585),title,28,t,1.4+n*1.1)
            moving_line(d,(x,655),(x+480,655),t,1+n*1.1,1.1,color=RED,width=6)
        text(d,(98,715),'Reference coverage is separate from measured recognition accuracy.',31,color=MUTED)
        if t<10:
            text(d,(98,845),'Glasses integration / live Muse clients / automatic following',33)
        else:
            d.rectangle((90,795,1830,975),fill=YELLOW)
            reveal(img,(115,818),'FUTURE / TEACHING SUPPORT',35,t,10,bold=True)
            reveal(img,(115,887),'Requires further development and extensive testing.',37,t,10.5)
    elif index==10:
        label(d,92,138,'AYAH LENS')
        reveal(img,(90,235),'Hear the recitation.',87,t,.2,bold=True,width=1080)
        reveal(img,(90,345),'Follow the meaning.',87,t,1.7,bold=True,width=1080)
        moving_line(d,(98,505),(1100,505),t,2.5,3,color=RED,width=8)
        wave(d,98,672,t,width=900,height=44,color=BLUE,speed=.55)
        text(d,(98,877),'github.com/khiradlabs/ayah-lens',35)
        text(d,(98,947),'Source footage predates Build 40 typography.',25,color=MUTED)
        text(d,(1210,109),'Native glasses recording / replay',25,color=RED)
    return img


def render_scene(index,destination,plan=None,*,start=0,duration=None,fps=FPS):
    """Write motion base at full HD. Optional start/duration support isolated motion proofs.

    Scene 3 reads assets/glasses-turntable.mp4 when present, then draws text above it.
    All other source footage is composited by the assembler, not this module.
    """
    plan=plan or load_plan()
    segment=plan['segments'][index]
    total=segment['end']-segment['start']
    length=min(duration if duration is not None else total-start,total-start)
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    product=OUT/'assets/glasses-turntable.mp4'
    decoder=None
    if index==3 and product.exists():
        decoder=subprocess.Popen(['ffmpeg','-v','error','-ss',str(start),'-i',str(product),'-vf',f'scale={W}:{H},fps={fps}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    args=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-threads','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(destination)]
    encoder=subprocess.Popen(args,stdin=subprocess.PIPE)
    product_frame=None
    try:
        for n in range(round(length*fps)):
            if decoder:
                data=decoder.stdout.read(W*H*3)
                if data:
                    assert len(data)==W*H*3,'Incomplete product frame'
                    product_frame=Image.frombytes('RGB',(W,H),data)
            frame=keyframe(index,start+n/fps,plan,product_frame)
            encoder.stdin.write(frame.tobytes())
    finally:
        encoder.stdin.close()
        if decoder:
            decoder.stdout.close()
            decoder.terminate()
            decoder.wait()
    assert encoder.wait()==0, f'Encoding failed: {destination}'
    print(f'RENDERED: {destination} / {length:.2f}s / {fps}fps',flush=True)
    return destination


def preview_keyframes(plan=None):
    """Save all-scene storyboard plus population and technical semantic stage sheets."""
    plan=plan or load_plan()
    folder=OUT/'preview'
    folder.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGB',(1920,1440),PAPER)
    for i,segment in enumerate(plan['segments']):
        t={2:15,7:15,8:9,9:12}.get(i,4)
        img=keyframe(i,t,plan)
        img.save(folder/f'scene-{i:02}.png')
        thumb=img.resize((640,360),Image.Resampling.LANCZOS)
        sheet.paste(thumb,((i%3)*640,(i//3)*360))
    sheet.save(folder/'storyboard.jpg',quality=94)
    for index,times in [(2,[1,5,9,15]),(7,[1,5,10,15,20,25])]:
        stage_sheet=Image.new('RGB',(1920,540*math.ceil(len(times)/2)),PAPER)
        for n,t in enumerate(times):
            img=keyframe(index,t,plan)
            img.save(folder/f'scene-{index:02}-t{t:02}.png')
            stage_sheet.paste(img.resize((960,540),Image.Resampling.LANCZOS),((n%2)*960,(n//2)*540))
        stage_sheet.save(folder/f'stages-{index:02}.jpg',quality=94)
    print(f'PREVIEW: {folder}/storyboard.jpg',flush=True)
    return folder/'storyboard.jpg'


def check(plan=None):
    plan=plan or load_plan()
    assert population_count(-1)==0 and population_count(3)==0
    assert 0<population_count(5)<25,'Population must build between the empty chart and quarter comparison'
    assert population_count(10)==25 and population_count(20)==25
    assert [pipeline_stage(t) for t in (0,5,9,13,18,25)]==[0,1,2,3,4,4],'Technical story must advance through five causal stages'
    assert len(plan['segments'])==11 and plan['segments'][0]['start']==0
    assert plan['segments'][-1]['end']==180
    assert all(a['end']==b['start'] for a,b in zip(plan['segments'],plan['segments'][1:]))
    assert plan['masjid_slot']['start']==60 and plan['masjid_slot']['end']==90
    assert source_example()['translation']=='The Beneficent, the Merciful.'
    differences={}
    # Content-region difference excludes progress rails/badges. Measures semantic stages.
    for index,times in [(2,[1,5,9,15]),(7,[1,5,10,15,20])]:
        frames=[keyframe(index,t,plan).crop((90,125,1830,990)) for t in times]
        means=[sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3 for a,b in zip(frames,frames[1:])]
        assert min(means)>2.0,(index,means)
        differences[str(index)]=[round(v,2) for v in means]
    # Every scene must be drawable and change beyond its footer as the story progresses.
    for index,segment in enumerate(plan['segments']):
        length=segment['end']-segment['start']
        a=keyframe(index,.1,plan).crop((90,125,1830,990))
        b=keyframe(index,min(length-1,7),plan).crop((90,125,1830,990))
        assert ImageChops.difference(a,b).getbbox(),f'Static scene {index}'
    print('PASS: 11 contiguous scenes / 180s / 60–90s reserved / exact source excerpt')
    print('PASS: population count build / five causal stages / all scenes change')
    print('CONTENT-REGION MEAN PIXEL CHANGE:',json.dumps(differences))
    return differences


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--preview',action='store_true')
    parser.add_argument('--render',action='store_true')
    parser.add_argument('--scene',type=int,help='Render only one zero-based scene')
    args=parser.parse_args()
    plan=load_plan()
    if args.check or not(args.preview or args.render):
        check(plan)
    if args.preview:
        preview_keyframes(plan)
        # Short isolated motion proofs preserve source-time progression at 30fps.
        render_scene(2,OUT/'preview/population-motion.mp4',plan,start=3,duration=12)
        render_scene(7,OUT/'preview/technical-motion.mp4',plan,start=0,duration=24)
    if args.render:
        for i in ([args.scene] if args.scene is not None else range(11)):
            render_scene(i,OUT/f'motion/scene-{i:02}.mp4',plan)
