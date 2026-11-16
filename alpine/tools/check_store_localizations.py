"""Store-only translation/media checks; never add runtime languages."""
from pathlib import Path
import json,subprocess,xml.etree.ElementTree as ET
from PIL import Image
R=Path(__file__).resolve().parents[1]
entries=json.loads((R/'store/localizations.json').read_text())
expected={'zh_TW','zh_CN','ja','in','ms','cs','da','de','en','es','fr','hr','it','hu','nl','nb','pl','pt_BR','pt_PT','sk','sl','fi','sv','el','ru','iw','th','ko'}
assert set(entries)==expected
manifest=ET.parse(R/'manifest.xml').getroot();ns={'iq':'http://www.garmin.com/xml/connectiq'}
assert {e.text.strip() for e in manifest.findall('.//iq:language',ns)}=={'eng','zhs'}
from make_store_media import font
reports=[]
for key,v in entries.items():
 assert 0<len(v['title'])<=50 and 0<len(v['description'])<=4000 and 0<len(v['whatsNew'])<=4000
 for field in ['title','description','whatsNew','headline','tagline','demoCaption']:
  assert not any(mark in v[field] for mark in ['TODO','TBD','TRANSLATE_ME'])
 # Check actual font cmap coverage via Fontconfig, including RTL and Thai text.
 path=font(30,key).path
 charsets=subprocess.run(['/opt/homebrew/bin/fc-query','--format=%{charset}\\n',str(path)],capture_output=True,text=True,check=True).stdout.splitlines()
 ranges=[]
 for cs in charsets:
  for token in cs.split():
   token=token.replace('\\n','')
   if not token:continue
   try:
    limits=token.split('-');ranges.append((int(limits[0],16),int(limits[-1],16)))
   except ValueError:pass
 missing={c for c in v['title']+v['headline']+v['tagline']+v['demoCaption'] if not c.isspace() and not any(a<=ord(c)<=b for a,b in ranges)}
 assert not missing,(key,missing,path)
 hero=R/f'store/images/hero-{key}-1440x720.jpg';assert Image.open(hero).size==(1440,720) and hero.stat().st_size<2000000
 reports.append({'storeKey':key,'titleChars':len(v['title']),'descriptionChars':len(v['description']),'fontCoverage':'passed'})
for path in (R/'store/images').glob('0*.jpg'):assert path.stat().st_size<150000
cover=R/'store/images/cover-500.png';assert Image.open(cover).size==(500,500) and cover.stat().st_size<300000
(R/'store/localization-validation.json').write_text(json.dumps({'languages':reports,'runtimeLanguagesUnchanged':['eng','zhs'],'localeSource':'Garmin developer Edit App Details visible language selector','imageChecks':'passed'},ensure_ascii=False,indent=2)+'\n')
print('PASS: 28 store locales, text bounds, font coverage, media sizes; runtime EN/ZHS unchanged')
