#!/usr/bin/env python3
import osmium,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
class Roads(osmium.SimpleHandler):
 def __init__(self):super().__init__();self.ways=[]
 def way(self,w):
  if 'highway' not in w.tags:return
  tags=dict(w.tags)
  if tags.get('access')=='private':return
  try:geo=[dict(lon=n.lon,lat=n.lat) for n in w.nodes]
  except osmium.InvalidLocationError:return
  self.ways.append(dict(type='way',id=w.id,tags=tags,geometry=geo))
h=Roads();h.apply_file(str(Path(sys.argv[1]) if len(sys.argv)>1 else root/'data/beijing-full.osm.pbf'),locations=True)
reader=osmium.io.Reader(str(Path(sys.argv[1]) if len(sys.argv)>1 else root/'data/beijing-full.osm.pbf')); timestamp=reader.header().get('osmosis_replication_timestamp');reader.close()
(root/'data/beijing-osm.json').write_text(json.dumps(dict(elements=h.ways,osm3s={'timestamp_osm_base':timestamp})))
print(len(h.ways))
