"""Native menu-resource recovery + cross-process background persistence probe.
Uses a separate test application ID and restores its own properties after pass 2.
"""
from pathlib import Path
import sys; sys.path.append(str(Path(__file__).resolve().parents[2]/'tools')); import ciq_env
import argparse,hashlib,json,os,subprocess,uuid
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('device');p.add_argument('--typecheck',type=int,choices=[0,1,2,3],default=1);a=p.parse_args()
folder=ROOT/'generated/recovery'/a.device;folder.mkdir(parents=True,exist_ok=True)
(folder/'RecoveryProbe.mc').write_text('''import Toybox.Application;
import Toybox.Graphics;
import Toybox.Test;
import Toybox.System;
import Toybox.Time;
(:test)
function restoreFaceAndPersistAcrossRestart(logger) {
 Settings.load();var old=Application.Storage.getValue("RecoveryProbeRestore");
 var second=old!=null;
 if(second) {
  Test.assertEqual(Settings.scene,13);Test.assertEqual(Settings.skyDecor,3);Test.assertEqual(Settings.weatherLink,1);
 } else {
  Application.Storage.setValue("RecoveryProbeRestore",[Settings.scene,Settings.skyDecor,Settings.weatherLink]);
  Test.assert(Settings.setChoice("Scene",13));Test.assert(Settings.setChoice("SkyDecor",3));Test.assert(Settings.setChoice("WeatherLink",1));
 }
 var ref=null;var bitmap;
 if(Graphics has :createBufferedBitmap) {ref=Graphics.createBufferedBitmap({:width=>1,:height=>1});bitmap=ref.get();}
 else {bitmap=new Graphics.BufferedBitmap({:width=>1,:height=>1});}
 var view=new AlpineView();view.releaseFaceResources();
 view.onUpdate(bitmap.getDc());
 Test.assert(view._time!=null && view._background!=null);
 Test.assert(view._artScene>=101 && view._artScene<=120);
 view.releaseFaceResources();view=null;bitmap=null;ref=null;
 if(second) {
  Settings.setChoice("Scene",old[0]);Settings.setChoice("SkyDecor",old[1]);Settings.setChoice("WeatherLink",old[2]);
  Application.Storage.deleteValue("RecoveryProbeRestore");System.println("RECOVERY_PROBE=reloaded_and_restored");
 } else {System.println("RECOVERY_PROBE=saved_for_restart");}
 return true;
}
''')
ident=uuid.uuid5(uuid.NAMESPACE_DNS,f'wristink.alpine.sky-recovery1.{a.device}').hex
(folder/'manifest.xml').write_text((ROOT/'tests/manifest.xml').read_text().replace('bb71078cce15417aa5425aa350817003',ident))
rel=folder.relative_to(ROOT)
jungle=(ROOT/'monkey.jungle').read_text().replace('project.manifest = manifest.xml',f'project.manifest = {rel}/manifest.xml').replace('base.sourcePath = source;live',f'base.sourcePath = source;live;{rel}')
jf=ROOT/f'scenario-recovery-{a.device}.jungle';jf.write_text(jungle)
sdk=ciq_env.sdk()
env=ciq_env.java_env()
out=ROOT/'bin/recovery'/a.device;out.mkdir(parents=True,exist_ok=True);prg=out/'Alpine.prg'
flags=['-O','2z','--disable-api-has-check-removal'] if a.device=='instinct2s' else []
with (out/'build.log').open('w') as log:
 subprocess.run([str(sdk/'bin/monkeyc'),'-f',str(jf),'-d',a.device,'-o',str(prg),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-t','-w','--no-gen-styles','-l',str(a.typecheck)]+flags,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
print('Native recovery probe compiled',flush=True)
records=[]
for phase,expected in [(1,'saved_for_restart'),(2,'reloaded_and_restored')]:
 run=subprocess.run([str(sdk/'bin/monkeydo'),str(prg),a.device,'-t'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
 path=ROOT/f'dist/evidence/recovery-{a.device}-phase{phase}.log';path.write_text(run.stdout)
 passed='PASSED (passed=1, failed=0, errors=0)' in run.stdout and 'RECOVERY_PROBE='+expected in run.stdout
 records.append({'phase':phase,'passed':passed,'returncode':run.returncode})
 print(json.dumps(records[-1]),flush=True)
 if not passed:raise RuntimeError(run.stdout)
(ROOT/f'dist/evidence/recovery-{a.device}.json').write_text(json.dumps({'device':a.device,'sha256':hashlib.sha256(prg.read_bytes()).hexdigest(),'phases':records},indent=2)+'\n')
