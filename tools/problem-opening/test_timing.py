"""Behavior checks for the standalone proof's editorial/source selection."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).with_name('timing.py')

class OpeningTimingTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MODULE.exists(), 'opening timing/source selection has not been implemented')
        spec = importlib.util.spec_from_file_location('opening_timing', MODULE)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)

    def test_problem_precedes_scale_then_approved_hook_benefits_and_same_source_replay(self):
        self.assertEqual([self.m.scene_at(f) for f in (0,239,240,359,360,464,465,573,574,899,900,1139)],
                         ['listen','listen','problem','problem','scale','scale','hook','hook','benefits','benefits','replay','replay'])
        with self.assertRaises(ValueError): self.m.scene_at(1140)

    def test_measured_narration_cannot_overlap_the_next_sentence(self):
        self.assertTrue(callable(getattr(self.m,'narration_windows',None)), 'measured narration guard is missing')
        self.m.narration_windows(self.m.TIMELINE['narration_durations'])
        with self.assertRaisesRegex(ValueError,'overlap'):
            self.m.narration_windows([8]+self.m.TIMELINE['narration_durations'][1:])

    def test_replay_uses_exact_first_eight_seconds_and_accepted_audio(self):
        self.assertEqual([self.m.source_frame(f) for f in (0,239,240,899,900,1139)], [0,239,None,None,0,239])
        self.assertEqual(self.m.audio_sources(), ['build/video-v0.2.1/audio/00.wav','build/video-v0.2.1/audio/02.wav'])
        approved_hook = 'What if your glasses became your personal Quran translator? The meaning, right in front of your eyes. The text follows the recitation automatically. No scrolling. No tapping. Just listen. And understand.'
        self.assertTrue(self.m.NARRATION.endswith(approved_hook), 'approved hook must remain verbatim')


    def test_narration_rejects_missing_or_extra_duration_instead_of_silent_zip_truncation(self):
        for durations in ([1], [1]*10):
            with self.assertRaisesRegex(ValueError,'count'):
                self.m.narration_windows(durations)

    def test_nine_spoken_beats_have_complete_nonoverlapping_windows(self):
        import re
        sentences=re.split(r'(?<=[.?])\s+',self.m.NARRATION)
        self.assertEqual(len(sentences),9)
        windows=self.m.narration_windows(self.m.TIMELINE['narration_durations'])
        self.assertEqual(len(windows),len(sentences))
        self.assertLess(windows[-1][1],30)

class VoiceCacheTests(unittest.TestCase):
    def test_changed_sentence_regenerates_positive_duration_audio(self):
        import tempfile
        module=Path(__file__).with_name('voice_cache.py')
        self.assertTrue(module.exists(), 'sentence-aware voice cache has not been implemented')
        spec=importlib.util.spec_from_file_location('voice_cache',module)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory() as folder:
            audio=Path(folder)/'voice.aiff';calls=[]
            def generate(p,text,voice,rate): calls.append(text);p.write_text(text)
            measure=lambda p: 1 if p.read_text() else 0
            self.assertTrue(m.ensure_voice(audio,'Old sentence.','Daniel',150,generate,measure))
            self.assertFalse(m.ensure_voice(audio,'Old sentence.','Daniel',150,generate,measure))
            self.assertTrue(m.ensure_voice(audio,'New sentence.','Daniel',150,generate,measure))
            self.assertEqual(calls,['Old sentence.','New sentence.'])
            self.assertEqual(audio.read_text(),'New sentence.')

if __name__ == '__main__': unittest.main()
