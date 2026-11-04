#!/usr/bin/env python3
import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ContinuityTests(unittest.TestCase):
 def setUp(self):
  p=ROOT/'tools/render_continuity_proof.py'
  self.assertTrue(p.exists(),'Continuous-stage proof renderer is missing')
  spec=importlib.util.spec_from_file_location('proof',p);self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
 def test_question_line_breaks_never_reflow_during_motion(self):
  m=self.m
  self.assertTrue(hasattr(m,"question_lines"),"Question has no stable line-break contract")
  lines=[m.question_lines(t) for t in [0,2.8,3.1,3.5,3.9,25]]
  self.assertTrue(all(x==lines[0] for x in lines))
  self.assertEqual(len(lines[0]),2)
  self.assertEqual(" ".join(lines[0]),"What if your glasses became your personal Quran translator?")
 def test_side_group_is_gone_before_source_window_expands(self):
  m=self.m
  self.assertTrue(hasattr(m,"side_opacity"),"Right-side group has no shared exit before card expansion")
  self.assertEqual(m.side_opacity(m.REPLAY_START-.8),0)
  self.assertEqual(m.side_opacity(m.REPLAY_START),0)
  self.assertEqual(m.side_opacity(m.PRODUCT_START),0)
 def test_source_pair_is_actual_matching_published_112_1(self):
  row=next(r for r in json.loads((ROOT/'App/Resources/verses.json').read_text()) if r['id']=='112:1')
  self.assertIn(self.m.ARABIC,row['arabic']);self.assertEqual(self.m.ENGLISH,row['translation'])
 def test_persistent_window_has_no_jump_or_missing_frame(self):
  m=self.m
  for boundary in [m.REPLAY_START-.8,m.REPLAY_START,m.PRODUCT_START,m.PRODUCT_START+1.2]:
   a=m.window_rect(boundary-.001);b=m.window_rect(boundary+.001)
   self.assertLess(max(abs(x-y) for x,y in zip(a,b)),3)
  self.assertTrue(all(m.window_rect(t)[2]>900 for t in [0,3,7,13,m.REPLAY_START,25,32]))
 def test_real_meaning_is_visible_when_promised_and_stays(self):
  m=self.m
  self.assertEqual(m.meaning_opacity(m.MEANING_START),1)
  for t in [m.MEANING_START,7,10,12,13]:self.assertEqual(m.meaning_opacity(t),1)
 def test_native_replay_uses_all_original_frames_then_holds_last(self):
  m=self.m
  self.assertEqual([m.native_index(m.REPLAY_START+i/30) for i in range(306)],list(range(306)))
  self.assertEqual(m.native_index(m.PRODUCT_START+5),305)
 def test_captions_are_separate_from_meaning_and_stop_during_recitation(self):
  m=self.m
  self.assertTrue(m.caption_at(m.MEANING_START))
  self.assertEqual(m.caption_at(m.REPLAY_START+3),'')
  self.assertTrue(m.caption_at(m.PRODUCT_START+3))
  self.assertGreater(m.CAPTION_Y,max(m.window_rect(t)[1]+m.window_rect(t)[3] for t in [0,14,18,25]))
 def test_duration_preserves_complete_audio_at_one_x(self):
  m=self.m
  self.assertAlmostEqual(m.REPLAY_START,36.85-m.VOICE_START+.15)
  self.assertAlmostEqual(m.PRODUCT_START-m.REPLAY_START,10.2)
  self.assertGreaterEqual(m.DURATION,m.PRODUCT_START+10.8)
if __name__=='__main__':unittest.main()
