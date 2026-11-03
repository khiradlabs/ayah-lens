"""Source and caption contracts for integrating the approved opening."""
import importlib.util
import tempfile
from pathlib import Path
import unittest

class FullDemoAssemblyTests(unittest.TestCase):
    def module(self):
        path=Path(__file__).with_name('assemble_full_demo.py')
        self.assertTrue(path.exists(),'Full-demo assembly helper is missing')
        spec=importlib.util.spec_from_file_location('assemble_full_demo',path)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

    def test_source_mapping_preserves_real_tail_and_retimes_only_product(self):
        m=self.module()
        self.assertEqual(m.source_at(37.9),('opening',37.9))
        self.assertEqual(m.source_at(38),('master',36))
        name,t=m.source_at(43);self.assertEqual((name,t),('master',42))
        self.assertEqual(m.source_at(48),('master',48))
        self.assertEqual(m.source_at(60),('master',60))
        self.assertEqual(m.source_at(89.9),('master',89.9))
        self.assertEqual(m.source_at(179.8),('master',179.8))
        for t in (-1,179.9):
            with self.assertRaises(ValueError):m.source_at(t)

    def test_caption_merge_keeps_approved_opening_and_same_tail_times(self):
        m=self.module()
        opening=[(0,4.4,'Just listen.'),(30,38,'Recorded display')]
        old=[(8,20,'obsolete opening'),(36.4,40.124,'Meet Ayah Lens'),(43.848,46.642,'meaning into view'),(48.4,59.164,'During Salat'),(168.4,178.2,'closing')]
        cues=m.merge_captions(opening,old)
        self.assertEqual(cues[:2],opening)
        self.assertNotIn('obsolete opening',[x[2] for x in cues])
        self.assertAlmostEqual(cues[2][0],38+.4/1.2)
        self.assertAlmostEqual(cues[3][1],38+10.642/1.2)
        self.assertEqual(cues[4:],old[3:])

    def test_boundary_crossing_captions_are_rejected_instead_of_silently_clipped(self):
        m=self.module()
        for old in ([(35,37,'bad')],[(47,49,'bad')]):
            with self.assertRaisesRegex(ValueError,'boundary'):m.merge_captions([],old)

    def test_badge_replacement_is_confined_to_the_editorial_header(self):
        m=self.module();badge=m.PLAN.get('editorial_badge')
        self.assertIsNotNone(badge,'Imported version badge replacement is missing')
        self.assertEqual(badge['text'],'VIDEO v0.5 / GUIDE VOICE')
        self.assertEqual(badge['start_seconds'],38)
        x,y,w,h=badge['rectangle']
        self.assertGreaterEqual(x,1390);self.assertGreaterEqual(y,20)
        self.assertLessEqual(x+w,1900);self.assertLessEqual(y+h,80)

    def test_badge_raster_is_bounded_and_contains_lettering(self):
        m=self.module()
        self.assertTrue(callable(getattr(m,'badge_image',None)),'Badge raster helper is missing')
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'badge.png';m.badge_image(path)
            with Image.open(path) as im:
                self.assertEqual(im.size,(460,48))
                self.assertEqual(im.getpixel((0,0)),(243,239,229))
                self.assertGreater(len(im.getcolors(100000)),2)

    def test_caption_round_trip_and_no_overlap(self):
        m=self.module();cues=[(8.1,11.784,'Familiar sound'),(38.333,41.437,'Meta tools')]
        self.assertEqual(m.parse_srt(m.srt_text(cues)),cues)
        with self.assertRaisesRegex(ValueError,'overlap'):m.srt_text([(1,3,'a'),(2,4,'b')])

if __name__=='__main__':unittest.main()
