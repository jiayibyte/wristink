"""Validate skin diversity and native bitmap constraints, not weather accuracy."""
from pathlib import Path
from PIL import Image
import hashlib,json,zipfile,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from map_skins import NAMES,select
from assets import phased_world

def main():
    rows=[];hashes=set()
    for skin,(name,label) in enumerate(NAMES):
        p=ROOT/f'resources/drawables/map-skin-{skin}-0.png';im=Image.open(p)
        assert im.mode=='1' and im.size==(89,29)
        digest=hashlib.sha256(im.tobytes()).hexdigest();assert digest not in hashes;hashes.add(digest)
        night=Image.open(ROOT/f'resources/drawables/map-skin-{skin}-1.png')
        assert night.mode=='1' and night.size==im.size
        assert night.tobytes()!=im.tobytes()
        rows.append({'id':skin,'name':name,'label':label,'day_sha256':digest})
    assert len(hashes)>=12 and len(NAMES)==16
    with zipfile.ZipFile(ROOT/'dist/RetroWorld-Instinct3-1.2.5.zip') as z:
        assert (ROOT/'resources/drawables/map-skin-1-0.png').read_bytes()==z.read('source-project/resources/drawables/map.png')
    seen={select(k,p,m) for k in range(8) for p in range(4) for m in (0,480,660,780,960,1320)}
    assert seen==set(range(16)),seen
    frames=[phased_world(t).tobytes() for t in (0,6,12,18)]
    assert len(set(frames))==4
    report={'count':len(NAMES),'unique_day_bitmaps':len(hashes),'all_day_night_pairs_distinct':True,'native_size':[89,29],'format':'1-bit','old_solid_map_preserved_exactly':True,'all_skins_reachable':True,'daily_phase_frames_distinct':True,'skins':rows}
    (ROOT/'dist/map-skins-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Validated 16 distinct, reachable skins; exact old solid option; all four daily phases differ; all bitmaps 89x29 monochrome.')

if __name__=='__main__':main()
