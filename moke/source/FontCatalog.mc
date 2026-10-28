// Generated font families; keep renderer and resource IDs in sync.
import Toybox.Graphics;
import Toybox.WatchUi;
import Toybox.Lang;
module FontCatalog {
    (:extendedCode)
    function id(group,family,size) as ResourceId {
        if(group.equals("data")){switch(family*5+size){
            case 0:return Rez.Fonts.DataF0S8;
            case 1:return Rez.Fonts.DataF0S10;
            case 2:return Rez.Fonts.DataF0S12;
            case 3:return Rez.Fonts.DataF0S14;
            case 4:return Rez.Fonts.DataF0S16;
            case 5:return Rez.Fonts.DataF1S8;
            case 6:return Rez.Fonts.DataF1S10;
            case 7:return Rez.Fonts.DataF1S12;
            case 8:return Rez.Fonts.DataF1S14;
            case 9:return Rez.Fonts.DataF1S16;
            case 10:return Rez.Fonts.DataF2S8;
            case 11:return Rez.Fonts.DataF2S10;
            case 12:return Rez.Fonts.DataF2S12;
            case 13:return Rez.Fonts.DataF2S14;
            case 14:return Rez.Fonts.DataF2S16;
        }}
        if(group.equals("time")){switch(family*4+size){
            case 0:return Rez.Fonts.TimeF0S54;
            case 1:return Rez.Fonts.TimeF0S58;
            case 2:return Rez.Fonts.TimeF0S64;
            case 3:return Rez.Fonts.TimeF0S68;
            case 4:return Rez.Fonts.TimeF1S54;
            case 5:return Rez.Fonts.TimeF1S58;
            case 6:return Rez.Fonts.TimeF1S64;
            case 7:return Rez.Fonts.TimeF1S68;
            case 8:return Rez.Fonts.TimeF2S54;
            case 9:return Rez.Fonts.TimeF2S58;
            case 10:return Rez.Fonts.TimeF2S64;
            case 11:return Rez.Fonts.TimeF2S68;
        }}
        if(group.equals("circle")){switch(family*4+size){
            case 0:return Rez.Fonts.CircleF0S18;
            case 1:return Rez.Fonts.CircleF0S22;
            case 2:return Rez.Fonts.CircleF0S22;
            case 3:return Rez.Fonts.CircleF0S22;
            case 4:return Rez.Fonts.CircleF1S18;
            case 5:return Rez.Fonts.CircleF1S22;
            case 6:return Rez.Fonts.CircleF1S22;
            case 7:return Rez.Fonts.CircleF1S22;
            case 8:return Rez.Fonts.CircleF2S18;
            case 9:return Rez.Fonts.CircleF2S22;
            case 10:return Rez.Fonts.CircleF2S26;
            case 11:return Rez.Fonts.CircleF2S28;
        }}
        if(group.equals("liveheart")){switch(family*4+size){
            case 0:return Rez.Fonts.LiveHeartF0S18;
            case 1:return Rez.Fonts.LiveHeartF0S22;
            case 2:return Rez.Fonts.LiveHeartF0S22;
            case 3:return Rez.Fonts.LiveHeartF0S22;
            case 4:return Rez.Fonts.LiveHeartF1S18;
            case 5:return Rez.Fonts.LiveHeartF1S22;
            case 6:return Rez.Fonts.LiveHeartF1S22;
            case 7:return Rez.Fonts.LiveHeartF1S22;
            case 8:return Rez.Fonts.LiveHeartF2S18;
            case 9:return Rez.Fonts.LiveHeartF2S22;
            case 10:return Rez.Fonts.LiveHeartF2S26;
            case 11:return Rez.Fonts.LiveHeartF2S28;
        }}
        if(group.equals("seconds")){switch(family*4+size){
            case 0:return Rez.Fonts.SecondF0S18;
            case 1:return Rez.Fonts.SecondF0S22;
            case 2:return Rez.Fonts.SecondF0S26;
            case 3:return Rez.Fonts.SecondF0S28;
            case 4:return Rez.Fonts.SecondF1S18;
            case 5:return Rez.Fonts.SecondF1S22;
            case 6:return Rez.Fonts.SecondF1S26;
            case 7:return Rez.Fonts.SecondF1S28;
            case 8:return Rez.Fonts.SecondF2S18;
            case 9:return Rez.Fonts.SecondF2S22;
            case 10:return Rez.Fonts.SecondF2S26;
            case 11:return Rez.Fonts.SecondF2S28;
        }}
        return Rez.Fonts.DataF0S14;
    }
    var _ids as Array<ResourceId> = [];
    var _fonts as Array = [];
    function reset() { _ids = []; _fonts = []; }
    function load(id as ResourceId) {
        for(var i=0;i<_ids.size();i++){if(_ids[i]==id){return _fonts[i];}}
        if(_ids.size()>=1){_ids.remove(_ids[0]);_fonts.remove(_fonts[0]);}
        var font=WatchUi.loadResource(id) as Graphics.FontType;
        _ids.add(id);_fonts.add(font);return font;
    }
    function data(family,size) { return load(id("data",family,size)); }
    function fit(dc,group,family,size,text,width,height) {
        for (var i=size;i>=0;i--) {
            var font=load(id(group,family,i));
            if (dc.getTextWidthInPixels(text,font)<=width && dc.getFontHeight(font)<=height) { return font; }
            font=null; // Release a rejected size before loading the next bitmap font.
        }
        return load(id(group,family,0));
    }
}
