"""Compile each supported target in its own build directory; retain every result."""
from pathlib import Path
import argparse,concurrent.futures,json,subprocess,time,os
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--demo',action='store_true');p.add_argument('--only',nargs='*');p.add_argument('--workers',type=int,default=1);a=p.parse_args()
rows=json.loads((ROOT/'config/mip-devices.json').read_text());rows=[r for r in rows if not a.only or r['id'] in a.only]
def build(row):
 d=row['id'];folder=ROOT/'bin/mip'/d;folder.mkdir(parents=True,exist_ok=True);name='demo' if a.demo else d
 start=time.time();proc=subprocess.run(['monkeyc','-f','preview.jungle' if a.demo else 'monkey.jungle','-d',d,'-o',str(folder/(name+'.prg')),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-r','--build-stats','0','-w'],cwd=ROOT,capture_output=True,text=True)
 log=proc.stdout+proc.stderr;(folder/(name+'.log')).write_text(log)
 r={'id':d,'name':row['name'],'success':proc.returncode==0,'seconds':round(time.time()-start,2),'memory_limit':row['memory'],'renderer':row['renderer'],'log':str(folder/(name+'.log'))};print(d, 'PASS' if r['success'] else 'FAIL',flush=True);return r
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:results=list(pool.map(build,rows))
file=ROOT/'bin'/('mip-demo-builds.json' if a.demo else 'mip-builds.json');file.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print(f"{sum(r['success'] for r in results)}/{len(results)} passed",flush=True)
raise SystemExit(0 if all(r['success'] for r in results) else 1)
