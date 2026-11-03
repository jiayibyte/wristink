from pathlib import Path
import os, subprocess, json, argparse, re, hashlib
R=Path(__file__).resolve().parents[1]
sdk=Path((Path.home()/'Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg').read_text().strip())
env=dict(os.environ,JAVA_HOME='/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
parser=argparse.ArgumentParser();parser.add_argument("--devices",nargs="+",default=["instinct2s","instinct3solar45mm","epix2"]);args=parser.parse_args()
results=[]
for device in args.devices:
 p=subprocess.run([str(sdk/'bin/monkeydo'),str(R/f'bin/Alpine-{device}-tests.prg'),device,'-t'],env=env,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60,text=True)
 (R/f'dist/evidence/{device}-tests.log').write_text(p.stdout)
 print(device,p.returncode,p.stdout[-2600:],flush=True)
 ok='PASSED (passed=' in p.stdout and 'FAILED' not in p.stdout
 results.append({'device':device,'passed':ok,'returncode':p.returncode,'tests':int(re.search(r'PASSED \(passed=(\d+)',p.stdout)[1]) if ok else 0,'sha256':hashlib.sha256((R/f'bin/Alpine-{device}-tests.prg').read_bytes()).hexdigest()})
 if not ok:break
prior=json.loads((R/'dist/evidence/tests.json').read_text()) if (R/'dist/evidence/tests.json').exists() else []
by_device={x['device']:x for x in prior};by_device.update({x['device']:x for x in results})
(R/'dist/evidence/tests.json').write_text(json.dumps(list(by_device.values()),indent=2)+'\n')
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
