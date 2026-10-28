"""Verify and package the released watch face, with actual runtime evidence."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
build=(ROOT/'bin/build.log').read_text()
assert build.count('BUILD SUCCESSFUL')==3 and 'ERROR:' not in build
tests=(ROOT/'bin/data-tests.log').read_text()
assert 'PASSED (passed=13, failed=0, errors=0)' in tests
runtime={}
for name in ('live','demo'):
    log=(ROOT/f'bin/{name}-runtime.log').read_text()
    assert 'RETRO_FRAME_OK version=1.2.11' in log and 'crash' not in log.lower(),log
    runtime[name]={'log':log.strip(),'first_free_bytes':int(re.search(r'free=(\d+)',log)[1])}
assert 'demo=false' in runtime['live']['log'] and 'demo=true' in runtime['demo']['log']
logs='\n'.join(r['log'] for r in runtime.values())
with zipfile.ZipFile(DIST/'RetroWorld-Instinct3-1.2.10.zip') as z:
    for name in ('Environment.mc','LiveData.mc','SolarMap.mc','MapStyle.mc','MapSkinResources.mc'):
        assert (ROOT/'source'/name).read_bytes()==z.read('source-project/source/'+name)
    old_view=z.read('source-project/source/RetroWorld.mc').decode()
    prior_lifecycle=z.read('validation/native-lifecycle-1.2.2.log').decode()
current_view=(ROOT/'source/RetroWorld.mc').read_text()
expected=old_view.replace('version=1.2.10','version=1.2.11')
expected=expected.replace('dc.setPenWidth(2);hand(dc,(_hour%12)*30+_min*0.5,11,19,19);','dc.setPenWidth(3);hand(dc,(_hour%12)*30+_min*0.5,11,19,19);')
expected=expected.replace('dc.fillCircle(19,19,1)','dc.fillCircle(19,19,2)')
assert current_view==expected,'Only analog hour/minute/hub geometry and release marker may change.'
assert 'function onPartialUpdate(' not in current_view
assert 'if(_sleeping) {return;}' in current_view
assert 'wake_only_seconds=true' in logs
sleep_seconds=re.findall(r'RETRO_SECONDS_SLEEP held=(\d+)',prior_lifecycle)
restored_seconds=re.findall(r'RETRO_MINUTE_OK asleep=true held_second=(\d+)',prior_lifecycle)
assert sleep_seconds and any(s in sleep_seconds for s in restored_seconds)
assert 'RETRO_SECONDS_WAKE' in prior_lifecycle
assert sha(ROOT/'bin/RetroWorld-Instinct3.prg')==sha(DIST/'RetroWorld-Instinct3.prg')
restored=['resources/fonts/'+n for n in ('tiny.fnt','tiny.png','medium.fnt','medium.png')]
with zipfile.ZipFile(DIST/'RetroWorld-Instinct3-1.1.1.zip') as z:
    for name in restored:assert (ROOT/name).read_bytes()==z.read('source-project/'+name),name
typography=json.loads((DIST/'typography-validation.json').read_text())
assert typography['metrics_unchanged_except_date'] and typography['letter_fonts_unchanged'] and typography['topology_unchanged']
assert typography['max_ink_change_fraction']<=.05
skin_report=json.loads((DIST/'map-skins-validation.json').read_text())
assert skin_report['count']>=12 and skin_report['unique_day_bitmaps']==skin_report['count'] and skin_report['all_skins_reachable']
alignment=json.loads((DIST/'status-alignment.json').read_text())
assert all(abs(r['visible_white_center'][i]-r['ink_center'][i])<=.5 for r in alignment['rows'] for i in (0,1))
date_padding=json.loads((DIST/'date-padding-validation.json').read_text())
assert date_padding['min_white_margin_top_bottom_pixels']>=1 and date_padding['segment_caps_preserved']
circle=json.loads((DIST/'circle-validation.json').read_text())
assert circle['all_720_hour_minute_positions_inside_cache'] and circle['other_preview_pixels_unchanged']
artifacts=['RetroWorld-Instinct3.prg','RetroWorld-1.2.11.iq','RetroWorld-weather-designs.png','typography-validation.json','RetroWorld-map-skins.png','RetroWorld-map-daylight.png','map-skins.json','map-skins-validation.json','status-alignment.json','date-padding-validation.json','circle-validation.json','RetroWorld-circle-comparison.png']
for name in ('RetroWorld-v1.2.11-simulator.png',):
    if (DIST/name).exists():artifacts.append(name)
report={
 'version':'1.2.11','product':'instinct3solar45mm (45 / 50 mm part numbers)','screen':[176,176],
 'application_id':'d2fd1f269ea4491f9bf5c77046e0e301','runtime':runtime,
 'build':'live PRG, demo PRG, both part-number IQ export variants passed',
 'tests':'Reuse 13 data/lifecycle tests for unchanged code paths. All 720 hour/minute hand positions checked inside the existing 39x39 cache. Font, date-padding and data modules unchanged. Current compile/render checked.',
 'font_restoration':'Tiny and medium text font files remain byte-identical to 1.1.1. Original slanted seven-segment geometry retained; only raster edge cleanup on time/seconds/date digits.',
 'typography':typography,
 'seconds_policy':'Wake/return-to-face: current numeric seconds and analog second hand update each second. Sleep: retain the last visible second and needle position, including during minute frame redraw. Next wake snaps to current seconds. No custom onPartialUpdate implementation.',
 'native_lifecycle_validation':'Wrist behavior test rerun; previous 1.2.2 native sleep/minute/wake log retained as historical evidence. No physical-wrist test.',
 'visual_qa':'Restored heavier instrument dial per user feedback: fitted black outer ring, 12 long + 48 short line ticks, original 3px hour hand and 2px-radius hub. Pointer lengths, original 12/3/6/9 glyphs, hardware size/location, wrist-only seconds and all other layout preserved. No grayscale or temporal dithering.',
 'analog_circle':circle,
 'date_padding':date_padding,
 'status_alignment':alignment,
 'power_validation_scope':'Existing wake-only behavior unchanged; no per-second application drawing at rest. No new battery-life measurement.',
 'cache_scope':'Map rebuilt only on a 5-minute slot, weather-category change, or marker-pixel change. Only current skin day/night bitmap pair loaded. Trigonometry for geographic rows/columns precomputed; contiguous night spans copied from prebaked textures. No new Position/Weather API calls.',
 'map_skins':skin_report,
 'skin_selection':'Uses cached weather and sunrise/sunset for chosen last-fix/weather-city position. Weather priority, then dawn/dusk/day/night. Polar missing sun times use approximate solar elevation; no position falls back to watch-local clock. All 16 styles are reachable.',
 'location':'Small ring/dot. Last known fix <=2 h preferred; fresh weather observation location <=3 h fallback. Missing/future/stale/invalid data do not create a marker. No continuous GPS activation; no raw coordinates in runtime logs.',
 'weather':'Garmin cached local weather. Separate icon/Celsius panel retained. Map weather skins are decorative local-condition textures, not global weather measurements. Missing weather is not invented.',
 'sun':'Garmin Weather.getSunrise/getSunset for selected position; watch-local time; missing and polar cases show --:--.',
 'basemap':'Natural Earth 1:110m land; public domain; equirectangular lon[-180,180] x lat[90,-90], 89x29 pixels',
 'physical_device_tested':False,'battery_life_measured':False,'store_submitted':False,
 'sha256':{name:sha(DIST/name) for name in artifacts}}
(DIST/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
archive=DIST/'RetroWorld-Instinct3-1.2.11.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for name in artifacts+['RetroWorld-preview.png','RetroWorld-pixels.png','SHA256SUMS','validation.json']:z.write(DIST/name,name)
    z.write(ROOT/'README.md','README.md')
    z.writestr('validation/native-lifecycle-1.2.2.log',prior_lifecycle)
    for name in ('build.log','live-runtime.log','demo-runtime.log','data-tests.log','test-build.log'):z.write(ROOT/'bin'/name,'validation/'+name)
    for folder in ('source','live','preview','resources','tools','tests','assets'):
        for p in sorted((ROOT/folder).rglob('*')):
            if p.is_file() and '__pycache__' not in str(p):z.write(p,'source-project/'+str(p.relative_to(ROOT)))
    for name in ('monkey.jungle','preview.jungle','manifest.xml','README.md'):z.write(ROOT/name,'source-project/'+name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(f'Verified package: {archive} ({archive.stat().st_size:,} bytes)')
print(f'Live PRG: {(DIST/"RetroWorld-Instinct3.prg").stat().st_size:,} bytes; SHA256 {sha(DIST/"RetroWorld-Instinct3.prg")}')
