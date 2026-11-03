"""Contract checks for the bounded, secret-safe Muse illustration helper."""
import base64, importlib.util, io, json, tempfile, unittest
from pathlib import Path
from PIL import Image

class MuseImageTests(unittest.TestCase):
    def module(self):
        p=Path(__file__).with_name('muse_image.py')
        self.assertTrue(p.exists(),'Muse helper missing')
        s=importlib.util.spec_from_file_location('muse_image',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    def image(self):
        b=io.BytesIO();Image.new('RGB',(32,24),'blue').save(b,format='PNG');return base64.b64encode(b.getvalue()).decode()
    def test_validated_image_and_receipt_do_not_expose_base64(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);out=root/'image.png'
            receipt=m.save_result({'data':[{'b64_json':self.image()}],'usage':{'total_tokens':42}},out,'prompt','test',1.2)
            self.assertEqual(receipt['dimensions'],[32,24]);self.assertEqual(receipt['est_cost_usd'],.01)
            self.assertNotIn('b64_json',json.dumps(receipt))
            with Image.open(out) as image:self.assertEqual(image.size,(32,24))
            self.assertEqual(len((root/'costs.jsonl').read_text().splitlines()),1)
    def test_empty_or_malformed_result_never_writes_an_asset(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'image.png'
            for result in ({'data':[]},{'data':[{'b64_json':'bad'}]},{'data':[{'b64_json':base64.b64encode(b'not an image').decode()}]}):
                with self.assertRaises(ValueError):m.save_result(result,out,'prompt','test',1)
                self.assertFalse(out.exists())
    def test_request_is_one_original_image_without_external_search(self):
        m=self.module();r=m.request_body('original scene')
        self.assertEqual(r['model'],'muse-image-1.0');self.assertEqual(r['n'],1)
        self.assertTrue(all(v is False for v in r['tool_enablement'].values()))

if __name__=='__main__':unittest.main()
