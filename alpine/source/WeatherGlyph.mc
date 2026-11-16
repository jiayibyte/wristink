import Toybox.Graphics;
import Toybox.Math;
module WeatherGlyph {
    function n(v) {return Math.round(v*Device.S).toNumber();}
    function draw(dc,x,y,ink,paper) {
        var kind=Data.weather;dc.setColor(ink,paper);dc.setPenWidth(1);
        if(kind==WeatherStyle.UNKNOWN) {dc.drawLine(x-n(5),y,x+n(5),y);return;}
        if(kind==WeatherStyle.CLEAR) {
            if(Sky.phase==4) {
                var r=n(5);var angle=Sky.moonPhase*2*Math.PI;var flip=Data.latitude!=null && Data.latitude<0 ? -1 : 1;
                dc.drawCircle(x,y,r);
                for(var yy=-r+1;yy<r;yy++) {for(var xx=-r+1;xx<r;xx++) {
                    var rr=(xx*xx+yy*yy).toFloat()/(r*r);
                    if(rr<=1 && flip*xx.toFloat()/r*Math.sin(angle)-Math.sqrt(1-rr)*Math.cos(angle)>0) {dc.drawPoint(x+xx,y+yy);}
                }}
            } else {
                dc.fillCircle(x,y,n(3));
                for(var i=0;i<8;i++) {var a=i*Math.PI/4;dc.drawLine(x+n(5*Math.cos(a)),y+n(5*Math.sin(a)),x+n(7*Math.cos(a)),y+n(7*Math.sin(a)));}
            }
            return;
        }
        if(kind==WeatherStyle.FOG) {
            for(var j=-1;j<=1;j++) {dc.drawLine(x-n(7),y+n(j*3),x+n(7),y+n(j*3));}return;
        }
        if(kind==WeatherStyle.PARTLY) {dc.drawCircle(x-n(5),y-n(3),n(3));}
        dc.fillCircle(x-n(4),y,n(3));dc.fillCircle(x,y-n(2),n(4));dc.fillCircle(x+n(4),y,n(3));dc.fillRectangle(x-n(6),y,n(12),n(3));
        if(kind==WeatherStyle.RAIN || kind==WeatherStyle.STORM) {
            dc.drawLine(x-n(4),y+n(5),x-n(5),y+n(7));dc.drawLine(x+n(1),y+n(5),x,y+n(7));
            if(kind==WeatherStyle.STORM) {dc.drawLine(x+n(5),y+n(4),x+n(3),y+n(6));dc.drawLine(x+n(3),y+n(6),x+n(5),y+n(6));}
        } else if(kind==WeatherStyle.SNOW) {
            for(var k=-1;k<=1;k+=2) {var sx=x+n(k*4);var sy=y+n(6);dc.drawLine(sx-n(1),sy,sx+n(1),sy);dc.drawLine(sx,sy-n(1),sx,sy+n(1));}
        }
    }
}
