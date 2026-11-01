#!/usr/bin/env python3
"""Render the private Version 3 review cut; keep the masjid slot replaceable."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/video-review'
W, H, FPS = 1920, 1080, 30
INK, WHITE, MUTED, TEAL, GOLD = '#080f18', '#f4f1e9', '#9caebc', '#29d9c1', '#dfbc7b'
FONT_ROOT = Path('/System/Library/Fonts/Supplemental')
PLAN = json.loads((ROOT / 'submission/video-edit.json').read_text())
FONT_CACHE = {}


def run(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, **kwargs)


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))


def font(size, bold=False, display=False):
    key = (size, bold, display)
    if key not in FONT_CACHE:
        name = 'DIN Alternate Bold.ttf' if display else ('Arial Bold.ttf' if bold else 'Arial.ttf')
        FONT_CACHE[key] = ImageFont.truetype(str(FONT_ROOT / name), size)
    return FONT_CACHE[key]


def text(draw, xy, content, size=42, color=WHITE, bold=False, display=False, width=None, gap=1.22):
    x, y = xy
    f = font(size, bold, display)
    lines = []
    for paragraph in content.split('\n'):
        line = ''
        for word in paragraph.split():
            trial = f'{line} {word}'.strip()
            if width and draw.textlength(trial, font=f) > width and line:
                lines.append(line)
                line = word
            else:
                line = trial
        lines.append(line)
    for line in lines:
        if width:
            assert draw.textlength(line, font=f) <= width + 2, f'Text too wide: {line}'
        draw.text((x, y), line, font=f, fill=color)
        y += round(size * gap)
    return y


def box(draw, rect, fill='#101e2b', border='#243a47', radius=25, line=2):
    draw.rounded_rectangle(rect, radius=radius, fill=fill, outline=border, width=line)


def tag(draw, x, y, label, color=TEAL):
    f = font(24, True)
    width = draw.textlength(label, font=f) + 36
    box(draw, (x, y, x + width, y + 45), fill='#112b30', border='#244d50', radius=20, line=1)
    text(draw, (x + 18, y + 8), label, 24, color, True)


def line_arrow(draw, start, end, color=TEAL, line=4):
    draw.line([start, end], fill=color, width=line)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    pts = [end]
    for delta in (-0.45, 0.45):
        pts.append((end[0] - 16 * math.cos(angle + delta), end[1] - 16 * math.sin(angle + delta)))
    draw.polygon(pts, fill=color)


def glasses(draw, x, y, scale=1, color=TEAL):
    def rect(a, b, c, d):
        return (x + a * scale, y + b * scale, x + c * scale, y + d * scale)
    draw.rounded_rectangle(rect(0, 0, 180, 135), radius=int(30 * scale), outline=color, width=max(2, int(5 * scale)))
    draw.rounded_rectangle(rect(220, 0, 400, 135), radius=int(30 * scale), outline=color, width=max(2, int(5 * scale)))
    draw.arc(rect(175, 15, 225, 60), 180, 360, fill=color, width=max(2, int(5 * scale)))
    draw.line([(x - 25 * scale, y + 12 * scale), (x, y + 20 * scale)], fill=color, width=max(2, int(5 * scale)))
    draw.line([(x + 400 * scale, y + 20 * scale), (x + 425 * scale, y + 12 * scale)], fill=color, width=max(2, int(5 * scale)))


def background(index):
    img = Image.new('RGB', (W, H), INK)
    glow = Image.new('RGB', (W, H), INK)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((1120, -400, 2200, 700), fill='#103b3e')
    gd.ellipse((-450, 650, 600, 1600), fill='#102735')
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(160)), .55)
    d = ImageDraw.Draw(img)
    for x in range(64, W, 90):
        for y in range(130, H - 60, 90):
            d.ellipse((x, y, x + 2, y + 2), fill='#192c37')
    if index > 1:
        text(d, (88, 38), 'AYAH LENS', 29, WHITE, True)
        d.ellipse((61, 47, 71, 57), fill=TEAL)
    text(d, (1390, 40), 'REVIEW CUT / GUIDE VOICE', 23, MUTED)
    d.line((88, 1009, 1832, 1009), fill='#253b47', width=2)
    d.line((88, 1009, 88 + (1832 - 88) * (index + 1) / 11, 1009), fill=TEAL, width=3)
    text(d, (88, 1030), 'Hear the recitation. Follow the meaning.', 22, MUTED)
    return img


def scene_image(index, phase=0):
    img = background(index)
    d = ImageDraw.Draw(img)
    if index == 0:
        text(d, (625, 370), 'Just listen.', 126, WHITE, display=True)
        text(d, (640, 552), 'For a moment, let the words reach you.', 32, MUTED)
        for n in range(29):
            x = 640 + n * 22
            h = 12 + 18 * abs(math.sin(n * .6))
            d.rounded_rectangle((x, 650 - h, x + 6, 650 + h), radius=3, fill=TEAL)
    elif index == 1:
        tag(d, 92, 160, 'THE MOMENT MEANING APPEARS')
        text(d, (92, 245), 'Now follow\nthe meaning.', 105, display=True, width=960)
        box(d, (83, 515, 1061, 782), fill='#030a10', border='#397e7c')
        text(d, (95, 812), 'Enlarged display from the same recording', 27, MUTED)
        text(d, (1190, 105), 'Native glasses recording', 26, TEAL)
        text(d, (95, 900), 'Same recorded passage, replayed with its meaning in view.', 29, MUTED, width=990)
    elif index == 2:
        tag(d, 92, 155, 'A RECURRING HUMAN NEED')
        text(d, (92, 225), '2.0B', 292, display=True)
        text(d, (110, 570), 'Muslims worldwide', 64, WHITE, True)
        text(d, (112, 680), 'For many, Arabic is not\nan everyday language.', 48, MUTED, width=1050)
        d.arc((1290, 285, 1720, 715), 0, 360, fill='#243440', width=48)
        d.arc((1290, 285, 1720, 715), -90, -90 + 360 * .256, fill=TEAL, width=48)
        text(d, (1362, 438), '~1 in 4', 60, WHITE, display=True)
        text(d, (1300, 772), 'people worldwide', 30, MUTED)
        text(d, (112, 930), 'Pew Research Center / 2020 estimate, published 2025', 26, MUTED)
        if phase == 0:
            d.rectangle((82, 218, 1210, 875), fill=INK)
            text(d, (92, 270), 'From hearing\nto understanding.', 115, display=True, width=1120)
            text(d, (98, 650), 'For many, the meaning takes another step.', 43, MUTED, width=1050)
    elif index == 3:
        tag(d, 92, 155, 'MEET')
        text(d, (92, 230), 'Ayah Lens', 152, display=True)
        glasses(d, 110, 465, 1.75)
        text(d, (100, 770), 'Meta glasses\nMuse Voice + Muse Spark', 47, WHITE, True, width=1080)
        text(d, (1240, 110), 'Actual recorded output', 27, TEAL)
    elif index == 4:
        text(d, (92, 150), 'Meaning, in the moment.', 86, display=True)
        for x, title, body in [(92, 'PRAYER LISTENING', 'A possible use during Salat'), (985, 'AT HOME', 'Follow a reciter on television')]:
            box(d, (x, 330, x + 835, 780))
            text(d, (x + 44, 585), title, 38, TEAL, True)
            text(d, (x + 44, 660), body, 36, WHITE, width=740)
        d.arc((385, 380, 620, 670), 180, 360, fill=TEAL, width=5)
        d.line((385, 525, 385, 565), fill=TEAL, width=5)
        d.line((620, 525, 620, 565), fill=TEAL, width=5)
        d.rounded_rectangle((1220, 395, 1575, 555), radius=12, outline=TEAL, width=5)
        d.line((1305, 570, 1490, 570), fill=TEAL, width=5)
        text(d, (95, 865), 'Technology demonstration only. This does not establish religious permissibility for use during prayer.', 30, MUTED, width=1720)
    elif index == 5:
        tag(d, 92, 150, 'MASJID RECORDING / RESERVED', GOLD)
        text(d, (92, 245), 'This is your\nmasjid moment.', 91, display=True, width=850)
        text(d, (96, 505), '30-second replacement slot', 40, GOLD, True)
        text(d, (96, 600), 'The existing phone capture is shown\nhere as an editing reference.', 37, MUTED, width=820)
        text(d, (96, 795), 'Keep the real recitation audible.\nLet the display follow without touching Next.', 32, WHITE, width=820)
        text(d, (1060, 105), 'REFERENCE FOOTAGE / REPLACE WITH MASJID TAKE', 23, GOLD)
        box(d, (1053, 132, 1835, 1010), fill='#0b151e')
        text(d, (1150, 480), 'MASJID CLIP\nGOES HERE', 62, MUTED, True, width=630)
    elif index == 6:
        tag(d, 92, 155, 'LOOK CLOSER')
        text(d, (92, 247), 'One long verse.\nAutomatic\nportions.', 91, display=True, width=850)
        text(d, (97, 680), '73:20', 54, TEAL, True)
        text(d, (97, 767), 'The passage stays the same.\nThe relevant portion changes.', 37, MUTED, width=820)
        text(d, (1060, 105), 'Recorded phone preview / enlarged source card', 25, TEAL)
    elif index == 7:
        text(d, (92, 145), 'Meta hardware. Meta AI. One experience.', 72, display=True)
        nodes = [(92, 'META GLASSES', 'Capture recitation'), (548, 'MUSE VOICE', 'Live Arabic transcript'), (1004, 'OUR TRACKER', 'Locate the passage'), (1460, 'GLASSES DISPLAY', 'Follow the meaning')]
        active = {0: 1, 1: 1, 2: 2}.get(phase, 1)
        for n, (x, title, desc) in enumerate(nodes):
            border = TEAL if n == active else '#29404c'
            box(d, (x, 320, x + 370, 535), border=border, line=4 if n == active else 2)
            text(d, (x + 25, 363), title, 29, TEAL if n == active else WHITE, True)
            text(d, (x + 25, 429), desc, 29, MUTED, width=320)
            if n < 3:
                line_arrow(d, (x + 383, 425), (x + 441, 425), color=TEAL if n < active else '#47606a')
        box(d, (548, 650, 1374, 870), border=TEAL if phase == 1 else '#29404c', line=4 if phase == 1 else 2)
        text(d, (581, 678), 'MUSE SPARK', 40, TEAL, True)
        text(d, (582, 741), 'Pairs Arabic + published English portions', 32, WHITE)
        text(d, (582, 804), 'Cached phrase plans / bounded ambiguity assistance', 26, MUTED)
        line_arrow(d, (1190, 650), (1190, 550), GOLD)
        line_arrow(d, (1374, 760), (1640, 760), TEAL)
        line_arrow(d, (1640, 760), (1640, 550), TEAL)
        text(d, (95, 700), 'Published\nsource text', 34, MUTED, width=350)
        line_arrow(d, (368, 760), (528, 760), GOLD)
        text(d, (95, 930), 'Models assist. Software validates. Displayed wording comes from the published sources.', 27, MUTED)
    elif index == 8:
        tag(d, 92, 155, 'HIFZ / QURAN MEMORIZATION')
        text(d, (92, 250), 'Practice with\na reference\nin view.', 100, display=True, width=920)
        box(d, (1120, 260, 1824, 485), border=TEAL, line=3)
        text(d, (1168, 300), 'ARABIC ONLY', 48, TEAL, True)
        text(d, (1168, 385), 'Reference while rehearsing', 34, WHITE)
        box(d, (1120, 565, 1824, 790))
        text(d, (1168, 608), 'ARABIC + ENGLISH', 43, WHITE, True)
        text(d, (1168, 690), 'Follow the published meaning', 32, MUTED)
        text(d, (97, 840), 'Choose what helps you follow.', 42, MUTED)
        text(d, (1125, 870), 'Viewing options / explanatory graphic', 25, MUTED)
        if phase == 1:
            d.rounded_rectangle((1120, 260, 1824, 485), radius=25, outline='#29404c', width=3)
            d.rounded_rectangle((1120, 565, 1824, 790), radius=25, outline=TEAL, width=4)
    elif index == 9:
        tag(d, 92, 155, 'BUILT DURING THE HACKATHON')
        text(d, (92, 245), 'A working foundation.', 95, display=True)
        for x, number, label in [(95, '114', 'SURAHS'), (690, '6,236', 'REFERENCE AYAHS'), (1285, '55', 'CORE TESTS PASSED')]:
            box(d, (x, 440, x + 540, 740))
            text(d, (x + 35, 465), number, 120, TEAL, display=True)
            text(d, (x + 35, 638), label, 28, WHITE, True)
        text(d, (98, 785), 'Glasses integration / live Muse clients / automatic following', 35, WHITE)
        text(d, (98, 855), 'Complete reference coverage is separate from measured recognition accuracy.', 27, MUTED)
        if phase == 1:
            box(d, (80, 755, 1840, 975), fill='#13252b', border=GOLD)
            text(d, (115, 782), 'FUTURE / TEACHING SUPPORT', 39, GOLD, True)
            text(d, (115, 853), 'Requires further development and extensive testing.', 40, WHITE)
    elif index == 10:
        tag(d, 92, 170, 'AYAH LENS')
        text(d, (92, 270), 'Hear the recitation.\nFollow the meaning.', 95, display=True, width=1060)
        glasses(d, 110, 650, 1.25)
        text(d, (98, 875), 'github.com/khiradlabs/ayah-lens', 34, MUTED)
        text(d, (1210, 105), 'Native glasses recording / replay', 25, TEAL)
    return img


def sources(index):
    assets = PLAN['source_assets']
    native = ROOT / assets['native']
    within = OUT / 'assets/within-card-clean.mp4'
    if index == 1:
        return [(native, None, 635, 844, 1185, 145, 0, 0),
                (native, assets['native_display_crop'], 960, 240, 92, 530, 0, 0)]
    if index == 3:
        return [(native, None, 580, 770, 1240, 160, 0, 0)]
    if index == 5:
        return [(within, None, 770, 873, 1060, 138, 0, 6)]
    if index == 6:
        return [(within, None, 770, 873, 1060, 138, 0, 0)]
    if index == 10:
        return [(native, None, 610, 810, 1210, 148, 0, 0)]
    return []


def frame_at(source, seconds, destination):
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', seconds, '-i', source, '-frames:v', '1', destination])


def prepare_phone_card():
    """Mask only surrounding status UI below the changing source card."""
    source = ROOT / PLAN['source_assets']['within']
    target = OUT / 'assets/within-card-clean.mp4'
    receipt = OUT / 'assets/card-mask.json'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if target.exists() and receipt.exists() and json.loads(receipt.read_text())['source_sha256'] == digest:
        return
    x, y, width, height = PLAN['source_assets']['within_crop']
    decode = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(source), '-an', '-vf', f'crop={width}:{height}:{x}:{y},fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    encode = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{width}x{height}', '-r', str(FPS), '-i', '-', '-i', str(source), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-map_metadata', '-1', '-shortest', str(target)], stdin=subprocess.PIPE)
    frame_bytes, cuts = width * height * 3, []
    while True:
        data = decode.stdout.read(frame_bytes)
        if not data:
            break
        assert len(data) == frame_bytes
        image = Image.frombytes('RGB', (width, height), data)
        pixels = image.load()
        count, cutoff = 0, height
        for row in range(260, height):
            black = max(pixels[24, row]) < 8 and max(pixels[42, row]) < 8
            count = count + 1 if black else 0
            if count >= 12:
                cutoff = min(height, row - 11 + 40)
                break
        if cutoff < height:
            ImageDraw.Draw(image).rectangle((0, cutoff, width, height), fill=(0, 0, 0))
        cuts.append(cutoff)
        encode.stdin.write(image.tobytes())
    encode.stdin.close()
    assert decode.wait() == 0 and encode.wait() == 0
    receipt.write_text(json.dumps({'source_sha256': digest, 'frames': len(cuts), 'min_mask_start': min(cuts), 'max_mask_start': max(cuts), 'operation': 'Mask surrounding UI below the source card; source card content unchanged'}, indent=2) + '\n')
    print(f'PREPARED: source-card-only panel / {len(cuts)} frames', flush=True)


def storyboard():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'assets').mkdir(exist_ok=True)
    prepare_phone_card()
    thumbnails = []
    for i, segment in enumerate(PLAN['segments']):
        img = scene_image(i, 1 if i == 2 else 0)
        img.save(OUT / f'assets/scene-{i:02}.png')
        for k, source in enumerate(sources(i)):
            path, crop, width, height, x, y, _, _ = source
            still = OUT / f'assets/still-{i:02}-{k}.png'
            frame_at(path, 6, still)
            pic = Image.open(still).convert('RGB')
            if crop:
                cx, cy, cw, ch = crop
                pic = pic.crop((cx, cy, cx + cw, cy + ch))
            img.paste(pic.resize((width, height), Image.Resampling.LANCZOS), (x, y))
        img.save(OUT / f'assets/story-{i:02}.png')
        thumb = img.resize((640, 360), Image.Resampling.LANCZOS)
        td = ImageDraw.Draw(thumb)
        td.rectangle((0, 330, 640, 360), fill='#071018')
        td.text((12, 334), f"{segment['start']//60}:{segment['start']%60:02} / {segment['title']}", font=font(16), fill=WHITE)
        thumbnails.append(thumb)
    sheet = Image.new('RGB', (1920, 4 * 360), '#03080e')
    for n, image in enumerate(thumbnails):
        sheet.paste(image, ((n % 3) * 640, (n // 3) * 360))
    sheet.save(OUT / 'storyboard.jpg', quality=94)
    scene_image(2, 0).save(OUT / 'assets/scene-02.png')
    for i, phase in [(2, 1), (7, 1), (7, 2), (8, 1), (9, 1)]:
        scene_image(i, phase).save(OUT / f'assets/scene-{i:02}-phase-{phase}.png')
    print(f'STORYBOARD: {OUT / "storyboard.jpg"}', flush=True)


def guide_audio():
    audio = OUT / 'audio'
    audio.mkdir(exist_ok=True)
    for i, segment in enumerate(PLAN['segments']):
        duration = segment['end'] - segment['start']
        target = audio / f'{i:02}.wav'
        if segment['narration']:
            script = audio / f'{i:02}.txt'
            script.write_text(segment['narration'].replace('Quran', 'Koran').replace('Ayah Lens', 'Eye-ah Lens').replace('Hifz', 'Hiffs'))
            raw = audio / f'{i:02}.aiff'
            run(['say', '-v', 'Daniel', '-r', '145', '-f', script, '-o', raw])
            length = float(probe(raw)['format']['duration'])
            speed = max(1, length / (duration - 1.0))
            filters = f'atempo={speed:.5f},loudnorm=I=-17:TP=-2:LRA=9,adelay=400:all=1,apad,atrim=duration={duration}'
            run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', raw, '-af', filters, '-ar', '48000', '-ac', '2', target])
        elif i in (0, 1):
            run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', ROOT / PLAN['source_assets']['native'], '-vn', '-af', f'volume=20dB,highpass=f=90,lowpass=f=7000,afade=t=in:d=0.08,afade=t=out:st=7.8:d=0.2,apad,atrim=duration={duration}', '-ar', '48000', '-ac', '2', target])
        elif i == 5:
            run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', ROOT / PLAN['source_assets']['within'], '-vn', '-af', f'volume=12dB,adelay=6000:all=1,apad,atrim=duration={duration}', '-ar', '48000', '-ac', '2', target])
        else:
            run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', duration, target])
        print(f'AUDIO: {i:02} / {duration}s / temporary guide or source audio', flush=True)


def render_segment(index):
    segment = PLAN['segments'][index]
    duration = segment['end'] - segment['start']
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-loop', '1', '-framerate', FPS, '-i', OUT / f'assets/scene-{index:02}.png']
    chain, previous = [], '0:v'
    number = 1
    if index in (2, 7, 8, 9):
        phases = {2: [(1, 7, 20)], 7: [(1, 6, 18), (2, 18, 26)], 8: [(1, 7.5, 14)], 9: [(1, 11, 16)]}[index]
        for phase, start, end in phases:
            cmd += ['-loop', '1', '-framerate', FPS, '-i', OUT / f'assets/scene-{index:02}-phase-{phase}.png']
            name = f'phase{phase}'
            chain.append(f'[{previous}][{number}:v]overlay=enable=\'between(t,{start},{end})\'[{name}]')
            previous, number = name, number + 1
    for n, item in enumerate(sources(index)):
        path, crop, width, height, x, y, seek, start = item
        cmd += ['-ss', seek, '-i', path]
        vf = f'[{number}:v]'
        if crop:
            cx, cy, cw, ch = crop
            vf += f'crop={cw}:{ch}:{cx}:{cy},'
        vf += f'scale={width}:{height},fps={FPS},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={duration},trim=duration={duration-start},format=rgba,fade=t=in:st=0:d=0.25:alpha=1,setpts=PTS+{start}/TB[src{n}]'
        chain.append(vf)
        name = f'comp{n}'
        chain.append(f'[{previous}][src{n}]overlay=x={x}:y={y}:enable=\'gte(t,{start})\':eof_action=pass[{name}]')
        previous, number = name, number + 1
    cmd += ['-i', OUT / f'audio/{index:02}.wav']
    # Editorial fades never change source playback speed.
    chain.append(f'[{previous}]fade=t=in:st=0:d=0.25,fade=t=out:st={duration-.25}:d=0.25,format=yuv420p[out]')
    cmd += ['-filter_complex', ';'.join(chain), '-map', '[out]', '-map', f'{number}:a', '-t', duration,
            '-r', FPS, '-c:v', 'libx264', '-preset', 'fast', '-crf', '19', '-threads', '4', '-c:a', 'aac', '-b:a', '192k',
            '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-map_metadata', '-1', '-movflags', '+faststart', OUT / f'segment-{index:02}.mp4']
    run(cmd, timeout=240)
    print(f'RENDERED: {index:02} / {segment["title"]}', flush=True)


def render():
    guide_audio()
    for index in range(len(PLAN['segments'])):
        render_segment(index)
    concat = OUT / 'concat.txt'
    concat.write_text(''.join(f"file 'segment-{i:02}.mp4'\n" for i in range(len(PLAN['segments']))))
    master = OUT / 'Ayah-Lens-Version-3-Review.mp4'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-reinit_filter', '0', '-f', 'concat', '-safe', '0', '-i', concat,
         '-vf', 'fps=30,setpts=PTS-STARTPTS', '-af', 'aresample=async=1:first_pts=0,apad',
         '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '4', '-c:a', 'aac', '-b:a', '192k',
         '-t', '179.9', '-map_metadata', '-1', '-movflags', '+faststart', master])
    data = probe(master)
    length = float(data['format']['duration'])
    assert 179 <= length <= 180, length
    assert {'video', 'audio'} <= {s['codec_type'] for s in data['streams']}
    video = next(s for s in data['streams'] if s['codec_type'] == 'video')
    assert (video['width'], video['height']) == (W, H)
    assert float(video['duration']) >= length - .1, 'Picture must cover the full review duration'
    assert int(video['nb_frames']) >= 5397, 'Missing picture frames'
    receipt = {'file': str(master), 'duration': length, 'resolution': [W, H], 'status': 'review only',
               'guide_narration': True, 'masjid_slot': PLAN['masjid_slot'], 'source_assets': PLAN['source_assets']}
    (OUT / 'render-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'PASS: {length:.3f}s / 1920x1080 / audio+video / masjid slot reserved', flush=True)
    print(f'REVIEW CUT: {master}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--storyboard-only', action='store_true')
    args = parser.parse_args()
    assert PLAN['duration_seconds'] == 180
    assert PLAN['masjid_slot']['end'] - PLAN['masjid_slot']['start'] == 30
    for key in ('native', 'within'):
        assert (ROOT / PLAN['source_assets'][key]).is_file()
    storyboard()
    if not args.storyboard_only:
        render()
