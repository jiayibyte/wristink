from pathlib import Path
import json,uuid,subprocess,os
R=Path(__file__).resolve().parents[2]/'moke'
rows={x['id']:x for x in json.loads((R/'config/mip-devices.json').read_text())}
lines=(R/'monkey.jungle').read_text().splitlines()
for device in ['instinct2s','instinct2x','instinct3solar45mm']:
 row=rows[device];folder=R/'bin/phone-final'/device;folder.mkdir(parents=True,exist_ok=True)
 manifest=(R/'manifest.xml').read_text().replace('e4c16f1eb76d4c88a6de6aa791adf801',uuid.uuid4().hex).replace('entry="InstinctFaceApp"','entry="PhoneApp"')
 (folder/'manifest.xml').write_text(manifest)
 get=lambda suffix:next(x.split(' = ')[1] for x in lines if x.startswith(device+suffix))
 paths=lambda v:';'.join(str(R/x) for x in v.split(';'))
 jungle='project.manifest = manifest.xml\nbase.sourcePath = .;'+paths(get('.sourcePath'))+'\nbase.resourcePath = '+paths(get('.resourcePath'))+';'+str(R/'generated/assets'/row['asset_key']/'resources-eng')+'\n'
 if row['renderer']=='legacy' and row['on_watch_settings']:jungle+='base.excludeAnnotations = classicPrefs\n'
 (folder/'phone.jungle').write_text(jungle)
 base='LegacyFace' if row['renderer']=='legacy' else 'InstinctFaceView'
 views='LegacyPower.views(_view)' if row['renderer']=='legacy' else '[_view,new PowerDelegate(_view)]'
 program='''import Toybox.System;import Toybox.Application;
class PhoneApp extends InstinctFaceApp {
 function initialize(){InstinctFaceApp.initialize();}
 function getInitialView(){_view=new PhoneFace();return VIEWS;}
 function onSettingsChanged(){InstinctFaceApp.onSettingsChanged();System.println("PHONE_CHANGED dark="+FacePrefs.flag("darkTheme")+" format="+FacePrefs.get("timeFormat"));}
}
class PhoneFace extends BASE {
 var _report=true;
 function initialize(){BASE.initialize();}
 function invalidate(){BASE.invalidate();_report=true;}
 function onUpdate(dc){BASE.onUpdate(dc);if(_report){_report=false;System.println("PHONE_RENDER dark="+FacePrefs.flag("darkTheme")+" format="+FacePrefs.get("timeFormat")+" free="+System.getSystemStats().freeMemory);}}
}
'''.replace('BASE',base).replace('VIEWS',views)
 # Modern view invalidation has the same production method name.
 (folder/'Phone.mc').write_text(program)
 result=subprocess.run(['monkeyc','-f',str(folder/'phone.jungle'),'-d',device,'-o',str(folder/'Phone.prg'),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-r','-O','3z','-w'],capture_output=True,text=True)
 (folder/'build.log').write_text(result.stdout+result.stderr)
 print(device,'PASS' if result.returncode==0 else result.stdout+result.stderr,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
