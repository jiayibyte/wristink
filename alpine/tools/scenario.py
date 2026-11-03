"""Build a fixture-only scene under an isolated app ID, without editing live sources."""
from pathlib import Path
import argparse, os, subprocess, uuid
from generate import generate, ROOT, DEVICES
p=argparse.ArgumentParser();p.add_argument('device',choices=DEVICES);p.add_argument('scene',type=int,choices=range(1,10));a=p.parse_args()
generate();dest=ROOT/'generated/scenarios'/f'{a.device}-{a.scene}';dest.mkdir(parents=True,exist_ok=True)
(dest/'Mode.mc').write_text(f'module Mode {{const DEMO=true;const SCENE={a.scene};}}\n')
manifest=(ROOT/'manifest.xml').read_text().replace('bb71078cce15417aa5425aa350817001',uuid.uuid5(uuid.NAMESPACE_DNS,f'wristink.alpine.detail6.{a.device}.{a.scene}').hex)
(dest/'manifest.xml').write_text(manifest)
rel=dest.relative_to(ROOT)
jungle=(ROOT/'monkey.jungle').read_text().replace('project.manifest = manifest.xml',f'project.manifest = {rel}/manifest.xml').replace('base.sourcePath = source;live',f'base.sourcePath = source;{rel}')
# Jungle relative paths resolve against the jungle itself, so retain it at project root.
j=ROOT/'scenario.jungle';j.write_text(jungle)
sdk=Path((Path.home()/'Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg').read_text().strip())
env=dict(os.environ,JAVA_HOME='/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
subprocess.run([str(sdk/'bin/monkeyc'),'-f',str(j),'-d',a.device,'-o',str(ROOT/f'bin/Alpine-{a.device}-scene{a.scene}.prg'),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-r','-O','0','-w'],cwd=ROOT,env=env,check=True)
