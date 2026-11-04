#!/usr/bin/env python3
"""Tests for tools/v1/render_v1.py. None of them renders the film.

Run with the venv that has numpy, Pillow, uharfbuzz and skia-python:
  /Users/farazsyed/data/khirad/apps/ayah-lens-prep/venv-data/bin/python tools/v1/test_render_v1.py
"""
import json
import subprocess
import sys
import tempfile
import unittest
import wave
from unittest import mock
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_v1 as R  # noqa: E402

RAW = R.load_edit_raw()
BASE = R.apply_fallback(RAW, False)                        # edit.json as written: s5 skeleton present, nothing applied
STAND_IN_TOGGLE = {'file': 'recordings/version-3/take-02-muzzammil-phone-original.mov', 'in': 66.5, 'out': 72.5, 'label': 'Phone screen recording'}
EDIT = R.apply_toggle(BASE)                                # default mode, no toggle clip: s5 dropped
TOG = R.apply_toggle(BASE, STAND_IN_TOGGLE)                # default mode with a (stand-in) toggle clip: s5 plays it
FB = R.apply_toggle(R.apply_fallback(RAW, True))
EST = R.load_edit(voice='callum')          # default mode with the establishing shot configured in edit.json
PLAN = R.make_plan(EDIT)
EST_PLAN = R.make_plan(EST)
PAL = R.Palette(EDIT)
W, H = EDIT['canvas']['w'], EDIT['canvas']['h']
FB_READY = all(R.rp(s['narration']['file']).exists() for s in FB['sections'] if s['narration'].get('file'))


def probe_duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)]).decode().strip())


def layers(section_id, ty=None, edit=EDIT):
    s = next(s for s in edit['sections'] if s['id'] == section_id)
    return [l for l in s['layers'] if ty is None or l['type'] == ty]


def content_plates(section_id, edit=EDIT):
    return [l for l in layers(section_id, 'plate', edit) if l.get('role') not in ('label', 'illustration')]


def all_texts(edit):
    for s in edit['sections']:
        for l in s['layers']:
            for ln in l.get('lines', []):
                yield s['id'], ln['text']


class EditJson(unittest.TestCase):
    def test_edit_json_is_valid_and_complete(self):
        self.assertEqual([s['id'] for s in BASE['sections']], [f's{i}' for i in range(1, 8)])
        self.assertEqual([s['id'] for s in EDIT['sections']], ['s1', 's2', 's3', 's4', 's6', 's7'], 'no toggle clip: s5 is dropped')
        self.assertEqual([s['id'] for s in TOG['sections']], [f's{i}' for i in range(1, 8)])
        self.assertIsNone(RAW['toggle']['file'])
        self.assertFalse(RAW['fallback']['enabled'], 'fallback mode must be off by default')
        self.assertEqual(EDIT['canvas'], {'w': 1920, 'h': 1080, 'fps': 30})
        self.assertEqual((EDIT['palette']['paper'], EDIT['palette']['ink'], EDIT['palette']['blue'], EDIT['palette']['red']),
                         ('#ECE7D3', '#1E1E1E', '#465D79', '#B94B37'))
        self.assertAlmostEqual(EDIT['palette']['dim_mix'], 0.55)
        for k, f in EDIT['fonts'].items():
            self.assertTrue(Path(f).exists(), f'font {k} missing: {f}')
        self.assertTrue(Path(EDIT['quran']['qpc_json']).exists())
        for key, src in EDIT['footage'].items():
            self.assertTrue(R.rp(src['file']).exists(), key)
            self.assertIn(src['range'], ('tv', 'pc'))
            self.assertEqual(src['matrix'], 'bt709')
        allowed = {'paper', 'card', 'plate', 'pin', 'ribbon', 'footage'}
        for edit in (EDIT, FB, EST):
            for s in edit['sections']:
                self.assertIn(s['bed']['source'], edit['footage'])
                self.assertIn(s['layers'][0]['type'], ('paper', 'card'), 'first layer must be opaque')
                for l in s['layers']:
                    self.assertIn(l['type'], allowed)
                    if l['type'] == 'footage':
                        self.assertIn(l['source'], edit['footage'])
                        cw, ch = l['crop'][2:]
                        dw, dh = l['dest'][2:]
                        self.assertLess(abs(cw / ch - dw / dh) / (cw / ch), 0.01, f"{s['id']} crop/dest aspect mismatch")
                    if l['type'] == 'ribbon':
                        self.assertIn(l['follow'], [x.get('id') for x in s['layers'] if x['type'] == 'footage'])
        for s in EDIT['sections']:
            if s['narration'].get('file'):
                self.assertTrue(R.rp(s['narration']['file']).exists(), s['id'])
        self.assertEqual(EDIT['audio']['duck_db'], -16.0)
        self.assertEqual(EDIT['audio']['duck_ramp_s'], 0.3)
        self.assertEqual((EDIT['audio']['bed_lufs'], EDIT['audio']['narration_lufs']), (-23.0, -20.0))

    def test_script_lines_are_exact(self):
        exact = EDIT['script_lines_exact']
        for edit in (EDIT, FB):
            s6 = [l['lines'][0]['text'] for l in content_plates('s6', edit)]
            self.assertEqual(sorted(s6), sorted([exact['s6_line1'], exact['s6_line2']]))
            s7 = layers('s7', 'card', edit)[0]
            self.assertEqual(' · '.join(l['text'] for l in s7['lines']), exact['s7_card'])
        s2 = [l['lines'][0]['text'] for l in content_plates('s2')]
        self.assertEqual(' · '.join(s2), exact['s2_card'])
        s5 = next(l for l in layers('s5', 'plate', TOG) if l.get('role') != 'label')['lines'][0]
        self.assertEqual((s5['text'], s5['size']), ('Arabic only, for memorization.', 56))
        s3 = [l['lines'][0]['text'] for l in layers('s3', 'plate')]
        self.assertIn('audio goes to Muse Voice', s3)
        self.assertIn('English prepared in advance', s3)
        self.assertEqual(layers('s3', 'card')[0]['lines'][0]['text'], 'Ayah Lens')
        self.assertEqual(layers('s3', 'card')[0]['end_s'], 1.0)

    def test_every_latin_word_is_large_enough(self):
        """Cap height 40 px needs a 56 px Arial font. Footage labels are 48 px by decision."""
        self.assertGreaterEqual(EDIT['min_latin_px'], 56)
        self.assertEqual(EDIT['label_px'], 48)
        for edit in (EDIT, FB, EST):
            for s in edit['sections']:
                for l in s['layers']:
                    for ln in l.get('lines', []):
                        floor = edit['label_px'] if l.get('role') in ('label', 'illustration') else edit['min_latin_px']
                        self.assertGreaterEqual(ln['size'], floor, f"{s['id']}: {ln['text']!r}")
                    if l['type'] == 'pin':
                        self.assertGreaterEqual(l['size'], 56)
                    if l['type'] == 'ribbon':
                        self.assertGreaterEqual(l['counter_size'], 56)
                        _, size, _, _ = R.layout_ribbon(edit, l)
                        self.assertGreaterEqual(size, edit['min_text_px'])


class Labels(unittest.TestCase):
    def test_every_footage_window_carries_its_label_in_one_corner(self):
        corners = set()
        for edit in (EDIT, FB, EST, TOG):
            for s in edit['sections']:
                foots = [l for l in s['layers'] if l['type'] == 'footage']
                labels = [l for l in s['layers'] if l['type'] == 'plate' and l.get('role') == 'label']
                self.assertEqual(len(labels), len(foots), s['id'])
                for foot, lab in zip(foots, labels):
                    want = foot.get('label') or edit['footage'][foot['source']]['label']
                    self.assertEqual(lab['lines'][0]['text'], want, s['id'])
                    self.assertEqual(lab['lines'][0]['size'], 48)
                    self.assertEqual(lab.get('end_s'), foot.get('end_s'), 'label must last exactly as long as its footage')
                    self.assertEqual(lab.get('start_s', 0), foot.get('start_s', 0))
                    corners.add((tuple(lab['pos']), lab['anchor']))
        self.assertEqual(corners, {((1884, 28), 'tr')})
        self.assertEqual({v['label'] for v in EDIT['footage'].values()}, {'Glasses display recording', 'Phone screen recording', 'Filmed on a phone'})
        by = {s['id']: next(l for l in s['layers'] if l.get('role') == 'label')['lines'][0]['text'] for s in EDIT['sections'] if any(l['type'] == 'footage' for l in s['layers'])}
        self.assertEqual(by['s1'], 'Filmed on a phone')
        self.assertEqual([l['lines'][0]['text'] for l in layers('s1', 'plate')], ['Filmed on a phone', 'What I see through the glasses'])
        self.assertEqual((by['s4'], by['s6'], by['s7']), ('Glasses display recording',) * 3)
        self.assertEqual((by['s2'], by['s3']), ('Phone screen recording',) * 2)
        self.assertEqual(next(l for l in layers('s5', 'plate', TOG) if l.get('role') == 'label')['lines'][0]['text'], 'Phone screen recording')

    def test_s4_carries_the_illustration_tag_for_the_whole_section(self):
        tag = next(l for l in layers('s4', 'plate') if l.get('role') == 'illustration')
        self.assertEqual(tag['lines'][0]['text'], 'Illustration, not in the app')
        self.assertEqual(tag['lines'][0]['size'], 48)
        for k in ('start_s', 'end_s', 'appear_phrase'):
            self.assertNotIn(k, tag)
        rib = layers('s4', 'ribbon')[0]
        bb = R.paint_plate(EDIT, PAL, tag).getchannel('A').getbbox()
        self.assertLessEqual(abs(bb[3] - rib['box'][1]), 20, 'tag must sit just above the ribbon')
        self.assertLessEqual(bb[3], rib['box'][1])

    def test_counter_text_uses_plain_words(self):
        rib = layers('s4', 'ribbon')[0]
        self.assertEqual(rib['counter_template'].format(a=8, b=9, n=20), 'Portion 8 of 20 on the lens')
        self.assertIsNotNone(R.paint_counter(EDIT, PAL, rib, 8, 9).getbbox())


class Arabic(unittest.TestCase):
    FP = EDIT['fonts']['arabic']

    def test_shaping_is_nonempty_right_to_left_and_joined(self):
        words = R.verse_words(EDIT['quran']['qpc_json'], '73:20')
        sh = R.shape_arabic(self.FP, ' '.join(words[:6]))
        self.assertEqual(sh['direction'], 'rtl')
        self.assertGreater(len(sh['glyphs']), 20)
        clusters = [g[1] for g in sh['glyphs']]
        self.assertEqual(clusters, sorted(clusters, reverse=True), 'RTL output must be in visual order (clusters descending)')
        iso = {g[0] for g in R.shape_arabic(self.FP, 'ب')['glyphs']}
        medial = {g[0] for g in R.shape_arabic(self.FP, 'ببب')['glyphs']}
        self.assertTrue(medial - iso, 'letters were not joined into medial forms')
        mask, adv, asc, padx = R.arabic_mask(self.FP, words[0], 56)
        self.assertIsNotNone(mask.getbbox(), 'rendered word has no ink')
        self.assertGreater(adv, 30)

    def test_verse_73_20_has_78_words_and_no_ayah_number(self):
        words = R.verse_words(EDIT['quran']['qpc_json'], '73:20')
        self.assertEqual(len(words), 78)
        joined = ''.join(words)
        for ch in '٠١٢٣٤٥٦٧٨٩۝ ':
            self.assertNotIn(ch, joined)
        self.assertTrue(words[0].startswith('۞'))
        self.assertTrue(words[-1].endswith('ۢ'))


class Verse282(unittest.TestCase):
    def test_2_282_has_128_words_and_no_ayah_number(self):
        words = R.verse_words(EDIT['quran']['qpc_json'], '2:282')
        self.assertEqual(len(words), 128)
        joined = ''.join(words)
        for ch in '\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669\u06dd\u00a0':
            self.assertNotIn(ch, joined)
        self.assertTrue(words[0].startswith('\u064a'))
        self.assertNotIn('\u06de', words[0])
        self.assertTrue(words[-1].startswith('\u0639'))

    def test_s4_is_pinned_to_2_282_and_ribbon_shapes_the_whole_verse(self):
        pin = layers('s4', 'pin')[0]
        self.assertEqual((pin['text'], pin['size']), ('2:282', 56))
        rib = layers('s4', 'ribbon')[0]
        self.assertEqual((rib['verse'], rib['counter_total']), ('2:282', 36))
        placed, size, pitch, above = R.layout_ribbon(EDIT, rib)
        self.assertEqual(sorted(i for row in placed for i, _, _ in row), list(range(128)))
        self.assertGreaterEqual(size, 40)
        self.assertLessEqual(rib['box'][1] + len(placed) * pitch, H - EDIT['bottom_margin_px'])
        base, states, _ = R.paint_ribbon_layers(EDIT, PAL, rib)
        self.assertEqual(len(states), len(rib['windows']))
        for img, counter, lit in states:
            self.assertIsNotNone(img.getbbox(), counter)
        self.assertEqual(rib['counter_template'].format(a=4, b=5, n=rib['counter_total']), 'Portion 4 of 36 on the lens')


class Ribbon(unittest.TestCase):
    def test_window_mapping(self):
        self.assertEqual(R.window_words(8, 9, 78), (29, 36))
        self.assertEqual(R.window_words(9, 10, 78), (33, 40))
        self.assertEqual(R.window_words(13, 14, 78), (49, 56))
        self.assertEqual(R.window_words(1, 1, 78), (1, 4))
        self.assertEqual(R.window_words(19, 20, 78), (73, 78))  # clamped at the verse end

    def test_ribbon_steps_follow_the_footage_counters(self):
        rib = layers('s4', 'ribbon')[0]
        foot = layers('s4', 'footage')[0]
        n_words = len(R.verse_words(EDIT['quran']['qpc_json'], rib['verse']))
        wins = rib['windows']
        times = [w['from_source_s'] for w in wins]
        self.assertEqual(times, sorted(times))
        self.assertEqual(len(set(times)), len(times))
        self.assertAlmostEqual(times[0], foot['in'], places=3)
        self.assertLessEqual(times[-1], foot['out'])
        counters = [w['counter'] for w in wins]
        for a, b in zip(counters, counters[1:]):
            self.assertEqual(b[0] - a[0], 1, 'counter must advance by one portion per step')
        for c in counters:
            self.assertEqual(c[1] - c[0], 1)
            self.assertLessEqual(c[1], rib['counter_total'])
        self.assertEqual((rib['mapping_mode'], rib['spans_are']), ('observed', 'observed, not computed'))
        for w in wins:
            self.assertIn('words_observed', w)
            self.assertFalse(w.get('computed', False), 'every state was readable, none may be marked computed')
        starts = [w['words_observed'][0] for w in wins]
        ends = [w['words_observed'][1] for w in wins]
        self.assertEqual(starts, sorted(starts))
        self.assertEqual(ends, sorted(ends))
        for lo, hi in zip(starts, ends):
            self.assertTrue(1 <= lo < hi <= n_words)
            self.assertLessEqual(hi - lo + 1, 12)
        base, states, size = R.paint_ribbon_layers(EDIT, PAL, rib)
        self.assertEqual(len(states), len(wins))
        self.assertIsNotNone(base.getbbox())
        for img, counter, lit in states:
            self.assertIsNotNone(img.getbbox(), f'state {counter} drew nothing')
        bx, by, bw, bh = rib['box']
        self.assertGreaterEqual(by, foot['dest'][1] + foot['dest'][3])
        self.assertLessEqual(by + bh, H - EDIT['bottom_margin_px'])
        placed, size, pitch, above = R.layout_ribbon(EDIT, rib)
        self.assertLessEqual(len(placed) * pitch, bh)
        self.assertEqual(sorted(i for row in placed for i, _, _ in row), list(range(n_words)))

    def test_state_times_land_inside_the_section(self):
        ps = next(p for p in PLAN['sections'] if p['id'] == 's4')
        foot = layers('s4', 'footage')[0]
        rib = layers('s4', 'ribbon')[0]
        for w in rib['windows']:
            t = foot['start_s'] + (w['from_source_s'] - foot['in'])
            self.assertTrue(0 <= t < ps['duration_s'])

    def test_dim_strip_contrast(self):
        paper, dim = PAL.paper, PAL.dim

        def lum(c):
            f = lambda v: (v / 255 / 12.92) if v / 255 <= 0.03928 else (((v / 255) + 0.055) / 1.055) ** 2.4
            return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])
        ratio = (lum(paper) + 0.05) / (lum(dim) + 0.05)
        self.assertGreater(ratio, 2.4, 'dim strip must keep at least 2.4:1 against paper')


class Bounds(unittest.TestCase):
    def test_cut_offsets_inside_clip_bounds(self):
        """Footage windows (after any narration alignment) and bed sources stay inside their files."""
        for edit, plan in ((EDIT, PLAN), (EST, EST_PLAN), (TOG, R.make_plan(TOG))):
            pal = R.Palette(edit)
            for s in edit['sections']:
                ps = next(p for p in plan['sections'] if p['id'] == s['id'])
                with tempfile.TemporaryDirectory() as d:
                    stages, _ = R.resolve_section(edit, plan, s, pal, Path(d))
                for st in (x for x in stages if x['kind'] == 'footage'):
                    dur = probe_duration(st['file'])
                    self.assertGreaterEqual(st['in'], 0, s['id'])
                    self.assertLessEqual(st['in'] + st['len'], dur + 1e-6, f"{s['id']} footage runs past the file end")
                    layer = next(l for l in s['layers'] if l['type'] == 'footage' and R.rp(edit['footage'][l['source']]['file']) == st['file'])
                    if not layer.get('freeze_after'):
                        end = st['end'] if st['end'] is not None else ps['duration_s']
                        self.assertLessEqual(end - st['start'], st['len'] + 1 / R.FPS, f"{s['id']} footage too short and not frozen")
                b = s['bed']
                start = R.bed_in(edit, ps, s)
                adur = R.probe_audio_duration(R.rp(edit['footage'][b['source']]['file']))
                need = ps['duration_s'] - b.get('start_s', 0.0) + 0.5
                self.assertGreater(adur - start, 0, s['id'])
                if start + need > adur + 0.5:
                    self.assertIn('continue_with', b, f"{s['id']} bed runs past its source and has no continuation")
                    cont = b['continue_with']
                    cdur = R.probe_audio_duration(R.rp(edit['footage'][cont['source']]['file']))
                    self.assertLessEqual(cont['in'] + (start + need - adur), cdur + 0.5, f"{s['id']} continuation runs past its source")

    def test_picture_cuts_land_0_4_s_before_narration_ends(self):
        for s, ps in zip(EDIT['sections'], PLAN['sections']):
            if not s['narration'].get('file'):
                continue
            cut = s['narration'].get('cut_offset_s', EDIT['timing']['default_cut_offset_s'])
            self.assertAlmostEqual(ps['narr_end'] - ps['end_s'], cut, delta=0.5 / R.FPS + 1e-6)
        defaults = [ps for s, ps in zip(EDIT['sections'], PLAN['sections']) if s['narration'].get('file') and s['narration'].get('cut_offset_s', 0.4) == 0.4]
        self.assertEqual([p['id'] for p in defaults], ['s2', 's3', 's4', 's6'])
        for a, b in zip(PLAN['sections'], PLAN['sections'][1:]):
            self.assertGreaterEqual(b['narr_start'], a['narr_end'])
            self.assertGreaterEqual(b['narr_start'], a['end_s'] - 0.4 - 1e-6)

    def test_total_planned_duration_under_180_s(self):
        self.assertLess(PLAN['duration_s'], 180)
        self.assertGreater(PLAN['duration_s'], 100)
        self.assertEqual(PLAN['audio_samples'], PLAN['total_frames'] * 1600)
        pos = 0
        for p in PLAN['sections']:
            self.assertEqual(p['start_frame'], pos)
            self.assertGreater(p['frames'], 0)
            pos = p['end_frame']
        self.assertEqual(pos, PLAN['total_frames'])


def times_disjoint(a, b):
    """True when layer a ends (end_s) no later than b starts (start_s), or the reverse: they are never on screen together."""
    for x, y in ((a, b), (b, a)):
        if x.get('end_s') is not None and x['end_s'] <= y.get('start_s', 0.0):
            return True
    return False


def check_overlaps(testcase, edit):
    """Plates stay inside the frame with the bottom margin, out of the footage window and out of the lens-text zone."""
    limit = H - edit['bottom_margin_px']
    for s in edit['sections']:
        foots = [l for l in s['layers'] if l['type'] == 'footage']
        for l in s['layers']:
            if l['type'] not in ('plate', 'pin'):
                continue
            img = R.paint_plate(edit, PAL, l) if l['type'] == 'plate' else R.paint_pin(edit, PAL, l)
            bb = img.getchannel('A').getbbox()
            testcase.assertIsNotNone(bb)
            name = f"{s['id']} {l.get('lines', [{'text': l.get('text')}])[0]['text']!r}"
            testcase.assertGreaterEqual(bb[0], 0, name)
            testcase.assertLessEqual(bb[2], W, name)
            testcase.assertLessEqual(bb[3], limit, f'{name} bottom {bb[3]} is inside the {edit["bottom_margin_px"]} px margin')
            for foot in foots:
                # a plate and a footage window that never share a frame (the cue hands over from one to the other) cannot overlap
                if times_disjoint(l, foot):
                    continue
                fx0, fy0, fw, fh = foot['dest']
                if (fw, fh) == (W, H):
                    zone_src = edit['footage'][foot['source']].get('text_zone')
                    if zone_src is None or l.get('role') == 'label':
                        continue
                    cx, cy, cw, ch = foot['crop']
                    sx, sy = fw / cw, fh / ch
                    zx0, zy0 = (zone_src[0] - cx) * sx, (zone_src[1] - cy) * sy
                    zx1, zy1 = zx0 + zone_src[2] * sx, zy0 + zone_src[3] * sy
                    testcase.assertTrue(bb[2] <= zx0 or bb[0] >= zx1 or bb[3] <= zy0 or bb[1] >= zy1, f'{name} bbox {bb} overlaps lens text zone')
                else:
                    if l['type'] == 'plate' and l.get('role') != 'label' and 'start_s' not in l and l['lines'][0]['text'] == 'Ayah Lens':
                        continue
                    testcase.assertTrue(bb[2] <= fx0 or bb[0] >= fx0 + fw or bb[3] <= fy0 or bb[1] >= fy0 + fh, f'{name} {bb} overlaps footage window')
        # overlays never collide with each other
        boxes = []
        for l in s['layers']:
            if l['type'] in ('plate', 'pin') and not (l['type'] == 'plate' and l['lines'][0]['text'] == 'Ayah Lens'):
                img = R.paint_plate(edit, PAL, l) if l['type'] == 'plate' else R.paint_pin(edit, PAL, l)
                boxes.append((l, img.getchannel('A').getbbox()))
        for i, (la, a) in enumerate(boxes):
            for lb, b in boxes[i + 1:]:
                if times_disjoint(la, lb):
                    continue  # never on screen together
                inter = not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])
                testcase.assertFalse(inter, f"{s['id']}: overlays {a} and {b} collide")


class Overlap(unittest.TestCase):
    def test_overlays_avoid_the_footages_own_text_and_the_bottom_margin(self):
        check_overlaps(self, EDIT)

    def test_fallback_overlays_avoid_the_footages_own_text_and_the_bottom_margin(self):
        check_overlaps(self, FB)

    def test_shipping_default_with_the_establishing_shot_avoids_overlaps_and_margins(self):
        check_overlaps(self, EST)
        check_overlaps(self, TOG)

    def test_ribbon_and_s6_plates_are_54_px_above_the_frame_edge(self):
        rib = layers('s4', 'ribbon')[0]
        self.assertLessEqual(rib['box'][1] + rib['box'][3], H - 54)
        _, size, pitch, _ = R.layout_ribbon(EDIT, rib)
        self.assertLessEqual(rib['box'][1] + len(R.layout_ribbon(EDIT, rib)[0]) * pitch, H - 54)
        for edit in (EDIT, FB, EST):
            for l in content_plates('s6', edit):
                bb = R.paint_plate(edit, PAL, l).getchannel('A').getbbox()
                self.assertLessEqual(bb[3], H - 54)


class Audio(unittest.TestCase):
    @staticmethod
    def sine_wav(path, amp, seconds=1.5, hz=1000.0):
        n = int(48000 * seconds)
        t = np.arange(n) / 48000.0
        x = (amp * np.sin(2 * np.pi * hz * t) * 32767).astype('<i2')
        with wave.open(str(path), 'wb') as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(48000)
            w.writeframes(np.repeat(x[:, None], 2, axis=1).tobytes())

    def test_loudness_and_peak_parser_on_tiny_wav(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / 'a.wav', Path(d) / 'b.wav'
            self.sine_wav(a, 0.1)
            self.sine_wav(b, 0.2)
            la, pa = R.measure_wav(a)
            lb, pb = R.measure_wav(b)
            self.assertAlmostEqual(lb - la, 6.02, delta=0.15)
            self.assertAlmostEqual(pa, -20.0, delta=0.2)
            self.assertAlmostEqual(pb, -13.98, delta=0.2)
            self.assertTrue(-30 < la < -15)

    def test_parsers_reject_missing_reports_and_read_group_1(self):
        with self.assertRaises(ValueError):
            R.parse_max_volume('no report here')
        with self.assertRaises(ValueError):
            R.parse_integrated_lufs('Summary:\n  nothing')
        log = '[Parsed_volumedetect_0 @ 0x1] max_volume: -3.1 dB\n'
        self.assertEqual(R.parse_max_volume(log), -3.1)
        summ = 't: 1 I: -99.0 LUFS\nSummary:\n\n  Integrated loudness:\n    I:         -20.1 LUFS\n    Threshold: -30.1 LUFS\n\n  Loudness range:\n    LRA:         3.0 LU\n'
        self.assertEqual(R.parse_integrated_lufs(summ), -20.1)
        self.assertEqual(R.parse_lra(summ), 3.0)

    def test_duck_envelope_depth_and_ramps(self):
        total = 48000 * 10
        g = R.duck_envelope_db(total, [(3.0, 6.0)], -16.0, 0.3)
        at = lambda t: g[int(round(t * 48000))]
        self.assertAlmostEqual(at(4.5), -16.0, places=6)
        self.assertAlmostEqual(at(3.0), -16.0, places=6)
        self.assertAlmostEqual(at(2.85), -8.0, delta=0.01)
        self.assertAlmostEqual(at(2.7), 0.0, delta=0.01)
        self.assertAlmostEqual(at(6.15), -8.0, delta=0.01)
        self.assertAlmostEqual(at(6.3), 0.0, delta=0.01)
        self.assertAlmostEqual(at(9.0), 0.0, places=6)

    def test_duck_measure_reports_median_and_share_under_6_db(self):
        rng = np.random.default_rng(1)
        n = 48000 * 6
        t = np.arange(n) / 48000.0
        tone = (0.1 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)     # RMS -23 dBFS
        narr = np.stack([tone, tone], axis=1)
        narr[48000 * 4:] = 0                                              # silence: not a speaking window
        bed = rng.normal(0, 10 ** (-37 / 20), size=(n, 2)).astype(np.float32)  # RMS -37 dBFS
        m = R.duck_measure(narr, bed)
        self.assertAlmostEqual(m['median_db'], 14.0, delta=0.6)
        self.assertEqual(m['share_under_6db'], 0.0)
        self.assertEqual(m['speaking_windows'], 10)
        bed_loud = bed * np.float32(10 ** (10 / 20))                      # only 4 dB under the narration
        self.assertEqual(R.duck_measure(narr, bed_loud)['share_under_6db'], 1.0)

    def test_close_keeps_the_bed_until_one_second_before_the_end(self):
        a = EDIT['audio']
        self.assertLessEqual(a['final_quiet_s'] + a['final_fade_s'], 1.05)
        self.assertGreaterEqual(a['final_quiet_s'] + a['final_fade_s'], 0.95)
        s7 = EDIT['sections'][-1]
        self.assertNotEqual(s7['bed']['source'], 'glasses', 'glasses audio is near-silent after the recitation ends')

    def test_cue_times_snap_to_narration_pauses(self):
        s = next(x for x in EDIT['sections'] if x['id'] == 's3')
        ps = next(p for p in PLAN['sections'] if p['id'] == 's3')
        pauses = R.narration_pauses(str(R.rp(s['narration']['file'])))
        self.assertGreaterEqual(len(pauses), 4)
        for phrase in ('Muse Voice', 'Muse Spark'):
            t_rel = R.phrase_time(EDIT, ps, s, phrase)
            narr_t = t_rel + ps['start_s'] - ps['narr_start']
            self.assertTrue(any(abs(narr_t - e) < 0.01 for _, e in pauses), f'{phrase} not snapped to a pause end')
        order = [R.phrase_time(EDIT, ps, s, p) for p in ('Muse Voice', 'Muse Spark')]
        self.assertLess(order[0], order[1])
        self.assertLess(order[1], ps['duration_s'])

    def test_narration_files_have_speech_and_positive_duration(self):
        for s in EDIT['sections']:
            if not s['narration'].get('file'):
                continue
            info = R.narration_info(str(R.rp(s['narration']['file'])))
            self.assertGreater(info['duration'], 5)
            self.assertLess(info['speech_start'], 0.5)
            self.assertGreater(info['speech_end'], info['duration'] - 0.8)


CUE_FREE = None


def s1_of(edit):
    return next(s for s in edit['sections'] if s['id'] == 's1')


class OpeningS1(unittest.TestCase):
    def test_s1_is_the_phone_clip_with_its_own_audio_then_the_lens_recording(self):
        s1 = s1_of(EST)
        self.assertNotIn('file', s1['narration'], 'no Callum s1 and no narration file')
        self.assertEqual(s1['narration']['duration_s'], 33.9)
        est, est_label, lens, lens_label = s1['layers'][1:]
        self.assertEqual([l['type'] for l in s1['layers']], ['paper', 'footage', 'plate', 'footage', 'plate'])
        self.assertEqual((est['source'], est['in'], est['out'], est['start_s'], est['end_s']), ('establishing', 0.0, 24.0, 0, 24.0))
        self.assertEqual((lens['source'], lens['in'], lens['out'], lens['start_s']), ('glasses_desk', 24.3, 34.2, 24.0))
        self.assertAlmostEqual(est['out'] - est['in'] + lens['out'] - lens['in'], s1['narration']['duration_s'], places=6)
        self.assertEqual(est_label['lines'][0]['text'], 'Filmed on a phone')
        self.assertEqual(lens_label['lines'][0]['text'], 'What I see through the glasses')
        self.assertEqual((est_label['end_s'], lens_label['start_s']), (24.0, 24.0))
        self.assertEqual(EST['footage']['establishing']['label'], 'Filmed on a phone')
        self.assertEqual(EST['footage']['establishing']['file'], 'recordings/v1/IMG_4535-sdr.mp4')

    def test_the_cut_to_s2_is_where_the_lens_clip_ends(self):
        ps = EST_PLAN['sections'][0]
        self.assertEqual((ps['id'], ps['frames'], ps['start_s'], ps['end_s']), ('s1', 1017, 0.0, 33.9))
        self.assertAlmostEqual(24.0 * R.FPS, 720)
        self.assertAlmostEqual((34.2 - 24.3) * R.FPS, 297, places=6)
        s2 = EST_PLAN['sections'][1]
        self.assertEqual((s2['id'], s2['start_s']), ('s2', 33.9))
        self.assertAlmostEqual(s2['narr_start'], 33.9 + EST['timing']['default_gap_s'], places=6)
        with tempfile.TemporaryDirectory() as d:
            stages, _ = R.resolve_section(EST, EST_PLAN, s1_of(EST), PAL, Path(d))
        foots = [st for st in stages if st['kind'] == 'footage']
        self.assertEqual((foots[0]['start'], foots[0]['end'], foots[1]['start'], foots[1]['end']), (0, 24.0, 24.0, None))
        self.assertAlmostEqual(foots[1]['in'], 24.3, places=3)
        self.assertAlmostEqual(foots[1]['len'], 9.9, places=3)

    def test_no_callum_s1_anywhere(self):
        blob = json.dumps(EST['sections']) + json.dumps(FB['sections']) + R.DEFAULT_EDIT.read_text()
        for needle in ('narration/s1.mp3', 's1-fallback', 'narration/own/s1'):
            self.assertNotIn(needle, blob)
        for edit in (EST, FB, TOG):
            self.assertNotIn('s1', [Path(s['narration']['file']).stem for s in edit['sections'] if s['narration'].get('file')])

    def test_portrait_clips_are_pillar_boxed_never_cropped(self):
        self.assertEqual(R.contain_rect(1080, 1920, 1920, 1080), [656, 0, 608, 1080])
        self.assertEqual(R.contain_rect(1920, 1080, 1920, 1080), [0, 0, 1920, 1080])
        self.assertEqual(R.contain_rect(1280, 720, 1920, 1080), [0, 0, 1920, 1080])
        for sw, sh in ((1080, 1920), (976, 1296), (1000, 1000), (3840, 2160)):
            x, y, w, h = R.contain_rect(sw, sh, 1920, 1080)
            self.assertLessEqual(w, 1920)
            self.assertLessEqual(h, 1080)
            self.assertAlmostEqual(w / h, sw / sh, delta=0.01 * sw / sh)
            self.assertEqual((x, y), ((1920 - w) // 2, (1080 - h) // 2))
        est = s1_of(EST)['layers'][1]
        self.assertEqual(est['crop'], [0, 0, 1080, 1920], 'the whole portrait frame is kept: the face box sits top-right')
        self.assertEqual(est['dest'], R.contain_rect(1080, 1920, 1920, 1080))
        self.assertEqual(s1_of(EST)['layers'][0], {'type': 'paper'})
        info = R.probe_video(R.rp('recordings/v1/IMG_4535-sdr.mp4'))
        self.assertEqual((info['w'], info['h'], info['color_transfer'], info['color_range']), (1080, 1920, 'bt709', 'tv'))
        self.assertAlmostEqual(info['duration'], 24.041, places=2)
        label = s1_of(EST)['layers'][2]
        bb = R.paint_plate(EST, PAL, label).getchannel('A').getbbox()
        self.assertGreaterEqual(bb[0], est['dest'][0] + est['dest'][2], 'the label sits on the paper pillar, not on the clip')
        with tempfile.TemporaryDirectory() as d:
            cmd = R.build_section_cmd(EST, EST_PLAN, s1_of(EST), PAL, Path(d), 'x.mp4')
        graph = cmd[cmd.index('-filter_complex') + 1]
        self.assertIn('crop=1080:1920:0:0', graph)
        self.assertIn('scale=w=608:h=1080', graph)
        self.assertIn('overlay=x=656:y=0', graph)
        self.assertEqual(sum(1 for c in cmd if c == '-ss'), 2)

    def test_s1_audio_voice_is_levelled_undudcked_and_the_bed_starts_under_the_lens_clip(self):
        with tempfile.TemporaryDirectory() as d:
            wav, rep = R.build_audio(EST, EST_PLAN, Path(d))
        v = rep['voice'][0]
        self.assertEqual((v['section'], v['source'], v['in'], v['out'], v['start_s']), ('s1', 'establishing', 0.0, 24.0, 0.0))
        self.assertAlmostEqual(v['measured_lufs'] + v['gain_db'], -20.0, delta=0.1)
        self.assertLessEqual(v['peak_dbfs_before_limiter'], -3.0, 'the voice already peaks at or below -3 dBFS')
        self.assertEqual(v['duck_db_under_voice_min'], 0.0, 'the on-camera voice is never ducked')
        self.assertEqual(v['bed_under_voice_max_abs'], 0.0, 'no bed under the on-camera voice')
        self.assertAlmostEqual(rep['stems']['voice_only_lufs'], -20.0, delta=1.0)
        b1 = next(b for b in rep['bed'] if b['section'] == 's1')
        self.assertAlmostEqual(b1['measured_lufs'] + b1['gain_db'], -23.0, delta=0.1)
        win = rep['bed_windows']['s1']
        self.assertAlmostEqual(win['start_s'], 24.0, places=3)
        self.assertEqual(win['duck_db_min'], 0.0, 'the bed under the lens recording is at the normal level, not ducked')
        self.assertEqual([n['section'] for n in rep['narration']], ['s2', 's3', 's4', 's6', 's7'])
        self.assertEqual(rep['stems']['duck_depth_db_min'], -16.0)
        self.assertLessEqual(rep['mix_peak_dbfs'], -3.0 + 0.05)
        self.assertGreaterEqual(rep['duck_measure']['speaking']['median_db'], 12.0)


class S7Alignment(unittest.TestCase):
    def test_2_282_arrives_on_hear_the_recitation(self):
        s7 = next(s for s in EST['sections'] if s['id'] == 's7')
        ps = next(p for p in EST_PLAN['sections'] if p['id'] == 's7')
        t_hear = R.phrase_time(EST, ps, s7, 'Hear the recitation')
        with tempfile.TemporaryDirectory() as d:
            stages, _ = R.resolve_section(EST, EST_PLAN, s7, PAL, Path(d))
        st = next(x for x in stages if x['kind'] == 'footage')
        self.assertEqual(st['file'], R.rp(EST['footage']['glasses_desk']['file']))
        arrival = st['start'] + (33.8 - st['in'])
        self.assertAlmostEqual(arrival, t_hear, delta=1.5 / R.FPS)
        self.assertGreaterEqual(st['in'], 0)
        self.assertAlmostEqual(R.bed_in(EST, ps, s7) + t_hear, 33.8, places=6)
        card = next(l for l in s7['layers'] if l['type'] == 'card')
        self.assertEqual(card['appear_phrase'], 'Follow the meaning.')
        self.assertGreater(R.phrase_time(EST, ps, s7, card['appear_phrase']), t_hear)

    def test_s6_holds_on_the_desk_clip_44_to_52_under_the_lines(self):
        f = layers('s6', 'footage', EST)[0]
        self.assertEqual((f['source'], f['in'], f['out'], f['freeze_after']), ('glasses_desk', 44.0, 52.0, True))
        self.assertEqual(len(content_plates('s6', EST)), 2)

    def test_s1_lens_recording_is_the_desk_clip_24_3_to_34_2(self):
        f = next(l for l in layers('s1', 'footage', EDIT) if l['id'] == 'main')
        self.assertEqual((f['source'], f['in'], f['out']), ('glasses_desk', 24.3, 34.2))


class ToggleAndPlaceholder(unittest.TestCase):
    def test_s5_exists_only_when_a_toggle_clip_is_set(self):
        # no clip: s5 dropped, s4 uses the line without the bridge, s6 follows s4 directly
        by = {s['id']: s for s in EDIT['sections']}
        self.assertNotIn('s5', by)
        self.assertTrue(by['s4']['narration']['file'].endswith('s4-fallback.mp3'))
        self.assertEqual(by['s6']['narration']['gap_before_s'], 0.35)
        self.assertFalse(EDIT['toggle_active'])
        # with a clip: s5 plays it, s4 keeps the bridged line, s6 waits out the hold
        byt = {s['id']: s for s in TOG['sections']}
        self.assertTrue(TOG['toggle_active'])
        self.assertTrue(byt['s4']['narration']['file'].endswith('narration/s4.mp3'))
        self.assertEqual(byt['s6']['narration']['gap_before_s'], 2.35)
        s5 = byt['s5']
        self.assertEqual([l['type'] for l in s5['layers']], ['paper', 'footage', 'plate', 'plate'])
        foot = s5['layers'][1]
        self.assertEqual((foot['source'], foot['in'], foot['out']), ('toggle', 66.5, 72.5))
        self.assertEqual(s5['layers'][3]['lines'][0], {'text': 'Arabic only, for memorization.', 'size': 56, 'bold': True})
        x, y, w, h = foot['dest']
        self.assertEqual((y, h), (0, 1080), 'a portrait clip is pillar-boxed full height')
        self.assertEqual(foot['crop'], [0, 0, 1206, 2622], 'never cropped')
        self.assertEqual(R.make_plan(TOG)['sections'][4]['id'], 's5')
        self.assertLess(R.make_plan(EDIT)['duration_s'], 180)
        self.assertLess(R.make_plan(TOG)['duration_s'], 180)

    def test_toggle_input_is_validated(self):
        with self.assertRaises(FileNotFoundError):
            R.apply_toggle(BASE, dict(STAND_IN_TOGGLE, file='recordings/nope.mov'))
        with self.assertRaises(ValueError):
            R.apply_toggle(BASE, dict(STAND_IN_TOGGLE, out=9999.0))
        with self.assertRaises(ValueError):
            R.apply_toggle(BASE, dict(STAND_IN_TOGGLE, **{'in': None}))
        real = R.probe_video(R.rp(STAND_IN_TOGGLE['file']))
        with mock.patch.object(R, 'probe_video', return_value=dict(real, color_transfer='smpte2084')):
            with self.assertRaises(ValueError):
                R.apply_toggle(BASE, STAND_IN_TOGGLE)
        # fallback mode drops s5 even when a clip is set
        fb = R.apply_toggle(R.apply_fallback(RAW, True), STAND_IN_TOGGLE)
        self.assertNotIn('s5', [s['id'] for s in fb['sections']])

    def test_no_mode_can_render_recording_pending(self):
        needles = ('recording pending', 'pending', 'placeholder')
        for src in (Path(R.__file__).read_text(), (R.DEFAULT_EDIT).read_text()):
            self.assertNotIn('recording pending', src.lower())
        combos = 0
        for fb in (False, True):
            for tog in (None, STAND_IN_TOGGLE):
                e = R.apply_fallback(RAW, fb)
                e = R.apply_toggle(e, tog) if tog else R.apply_toggle(e)
                for voice in ('callum', 'own'):
                    e2 = R.apply_narration_source(e, voice)
                    blob = json.dumps(e2['sections']).lower()
                    for n in needles:
                        self.assertNotIn(n, blob, f'fallback={fb} toggle={bool(tog)} voice={voice}: {n!r}')
                    for sid, text in all_texts(e2):
                        self.assertNotIn('pending', text.lower())
                    combos += 1
        self.assertEqual(combos, 8)
        for voice in ('callum', 'own'):
            for fb in (None, True):
                e = R.load_edit(fallback=fb, voice=voice)
                self.assertNotIn('pending', json.dumps(e['sections']).lower())
                self.assertNotIn('s5', [s['id'] for s in e['sections']])


class Fallback(unittest.TestCase):
    def test_fallback_uses_the_fallback_narration_and_pictures(self):
        by = {s['id']: s for s in FB['sections']}
        self.assertNotIn('file', by['s1']['narration'], 'fallback s1 is the same on-camera opening: no Callum s1')
        self.assertTrue(by['s4']['narration']['file'].endswith('s4-fallback.mp3'))
        self.assertTrue(by['s6']['narration']['file'].endswith('s6.mp3'))
        self.assertEqual(by['s6']['narration']['gap_before_s'], 0.35)
        f6 = next(l for l in by['s6']['layers'] if l['type'] == 'footage')
        self.assertEqual((f6['source'], f6['in'], f6['out']), ('phone_long', 60.0, 72.0))
        f7 = next(l for l in by['s7']['layers'] if l['type'] == 'footage')
        self.assertEqual(f7['source'], 'glasses')
        self.assertGreaterEqual(f7['in'], 14.3)
        self.assertLessEqual(f7['out'], 29.5)
        self.assertFalse(RAW['fallback']['enabled'])

    @unittest.skipUnless(FB_READY, 'fallback narration files not generated yet')
    def test_fallback_footage_stays_inside_the_source_files(self):
        plan = R.make_plan(FB)
        for s in FB['sections']:
            ps = next(p for p in plan['sections'] if p['id'] == s['id'])
            for l in s['layers']:
                if l['type'] == 'footage':
                    dur = probe_duration(R.rp(FB['footage'][l['source']]['file']))
                    self.assertLessEqual(l['out'], dur + 1e-6, s['id'])
                    self.assertLess(l['start_s'], ps['duration_s'], s['id'])

    @unittest.skipUnless(FB_READY, 'fallback narration files not generated yet')
    def test_fallback_plan_is_valid_and_s7_english_lands_on_hear_the_recitation(self):
        plan = R.make_plan(FB)
        self.assertLess(plan['duration_s'], 180)
        self.assertEqual(plan['audio_samples'], plan['total_frames'] * 1600)
        s7 = next(s for s in FB['sections'] if s['id'] == 's7')
        ps = next(p for p in plan['sections'] if p['id'] == 's7')
        t_hear = R.phrase_time(FB, ps, s7, 'Hear the recitation')
        f7 = next(l for l in s7['layers'] if l['type'] == 'footage')
        landing = f7['start_s'] + (27.0 - f7['in'])  # 112:4 arrives at 27.0 s in take-03
        self.assertAlmostEqual(landing, t_hear, delta=0.1)
        card = next(l for l in s7['layers'] if l['type'] == 'card')
        self.assertGreater(card['start_s'], landing + 1.0)
        for s in FB['sections']:
            if s['narration'].get('file'):
                self.assertTrue(R.rp(s['narration']['file']).exists(), s['id'])
            ps = next(p for p in plan['sections'] if p['id'] == s['id'])
            for l in s['layers']:
                if l['type'] == 'footage' and not l.get('freeze_after'):
                    self.assertLessEqual(l.get('end_s', ps['duration_s']) - l['start_s'], l['out'] - l['in'] + 1 / R.FPS)

    @unittest.skipUnless(FB_READY, 'fallback narration files not generated yet')
    def test_fallback_ribbon_states_fit_the_shorter_s4(self):
        plan = R.make_plan(FB)
        ps = next(p for p in plan['sections'] if p['id'] == 's4')
        s4 = next(s for s in FB['sections'] if s['id'] == 's4')
        foot = next(l for l in s4['layers'] if l['type'] == 'footage')
        rib = next(l for l in s4['layers'] if l['type'] == 'ribbon')
        for w in rib['windows']:
            self.assertLess(foot['start_s'] + w['from_source_s'] - foot['in'], ps['duration_s'])


class NarrationSource(unittest.TestCase):
    def test_callum_is_the_default_and_keeps_the_files_as_written(self):
        self.assertEqual(RAW['narration']['source'], 'callum')
        self.assertEqual(EDIT['narration']['source'], 'callum')
        self.assertTrue(EDIT['sections'][1]['narration']['file'].endswith('narration/s2.mp3'))

    def test_own_source_resolves_every_section_to_own_wav(self):
        own = R.apply_narration_source(EDIT, 'own')
        self.assertEqual(own['narration']['source'], 'own')
        by = {s['id']: s for s in own['sections']}
        self.assertNotIn('file', by['s1']['narration'], 's1 has no narration file: Faraz speaks on camera')
        stems = {sid: Path(s['narration']['file']).stem for sid, s in by.items() if s['narration'].get('file')}
        self.assertEqual(stems, {'s2': 's2', 's3': 's3', 's4': 's4-fallback', 's6': 's6', 's7': 's7'})
        for sid, stem in stems.items():
            self.assertEqual(by[sid]['narration']['file'], f"build/video-v1.0/narration/own/{stem}.wav")
            self.assertTrue(by[sid]['narration']['callum_file'].endswith('.mp3'))
        own_t = R.apply_narration_source(TOG, 'own')
        self.assertEqual([Path(s['narration']['file']).stem for s in own_t['sections'] if s['narration'].get('file')], ['s2', 's3', 's4', 's5', 's6', 's7'])
        for a, b in zip(EDIT['sections'], own['sections']):
            for k in ('cut_offset_s', 'gap_before_s'):
                self.assertEqual(a['narration'].get(k), b['narration'].get(k))

    def test_own_source_in_fallback_mode_uses_the_fallback_takes(self):
        own_fb = R.apply_narration_source(FB, 'own')
        by = {s['id']: s['narration'].get('file') for s in own_fb['sections']}
        self.assertEqual(list(by), ['s1', 's2', 's3', 's4', 's6', 's7'])
        self.assertIsNone(by['s1'])
        self.assertEqual(by['s4'], 'build/video-v1.0/narration/own/s4-fallback.wav')
        self.assertEqual(by['s6'], 'build/video-v1.0/narration/own/s6.wav')
        self.assertEqual(R.load_edit(fallback=True, voice='own')['sections'][3]['narration']['file'], by['s4'])

    def test_unknown_source_is_rejected_and_missing_own_files_name_the_fix(self):
        with self.assertRaises(ValueError):
            R.apply_narration_source(EDIT, 'robot')
        own = R.apply_narration_source(EDIT, 'own')
        own['narration']['own_dir'] = '/nonexistent-own-dir'
        for s in own['sections']:
            if s['narration'].get('file'):
                s['narration']['file'] = f"/nonexistent-own-dir/{s['id']}.wav"
        with self.assertRaises(FileNotFoundError) as cm:
            R.make_plan(own)
        self.assertIn('ingest_voice.py', str(cm.exception))
        self.assertIn('s2', str(cm.exception))
        self.assertNotIn('s1:', str(cm.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)
