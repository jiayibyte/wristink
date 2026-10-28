"""Run Garmin's official simulator launcher, retaining per-target evidence."""
from pathlib import Path
import argparse,os,subprocess,time,signal,json,re,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];SDK=Path.home()/'Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2'
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['perf','test'],default='perf');p.add_argument('--devices',nargs='+',required=True);p.add_argument('--timeout',type=int,default=45);a=p.parse_args()
env=dict(os.environ,JAVA_HOME='/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
folder=ROOT/'bin/probes'/a.mode;folder.mkdir(parents=True,exist_ok=True);results=[]
for id in a.devices:
 prg=ROOT/'bin/matrix'/a.mode/id/'RetroWorld.prg';build=prg.parent/'build.log'
 assert prg.exists() and 'BUILD SUCCESSFUL' in build.read_text() and 'ERROR:' not in build.read_text(),id
 digest=hashlib.sha256(prg.read_bytes()).hexdigest()
 launched=folder/(id+'-'+digest[:8]+'.prg');shutil.copy2(prg,launched)
 if prg.with_suffix('.prg.debug.xml').exists():shutil.copy2(prg.with_suffix('.prg.debug.xml'),launched.with_suffix('.prg.debug.xml'))
 path=folder/(id+'.log');cmd=[str(SDK/'bin/monkeydo'),str(prg),id]+(['-t'] if a.mode=='test' else [])
 with path.open('w') as log:
  proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);deadline=time.monotonic()+a.timeout
  while time.monotonic()<deadline:
   text=path.read_text();done='PERF_READY' in text if a.mode=='perf' else 'PASSED (passed=' in text
   if done or 'app crash' in text or 'FAILED (' in text or proc.poll() is not None:break
   time.sleep(.25)
  text=path.read_text();passed=('PERF_RESULT' in text and 'PERF_READY' in text if a.mode=='perf' else 'PASSED (passed=' in text) and not any(t in text.lower() for t in ('app crash','error:','failed ('))
  if passed:
   try:proc.wait(8)
   except subprocess.TimeoutExpired:pass
  if proc.poll() is None:
   os.killpg(proc.pid,signal.SIGINT)
   try:proc.wait(3)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM)
  result={'device':id,'passed':passed,'mode':a.mode,'log':str(path),'prg_sha256':digest}
  if a.mode=='perf' and passed:
   line=next(l for l in text.splitlines() if l.startswith('PERF_RESULT'))
   result['measurements']={k:(v=='true' if v in ('true','false') else float(v) if '.' in v and k!='version' else int(v) if v.isdigit() else v) for k,v in re.findall(r'(\w+)=([^ ]+)',line)}
  results.append(result);print(id,'PASS' if passed else text[-900:] or 'TIMEOUT',flush=True)
  if not passed:break
report=ROOT/f'dist/native-{a.mode}.json'
previous=json.loads(report.read_text()) if report.exists() else []
replace={r['device']:r for r in previous};replace.update({r['device']:r for r in results});report.write_text(json.dumps(list(replace.values()),indent=2)+'\n')
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
