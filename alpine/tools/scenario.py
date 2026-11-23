"""Build isolated, deterministic time/weather previews; never change the live app ID."""
from pathlib import Path
import sys; sys.path.append(str(Path(__file__).resolve().parents[2]/'tools')); import ciq_env
import argparse,os,subprocess,uuid,datetime
from generate import generate,ROOT,DEVICES
p=argparse.ArgumentParser();p.add_argument('device',choices=DEVICES);p.add_argument('scene',type=int,choices=range(18));p.add_argument('--at');p.add_argument('--weather',choices=['unknown','clear','partly','cloudy','rain','snow','storm','fog'],default='clear');p.add_argument('--lat',type=float,default=39.9);p.add_argument('--lon',type=float,default=116.4);p.add_argument('--name');a=p.parse_args()
hour={1:5,3:19,4:23,9:23}.get(a.scene,14)
at=datetime.datetime.fromisoformat(a.at) if a.at else datetime.datetime(2026,6,21,hour,23,tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
if at.tzinfo is None:p.error('--at requires a UTC offset')
wx=['unknown','clear','partly','cloudy','rain','snow','storm','fog'].index(a.weather)
name=a.name or f'scene{a.scene}';assert all(c.isalnum() or c in '-_' for c in name)
generate();dest=ROOT/'generated/scenarios'/f'{a.device}-{name}';dest.mkdir(parents=True,exist_ok=True)
date=at.strftime('%a %m/%d').upper()
(dest/'Mode.mc').write_text(f'module Mode {{const DEMO=true;const SCENE={a.scene};const STAMP={int(at.timestamp())};const MINUTES={at.hour*60+at.minute};const WEATHER={wx};const LAT={a.lat}d;const LON={a.lon}d;const DATE="{date}";function refresh() {{}}}}\n')
ident=uuid.uuid5(uuid.NAMESPACE_DNS,f'wristink.alpine.weather1.{a.device}.{a.scene}.{at.isoformat()}.{wx}.{a.lat}.{a.lon}').hex
(dest/'manifest.xml').write_text((ROOT/'manifest.xml').read_text().replace('bb71078cce15417aa5425aa350817001',ident))
rel=dest.relative_to(ROOT);j=ROOT/'scenario.jungle'
j.write_text((ROOT/'monkey.jungle').read_text().replace('project.manifest = manifest.xml',f'project.manifest = {rel}/manifest.xml').replace('base.sourcePath = source;live',f'base.sourcePath = source;{rel}'))
sdk=ciq_env.sdk()
env=ciq_env.java_env()
optimization='2z' if a.device in ('instinct2','instinct2s','instinct2x') else '0'
compat=['--disable-api-has-check-removal'] if optimization=='2z' else []
subprocess.run([str(sdk/'bin/monkeyc'),'-f',str(j),'-d',a.device,'-o',str(ROOT/f'bin/Alpine-{a.device}-{name}.prg'),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-r','-O',optimization,'-w','--no-gen-styles']+compat,cwd=ROOT,env=env,check=True)
