"""Parallel native builds with isolated compiler output directories (no shared gen/)."""
from pathlib import Path
import os,subprocess,concurrent.futures,shutil,json,argparse,time
from generate import generate,ROOT,DEVICES
p=argparse.ArgumentParser();p.add_argument('mode',choices=['live','preview','tests']);p.add_argument('devices',nargs='*');p.add_argument('--jobs',type=int,default=2);a=p.parse_args()
subprocess.run([os.sys.executable,str(ROOT/'tools/settings.py')],check=True);generate()
sdk=Path((Path.home()/'Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg').read_text().strip());key=Path.home()/'.Garmin/keys/developer_key.der'
env=dict(os.environ,JAVA_HOME='/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
def build(device):
 out=ROOT/'bin/isolated'/a.mode/device;out.mkdir(parents=True,exist_ok=True);prg=out/'Alpine.prg';log=ROOT/f'bin/{device}-{a.mode}-build.log'
 jungle='monkey.jungle' if a.mode=='live' else f'{a.mode}-{device}.jungle'
 cmd=[str(sdk/'bin/monkeyc'),'-f',jungle,'-d',device,'-o',str(prg),'-y',str(key),'-w','--no-gen-styles']+(['-t'] if a.mode=='tests' else ['-r','-O','0'])
 start=time.monotonic()
 with log.open('w') as f:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:print(log.read_text()[-6000:],flush=True)
 else:
  target=ROOT/f'bin/Alpine-{device}-{a.mode}.prg';shutil.copy2(prg,target)
  settings=out/'Alpine-settings.json'
  if settings.exists():shutil.copy2(settings,ROOT/f'bin/Alpine-{device}-{a.mode}-settings.json')
  debug=prg.with_suffix('.prg.debug.xml')
  if debug.exists():shutil.copy2(debug,target.with_suffix('.prg.debug.xml'))
 result={'device':device,'mode':a.mode,'passed':r.returncode==0,'seconds':round(time.monotonic()-start,1)};print(json.dumps(result),flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:results=list(pool.map(build,a.devices or DEVICES))
(ROOT/'dist').mkdir(exist_ok=True);(ROOT/f'dist/build-{a.mode}.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if all(x['passed'] for x in results) else 1)
