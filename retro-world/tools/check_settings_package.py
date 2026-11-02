"""Verify every hardware variant carries the complete bilingual settings."""
from pathlib import Path
import argparse,json,subprocess,tempfile,xml.etree.ElementTree as ET,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('package');a=p.parse_args();archive=Path(a.package).resolve()
expected={e.get('id') for e in ET.parse(ROOT/'resources/settings/properties.xml').getroot()}
ns={'iq':'http://www.garmin.com/xml/connectiq'}
with tempfile.TemporaryDirectory(prefix='retro-settings-') as folder:
    subprocess.run(['7zz','x','-r','-y','-o'+folder,str(archive),'manifest.xml','*-settings.json'],check=True,capture_output=True)
    app=ET.parse(Path(folder)/'manifest.xml').getroot().find('iq:application',ns)
    assert app.get('id')=='d2fd1f269ea4491f9bf5c77046e0e301'
    products=app.find('iq:products',ns)
    for product in products:
        data=json.loads((Path(folder)/product.get('settings')).read_text())
        rows={row['key']:row for row in data['settings']};assert set(rows)==expected
        assert len(rows)==21 and rows['ManualLocation']['defaultValue'] is False
        assert rows['RefreshMode']['defaultValue']==1 and rows['TimeFormat']['defaultValue']==0
        for i in range(1,10): assert [o['value'] for o in rows[f'Field{i}']['configOptions']]==list(range(15))
        langs=data['languages'];assert langs['valyrian']['TimeFormatTitle']=='Time format'
        assert langs['zhs']['TimeFormatTitle']=='时间格式'
        assert rows['Latitude']['valueType']=='float' and rows['Longitude']['valueType']=='float'
    result={'passed':True,'hardware_variants':len(products),'settings_per_variant':len(expected),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
    (ROOT/'dist/settings-package-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
