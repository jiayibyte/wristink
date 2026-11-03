from pathlib import Path
import os, subprocess, json
R=Path(__file__).resolve().parents[1]
sdk=Path((Path.home()/'Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg').read_text().strip())
env=dict(os.environ,JAVA_HOME='/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
results=[]
for device in ['instinct2s','instinct3solar45mm','epix2']:
 p=subprocess.run([str(sdk/'bin/monkeydo'),str(R/f'bin/Alpine-{device}-tests.prg'),device,'-t'],env=env,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60,text=True)
 (R/f'dist/evidence/{device}-tests.log').write_text(p.stdout)
 print(device,p.returncode,p.stdout[-2600:],flush=True)
 ok='PASSED (passed=' in p.stdout and 'FAILED' not in p.stdout
 results.append({'device':device,'passed':ok,'returncode':p.returncode})
 if not ok:break
(R/'dist/evidence/tests.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
