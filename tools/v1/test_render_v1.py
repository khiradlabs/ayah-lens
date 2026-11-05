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
                yield s['id'], (ln['text'] if isinstance(ln, dict) else ln)
            for nd in l.get('nodes', []):
                yield s['id'], ' \u00b7 '.join(R.node_parts(nd))


class EditJson(unittest.TestCase):
    def test_edit_json_is_valid_and_complete(self):
        self.assertEqual([s['id'] for s in BASE['sections']], ['s1', 's2', 's3', 's4', 's5', 's3b', 's6', 's7'])
        self.assertEqual([s['id'] for s in EDIT['sections']], ['s1', 's2', 's3', 's4', 's3b', 's6', 's7'], 'no toggle clip: s5 is dropped')
        self.assertEqual([s['id'] for s in TOG['sections']], ['s1', 's2', 's3', 's4', 's5', 's3b', 's6', 's7'])
        self.assertIsNone(RAW['toggle']['file'])
        self.assertFalse(RAW['fallback']['enabled'], 'fallback mode must be off by default')
        self.assertEqual(EDIT['canvas'], {'w': 1920, 'h': 1080, 'fps': 30})
        self.assertEqual((EDIT['palette']['paper'], EDIT['palette']['ink'], EDIT['palette']['blue'], EDIT['palette']['red']),
                         ('#ECE7D3', '#1E1E1E', '#465D79', '#B94B37'))
        self.assertAlmostEqual(EDIT['palette']['dim_mix'], 0.55)
        for k, f in EDIT['fonts'].items():
            self.assertTrue(Path(f).exists(), f'font {k} missing: {f}')
        self.assertTrue(Path(EDIT['quran']['qpc_json']).exists())
        self.assertEqual(EDIT['version'], '1.3')
        self.assertTrue(EDIT['output'].endswith('Ayah-Lens-Demo-v1.3.mp4'))
        self.assertEqual(EDIT['limits'], {'cap_s': 178.0, 'hard_s': 180.0})
        for key, src in EDIT['footage'].items():
            self.assertTrue(R.rp(src['file']).exists(), key)
            self.assertIn(src['range'], ('tv', 'pc'))
            self.assertEqual(src['matrix'], 'bt709')
        allowed = {'paper', 'card', 'plate', 'pin', 'ribbon', 'footage', 'diagram', 'api_card'}
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
            s6 = [l['lines'][0]['text'] for l in layers('s6', 'plate', edit) if l.get('role') == 'stat']
            self.assertEqual(s6, [exact['s6_line1'], 'Unchanged source text: Tanzil Arabic \u00b7 Pickthall English', exact['s6_line2']],
                             'the stale-decisions line left with its sentence: node 7 already shows it')
            s7 = layers('s7', 'card', edit)[0]
            self.assertEqual(' \u00b7 '.join(l['text'] for l in s7['lines']), exact['s7_card'])
        s2 = [l['lines'][0]['text'] for l in content_plates('s2') if l.get('role') != 'rubric']
        self.assertEqual(' \u00b7 '.join(s2), exact['s2_card'])
        s5 = next(l for l in layers('s5', 'plate', TOG) if l.get('role') not in ('label', 'rubric'))['lines'][0]
        self.assertEqual((s5['text'], s5['size']), ('Arabic only, for memorization.', 56))
        s3 = [l['lines'][0]['text'] for l in layers('s3', 'plate')]
        self.assertIn('audio goes to Muse Voice', s3)
        self.assertIn('English prepared in advance', s3)
        title = layers('s1', 'card')[0]['lines']
        self.assertEqual((title[0]['text'], title[0]['size']), ('Ayah Lens', 160))
        self.assertEqual((title[1]['text'], title[1]['size']), ('Meta Global AI Developer Hackathon \u00b7 Build for Your World', 48))
    def test_every_latin_word_is_large_enough(self):
        """Cap height 40 px needs a 56 px Arial font. Labels, rubric plates, the s6 stat lines and the title card's
        sub-line are 48 px by decision; diagram node titles are 48 px and every other diagram text is 40 px or more."""
        self.assertGreaterEqual(EDIT['min_latin_px'], 56)
        self.assertEqual(EDIT['label_px'], 48)
        for edit in (EDIT, FB, EST):
            for s in edit['sections']:
                for l in s['layers']:
                    for ln in l.get('lines', []):
                        if isinstance(ln, str):
                            continue
                        small = l.get('role') in ('label', 'illustration', 'rubric', 'stat') or l['type'] == 'card'
                        floor = edit['label_px'] if small else edit['min_latin_px']
                        if l.get('role') == 'future':
                            floor = 44  # the three 'next, with more development' lines are 44 px by decision
                        self.assertGreaterEqual(ln['size'], floor, f"{s['id']}: {ln['text']!r}")
                    if l['type'] == 'pin':
                        self.assertGreaterEqual(l['size'], 56)
                    if l['type'] == 'ribbon':
                        self.assertGreaterEqual(l['counter_size'], 56)
                        _, size, _, _ = R.layout_ribbon(edit, l)
                        self.assertGreaterEqual(size, edit['min_text_px'])
                    if l['type'] == 'diagram':
                        self.assertEqual(l['title_px'], 48)
                        self.assertGreaterEqual(min(l['sub_px'], l['tag_px'], l['audio_flow']['label_px']), 40)
                    if l['type'] == 'api_card':
                        self.assertEqual((l['line_px'], l['code']['px']), (44, 40))


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
        self.assertEqual([l['lines'][0]['text'] for l in layers('s1', 'plate') if l.get('role') == 'label'], ['Filmed on a phone', 'What I see through the glasses'])
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

    def test_every_boundary_is_a_half_second_crossfade_and_narration_starts_on_the_first_frame_after_it(self):
        X = EDIT['timing']['crossfade_s']
        self.assertEqual(X, 0.5)
        self.assertEqual(PLAN['crossfade_frames'], 15)
        self.assertEqual(EDIT['audio']['crossfade_s'], X, 'the bed crossfades over the same frames as the picture')
        for edit, plan in ((EDIT, PLAN), (TOG, R.make_plan(TOG))):
            secs = plan['sections']
            self.assertEqual(secs[0]['fade_in_frames'], 0)
            self.assertEqual(secs[-1]['tail_frames'], 0)
            self.assertEqual(sum(p['frames'] for p in secs), plan['total_frames'])
            for a, b in zip(secs, secs[1:]):
                self.assertEqual((a['tail_frames'], b['fade_in_frames']), (15, 15))
                self.assertEqual(b['start_frame'], a['end_frame'], 'the fade out of one section begins on the frame the next fades in')
                self.assertEqual(a['render_frames'], a['frames'] + 15)
                self.assertGreaterEqual(a['frames'], 2 * 15 - 15, 'a section is longer than its fade')
                if b['has_narration']:
                    self.assertEqual(round(b['narr_start'] * R.FPS), b['start_frame'] + 15, f"{b['id']}: narration starts on the first frame after the fade")
                    self.assertAlmostEqual(b['narr_start'], (b['start_frame'] + 15) / R.FPS, places=9)
                    self.assertGreaterEqual(b['narr_start'], a['end_s'] + X - 1e-9, f"{b['id']}'s narration starts while {a['id']}'s picture is still on screen")
        # no section keeps the old gap model
        for s_ in BASE['sections']:
            self.assertNotIn('gap_before_s', s_['narration'], s_['id'])
        # the fade begins when the voice stops (sections with no explicit cut or end_at)
        by = {p['id']: p for p in PLAN['sections']}
        for sid in ('s2', 's3', 's4', 's6'):
            p = by[sid]
            self.assertGreaterEqual(p['end_s'], p['speech_end'] - 1e-9, f'{sid}: the fade starts before the voice has stopped')
            self.assertLess(p['end_s'] - p['speech_end'], 1 / R.FPS + 1e-9, f'{sid}: the fade starts later than needed')
        # the explicit ones: s3b holds the API card 2.5 s past the voice, s7 holds the close 1.0 s past it
        self.assertAlmostEqual(by['s3b']['end_s'] - by['s3b']['narr_end'], 2.5, delta=1 / R.FPS)
        self.assertAlmostEqual(by['s7']['end_s'] - by['s7']['narr_end'], 1.0, delta=1 / R.FPS)
        self.assertAlmostEqual(by['s6']['narr_start'] - by['s3b']['end_s'], 0.5, places=9, msg='s6 starts when the fade off the API card ends')
        self.assertAlmostEqual(by['s2']['narr_start'] - by['s1']['end_s'], 0.5, places=9)

    def test_the_assembly_filter_crossfades_every_boundary_at_its_plan_frame(self):
        g = R.xfade_graph(PLAN)
        self.assertEqual(g.count('xfade=transition=fade:duration=0.500000'), len(PLAN['sections']) - 1)
        for p in PLAN['sections'][1:]:
            self.assertIn(f"offset={p['start_frame'] / R.FPS:.6f}[", g)
        self.assertEqual(g.count(f'fps={R.FPS}'), len(PLAN['sections']))
        self.assertIn('setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709[vout]', g)

    def test_no_narration_begins_with_the_four_words_the_previous_one_ended_with(self):
        import re

        def words(t):
            return re.findall(r"[a-z0-9']+", t.lower())
        # the checker itself: a repeated four-word ending and opening is caught
        self.assertEqual(words('It is Ayah Lens.')[-4:], words('It is Ayah Lens, and')[:4])
        for edit in (EDIT, TOG, FB, EST):
            texts = []
            for s_ in edit['sections']:
                if s_['narration'].get('file'):
                    try:
                        texts.append((s_['id'], R.narration_text(edit, s_)))
                    except KeyError:
                        assert s_['id'] == 's5', 'only the stand-in s5 clip has no paragraph text'
            self.assertGreaterEqual(len(texts), 6)
            for (ida, ta), (idb, tb) in zip(texts, texts[1:]):
                self.assertNotEqual(words(ta)[-4:], words(tb)[:4], f'{idb} opens with the four words {ida} ended on: {" ".join(words(tb)[:4])!r}')
        by = {s_['id']: R.narration_text(EDIT, s_) for s_ in EDIT['sections'] if s_['narration'].get('file')}
        self.assertTrue(by['s2'].rstrip().endswith('This is Ayah Lens.'))
        self.assertFalse(by['s3'].startswith('This is Ayah Lens'), 'the v1.2 s3 no longer repeats the opener')

    def test_total_planned_duration_structure(self):
        self.assertGreaterEqual(PLAN['duration_s'], 165)
        self.assertEqual([p['id'] for p in PLAN['sections']], ['s1', 's2', 's3', 's4', 's3b', 's6', 's7'])
        self.assertEqual(PLAN['audio_samples'], PLAN['total_frames'] * 1600)
        pos = 0
        for p in PLAN['sections']:
            self.assertEqual(p['start_frame'], pos)
            self.assertGreater(p['frames'], 0)
            pos = p['end_frame']
        self.assertEqual(pos, PLAN['total_frames'])

    def test_total_planned_duration_is_under_the_178_s_cap(self):
        """RED in v1.2 as specified: the six narration files alone run 148.17 s and the establishing clip 24.0 s, so 178.0 s needs
        everything else (title card, lens recording, six crossfades, the s3b card hold, the close) inside 5.8 s. See the v1.2 report."""
        self.assertLessEqual(PLAN['duration_s'], EDIT['limits']['cap_s'], 'over the cap')
        self.assertLess(PLAN['duration_s'], EDIT['limits']['hard_s'], 'over the 180 s limit')


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
        s = next(x for x in EDIT['sections'] if x['id'] == 's3b')
        ps = next(p for p in PLAN['sections'] if p['id'] == 's3b')
        pauses = R.narration_pauses(str(R.rp(s['narration']['file'])))
        self.assertGreaterEqual(len(pauses), 8)
        diagram = next(l for l in s['layers'] if l['type'] == 'diagram')
        times = []
        for nd in diagram['nodes']:
            t_rel = R.phrase_time(EDIT, ps, s, nd['cue'])
            times.append(t_rel)
            narr_t = t_rel + ps['start_s'] - ps['narr_start']
            if nd['cue'] not in ('iPhone app', 'Muse Voice Transcribe') and not nd.get('cue_offset_s'):  # mid-sentence cues are proportional estimates
                self.assertTrue(any(abs(narr_t - e) < 0.01 for _, e in pauses), f"{nd['cue']} not snapped to a pause end")
        self.assertEqual(times, sorted(times), 'nodes must build in narration order')
        self.assertLess(times[-1] + diagram['nodes'][-1].get('cue_offset_s', 0.0) + 0.1, ps['narr_end'] - ps['start_s'] - diagram['slide']['before_narration_end_s'])
        late = next(nd for nd in diagram['nodes'] if nd.get('late'))
        self.assertGreater(R.phrase_time(EDIT, ps, s, late['late']['cue']), R.phrase_time(EDIT, ps, s, late['cue']))
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
    def test_s1_is_the_phone_clip_the_title_card_then_the_lens_recording(self):
        s1 = s1_of(EST)
        self.assertNotIn('file', s1['narration'], 'no Callum s1 and no narration file')
        self.assertEqual(s1['narration']['duration_s'], 28.8)
        self.assertEqual([l['type'] for l in s1['layers']], ['paper', 'footage', 'plate', 'plate', 'card', 'footage', 'plate'])
        _, est, est_label, rubric, card, lens, lens_label = s1['layers']
        self.assertEqual((est['source'], est['in'], est['out'], est['start_s'], est['end_s'], est['fade_s']), ('establishing', 0.0, 24.0, 0, 24.0, 1.0))
        self.assertEqual((lens['source'], lens['in'], lens['start_s'], lens['fade_s']), ('glasses_desk', 24.3, 24.8, 0.8))
        self.assertAlmostEqual(lens['out'] - lens['in'], 4.5, places=6, msg='4.0 s in the section plus the 0.5 s fade tail')
        # 24.0 s phone clip + 0.8 s title card hold + 4.0 s lens recording; each crossfade overlaps (0.8 s)
        self.assertAlmostEqual(24.0 + 0.8 + (lens['out'] - lens['in'] - 0.5), s1['narration']['duration_s'], places=6)
        self.assertEqual((card['start_s'], card['end_s'], card['fade_s']), (23.2, 25.6, 0.8))
        self.assertAlmostEqual(card['start_s'] + card['fade_s'], est['end_s'], places=6, msg='phone clip ends as the card is fully in')
        self.assertAlmostEqual(card['end_s'] - card['fade_s'], lens['start_s'], places=6, msg='the lens crossfade starts as the 2.0 s hold ends')
        self.assertAlmostEqual(lens['start_s'] - est['end_s'], 0.8, places=6)
        self.assertEqual(est_label['lines'][0]['text'], 'Filmed on a phone')
        self.assertEqual(lens_label['lines'][0]['text'], 'What I see through the glasses')
        self.assertEqual((est_label['end_s'], lens_label['start_s']), (24.0, 24.8))
        self.assertEqual(EST['footage']['establishing']['label'], 'Filmed on a phone')
        self.assertEqual(EST['footage']['establishing']['file'], 'recordings/v1/IMG_4535-sdr.mp4')
        # audio: voice fades in over 1.0 s and out over 0.8 s; the bed starts under the lens recording and fades in over 0.5 s
        self.assertEqual((s1['voice']['fade_in_s'], s1['voice']['fade_out_s'], s1['voice']['lufs']), (1.0, 0.8, -20.0))
        self.assertEqual((s1['bed']['start_s'], s1['bed']['fade_in_s'], s1['bed']['in']), (24.8, 0.5, 24.3))

    def test_the_cut_to_s2_is_where_the_lens_clip_ends(self):
        ps = EST_PLAN['sections'][0]
        self.assertEqual((ps['id'], ps['frames'], ps['start_s'], ps['end_s']), ('s1', 864, 0.0, 28.8))
        self.assertEqual(ps['render_frames'], 864 + 15, 'plus the 15-frame tail that fades into s2')
        s2 = EST_PLAN['sections'][1]
        self.assertEqual((s2['id'], s2['start_s']), ('s2', 28.8))
        self.assertAlmostEqual(s2['narr_start'], 28.8 + 0.5, places=6)
        with tempfile.TemporaryDirectory() as d:
            stages, _ = R.resolve_section(EST, EST_PLAN, s1_of(EST), PAL, Path(d))
        foots = [st for st in stages if st['kind'] == 'footage']
        self.assertEqual((foots[0]['start'], foots[0]['end'], foots[1]['start'], foots[1]['end']), (0, 24.0, 24.8, None))
        self.assertAlmostEqual(foots[1]['in'], 24.3, places=3)
        self.assertAlmostEqual(foots[1]['len'], 4.5, places=3)
        self.assertAlmostEqual(foots[1]['start'] + foots[1]['len'], ps['render_frames'] / R.FPS, places=3)
        self.assertEqual((foots[0]['fade'], foots[1]['fade']), (1.0, 0.8))

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
        self.assertEqual(label['lines'][0]['text'], 'Filmed on a phone')
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
        self.assertAlmostEqual(win['start_s'], 24.8, places=3)
        self.assertEqual(win['duck_db_min'], 0.0, 'the bed under the lens recording is at the normal level, not ducked')
        self.assertEqual([n['section'] for n in rep['narration']], ['s2', 's3', 's4', 's3b', 's6', 's7'])
        self.assertEqual(rep['stems']['duck_depth_db_min'], -16.0)
        self.assertLessEqual(rep['mix_peak_dbfs'], -3.0 + 0.05)
        self.assertGreaterEqual(rep['duck_measure']['speaking']['median_db'], 12.0)

    def test_the_three_opening_transitions_are_gradual_fades(self):
        """Render the s1 picture and frame-diff the boundaries: each transition must change gradually over at least 20 frames."""
        import copy
        edit = copy.deepcopy(EST)
        with tempfile.TemporaryDirectory() as d:
            edit['work_dir'] = d
            R.render_sections(edit, EST_PLAN, only={'s1'})
            raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(Path(d) / 's1.mp4'), '-vf', 'scale=192:108:flags=area,format=gray',
                                           '-f', 'rawvideo', '-'])
        frames = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 108, 192).astype(np.float64)
        self.assertEqual(len(frames), 879, '864 frames plus the 15-frame fade tail')

        def progress(a, b):
            ref = np.abs(frames[b] - frames[a]).mean()
            self.assertGreater(ref, 8, 'the two ends of a transition must differ')
            return np.array([np.abs(frames[f] - frames[a]).mean() / ref for f in range(a, b + 1)])
        for name, a, b in (('fade in from paper', 0, 30), ('phone clip to title card', 696, 720), ('title card to lens recording', 744, 768)):
            p = progress(a, b)
            mid = int(((p > 0.05) & (p < 0.95)).sum())
            self.assertGreaterEqual(mid, 20, f'{name}: only {mid} gradual frames')
            self.assertLessEqual(float(np.abs(np.diff(p)).max()), 0.15, f'{name}: a sudden jump')
            self.assertGreaterEqual(float(p[-1]), 0.9, name)
        # the boundaries themselves never jump (the lens recording's own fast camera motion is not a cut)
        step = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
        for a, b in ((0, 30), (690, 726), (738, 774)):
            self.assertLess(float(step[a:b].max()), 14.0, f'a hard cut near frame {a}-{b}')
        # the last frames, before the fade into s2: the lens clip's own camera pan makes the steps large but they ramp, never jump
        self.assertLess(float(np.abs(np.diff(step[840:878])).max()), 10.0, 'a hard cut in the tail of s1')


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

    def test_s7_says_today_then_shows_three_future_uses_over_the_footage_as_they_are_spoken(self):
        s7 = next(s for s in EST['sections'] if s['id'] == 's7')
        ps = next(p for p in EST_PLAN['sections'] if p['id'] == 's7')
        plates = [l for l in s7['layers'] if l['type'] == 'plate' and l.get('role') in ('stat', 'future')]
        today, tag, *future = plates
        x = EST['script_lines_exact']
        self.assertEqual(today['lines'][0]['text'], 'Today: the meaning follows the recitation, hands free')
        self.assertEqual(tag['lines'][0]['text'], 'NEXT, WITH MORE DEVELOPMENT')
        self.assertEqual([l['lines'][0]['text'] for l in future],
                         ['Support for those memorizing the Quran', 'Flag a wrong recitation for a learner', 'The meaning in any language'])
        self.assertEqual([x['s7_today'], x['s7_next_tag'], x['s7_next1'], x['s7_next2'], x['s7_next3']], [l['lines'][0]['text'] for l in plates])
        self.assertEqual([l['lines'][0]['size'] for l in (today, tag)], [48, 48])
        self.assertEqual([l['lines'][0]['size'] for l in future], [44, 44, 44])
        self.assertEqual((tag['fill'], tag['lines'][0]['color']), ('red', 'paper'), 'the NEXT tag is red')
        self.assertEqual([l['appear_phrase'] for l in plates],
                         ['Today, Ayah Lens does one thing well', 'With more development', 'memorize the Quran', 'flag a wrong recitation', 'and bring the meaning'])
        text = R.narration_text(EST, s7)
        for l in plates:
            self.assertIn(l['appear_phrase'], text)
        self.assertTrue(text.startswith('Today, Ayah Lens does one thing well: the meaning follows the recitation, hands free.'))
        self.assertIn('With more development, the same foundation can support', text)
        self.assertNotIn('That is where this is going', text)
        cues = [R.phrase_time(EST, ps, s7, l['appear_phrase']) for l in plates]
        t_hear = R.phrase_time(EST, ps, s7, 'Hear the recitation')
        t_close = R.phrase_time(EST, ps, s7, 'Follow the meaning.')
        self.assertEqual(cues, sorted(cues), 'the lines appear in the order the voice reaches them')
        self.assertEqual(len(set(round(c, 1) for c in cues)), 5)
        self.assertLess(cues[-1], t_hear)
        self.assertLess(t_hear, t_close)
        self.assertGreaterEqual(t_close - t_hear, 1.0, 'the two short closing sentences snap to their own pauses')
        self.assertLessEqual(ps['narr_end'] - ps['start_s'] - t_close, 1.6, 'the close card arrives on the last sentence')
        card = next(l for l in s7['layers'] if l['type'] == 'card')
        self.assertEqual(card['appear_phrase'], 'Follow the meaning.')
        self.assertEqual(s7['layers'].index(card), len(s7['layers']) - 1, 'the card is on top of the plates: they stay until it arrives')
        for l in plates:
            self.assertNotIn('end_s', l, 'the lines stay until the close card')
        # layout: today on the left, the future block on the right, all above the lens text and clear of each other and the label
        boxes = [R.paint_plate(EST, PAL, l).getchannel('A').getbbox() for l in plates]
        for bb in boxes:
            self.assertLessEqual(bb[3], 559, 'above the lens text zone')
            self.assertLessEqual(bb[2], 1880)
            self.assertGreaterEqual(bb[1], 118, 'below the top-right label')
        self.assertLessEqual(boxes[0][2], boxes[1][0], 'the today line sits left of the future block')
        for a, b in zip(boxes[1:], boxes[2:]):
            self.assertLessEqual(a[3], b[1], 'the future block stacks top to bottom without overlap')
        weights = [(b[2] - b[0]) * (b[3] - b[1]) for b in boxes]
        self.assertGreater(sum(weights[1:]), 2 * weights[0], 'the future block carries more weight than the today line')
        # the footage alignment still lands 2:282 on "Hear the recitation"
        with tempfile.TemporaryDirectory() as d:
            stages, _ = R.resolve_section(EST, EST_PLAN, s7, PAL, Path(d))
        st = next(x_ for x_ in stages if x_['kind'] == 'footage')
        self.assertAlmostEqual(st['start'] + (33.8 - st['in']), t_hear, delta=1.5 / R.FPS)
        self.assertGreaterEqual(st['in'], 0)

    def test_s6_holds_on_the_desk_clip_44_to_52_beside_the_three_lines(self):
        f = layers('s6', 'footage', EST)[0]
        self.assertEqual((f['source'], f['in'], f['out'], f['freeze_after']), ('glasses_desk', 44.0, 52.0, True))
        stats = [l for l in layers('s6', 'plate', EST) if l.get('role') == 'stat']
        self.assertEqual(len(stats), 3)
        self.assertEqual([l['lines'][0]['size'] for l in stats], [48] * 3)
        self.assertNotIn('Stale decisions are discarded', R.narration_text(EST, next(s for s in EST['sections'] if s['id'] == 's6')))
        cues = [R.phrase_time(EST, EST_PLAN['sections'][-2], next(s for s in EST['sections'] if s['id'] == 's6'), l['appear_phrase']) for l in stats]
        self.assertEqual(cues, sorted(cues), 'the lines appear in the order the voice reaches them')
        self.assertEqual(stats[0]['lines'][0]['text'], EST['script_lines_exact']['s6_line1'])
        self.assertEqual(stats[2]['lines'][0]['text'], EST['script_lines_exact']['s6_line2'])
        self.assertIn('59 tests passed, Nov 2', stats[2]['lines'][0]['text'])

    def test_s1_lens_recording_is_the_desk_clip_24_3_to_34_2(self):
        f = next(l for l in layers('s1', 'footage', EDIT) if l['id'] == 'main')
        self.assertEqual((f['source'], f['in'], f['start_s']), ('glasses_desk', 24.3, 24.8))
        self.assertAlmostEqual(f['out'] - f['in'], 4.5, places=6)


class ToggleAndPlaceholder(unittest.TestCase):
    def test_s5_exists_only_when_a_toggle_clip_is_set(self):
        # no clip: s5 dropped, s4 uses the line without the bridge, s6 follows s4 directly
        by = {s['id']: s for s in EDIT['sections']}
        self.assertNotIn('s5', by)
        self.assertTrue(by['s4']['narration']['file'].endswith('s4-fallback.mp3'))
        self.assertNotIn('gap_before_s', by['s3b']['narration'])
        self.assertNotIn('gap_before_s', by['s6']['narration'])
        self.assertFalse(EDIT['toggle_active'])
        # with a clip: s5 plays it, s4 keeps the bridged line, s6 waits out the hold
        byt = {s['id']: s for s in TOG['sections']}
        self.assertTrue(TOG['toggle_active'])
        self.assertTrue(byt['s4']['narration']['file'].endswith('narration/s4.mp3'))
        self.assertNotIn('gap_before_s', byt['s3b']['narration'])
        s5 = byt['s5']
        self.assertEqual([l['type'] for l in s5['layers']], ['paper', 'footage', 'plate', 'plate'])
        foot = s5['layers'][1]
        self.assertEqual((foot['source'], foot['in'], foot['out']), ('toggle', 66.5, 72.5))
        self.assertEqual(s5['layers'][3]['lines'][0], {'text': 'Arabic only, for memorization.', 'size': 56, 'bold': True})
        x, y, w, h = foot['dest']
        self.assertEqual((y, h), (0, 1080), 'a portrait clip is pillar-boxed full height')
        self.assertEqual(foot['crop'], [0, 0, 1206, 2622], 'never cropped')
        self.assertEqual(R.make_plan(TOG)['sections'][4]['id'], 's5')
        cap = EDIT['limits']['cap_s']
        R.check_cap(R.make_plan(EDIT), 1000.0)
        self.assertGreater(R.make_plan(TOG)['duration_s'], R.make_plan(EDIT)['duration_s'] + 6, 'a toggle clip adds s5')
        with self.assertRaises(ValueError):
            R.check_cap(R.make_plan(TOG), cap)

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


RUBRIC = {'s1': 'DEMO', 's2': 'IMPACT', 's3': 'META AI TOOLING', 's4': 'DEMO \u00b7 TECHNICAL DEPTH',
          's3b': 'META AI TOOLING \u00b7 TECHNICAL DEPTH', 's6': 'TECHNICAL DEPTH', 's7': 'IMPACT'}
NODES = [
    (1, 'Glasses microphones'), (2, 'iPhone app \u00b7 Device Access Toolkit'), (3, 'Muse Voice Transcribe \u00b7 live Arabic'),
    (4, 'Local index \u00b7 6,236 ayahs'), (5, 'Source-word tracker \u00b7 position inside the verse'),
    (6, 'Muse Spark 1.3 \u00b7 chat completions API \u00b7 strict JSON-schema output \u00b7 constrained choice or abstain \u00b7 Arabic \u2194 Pickthall pairing \u00b7 validated, then cached'),
    (7, 'Display scheduler \u00b7 newest window only'), (8, 'Lens')]
API_LINES = ['Meta Model API \u00b7 https://api.meta.ai/v1',
             'muse-voice-transcribe-1.0 \u00b7 wss://api.meta.ai/v1/asr/realtime (streaming Arabic)',
             'muse-spark-1.3 \u00b7 POST /v1/chat/completions \u00b7 response_format json_schema, strict',
             'candidates enum: verse ids + "abstain"',
             'Wearables Device Access Toolkit 1.0.1 \u00b7 MWDATCore \u00b7 MWDATDisplay']


class RubricPlates(unittest.TestCase):
    def test_every_section_opens_with_its_rubric_plate_for_2_5_s(self):
        for sid, text in RUBRIC.items():
            plates = [l for l in layers(sid, 'plate', EDIT) if l.get('role') == 'rubric']
            self.assertEqual(len(plates), 1, sid)
            pl = plates[0]
            self.assertEqual(pl['lines'], [{'text': text, 'size': 48, 'bold': True, 'color': 'blue'}], sid)
            self.assertEqual((pl['anchor'], pl['pos'][1], pl['end_s']), ('tl', 28, 2.5), sid)
            self.assertNotIn('start_s', pl)
            self.assertNotIn('appear_phrase', pl)
            self.assertLess(pl['pos'][0], 300)
        self.assertEqual(sorted(RUBRIC), sorted(s['id'] for s in EDIT['sections']))

    def test_rubric_plates_never_overlap_labels_pins_footage_or_each_other(self):
        for sid in RUBRIC:
            s = next(x for x in EDIT['sections'] if x['id'] == sid)
            rub = next(l for l in s['layers'] if l.get('role') == 'rubric')
            bb = R.paint_plate(EDIT, PAL, rub).getchannel('A').getbbox()
            self.assertIsNotNone(bb)
            self.assertLessEqual(bb[2], 1280, f'{sid}: the rubric plate reaches the top-right label corner')
            for l in s['layers']:
                if l is rub:
                    continue
                if l['type'] in ('plate', 'pin') and not times_disjoint(rub, l):
                    other = (R.paint_plate(EDIT, PAL, l) if l['type'] == 'plate' else R.paint_pin(EDIT, PAL, l)).getchannel('A').getbbox()
                    self.assertTrue(bb[2] <= other[0] or other[2] <= bb[0] or bb[3] <= other[1] or other[3] <= bb[1], f"{sid}: rubric overlaps {l.get('role') or l['type']}")
                if l['type'] == 'footage' and tuple(l['dest'][2:]) != (W, H):
                    fx, fy, fw, fh = l['dest']
                    self.assertTrue(bb[2] <= fx or bb[0] >= fx + fw or bb[3] <= fy or bb[1] >= fy + fh, f'{sid}: rubric overlaps the footage window')
        # s4: the plate sits right of the 2:282 pin
        s4 = next(x for x in EDIT['sections'] if x['id'] == 's4')
        pin = R.paint_pin(EDIT, PAL, next(l for l in s4['layers'] if l['type'] == 'pin')).getchannel('A').getbbox()
        rub = R.paint_plate(EDIT, PAL, next(l for l in s4['layers'] if l.get('role') == 'rubric')).getchannel('A').getbbox()
        self.assertGreaterEqual(rub[0], pin[2])


class Diagram(unittest.TestCase):
    def setUp(self):
        self.s3b = next(s for s in EDIT['sections'] if s['id'] == 's3b')
        self.diagram = next(l for l in self.s3b['layers'] if l['type'] == 'diagram')

    def test_eight_nodes_with_the_exact_texts_in_two_rows(self):
        nodes = self.diagram['nodes']
        self.assertEqual(len(nodes), 8)
        self.assertEqual([(n['n'], ' \u00b7 '.join(R.node_parts(n))) for n in nodes], NODES)
        self.assertEqual([n['row'] for n in nodes], [0, 0, 0, 0, 1, 1, 1, 1])
        tags = {n['n']: (n['tag']['text'], n['tag']['color']) for n in nodes if n.get('tag')}
        self.assertEqual(tags, {3: ('LIVE', 'blue'), 5: ('LIVE', 'blue'), 6: ('PREPARED IN ADVANCE', 'red')})
        n6 = nodes[5]
        self.assertEqual(n6['title'], 'Muse Spark 1.3 \u00b7 chat completions API')
        self.assertEqual(n6['subs'], ['strict JSON-schema output \u00b7 constrained choice or abstain', 'Arabic \u2194 Pickthall pairing \u00b7 validated, then cached'])
        self.assertEqual((n6['tag']['text'], n6['tag']['color']), ('PREPARED IN ADVANCE', 'red'), 'the tag stays')
        self.assertEqual(n6['late']['items'], ['sub:1', 'tag'], 'the pairing line and the tag arrive on the pairing sentence')
        self.assertEqual(n6['cue'], 'Muse Spark 1.3')
        self.assertIn(n6['late']['cue'], R.narration_text(EDIT, self.s3b))
        laid, row_y, row_h, g = R.diagram_layout(EDIT, self.diagram)
        lay6 = laid[5]
        self.assertEqual(lay6['title_lines'], ['Muse Spark 1.3', 'chat completions API'], 'the title breaks at its separator, which is dropped')
        self.assertEqual(lay6['sub_lines'], [['strict JSON-schema output', 'constrained choice or abstain'], ['Arabic \u2194 Pickthall pairing', 'validated, then cached']])
        for ln in lay6['title_lines'] + [x for subl in lay6['sub_lines'] for x in subl]:
            self.assertFalse(ln.startswith('\u00b7') or ln.endswith('\u00b7'), f'dangling separator on {ln!r}')
        self.assertEqual(len(lay6['title_lines']), 2)
        for sub, wrapped in zip(n6['subs'], lay6['sub_lines']):
            self.assertEqual(' '.join(wrapped).split(), sub.replace(' \u00b7 ', ' ').split(), 'every word survives; only the separator is dropped at a break')
        self.assertGreaterEqual(self.diagram['sub_px'], 40)
        self.assertGreaterEqual(self.diagram['tag_px'], 40)
        self.assertLessEqual(lay6['y'] + lay6['h'], H - EDIT['bottom_margin_px'])
        af = self.diagram['audio_flow']
        self.assertEqual((af['from'], af['to'], af['label']), (1, 3, 'audio goes to Muse Voice'))

    def test_all_diagram_text_is_at_least_40_px_and_node_titles_48(self):
        self.assertEqual(self.diagram['title_px'], 48)
        for k in ('sub_px', 'tag_px'):
            self.assertGreaterEqual(self.diagram[k], 40)
        self.assertGreaterEqual(self.diagram['audio_flow']['label_px'], 40)
        nodes, row_y, row_h, g = R.diagram_layout(EDIT, self.diagram)
        self.assertEqual(len(nodes), 8)
        self.assertEqual((g['title_px'], g['sub_px'], g['tag_px']), (48, 40, 40))
        # every wrapped line fits inside its node (layout raises otherwise)
        for n in nodes:
            for ln in n['title_lines']:
                self.assertLessEqual(R.text_width(EDIT['fonts']['latin_bold'], 48, ln), n['w'] - 2 * g['pad'] + 1)

    def test_diagram_stays_inside_the_safe_area(self):
        nodes, row_y, row_h, g = R.diagram_layout(EDIT, self.diagram)
        for n in nodes:
            self.assertGreaterEqual(n['x'], 60)
            self.assertLessEqual(n['x'] + n['w'], W - 60)
            self.assertGreaterEqual(n['y'], 130)
            self.assertLessEqual(n['y'] + n['h'], H - EDIT['bottom_margin_px'])
        items = R.paint_diagram(EDIT, PAL, self.diagram)
        self.assertEqual(len([i for i in items if i['node']]), 9, '8 nodes plus the late items of node 6')
        for it in items:
            bb = it['img'].getchannel('A').getbbox()
            self.assertGreaterEqual(bb[0], 40)
            self.assertLessEqual(bb[2], W - 40)
            self.assertGreaterEqual(bb[1], 100)
            self.assertLessEqual(bb[3], H - EDIT['bottom_margin_px'], it['name'])

    def test_nodes_build_in_time_with_the_narration_cues(self):
        ps = next(p for p in PLAN['sections'] if p['id'] == 's3b')
        text = R.narration_text(EDIT, self.s3b)
        for n in self.diagram['nodes']:
            self.assertIn(n['cue'], text)
        times = [R.phrase_time(EDIT, ps, self.s3b, n['cue']) + n.get('cue_offset_s', 0.0) for n in self.diagram['nodes']]
        self.assertEqual(times, sorted(times))
        self.assertEqual(len(set(round(x, 2) for x in times)), 8)
        audio = R.phrase_time(EDIT, ps, self.s3b, self.diagram['audio_flow']['cue'])
        self.assertLess(audio, times[2] + 0.01, 'the audio line is drawn no later than node 3')
        self.assertGreater(audio, times[0])


class ApiCard(unittest.TestCase):
    def setUp(self):
        self.s3b = next(s for s in EDIT['sections'] if s['id'] == 's3b')
        self.card = next(l for l in self.s3b['layers'] if l['type'] == 'api_card')

    def test_the_five_api_lines_are_exact_44_px_with_identifiers_in_monospace(self):
        plain = [R.plain_from_markup(x) for x in self.card['lines']]
        self.assertEqual(plain, API_LINES)
        self.assertEqual(self.card['line_px'], 44)
        self.assertEqual(self.card['title'], 'API references, from the source')
        mono = {t for raw in self.card['lines'] for t, m, _ in R.parse_markup(raw) if m}
        for ident in ('https://api.meta.ai/v1', 'muse-voice-transcribe-1.0', 'wss://api.meta.ai/v1/asr/realtime', 'muse-spark-1.3',
                      'POST /v1/chat/completions', 'MWDATCore', 'MWDATDisplay', '"abstain"'):
            self.assertIn(ident, mono)
        rows, src_lines, wrapped = R.api_card_layout(EDIT, self.card)
        # identifiers are never split across lines
        for toks, widths, lines in rows:
            placed = sorted(i for ln in lines for i in ln)
            self.assertEqual(placed, list(range(len(toks))))

    def test_code_excerpt_is_verbatim_from_museSpark_swift_and_never_truncated(self):
        code = self.card['code']
        self.assertEqual((code['label'], code['px'], code['lines']), ('MuseSpark.swift', 40, [24, 25]))
        src = (R.ROOT / code['source']).read_text().split('\n')
        want = [src[n - 1].strip() for n in code['lines']]
        self.assertIn('"model": "muse-spark-1.3"', want[0])
        self.assertIn('"response_format": ["type": "json_schema"', want[1])
        self.assertIn('"strict": true', want[1])
        rows, src_lines, wrapped = R.api_card_layout(EDIT, self.card)
        self.assertEqual(src_lines, want)
        self.assertNotIn('"enum": ids + ["abstain"]', ' '.join(wrapped), 'line 19 is dropped; the card keeps its own candidates line')
        self.assertIn('candidates enum: verse ids + "abstain"', [R.plain_from_markup(x) for x in self.card['lines']])
        self.assertEqual(' '.join(wrapped).split(' '), ' '.join(want).split(' '), 'wrapping at spaces only: every token survives')
        self.assertLessEqual(len(wrapped), 12, 'two source lines wrap to about eleven visual lines (three lines took sixteen)')
        mono = EDIT['fonts']['mono']
        for ln in wrapped:
            self.assertLessEqual(R.text_width(mono, 40, ln), self.card['right'][2] - 52 + 1)

    def test_card_arrives_one_second_before_the_voice_ends_and_stays_three_and_a_half_after_a_two_second_diagram_hold(self):
        img = R.paint_api_card(EDIT, PAL, self.card)
        self.assertEqual(img.size, (W, H))
        ps = next(p for p in PLAN['sections'] if p['id'] == 's3b')
        diagram = next(l for l in self.s3b['layers'] if l['type'] == 'diagram')
        slide = ps['narr_end'] - ps['start_s'] - diagram['slide']['before_narration_end_s']
        start = ps['narr_end'] - ps['start_s'] - self.card['appear_before_narration_end_s']
        self.assertEqual((diagram['slide']['before_narration_end_s'], self.card['appear_before_narration_end_s']), (1.0, 1.0))
        self.assertAlmostEqual(start, slide, places=6, msg='the diagram leaves exactly as the card arrives')
        self.assertEqual(diagram['slide']['duration_s'], self.card['slide_in_s'])
        self.assertAlmostEqual(ps['duration_s'] - start, 3.5, delta=1 / R.FPS + 0.01, msg='card on screen 3.5 s from the start of the slide until its fade out begins')
        self.assertAlmostEqual(ps['end_s'] - ps['narr_end'], 2.5, delta=1 / R.FPS)
        n8 = diagram['nodes'][-1]
        t8 = R.phrase_time(EDIT, ps, self.s3b, n8['cue']) + n8.get('cue_offset_s', 0.0)
        self.assertLessEqual(t8 + 2.0, start, 'the finished diagram holds at least 2.0 s before the card pushes in')
        n7 = diagram['nodes'][-2]
        t7 = R.phrase_time(EDIT, ps, self.s3b, n7['cue']) + n7.get('cue_offset_s', 0.0)
        self.assertAlmostEqual(t8 - t7, 1.0, places=6, msg='nodes 7 and 8 are 1.0 s apart')
        self.assertIn('min(1,max(0,(t-', R.motion_y({'kind': 'out_up', 't0': 1.0, 'd': 1.0}, H))
        self.assertTrue(R.motion_y({'kind': 'in_up', 't0': 1.0, 'd': 1.0}, H).startswith(f'{H}*(1-'))



class OrderAndNarration(unittest.TestCase):
    def test_section_order_and_narration_files(self):
        self.assertEqual([s['id'] for s in EDIT['sections']], ['s1', 's2', 's3', 's4', 's3b', 's6', 's7'])
        files = {s['id']: Path(s['narration']['file']).name for s in EDIT['sections'] if s['narration'].get('file')}
        self.assertEqual(files, {'s2': 's2.mp3', 's3': 's3-v12.mp3', 's4': 's4-fallback.mp3', 's3b': 's3b-v12.mp3',
                                 's6': 's6-v12.mp3', 's7': 's7-v13.mp3'})
        for sid, name in files.items():
            self.assertTrue((R.ROOT / 'build/video-v1.0/narration' / name).exists(), name)
            self.assertGreater(len(R.narration_text(EDIT, next(s for s in EDIT['sections'] if s['id'] == sid))), 40)
        by = {p['id']: p for p in PLAN['sections']}
        for sid, prev in (('s2', 's1'), ('s3', 's2'), ('s4', 's3'), ('s3b', 's4'), ('s6', 's3b'), ('s7', 's6')):
            self.assertAlmostEqual(by[sid]['narr_start'] - by[prev]['end_s'], 0.5, places=9, msg=f'{sid} starts when the fade off {prev} ends')
        # s3 ends on 'that is the easy part'; s4 (without the bridge) ends 'moves with it'
        self.assertTrue(R.narration_text(EDIT, next(s for s in EDIT['sections'] if s['id'] == 's3')).rstrip().endswith('And that is the easy part.'))
        self.assertTrue(R.narration_text(EDIT, next(s for s in EDIT['sections'] if s['id'] == 's4')).rstrip().endswith('and the meaning moves with it.'))
        for sid in ('s2', 's3', 's4', 's6'):
            self.assertAlmostEqual(by[sid]['end_s'], by[sid]['speech_end'], delta=1 / R.FPS)

    def test_s7_close_card_and_tail(self):
        s7 = next(s for s in EDIT['sections'] if s['id'] == 's7')
        self.assertEqual(s7['narration']['cut_offset_s'], -1.0, 'the close holds 1.0 s past the voice (was 2.0 s in v1.1)')
        ps = next(p for p in PLAN['sections'] if p['id'] == 's7')
        self.assertAlmostEqual(ps['end_s'] - ps['narr_end'], 1.0, delta=1 / R.FPS)
        card = next(l for l in s7['layers'] if l['type'] == 'card')
        self.assertEqual(' \u00b7 '.join(l['text'] for l in card['lines']), EDIT['script_lines_exact']['s7_card'])
        self.assertEqual(EDIT['audio']['final_fade_s'] + EDIT['audio']['final_quiet_s'], 1.0)


class Fallback(unittest.TestCase):
    def test_fallback_uses_the_fallback_narration_and_pictures(self):
        by = {s['id']: s for s in FB['sections']}
        self.assertNotIn('file', by['s1']['narration'], 'fallback s1 is the same on-camera opening: no Callum s1')
        self.assertTrue(by['s4']['narration']['file'].endswith('s4-fallback.mp3'))
        self.assertTrue(by['s6']['narration']['file'].endswith('s6-v12.mp3'))
        self.assertFalse(RAW['fallback']['enabled'])
        # with the old fallback pictures removed, fallback mode is the default without a toggle clip
        self.assertEqual(FB['sections'], EDIT['sections'])

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
    @unittest.skipUnless(FB_READY, 'fallback narration files not generated yet')
    def test_fallback_plan_is_valid(self):
        plan = R.make_plan(FB)
        self.assertEqual(plan['duration_s'], PLAN['duration_s'])
        self.assertEqual(plan['audio_samples'], plan['total_frames'] * 1600)

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
        self.assertEqual(stems, {'s2': 's2', 's3': 's3-v12', 's4': 's4-fallback', 's3b': 's3b-v12', 's6': 's6-v12', 's7': 's7-v13'})
        for sid, stem in stems.items():
            self.assertEqual(by[sid]['narration']['file'], f"build/video-v1.0/narration/own/{stem}.wav")
            self.assertTrue(by[sid]['narration']['callum_file'].endswith('.mp3'))
        own_t = R.apply_narration_source(TOG, 'own')
        self.assertEqual([Path(s['narration']['file']).stem for s in own_t['sections'] if s['narration'].get('file')],
                         ['s2', 's3-v12', 's4', 's5', 's3b-v12', 's6-v12', 's7-v13'])
        for a, b in zip(EDIT['sections'], own['sections']):
            for k in ('cut_offset_s', 'gap_before_s', 'end_at'):
                self.assertEqual(a['narration'].get(k), b['narration'].get(k))

    def test_own_source_in_fallback_mode_uses_the_fallback_takes(self):
        own_fb = R.apply_narration_source(FB, 'own')
        by = {s['id']: s['narration'].get('file') for s in own_fb['sections']}
        self.assertEqual(list(by), ['s1', 's2', 's3', 's4', 's3b', 's6', 's7'])
        self.assertIsNone(by['s1'])
        self.assertEqual(by['s4'], 'build/video-v1.0/narration/own/s4-fallback.wav')
        self.assertEqual(by['s6'], 'build/video-v1.0/narration/own/s6-v12.wav')

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
