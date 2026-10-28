import importlib.util
from pathlib import Path
import tempfile
import unittest
from PIL import Image

spec=importlib.util.spec_from_file_location('pixel_review',Path(__file__).parents[1]/'scripts/pixel_review.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)

class PixelReviewTests(unittest.TestCase):
    def test_mask_excludes_hardware_and_detects_one_pixel_shift(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);ref=Image.new('RGB',(8,8));cur=ref.copy()
            ref.putpixel((2,2),(255,255,255));cur.putpixel((3,2),(255,255,255))
            cur.putpixel((7,7),(255,0,0))
            mask=Image.new('L',(8,8),255);mask.putpixel((7,7),0)
            ref.save(p/'ref.png');cur.save(p/'cur.png');mask.save(p/'mask.png')
            r=qa.compare(p/'ref.png',p/'cur.png',p/'out',mask=p/'mask.png')
            self.assertEqual(r['regions']['screen']['changed_pixels'],2)
            self.assertEqual(r['regions']['screen']['visible_pixels'],63)
            with Image.open(p/'out/native-reference-actual-diff.png') as image:
                self.assertEqual(image.size,(24,8))
            with Image.open(p/'out/magnified-reference-actual-diff.png') as image:
                self.assertEqual(image.size,(96,32))

    def test_refuses_false_comparison(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);Image.new('RGB',(8,8)).save(p/'a.png');Image.new('RGB',(9,8)).save(p/'b.png')
            with self.assertRaises(ValueError):qa.compare(p/'a.png',p/'b.png',p/'out')
            with self.assertRaises(ValueError):qa.compare(p/'a.png',p/'a.png',p/'out',regions={'bad':[7,0,2,2]})

    def test_detects_collapsed_zero_and_eight_and_bounds(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);image=Image.new('RGBA',(40,5),(255,255,255,0));lines=['page id=0 file="digits.png"']
            for i in range(10):
                # Distinct bit patterns; deliberately make 8 equal 0.
                code=1 if i==8 else i+1
                for bit in range(4):
                    if code & (1<<bit):image.putpixel((i*4+bit,2),(255,255,255,255))
                image.putpixel((i*4,0),(255,255,255,255))
                lines.append(f'char id={48+i} x={i*4} y=0 width=4 height=5 xadvance=5 yoffset=0 page=0')
            image.save(p/'digits.png');(p/'digits.fnt').write_text('\n'.join(lines))
            r=qa.atlas(p/'digits.fnt',p/'audit.json')
            self.assertFalse(r['passed']);self.assertTrue(any('0 and 8' in s for s in r['errors']))
            lines[-1]=lines[-1].replace('width=4','width=8');(p/'digits.fnt').write_text('\n'.join(lines))
            self.assertTrue(any('rectangle' in s for s in qa.atlas(p/'digits.fnt',p/'audit.json')['errors']))

if __name__=='__main__':unittest.main()
