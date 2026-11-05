"""Build an isolated simulator scenario using the unmodified production source."""
from pathlib import Path
import argparse,json,os,subprocess,uuid,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--device',default='instinct3solar45mm');p.add_argument('--name',required=True);p.add_argument('--settings',default='{}');p.add_argument('--refresh-probe',action='store_true',help='Log real OS partial callbacks and budget violations; simulator only');a=p.parse_args()
values=json.loads(a.settings);folder=ROOT/'bin/scenarios'/a.name;folder.mkdir(parents=True,exist_ok=True)
ns='http://www.garmin.com/xml/connectiq';ET.register_namespace('iq',ns)
tree=ET.parse(ROOT/'manifest.xml');app=tree.getroot().find('{'+ns+'}application');app.set('entry','ScenarioApp');app.set('id',uuid.uuid5(uuid.NAMESPACE_URL,'wristink-scenario/'+a.name).hex)
tree.write(folder/'manifest.xml',encoding='utf-8')
body=''.join('Application.Properties.setValue('+json.dumps(k)+','+json.dumps(v)+');' for k,v in values.items())
initial='function getInitialView(){var view=new RefreshProbeView();return [view,new RefreshProbeDelegate(view)];}' if a.refresh_probe else ''
probe='''
import Toybox.System;
import Toybox.Time;
class RefreshProbeDelegate extends RetroWorldDelegate {
    function initialize(view) {RetroWorldDelegate.initialize(view);}
    function onPowerBudgetExceeded(info) {
        System.println("REFRESH_BUDGET average_ms="+info.executionTimeAverage+" limit_ms="+info.executionTimeLimit);
        RetroWorldDelegate.onPowerBudgetExceeded(info);
    }
}
class RefreshProbeView extends RetroWorldView {
    var calls=0;var digits=0;var needles=0;var lastReport=-1;var start=-1;
    function initialize() {RetroWorldView.initialize();}
    function onEnterSleep() {RetroWorldView.onEnterSleep();System.println("REFRESH_SLEEP");}
    function onExitSleep() {RetroWorldView.onExitSleep();System.println("REFRESH_WAKE");}
    function onPartialUpdate(dc) {
        calls++;var digit=_lastSecond;var needle=_oldSecond;
        RetroWorldView.onPartialUpdate(dc);
        if(digit!=_lastSecond) {digits++;}if(needle!=_oldSecond) {needles++;}
    }
    function onUpdate(dc) {
        RetroWorldView.onUpdate(dc);var now=Time.now().value();if(start<0) {start=now;}
        if(lastReport<0 || now-lastReport>=60) {
            System.println("REFRESH_FRAME elapsed="+(now-start)+" asleep="+_sleeping+" calls="+calls+" digits="+digits+" needles="+needles+" second="+_visibleSecond+" blocked="+_partialBlocked);
            lastReport=now;
        }
    }
}
''' if a.refresh_probe else ''
(folder/'ScenarioApp.mc').write_text('import Toybox.Application;\nclass ScenarioApp extends RetroWorldApp {function initialize(){RetroWorldApp.initialize();}function onStart(state){'+body+'}'+initial+'}\n'+probe)
lines=(ROOT/'monkey.jungle').read_text().splitlines()
source=next(l.split(' = ')[1] for l in lines if l.startswith(a.device+'.sourcePath'))
resources=next(l.split(' = ')[1] for l in lines if l.startswith(a.device+'.resourcePath'))
absolute=lambda paths:';'.join(str(ROOT/part) for part in paths.split(';'))
(folder/'scenario.jungle').write_text('project.manifest = manifest.xml\nbase.excludeAnnotations = diagnostic\nbase.sourcePath = .;'+absolute(source)+'\nbase.resourcePath = '+absolute(resources)+'\nbase.lang.zhs = '+str(ROOT/'resources-zhs')+'\n')
sdk=Path((Path.home()/'Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg').read_text().strip())
env=dict(os.environ,JAVA_HOME='/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
cmd=[str(sdk/'bin/monkeyc'),'-f',str(folder/'scenario.jungle'),'-d',a.device,'-o',str(folder/'Scenario.prg'),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-r','-O','3z','-w']
r=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True);(folder/'build.log').write_text(r.stdout+r.stderr);print(r.stdout[-1500:]);raise SystemExit(r.returncode)
