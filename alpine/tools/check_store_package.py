from pathlib import Path
import argparse,json,hashlib,subprocess,tempfile,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);parser.add_argument('--version',default='1.0.0');parser.add_argument('--package');args=parser.parse_args()
source_commit=subprocess.check_output(['git','rev-parse',args.source_commit],cwd=R,text=True).strip()
inputs=['config/devices.json','source','live','resources','resources-zhs','manifest.xml','monkey.jungle','tools/settings.py','tools/generate.py','tools/panels.py','tools/everest_art.py','tools/typography.py','tools/sky_ornaments.py','tools/festivals.py']
subprocess.run(['git','diff','--quiet',source_commit,'--']+inputs,cwd=R,check=True)
package=Path(args.package).resolve() if args.package else R/f'dist/Alpine-{args.version}.iq'
assert package.exists()
root=Path(tempfile.mkdtemp(prefix='iq-audit-',dir=R/'dist'))
subprocess.run(['/opt/homebrew/bin/7zz','x',str(package),'-o'+str(root),'-y'],stdout=subprocess.DEVNULL,check=True)
ns={'iq':'http://www.garmin.com/xml/connectiq'};doc=ET.parse(root/'manifest.xml').getroot();app=doc.find('iq:application',ns)
assert app.attrib['id']=='bb71078cce15417aa5425aa350817001' and app.attrib['type']=='watchface'
assert {e.text for e in app.findall('.//iq:language',ns)}=={'eng','zhs'}
profiles=json.loads((R/'config/devices.json').read_text());expected={}
for dev in profiles:
 data=json.loads((Path.home()/f'Library/Application Support/Garmin/ConnectIQ/Devices/{dev}/compiler.json').read_text())
 for p in data['partNumbers']:expected[p['number']]={'sdkDevice':dev,'api':p['connectIQVersion']}
products=app.findall('.//iq:product',ns);assert {p.attrib['partNumber'] for p in products}==set(expected)
reports=[]
for entry in products:
 pn=entry.attrib['partNumber'];path=root/entry.attrib['filename'];assert path.exists()
 blob=path.read_bytes()
 for forbidden in ['ALPINE_READY demo=true','RECOVERY_PROBE','PreviewFrame','restoreFaceAndPersistAcrossRestart']:
  assert forbidden.encode() not in blob and forbidden.encode('utf-16le') not in blob,(pn,forbidden)
 debug=path.parent/'debug.xml'
 if debug.exists():
  s=debug.read_text()
  assert all('/'+d+'/' not in s for d in ['preview','tests','gallery','recovery']),pn
 settings=list(path.parent.glob('*settings.json'));assert len(settings)==1,(pn,settings)
 data=json.loads(settings[0].read_text());items={i['key']:i for i in data['settings']}
 for key,default,count in [('TimeFormat',0,3),('PanelStyle',1,4)]:
  assert items[key]['defaultValue']==default
  assert [x['value'] for x in items[key]['configOptions']]==list(range(count))
 for lang in ['valyrian','zhs']:
  assert lang in data['languages']
  for item in items.values():
   assert item['configTitle'] in data['languages'][lang]
 reports.append({'partNumber':pn,'device':expected[pn]['sdkDevice'],'api':entry.attrib['connectIqVersion'],'sha256':hashlib.sha256(blob).hexdigest(),'settings':'passed','diagnosticStrings':'absent'})
report={'package':str(package),'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'sourceCommit':source_commit,'variants':reports,'runtimeLanguages':['eng','zhs'],'auditFolder':str(root),'signatureVerification':'separate Garmin SDK VerifyIq result required'}
(R/'dist/evidence/store-package-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS:',len(reports),'hardware variants; defaults, runtime languages, diagnostics and settings verified')
