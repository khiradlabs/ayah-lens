"""Contracts protecting generated narration and genuine recitation windows."""
import importlib.util,io,json,tempfile,unittest,wave,struct
from pathlib import Path

class NarrationTests(unittest.TestCase):
    def module(self):
        p=Path(__file__).with_name('openai_narration.py')
        self.assertTrue(p.exists(),'OpenAI narration helper is missing')
        s=importlib.util.spec_from_file_location('openai_narration',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    def test_request_keeps_words_and_directs_emotion(self):
        m=self.module();body=m.request_body('Just listen. And understand.','Warm sincere closing')
        self.assertEqual(body['input'],'Just listen. And understand.')
        self.assertEqual((body['model'],body['voice'],body['response_format']),('gpt-4o-mini-tts',m.PLAN['voice'],'wav'))
        self.assertEqual(body['instructions'],'Warm sincere closing')
    def test_cache_identity_changes_with_emotional_direction(self):
        m=self.module();a=m.identity('Words','Warm');b=m.identity('Words','Confident')
        self.assertNotEqual(a,b);self.assertEqual(a,m.identity('Words','Warm'))
        self.assertNotEqual(m.identity('Words','Warm',voice='cedar'),m.identity('Words','Warm',voice='marin'))
    def test_clip_fit_rejects_truncation_and_large_speedup(self):
        m=self.module();self.assertEqual(m.fit_tempo(2,3),1)
        self.assertAlmostEqual(m.fit_tempo(3.15,3),1.05)
        with self.assertRaisesRegex(ValueError,'pacing'):m.fit_tempo(4,3)
        with self.assertRaises(ValueError):m.fit_tempo(0,3)
    def test_clip_cannot_touch_genuine_recitation(self):
        m=self.module();m.validate_windows([{'start':8.1,'duration':3},{'start':38.2,'duration':9}])
        for clip in ({'start':7.9,'duration':1},{'start':29.5,'duration':1},{'start':59.5,'duration':1}):
            with self.assertRaisesRegex(ValueError,'protected'):m.validate_windows([clip])
        with self.assertRaisesRegex(ValueError,'overlap'):m.validate_windows([{'start':9,'duration':3},{'start':10,'duration':1}])
    def test_redaction_and_manifest_never_contain_credential(self):
        m=self.module();self.assertNotIn('test-sensitive',m.safe_error('bad test-sensitive value','test-sensitive'))
        beats=m.beats();self.assertEqual(len(beats),16)
        self.assertEqual(beats[2]['text'],'What if your glasses became your personal Quran translator?')
        self.assertNotIn('api_key',json.dumps(beats).lower())
    def test_streaming_wav_header_does_not_invent_hours_or_cost(self):
        m=self.module();b=io.BytesIO()
        with wave.open(b,'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b'\0\0'*24000)
        data=bytearray(b.getvalue());data[4:8]=struct.pack('<I',0xffffffff);data[40:44]=struct.pack('<I',0xffffffff)
        self.assertTrue(callable(getattr(m,'normalize_wav',None)),'streaming WAV normalization missing')
        clean,seconds,channels,rate=m.normalize_wav(bytes(data))
        self.assertEqual((seconds,channels,rate),(1,1,24000))
        with wave.open(io.BytesIO(clean)) as w:self.assertEqual(w.getnframes(),24000)
    def test_coherent_hook_requires_every_word_before_slicing(self):
        m=self.module();self.assertTrue(callable(getattr(m,'align_phrases',None)),'validated phrase alignment missing')
        phrases=['Just listen.','And understand.'];words=[{'word':w,'start':i*.4,'end':i*.4+.2} for i,w in enumerate(['Just','listen','And','understand'])]
        spans=m.align_phrases(phrases,words,1.6)
        self.assertEqual(len(spans),2);self.assertLessEqual(spans[0][0],0)
        self.assertGreaterEqual(spans[-1][1],1.4)
        with self.assertRaisesRegex(ValueError,'words'):m.align_phrases(phrases,words[:2],1.6)
    def test_lexical_check_allows_orthography_but_not_omitted_clauses(self):
        m=self.module();self.assertTrue(callable(getattr(m,'canonical_words',None)),'orthographic lexical normalization missing')
        expected='Ayah Lens covers all114 surahs. Fifty-nine tests.'
        actual='Aya Lens covers all one hundred and fourteen suras. 59 tests.'
        self.assertEqual(m.canonical_words(expected.replace('all114','all 114')),m.canonical_words(actual))
        self.assertNotEqual(m.canonical_words('Just listen. And understand.'),m.canonical_words('Just listen.'))
    def test_transcription_upload_accepts_only_receipted_synthetic_english(self):
        m=self.module();self.assertTrue(callable(getattr(m,'validate_transcription_source',None)),'synthetic-only upload guard missing')
        with tempfile.TemporaryDirectory() as d:
            m.WORK=Path(d);p=Path(d)/'synthetic.wav';p.write_bytes(b'synthetic fixture')
            r={'provider':'OpenAI','text':'Just listen.','sha256':m.sha(p)};p.with_suffix('.json').write_text(json.dumps(r))
            m.validate_transcription_source(p)
            r['text']='بسم الله';p.with_suffix('.json').write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'English'):m.validate_transcription_source(p)
            r['text']='Words';r['sha256']='bad';p.with_suffix('.json').write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'hash'):m.validate_transcription_source(p)
    def test_disclosure_asset_stays_inside_existing_version_header(self):
        from PIL import Image
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            m.WORK=Path(d);m.badges()
            with Image.open(Path(d)/'ai-disclosure.png') as image:
                self.assertEqual(image.size,(460,48),'AI disclosure must not reach recorded-source labels below the version header')

if __name__=='__main__':unittest.main()
