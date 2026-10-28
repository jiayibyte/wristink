"""Run isolated, instrumented SDK simulator variants; keep native rendering logs.
This checks runtime rendering and memory only. It does not replace visual inspection.
"""
from pathlib import Path
import argparse,json,uuid,subprocess,time,os,signal,select,re
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('devices',nargs='+');p.add_argument('--profile',default='default');p.add_argument('--build-only',action='store_true');p.add_argument('--seconds',type=int,default=18);p.add_argument('--locale',choices=['zhs','eng'],default='zhs');a=p.parse_args();config={}
if a.profile!='default':
 import runpy
 config=runpy.run_path(str(R/'scripts/build-config-fixture.py'))['PROFILES'][a.profile]
rows={r['id']:r for r in json.loads((R/'config/mip-devices.json').read_text())};results=[]
for device in a.devices:
 row=rows[device];folder=R/'bin/mip-probes'/(device+'-'+a.profile+'-'+a.locale);folder.mkdir(parents=True,exist_ok=True)
 manifest=(R/'preview/manifest.xml').read_text().replace('e4c16f1eb76d4c88a6de6aa791adf802',uuid.uuid5(uuid.NAMESPACE_DNS,'moke-runtime-probe-v6-'+device+'-'+a.profile+'-'+a.locale+'-'+a.locale).hex).replace('entry="InstinctFaceApp"','entry="ProbeApp"');(folder/'manifest.xml').write_text(manifest)
 lines=(R/'preview.jungle').read_text().splitlines();src=next(x.split(' = ')[1] for x in lines if x.startswith(device+'.sourcePath'));res=next(x.split(' = ')[1] for x in lines if x.startswith(device+'.resourcePath'))
 source=';'.join(str(R/x) for x in src.split(';'));resource=';'.join(str(R/x) for x in res.split(';'))
 if a.locale=='eng':resource+=';'+str(R/'generated/assets'/row['asset_key']/'resources-eng')
 jungle='project.manifest = manifest.xml\nbase.sourcePath = .;'+source+'\nbase.resourcePath = '+resource+'\n'
 if row['renderer']=='legacy' and row['on_watch_settings']:jungle+='base.excludeAnnotations = classicPrefs\n'
 (folder/'probe.jungle').write_text(jungle)
 base='LegacyFace' if row['renderer']=='legacy' else 'InstinctFaceView'
 init=''.join('Application.getApp().setProperty('+json.dumps(k)+','+json.dumps(v)+');' for k,v in config.items())
 (folder/'ProbeApp.mc').write_text('''import Toybox.System;\nimport Toybox.Application;\nclass ProbeApp extends InstinctFaceApp {function initialize(){InstinctFaceApp.initialize();}function onStart(state){InstinctFaceApp.onStart(state);'''+init+'''}function getInitialView(){_view=new ProbeFace();return [_view];}}\nclass ProbeFace extends '''+base+''' {var _logged=false;function initialize(){'''+base+'''.initialize();}function onUpdate(dc){'''+base+'''.onUpdate(dc);if(!_logged){_logged=true;System.println("FRAME_OK '''+device+''' free="+System.getSystemStats().freeMemory+" EN="+FaceLocale.english());}}function onPartialUpdate(dc){'''+base+'''.onPartialUpdate(dc);if(!_logged){_logged=true;System.println("PARTIAL_OK '''+device+'''");}}}\n''')
 build=subprocess.run(['monkeyc','-f',str(folder/'probe.jungle'),'-d',device,'-o',str(folder/'probe.prg'),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-r','-O','3z','-w'],cwd=R,capture_output=True,text=True);(folder/'build.log').write_text(build.stdout+build.stderr)
 if build.returncode:results.append(dict(id=device,status='compile-failed'));print(device,'COMPILE_FAIL',flush=True);continue
 if a.build_only:
  print(device,'COMPILED',flush=True);continue
 proc=subprocess.Popen(['monkeydo',str(folder/'probe.prg'),device],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True);output=b'';start=time.monotonic()
 while time.monotonic()-start<a.seconds:
  ready,_,_=select.select([proc.stdout],[],[],.5)
  if ready:
   chunk=os.read(proc.stdout.fileno(),65536)
   if chunk:output+=chunk
   elif proc.poll() is not None:break
  if b'app crash' in output.lower():break
 try:os.killpg(proc.pid,signal.SIGTERM)
 except ProcessLookupError:pass
 try:proc.wait(timeout=3)
 except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL)
 text=output.decode(errors='replace');(folder/'runtime.log').write_text(text)
 status='passed' if 'FRAME_OK' in text and 'app crash' not in text.lower() else 'failed'
 results.append(dict(id=device,profile=a.profile,locale=a.locale,status=status,free_bytes=re.findall(r'free=(\d+)',text),partial='PARTIAL_OK' in text,scope='SDK simulator native render with isolated test app ID; visual QA separate'));print(device,status,text[-300:].strip(),flush=True)
if a.build_only:raise SystemExit(0)
file=R/'bin/mip-runtime-1.1.0.json';previous=json.loads(file.read_text()) if file.exists() else [];by_id={(r['id'],r.get('profile','default'),r.get('locale','zhs')):r for r in previous};by_id.update({(r['id'],r.get('profile','default'),r.get('locale','zhs')):r for r in results});file.write_text(json.dumps(list(by_id.values()),ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if all(r['status']=='passed' for r in results) else 1)
