"""Gate the 2.0 store submission on native, visual, archive and signature evidence."""
from pathlib import Path
import hashlib,json,re,subprocess,xml.etree.ElementTree as ET,zipfile
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist';STORE=ROOT/'store';VERSION='2.0.0';IQ=DIST/f'RetroWorld-{VERSION}.iq'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
matrix=json.loads((DIST/'device-matrix.json').read_text());parts=sum(r['parts'] for r in matrix['devices'])
log=(ROOT/'bin/store-export.log').read_text();assert 'BUILD SUCCESSFUL' in log and 'ERROR:' not in log and f'{parts} OUT OF {parts} DEVICES BUILT' in log
native=json.loads((DIST/'native-perf.json').read_text());tests=json.loads((DIST/'native-test.json').read_text())
required={'instinct3solar45mm','instinct2s','venu3','instincte40mm','fenix6s','venusq2','fr55','instinct3amoled45mm','instinctcrossover','venu2s','vivoactive4s','venux1','instinct3amoled50mm','fenix7x','venu','venusq','instinctcrossoveramoled'}
lookup={r['device']:r for r in native}
assert required<=lookup.keys()
for id in required:
 r=lookup[id];assert r['passed'],id;m=r['measurements'];assert m['min_free']>=8192,(id,m)
 assert m['awake_map_builds']==0 and m['awake_weather_reads']==0,(id,m)
 assert m['width']==m['dc_width'] and m['height']==m['dc_height'],(id,m)
for id in ('instinct3solar45mm','venu3','instinct2s','venusq2'):
 r=next(x for x in tests if x['device']==id);assert r['passed'],id
 assert 'PASSED (passed=19, failed=0, errors=0)' in Path(r['log']).read_text(),id
layout=json.loads((DIST/'device-layout-validation.json').read_text());assert all(r['all_small_digits_distinct'] for r in layout['profiles'])
assert all(r.get('aod_fraction',0)<.1 and r.get('aod_four_minute_shared_pixels',0)==0 for r in layout['profiles'])
circle=json.loads((DIST/'circle-alignment-2.0.json').read_text());assert circle['bezel_center']==circle['dial_center'] and circle['white_pixels_clipped_by_hardware_mask']==0
media=json.loads((STORE/'media-validation.json').read_text());assert len(media['screenshots'])==8
subprocess.run(['7zz','t',str(IQ)],check=True,stdout=subprocess.DEVNULL)
inspect=ROOT/'bin/store-export-inspect';subprocess.run(['7zz','x','-y','-o'+str(inspect),str(IQ)],check=True,stdout=subprocess.DEVNULL)
ns={'i':'http://www.garmin.com/xml/connectiq'};app=ET.parse(inspect/'manifest.xml').getroot().find('i:application',ns)
assert app.get('id')=='d2fd1f269ea4491f9bf5c77046e0e301'
products=app.find('i:products',ns);assert len(products)==parts
subprocess.run(['openssl','dgst','-sha256','-keyform','DER','-verify',str(inspect/'dev_key.pub'),'-signature',str(inspect/'manifest.sig2'),str(inspect/'manifest.xml')],check=True,stdout=subprocess.DEVNULL)
for product in products:
 path=inspect/product.get('filename');assert path.is_file()
 assert b'PERF_RESULT' not in path.read_bytes(),'Diagnostic marker in release binary'
sdk=Path.home()/'Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2'
subprocess.run(['/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home/bin/java','-cp',str(sdk/'bin/monkeybrains.jar'),str(ROOT/'tools/VerifyIq.java'),str(IQ),str(inspect/'dev_key.pub')],check=True)
report={'version':VERSION,'name_zh':'寰游时刻 · Retro World','name_en':'Retro World · Map Watch Face','price':'Free','device_targets':len(matrix['devices']),'hardware_variants':parts,'resource_profiles':matrix['profiles'],'excluded_targets':len(matrix['excluded']),'iq_sha256':sha(IQ),'iq_bytes':IQ.stat().st_size,'signature_verification':'manifest and every PRG verified with exported public key','native_probes':native,'native_tests':tests,'layout':layout,'circle':circle,'media':media,'physical_device_tested':False,'battery_life_measured':False,'timing_scope':'Host simulator measurements; not real-watch battery/CPU benchmarks','publication_status':'ready; not submitted'}
receipt_path=STORE/'submission-receipt.json'
publication_status='ready; not submitted'
if receipt_path.exists():
 receipt=json.loads(receipt_path.read_text())
 if receipt['iq_sha256']==sha(IQ):
  publication_status=receipt['status'];report['submission']=receipt
report['publication_status']=publication_status
(DIST/'release-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(DIST/'SHA256SUMS').write_text(sha(IQ)+'  '+IQ.name+'\n')
meta=json.loads((STORE/'metadata.json').read_text());meta.update(publication_status=publication_status,package_sha256=sha(IQ),device_targets=len(matrix['devices']),hardware_variants=parts);(STORE/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
archive=DIST/f'RetroWorld-{VERSION}-release-kit.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for path in [IQ,DIST/'SHA256SUMS',DIST/'release-validation.json',DIST/'device-matrix.json',DIST/'circle-alignment-2.0.json']:
  z.write(path,path.name)
 for path in STORE.rglob('*'):
  if path.is_file() and ('evidence' not in path.parts or path.name.startswith('submitted-')):z.write(path,'store/'+str(path.relative_to(STORE)))
 for folder in ('source','live','preview','diagnostics','resources','tools','tests','assets'):
  for path in (ROOT/folder).rglob('*'):
   if path.is_file() and '__pycache__' not in path.parts:z.write(path,'source-project/'+str(path.relative_to(ROOT)))
 for name in ('README.md','manifest.xml','monkey.jungle','preview.jungle','tests.jungle','diagnostic.jungle'):z.write(ROOT/name,'source-project/'+name)
 for name in ('store-export.log','native-tests-run.log','native-probe-run.log','last-compat-run.log'):
  path=ROOT/'bin'/name
  if path.exists():z.write(path,'validation/'+name)
 for row in native+tests:z.write(row['log'],'validation/'+row['mode']+'/'+Path(row['log']).name)
print('Verified release kit:',archive,'bytes:',archive.stat().st_size)
print('IQ SHA256:',sha(IQ))
