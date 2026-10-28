#!/usr/bin/env python3
import math,json,pickle,heapq,xml.etree.ElementTree as E
from pathlib import Path
import networkx as nx
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
def dec(s,i,n):
 v=0
 for c in s[i:i+n]:v=v*64+ord(c)-33
 return v
def main():
 g,coords,owner,parent,dist,roots,portals,components=pickle.loads((ROOT/'data/nav-hierarchy.pickle').read_bytes())
 ids,number,coords=pickle.loads((ROOT/'data/nav-numbering.pickle').read_bytes())
 resources={e.get('id'):json.loads(e.text) for e in E.parse(ROOT/'resources/navigation/navigation.xml').getroot()}
 for page in range((len(ids)+511)//512):
  text=resources[f'Fine_{page}'];n=min(512,len(ids)-page*512)
  for index in range(n):
   begin=n*3+dec(text,index*3,3);end=n*3+dec(text,(index+1)*3,3) if index+1<n else len(text);record=text[begin:end];node=ids[page*512+index]
   assert dec(record,6,4)==number[parent[node]]
   assert dec(record,10,3)==owner[node]
   assert abs(2*dec(record,0,3)-coords[node][0])<=1.01 and abs(2*dec(record,3,3)-coords[node][1])<=1.01
   mode=dec(record,13,1);count=dec(record,14,2);assert len(record)==16+count*(4 if mode==0 else 6)
   if node!=parent[node]:
    assert g.has_edge(node,parent[node]) and dist[parent[node]]<dist[node] and owner[parent[node]]==owner[node]
 macro=nx.Graph()
 for (ra,rb),(weight,a,b) in portals.items():
  assert g.has_edge(a,b) and owner[a]==ra and owner[b]==rb
  macro.add_edge(ra,rb,weight=math.ceil(weight),a=a,b=b)
 def weighted(source,target):
  goal=coords[roots[target]]
  def h(n):return math.dist(coords[roots[n]],goal)
  heap=[(int(2.5*h(source)),0,source)];seen={source:0};prev={source:None};expanded=0
  while heap:
   f,cost,n=heapq.heappop(heap)
   if cost!=seen[n]:continue
   if n==target:
    path=[];p=n
    while p is not None:path.append(p);p=prev[p]
    return path[::-1],expanded,len(seen)
   expanded+=1
   for k,e in macro[n].items():
    d=cost+e['weight']
    if d<seen.get(k,float('inf')):seen[k]=d;prev[k]=n;heapq.heappush(heap,(int(d+2.5*h(k)),d,k))
   if len(seen)>640:return None,expanded,len(seen)
  return None,expanded,len(seen)
 def chain(n):
  result=[n]
  while parent[n]!=n:n=parent[n];result.append(n)
  return result
 def connect(a,b):
  left,right=chain(a),chain(b);i,j=len(left)-1,len(right)-1
  assert left[i]==right[j]
  while i and j and left[i-1]==right[j-1]:i-=1;j-=1
  return left[:i+1]+right[:j][::-1]
 xy=[coords[n] for n in ids];tree=cKDTree(xy)
 def snap(lon,lat):
  x=(lon-115)*111320*math.cos(math.radians(40));y=(lat-39)*111320
  d,i=tree.query((x,y));assert d<=250,(lon,lat,d)
  return ids[i],float(d)
 start,snap_distance=snap(116.3913,39.9075);fixtures=[]
 for name,lon,lat in [('天坛',116.4102,39.8810),('颐和园',116.2735,39.9990),('延庆',115.975,40.457),('密云',116.843,40.377)]:
  target,d=snap(lon,lat);ra,rb=owner[start],owner[target]
  assert components[start]==components[target]
  route,expanded,used=weighted(ra,rb) if ra!=rb else ([ra],0,0)
  assert route is not None,(name,expanded,used)
  path=[];current=start
  for a,b in zip(route,route[1:]):
   _,u,v=portals[(min(a,b),max(a,b))]
   if owner[u]!=a:u,v=v,u
   leg=connect(current,u);path.extend(leg if not path else leg[1:]);path.append(v);current=v
  leg=connect(current,target);path.extend(leg if not path else leg[1:])
  length=0.
  for a,b in zip(path,path[1:]):assert g.has_edge(a,b);length+=g[a][b]['weight']
  shortest=nx.shortest_path_length(g,start,target,weight='weight')
  fixtures.append({'destination':name,'route_meters':round(length),'fine_shortest_meters':round(shortest),'ratio':round(length/shortest,2),'macro_expanded':expanded,'macro_states':used,'connected_fine_edges':len(path)-1,'snap_meters':round(d)})
 search_count=0;matches=[];search_resources={e.get('id'):json.loads(e.text) for e in E.parse(ROOT/'resources/search/search.xml').getroot()}
 for page in range(len(search_resources)-1):
  text=search_resources[f'SearchPage_{page}'];offset=0;previous_name='';previous_py=''
  while offset<len(text):
   size=dec(text,offset,2);line=text[offset+2:offset+2+size-1];offset+=size+2
   namepart,pypart,position=line.split('|');name=previous_name[:ord(namepart[0])-33]+namepart[1:];py=previous_py[:ord(pypart[0])-33]+pypart[1:]
   assert name and py and len(position)==6
   previous_name,previous_py=name,py;search_count+=1
   if py.startswith('tiantan'):matches.append(name)
  assert offset==len(text)
 assert any('天坛' in name for name in matches)
 result={'passed':True,'fine_nodes_verified':len(ids),'portal_edges_verified':len(portals),'search_records_verified':search_count,'search_tiantan_samples':matches[:15],'route_fixtures':fixtures,'limitations':'Routes follow stored OSM connectivity but are not guaranteed shortest; nearest graph node within 250m required.'}
 (ROOT/'dist/offline-navigation-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
