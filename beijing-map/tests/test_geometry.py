import importlib.util, unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'tools/pack_map.py'
s=importlib.util.spec_from_file_location('pack',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class GeometryTests(unittest.TestCase):
 def test_crossing_tile_boundaries(self):
  a=(-100,2000);b=(8100,2000)
  segments=[m.clip(a,b,x*4000,0,(x+1)*4000,4000) for x in range(2)]
  self.assertEqual(segments,[((0,2000),(4000,2000)),((4000,2000),(8000,2000))])
 def test_outside_and_corner(self):
  self.assertIsNone(m.clip((-1,-1),(-1,5000),0,0,4000,4000))
  self.assertEqual(m.clip((-10,-10),(4010,4010),0,0,4000,4000),((0,0),(4000,4000)))
 def test_curved_road_not_shortcut(self):
  self.assertEqual(m.simplify([(0,0),(100,100),(200,0)],12),[(0,0),(100,100),(200,0)])
 def test_coordinate_precision(self):
  for n in [0,1,63,64,1999,2000,4095]:
   s=m.enc(n);self.assertEqual((ord(s[0])-33)*64+ord(s[1])-33,n)
 def test_wgs84_project(self):
  x,y=m.project(116.3913,39.9075)
  self.assertAlmostEqual(x/m.XDEG+115,116.3913)
  self.assertAlmostEqual(y/m.YDEG+39,39.9075)
if __name__=='__main__':unittest.main()
