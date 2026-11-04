#!/usr/bin/env python3
"""Behavior checks for the restored v0.9 assembly contract."""
import importlib.util,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('restored',ROOT/'tools/render_restored_v09.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class RestoredTests(unittest.TestCase):
 def manifest(self,duration=10):
  source=json.loads((ROOT/'submission/narration-v0.9.json').read_text())
  return {'clips':[dict(c,path='synthetic.wav',duration_seconds=duration,sha256='test',verified=True) for c in source['clips']]}
 def test_approved_opening_cannot_be_replaced_by_audition(self):
  x=self.manifest();self.assertEqual(m.validate_narration(x),json.loads((ROOT/'submission/narration-v0.9.json').read_text())['spoken_word_count'])
  x['clips'][0]['text']='What if your glasses became your personal Quran translator?'
  with self.assertRaisesRegex(ValueError,'approved opening'):m.validate_narration(x)
 def test_source_range_is_converted_before_tagging(self):
  self.assertIn('in_range=pc:out_range=tv',m.SOURCE_FILTER)
  self.assertIn('in_color_matrix=bt601:out_color_matrix=bt709',m.SOURCE_FILTER)
 def test_normalization_uses_exact_sample_count_not_filter_timestamps(self):
  chain=m.normalization_filter(1110)
  self.assertIn('asetpts=N/SR/TB',chain)
  self.assertIn('apad=whole_len=1776000',chain)
  self.assertIn('atrim=end_sample=1776000',chain)
 def test_volume_report_parser_uses_captured_numeric_group(self):
  self.assertEqual(m.audio_peak('[Parsed_volumedetect] max_volume: -3.0 dB'),-3.0)
  with self.assertRaisesRegex(ValueError,'peak'):m.audio_peak('no volume report')
 def test_exact_source_frame_rounding(self):
  self.assertEqual([m.source_frame(i/30,0,240) for i in range(240)],list(range(240)))
  self.assertEqual(m.source_frame(8,0,240),239)
 def test_demo_slots_are_separated_and_silent(self):
  edit=m.layout(self.manifest());slots=[s for s in edit['scenes'] if s['kind']=='slot']
  self.assertEqual([(s['id'],s['frames']) for s in slots],[('tv_demo',540),('long_demo',330),('toggle_demo',210)])
  self.assertTrue(all('AWAITING RECORDING' in s['label'] and not s.get('audio') for s in slots))
  ids=[s['id'] for s in edit['scenes']]
  self.assertLess(ids.index('tv_demo'),ids.index('long_demo'));self.assertLess(ids.index('long_demo'),ids.index('meta_pipeline'))
  self.assertLess(ids.index('hifz'),ids.index('toggle_demo'))
 def test_unverified_voice_and_overlong_cut_rejected(self):
  x=self.manifest();x['clips'][0]['verified']=False
  with self.assertRaisesRegex(ValueError,'verified'):m.layout(x)
  with self.assertRaisesRegex(ValueError,'180'):m.layout(self.manifest(20))
 def test_layout_has_complete_narration_without_tempo_changes(self):
  x=self.manifest();e=m.layout(x);audio=[s for s in e['scenes'] if s['kind']=='voice']
  self.assertEqual([s['id'] for s in audio],[c['id'] for c in x['clips']])
  self.assertTrue(all(s['frames']/30>=s['duration_seconds'] for s in audio))
  self.assertTrue(all(s['speed']==1 for s in e['scenes']))
 def test_live_and_cached_paths_are_distinguished(self):
  self.assertIn('cached',m.CACHE_LABEL.lower());self.assertIn('live',m.LIVE_LABEL.lower())
  self.assertEqual(m.PIPELINE,['GLASSES AUDIO','MUSE VOICE','OUR TRACKER','PUBLISHED SOURCE','LENS'])
 def test_actual_waveform_cues_accept_numeric_asr_without_estimated_pauses(self):
  words=[{'word':'2','start':5.5},{'word':'billion','start':5.9},{'word':'Muslims,','start':6.3},{'word':'The','start':8},{'word':'potential','start':8.3},{'word':'impact','start':8.7}]
  self.assertEqual(m.phrase_starts(words,['Two billion Muslims','The potential impact']),[5.5,8])
  with self.assertRaisesRegex(ValueError,'Cannot align'):m.phrase_starts(words,['What if your glasses'])
 def test_opening_has_original_sequence_and_new_impact(self):
  self.assertEqual([c[0] for c in m.OPENING_CUES],['problem','population','impact','need','hook','meaning','following','hands_free'])
  self.assertIn('potential impact is enormous',m.APPROVED_OPENING)

if __name__=='__main__':unittest.main()
