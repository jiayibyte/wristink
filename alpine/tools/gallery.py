"""Build reproducible native gallery frames without changing live defaults or data.
Uses the production source, generated native assets, and isolated demo app IDs.
"""
from pathlib import Path
import argparse,concurrent.futures,json,os,shutil,subprocess,uuid,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('device',choices=['fenix7','epix2','instinct2s','instinct3solar45mm']);p.add_argument('names',nargs='+',choices=['halloween','mid-autumn-night','sunrise','sunset','sky-birds','sky-plane','sky-both','aurora','rain','snow','auto-rain','budget']);a=p.parse_args()
FRAMES={'halloween':(4,0),'mid-autumn-night':(5,3),'sunrise':(1,1),'sunset':(1,2),'sky-birds':(1,0),'sky-plane':(1,0),'sky-both':(1,0),'aurora':(1,3),'rain':(1,6),'snow':(1,7),'auto-rain':(1,6),'budget':(1,8)}
PRESETS={'halloween':{'Scene':16},'mid-autumn-night':{'Scene':17},'sky-birds':{'Scene':2,'SkyDecor':1,'WeatherLink':1},'sky-plane':{'Scene':2,'SkyDecor':2,'WeatherLink':1},'sky-both':{'Scene':2,'SkyDecor':3,'WeatherLink':1},'aurora':{'Scene':13,'SkyDecor':3,'WeatherLink':1},'rain':{'Scene':5,'SkyDecor':3},'snow':{'Scene':10,'SkyDecor':3},'auto-rain':{'Scene':0}}
# Avoid the legacy factory IDs that first-run migration intentionally hides.
PRESETS['budget']={'Scene':7,'SkyDecor':3,'PanelStyle':3,'HeaderTop':5,'HeaderLeft':3,'HeaderRight':8,'Left':5,'Middle':1,'Right':7}
sdk=Path((Path.home()/'Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg').read_text().strip())
env=dict(os.environ,JAVA_HOME='/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
def build(name):
 festival,frame=FRAMES[name]
 folder=ROOT/'generated/gallery'/a.device/name;folder.mkdir(parents=True,exist_ok=True)
 resources=folder/'resources';shutil.copytree(ROOT/'resources',resources,dirs_exist_ok=True)
 tree=ET.parse(resources/'settings/properties.xml')
 for prop in tree.getroot():
  if prop.attrib['id']=='Festival':prop.text=str(festival)
  if prop.attrib['id']=='TimeFormat':prop.text='2'
  if prop.attrib['id'] in PRESETS.get(name,{}):prop.text=str(PRESETS[name][prop.attrib['id']])
 tree.write(resources/'settings/properties.xml',encoding='unicode')
 mode=(ROOT/'preview/Mode.mc').read_text().replace('var i=Application.Properties.getValue("PreviewFrame");if(!(i instanceof Number) || i<0 || i>=10) {i=0;}',f'var i={frame};')
 (folder/'Mode.mc').write_text(mode)
 ident=uuid.uuid5(uuid.NAMESPACE_DNS,f'wristink.alpine.release-gallery1.{a.device}.{name}').hex
 (folder/'manifest.xml').write_text((ROOT/'preview/manifest.xml').read_text().replace('bb71078cce15417aa5425aa350817002',ident))
 rel=folder.relative_to(ROOT)
 jungle=(ROOT/'preview.jungle').read_text().replace('project.manifest = preview/manifest.xml',f'project.manifest = {rel}/manifest.xml').replace('base.sourcePath = source;preview',f'base.sourcePath = source;{rel}').replace('base.resourcePath = resources;preview/resources',f'base.resourcePath = {rel}/resources;preview/resources')
 # Generated English/Chinese menu strings remain exactly those of the live build.
 jf=ROOT/f'scenario-gallery-{a.device}-{name}.jungle';jf.write_text(jungle)
 output=ROOT/'bin/gallery'/a.device/name;output.mkdir(parents=True,exist_ok=True)
 flags=['-O','2z','--disable-api-has-check-removal']
 cmd=[str(sdk/'bin/monkeyc'),'-f',str(jf),'-d',a.device,'-o',str(output/'Alpine.prg'),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-r','-w','--no-gen-styles']+flags
 with (output/'build.log').open('w') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 result={'device':a.device,'name':name,'passed':r.returncode==0,'prg':str(output/'Alpine.prg')}
 print(json.dumps(result),flush=True)
 if r.returncode:print((output/'build.log').read_text(),flush=True)
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(build,a.names))
(ROOT/f'dist/evidence/gallery-builds-{a.device}.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
