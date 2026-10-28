#!/usr/bin/env python3
"""Memory-bounded multilevel routing: shortest-path forest + portal graph.
Every parent/crossing edge follows real OSM connectivity. No geometric crossing
is invented. Portal-graph shortest paths are recommended routes, not guaranteed
fine-graph shortest paths. Node pages and route expansion stream on the watch.
"""
import pickle,math,heapq,collections,json,html
from pathlib import Path
import networkx as nx
from pack_map import simplify
ROOT=Path(__file__).resolve().parents[1];FP=512;MP=64;CELL=2000

def enc(n,k):
 assert 0<=n<64**k,n
 return ''.join(chr(33+((n>>(6*i))&63)) for i in range(k-1,-1,-1))
def geometry(points):
 points=simplify(points,6)
 start=points[0];middle=points[1:-1]
 relative=all(-2048<=round((p[j]-start[j])/2)<=2047 for p in middle for j in [0,1])
 data=enc(0 if relative else 1,1)+enc(len(middle),2)
 for x,y in middle:
  data+=(enc(round((x-start[0])/2)+2048,2)+enc(round((y-start[1])/2)+2048,2)) if relative else enc(round(x/2),3)+enc(round(y/2),3)
 return data

def edge_geometry(g,a,b):
 e=g[a][b];points=e['geometry']
 return points if math.dist(points[0],g.nodes[a]['xy'])<1 else points[::-1]

def main():
 meta=ROOT/'data/navigation-stats.json'
 if meta.exists() and json.loads(meta.read_text()).get('foot_direction_restrictions',0):
  raise ValueError('Directed foot restrictions require a directed hierarchy; refusing undirected preprocessing.')
 cache=ROOT/'data/nav-hierarchy.pickle'
 if cache.exists():g,coords,owner,parent,dist,roots,portals,components=pickle.loads(cache.read_bytes())
 else:
  raw,coords,pois=pickle.loads((ROOT/'data/nav-compact.pickle').read_bytes())
  g=nx.Graph()
  for a,b,data in raw.edges(data=True):
   if a==b:continue
   if not g.has_edge(a,b) or data['weight']<g[a][b]['weight']:g.add_edge(a,b,weight=data['weight'],geometry=data['geometry'])
  for n in g:g.nodes[n]['xy']=coords[n]
  components={n:i for i,c in enumerate(sorted(nx.connected_components(g),key=len,reverse=True)) for n in c}
  # One anchor per occupied spatial cell and connected component.
  cells={}
  for n,(x,y) in coords.items():
   if n not in g:continue
   sx,sy=math.floor(x/CELL),math.floor(y/CELL);key=(sy,sx,components[n]);d=(x-(sx+.5)*CELL)**2+(y-(sy+.5)*CELL)**2
   if key not in cells or d<cells[key][0]:cells[key]=(d,n)
  roots=[cells[k][1] for k in sorted(cells)];owner={};parent={};dist={};heap=[]
  for i,n in enumerate(roots):owner[n]=i;parent[n]=n;dist[n]=0.;heap.append((0.,n))
  heapq.heapify(heap);settled=0
  while heap:
   d,n=heapq.heappop(heap)
   if d!=dist.get(n):continue
   settled+=1
   for k,e in g[n].items():
    nd=d+e['weight']
    if nd<dist.get(k,float('inf')):
     dist[k]=nd;owner[k]=owner[n];parent[k]=n;heapq.heappush(heap,(nd,k))
  print('Forest',settled,'nodes;',len(roots),'anchors',flush=True)
  portals={}
  for a,b,e in g.edges(data=True):
   ra,rb=owner[a],owner[b]
   if ra==rb:continue
   if ra>rb:ra,rb,a,b=rb,ra,b,a
   w=dist[a]+e['weight']+dist[b];key=(ra,rb)
   if key not in portals or w<portals[key][0]:portals[key]=(w,a,b)
  print('Portals',len(portals),flush=True)
  cache.write_bytes(pickle.dumps((g,coords,owner,parent,dist,roots,portals,components),protocol=4))
 ids=sorted(g,key=lambda n:(math.floor(coords[n][1]/CELL),math.floor(coords[n][0]/CELL),coords[n][0],coords[n][1]))
 number={n:i for i,n in enumerate(ids)};assert len(ids)<64**4 and len(roots)<64**3
 spatial=collections.defaultdict(dict)
 for i,n in enumerate(ids):
  x,y=coords[n];sx,sy=math.floor(x/CELL),math.floor(y/CELL)
  if sx not in spatial[sy]:spatial[sy][sx]=[i,0]
  spatial[sy][sx][1]+=1
 out=ROOT/'resources/navigation';out.mkdir(exist_ok=True);xml=['<resources>'];fine=[];macro=[];largest=0
 for start in range(0,len(ids),FP):
  records=[];offsets=[];offset=0
  for n in ids[start:start+FP]:
   x,y=coords[n];p=parent[n]
   geo=enc(0,1)+enc(0,2) if p==n else geometry(edge_geometry(g,n,p))
   record=enc(round(x/2),3)+enc(round(y/2),3)+enc(number[p],4)+enc(owner[n],3)+geo
   records.append(record);offsets.append(offset);offset+=len(record)
  text=''.join(enc(v,3) for v in offsets)+''.join(records);name='Fine_'+str(start//FP);fine.append('Rez.JsonData.'+name);largest=max(largest,len(text))
  xml.append(f'<jsonData id="{name}">{html.escape(json.dumps(text))}</jsonData>')
 adjacency=collections.defaultdict(list)
 for (ra,rb),(w,a,b) in portals.items():
  adjacency[ra].append((rb,w,a,b));adjacency[rb].append((ra,w,b,a))
 for start in range(0,len(roots),MP):
  records=[];offsets=[];offset=0
  for rid in range(start,min(start+MP,len(roots))):
   n=roots[rid];x,y=coords[n];adj=sorted(adjacency[rid]);record=enc(round(x/2),3)+enc(round(y/2),3)+enc(components[n],3)+enc(number[n],4)+enc(len(adj),2)
   for other,w,a,b in adj:
    record+=enc(other,3)+enc(math.ceil(w),3)+enc(number[a],4)+enc(number[b],4)+geometry(edge_geometry(g,a,b))
   records.append(record);offsets.append(offset);offset+=len(record)
  text=''.join(enc(v,3) for v in offsets)+''.join(records);name='Macro_'+str(start//MP);macro.append('Rez.JsonData.'+name);largest=max(largest,len(text))
  xml.append(f'<jsonData id="{name}">{html.escape(json.dumps(text))}</jsonData>')
 rows={}
 for sy,row in sorted(spatial.items()):
  name='Cell_'+str(sy);rows[sy]='Rez.JsonData.'+name
  data={str(sx):v for sx,v in row.items()}
  xml.append(f'<jsonData id="{name}">{html.escape(json.dumps(data))}</jsonData>')
 xml.append('</resources>');(out/'navigation.xml').write_text('\n'.join(xml))
 code=['import Toybox.Lang;','module NavData {',f'const FINE_N={len(ids)};const FINE_PAGE={FP};const MACRO_N={len(roots)};const MACRO_PAGE={MP};']
 for tag,values in [('fine',fine),('macro',macro)]:
  code.append(f'function {tag}(page) {{var row;switch((page/32).toNumber()){{')
  for i in range(0,len(values),32):code.append(f'case {i//32}:row={tag}{i//32}();break;')
  code.append('default:return null;}return (row as Array)[page%32];}')
  for i in range(0,len(values),32):code.append(f'function {tag}{i//32}(){{return ['+','.join(values[i:i+32])+'];}')
 code+=['function cells(y){switch(y){']
 for sy,val in rows.items():code.append(f'case {sy}:return {val};')
 code+=['}return null;}','}'];(ROOT/'source/NavData.mc').write_text('\n'.join(code))
 stats={'fine_nodes':len(ids),'fine_pages':len(fine),'anchors':len(roots),'macro_pages':len(macro),'undirected_portals':len(portals),'spatial_rows':len(rows),'max_page_characters':largest,'hierarchy_cell_meters':CELL,'geometry_tolerance_meters':6,'algorithm':'multi-source shortest-path forest, connected-cell portal graph, weighted A*, lowest-common-ancestor path expansion','route_quality':'valid connected walking routes; not guaranteed globally shortest','network':'Public pedestrian-permitted road/path/service ways; actual OSM junction IDs; all connected components kept','osm_timestamp':'2026-10-25T21:21:21Z'}
 (ROOT/'data/offline-navigation-stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2));print(json.dumps(stats,ensure_ascii=False),flush=True)
 (ROOT/'data/nav-numbering.pickle').write_bytes(pickle.dumps((ids,number,coords),protocol=4))
if __name__=='__main__':main()
