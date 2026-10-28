"""Bounded parallel native compiles; fail the release on any listed target error."""
from pathlib import Path
import concurrent.futures,json,os,subprocess,argparse,time
ROOT=Path(__file__).resolve().parents[1]
SDK=Path.home()/'Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2'
args=argparse.ArgumentParser();args.add_argument('--mode',choices=['live','demo','perf','test'],default='live');args.add_argument('--devices',nargs='*');args.add_argument('--jobs',type=int,default=2);a=args.parse_args()
rows=json.loads((ROOT/'dist/device-matrix.json').read_text())['devices'];ids=a.devices or [r['id'] for r in rows]
env=dict(os.environ,JAVA_HOME='/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
folder=ROOT/'bin/matrix'/a.mode;folder.mkdir(parents=True,exist_ok=True)
def build(id):
    out=folder/id;out.mkdir(exist_ok=True);start=time.monotonic()
    cmd=[str(SDK/'bin/monkeyc'),'-f',{'live':'monkey.jungle','demo':'preview.jungle','perf':'diagnostic.jungle','test':'tests.jungle'}[a.mode],'-d',id,'-o',str(out/'RetroWorld.prg'),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-w']
    cmd+=['-t'] if a.mode=='test' else ['-r','-O','3z']
    result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    (out/'build.log').write_text(result.stdout)
    data={'device':id,'passed':result.returncode==0 and 'BUILD SUCCESSFUL' in result.stdout,'seconds':round(time.monotonic()-start,2),'log':str(out/'build.log'),'prg':str(out/'RetroWorld.prg')}
    print(id,'PASS' if data['passed'] else result.stdout[-1500:],flush=True);return data
with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:results=list(pool.map(build,ids))
report=ROOT/f'dist/build-matrix-{a.mode}.json'
previous=json.loads(report.read_text()) if report.exists() else []
merged={r['device']:r for r in previous};merged.update({r['device']:r for r in results})
report.write_text(json.dumps(list(merged.values()),indent=2)+'\n')
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
