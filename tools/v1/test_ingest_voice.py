#!/usr/bin/env python3
"""Tests for tools/v1/ingest_voice.py. Synthetic audio plus the Callum MP3s as stand-ins; nothing is rendered and
nothing is written outside temporary folders.

  /Users/farazsyed/data/khirad/apps/ayah-lens-prep/venv-data/bin/python tools/v1/test_ingest_voice.py
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ingest_voice as I  # noqa: E402
import render_v1 as R  # noqa: E402

CALLUM = R.ROOT / 'build/video-v1.0/narration'
SR = 48000


def speech_like(seconds, seed=3):
    """Voiced-sounding test signal: three harmonics with a syllable-rate envelope plus a little noise."""
    t = np.arange(int(seconds * SR)) / SR
    env = 0.55 + 0.45 * np.sin(2 * np.pi * 3.0 * t)
    x = (np.sin(2 * np.pi * 140 * t) + 0.6 * np.sin(2 * np.pi * 280 * t) + 0.3 * np.sin(2 * np.pi * 560 * t)) * env
    x = 0.25 * x / np.abs(x).max()
    return x + np.random.default_rng(seed).normal(0, 0.0004, size=len(t))


def write_wav(path, x, rate=SR):
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())


def padded(speech_s=6.0, pad_s=2.0, dc=0.0):
    sil = np.zeros(int(pad_s * SR))
    return np.concatenate([sil, speech_like(speech_s), sil]) + dc


def read_out(path):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'])
    return np.frombuffer(raw, dtype='<f4').astype(np.float64)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class FakeCallum:
    """A temporary Callum folder whose s1 paragraph is 7.0 s long."""

    def __enter__(self):
        self.d = tempfile.TemporaryDirectory()
        write_wav(Path(self.d.name) / 's1.wav', np.zeros(int(7.0 * SR)) + 0.001)
        return Path(self.d.name)

    def __exit__(self, *a):
        self.d.cleanup()


class Ingest(unittest.TestCase):
    def test_two_seconds_of_silence_at_both_ends_becomes_0_3_s_pads(self):
        with tempfile.TemporaryDirectory() as d, FakeCallum() as cal:
            src, out = Path(d) / 's1.wav', Path(d) / 'own'
            write_wav(src, padded())
            rec = I.ingest_file('s1', src, out, cal)
            y = read_out(out / 's1.wav')
            self.assertAlmostEqual(len(y) / SR, 6.0 + 0.6, delta=0.12)
            loud = np.where(np.abs(y) > 0.003)[0]
            self.assertAlmostEqual(loud[0] / SR, 0.3, delta=0.04)
            self.assertAlmostEqual((len(y) - loud[-1]) / SR, 0.3, delta=0.04)
            self.assertEqual((rec['lead_s'], rec['trail_s']), (0.3, 0.3))
            self.assertEqual(rec['samples'], len(y))

    def test_loudness_is_within_1_lu_of_minus_20_and_peak_at_or_below_minus_3(self):
        with tempfile.TemporaryDirectory() as d, FakeCallum() as cal:
            src, out = Path(d) / 's1.wav', Path(d) / 'own'
            write_wav(src, padded() * 0.4)  # a quiet take, as Voice Memos tends to give
            rec = I.ingest_file('s1', src, out, cal)
            lufs, peak = R.measure_wav(out / 's1.wav')
            self.assertAlmostEqual(lufs, -20.0, delta=1.0)
            self.assertLessEqual(peak, -2.9)
            self.assertAlmostEqual(rec['integrated_lufs'], lufs, delta=0.05)
            self.assertEqual(rec['status'], 'ok')

    def test_dc_offset_is_removed(self):
        with tempfile.TemporaryDirectory() as d, FakeCallum() as cal:
            src, out = Path(d) / 's1.wav', Path(d) / 'own'
            write_wav(src, padded(dc=0.05))
            rec = I.ingest_file('s1', src, out, cal)
            self.assertAlmostEqual(rec['dc_offset_removed'], 0.05, delta=0.01)
            y = read_out(out / 's1.wav')
            self.assertLess(abs(y.mean()), 0.002)
            self.assertLess(abs(y[:int(0.25 * SR)]).max(), 0.01, 'the lead pad must be quiet, not a 0.05 offset')

    def test_duration_guard_refuses_a_too_short_file_by_name_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d, FakeCallum() as cal:
            src, out = Path(d) / 's1.wav', Path(d) / 'own'
            write_wav(src, padded(speech_s=2.0))  # 2.6 s against a 7.0 s paragraph
            with self.assertRaises(I.Refused) as cm:
                I.ingest_file('s1', src, out, cal)
            msg = str(cm.exception)
            self.assertIn('REFUSED s1', msg)
            self.assertIn('s1.wav', msg)
            self.assertIn('Callum', msg)
            self.assertFalse((out / 's1.wav').exists())

    def test_duration_guard_limits_are_plus_minus_40_percent(self):
        for ratio, ok in ((1.39, True), (1.41, False), (0.61, True), (0.59, False), (1.0, True)):
            if ok:
                I.check_duration('s2', 'x.m4a', 10 * ratio, 10.0)
            else:
                with self.assertRaises(I.Refused):
                    I.check_duration('s2', 'x.m4a', 10 * ratio, 10.0)
        real = R.narration_info(str(CALLUM / 's1.mp3'))['duration']
        with self.assertRaises(I.Refused) as cm:
            I.check_duration('s1', 'voice.m4a', real * 0.4, real)
        self.assertIn('s1', str(cm.exception))

    def test_silent_file_is_refused(self):
        with tempfile.TemporaryDirectory() as d, FakeCallum() as cal:
            src = Path(d) / 's1.wav'
            write_wav(src, np.zeros(SR * 3))
            with self.assertRaises(I.Refused):
                I.ingest_file('s1', src, Path(d) / 'own', cal)


class Folder(unittest.TestCase):
    def test_find_sources_accepts_common_formats_and_picks_the_newest(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            for name in ('s1.m4a', 'S2 (1).mp3', 's2 2.wav', 's4-fallback.caf', 's1-fallback.m4a', 's2-fallback.m4a', 's3.txt', 'holiday.m4a', 's9.m4a'):
                (d / name).write_bytes(b'x')
            import os
            os.utime(d / 's2 2.wav', (10 ** 9 + 100, 10 ** 9 + 100))
            os.utime(d / 'S2 (1).mp3', (10 ** 9, 10 ** 9))
            got, warns = I.find_sources(d)
            self.assertEqual(sorted(got), ['s1', 's1-fallback', 's2', 's4-fallback'])
            self.assertEqual(got['s2'].name, 's2 2.wav')
            self.assertTrue(any('s2' in w and 'newest' in w for w in warns))
            self.assertTrue(any('s2-fallback' in w or 'only s1 and s4' in w for w in warns))

    def test_callum_mp3s_as_stand_ins_ingest_cleanly_and_are_never_touched(self):
        before = {p.name: sha(p) for p in CALLUM.glob('*.mp3')}
        self.assertGreaterEqual(len(before), 9)
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / 'in', Path(d) / 'own'
            src.mkdir()
            names = [f's{i}' for i in range(1, 8)] + ['s1-fallback', 's4-fallback', 's3-short', 's3b-architecture', 's6-deep', 's3-v12', 's3b-v12', 's6-v12', 's7-v12']
            for n in names:
                shutil.copy(CALLUM / f'{n}.mp3', src / f'{n}.mp3')
            m = I.ingest_folder(src, out, CALLUM, log=lambda *_: None)
            self.assertEqual(sorted(f['id'] for f in m['files']), sorted(names))
            self.assertEqual((m['refused'], m['missing_required']), ([], []))
            self.assertEqual(sorted(m['extra_ingested']), sorted(['s1', 's3', 's4', 's5', 's6', 's7', 's1-fallback', 's3-short', 's3b-architecture', 's6-deep']),
                             'the old s3 and s6, the bridged s4, s5, s1 and s1-fallback are ingested but unused in the default film')
            for f in m['files']:
                self.assertEqual(f['status'], 'ok', f)
                self.assertAlmostEqual(f['integrated_lufs'], -20.0, delta=1.0)
                self.assertLessEqual(f['peak_dbfs'], -2.9)
                self.assertLess(abs(f['ratio_to_callum'] - 1), 0.1)
                self.assertTrue(Path(f['output']).exists())
            self.assertTrue((out / 'manifest.json').exists())
            for name in ('paragraphs.json', 'fallback-paragraphs.json'):  # the cue texts live one folder above own/
                shutil.copy(CALLUM / name, Path(d) / name)
            # the render plan accepts the own files: swap them in through narration.source and compare durations
            edit = R.apply_narration_source(R.load_edit(fallback=False, voice='callum'), 'own')
            for s in edit['sections']:
                if s['narration'].get('file'):
                    s['narration']['file'] = str(out / (Path(s['narration']['file']).stem + '.wav'))
            plan, base = R.make_plan(edit), R.make_plan(R.load_edit(voice='callum'))
            # the over-cap question belongs to test_render_v1 (the cap test); here the own files only have to track the Callum timing
            self.assertLess(abs(plan['duration_s'] - base['duration_s']), 3.0)
        after = {p.name: sha(p) for p in CALLUM.glob('*.mp3')}
        self.assertEqual(before, after, 'Callum files must never change')

    def test_output_folder_may_not_be_the_callum_folder(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):
                I.ingest_folder(d, CALLUM, CALLUM, log=lambda *_: None)

    def test_missing_required_files_are_reported(self):
        with tempfile.TemporaryDirectory() as d, FakeCallum() as cal:
            src, out = Path(d) / 'in', Path(d) / 'own'
            src.mkdir()
            write_wav(src / 's1.wav', padded())
            m = I.ingest_folder(src, out, cal, log=lambda *_: None)
            self.assertEqual(m['required_ids'], ['s2', 's3-v12', 's4-fallback', 's3b-v12', 's6-v12', 's7-v12'])
            self.assertEqual(m['missing_required'], ['s2', 's3-v12', 's4-fallback', 's3b-v12', 's6-v12', 's7-v12'])
            self.assertEqual([f['id'] for f in m['files']], ['s1'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
