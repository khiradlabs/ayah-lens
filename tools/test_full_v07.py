#!/usr/bin/env python3
"""Behavioral guards for the complete v0.7 edit; offline and synthetic inputs."""
import importlib.util, unittest
from pathlib import Path
P=Path(__file__).with_name('render_full_v07.py')
class FullCut(unittest.TestCase):
 def load(self):
  self.assertTrue(P.exists(),'Complete-cut renderer is missing')
  s=importlib.util.spec_from_file_location('full',P); m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 def test_measured_timing_respects_fixed_proof_and_under_three_minutes(self):
  m=self.load(); ds=dict(hook=13.65,human_context=17,long_verse_cue=6.3,following=9,mechanism=19,choice_and_use=13,foundation=16,close=9)
  t=m.make_timeline(ds)
  self.assertEqual(t['masjid_reservation'],[60,66]);self.assertEqual(t['phone_reference'],[66,90]);self.assertLess(t['close'][1],180)
  self.assertEqual(round((t['native_proof'][1]-t['native_proof'][0])*30),375)
  self.assertEqual(round((t['phone_reference'][1]-t['phone_reference'][0])*30),720)
  with self.assertRaises(ValueError):m.make_timeline(dict(ds,human_context=26))
  with self.assertRaises(ValueError):m.make_timeline(dict(ds,mechanism=90))
 def test_english_cannot_touch_recitation_and_sources_cannot_speed_or_escape_crop(self):
  m=self.load()
  with self.assertRaises(ValueError):m.validate_audio_windows([('english',5,8),('quran',0,6)])
  m.validate_audio_windows([('quran',0,6),('english',6.1,8)])
  m.validate_source({'start_seconds':0,'end_seconds':12.5,'speed':1,'crop':[208,832,576,144]},12.5,976,1296)
  for patch in ({'speed':1.01},{'end_seconds':13},{'crop':[208,1200,576,144]}):
   with self.assertRaises(ValueError):m.validate_source(dict(start_seconds=0,end_seconds=12.5,speed=1,crop=[208,832,576,144],**{})|patch,12.5,976,1296)
 def test_quiet_handoffs_hold_previous_picture_without_early_phone(self):
  m=self.load();t={'listen':[0,6],'hook':[6.133,19.8],'native_proof':[38.033,50.533],'long_verse_cue':[50.7,60],'masjid_reservation':[60,66],'phone_reference':[66,90],'following':[90.2,100]}
  self.assertTrue(hasattr(m,'scene_at'),'Quiet handoff picture selection is missing')
  self.assertEqual(m.scene_at(t,6.05),'listen')
  self.assertEqual(m.scene_at(t,50.6),'native_proof')
  self.assertEqual(m.scene_at(t,90.1),'phone_reference')
 def test_native_proof_has_every_source_frame_once_despite_float_boundaries(self):
  m=self.load();self.assertTrue(hasattr(m,'source_frame'),'Exact source frame mapping is missing')
  start=1141/30;indices=[m.source_frame(i/30,start,375) for i in range(1141,1516)]
  self.assertEqual(indices,list(range(375)))
 def test_captions_use_approved_words_with_recognition_timing(self):
  m=self.load();self.assertTrue(hasattr(m,'caption_chunks'),'Approved-copy caption mapping is missing')
  chunks=m.caption_chunks('Pew on Ray-Ban display.',[{'word':'Q','start':0,'end':.2},{'word':'on','start':.2,'end':.4},{'word':'Ray','start':.4,'end':.5},{'word':'Ban','start':.5,'end':.7},{'word':'display','start':.7,'end':1}])
  self.assertEqual(chunks,[(0,1,'Pew on Ray-Ban display.')])
 def test_mechanism_exits_smoothly_while_moving_proof_keeps_full_opacity(self):
  m=self.load();self.assertTrue(hasattr(m,'scene_exit_opacity'),'Scene-exit opacity is missing')
  end=3671/30
  self.assertEqual(m.scene_exit_opacity('mechanism',end-.4,end),1)
  self.assertAlmostEqual(m.scene_exit_opacity('mechanism',end-.15,end),.5)
  self.assertLess(m.scene_exit_opacity('mechanism',end-1/30,end),.04)
  self.assertEqual(m.scene_exit_opacity('phone_reference',89.98,90),1)
 def test_transcription_accepts_known_spelling_only_and_rejects_missing_words(self):
  m=self.load();self.assertTrue(m.words_equal('Ayah Lens Quran Hifz Ray-Ban','Aya Lenz Koran Hifts Ray Ban'))
  self.assertFalse(m.words_equal('follow the meaning and stay with the moment','follow the meaning'))
if __name__=='__main__':unittest.main()
