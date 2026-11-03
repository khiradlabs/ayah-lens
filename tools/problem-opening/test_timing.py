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

    def test_problem_precedes_scale_then_phone_then_same_source_replay(self):
        self.assertEqual([self.m.scene_at(f) for f in (0,239,240,513,514,657,658,741,742,839,840,1079)],
                         ['listen','listen','problem','problem','scale','scale','phone','phone','bridge','bridge','replay','replay'])
        with self.assertRaises(ValueError): self.m.scene_at(1080)

    def test_measured_narration_cannot_overlap_the_next_sentence(self):
        self.assertTrue(callable(getattr(self.m,'narration_windows',None)), 'measured narration guard is missing')
        self.m.narration_windows(self.m.TIMELINE['narration_durations'])
        with self.assertRaisesRegex(ValueError,'overlap'):
            self.m.narration_windows([4.634558,4.437778,4.797143,3.566032,2.904354])

    def test_replay_uses_exact_first_eight_seconds_and_accepted_audio(self):
        self.assertEqual([self.m.source_frame(f) for f in (0,239,240,839,840,1079)], [0,239,None,None,0,239])
        self.assertEqual(self.m.audio_sources(), ['build/video-v0.2.1/audio/00.wav','build/video-v0.2.1/audio/02.wav'])
        self.assertEqual(self.m.NARRATION, 'Imagine hearing the Quran every day, without understanding its meaning. For many Muslims who don’t understand Arabic, that is familiar. About two billion people are Muslim, roughly one quarter of humanity. Reading a translation pulls your eyes down to your phone. Now listen again, with the meaning in view.')


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
