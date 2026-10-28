"""Inspect Garmin's signed 7z IQ export without changing the signed archive."""
from pathlib import Path
import subprocess,json,xml.etree.ElementTree as ET,hashlib,argparse,tempfile
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('package');p.add_argument('--only',nargs='*');a=p.parse_args();archive=Path(a.package).resolve();ns={'iq':'http://www.garmin.com/xml/connectiq'}
rows=json.loads((R/'config/mip-devices.json').read_text());rows=[r for r in rows if not a.only or r['id'] in a.only];devices=Path.home()/'Library/Application Support/Garmin/ConnectIQ/Devices';expected={}
for row in rows:
 c=json.loads((devices/row['id']/'compiler.json').read_text())
 for part in c['partNumbers']:expected[part['number']]=(row['id'],part)
with tempfile.TemporaryDirectory(prefix='moke-iq-review-') as folder:
 subprocess.run(['7zz','x','-r','-y','-o'+folder,str(archive),'manifest.xml','*-settings.json'],check=True,capture_output=True)
 root=ET.parse(Path(folder)/'manifest.xml').getroot();app=root.find('iq:application',ns);assert app.get('id')=='e4c16f1eb76d4c88a6de6aa791adf801' and app.get('entry')=='InstinctFaceApp'
 products=app.find('iq:products',ns);assert {x.get('partNumber') for x in products}==set(expected)
 schema=json.loads((R/'config/settings-catalog.json').read_text());keys={x['key'] for x in schema['settings']};translations=json.loads((R/'config/english-translations.json').read_text());licensed=0;bilingual=0
 for item in products:
  part=item.get('partNumber');device,original=expected[part];assert int(item.get('minFirmwareVersion') or 0)>=original.get('firmwareVersion',0);assert item.get('connectIqVersion')==original['connectIQVersion']
  data=json.loads((Path(folder)/item.get('settings')).read_text());assert {x['key'] for x in data['settings']}==keys,part
  langs=data['languages'];text=json.dumps(langs,ensure_ascii=False)
  assert 'eng' in langs and 'valyrian' in langs,part
  settings={x['key']:x for x in data['settings']}
  for row in schema['settings']:
   item=settings[row['key']];assert item['defaultValue']==row['default']
   title=schema['groups'][row['group']][1]+' · '+row['label'];english=translations[schema['groups'][row['group']][1]]+' · '+translations[row['label']]
   assert langs['valyrian'][item['configTitle']]==title,(part,row['key'],'Chinese')
   assert langs['eng'][item['configTitle']]==english,(part,row['key'],'English')
   if row['type']==0:
    options=item['configOptions'];assert [o['value'] for o in options]==list(range(len(row['options'])))
    assert [langs['eng'][o['display']] for o in options]==[translations[x] for x in row['options']]
  bilingual+=1
  if 'SIL OPEN FONT LICENSE' in text and 'Aileron' in text:licensed+=1
 assert licensed==len(products),(licensed,len(products),'font notices absent from compiled settings metadata')
 result=dict(status='passed',package=str(archive),sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),size=archive.stat().st_size,device_targets=len(rows),part_number_variants=len(products),settings_per_variant=len(keys),font_notices=licensed,bilingual_settings_variants=bilingual,scope='Signed archive manifest, variant coverage, firmware floors, application identity, settings and bundled font notices; no runtime claim.')
 (R/'bin/iq-package-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(result)
