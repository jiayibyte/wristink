import Toybox.Graphics;
import Toybox.WatchUi;
import Toybox.System;
import Toybox.Math;
module NativeStyle {
    var _icons;var _upper;var _moon;var _wind;var _native=null;
    function enabled(){if(_native==null){var part=System.getDeviceSettings().partNumber;_native=part.equals("006-B4585-00") || part.equals("006-B4759-00");}return _native;}
    function reset(){_icons=null;_upper=null;_moon=null;_wind=null;}
    function windIndex(bearing){var value=bearing-Math.floor(bearing/360.0)*360;return Math.round(value*32/360).toNumber()%32;}
    function windArrow(dc,cx,cy,bearing,ink,paper){
        if(_wind==null){_wind=WatchUi.loadResource(Rez.Fonts.ShaftWindArrow);}
        var codes="0123456789ABCDEFGHIJKLMNOPQRSTUV";var i=windIndex(bearing);
        dc.setColor(ink,Graphics.COLOR_TRANSPARENT);dc.drawText(cx-7,cy-7,_wind,codes.substring(i,i+1),Graphics.TEXT_JUSTIFY_LEFT);dc.setColor(ink,paper);
    }
    function upperFont(){if(_upper==null){_upper=WatchUi.loadResource(Rez.Fonts.UpperDetails);}return _upper;}
    function activity(dc,x,y,ink,paper){dc.setColor(ink,paper);dc.drawText(x,y,upperFont(),"Q",Graphics.TEXT_JUSTIFY_LEFT);}
    function battery(dc,x,y,ink,paper,percent){
        var level=Math.floor(percent*8/100).toNumber();level=level<0 ? 0 : (level>8 ? 8 : level);
        var codes="012345678";dc.setColor(ink,paper);
        dc.drawText(x,y,upperFont(),codes.substring(level,level+1),Graphics.TEXT_JUSTIFY_LEFT);
    }
    function circleIcon(dc,kind,cx,y,ink,paper){
        if(kind!=6 && kind!=15){return false;}
        var shape=paper==Graphics.COLOR_WHITE && FacePrefs.get("cellsSource")==0 && FacePrefs.get("ringSource")==0 ? "m" : "l";
        dc.setColor(ink,paper);dc.drawText(cx-6,y,upperFont(),shape,Graphics.TEXT_JUSTIFY_LEFT);return true;
    }
    function moon(dc,cx,cy,phase,ink,paper){
        if(_moon==null){_moon=WatchUi.loadResource(Rez.Fonts.UpperMoon);}
        var index=Math.round(phase*32).toNumber()%32;
        var codes="0123456789ABCDEFGHIJKLMNOPQRSTUV";
        dc.setColor(ink,paper);dc.drawText(cx-7,cy-7,_moon,codes.substring(index,index+1),Graphics.TEXT_JUSTIFY_LEFT);
    }
    function icon(dc,kind,x,y,ink,paper){
        var text=null;
        switch(kind){
            case 1:case 17:battery(dc,x,y,ink,paper,FaceDraw.batteryPercent);return true;
            case 2:text="Ä";break;case 3:text="Q";break;case 4:text="e";break;
            case 5:text="X";break;case 6:case 15:text="l";break;
            case 8:text="c";break;case 9:text="b";break;case 10:text="Í";break;
            case 11:text="Â";break;case 12:text="g";break;case 19:text="A";break;
            case 20:case 21:case 22:case 23:text="o";break;case 24:text="r";break;
            case 25:text="R";break;case 26:text="È";break;
        }
        if(text==null){return false;}
        if(_icons==null){_icons=WatchUi.loadResource(Rez.Fonts.GarminStandardIcons);}
        dc.setColor(ink,paper);dc.drawText(x,y,_icons,text,Graphics.TEXT_JUSTIFY_LEFT);return true;
    }
}
