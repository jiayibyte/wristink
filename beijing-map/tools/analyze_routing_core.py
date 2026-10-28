import pickle,collections,json,math
from pathlib import Path
import networkx as nx
r=Path(__file__).resolve().parents[1]
g,nodes,pois=pickle.loads((r/'data/nav-compact.pickle').read_bytes());u=nx.Graph(g);u.remove_edges_from(list(nx.selfloop_edges(u)))
queue=collections.deque(n for n in u if u.degree(n)<2)
while queue:
 n=queue.popleft()
 if n not in u:continue
 neighbors=list(u[n]);u.remove_node(n)
 for k in neighbors:
  if k in u and u.degree(k)<2:queue.append(k)
print('core before recontract',len(u),u.number_of_edges(),flush=True)
keep={n for n in u if u.degree(n)!=2}
for c in nx.connected_components(u):
 if not keep.intersection(c):keep.add(next(iter(c)))
seen=set();todo=list(keep);out=nx.Graph()
for a in todo:
 for b in list(u[a]):
  if (a,b) in seen:continue
  start=a;prev=a;cur=b;length=0;geom=[]
  while True:
   seen.add((prev,cur));seen.add((cur,prev));edge=min(g.get_edge_data(prev,cur).values(),key=lambda v:v['weight']);length+=edge['weight'];geom+=edge['geometry'] if not geom else edge['geometry'][1:]
   finish=cur in keep
   if finish or length>=220:
    if out.has_edge(start,cur):
     if out[start][cur]['weight']>length:out[start][cur].update(weight=length,geometry=geom[:])
    else:out.add_edge(start,cur,weight=length,geometry=geom[:])
    if not finish:keep.add(cur);todo.append(cur)
    start=cur;length=0;geom=[]
   if finish:break
   after=next(k for k in u[cur] if k!=prev);prev,cur=cur,after
print('core after recontract',len(out),out.number_of_edges(),flush=True)
cs=sorted(nx.connected_components(out),key=len,reverse=True);print('largest',[len(c) for c in cs[:8]],flush=True)
(r/'data/nav-core.pickle').write_bytes(pickle.dumps((out,{n:nodes[n] for n in out},pois),protocol=4))
