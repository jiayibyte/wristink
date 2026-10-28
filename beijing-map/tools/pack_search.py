#!/usr/bin/env python3
import osmium,json,math,html,collections,re
from pathlib import Path
from pypinyin import lazy_pinyin
ROOT=Path(__file__).resolve().parents[1];XDEG=111320*math.cos(math.radians(40))
def enc(n):return ''.join(chr(33+((n>>shift)&63)) for shift in [12,6,0])
def project(lon,lat):return round((lon-115)*XDEG/2),round((lat-39)*111320/2)
def interesting(t):return any(k in t for k in ['amenity','tourism','shop','leisure','place','railway','public_transport','addr:housenumber','highway'])
def label(t):
 name=t.get('name:zh') or t.get('name');street=t.get('addr:street');num=t.get('addr:housenumber')
 if street and num:
  address=street+num+('' if num.endswith('号') else '号');name=address if not name else name+' '+address
 return name
class Read(osmium.SimpleHandler):
 def __init__(self):super().__init__();self.rows=[]
 def node(self,n):
  t=dict(n.tags);name=label(t)
  if not name or not interesting(t):return
  self.rows.append((name,*project(n.location.lon,n.location.lat)))
 def way(self,w):
  t=dict(w.tags);name=label(t)
  if not name or not interesting(t):return
  try:ps=[(n.lon,n.lat) for n in w.nodes]
  except osmium.InvalidLocationError:return
  if not ps:return
  if 'highway' in t:p=ps[len(ps)//2]
  else:p=(sum(p[0] for p in ps)/len(ps),sum(p[1] for p in ps)/len(ps))
  self.rows.append((name,*project(*p)))
def main():
 cache=ROOT/'data/search-candidates.json'
 if cache.exists():rows=json.loads(cache.read_text())
 else:
  r=Read();r.apply_file(str(ROOT/'data/beijing-full.osm.pbf'),locations=True);rows=r.rows;cache.write_text(json.dumps(rows,ensure_ascii=False))
 buckets=collections.defaultdict(list);seen=set();count=0
 for name,x,y in rows:
  name=name.replace('|',' ').replace('\n',' ')[:40]
  if not (0<=x<262144 and 0<=y<262144):continue
  key=(name,x//150,y//150)
  if key in seen:continue
  seen.add(key);py=re.sub('[^a-z0-9]','',''.join(lazy_pinyin(name)).lower())
  if len(py)<2:continue
  aliases={py}
  for prefix in ['beijingshi','beijing']:
   if py.startswith(prefix) and len(py)>len(prefix)+1:aliases.add(py[len(prefix):])
  for alias in aliases:buckets[alias[:2]].append(name+'|'+alias+'|'+enc(x)+enc(y)+'\n')
  count+=1
 out=ROOT/'resources/search';out.mkdir(exist_ok=True);xml=['<resources>'];ordered=[]
 for key,records in buckets.items():
  for record in set(records):
   name,py,position=record.rstrip('\n').split('|');ordered.append((py,name,position))
 ordered.sort();pages=[];ranges={};chunk='';previous_name='';previous_py='';current=[]
 def common(a,b):
  n=0
  while n<min(len(a),len(b),63) and a[n]==b[n]:n+=1
  return n
 for py,name,position in ordered:
  pn=common(name,previous_name);pp=common(py,previous_py)
  record=chr(33+pn)+name[pn:]+'|'+chr(33+pp)+py[pp:]+'|'+position+'\n'
  if len((chunk+record).encode())+2>8000 and chunk:
   pages.append(chunk);chunk='';previous_name='';previous_py=''
   record='!'+name+'|!'+py+'|'+position+'\n'
  page=len(pages);key=py[:2]
  if key not in ranges:ranges[key]=[page,page]
  ranges[key][1]=page
  size=len(record);record=chr(33+size//64)+chr(33+size%64)+record
  chunk+=record;previous_name=name;previous_py=py
 if chunk:pages.append(chunk)
 values=[]
 for i,text in enumerate(pages):
  rid='SearchPage_'+str(i);values.append('Rez.JsonData.'+rid)
  xml.append(f'<jsonData id="{rid}">{html.escape(json.dumps(text,ensure_ascii=False))}</jsonData>')
 def enc2(n):return chr(33+n//64)+chr(33+n%64)
 index=''.join(key+enc2(a)+enc2(b) for key,(a,b) in sorted(ranges.items()))
 xml.append(f'<jsonData id="SearchIndex">{html.escape(json.dumps(index))}</jsonData>');xml.append('</resources>');(out/'search.xml').write_text('\n'.join(xml))
 code=['import Toybox.Lang;','module SearchData {',f'const PAGE_N={len(pages)};const PREFIX_N={len(ranges)};','function index(){return Rez.JsonData.SearchIndex;}','function page(n){var row;switch((n/32).toNumber()){']
 for i in range(0,len(values),32):code.append(f'case {i//32}:row=p{i//32}();break;')
 code+=['default:return null;}return (row as Array)[n%32];}']
 for i in range(0,len(values),32):code.append(f'function p{i//32}(){{return ['+','.join(values[i:i+32])+'];}')
 code+=['}'];(ROOT/'source/SearchData.mc').write_text('\n'.join(code))
 resources=len(values)+1;largest=max(len(text.encode()) for text in pages);index=ranges
 stats={'unique_places_and_addresses':count,'aliases':sum(len(v) for v in buckets.values()),'prefix_buckets':len(index),'resources':resources,'max_utf8_payload':largest,'coordinates':'WGS84','query':'Chinese substring or full-pinyin prefix; Beijing/BeijingShi prefix also stripped','source':'Geofabrik OSM Beijing 2026-10-25'}
 (ROOT/'data/search-stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2));print(json.dumps(stats,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
