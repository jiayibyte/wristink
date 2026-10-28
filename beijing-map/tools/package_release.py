#!/usr/bin/env python3
from pathlib import Path
import re,json,hashlib,zipfile,shutil,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
def main():
 log=(ROOT/'tests/native-batch/runtime.log').read_text()
 assert 'BATCH_ALL_OK' in log and 'Encountered an app crash' not in log and 'BATCH_ROUTE_FAIL' not in log, 'Native regression suite has not passed'
 routes=[dict(destination=m[0],points=int(m[1]),meters=float(m[2]),elapsed_ms=int(m[3]),free_after_bytes=int(m[4])) for m in re.findall(r'BATCH_ROUTE_OK (\S+) points=(\d+) meters=([0-9.]+) ms=(\d+) free=(\d+)',log)]
 smoke=(ROOT/'dist/simulator-v03-production.log').read_text();assert 'MAP_FRAME part=50/50' in smoke and 'APP_STOP' in smoke and 'Encountered an app crash' not in smoke
 assert 'TAB page=1' in smoke and 'TAB page=0' in smoke
 ui=(ROOT/'dist/simulator-v03-ui.log').read_text();assert 'DASHBOARD_CHECKS_OK' in ui and 'DASHBOARD_CHECKS_FAIL' not in ui and 'Encountered an app crash' not in ui
 timer=re.search(r'BATCH_TIMER elapsed=(\d+) restored_and_reset=true',log);assert timer
 assert len(routes)==4
 trail=re.search(r'BATCH_TRAIL persisted=true valid=true points=(\d+) fit_save_api=true min_free=(\d+)',log);assert trail
 build=(ROOT/'dist/build-v03-full.log').read_text();assert 'BUILD SUCCESSFUL' in build and 'ERROR:' not in build
 ns={'i':'http://www.garmin.com/xml/connectiq'};permissions=[n.get('id') for n in E.parse(ROOT/'manifest.xml').findall('.//i:uses-permission',ns)];assert permissions==['Positioning','Fit','Sensor']
 source=''.join(p.read_text() for p in (ROOT/'source').glob('*.mc'));assert 'Communications' not in source
 artifact=ROOT/'dist/BeijingMap-Instinct3Solar.prg';sha=hashlib.sha256(artifact.read_bytes()).hexdigest()
 summary={'version':'0.3','target':'Instinct 3 Solar 45/50 mm shared SDK target','all_features_offline':True,'permissions':permissions,'size_bytes':artifact.stat().st_size,'sha256':sha,'native_fixed_coordinate_routes':routes,'native_trail':{'injected_samples':2600,'persisted_and_restored':True,'simplified_points':int(trail[1]),'start_and_latest_position_preserved':True,'fit_save_api_returned_true':True,'min_observed_free_bytes_after_tick':int(trail[2])},'native_dashboard_checks_passed':True,'recording_timer_save_restore_reset_passed':True,'native_recording_timer_test_seconds':int(timer[1]),'ui_evidence':{'simulator-v03-map.png':'Synthetic coordinates/metrics, SIM label','simulator-v03-dashboard.png':'Synthetic metrics, SIM label','simulator-v03-production-map.png':'Actual delivery PRG using Garmin simulator APIs','simulator-v03-production-dashboard.png':'Actual delivery PRG, missing heart rate displayed as -- if no sensor sample'},'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'source').glob('*.mc')},'production_prg_simulator_start_and_exit':True,'real_watch_installed':False,'real_gps_compass_tested':False,'FIT_GPS_contents_verified':False,'real_battery_tested':False,'limits':['Only OSM-indexed places/addresses','Hierarchical walking recommendation; not guaranteed shortest','250m graph-node snap; road endpoints may differ from entrances','Complex routes may require intermediate destinations','Standing wrist orientation is not guaranteed by GPS course']}
 (ROOT/'dist/validation-v03.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
 (ROOT/'dist/BeijingMap-Instinct3Solar.sha256').write_text(sha+'  BeijingMap-Instinct3Solar.prg\n')
 evidence=['validation-v03.json','data-validation.json','offline-navigation-validation.json','simulator-v03-map.png','simulator-v03-dashboard.png','simulator-v03-production-map.png','simulator-v03-production-dashboard.png','simulator-v03-production.log','simulator-v03-ui.log']
 target=ROOT/'dist/BeijingMap-Instinct3Solar-v0.3-双页全离线导航.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  z.write(artifact,artifact.name);z.write(ROOT/'dist/BeijingMap-Instinct3Solar.sha256','BeijingMap-Instinct3Solar.sha256');z.write(ROOT/'README.md','安装说明.md')
  for name in evidence:z.write(ROOT/'dist'/name,name)
  for folder in ['source','resources','tools','tests']:
   for p in (ROOT/folder).rglob('*'):
    if not p.is_file() or any(part in {'gen','__pycache__'} for part in p.parts) or '.prg.' in p.name:continue
    if p.suffix not in {'.mc','.xml','.jungle','.png','.py','.sh','.md'}:continue
    z.write(p,'source-project/'+str(p.relative_to(ROOT)))
  for name in ['manifest.xml','monkey.jungle','README.md']:z.write(ROOT/name,'source-project/'+name)
  for name in ['map-stats.json','packed-preview.json','navigation-stats.json','offline-navigation-stats.json','search-stats.json','beijing-full.osm.pbf.md5']:
   z.write(ROOT/'data'/name,'source-project/data/'+name)
  z.write(ROOT/'tests/native-batch/runtime.log','evidence/native-batch.log')
 with zipfile.ZipFile(target) as z:assert z.testzip() is None
 shutil.copy2(target,ROOT/'dist/BeijingMap-Instinct3Solar-试用包.zip')
 print(json.dumps({'package':str(target),'zip_bytes':target.stat().st_size,'prg_bytes':artifact.stat().st_size,'sha256':sha,'native_routes':len(routes),'native_trail_points':int(trail[1]),'min_free':int(trail[2])},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
