// Generated white-heart fonts; load only the chosen family/size.
import Toybox.Graphics;
import Toybox.WatchUi;
module WhiteHeartFonts {function load(family,size){var id=Rez.Fonts.WhiteHeartF0S26;switch(family*3+size){
case 0:id=Rez.Fonts.WhiteHeartF0S22;break;
case 1:id=Rez.Fonts.WhiteHeartF0S26;break;
case 2:id=Rez.Fonts.WhiteHeartF0S28;break;
case 3:id=Rez.Fonts.WhiteHeartF1S22;break;
case 4:id=Rez.Fonts.WhiteHeartF1S26;break;
case 5:id=Rez.Fonts.WhiteHeartF1S28;break;
case 6:id=Rez.Fonts.WhiteHeartF2S22;break;
case 7:id=Rez.Fonts.WhiteHeartF2S26;break;
case 8:id=Rez.Fonts.WhiteHeartF2S28;break;
}return WatchUi.loadResource(id) as Graphics.FontType;}}
