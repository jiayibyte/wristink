#!/usr/bin/env python3
"""OSM Overpass geometry -> independently loaded 4 km map resources.
Coordinates are WGS84, local equirectangular projection (not GCJ-02).
The derived road database is ODbL-1.0; retain data and attribution.
"""
import json, math, html, collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
XDEG=111320*math.cos(math.radians(40)); YDEG=111320
TILE=16000; UNIT=4
KINDS={'motorway':0,'trunk':0,'primary':0,'motorway_link':0,'trunk_link':0,'primary_link':0,'secondary':1,'secondary_link':1,'tertiary':1,'tertiary_link':1,'residential':2,'unclassified':2,'living_street':2,'pedestrian':2,'footway':3,'path':3,'track':3,'steps':3}
def project(lon,lat): return ((lon-115)*XDEG,(lat-39)*YDEG)
def distance(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1]
 t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy))) if dx or dy else 0
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def simplify(pts,tol):
 if len(pts)<3:return pts
 d,i=max((distance(p,pts[0],pts[-1]),i) for i,p in enumerate(pts[1:-1],1))
 if d<=tol:return [pts[0],pts[-1]]
 return simplify(pts[:i+1],tol)[:-1]+simplify(pts[i:],tol)
def clip(a,b,x0,y0,x1,y1):
 dx=b[0]-a[0];dy=b[1]-a[1];lo=0;hi=1
 for p,q in [(-dx,a[0]-x0),(dx,x1-a[0]),(-dy,a[1]-y0),(dy,y1-a[1])]:
  if p==0:
   if q<0:return None
  else:
   t=q/p
   if p<0:lo=max(lo,t)
   else:hi=min(hi,t)
   if lo>hi:return None
 return ((a[0]+lo*dx,a[1]+lo*dy),(a[0]+hi*dx,a[1]+hi*dy))
def enc(n):
 assert 0<=n<4096,n
 return chr(33+n//64)+chr(33+n%64)
def encode_path(kind,pts,tx,ty):
 coords=[]
 for x,y in pts:
  p=(round((x-tx*TILE)/UNIT),round((y-ty*TILE)/UNIT))
  if not coords or coords[-1]!=p:coords.append(p)
 if len(coords)<2:return ''
 assert len(coords)<4096
 return chr(33+kind)+enc(len(coords))+''.join(enc(x)+enc(y) for x,y in coords)
def main():
 raw=json.loads((ROOT/'data/beijing-osm.json').read_text()); ways=raw.get('elements',[])
 if not ways or raw.get('remark'):raise ValueError('Incomplete/empty Overpass response: '+str(raw.get('remark')))
 tiles=collections.defaultdict(list);counts=collections.Counter();segments=0
 for way in ways:
  kind=KINDS.get(way.get('tags',{}).get('highway'))
  geo=way.get('geometry',[])
  if kind is None or len(geo)<2:continue
  counts[way['tags']['highway']]+=1
  pts=simplify([project(p['lon'],p['lat']) for p in geo],8 if kind==3 else 12)
  current={}
  for a,b in zip(pts,pts[1:]):
   for sx in range(math.floor(min(a[0],b[0])/4000),math.floor(max(a[0],b[0])/4000)+1):
    for sy in range(math.floor(min(a[1],b[1])/4000),math.floor(max(a[1],b[1])/4000)+1):
     clipped=clip(a,b,sx*4000,sy*4000,(sx+1)*4000,(sy+1)*4000)
     if not clipped:continue
     key=(sx,sy);p,q=clipped
     runs=current.setdefault(key,[])
     if runs and math.dist(runs[-1][-1],p)<0.01:runs[-1].append(q)
     else:runs.append([p,q])
  for (sx,sy),runs in current.items():
   tx=sx//4;ty=sy//4
   for run in runs:
    # Bound decode scratch array and split with shared endpoints.
    for i in range(0,len(run)-1,240):
     encoded=encode_path(kind,run[i:i+241],tx,ty)
     if encoded:tiles[(tx,ty)].append((sx,sy,encoded));segments+=len(run[i:i+241])-1
 minx=min(t[0] for t in tiles);maxx=max(t[0] for t in tiles);miny=min(t[1] for t in tiles);maxy=max(t[1] for t in tiles)
 out=ROOT/'resources/map';out.mkdir(parents=True,exist_ok=True)
 xml=['<resources>'];sizes=[];preview={}
 for ty in range(miny,maxy+1):
  for tx in range(minx,maxx+1):
   if (tx,ty) not in tiles:continue
   name=f'Tile_{tx}_{ty}'
   chunks=[];chunk='';cell=None
   for sx,sy,record in sorted(tiles[(tx,ty)]):
    if cell is None:cell=(sx,sy)
    if len(chunk)+len(record)>7000:
     if chunk:chunks.append((cell,chunk))
     chunk='';cell=(sx,sy)
    chunk+=record
   if chunk:chunks.append((cell,chunk))
   index=[]
   for j,((sx,sy),chunk) in enumerate(chunks):
    part=f'{name}_{j}'
    def dec2(s,i):return (ord(s[i])-33)*64+ord(s[i+1])-33
    bounds=[4095,4095,0,0];p=0
    while p<len(chunk):
     n=dec2(chunk,p+1);p+=3
     for k in range(n):
      x=dec2(chunk,p);y=dec2(chunk,p+2);p+=4
      bounds=[min(bounds[0],x),min(bounds[1],y),max(bounds[2],x),max(bounds[3],y)]
    header=''.join(enc(v) for v in bounds)
    xml.append(f'<jsonData id="{part}">{html.escape(json.dumps(header+chunk))}</jsonData>')
    index.append('Rez.JsonData.'+part)
   (out/(name+'.mcfrag')).write_text(','.join(index))
   # Generated chunk loader is paged by tile; no geometry is held globally.
   preview[f'{tx},{ty}']=[c for cell,c in chunks]
   sizes.append(sum(len(c) for cell,c in chunks))
   
 # Geometry lives in independent resources; the code index contains only IDs.
 xml.append('</resources>');(out/'maps.xml').write_text('\n'.join(xml))
 loader=['import Toybox.Lang;','module MapData {',f'const XDEG={XDEG:.6f}; const YDEG={YDEG}; const TILE={TILE};',f'const MINX={minx};const MAXX={maxx};const MINY={miny};const MAXY={maxy};',
 'function chunks(tx,ty) { if(tx<MINX || tx>MAXX){return [];} var row;switch(ty) {']
 for ty in range(miny,maxy+1):loader.append(f'case {ty}: row=row{ty}();break;')
 loader+=['default:return [];} return (row as Array)[tx-MINX]; }']
 for ty in range(miny,maxy+1):
  loader.append(f'function row{ty}() {{ return [')
  for tx in range(minx,maxx+1):
   name=f'Tile_{tx}_{ty}';frag=out/(name+'.mcfrag')
   loader.append('['+frag.read_text()+'],' if frag.exists() else '[],')
   if frag.exists():frag.unlink()
  loader+= [']; }']
 loader+=['}']
 (ROOT/'source/MapData.mc').write_text('\n'.join(loader))
 (ROOT/'data/packed-preview.json').write_text(json.dumps(preview))
 stats=dict(osm_timestamp=raw.get('osm3s',{}).get('timestamp_osm_base'),ways=len(ways),road_classes=dict(counts),tiles=len(tiles),tile_meters=TILE,segments=segments,encoded_bytes=sum(sizes),max_tile_bytes=max(sizes),coordinate_unit_meters=UNIT,bounds_grid=[minx,miny,maxx,maxy],simplification_meters={'roads':12,'paths':8},coordinate_system='WGS84',source='https://download.geofabrik.de/asia/china/beijing.html',license='ODbL-1.0')
 (ROOT/'data/map-stats.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
