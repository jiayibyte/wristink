"""Parallel native builds with isolated compiler output directories (no shared gen/)."""
from pathlib import Path
import sys; sys.path.append(str(Path(__file__).resolve().parents[2]/'tools')); import ciq_env
import os,subprocess,concurrent.futures,shutil,json,argparse,time,xml.etree.ElementTree as ET
from generate import generate,ROOT,DEVICES
p=argparse.ArgumentParser();p.add_argument('mode',choices=['live','preview','tests']);p.add_argument('devices',nargs='*');p.add_argument('--jobs',type=int,default=2);p.add_argument('--skip-generate',action='store_true');p.add_argument('--typecheck',type=int,choices=[0,1,2,3],default=1);a=p.parse_args()
if not a.skip_generate:
 subprocess.run([os.sys.executable,str(ROOT/'tools/settings.py')],check=True);generate()
sdk=ciq_env.sdk();key=Path.home()/'.Garmin/keys/developer_key.der'
env=ciq_env.java_env()
def build(device):
 out=ROOT/'bin/isolated'/a.mode/device;out.mkdir(parents=True,exist_ok=True);prg=out/'Alpine.prg';log=ROOT/f'bin/{device}-{a.mode}-build.log'
 ns='http://www.garmin.com/xml/connectiq';ET.register_namespace('iq',ns)
 tree=ET.parse(ROOT/('manifest.xml' if a.mode=='live' else f'generated/{device}/{a.mode}-manifest.xml'))
 products=tree.getroot().find('{'+ns+'}application/{'+ns+'}products')
 for product in list(products):
  if product.get('id')!=device:products.remove(product)
 tree.write(out/'manifest.xml',encoding='utf-8')
 source=[ROOT/'source',ROOT/('preview' if a.mode=='preview' else 'live'),ROOT/'generated'/device]
 if a.mode=='tests':source.append(ROOT/'tests')
 resources=[ROOT/'resources',ROOT/'generated'/device/'resources'];chinese=[ROOT/'resources-zhs']
 if a.mode=='preview':resources.append(ROOT/'preview/resources');chinese.append(ROOT/'preview/resources-zhs')
 jungle=out/'target.jungle'
 jungle.write_text('project.manifest = manifest.xml\nbase.sourcePath = '+';'.join(map(str,source))+'\nbase.resourcePath = '+';'.join(map(str,resources))+'\nbase.lang.zhs = '+';'.join(map(str,chinese))+'\n')
 # Legacy Instinct bytecode lives in the same 60 KB pool as bitmap resources.
 # Fast code-space optimisation keeps the complete face and menus in budget.
 opt='2z' if device in ['instinct2','instinct2s','instinct2x'] else '0'
 flags=(['-t','-O',opt] if opt=='2z' else ['-t']) if a.mode=='tests' else ['-r','-O',opt]
 # Keep runtime API guards for regional firmware below the default SDK device API.
 compat=['--disable-api-has-check-removal']
 cmd=[str(sdk/'bin/monkeyc'),'-f',str(jungle),'-d',device,'-o',str(prg),'-y',str(key),'-w','--no-gen-styles','-l',str(a.typecheck)]+flags+compat
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
