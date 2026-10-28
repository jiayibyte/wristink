"""Compile an isolated simulator app for one personalization regression profile."""
from pathlib import Path
import argparse,json,subprocess,uuid

ROOT=Path(__file__).resolve().parents[1]
PROFILES={
 'crossover-hands':dict(analogHandMode=2),
 'cards-new':dict(topCardImage=12,bottomCardImage=19),
 'cards-single':dict(topCardImage=14,bottomCardImage=0),
 'cards-seconds':dict(topCardImage=0,bottomCardImage=0,secondsMode=0),
 'cards-light':dict(darkTheme=False,topCardImage=8,bottomCardImage=9),
 'power-always':dict(secondsMode=2,showSeconds=True),
 'power-gesture':dict(secondsMode=1,showSeconds=True),
 'typography':dict(darkTheme=False,dataFont=1,dataSize=2,timeFormat=1,timeFont=1,timeSeparator=1,dateFormat=7,dateFont=3,dateSize=3,circleBackground=1),
 'short-date-12h':dict(timeFormat=1,dateFormat=5,dateSize=3),
 'progress':dict(topOne=19,topOneStyle=2,topTwo=20,topTwoStyle=3,bottomLeft=2,bottomLeftStyle=4,bottomRight=19,bottomRightStyle=6,footerLeft=5,footerLeftStyle=5,footerLeftGoal=2000,footerRight=18,footerRightStyle=1,circle=22,cellsSource=2,cellsStyle=1,ringSource=3,ringStyle=3,ringStart=1),
 'hidden':dict(topOne=0,topTwo=0,topThree=0,bottomLeft=0,bottomRight=0,footerLeft=0,footerRight=0,showTime=False,showDate=False,showSeconds=False,showCircle=False,showWind=False,showMoon=False,showMoveBar=False,showStatus=False),
 'long':dict(dataFont=2,dataSize=2,topThree=18,dateFormat=7,sideData=28,circle=2,cellsSource=0,ringSource=0,footerLeft=2,footerRight=28),
}
def main():
 p=argparse.ArgumentParser();p.add_argument('profile',choices=PROFILES);args=p.parse_args()
 folder=ROOT/'bin/config-fixtures'/args.profile;folder.mkdir(parents=True,exist_ok=True)
 appid=uuid.uuid5(uuid.NAMESPACE_DNS,'instinct-personalization-test-'+args.profile).hex
 manifest=(ROOT/'preview/manifest.xml').read_text().replace('e4c16f1eb76d4c88a6de6aa791adf802',appid).replace('entry="InstinctFaceApp"','entry="FixtureApp"')
 (folder/'manifest.xml').write_text(manifest)
 config=json.dumps(PROFILES[args.profile],ensure_ascii=False)
 source='''import Toybox.Application;
import Toybox.Lang;
class FixtureApp extends InstinctFaceApp {
    function initialize(){
        InstinctFaceApp.initialize();
        var values='''+config+''';
        var keys=values.keys();
        for(var i=0;i<keys.size();i++){var key=keys[i] as String;Application.Properties.setValue(key,values[key]);}
        FacePrefs.reload();FontCatalog.reset();
    }
}
'''
 (folder/'FixtureApp.mc').write_text(source)
 (folder/'fixture.jungle').write_text('project.manifest = manifest.xml\nbase.sourcePath = .;../../../source;../../../preview;../../../profiles/base\nbase.resourcePath = ../../../resources;../../../preview/resources\n')
 # Use Monkey C's dictionary syntax; JSON is only used for the boolean and string literals.
 source=source.replace('var values='+config+';','var values={'+','.join(json.dumps(k)+'=>'+json.dumps(v) for k,v in PROFILES[args.profile].items())+'};')
 (folder/'FixtureApp.mc').write_text(source)
 command=['monkeyc','-f',str(folder/'fixture.jungle'),'-d','instinct3solar45mm','-o',str(folder/'fixture.prg'),'-y',str(Path.home()/'.Garmin/keys/developer_key.der'),'-r','-w']
 subprocess.run(command,check=True,cwd=ROOT)
 print(f'Fixture {args.profile}: {folder}/fixture.prg')
if __name__=='__main__':main()
