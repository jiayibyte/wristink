#!/usr/bin/env python3
"""Use Garmin's supported extended-code annotation for cold/nav code.
Generated registries contain thousands of references; paging their methods keeps
the app heap available for map, recording and offline query data.
"""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
hot={
 'BeijingMapApp.mc':{'onUpdate','onPosition','drawChunk','decode','min','max','drawTrail','tick','statusTick'},
 'TrailRecorder.mc':{'addFix','get24','put24','point'},
 'OfflineRouting.mc':{'number','get24','put24','point','draw','remaining'},
}
for p in (ROOT/'source').glob('*.mc'):
 s=p.read_text();s=re.sub(r'(?m)^\s*\(:extendedCode\)\s*\n','',s)
 def mark(m):
  indent,name=m.group(1),m.group(2)
  return indent+('' if name in hot.get(p.name,set()) else '(:extendedCode)\n'+indent)+'function '+name+'('
 s=re.sub(r'(?m)^(\s*)function\s+(\w+)\(',mark,s)
 p.write_text(s)
