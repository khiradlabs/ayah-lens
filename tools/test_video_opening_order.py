#!/usr/bin/env python3
"""Check the approved listen → scale → meaning order and its semantic content."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import ImageChops
import editorial_motion as motion
import render_demo_video as video


def reordered_plan():
    plan = copy.deepcopy(video.PLAN)
    by_capture = {s['capture']: s for s in plan['segments']}
    opening = [('opening_recitation', 0, 8, 0), ('founder_intro', 8, 28, 2), ('opening_reveal', 28, 36, 1)]
    for position, (capture, start, end, identity) in enumerate(opening):
        segment = copy.deepcopy(by_capture[capture])
        segment.update(start=start, end=end, visual_scene=identity)
        plan['segments'][position] = segment
    return plan


class OpeningOrderTests(unittest.TestCase):
    def test_maintained_opening_order_and_boundaries(self):
        expected = [('opening_recitation', 0, 8), ('founder_intro', 8, 28), ('opening_reveal', 28, 36)]
        actual = [(s['capture'], s['start'], s['end']) for s in video.PLAN['segments'][:3]]
        self.assertEqual(actual, expected, 'Opening must play listen, scale, then meaning')
        self.assertEqual([(s['start'], s['end']) for s in video.PLAN['segments'][3:]],
                         [(36,48),(48,60),(60,90),(90,112),(112,138),(138,152),(152,168),(168,180)])

    def test_visual_content_follows_scene_identity(self):
        plan = reordered_plan()
        for position, identity in [(1, 2), (2, 1)]:
            original = copy.deepcopy(plan)
            original['segments'][position]['visual_scene'] = position
            original['segments'][identity] = copy.deepcopy(plan['segments'][position])
            original['segments'][identity]['visual_scene'] = identity
            before = motion.keyframe(identity, 5, original).crop((90, 125, 1830, 990))
            after = motion.keyframe(position, 5, plan).crop((90, 125, 1830, 990))
            self.assertIsNone(ImageChops.difference(before, after).getbbox(), f'Content changed for semantic scene {identity}')

    def test_sources_follow_identity_and_not_position(self):
        with patch.object(video, 'PLAN', reordered_plan()):
            self.assertEqual(video.sources(1), [], 'Population must have no native display overlays')
            overlays = video.sources(2)
            self.assertEqual(len(overlays), 2, 'Meaning reveal needs both native and enlarged views')
            self.assertEqual(overlays[1][1], video.PLAN['source_assets']['native_display_crop'])

    def test_reused_audio_keeps_existing_tail_padding_and_identity(self):
        plan = reordered_plan()
        copied = []
        durations = {motion.scene_id(i, plan): s['end'] - s['start'] for i, s in enumerate(plan['segments'])}
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(video, 'PLAN', plan), patch.object(video, 'OUT', Path(folder)), \
                 patch.object(video, 'probe', side_effect=lambda p: {'format': {'duration': str(durations[int(p.stem)] - .5)}}), \
                 patch.object(video.shutil, 'copy2', side_effect=lambda source, target: copied.append((source.name, target.name))):
                video.guide_audio(Path(folder) / 'approved')
        self.assertEqual(copied[:3], [('00.wav', '00.wav'), ('02.wav', '01.wav'), ('01.wav', '02.wav')])

    def test_reveal_uses_source_recitation_after_move(self):
        calls = []
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(video, 'PLAN', reordered_plan()), patch.object(video, 'OUT', Path(folder)), \
                 patch.object(video, 'run', side_effect=lambda args, **kw: calls.append([str(a) for a in args])), \
                 patch.object(video, 'probe', return_value={'format': {'duration': '10'}}):
                video.guide_audio()
        reveal = next(c for c in calls if c[-1].endswith('/02.wav'))
        self.assertIn(str(video.ROOT / video.PLAN['source_assets']['native']), reveal,
                      'Moved meaning reveal must retain source recitation, not silent audio')
        self.assertNotIn('anullsrc=r=48000:cl=stereo', reveal)


if __name__ == '__main__':
    unittest.main(verbosity=2)
