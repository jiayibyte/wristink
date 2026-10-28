#!/usr/bin/env python3
"""Prepare offline pedestrian graph and Chinese/pinyin search from OSM PBF.
All graph junctions are OSM node IDs; geometric crossings are never connected.
"""
import osmium, math, json, pickle, collections, time
from pathlib import Path
import networkx as nx
ROOT=Path(__file__).resolve().parents[1]
XDEG=111320*math.cos(math.radians(40));YDEG=111320
WALK={'primary','secondary','tertiary','residential','unclassified','living_street','pedestrian','footway','path','track','steps','service','primary_link','secondary_link','tertiary_link','bridleway'}
def xy(lon,lat):return ((lon-115)*XDEG,(lat-39)*YDEG)
def allowed(tags):
 if tags.get('highway') not in WALK:return False
 foot=tags.get('foot');access=tags.get('access')
 if foot in {'no','private','use_sidepath'}:return False
 if access in {'no','private'} and foot not in {'yes','designated','permissive'}:return False
 return True
class Read(osmium.SimpleHandler):
 def __init__(self):super().__init__();self.g=nx.Graph();self.pois=[];self.forward_only=set();self.names=[]
 def node(self,n):
  t=dict(n.tags);name=t.get('name:zh') or t.get('name')
  street=t.get('addr:street');number=t.get('addr:housenumber')
  if street and number:name=(street+number+'号') if not name else name+' '+street+number
  if not name or len(name)>36:return
  if not any(k in t for k in ['amenity','tourism','shop','leisure','place','railway','public_transport','addr:housenumber']):return
  x,y=xy(n.location.lon,n.location.lat);self.pois.append((name,x,y,'地点'))
 def way(self,w):
  t=dict(w.tags);name=t.get('name:zh') or t.get('name')
  if not allowed(t):return
  try:pts=[(n.ref,*xy(n.lon,n.lat)) for n in w.nodes]
  except osmium.InvalidLocationError:return
  if name and len(name)<=36 and pts:
   p=pts[len(pts)//2];self.pois.append((name,p[1],p[2],'道路'))
  direct=t.get('oneway:foot')
  for a,b in zip(pts,pts[1:]):
   if a[0]==b[0]:continue
   d=math.hypot(a[1]-b[1],a[2]-b[2]);
   if d<0.1:continue
   self.g.add_node(a[0],x=a[1],y=a[2]);self.g.add_node(b[0],x=b[1],y=b[2])
   self.g.add_edge(a[0],b[0],weight=d)
   if direct in {'yes','1','true'}:self.forward_only.add((b[0],a[0]))
   if direct=='-1':self.forward_only.add((a[0],b[0]))

def main():
 cache=ROOT/'data/nav-raw.pickle'
 if cache.exists():
  g,pois,blocked=pickle.loads(cache.read_bytes())
 else:
  r=Read();r.apply_file(str(ROOT/'data/beijing-full.osm.pbf'),locations=True)
  g,pois,blocked=r.g,r.pois,r.forward_only;cache.write_bytes(pickle.dumps((g,pois,blocked),protocol=4))
 print('Raw',len(g),g.number_of_edges(),'POIs',len(pois),'directed restrictions',len(blocked),flush=True)
 # Preserve real junctions/endpoints and explicit pedestrian direction restrictions.
 keep={n for n in g if g.degree(n)!=2};keep.update(n for edge in blocked for n in edge)
 for component in nx.connected_components(g):
  if not (keep & component):keep.add(next(iter(component)))
 # Add anchors along chains so a snap point is never kilometres from a long road.
 visited=set();edges=[];todo=list(keep)
 for start in todo:
  for nxt in g[start]:
   if (start,nxt) in visited:continue
   path=[start];prev=start;cur=nxt;dist=0.0;segstart=start
   while True:
    visited.add((prev,cur));visited.add((cur,prev));dist+=g[prev][cur]['weight'];path.append(cur)
    finish=cur in keep
    if finish or dist>=220 or len(path)>=28:
     edges.append((segstart,cur,dist,path[:]))
     if not finish:keep.add(cur);todo.append(cur)
     segstart=cur;path=[cur];dist=0
    if finish:break
    neighbors=list(g[cur]);after=neighbors[0] if neighbors[1]==prev else neighbors[1]
    prev,cur=cur,after
 # Avoid duplicate segments introduced when an anchor becomes a later traversal start.
 compact=nx.MultiDiGraph();nodes={n:(g.nodes[n]['x'],g.nodes[n]['y']) for n in keep}
 seen=set()
 for a,b,w,path in edges:
  if len(path)<2:continue
  key=(min(a,b),max(a,b),tuple(sorted((path[0],path[1]))))
  if key in seen:continue
  seen.add(key)
  coords=[(g.nodes[n]['x'],g.nodes[n]['y']) for n in path]
  if not any((u,v) in blocked for u,v in zip(path,path[1:])):compact.add_edge(a,b,weight=w,geometry=coords)
  if not any((v,u) in blocked for u,v in zip(path,path[1:])):compact.add_edge(b,a,weight=w,geometry=coords[::-1])
 components=sorted(nx.weakly_connected_components(compact),key=len,reverse=True)
 stats={'raw_nodes':len(g),'raw_edges':g.number_of_edges(),'routing_nodes':len(compact),'routing_edges':compact.number_of_edges(),'largest_components':[len(c) for c in components[:15]],'poi_candidates':len(pois),'foot_direction_restrictions':len(blocked)}
 (ROOT/'data/navigation-stats.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2),flush=True)
 (ROOT/'data/nav-compact.pickle').write_bytes(pickle.dumps((compact,nodes,pois),protocol=4))
if __name__=='__main__':main()
