#!/usr/bin/env python3
"""Ayah Lens demo v1.0 renderer.

Reads tools/v1/edit.json (all footage choices, cut points, captions and audio settings live there),
renders one picture segment per section with ffmpeg filters plus Pillow/Skia overlays, mixes the audio
(recitation bed ducked under narration) and muxes build/video-v1.0/Ayah-Lens-Demo-v1.0.mp4.

Run with the venv that has numpy, Pillow, uharfbuzz and skia-python:
  /Users/farazsyed/data/khirad/apps/ayah-lens-prep/venv-data/bin/python tools/v1/render_v1.py [--check]

--check is read-only: it never renders. It decodes the existing export and reports duration, frames,
loudness, peak, colour tags and the 180 s limit.
"""
import argparse
import copy
import hashlib
import json
import math
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EDIT = Path(__file__).resolve().parent / 'edit.json'
FPS = 30
SR = 48000
SPF = SR // FPS  # 1600 samples per frame
SS = 2  # overlay supersampling


# ----------------------------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------------------------
def run(args, **kw):
    return subprocess.run([str(x) for x in args], check=True, **kw)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def rp(p):
    """Resolve a path from edit.json against the project root."""
    p = Path(p)
    return p if p.is_absolute() else ROOT / p


def load_edit_raw(path=DEFAULT_EDIT):
    return json.loads(Path(path).read_text())


def deep_merge(base, over):
    """Dicts merge recursively; lists and scalars in `over` replace those in `base`."""
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def apply_fallback(edit, enabled=None):
    """Fallback mode (edit['fallback']['enabled'], off by default): drop the s5 placeholder and swap in the
    fallback narration and pictures. Returns a new dict; edit['fallback_active'] says which mode it is."""
    fb = edit.get('fallback', {})
    on = fb.get('enabled', False) if enabled is None else enabled
    edit = copy.deepcopy(edit)
    edit['fallback_active'] = bool(on)
    if not on:
        return edit
    drop = set(fb.get('drop_sections', []))
    secs = []
    for s in edit['sections']:
        if s['id'] in drop:
            continue
        if s['id'] in fb.get('overrides', {}):
            s = deep_merge(s, fb['overrides'][s['id']])
        secs.append(s)
    edit['sections'] = secs
    return edit


def apply_narration_source(edit, source=None):
    """Narration source switch (edit['narration']['source']): 'callum' keeps each section's file as written;
    'own' points every section at <own_dir>/<stem>.wav, where stem is the stem of the file the section would
    use (s1, s4-fallback, ...). Cut offsets stay relative to the end of whichever file is used."""
    cfg = edit.get('narration', {})
    src = cfg.get('source', 'callum') if source is None else source
    if src not in ('callum', 'own'):
        raise ValueError(f"narration.source must be 'callum' or 'own', not {src!r}")
    edit = copy.deepcopy(edit)
    edit.setdefault('narration', {})['source'] = src
    if src == 'own':
        own_dir = cfg.get('own_dir', 'build/video-v1.0/narration/own')
        for s in edit['sections']:
            if not s['narration'].get('file'):
                continue  # a section with its own recorded voice (s1) has no narration file
            stem = Path(s['narration']['file']).stem
            s['narration']['callum_file'] = s['narration']['file']
            s['narration']['file'] = f'{own_dir}/{stem}.wav'
    return edit


HDR_TRANSFERS = ('arib-std-b67', 'smpte2084')


def probe_video(path):
    """Display size (after any rotation tag), colour tags and duration of a video file."""
    d = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams', '-show_format', '-of', 'json', str(path)]))
    st = d['streams'][0]
    w, h = st['width'], st['height']
    rot = 0
    for sd in st.get('side_data_list', []):
        if 'rotation' in sd:
            rot = int(float(sd['rotation']))
    if rot == 0 and st.get('tags', {}).get('rotate'):
        rot = int(st['tags']['rotate'])
    if abs(rot) % 180 == 90:
        w, h = h, w
    return {'w': w, 'h': h, 'duration': float(d['format']['duration']), 'color_transfer': st.get('color_transfer'),
            'color_space': st.get('color_space'), 'color_range': st.get('color_range')}


def contain_rect(w, h, cw, ch):
    """Largest even-sized rectangle with the aspect of a w x h frame that fits a cw x ch canvas, centred.
    A portrait clip on a landscape canvas comes out full height and pillar-boxed (never centre-cropped)."""
    k = min(cw / w, ch / h)
    dw, dh = round(w * k / 2) * 2, round(h * k / 2) * 2
    return [(cw - dw) // 2, (ch - dh) // 2, dw, dh]


LABEL_TEMPLATE = {'type': 'plate', 'role': 'label', 'pos': [1884, 28], 'anchor': 'tr', 'pad': 14, 'radius': 12}


def apply_toggle(edit, cfg=None):
    """s5 (English off and on) exists only when a toggle clip is set (edit['toggle']['file']).
    With a clip: s5 plays it (pillar-boxed or letter-boxed on paper unless crop/dest are given) with the caption, and
    s4 keeps its bridged narration. Without one: s5 is dropped and s4 and s6 take the 'without_toggle' overrides
    (the s4 narration without the 'steps aside' bridge, no s5 hold before s6). No placeholder text ever ships."""
    cfg = cfg if cfg is not None else edit.get('toggle') or {}
    edit = copy.deepcopy(edit)
    has5 = any(s['id'] == 's5' for s in edit['sections'])
    if not cfg.get('file'):
        wt = cfg.get('without_toggle') or {'drop_sections': ['s5']}
        drop = set(wt.get('drop_sections', ['s5']))
        secs = []
        for sec in edit['sections']:
            if sec['id'] in drop:
                continue
            if sec['id'] in wt.get('overrides', {}):
                sec = deep_merge(sec, wt['overrides'][sec['id']])
            secs.append(sec)
        edit['sections'] = secs
        edit['toggle_active'] = False
        return edit
    if not has5:
        return edit  # fallback mode drops s5 even when a toggle clip exists
    path = rp(cfg['file'])
    if not path.exists():
        raise FileNotFoundError(f'toggle clip not found: {path}')
    info = probe_video(path)
    if info['color_transfer'] in HDR_TRANSFERS:
        raise ValueError(f'toggle clip {path.name} is HDR ({info["color_transfer"]}); re-export it as SDR')
    t_in, t_out = cfg.get('in'), cfg.get('out')
    if t_in is None or t_out is None or t_in < 0 or t_in >= t_out or t_out > info['duration'] + 1e-6:
        raise ValueError(f"toggle in/out {t_in}-{t_out} s do not fit {path.name} ({info['duration']:.2f} s)")
    W, H = edit['canvas']['w'], edit['canvas']['h']
    label = cfg.get('label', 'Glasses display recording')
    edit['footage']['toggle'] = {'file': cfg['file'], 'range': cfg.get('range') or ('pc' if info['color_range'] == 'pc' else 'tv'),
                                 'matrix': cfg.get('matrix') or ('bt601' if info['color_space'] in ('smpte170m', 'bt470bg') else 'bt709'),
                                 'label': label, 'kind': 'English off and on clip'}
    crop = cfg.get('crop') or [0, 0, info['w'], info['h']]
    dest = cfg.get('dest') or contain_rect(crop[2], crop[3], W, H)
    caption = cfg.get('caption', 'Arabic only, for memorization.')
    right, left = W - (dest[0] + dest[2]), dest[0]
    pos = cfg.get('caption_pos')
    if pos is None:
        if dest[2] >= W - 2 and dest[3] >= H - 2:
            pos, anchor, mw = [W // 2, H - edit.get('bottom_margin_px', 54)], 'bc', W - 60
        elif right >= 600:
            pos, anchor, mw = [dest[0] + dest[2] + 40, 330], 'tl', right - 100
        elif left >= 600:
            pos, anchor, mw = [40, 330], 'tl', left - 80
        else:
            pos, anchor, mw = [W // 2, H - edit.get('bottom_margin_px', 54)], 'bc', W - 60
    else:
        anchor, mw = cfg.get('caption_anchor', 'tl'), cfg.get('caption_max_width', 800)
    sec5 = next(sec for sec in edit['sections'] if sec['id'] == 's5')
    sec5['name'] = 'Hifz'
    sec5['layers'] = [
        {'type': 'paper'},
        {'type': 'footage', 'id': 'main', 'source': 'toggle', 'in': t_in, 'out': t_out, 'start_s': 0, 'crop': crop, 'dest': dest, 'freeze_after': True},
        dict(LABEL_TEMPLATE, lines=[{'text': label, 'size': 48, 'bold': True}]),
        {'type': 'plate', 'pos': pos, 'anchor': anchor, 'max_width': mw, 'pad': 18, 'fade_s': 0.3,
         'lines': [{'text': caption, 'size': 56, 'bold': True}]},
    ]
    edit['toggle_active'] = True
    return edit


def load_edit(path=DEFAULT_EDIT, fallback=None, voice=None):
    return apply_narration_source(apply_toggle(apply_fallback(load_edit_raw(path), fallback)), voice)


def missing_narration(edit):
    return [(s['id'], str(rp(s['narration']['file']))) for s in edit['sections']
            if s['narration'].get('file') and not rp(s['narration']['file']).exists()]


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def snap_frame(seconds):
    """Round a source time to the nearest frame boundary (never int(): binary float drift)."""
    return round(seconds * FPS) / FPS


class Palette:
    def __init__(self, edit):
        p = edit['palette']
        self.paper = hexrgb(p['paper'])
        self.ink = hexrgb(p['ink'])
        self.blue = hexrgb(p['blue'])
        self.red = hexrgb(p['red'])
        m = p.get('dim_mix', 0.36)
        self.dim = tuple(round(a * (1 - m) + b * m) for a, b in zip(self.paper, self.ink))

    def get(self, name):
        if name is None:
            return None
        if isinstance(name, str) and name.startswith('#'):
            return hexrgb(name)
        return getattr(self, name)


# ----------------------------------------------------------------------------------------------
# numeric report parsers (CLAUDE.md: use group(1) and reject a missing numeric report)
# ----------------------------------------------------------------------------------------------
def parse_max_volume(log):
    m = re.search(r'max_volume:\s*(-?\d+(?:\.\d+)?)\s*dB', log)
    if m is None:
        raise ValueError('No max_volume report')
    return float(m.group(1))


def parse_mean_volume(log):
    m = re.search(r'mean_volume:\s*(-?\d+(?:\.\d+)?)\s*dB', log)
    if m is None:
        raise ValueError('No mean_volume report')
    return float(m.group(1))


def parse_integrated_lufs(log):
    i = log.rfind('Summary:')
    if i < 0:
        raise ValueError('No ebur128 summary')
    m = re.search(r'I:\s+(-?\d+(?:\.\d+)?)\s+LUFS', log[i:])
    if m is None:
        raise ValueError('No integrated loudness in ebur128 summary')
    return float(m.group(1))


def parse_lra(log):
    i = log.rfind('Summary:')
    m = re.search(r'LRA:\s+(-?\d+(?:\.\d+)?)\s+LU', log[i:]) if i >= 0 else None
    if m is None:
        raise ValueError('No loudness range in ebur128 summary')
    return float(m.group(1))


def measure_wav(path):
    """Return (integrated LUFS, max sample peak dBFS) for any audio file, via ffmpeg."""
    e = run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'],
            capture_output=True, text=True).stderr
    v = run(['ffmpeg', '-hide_banner', '-i', path, '-vn', '-af', 'volumedetect', '-f', 'null', '-'],
            capture_output=True, text=True).stderr
    return parse_integrated_lufs(e), parse_max_volume(v)


def measure_pcm_lufs(pcm):
    """Integrated loudness of float32 stereo PCM (n, 2) at 48 kHz."""
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                        '-af', 'ebur128', '-f', 'null', '-'], input=pcm.astype('<f4').tobytes(),
                       capture_output=True, check=True)
    return parse_integrated_lufs(p.stderr.decode())


# ----------------------------------------------------------------------------------------------
# narration + plan
# ----------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def narration_info(path):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'])
    a = np.frombuffer(raw, dtype='<f4')
    if len(a) == 0:
        raise ValueError(f'Narration decoded to zero samples: {path}')
    idx = np.where(np.abs(a) > 10 ** (-45 / 20))[0]
    if len(idx) == 0:
        raise ValueError(f'Narration has no speech above -45 dBFS: {path}')
    return {'samples': len(a), 'duration': len(a) / SR,
            'speech_start': float(idx[0]) / SR, 'speech_end': float(idx[-1] + 1) / SR}


def narration_text(edit, section):
    """Paragraph text for the cue-time estimates. paragraphs.json (list of {id, text}) or fallback-paragraphs.json
    (stem: text), looked up next to the narration file and one folder up (own voice files live in narration/own).
    Exact file stems win; otherwise the id before the first '-' is used (s3-short -> s3, s6-deep -> s6)."""
    f = rp(section['narration']['file'])
    texts = {}
    for folder in (f.parent, f.parent.parent):
        pj = folder / 'paragraphs.json'
        if pj.exists():
            for p in json.loads(pj.read_text()):
                texts.setdefault(p['id'], p['text'])
        fj = folder / 'fallback-paragraphs.json'
        if fj.exists():
            for k, v in json.loads(fj.read_text()).items():
                if isinstance(v, str):
                    texts.setdefault(k, v)
    for key in (f.stem, f.stem.split('-')[0]):
        if key in texts:
            return texts[key]
    raise KeyError(f'No paragraph text for {f.name}')


def make_plan(edit):
    """Timeline in frames and seconds. Pure arithmetic from edit.json plus decoded narration lengths.

    Crossfade model: every boundary between sections is a picture crossfade of timing.crossfade_s (15 frames). Section k
    owns the frames [start_frame, end_frame); end_frame is where its fade OUT begins, and the next section's fade IN
    begins on that same frame. Section k+1's narration starts on the first frame after the fade, so
    narr_start = start_frame / FPS + crossfade_s (the first section starts its narration after timing.lead_in_s).
    The picture of section k is rendered tail_frames longer than it owns, to be blended with the next section.
    Where the fade begins: at the last speech sample of the narration plus timing.fade_after_speech_s by default;
    narration.cut_offset_s (fade begins that long before the end of the file) and narration.end_at override it."""
    t = edit['timing']
    X = t['crossfade_s']
    XF = round(X * FPS)
    if abs(XF / FPS - X) > 1e-9:
        raise ValueError(f'timing.crossfade_s {X} is not a whole number of frames')
    miss = missing_narration(edit)
    if miss:
        hint = ' Run tools/v1/ingest_voice.py first, or set narration.source to "callum".' if edit.get('narration', {}).get('source') == 'own' else ''
        raise FileNotFoundError('Narration file missing: ' + '; '.join(f'{i}: {p}' for i, p in miss) + '.' + hint)
    secs = []
    prev_frame = 0
    n_secs = len(edit['sections'])
    for k, s in enumerate(edit['sections']):
        n = s['narration']
        start_s = prev_frame / FPS
        fade_in = XF if k > 0 else 0
        if n.get('file'):
            info = narration_info(str(rp(n['file'])))
            N = t['lead_in_s'] if k == 0 else start_s + X
            E = N + info['duration']
            speech_start, speech_end = N + info['speech_start'], N + info['speech_end']
            ea = n.get('end_at')
            if ea:
                # the picture ends plus_s seconds after a narration cue (a beat that outlasts the voice)
                if 'after_narration_end_s' in ea:
                    B = E + ea['after_narration_end_s']
                else:
                    pseudo = {'narr_start': N, 'speech_start': speech_start, 'speech_end': speech_end, 'start_s': N}
                    B = N + phrase_time(edit, pseudo, s, ea['phrase']) + ea['plus_s']
                end_frame = round(B * FPS)
            elif 'cut_offset_s' in n:
                B = E - n['cut_offset_s']
                end_frame = round(B * FPS)
            else:
                B = speech_end + t.get('fade_after_speech_s', 0.0)
                end_frame = math.ceil(B * FPS - 1e-6)  # the fade never starts before the voice has stopped
            nar = {'narr_start': N, 'narr_end': E, 'narr_duration': info['duration'], 'speech_start': speech_start, 'speech_end': speech_end,
                   'cut_offset_s': E - end_frame / FPS}
        else:
            # no narration file: the section's length is fixed (its own recorded voice and/or recitation only)
            end_frame = prev_frame + round(n['duration_s'] * FPS)
            B = end_frame / FPS
            nar = {'narr_start': B, 'narr_end': B, 'narr_duration': 0.0, 'speech_start': None, 'speech_end': None, 'cut_offset_s': 0.0}
        if end_frame - prev_frame < max(fade_in, XF if k < n_secs - 1 else 0) + 1:
            raise ValueError(f"Section {s['id']} has no picture frames")
        tail = XF if k < n_secs - 1 else 0
        secs.append({
            'id': s['id'], 'index': k, 'name': s.get('name', s['id']), 'has_narration': bool(n.get('file')), **nar,
            'start_frame': prev_frame, 'end_frame': end_frame, 'frames': end_frame - prev_frame,
            'fade_in_frames': fade_in, 'tail_frames': tail, 'render_frames': end_frame - prev_frame + tail,
            'start_s': start_s, 'end_s': end_frame / FPS, 'duration_s': (end_frame - prev_frame) / FPS,
        })
        prev_frame = end_frame
    total = prev_frame
    return {'sections': secs, 'total_frames': total, 'duration_s': total / FPS, 'audio_samples': total * SPF, 'crossfade_frames': XF}


@lru_cache(maxsize=None)
def narration_pauses(path):
    """(start, end) of every pause of 0.12 s or more, from ffmpeg silencedetect (noise floor -32 dB)."""
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-af', 'silencedetect=noise=-32dB:d=0.12', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    starts = [float(m.group(1)) for m in re.finditer(r'silence_start:\s*(-?\d+(?:\.\d+)?)', log)]
    ends = [float(m.group(1)) for m in re.finditer(r'silence_end:\s*(-?\d+(?:\.\d+)?)', log)]
    return tuple(zip(starts, ends))


def phrase_time(edit, plan_sec, section, phrase, snap_s=1.3):
    """Section-relative time at which `phrase` starts. Word timing does not exist, so the estimate is the
    proportional character position across the measured speech span. When the phrase follows a full stop or
    comma, it snaps to the end of the nearest pause within snap_s seconds, which is where the voice restarts."""
    text = narration_text(edit, section)
    i = text.find(phrase)
    if i < 0:
        raise ValueError(f'Phrase {phrase!r} not in narration for {section["id"]}')
    n0 = plan_sec['narr_start']
    sp0, sp1 = plan_sec['speech_start'] - n0, plan_sec['speech_end'] - n0
    est = sp0 + (i / len(text)) * (sp1 - sp0)
    t_narr = est
    lead = text[max(0, i - 2):i]
    if lead in ('. ', ', ', '; '):
        pauses = [(s_, e) for s_, e in narration_pauses(str(rp(section['narration']['file']))) if abs(e - est) <= snap_s]
        if lead == '. ':
            # a sentence start follows a sentence-end pause, which is longer than a comma pause: prefer those
            # and only those that no other sentence start is nearer to: the two short closing sentences of s7 would
            # otherwise both snap to the pause before the first of them
            starts = [0] + [m.end() for m in re.finditer(r'\. (?=\S)', text)]
            ests = [sp0 + (j / len(text)) * (sp1 - sp0) for j in starts]
            long_ = [(s_, e) for s_, e in pauses if e - s_ >= 0.4 and min(ests, key=lambda x: abs(x - e)) == est]
            pauses = long_ or pauses
        cands = [e for _, e in pauses]
        if cands:
            t_narr = min(cands, key=lambda e: abs(e - est))
    return max(0.0, n0 + t_narr - plan_sec['start_s'])


# ----------------------------------------------------------------------------------------------
# Arabic: HarfBuzz shaping + Skia outlines (Pillow without raqm cannot join or position Hafs marks)
# ----------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _hb(path):
    import uharfbuzz as hb
    blob = hb.Blob.from_file_path(str(path))
    face = hb.Face(blob)
    return hb, face.upem, hb.Font(face)


def shape_arabic(font_path, text):
    """Shape RTL Arabic. Returns dict(direction, glyphs=[(gid, cluster, x_advance, x_offset, y_offset)], upem)."""
    hb, upem, font = _hb(str(font_path))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.direction = 'rtl'
    buf.script = 'Arab'
    buf.language = 'ar'
    hb.shape(font, buf, {})
    glyphs = [(i.codepoint, i.cluster, p.x_advance, p.x_offset, p.y_offset)
              for i, p in zip(buf.glyph_infos, buf.glyph_positions)]
    return {'direction': buf.direction, 'glyphs': glyphs, 'upem': upem}


@lru_cache(maxsize=None)
def _glyph_path(font_path, gid):
    import skia
    hb, upem, font = _hb(str(font_path))
    path = skia.Path()
    funcs = hb.DrawFuncs()
    funcs.set_move_to_func(lambda x, y, st: path.moveTo(x, y))
    funcs.set_line_to_func(lambda x, y, st: path.lineTo(x, y))
    funcs.set_quadratic_to_func(lambda a, b, c, d, st: path.quadTo(a, b, c, d))
    funcs.set_cubic_to_func(lambda a, b, c, d, e, f, st: path.cubicTo(a, b, c, d, e, f))
    funcs.set_close_path_func(lambda st: path.close())
    font.draw_glyph(gid, funcs)
    return path


def arabic_advance_px(font_path, text, size):
    sh = shape_arabic(font_path, text)
    return sum(g[2] for g in sh['glyphs']) * size / sh['upem']


@lru_cache(maxsize=None)
def arabic_mask(font_path, text, size):
    """Coverage mask (mode L) of one shaped RTL run. Returns (mask, advance_px, baseline_y, pad_x)."""
    import skia
    sh = shape_arabic(font_path, text)
    scale = size / sh['upem']
    adv = sum(g[2] for g in sh['glyphs']) * scale
    padx = math.ceil(size * 0.2)
    asc = math.ceil(size * 1.25)
    desc = math.ceil(size * 0.7)
    w, h = math.ceil(adv) + 2 * padx, asc + desc
    surf = skia.Surface(w, h)
    canvas = surf.getCanvas()
    canvas.clear(skia.ColorTRANSPARENT)
    paint = skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, 255))
    x = float(padx)
    for gid, _cl, xa, xo, yo in sh['glyphs']:
        path = skia.Path(_glyph_path(str(font_path), gid))
        m = skia.Matrix()
        m.setScale(scale, -scale)
        m.postTranslate(x + xo * scale, asc - yo * scale)
        path.transform(m)
        canvas.drawPath(path, paint)
        x += xa * scale
    arr = surf.makeImageSnapshot().toarray()
    mask = Image.fromarray(np.ascontiguousarray(arr[:, :, 3]), 'L')
    return mask, adv, asc, padx


# ----------------------------------------------------------------------------------------------
# Quran text and the ribbon
# ----------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def verse_words(qpc_json, key):
    d = json.loads(Path(qpc_json).read_text())
    text = d[key]['text']
    text = re.sub(r'[\s\u00a0]*[\u0660-\u0669\u06dd]+\s*$', '', text)  # strip trailing ayah-number glyph
    return tuple(w.replace('\u00a0', '') for w in text.split(' ') if w.strip('\u00a0'))


def window_words(a, b, n_words, per=4):
    """Counter 'a-b/20' lights words per*a-(per-1) .. per*b (window k of 20 = words 4k-3..4k)."""
    lo = per * a - (per - 1)
    hi = per * b
    return max(1, lo), min(n_words, hi)


@lru_cache(maxsize=None)
def font(path, size, _=0):
    return ImageFont.truetype(str(path), int(size))


def ink_extent(fp, words, size, pct=85):
    """Ink height above and below the baseline at this size, as the pct-th percentile over all words.
    The tallest outliers are waqf signs; letting them poke into the line gap keeps the strip compact."""
    above, below = [], []
    for w in words:
        mask, adv, asc, padx = arabic_mask(str(fp), w, size)
        bb = mask.getbbox()
        if bb:
            above.append(asc - bb[1])
            below.append(bb[3] - asc)
    return math.ceil(np.percentile(above, pct)), math.ceil(np.percentile(below, pct))


def layout_ribbon(edit, layer):
    """Return (rows, size, pitch, above). rows = list of lines, each [(word_index, x_left, x_right)]."""
    fp = edit['fonts']['arabic']
    words = verse_words(edit['quran']['qpc_json'], layer['verse'])
    bx, by, bw, bh = layer['box']
    size = layer['font_size']
    while True:
        space = max(arabic_advance_px(fp, ' ', size), 0.30 * size)
        widths = [arabic_advance_px(fp, w, size) for w in words]
        lines, cur, cur_w = [], [], 0.0
        for i, w in enumerate(widths):
            add = w if not cur else w + space
            if cur and cur_w + add > bw:
                lines.append(cur)
                cur, cur_w = [i], w
            else:
                cur.append(i)
                cur_w += add
        if cur:
            lines.append(cur)
        above, below = ink_extent(fp, words, size, layer.get('extent_percentile', 85))
        pitch = math.ceil(above + below + layer.get('line_gap', 0.12) * size)
        if len(lines) * pitch <= bh or size <= edit['min_text_px']:
            break
        size -= 2
    placed = []
    for li, idxs in enumerate(lines):
        total = sum(widths[i] for i in idxs) + space * (len(idxs) - 1)
        gap = space
        last = li == len(lines) - 1
        if not last and len(idxs) > 1:
            extra = (bw - total) / (len(idxs) - 1)
            if extra <= 0.6 * size:
                gap = space + extra
        x_right = bx + bw
        row = []
        for i in idxs:
            row.append((i, x_right - widths[i], x_right))
            x_right -= widths[i] + gap
        placed.append(row)
    return placed, size, pitch, above


def paint_ribbon_layers(edit, pal, layer):
    """Base dim ribbon and one lit overlay per counter state. Returns (base_img, [(img, (a,b), lit_words)])."""
    fp = edit['fonts']['arabic']
    words = verse_words(edit['quran']['qpc_json'], layer['verse'])
    placed, size, pitch, above = layout_ribbon(edit, layer)
    W, H = edit['canvas']['w'], edit['canvas']['h']
    by = layer['box'][1]
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for li, row in enumerate(placed):
        for i, xl, xr in row:
            mask, adv, asc, padx = arabic_mask(str(fp), words[i], size)
            top = by + li * pitch + round(0.05 * size) + above - asc
            base.paste(Image.new('RGBA', mask.size, pal.dim + (255,)), (round(xl) - padx, top), mask)
    states = []
    per = edit['quran']['words_per_window']
    for win in layer['windows']:
        a, b = win['counter']
        if layer.get('mapping_mode', 'observed') == 'observed' and win.get('words_observed'):
            lo, hi = win['words_observed']
        else:
            lo, hi = window_words(a, b, len(words), per)
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        plate_mask = Image.new('L', (W, H), 0)
        pm = ImageDraw.Draw(plate_mask)
        text_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        padx_plate = round(size * 0.22)
        for li, row in enumerate(placed):
            lit = [(i, xl, xr) for i, xl, xr in row if lo <= i + 1 <= hi]
            if not lit:
                continue
            xl0 = min(x[1] for x in lit) - padx_plate
            xr0 = max(x[2] for x in lit) + padx_plate
            ytop = by + li * pitch
            box = (round(xl0), ytop, round(xr0), ytop + pitch - 2)
            d.rounded_rectangle(box, radius=10, fill=pal.blue + (255,))
            pm.rounded_rectangle(box, radius=10, fill=255)
            for i, xl, xr in lit:
                mask, adv, asc, padx = arabic_mask(str(fp), words[i], size)
                top = by + li * pitch + round(0.05 * size) + above - asc
                text_layer.paste(Image.new('RGBA', mask.size, pal.paper + (255,)), (round(xl) - padx, top), mask)
        # lit text only inside the plates: a mark that rises above a plate stays dim instead of vanishing
        r, g, b_, al = text_layer.split()
        text_layer.putalpha(ImageChops.multiply(al, plate_mask))
        img.alpha_composite(text_layer)
        states.append((img, (a, b), (lo, hi)))
    return base, states, size


# ----------------------------------------------------------------------------------------------
# Latin overlay painters (drawn at 2x then reduced)
# ----------------------------------------------------------------------------------------------
class Art:
    def __init__(self, w, h, bg=None):
        self.w, self.h = w, h
        self.im = Image.new('RGBA', (w * SS, h * SS), bg or (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def rrect(self, box, radius=0, fill=None, outline=None, width=0):
        x0, y0, x1, y1 = [v * SS for v in box]
        self.d.rounded_rectangle((x0, y0, x1, y1), radius=radius * SS, fill=fill, outline=outline, width=width * SS)

    def ellipse(self, box, outline, width):
        self.d.ellipse([v * SS for v in box], outline=outline, width=width * SS)

    def text(self, xy, s, fnt_path, size, color, anchor='ls'):
        self.d.text((xy[0] * SS, xy[1] * SS), s, font=font(fnt_path, size * SS), fill=color + (255,), anchor=anchor)

    def finish(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def text_width(fnt_path, size, s):
    return font(fnt_path, size * SS).getlength(s) / SS


def wrap_text(fnt_path, size, s, max_w):
    """Wrap at ' · ' groups first, then at spaces."""
    if text_width(fnt_path, size, s) <= max_w:
        return [s]
    if ' \u00b7 ' in s:
        parts = s.split(' \u00b7 ')
        lines, cur = [], ''
        for j, p in enumerate(parts):
            piece = p + (' \u00b7' if j < len(parts) - 1 else '')
            trial = piece if not cur else cur + ' ' + piece
            if cur and text_width(fnt_path, size, trial) > max_w:
                lines.append(cur)
                cur = piece
            else:
                cur = trial
        lines.append(cur)
        if all(text_width(fnt_path, size, ln) <= max_w for ln in lines):
            return lines
    words, lines, cur = s.split(' '), [], ''
    for w in words:
        trial = w if not cur else cur + ' ' + w
        if cur and text_width(fnt_path, size, trial) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    lines.append(cur)
    return lines


def line_font(edit, ln):
    return edit['fonts']['latin_bold' if ln.get('bold', True) else 'latin']


def paint_paper(edit, pal):
    W, H = edit['canvas']['w'], edit['canvas']['h']
    return Image.new('RGBA', (W, H), pal.paper + (255,))


def paint_card(edit, pal, layer):
    W, H = edit['canvas']['w'], edit['canvas']['h']
    art = Art(W, H, bg=pal.paper + (255,))
    maxw = layer.get('max_width', 1700)
    rows = []
    for ln in layer['lines']:
        size, fp = ln['size'], line_font(edit, ln)
        while text_width(fp, size, ln['text']) > maxw and size > edit['min_text_px']:
            size -= 2
        rows.append((ln, size, fp))
    total = sum(r[1] * 1.2 + r[0].get('gap_after', 0) for r in rows) - rows[-1][0].get('gap_after', 0)
    y = (H - total) / 2 if layer.get('valign', 'middle') == 'middle' else layer.get('y', 200)
    for ln, size, fp in rows:
        baseline = y + size * 0.95
        w = text_width(fp, size, ln['text'])
        art.text(((W - w) / 2, baseline), ln['text'], fp, size, pal.get(ln.get('color', 'ink')))
        y += size * 1.2 + ln.get('gap_after', 0)
    return art.finish()


def paint_plate(edit, pal, layer):
    W, H = edit['canvas']['w'], edit['canvas']['h']
    pad = layer.get('pad', 24)
    maxw = layer.get('max_width')
    inner = (maxw - 2 * pad) if maxw else None
    rows = []
    for ln in layer['lines']:
        fp, size = line_font(edit, ln), ln['size']
        for part in (wrap_text(fp, size, ln['text'], inner) if inner else [ln['text']]):
            rows.append((part, ln, fp, size))
    tw = max(text_width(r[2], r[3], r[0]) for r in rows)
    th = sum(r[3] * 1.25 for r in rows)
    pw, ph = tw + 2 * pad, th + 2 * pad
    x, y = layer['pos']
    anchor = layer.get('anchor', 'tl')
    if anchor == 'tl':
        x0, y0 = x, y
    elif anchor == 'tr':
        x0, y0 = x - pw, y
    elif anchor == 'bl':
        x0, y0 = x, y - ph
    elif anchor == 'br':
        x0, y0 = x - pw, y - ph
    elif anchor == 'bc':
        x0, y0 = x - pw / 2, y - ph
    elif anchor == 'c':
        x0, y0 = x - pw / 2, y - ph / 2
    else:
        raise ValueError(anchor)
    art = Art(W, H)
    fill = layer.get('fill', 'paper')
    border = layer.get('border')
    if fill or border:
        art.rrect((x0, y0, x0 + pw, y0 + ph), radius=layer.get('radius', 14),
                  fill=(pal.get(fill) + (255,)) if fill else None,
                  outline=(pal.get(border) + (255,)) if border else None, width=4 if border else 0)
    yy = y0 + pad
    for part, ln, fp, size in rows:
        art.text((x0 + pad, yy + size * 0.98), part, fp, size, pal.get(ln.get('color', 'ink')))
        yy += size * 1.25
    return art.finish()


def paint_pin(edit, pal, layer):
    W, H = edit['canvas']['w'], edit['canvas']['h']
    fp = edit['fonts']['latin_bold']
    size = layer['size']
    x, y = layer['pos']
    tw = text_width(fp, size, layer['text'])
    padx, pady = 26, 12
    art = Art(W, H)
    art.ellipse((x, y, x + tw + 2 * padx, y + size * 1.25 + 2 * pady), pal.red + (255,), 5)
    art.text((x + padx, y + pady + size * 0.98), layer['text'], fp, size, pal.ink)
    return art.finish()


def paint_counter(edit, pal, layer, a, b):
    W, H = edit['canvas']['w'], edit['canvas']['h']
    art = Art(W, H)
    fp = edit['fonts']['latin_bold']
    x, y = layer['counter_pos']
    text = layer.get('counter_template', 'Portion {a} of {n} on the lens').format(a=a, b=b, n=layer.get('counter_total', 20))
    art.text((x, y + layer['counter_size'] * 0.95), text, fp, layer['counter_size'], pal.blue)
    return art.finish()


# ----------------------------------------------------------------------------------------------
# architecture diagram and API card
# ----------------------------------------------------------------------------------------------
def mix_colour(a, b, m):
    return tuple(round(x * (1 - m) + y * m) for x, y in zip(a, b))


def wrap_clauses(fnt_path, size, text, max_w):
    """Wrap text that holds ' \u00b7 ' separators so a line break always falls at a separator, and the separator is dropped
    there (no line starts or ends with a dangling dot). Clauses that fit together keep their dot; a clause wider than
    the line wraps by words."""
    clauses = text.split(' \u00b7 ')
    if len(clauses) == 1:
        return wrap_text(fnt_path, size, text, max_w)
    lines, cur = [], None
    for c in clauses:
        cand = c if cur is None else cur + ' \u00b7 ' + c
        if cur is not None and text_width(fnt_path, size, cand) > max_w:
            lines.append(cur)
            cur = None
            cand = c
        if text_width(fnt_path, size, cand) > max_w:
            wrapped = wrap_text(fnt_path, size, cand, max_w)
            lines.extend(wrapped[:-1])
            cur = wrapped[-1]
        else:
            cur = cand
    lines.append(cur)
    return lines


def node_parts(nd):
    """[title, sub, sub, ...] of a diagram node: explicit 'title' + 'subs', or 'text' split on ' \u00b7 '."""
    if 'title' in nd:
        return [nd['title']] + list(nd.get('subs', []))
    return nd['text'].split(' \u00b7 ')


def diagram_layout(edit, layer):
    """Geometry of the architecture diagram: per node box, wrapped text lines, tag; row heights; arrow anchors.
    Raises if the diagram does not fit the safe area (60 px sides, bottom margin from edit)."""
    W, H = edit['canvas']['w'], edit['canvas']['h']
    g = layer.get('geometry', {})
    pad, mx, gap, wrap_gap = g.get('pad', 22), g.get('margin_x', 60), g.get('gap', 60), g.get('wrap_gap', 90)
    title_px, sub_px, tag_px = layer['title_px'], layer['sub_px'], layer['tag_px']
    bold, reg = edit['fonts']['latin_bold'], edit['fonts']['latin']
    nodes = []
    for nd in layer['nodes']:
        parts = node_parts(nd)
        inner = nd['w'] - 2 * pad
        title_lines = wrap_clauses(bold, title_px, parts[0], inner)
        sub_lines = [wrap_clauses(reg, sub_px, sp, inner) for sp in parts[1:]]
        subline = wrap_text(reg, sub_px, nd['subline'], inner) if nd.get('subline') else []
        for fp_, px_, lines_ in [(bold, title_px, title_lines)] + [(reg, sub_px, x_) for x_ in sub_lines + [subline]]:
            for ln_ in lines_:
                if text_width(fp_, px_, ln_) > inner + 1:
                    raise ValueError(f"node {nd['n']}: {ln_!r} is wider than the node ({nd['w']} px)")
        tag = nd.get('tag')
        tag_w = text_width(bold, tag_px, tag['text']) + 36 if tag else 0
        h = pad + len(title_lines) * round(title_px * 1.2)
        h += sum(len(x) for x in sub_lines) * round(sub_px * 1.2) + len(subline) * round(sub_px * 1.2) + (8 if subline else 0)
        if tag:
            h += 14 + round(tag_px * 1.2) + 12
        h += pad
        nodes.append(dict(nd, title_lines=title_lines, sub_lines=sub_lines, subline_lines=subline, tag_w=tag_w, h_need=h))
    rows = sorted({n['row'] for n in nodes})
    row_h = {r: max(n['h_need'] for n in nodes if n['row'] == r) for r in rows}
    row_y = {}
    y = g.get('row0_y', 250)
    for r in rows:
        row_y[r] = y
        y += row_h[r] + wrap_gap
    bottom = row_y[rows[-1]] + row_h[rows[-1]]
    if bottom > H - edit.get('bottom_margin_px', 54):
        raise ValueError(f'diagram bottom {bottom} is inside the {edit.get("bottom_margin_px", 54)} px bottom margin')
    for r in rows:
        row_nodes = [n for n in nodes if n['row'] == r]
        row_w = sum(n['w'] for n in row_nodes) + gap * (len(row_nodes) - 1)
        if row_w > W - 2 * mx:
            raise ValueError(f'diagram row {r} is {row_w} px wide, the safe width is {W - 2 * mx}')
        x = mx + (W - 2 * mx - row_w) / 2
        for n in row_nodes:
            n.update(x=x, y=row_y[r], h=row_h[r])
            x += n['w'] + gap
    return nodes, row_y, row_h, dict(pad=pad, gap=gap, wrap_gap=wrap_gap, title_px=title_px, sub_px=sub_px, tag_px=tag_px)


def _arrowhead(art, tip, direction, size, colour):
    x, y = tip
    if direction == 'right':
        pts = [(x, y), (x - size, y - size * 0.6), (x - size, y + size * 0.6)]
    else:  # down
        pts = [(x, y), (x - size * 0.6, y - size), (x + size * 0.6, y - size)]
    art.d.polygon([(px * SS, py * SS) for px, py in pts], fill=colour + (255,))


def _line(art, pts, width, colour):
    art.d.line([(px * SS, py * SS) for px, py in pts], fill=colour + (255,), width=width * SS, joint='curve')


def paint_diagram(edit, pal, layer):
    """Return [{name, img, cue, node}] in reveal order. Each node image holds its box and the arrow leading into it;
    node 6 may split into an early and a late image (late items appear on a later cue)."""
    W, H = edit['canvas']['w'], edit['canvas']['h']
    nodes, row_y, row_h, g = diagram_layout(edit, layer)
    bold, reg = edit['fonts']['latin_bold'], edit['fonts']['latin']
    card = mix_colour(pal.paper, (255, 255, 255), 0.45)
    out = []
    by_n = {n['n']: n for n in nodes}
    prev = None
    for nd in nodes:
        tagc = pal.get(nd['tag']['color']) if nd.get('tag') else None
        border = tagc if tagc else pal.ink
        solid = nd.get('style') == 'solid'
        late = nd.get('late')
        late_items = set(late['items']) if late else set()

        def draw(art, stage):
            if stage == 0:
                art.rrect((nd['x'], nd['y'], nd['x'] + nd['w'], nd['y'] + nd['h']), radius=24,
                          fill=(pal.blue if solid else card) + (255,), outline=border + (255,), width=5)
            yy = nd['y'] + g['pad']
            tcol = pal.paper if solid else pal.ink
            for ln in nd['title_lines']:
                if stage == 0:
                    art.text((nd['x'] + g['pad'], yy + g['title_px'] * 0.95), ln, bold, g['title_px'], tcol)
                yy += round(g['title_px'] * 1.2)
            for si, lines in enumerate(nd['sub_lines']):
                for ln in lines:
                    if (stage == 0) == (f'sub:{si}' not in late_items):
                        art.text((nd['x'] + g['pad'], yy + g['sub_px'] * 0.95), ln, reg, g['sub_px'], tcol)
                    yy += round(g['sub_px'] * 1.2)
            if nd['subline_lines']:
                yy += 8
                for ln in nd['subline_lines']:
                    if (stage == 0) == ('subline' not in late_items):
                        art.text((nd['x'] + g['pad'], yy + g['sub_px'] * 0.95), ln, reg, g['sub_px'], pal.blue)
                    yy += round(g['sub_px'] * 1.2)
            if nd.get('tag') and (stage == 0) == ('tag' not in late_items):
                yy += 14
                ph = round(g['tag_px'] * 1.2)
                art.rrect((nd['x'] + g['pad'], yy, nd['x'] + g['pad'] + nd['tag_w'], yy + ph), radius=ph // 2, fill=tagc + (255,))
                art.text((nd['x'] + g['pad'] + 18, yy + g['tag_px'] * 1.0), nd['tag']['text'], bold, g['tag_px'], pal.paper)

        def arrow(art):
            if prev is None:
                return
            if prev['row'] == nd['row']:
                yc = nd['y'] + nd['h'] / 2
                x0, x1 = prev['x'] + prev['w'], nd['x']
                _line(art, [(x0 + 4, yc), (x1 - 14, yc)], 6, pal.ink)
                _arrowhead(art, (x1 - 3, yc), 'right', 22, pal.ink)
            else:  # wrap: down from the end of the previous row, back to the start of this one
                x0, y0 = prev['x'] + prev['w'] / 2, prev['y'] + prev['h']
                x1, y1 = nd['x'] + nd['w'] / 2, nd['y']
                ym = (y0 + y1) / 2
                _line(art, [(x0, y0 + 4), (x0, ym), (x1, ym), (x1, y1 - 16)], 6, pal.ink)
                _arrowhead(art, (x1, y1 - 3), 'down', 22, pal.ink)

        a0 = Art(W, H)
        arrow(a0)
        draw(a0, 0)
        out.append({'name': f"node{nd['n']}", 'img': a0.finish(), 'cue': nd['cue'], 'cue_offset_s': nd.get('cue_offset_s', 0.0), 'node': nd['n']})
        if late:
            a1 = Art(W, H)
            draw(a1, 1)
            out.append({'name': f"node{nd['n']}-late", 'img': a1.finish(), 'cue': late['cue'], 'node': nd['n']})
        prev = nd
    af = layer.get('audio_flow')
    if af:
        a, b = by_n[af['from']], by_n[af['to']]
        art = Art(W, H)
        yl = row_y[a['row']] - af.get('rise', 30)
        x0, x1 = a['x'] + a['w'] / 2, b['x'] + b['w'] / 2
        red = pal.red
        _line(art, [(x0, a['y'] - 4), (x0, yl), (x1, yl), (x1, b['y'] - 16)], af.get('width', 4), red)
        _arrowhead(art, (x1, b['y'] - 3), 'down', 18, red)
        lw = text_width(bold, af['label_px'], af['label'])
        art.text(((x0 + x1) / 2 - lw / 2, yl - 16), af['label'], bold, af['label_px'], red)
        out.append({'name': 'audio-flow', 'img': art.finish(), 'cue': af['cue'], 'node': None})
    return out


def parse_markup(s):
    """'text with `identifiers`' -> tokens [(text, mono, space_before)]. A backtick run is one unbreakable token."""
    tokens, last_end = [], 0
    for m in re.finditer(r'`([^`]+)`|(\S+)', s):
        space = m.start() > last_end
        tokens.append((m.group(1), True, space) if m.group(1) is not None else (m.group(2), False, space))
        last_end = m.end()
    return tokens


def plain_from_markup(s):
    return s.replace('`', '')


def wrap_tokens(tokens, widths, space_w, max_w):
    """Greedy wrap of tokens at word boundaries; a mono identifier is never split. Returns lines of token indices."""
    lines, cur, cur_w = [], [], 0.0
    for i, (tok, mono, sp) in enumerate(tokens):
        add = widths[i] + (space_w if (cur and sp) else 0)
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [i], widths[i]
        else:
            cur.append(i)
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def read_source_lines(path, numbers):
    lines = Path(path).read_text().split('\n')
    return [lines[n - 1].strip() for n in numbers]


def wrap_code(text_lines, mono_path, px, max_w):
    """Wrap verbatim source lines at spaces for a monospace panel; return the visual lines. Raises when a single
    token is wider than the panel (an identifier must never be truncated)."""
    out = []
    for ln in text_lines:
        words = ln.split(' ')
        cur = ''
        for w in words:
            if text_width(mono_path, px, w) > max_w:
                raise ValueError(f'code token {w!r} is wider than the panel')
            trial = w if not cur else cur + ' ' + w
            if cur and text_width(mono_path, px, trial) > max_w:
                out.append(cur)
                cur = w
            else:
                cur = trial
        out.append(cur)
    return out


def api_card_layout(edit, layer):
    bold, reg, mono = edit['fonts']['latin_bold'], edit['fonts']['latin'], edit['fonts']['mono']
    px = layer['line_px']
    lx, ly, lw = layer['left']
    rows = []
    for raw in layer['lines']:
        toks = parse_markup(raw)
        widths = [text_width(mono if m else reg, px, t) for t, m, _ in toks]
        space_w = text_width(reg, px, ' ')
        lines = wrap_tokens(toks, widths, space_w, lw)
        for ln in lines:
            if sum(widths[i] for i in ln) > lw + 1:
                raise ValueError(f'API line token wider than the card: {raw!r}')
        rows.append((toks, widths, lines))
    code = layer['code']
    rx, ry, rw = layer['right']
    src_lines = read_source_lines(rp(code['source']), code['lines'])
    pad = 26
    wrapped = wrap_code(src_lines, mono, code['px'], rw - 2 * pad)
    return rows, src_lines, wrapped


def paint_api_card(edit, pal, layer):
    W, H = edit['canvas']['w'], edit['canvas']['h']
    bold, reg, mono = edit['fonts']['latin_bold'], edit['fonts']['latin'], edit['fonts']['mono']
    rows, src_lines, wrapped = api_card_layout(edit, layer)
    art = Art(W, H, bg=pal.paper + (255,))
    px = layer['line_px']
    lx, ly, lw = layer['left']
    rx, ry, rw = layer['right']
    art.text((lx, 118), layer['title'], bold, layer['title_px'], pal.ink)
    code = layer['code']
    art.text((rx, 118), code['label'], bold, code['label_px'], pal.blue)
    y = ly
    lh = round(px * 1.32)
    space_w = text_width(reg, px, ' ')
    for toks, widths, lines in rows:
        for ln in lines:
            x = lx
            for j, i in enumerate(ln):
                t, m, sp = toks[i]
                if j > 0 and sp:
                    x += space_w
                art.text((x, y + px * 0.95), t, mono if m else reg, px, pal.blue if m else pal.ink)
                x += widths[i]
            y += lh
        y += 14
    cp = code['px']
    clh = round(cp * 1.25)
    pad = 26
    ph = len(wrapped) * clh + 2 * pad
    art.rrect((rx, ry, rx + rw, ry + ph), radius=18, fill=pal.ink + (255,))
    yy = ry + pad
    for ln in wrapped:
        art.text((rx + pad, yy + cp * 0.95), ln, mono, cp, pal.paper)
        yy += clh
    bottom = max(y, ry + ph)
    if bottom > H - edit.get('bottom_margin_px', 54):
        raise ValueError(f'API card bottom {bottom} is inside the bottom margin')
    return art.finish()


# ----------------------------------------------------------------------------------------------
# layer resolution: every layer becomes inputs + overlay stages with section-relative timing
# ----------------------------------------------------------------------------------------------
def footage_spec(edit, layer, dur_s, in_override=None):
    src = edit['footage'][layer['source']]
    t_in = snap_frame(layer['in'] if in_override is None else in_override)
    clip_len = max(layer['out'] - t_in, 0.5)
    return src, t_in, clip_len


def resolve_section(edit, plan, section, pal, workdir):
    """Return list of stage dicts: {kind, png|footage..., start, end, fade, x, y}."""
    ps = next(p for p in plan['sections'] if p['id'] == section['id'])
    dur = ps['duration_s']
    stages = []
    foot_by_id = {}
    for li, layer in enumerate(section['layers']):
        ty = layer['type']
        start = layer.get('start_s', 0.0)
        if 'appear_phrase' in layer:
            start = phrase_time(edit, ps, section, layer['appear_phrase'])
        if 'appear_before_narration_end_s' in layer:
            start = ps['narr_end'] - ps['start_s'] - layer['appear_before_narration_end_s']
        start += layer.get('appear_offset_s', 0.0)
        end = layer.get('end_s')
        if 'end_phrase' in layer:
            end = phrase_time(edit, ps, section, layer['end_phrase'])
        fade = layer.get('fade_s', 0.0)
        tag = f"{section['id']}-{li}"

        def save(img, name):
            p = workdir / 'overlays' / f'{tag}-{name}.png'
            p.parent.mkdir(parents=True, exist_ok=True)
            img.save(p)
            return p

        if ty == 'paper':
            stages.append({'kind': 'image', 'png': save(paint_paper(edit, pal), 'paper'), 'start': 0, 'end': None, 'fade': 0, 'x': 0, 'y': 0, 'base': li == 0})
        elif ty == 'card':
            stages.append({'kind': 'image', 'png': save(paint_card(edit, pal, layer), 'card'), 'start': start, 'end': end, 'fade': fade, 'x': 0, 'y': 0, 'base': li == 0})
        elif ty in ('plate', 'pin'):
            img = paint_plate(edit, pal, layer) if ty == 'plate' else paint_pin(edit, pal, layer)
            stages.append({'kind': 'image', 'png': save(img, ty), 'start': start, 'end': end, 'fade': fade, 'x': 0, 'y': 0, 'base': False})
        elif ty == 'footage':
            in_override = None
            if 'in_align' in layer:
                # place the source moment source_s exactly on the narration cue: in = source_s - (cue time - layer start)
                al = layer['in_align']
                in_override = al['source_s'] - (phrase_time(edit, ps, section, al['phrase']) - start)
                if in_override < 0:
                    raise ValueError(f"{section['id']}: aligning {al['source_s']} s to '{al['phrase']}' needs a negative in-point")
            src, t_in, clip_len = footage_spec(edit, layer, dur, in_override)
            x, y, w, h = layer['dest']
            stages.append({'kind': 'footage', 'src': src, 'file': rp(src['file']), 'in': t_in, 'len': clip_len,
                           'crop': layer['crop'], 'dest': layer['dest'], 'start': start, 'end': end, 'fade': fade,
                           'freeze': layer.get('freeze_after', False), 'x': x, 'y': y, 'base': False})
            foot_by_id[layer.get('id', 'main')] = layer
        elif ty == 'ribbon':
            base, states, used = paint_ribbon_layers(edit, pal, layer)
            f = foot_by_id[layer['follow']]
            stages.append({'kind': 'image', 'png': save(base, 'ribbon-dim'), 'start': 0, 'end': None, 'fade': 0, 'x': 0, 'y': 0, 'base': False})
            times = [f.get('start_s', 0.0) + (w['from_source_s'] - f['in']) for w in layer['windows']]
            times[0] = 0.0
            for si, (img, (a, b), lit) in enumerate(states):
                t1 = times[si + 1] if si + 1 < len(times) else None
                stages.append({'kind': 'image', 'png': save(img, f'ribbon-lit{si}'), 'start': times[si], 'end': t1, 'fade': 0, 'x': 0, 'y': 0, 'base': False, 'sharp': True})
                stages.append({'kind': 'image', 'png': save(paint_counter(edit, pal, layer, a, b), f'counter{si}'), 'start': times[si], 'end': t1, 'fade': 0, 'x': 0, 'y': 0, 'base': False, 'sharp': True})
        elif ty == 'diagram':
            motion = None
            sl = layer.get('slide')
            if sl:
                if 'before_narration_end_s' in sl:
                    t0 = ps['narr_end'] - ps['start_s'] - sl['before_narration_end_s']
                else:
                    t0 = phrase_time(edit, ps, section, sl['phrase']) + sl.get('offset_s', 0.0)
                motion = {'kind': 'out_up', 't0': t0, 'd': sl['duration_s']}
            for it in paint_diagram(edit, pal, layer):
                stages.append({'kind': 'image', 'png': save(it['img'], it['name']), 'start': phrase_time(edit, ps, section, it['cue']) + it.get('cue_offset_s', 0.0), 'end': None,
                               'fade': layer.get('fade_s', 0.3), 'x': 0, 'y': 0, 'base': False, 'motion': motion, 'name': it['name']})
        elif ty == 'api_card':
            motion = {'kind': 'in_up', 't0': start, 'd': layer.get('slide_in_s', 1.0)}
            stages.append({'kind': 'image', 'png': save(paint_api_card(edit, pal, layer), 'api-card'), 'start': start, 'end': end, 'fade': 0,
                           'x': 0, 'y': 0, 'base': False, 'motion': motion, 'name': 'api-card'})
        else:
            raise ValueError(f'Unknown layer type {ty}')
    return stages, ps


def frame_mid(t):
    """Boundary placed half a frame before frame t so the compare is never on a tie."""
    return round(t * FPS) / FPS - 0.5 / FPS


def enable_expr(start, end):
    if start <= 0 and end is None:
        return None
    parts = []
    if start > 0:
        parts.append(f'gte(t,{frame_mid(start):.5f})')
    if end is not None:
        parts.append(f'lt(t,{frame_mid(end):.5f})')
    return '*'.join(parts) if len(parts) > 1 else parts[0]


def motion_y(motion, H):
    """ffmpeg overlay y expression for a vertical push: out_up slides the layer up and out of the frame, in_up slides it
    in from below. Smoothstep easing over motion['d'] seconds starting at motion['t0']."""
    p = f"min(1,max(0,(t-{motion['t0']:.4f})/{motion['d']:.4f}))"
    ease = f"({p}*{p}*(3-2*{p}))"
    if motion['kind'] == 'out_up':
        return f"-{H}*{ease}"
    if motion['kind'] == 'in_up':
        return f"{H}*(1-{ease})"
    raise ValueError(motion['kind'])


def build_section_cmd(edit, plan, section, pal, workdir, out_path):
    stages, ps = resolve_section(edit, plan, section, pal, workdir)
    frames = ps['render_frames']  # the section's own frames plus the tail that is blended with the next section
    dur = frames / FPS
    V = edit['video']
    W, H = edit['canvas']['w'], edit['canvas']['h']
    cmd = ['ffmpeg', '-v', 'error', '-y']
    chains, cur = [], None
    for si, st in enumerate(stages):
        if st['kind'] == 'image':
            cmd += ['-loop', '1', '-framerate', str(FPS), '-t', f'{dur + 1:.3f}', '-i', st['png']]
            idx = sum(1 for c in cmd if c == '-i') - 1
            if st.get('base'):
                chains.append(f'[{idx}:v]format=gbrp[base]')
                cur = 'base'
                continue
            lab = f'ov{si}'
            if st['fade'] > 0:
                chains.append(f"[{idx}:v]format=rgba,fade=t=in:st={st['start']:.3f}:d={st['fade']:.3f}:alpha=1,format=gbrap[{lab}]")
            else:
                chains.append(f'[{idx}:v]format=gbrap[{lab}]')
            en = enable_expr(st['start'], st['end'])
            nxt = f'o{si}'
            if st.get('motion'):
                chains.append(f"[{cur}][{lab}]overlay=x={st['x']}:y='{motion_y(st['motion'], H)}':eval=frame:format=gbrp:eof_action=repeat" + (f":enable='{en}'" if en else '') + f'[{nxt}]')
            else:
                chains.append(f"[{cur}][{lab}]overlay=x={st['x']}:y={st['y']}:format=gbrp:eof_action=repeat" + (f":enable='{en}'" if en else '') + f'[{nxt}]')
            cur = nxt
        else:
            src = st['src']
            need = dur - st['start'] + 0.5
            length = st['len'] if st['freeze'] or st['len'] < need else need
            cmd += ['-ss', f"{st['in']:.6f}", '-t', f'{max(length, 0.2):.6f}', '-i', st['file']]
            idx = sum(1 for c in cmd if c == '-i') - 1
            cx, cy, cw, ch = st['crop']
            dx, dy, dw, dh = st['dest']
            lab = f'fg{si}'
            ch_ = (f"[{idx}:v]fps=fps={FPS}:start_time=0:round=near,crop={cw}:{ch}:{cx}:{cy},"
                   f"scale=w={dw}:h={dh}:flags=lanczos+accurate_rnd+full_chroma_int:in_range={src['range']}:in_color_matrix={src['matrix']},"
                   f"format=gbrp,setpts=PTS-STARTPTS+{st['start']:.5f}/TB")
            if st['freeze']:
                ch_ += ',tpad=stop=-1:stop_mode=clone'
            if st['fade'] > 0:  # alpha fade-in: over paper at the film start, or over the title card (a crossfade)
                ch_ += f",format=rgba,fade=t=in:st={st['start']:.3f}:d={st['fade']:.3f}:alpha=1,format=gbrap"
            chains.append(ch_ + f'[{lab}]')
            en = enable_expr(st['start'], st['end'])
            nxt = f'o{si}'
            chains.append(f"[{cur}][{lab}]overlay=x={dx}:y={dy}:format=gbrp:eof_action=repeat" + (f":enable='{en}'" if en else '') + f'[{nxt}]')
            cur = nxt
    chains.append(f"[{cur}]scale=w=iw:h=ih:flags=accurate_rnd+full_chroma_int:in_range=full:out_range=tv:out_color_matrix=bt709,"
                  f"format=yuv420p,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709[vout]")
    cmd += ['-filter_complex', ';'.join(chains), '-map', '[vout]', '-an', '-frames:v', str(frames), '-r', str(FPS),
            '-c:v', 'libx264', '-preset', V['preset'], '-crf', str(V.get('intermediate_crf', V['crf'])), '-pix_fmt', 'yuv420p',
            '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-x264-params', 'colorprim=bt709:transfer=bt709:colormatrix=bt709:fullrange=off', '-movflags', '+faststart', out_path]
    return cmd


def render_sections(edit, plan, only=None):
    pal = Palette(edit)
    work = rp(edit['work_dir'])
    work.mkdir(parents=True, exist_ok=True)
    for s in edit['sections']:
        if only and s['id'] not in only:
            continue
        out = work / f"{s['id']}.mp4"
        cmd = build_section_cmd(edit, plan, s, pal, work, out)
        (work / f"{s['id']}.cmd.txt").write_text(' '.join(f"'{c}'" if (' ' in str(c) or ';' in str(c)) else str(c) for c in cmd) + '\n')
        run(cmd)
        n = int(run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames',
                     '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip())
        want = next(p['render_frames'] for p in plan['sections'] if p['id'] == s['id'])
        if n != want:
            raise RuntimeError(f"{s['id']}: rendered {n} frames, planned {want}")
        print(f"rendered {s['id']}: {n} frames", flush=True)


# ----------------------------------------------------------------------------------------------
# audio
# ----------------------------------------------------------------------------------------------
def decode_pcm(path, start, dur):
    """Float32 stereo 48 kHz excerpt, zero-padded when the source is shorter or start is negative."""
    n = round(dur * SR)
    out = np.zeros((n, 2), dtype=np.float32)
    lead = 0
    if start < 0:
        lead = round(-start * SR)
        dur += start
        start = 0.0
    if dur <= 0:
        return out
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{start:.6f}', '-t', f'{dur:.6f}', '-i', str(path), '-vn',
                                   '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'])
    a = np.frombuffer(raw, dtype='<f4').reshape(-1, 2)
    m = min(len(a), n - lead)
    out[lead:lead + m] = a[:m]
    return out


def normalise(pcm, target_lufs, what):
    meas = measure_pcm_lufs(pcm)
    gain = target_lufs - meas
    return pcm * np.float32(10 ** (gain / 20)), meas, gain


def probe_audio_duration(path):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=duration', '-of', 'csv=p=0', str(path)]).decode().strip()
    return float(out)


def bed_in(edit, ps, section):
    """Source time of the bed at the start of the section. 'in_align' puts source_s on a narration cue; with
    the bed of a section that starts later than the picture (bed.start_s) is aligned from that moment."""
    b = section['bed']
    al = b.get('in_align')
    if al:
        return al['source_s'] - phrase_time(edit, ps, section, al['phrase'])
    return b['in']


def duck_envelope_db(total, intervals, duck_db, ramp_s):
    """Gain in dB per sample: duck_db inside each (start_s, end_s) speech span, dB-linear ramps of ramp_s
    that finish at the speech start and begin at the speech end. Overlaps take the deeper duck."""
    t = np.arange(total, dtype=np.float64) / SR
    g_db = np.zeros(total, dtype=np.float64)
    for s0, e0 in intervals:
        d = duck_db * np.clip((t - (s0 - ramp_s)) / ramp_s, 0, 1) * np.clip(((e0 + ramp_s) - t) / ramp_s, 0, 1)
        g_db = np.minimum(g_db, d)
    return g_db


def duck_measure(narr, bed, win_s=0.4, speak_floor_dbfs=-40.0, spans=None):
    """Narration level minus bed level in non-overlapping 400 ms windows. narr and bed are float stereo (n, 2)
    stems after ducking. Two views: 'speaking' = windows whose narration RMS is above speak_floor_dbfs;
    'in_spans' (when spans=[(start_s, end_s)] is given) = every window whose centre lies inside a narration
    speech span, pauses between words and sentences included."""
    n = round(win_s * SR)
    k = min(len(narr), len(bed)) // n
    a = narr[:k * n].reshape(k, n, 2).astype(np.float64)
    b = bed[:k * n].reshape(k, n, 2).astype(np.float64)
    ra = 10 * np.log10(np.mean(a ** 2, axis=(1, 2)) + 1e-20)
    rb = 10 * np.log10(np.mean(b ** 2, axis=(1, 2)) + 1e-20)

    def summary(mask):
        ratio = (ra - rb)[mask]
        if len(ratio) == 0:
            raise ValueError('No windows found')
        return {'windows': int(mask.sum()), 'median_db': round(float(np.median(ratio)), 2), 'p10_db': round(float(np.percentile(ratio, 10)), 2),
                'share_under_6db': round(float(np.mean(ratio < 6.0)), 4)}
    speaking = ra > speak_floor_dbfs
    out = {'window_ms': round(win_s * 1000), 'speak_floor_dbfs': speak_floor_dbfs, 'speaking': summary(speaking)}
    out['speaking_windows'] = out['speaking']['windows']
    out['median_db'] = out['speaking']['median_db']
    out['share_under_6db'] = out['speaking']['share_under_6db']
    if spans:
        centres = (np.arange(k) + 0.5) * win_s
        inside = np.zeros(k, dtype=bool)
        for s0, e0 in spans:
            inside |= (centres >= s0) & (centres <= e0)
        out['in_spans'] = summary(inside)
    return out


def build_audio(edit, plan, work):
    A = edit['audio']
    total = plan['audio_samples']
    secs = plan['sections']
    xf = round(A['crossfade_s'] * SR)  # equal to the picture crossfade: the bed blends over exactly the frames the picture does
    if xf != plan['crossfade_frames'] * SPF:
        raise ValueError('audio.crossfade_s must equal timing.crossfade_s')
    bed = np.zeros((total, 2), dtype=np.float32)
    report = {'bed': [], 'narration': [], 'voice': []}
    bed_windows = {}
    for k, s in enumerate(edit['sections']):
        ps = secs[k]
        b = s['bed']
        src = edit['footage'][b['source']]
        p0 = ps['start_frame'] * SPF
        p1 = ps['end_frame'] * SPF
        bs = round(b.get('start_s', 0.0) * SR)  # a bed that starts after the section does (s1: bed only under the lens recording)
        p0b = p0 + bs
        late = bs > 0
        a0 = p0b if late else p0
        a1 = total if k == len(secs) - 1 else p1 + xf
        b_in = bed_in(edit, ps, s)
        src_start = b_in - (p0b - a0) / SR
        need = a1 - a0
        src_path = rp(src['file'])
        valid = int(np.clip(round((probe_audio_duration(src_path) - src_start) * SR), 0, need))
        cont = b.get('continue_with')
        if cont and valid < need and valid > xf:
            # the source audio ends inside this section: continue with a second recording, crossfaded, each at -23 LUFS
            p1_, meas, gain = normalise(decode_pcm(src_path, src_start, valid / SR), A['bed_lufs'], f"bed {s['id']}")
            cstart = cont['in'] - xf / SR
            p2, meas2, gain2 = normalise(decode_pcm(rp(edit['footage'][cont['source']]['file']), cstart, (need - valid + xf) / SR), A['bed_lufs'], f"bed {s['id']} continuation")
            u = np.linspace(0, 1, xf, dtype=np.float32)
            seg = np.zeros((need, 2), dtype=np.float32)
            seg[:valid] = p1_
            seg[valid - xf:valid] *= np.cos(u * np.pi / 2)[:, None]
            p2[:xf] *= np.sin(u * np.pi / 2)[:, None]
            seg[valid - xf:] += p2
            report_cont = {'continue_with': cont['source'], 'continue_in': cont['in'], 'switch_at_s': round(valid / SR, 2), 'continuation_lufs': round(meas2, 2)}
        else:
            seg = decode_pcm(src_path, src_start, need / SR)
            seg, meas, gain = normalise(seg, A['bed_lufs'], f"bed {s['id']}")
            report_cont = {}
        n = len(seg)
        env = np.ones(n, dtype=np.float32)
        fin = round(b['fade_in_s'] * SR) if (late and b.get('fade_in_s')) else (xf if (k > 0 or late) else round(A['fade_in_s'] * SR))
        u = np.linspace(0, 1, fin, dtype=np.float32)
        env[:fin] *= np.sin(u * np.pi / 2) if (k > 0 or late) else u
        if k < len(secs) - 1:
            u = np.linspace(0, 1, xf, dtype=np.float32)
            env[n - xf:] *= np.cos(u * np.pi / 2)
        bed[a0:a0 + n] += seg * env[:, None]
        bed_windows[s['id']] = (a0, a0 + n, p1)
        report['bed'].append({'section': s['id'], 'source': b['source'], 'in': round(b_in, 3), 'measured_lufs': round(meas, 2), 'gain_db': round(gain, 2), **report_cont})
    # duck under narration speech with dB-linear ramps
    spans = [(ps['speech_start'], ps['speech_end']) for ps in secs if ps['speech_start'] is not None]
    g_db = duck_envelope_db(total, spans, A['duck_db'], A['duck_ramp_s'])
    bed_unducked = bed.copy()
    bed *= (10 ** (g_db / 20)).astype(np.float32)[:, None]
    # final fade and quiet
    quiet = round(A['final_quiet_s'] * SR)
    fade = round(A['final_fade_s'] * SR)
    q0 = total - quiet
    bed[q0:] = 0
    u = np.linspace(1, 0, fade, dtype=np.float32)
    bed[q0 - fade:q0] *= u[:, None]
    # narration at -20 LUFS; a section with its own recorded voice (s1) adds that voice, levelled, never ducked
    mix = bed.copy()
    narr_only = np.zeros_like(mix)
    voice_only = np.zeros_like(mix)
    for k, s in enumerate(edit['sections']):
        ps = secs[k]
        if s['narration'].get('file'):
            nar = decode_pcm(rp(s['narration']['file']), 0, ps['narr_duration'])
            nar, meas, gain = normalise(nar, A['narration_lufs'], f"narration {s['id']}")
            i0 = round(ps['narr_start'] * SR)
            narr_only[i0:i0 + len(nar)] += nar[:max(0, total - i0)]
            report['narration'].append({'section': s['id'], 'start_s': round(ps['narr_start'], 3), 'measured_lufs': round(meas, 2),
                                        'gain_db': round(gain, 2), 'peak_dbfs': round(float(20 * np.log10(np.abs(nar).max())), 2)})
        v = s.get('voice')
        if v:
            vsrc = edit['footage'][v['source']]
            vox = decode_pcm(rp(vsrc['file']), v['in'], v['out'] - v['in'])
            vox, meas, gain = normalise(vox, v.get('lufs', A['narration_lufs']), f"voice {s['id']}")
            fo = min(len(vox), round(v.get('fade_out_s', 0.03) * SR))
            vox[len(vox) - fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
            fi = min(len(vox), round(v.get('fade_in_s', 0.0) * SR))
            if fi:
                vox[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)[:, None]
            i0 = ps['start_frame'] * SPF + round(v.get('start_s', 0.0) * SR)
            voice_only[i0:i0 + len(vox)] += vox[:max(0, total - i0)]
            report['voice'].append({'section': s['id'], 'source': v['source'], 'in': v['in'], 'out': v['out'], 'start_s': round(i0 / SR, 3),
                                    'measured_lufs': round(meas, 2), 'gain_db': round(gain, 2),
                                    'peak_dbfs_before_limiter': round(float(20 * np.log10(np.abs(vox).max())), 2),
                                    'duck_db_under_voice_min': round(float(g_db[i0:i0 + len(vox)].min()), 3),
                                    'bed_under_voice_max_abs': float(np.abs(bed_unducked[i0:i0 + len(vox) - 2 * xf]).max())})
    mix += narr_only + voice_only
    for sid, (w0, w1, pe) in bed_windows.items():
        report.setdefault('bed_windows', {})[sid] = {'start_s': round(w0 / SR, 3), 'end_s': round(pe / SR, 3),
                                                      'duck_db_min': round(float(g_db[w0:pe].min()), 3)}  # inside the section itself
    report['stems'] = {'bed_unducked_lufs': round(measure_pcm_lufs(bed_unducked), 2), 'bed_ducked_lufs': round(measure_pcm_lufs(bed), 2),
                       'narration_only_lufs': round(measure_pcm_lufs(narr_only), 2),
                       'voice_only_lufs': round(measure_pcm_lufs(voice_only), 2) if report['voice'] else None,
                       'duck_depth_db_min': round(float(g_db.min()), 2)}
    report['duck_measure'] = duck_measure(narr_only, bed, spans=spans)
    attack_ms = 5
    latency = round(attack_ms * SR / 1000)  # alimiter delays its output by the attack time; trim it so audio stays sample-aligned
    raw = work / 'mix.f32'
    raw.write_bytes(np.concatenate([mix, np.zeros((2 * latency, 2), dtype=np.float32)]).astype('<f4').tobytes())
    ceiling = 10 ** (A['peak_ceiling_dbfs'] / 20)
    wav = work / 'audio-final.wav'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', raw, '-af',
         f'alimiter=limit={ceiling:.4f}:attack={attack_ms}:release=60:level=disabled,'
         f'atrim=start_sample={latency}:end_sample={latency + total},asetpts=N/SR/TB', '-c:a', 'pcm_s24le', wav])
    raw.unlink()
    n = int(run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=duration_ts', '-of', 'csv=p=0', wav],
                capture_output=True, text=True).stdout.strip())
    if n != total:
        raise RuntimeError(f'Audio length {n} samples, expected {total} (frames x {SPF})')
    report['mix_lufs'], report['mix_peak_dbfs'] = measure_wav(wav)
    return wav, report


# ----------------------------------------------------------------------------------------------
# assemble
# ----------------------------------------------------------------------------------------------
def xfade_graph(plan, labels=None):
    """filter_complex joining the section renders with a linear crossfade of plan['crossfade_frames'] frames. Section k's
    render holds its own frames plus the fade tail; the fade starts on its start_frame, so the blend covers
    [start_frame, start_frame + crossfade) of the final timeline exactly."""
    secs = plan['sections']
    X = plan['crossfade_frames'] / FPS
    chains = [f'[{i}:v]settb=1/{FPS},setpts=PTS-STARTPTS,fps={FPS}[v{i}]' for i in range(len(secs))]
    prev = 'v0'
    for i in range(1, len(secs)):
        chains.append(f"[{prev}][v{i}]xfade=transition=fade:duration={X:.6f}:offset={secs[i]['start_frame'] / FPS:.6f}[x{i}]")
        prev = f'x{i}'
    chains.append(f"[{prev}]format=yuv420p,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709[vout]")
    return ';'.join(chains)


def assemble(edit, plan, wav):
    work = rp(edit['work_dir'])
    out = rp(edit['output'])
    out.parent.mkdir(parents=True, exist_ok=True)
    V = edit['video']
    pic = work / 'picture.mp4'
    cmd = ['ffmpeg', '-v', 'error', '-y']
    for sec in edit['sections']:
        cmd += ['-i', str(work / f"{sec['id']}.mp4")]
    cmd += ['-filter_complex', xfade_graph(plan), '-map', '[vout]', '-an', '-frames:v', str(plan['total_frames']), '-r', str(FPS),
            '-c:v', 'libx264', '-preset', V['preset'], '-crf', str(V['crf']), '-pix_fmt', 'yuv420p',
            '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-x264-params', 'colorprim=bt709:transfer=bt709:colormatrix=bt709:fullrange=off', '-movflags', '+faststart', str(pic)]
    run(cmd)
    run(['ffmpeg', '-v', 'error', '-y', '-i', pic, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
         '-c:a', 'aac', '-b:a', edit['audio']['aac_bitrate'], '-ar', str(SR), '-ac', '2', '-t', f"{plan['duration_s']:.6f}",
         '-map_metadata', '-1', '-movflags', '+faststart', out])
    return out


# ----------------------------------------------------------------------------------------------
# check (read-only)
# ----------------------------------------------------------------------------------------------
def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(path)]))


def rgb_frame(path, t, vf_extra=''):
    vf = 'scale=in_range=tv:in_color_matrix=bt709:out_range=pc,format=rgb24' if not vf_extra else vf_extra
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{t:.4f}', '-i', str(path), '-frames:v', '1', '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    return raw


def check(edit, plan=None):
    plan = plan or make_plan(edit)
    out = rp(edit['output'])
    res = {'output': str(out), 'checks': {}}
    ok = True

    def verdict(name, cond, detail=None):
        nonlocal ok
        res['checks'][name] = {'pass': bool(cond), 'detail': detail}
        ok = ok and bool(cond)

    if not out.exists():
        verdict('exists', False, 'output file missing')
        res['pass'] = False
        return res
    verdict('exists', True, out.stat().st_size)
    res['size_bytes'] = out.stat().st_size
    res['sha256'] = sha256(out)
    dec = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(out), '-f', 'null', '-'], capture_output=True, text=True)
    verdict('full_decode_clean', dec.returncode == 0 and dec.stderr.strip() == '', dec.stderr.strip()[:300] or 'no decode errors')
    p = probe(out)
    v = next(s for s in p['streams'] if s['codec_type'] == 'video')
    a = next(s for s in p['streams'] if s['codec_type'] == 'audio')
    dur = float(p['format']['duration'])
    vdur, adur = float(v['duration']), float(a['duration'])
    frames = int(v['nb_read_frames'])
    res['duration_s'] = dur
    res['video_duration_s'] = vdur
    res['audio_duration_s'] = adur
    res['frames'] = frames
    verdict('under_180_s', dur < 180, round(dur, 3))
    cap = edit.get('limits', {}).get('cap_s', 180.0)
    verdict('under_cap', dur <= cap, {'duration_s': round(dur, 3), 'cap_s': cap})
    verdict('frame_count_matches_plan', frames == plan['total_frames'], {'frames': frames, 'planned': plan['total_frames']})
    verdict('video_duration_matches_plan', abs(vdur - plan['duration_s']) < 0.002, {'video': vdur, 'planned': plan['duration_s']})
    verdict('audio_duration_matches_picture', abs(adur - vdur) < 0.05, {'audio': adur, 'video': vdur})
    verdict('resolution_fps', (v['width'], v['height'], v['r_frame_rate']) == (1920, 1080, '30/1'), [v['width'], v['height'], v['r_frame_rate']])
    verdict('h264_yuv420p', v['codec_name'] == 'h264' and v['pix_fmt'] == 'yuv420p', [v['codec_name'], v['pix_fmt']])
    tags = [v.get('color_range'), v.get('color_space'), v.get('color_transfer'), v.get('color_primaries')]
    verdict('bt709_tv_tags', tags == ['tv', 'bt709', 'bt709', 'bt709'], tags)
    verdict('audio_aac_48k_stereo', (a['codec_name'], a['sample_rate'], a['channels']) == ('aac', '48000', 2), [a['codec_name'], a['sample_rate'], a['channels']])
    e = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(out), '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    vd = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(out), '-vn', '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    res['integrated_lufs'] = parse_integrated_lufs(e)
    res['loudness_range_lu'] = parse_lra(e)
    res['peak_dbfs'] = parse_max_volume(vd)
    res['mean_volume_db'] = parse_mean_volume(vd)
    verdict('peak_at_or_below_target', res['peak_dbfs'] <= edit['audio']['target_peak_dbfs'] + 0.05, {'peak_dbfs': res['peak_dbfs'], 'target': edit['audio']['target_peak_dbfs']})
    q = edit['audio']['final_quiet_s']
    tail = subprocess.run(['ffmpeg', '-hide_banner', '-ss', f'{dur - min(q, 0.15):.3f}', '-i', str(out), '-vn', '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    res['final_quiet_max_volume_db'] = parse_max_volume(tail)
    verdict('ends_in_silence', res['final_quiet_max_volume_db'] <= -60, res['final_quiet_max_volume_db'])
    # the recitation bed must keep running under the close card until about 1 s before the end
    mid = subprocess.run(['ffmpeg', '-hide_banner', '-ss', f'{dur - 2.0:.3f}', '-t', '0.8', '-i', str(out), '-vn', '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    res['close_bed_mean_volume_db'] = parse_mean_volume(mid)
    verdict('close_bed_running', res['close_bed_mean_volume_db'] >= -45, res['close_bed_mean_volume_db'])
    # audio offset: find each narration inside the export (4 s excerpt, +-0.5 s search) and report the lag in samples
    full = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(out), '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']), dtype='<f4')
    lags = {}
    for s_, ps in zip(edit['sections'], plan['sections']):
        if not s_['narration'].get('file'):
            continue
        nar = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(rp(s_['narration']['file'])), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']), dtype='<f4')
        seg = nar[SR * 2:SR * 6]
        exp = round(ps['narr_start'] * SR) + SR * 2
        win = full[exp - SR // 2:exp + len(seg) + SR // 2]
        Lc = len(win) + len(seg)
        Nf = 1 << (Lc - 1).bit_length()
        c = np.fft.irfft(np.fft.rfft(win, Nf) * np.conj(np.fft.rfft(seg, Nf)), Nf)[:len(win) - len(seg) + 1]
        lags[ps['id']] = int(np.argmax(c)) - SR // 2
    res['audio_offset_samples'] = lags
    verdict('audio_offset_within_1_sample', max(abs(v) for v in lags.values()) <= 1, lags)
    verdict('loudness_plausible', -26 <= res['integrated_lufs'] <= -17, res['integrated_lufs'])
    # colour: paper pixels in the s2 card must decode back to the palette paper in explicit BT.709 RGB
    pal = Palette(edit)
    s2 = next(s for s in plan['sections'] if s['id'] == 's2')
    px = np.frombuffer(rgb_frame(out, s2['start_s'] + s2['duration_s'] / 2), dtype=np.uint8).reshape(1080, 1920, 3)
    got = tuple(int(x) for x in px[10, 10])
    verdict('paper_colour_round_trip', max(abs(g - w) for g, w in zip(got, pal.paper)) <= 3, {'got': got, 'want': pal.paper})
    # colour: footage region vs source in the same RGB space (full-range phone source, s4)
    try:
        s4sec = next(s for s in edit['sections'] if s['id'] == 's4')
        f = next(l for l in s4sec['layers'] if l['type'] == 'footage')
        ps4 = next(s for s in plan['sections'] if s['id'] == 's4')
        t_rel = 5.0
        dx, dy, dw, dh = f['dest']
        cx, cy, cw, ch = f['crop']
        src = edit['footage'][f['source']]
        outpx = np.frombuffer(rgb_frame(out, ps4['start_s'] + t_rel), dtype=np.uint8).reshape(1080, 1920, 3)[dy:dy + dh, dx:dx + dw].reshape(-1, 3).mean(axis=0)
        srcraw = rgb_frame(rp(src['file']), f['in'] + t_rel,
                           f"crop={cw}:{ch}:{cx}:{cy},scale=w={dw}:h={dh}:flags=lanczos:in_range={src['range']}:in_color_matrix={src['matrix']},format=rgb24")
        srcpx = np.frombuffer(srcraw, dtype=np.uint8).reshape(dh, dw, 3).reshape(-1, 3).mean(axis=0)
        verdict('footage_rgb_matches_source', float(np.abs(outpx - srcpx).max()) <= 3.0,
                {'output_mean_rgb': [round(float(x), 2) for x in outpx], 'source_mean_rgb': [round(float(x), 2) for x in srcpx]})
    except StopIteration:
        pass
    res['pass'] = ok
    return res


# ----------------------------------------------------------------------------------------------
# QA frames
# ----------------------------------------------------------------------------------------------
def extract_frames(edit, plan, folder):
    out = rp(edit['output'])
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for ps, s in zip(plan['sections'], edit['sections']):
        times = {'a': 0.4, 'b': ps['duration_s'] / 2, 'c': ps['duration_s'] - 0.35}
        if ps['fade_in_frames']:
            fx = ps['fade_in_frames'] / FPS
            times.update({'x0': 0.0, 'x1': fx * 0.25, 'x2': fx * 0.5, 'x3': fx * 0.75, 'x4': fx})
        for L in s['layers']:
            if L['type'] == 'ribbon':
                f = next(x for x in s['layers'] if x['type'] == 'footage')
                for i, w in enumerate(L['windows']):
                    times[f'win{i}'] = min(ps['duration_s'] - 0.1, f.get('start_s', 0) + (w['from_source_s'] - f['in']) + 0.6)
            if 'appear_phrase' in L:
                times['ph_' + L['appear_phrase'].replace(' ', '_')] = min(ps['duration_s'] - 0.1, phrase_time(edit, ps, s, L['appear_phrase']) + 0.8)
        for tag, t in times.items():
            p = folder / f"{s['id']}-{tag}.png"
            run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{ps['start_s'] + t:.4f}", '-i', out, '-frames:v', '1', p])
            paths.append(p)
    return paths


def check_cap(plan, cap=180.0):
    """Hard cap: refuse a plan longer than cap (edit.json limits.cap_s, 178.0) and, always, one of 180 s or more
    unless the caller renders an explicitly named over-cap proof."""
    if plan['duration_s'] > cap + 1e-9:
        raise ValueError(f"planned duration {plan['duration_s']:.3f} s is over the {cap:.1f} s cap")


def print_plan(plan):
    print(f"total {plan['duration_s']:.3f} s, {plan['total_frames']} frames, {plan['audio_samples']} audio samples")
    for p in plan['sections']:
        nar = (f"narration {p['narr_start']:7.3f}-{p['narr_end']:7.3f}  cut {p['cut_offset_s']:+.2f} s vs narration end"
               if p['has_narration'] else 'no narration (own voice / recitation only)')
        print(f"{p['id']}: picture {p['start_s']:7.3f}-{p['end_s']:7.3f} ({p['frames']:4d} f)  {nar}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--edit', default=str(DEFAULT_EDIT))
    ap.add_argument('--check', action='store_true', help='verify the existing output without rendering')
    ap.add_argument('--plan', action='store_true', help='print the planned timeline and exit')
    ap.add_argument('--only', help='comma list of section ids: render just those picture segments and stop')
    ap.add_argument('--audio-only', action='store_true')
    ap.add_argument('--fallback', choices=['on', 'off'], help='override fallback.enabled in edit.json for this run')
    ap.add_argument('--voice', choices=['callum', 'own'], help='override narration.source in edit.json for this run')
    ap.add_argument('--allow-over-cap', action='store_true', help='render a plan that is over limits.cap_s as a proof; the file name gets -OVER-CAP and no v1.2 file is written')
    ap.add_argument('--output', help='override the output path (use with --fallback on to keep the default export intact)')
    ap.add_argument('--work-dir', help='override the work directory')
    ap.add_argument('--frames', metavar='DIR', help='extract QA frames from the existing output into DIR')
    args = ap.parse_args(argv)
    edit = load_edit(args.edit, None if args.fallback is None else args.fallback == 'on', args.voice)
    if args.output:
        edit['output'] = args.output
    if args.work_dir:
        edit['work_dir'] = args.work_dir
    try:
        plan = make_plan(edit)
    except FileNotFoundError as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 2
    if args.plan:
        print_plan(plan)
        return 0
    if args.check:
        res = check(edit, plan)
        print(json.dumps(res, indent=2, default=str))
        return 0 if res['pass'] else 1
    if args.frames:
        for p in extract_frames(edit, plan, args.frames):
            print(p)
        return 0
    work = rp(edit['work_dir'])
    work.mkdir(parents=True, exist_ok=True)
    print_plan(plan)
    try:
        check_cap(plan, edit.get('limits', {}).get('cap_s', 180.0))
    except ValueError as e:
        if not args.allow_over_cap:
            print(f'ERROR: {e}', file=sys.stderr)
            return 3
        o = Path(edit['output'])
        edit['output'] = str(o.with_name(o.stem + '-OVER-CAP' + o.suffix))
        print(f'WARNING: {e}. Rendering a proof to {edit["output"]}', file=sys.stderr)
    if args.only:
        render_sections(edit, plan, only=set(args.only.split(',')))
        return 0
    if args.audio_only:
        wav, rep = build_audio(edit, plan, work)
        print(json.dumps(rep, indent=2))
        return 0
    render_sections(edit, plan)
    wav, arep = build_audio(edit, plan, work)
    out = assemble(edit, plan, wav)
    res = check(edit, plan)
    res['audio_build'] = arep
    rec = rp('build/video-v1.0/receipts')
    rec.mkdir(parents=True, exist_ok=True)
    tag = ('-fallback' if edit.get('fallback_active') else '') + ('-OVER-CAP' if '-OVER-CAP' in edit['output'] else '')
    (rec / f"render-v{edit['version']}{tag}.json").write_text(json.dumps({'plan': plan, 'check': res}, indent=2, default=str) + '\n')
    print(json.dumps(res, indent=2, default=str))
    return 0 if res['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
