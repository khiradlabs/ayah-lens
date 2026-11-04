#!/usr/bin/env python3
import importlib.util,json,tempfile,unittest,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HELPER=ROOT/'tools/prepare_v09_narration.py'

class NarrationTests(unittest.TestCase):
 def module(self):
  self.assertTrue(HELPER.exists(),'v0.9 verified narration helper is missing')
  spec=importlib.util.spec_from_file_location('v09',HELPER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 def test_approved_opening_is_exact_and_budget_is_bounded(self):
  m=self.module();p=m.load_plan()
  approved=json.loads((ROOT/'submission/RESTORATION-V0.9.json').read_text())['approved_opening']['narration']
  self.assertEqual(p['clips'][0]['text'],approved);self.assertEqual(len(approved.split()),87)
  self.assertLess(p['spoken_word_count']/175*60+p['quiet_budget_seconds']+p['transition_budget_seconds'],180)
 def test_voice_substitution_and_duplicate_ids_are_rejected(self):
  m=self.module();p=m.load_plan();p['voice']='marin'
  with self.assertRaisesRegex(ValueError,'selected B'):m.validate_plan(p)
  p=m.load_plan();p['clips'][-1]['id']='opening'
  with self.assertRaisesRegex(ValueError,'scene IDs'):m.validate_plan(p)
 def test_meaningful_omission_is_not_treated_as_phonetic_alias(self):
  m=self.module();self.assertTrue(m.words_equal('Ayah Lens. Fifty-nine tests.','Ayah Lens. 59 tests.'))
  self.assertTrue(m.words_equal('over six thousand verses', 'over 6,000 verses'))
  self.assertFalse(m.words_equal('Muse Spark resolves uncertain matches.','Muse Spark resolves matches.'))
  self.assertFalse(m.words_equal('Transcription and passage tracking run live.','Transcription runs live.'))
 def test_cached_changed_generation_is_rejected_before_reuse(self):
  m=self.module()
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'take.wav'
   with wave.open(str(path),'wb') as w:w.setparams((1,2,24000,0,'NONE','not compressed'));w.writeframes(b'\0\0'*24000)
   take={'model':'gpt-realtime-2.1','voice':'cedar','text':'Original text.','instructions':'B direction','speed':1}
   receipt={'provider':'OpenAI',**take,'sha256':m.sha(path)}
   path.with_suffix('.json').write_text(json.dumps(receipt));self.assertEqual(m.receipt_valid(path,take)['sha256'],m.sha(path))
   take['text']='Changed text.'
   with self.assertRaisesRegex(ValueError,'Cached generation identity'):m.receipt_valid(path,take)
 def test_performance_refinement_keeps_voice_speed_and_text(self):
  m=self.module();p=m.load_plan();scene=dict(p['clips'][0],instructions='Connected B flow; brief natural pauses.')
  self.assertTrue(hasattr(m,'take_for'),'per-clip performance refinement is missing')
  take=m.take_for(scene,p)
  self.assertEqual((take['voice'],take['speed'],take['text']),('cedar',1,scene['text']))
  self.assertEqual(take['instructions'],scene['instructions'])
 def test_future_teaching_must_remain_qualified_when_not_spoken(self):
  m=self.module();p=m.load_plan();p['onscreen_qualifications']=[]
  with self.assertRaisesRegex(ValueError,'future teaching'):m.validate_plan(p)
 def test_quiet_budget_must_equal_original_recitation_and_demo_slots(self):
  m=self.module();p=m.load_plan();p['quiet_budget_seconds']+=1
  with self.assertRaisesRegex(ValueError,'quiet allocation'):m.validate_plan(p)
 def test_unverified_clip_cannot_enter_export_manifest(self):
  m=self.module();p=m.load_plan()
  with self.assertRaisesRegex(ValueError,'verified'):m.validate_manifest({'clips':[{'id':'opening','verified':False}]},p)

if __name__=='__main__':unittest.main()
