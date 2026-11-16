"""Build a few immutable visual fixtures with separate app IDs and compiler folders."""
from pathlib import Path
import os,json,datetime,uuid,subprocess,concurrent.futures,shutil,time
from generate import ROOT,generate
CASES=[('sunrise','2026-06-21T04:50:00+08:00',1),('fullmoon','2026-10-26T23:00:00+08:00',1),('snow','2026-12-21T12:00:00+08:00',5)]
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--cases',nargs='+');parser.add_argument('--device',default='epix2',choices=['epix2','instinct2s','instinct3solar45mm']);args=parser.parse_args()
if args.cases:CASES=[x for x in CASES if x[0] in args.cases]
subprocess.run([os.sys.executable,str(ROOT/'tools/settings.py')],check=True);generate()
sdk=Path((Path.home()/'Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg').read_text().strip())
env=dict(os.environ,JAVA_HOME='/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
def build(case):
 name,when,weather=case;at=datetime.datetime.fromisoformat(when);src=ROOT/'generated/samples'/f'{args.device}-{name}';src.mkdir(parents=True,exist_ok=True);out=ROOT/'bin/sky-samples'/f'{args.device}-{name}';out.mkdir(parents=True,exist_ok=True)
 (src/'Mode.mc').write_text(f'import Toybox.Lang;\nmodule Mode {{const DEMO=true;const SCENE=0;const STAMP={int(at.timestamp())};const MINUTES={at.hour*60+at.minute};const WEATHER={weather};const LAT=39.9d;const LON=116.4d;const DATE="{at.strftime("%a %m/%d").upper()}";function refresh() {{}}}}\n')
 (src/'manifest.xml').write_text((ROOT/'manifest.xml').read_text().replace('bb71078cce15417aa5425aa350817001',uuid.uuid5(uuid.NAMESPACE_DNS,'wristink.alpine.sky-fixture3.'+args.device+'.'+name).hex))
 j=ROOT/f'scenario-{args.device}-{name}.jungle';rel=src.relative_to(ROOT)
 j.write_text((ROOT/'monkey.jungle').read_text().replace('project.manifest = manifest.xml',f'project.manifest = {rel}/manifest.xml').replace('base.sourcePath = source;live',f'base.sourcePath = source;{rel}'))
 start=time.monotonic()
 with (out/'build.log').open('w') as log:r=subprocess.run([str(sdk/'bin/monkeyc'),'-f',str(j),'-d',args.device,'-o',str(out/'Alpine.prg'),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-r','-O','0','-w','--no-gen-styles'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 result={'name':name,'passed':r.returncode==0,'seconds':round(time.monotonic()-start,1),'stamp':int(at.timestamp()),'weather':weather}
 print(json.dumps(result),flush=True)
 if r.returncode:print((out/'build.log').read_text()[-3000:],flush=True)
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(build,CASES))
(ROOT/f'dist/sky-samples-{args.device}.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if all(x['passed'] for x in results) else 1)
