"""Fail the release if any device binary exceeds the user's 100,000-byte cap."""
from pathlib import Path
import argparse,subprocess,tempfile,xml.etree.ElementTree as ET,json,hashlib
p=argparse.ArgumentParser();p.add_argument('package');p.add_argument('--limit',type=int,default=100000);a=p.parse_args();package=Path(a.package).resolve()
with tempfile.TemporaryDirectory(prefix='alpine-size-') as tmp:
 subprocess.run(['7zz','x','-y','-o'+tmp,str(package)],check=True,capture_output=True)
 root=ET.parse(Path(tmp)/'manifest.xml').getroot();rows=[]
 for item in root.iter():
  if 'filename' in item.attrib:
   file=Path(tmp)/item.attrib['filename']
   if file.suffix.lower()=='.prg':rows.append({'hardware':item.get('partNumber'),'bytes':file.stat().st_size})
 if not rows:
  rows=[{'hardware':str(f.relative_to(tmp)),'bytes':f.stat().st_size} for f in Path(tmp).rglob('*.prg')]
 assert rows,'No device binaries found'
 report={'package':str(package),'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'limit_bytes':a.limit,'variants':len(rows),'minimum_bytes':min(r['bytes'] for r in rows),'maximum_bytes':max(r['bytes'] for r in rows),'passed':all(r['bytes']<a.limit for r in rows),'devices':rows}
 print(json.dumps(report,indent=2));assert report['passed'],'A device binary exceeds the size cap'
