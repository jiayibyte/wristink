"""Build native command-parity test against generated 64 KiB icons."""
from pathlib import Path
import sys; sys.path.append(str(Path(__file__).resolve().parents[3]/'tools')); import ciq_env
import shutil,subprocess,os,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[2];out=root/'bin/icon-parity';out.mkdir(parents=True,exist_ok=True)
for name in ['LegacyIcons.mc','WeatherGlyphs.mc','WeatherIcons.mc']:shutil.copy2(root/'generated/profiles/instinct2x'/name,out/name)
shutil.copy2(Path(__file__).with_name('Parity.mc'),out/'Parity.mc')
(out/'ReferenceIcons.mc').write_text((root/'compat/legacy/LegacyIcons.mc').read_text().replace('module LegacyIcons','module ReferenceIcons'))
ns='http://www.garmin.com/xml/connectiq';ET.register_namespace('iq',ns);tree=ET.parse(root/'manifest.xml');app=tree.getroot().find('{'+ns+'}application');app.set('id','9caf0d421c23483ca457c8c508ddf0a1');app.set('entry','ParityApp');tree.write(out/'manifest.xml',encoding='utf-8')
(out/'test.jungle').write_text('project.manifest = manifest.xml\nbase.sourcePath = .\nbase.resourcePath = ../../resources;../../resources-eng\n')
env=ciq_env.java_env()
r=subprocess.run(['monkeyc','-f',str(out/'test.jungle'),'-d','fr55','-o',str(out/'test.prg'),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-t','-w'],env=env,capture_output=True,text=True);(out/'build.log').write_text(r.stdout+r.stderr);print('PASS' if r.returncode==0 else r.stdout+r.stderr);raise SystemExit(r.returncode)
