from pathlib import Path
import tempfile,subprocess,xml.etree.ElementTree as E,json,hashlib
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT.parent/'watchface-feedback-20261114';ALP=ROOT.parent/'alpine-device-expansion-20261116'
def sizes(p):
 with tempfile.TemporaryDirectory(prefix='watchface-sizes-') as d:
  subprocess.run(['7zz','x','-r','-y','-o'+d,str(p),'manifest.xml','*.prg'],check=True,capture_output=True)
  r=E.parse(Path(d)/'manifest.xml').getroot();return {v.get('partNumber'):(Path(d)/v.get('filename')).stat().st_size for v in r.iter() if v.get('partNumber') and v.get('filename')}
report={}
for app,old,new in [('Alpine',ALP/'alpine/dist/Alpine-1.1.0-compact.iq',ROOT/'alpine/dist/Alpine-1.2.0.iq'),('Moke',OLD/'moke/dist/Moke-1.2.1.iq',ROOT/'moke/dist/Moke-1.2.2.iq'),('Retro',OLD/'retro-world/dist/RetroWorld-2.1.2.iq',ROOT/'retro-world/dist/RetroWorld-2.1.3.iq')]:
 before=sizes(old);after=sizes(new);assert set(before)==set(after)
 rows=[{'hardware':k,'before_bytes':before[k],'after_bytes':after[k],'reduction_percent':round(100*(1-after[k]/before[k]),2)} for k in sorted(after)]
 report[app]={'version':new.stem,'variants':len(rows),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'minimum_bytes':min(after.values()),'maximum_bytes':max(after.values()),'all_smaller':all(after[k]<before[k] for k in after),'min_reduction_percent':min(r['reduction_percent'] for r in rows),'max_reduction_percent':max(r['reduction_percent'] for r in rows),'devices':rows}
 print(app,{k:v for k,v in report[app].items() if k not in ['devices','source_commit','sha256']},flush=True)
Path(__file__).with_name('package-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
