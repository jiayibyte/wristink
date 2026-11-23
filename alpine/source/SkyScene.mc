import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;

// The sky for the real time and weather: day sky with the Sun, night sky with
// the Moon (its actual phase) and stars, dawn and dusk colours, and a grey sky
// with no Sun, Moon or stars when it is cloudy, raining, snowing or foggy.
// The Sun and Moon follow their computed rise-to-set progress (Sky); the arcs
// are illustrative. Colour screens paint this behind the mountain, whose sky is
// transparent; 1-bit screens draw small objects in the top-left, which is sky
// in all four mountains (measured: ridges stay below 28% of the height there).
module SkyScene {
    const STARS as Array<Number> = [10,8, 22,15, 34,6, 46,12, 58,5, 70,10, 82,16, 16,26, 40,22, 64,24, 88,30, 28,33];
    const MONO_STARS as Array<Number> = [6,5, 14,19, 27,4, 31,16, 9,12, 24,23];

    function overcast() as Boolean {
        var w=Data.weather;
        return w==WeatherStyle.CLOUDY || w==WeatherStyle.RAIN || w==WeatherStyle.SNOW || w==WeatherStyle.STORM || w==WeatherStyle.FOG;
    }
    function phase() as Number {return Sky.ready ? Sky.phase : 2;}

    // Top and horizon colours (AMOLED) or four flat bands (64-colour MIP).
    function amoledEnds() as Array<Number> {
        var p=phase();var w=Data.weather;
        if(w==WeatherStyle.FOG) {return p==4 ? [0x101418,0x343A40] : [0x7E868C,0xC9CED2];}
        if(overcast()) {return p==4 ? [0x0A0D12,0x2A3038] : (p==2 ? [0x58636D,0xAAB3BA] : [0x3B3D4C,0x988A88]);}
        if(p==1) {return [0x2B3266,0xF0A88C];}
        if(p==3) {return [0x2A1E4A,0xF0956A];}
        if(p==4) {return [0x030812,0x1C3550];}
        return [0x2E7BC8,0xBEE3F6];
    }
    function mipBands() as Array<Number> {
        var p=phase();
        if(overcast()) {return p==4 ? [0x000000,0x000000,0x000055,0x555555] : (p==2 ? [0x555555,0x555555,0xAAAAAA,0xAAAAAA] : [0x000055,0x555555,0xAA5555,0xAAAAAA]);}
        if(p==1) {return [0x000055,0x5555AA,0xAA55AA,0xFFAAAA];}
        if(p==3) {return [0x000055,0x550055,0xAA5555,0xFFAA55];}
        if(p==4) {return [0x000000,0x000000,0x000055,0x000055];}
        return [0x0055AA,0x0055FF,0x55AAFF,0xAAFFFF];
    }
    function mix(a as Number,b as Number,k as Float) as Number {
        var r=((a>>16)&255)+(((b>>16)&255)-((a>>16)&255))*k;
        var g=((a>>8)&255)+(((b>>8)&255)-((a>>8)&255))*k;
        var bl=(a&255)+((b&255)-(a&255))*k;
        return (r.toNumber()<<16)|(g.toNumber()<<8)|bl.toNumber();
    }
    // Sky colour at height y; used again for the Moon's shadow.
    function colourAt(y as Numeric) as Number {
        var end=Device.H*0.62;var k=y>=end ? 1.0 : (y<0 ? 0.0 : (y/end).toFloat());
        if(Device.AMOLED) {var e=amoledEnds();var steps=10;return mix(e[0],e[1],((k*(steps-1)).toNumber()).toFloat()/(steps-1));}
        var b=mipBands();var i=(k*4).toNumber();return b[i>3 ? 3 : i];
    }

    // Colour screens, before the mountain bitmap.
    function paint(dc) as Void {
        var end=Device.H*0.62;var steps=Device.AMOLED ? 10 : 4;
        for(var i=0;i<steps;i++) {
            var y0=(end*i/steps).toNumber();var y1=i==steps-1 ? Device.H : (end*(i+1)/steps).toNumber();
            dc.setColor(colourAt(y0+1),colourAt(y0+1));dc.fillRectangle(0,y0,Device.W,y1-y0);
        }
        if(overcast()) {return;}
        var p=phase();var partly=Data.weather==WeatherStyle.PARTLY;
        var moon=p==4 && Sky.ready && Sky.showMoon(0);
        var mx=0;var my=0;var mr=Device.W*0.045;
        if(moon) {mx=arcX(Sky.moonProgress);my=arcY(Sky.moonProgress);}
        if(p==4) {stars(dc,moon,mx,my,mr*2.4,partly);}
        if(p!=4 && Sky.ready && Sky.sunVisible) {
            var c=Device.AMOLED ? (p==2 ? 0xFFE27A : 0xFFB25E) : (p==2 ? 0xFFFF55 : 0xFFAA55);
            dc.setColor(c,Graphics.COLOR_TRANSPARENT);dc.fillCircle(arcX(Sky.sunProgress),arcY(Sky.sunProgress),Device.W*0.055);
        }
        if(moon) {moonDisc(dc,mx,my,mr,Device.AMOLED ? 0xF3EEDC : 0xFFFFAA);}
        if(partly) {
            var c=p==4 ? (Device.AMOLED ? 0x4A5260 : 0x555555) : (p==2 ? (Device.AMOLED ? 0xEEF3F7 : 0xFFFFFF) : (Device.AMOLED ? 0xE8C4C0 : 0xFFAAAA));
            cloud(dc,Device.W*0.30,Device.H*0.24,Device.W*0.05,c);cloud(dc,Device.W*0.70,Device.H*0.14,Device.W*0.04,c);
        }
    }
    function arcX(progress) as Number {return (Device.W*(0.12+0.76*progress)).toNumber();}
    function arcY(progress) as Number {return (Device.H*(0.50-0.34*Math.sin(Math.PI*progress))).toNumber();}
    function stars(dc,moon,mx,my,clear,partly) as Void {
        var size=Device.W/208;if(size<1) {size=1;}
        for(var i=0;i<STARS.size();i+=2) {
            if(partly && i%4==2) {continue;}
            var x=Device.W*STARS[i]/100;var y=Device.H*STARS[i+1]/100;
            if(moon && (x-mx)*(x-mx)+(y-my)*(y-my)<clear*clear) {continue;}
            var c=i%6==4 ? (Device.AMOLED ? 0x8C9AB8 : 0xAAAAAA) : (Device.AMOLED ? 0xE6EEFF : 0xFFFFFF);
            dc.setColor(c,Graphics.COLOR_TRANSPARENT);dc.fillRectangle(x,y,size,size);
        }
    }
    // The lit disc, then a sky-coloured disc that leaves the actual phase.
    // Waxing is lit on the right in the northern hemisphere.
    function moonDisc(dc,x,y,r,lit) as Void {
        dc.setColor(lit,Graphics.COLOR_TRANSPARENT);dc.fillCircle(x,y,r);
        var light=Sky.illumination;if(light>=0.97) {return;}
        var side=Sky.moonPhase<0.5 ? -1 : 1;if(Data.latitude!=null && Data.latitude<0) {side=-side;}
        var shadow=Device.MONO ? Graphics.COLOR_BLACK : colourAt(y);
        dc.setColor(shadow,Graphics.COLOR_TRANSPARENT);dc.fillCircle(x+side*2*r*light,y,r);
    }
    function cloud(dc,x,y,r,c) as Void {
        dc.setColor(c,Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(x-r,y,r*0.8);dc.fillCircle(x,y-r*0.45,r);dc.fillCircle(x+r,y,r*0.75);
        dc.fillRectangle(x-r*1.6,y,r*3.2,r*0.75);
    }

    // 1-bit screens, after the opaque mountain bitmap.
    function paintMono(dc) as Void {
        if(overcast()) {return;}
        var p=phase();var x=Device.W*0.18;var y=Device.H*0.13;var r=Device.W*0.055;
        dc.setColor(Graphics.COLOR_WHITE,Graphics.COLOR_TRANSPARENT);
        if(p==4) {
            for(var i=0;i<MONO_STARS.size();i+=2) {
                if(Data.weather==WeatherStyle.PARTLY && i%4==2) {continue;}
                var sx=Device.W*MONO_STARS[i]/100;var sy=Device.H*MONO_STARS[i+1]/100;
                if((sx-x)*(sx-x)+(sy-y)*(sy-y)<r*r*4) {continue;}
                dc.drawPoint(sx,sy);
            }
            if(Sky.ready && Sky.showMoon(0)) {moonDisc(dc,x,y,r,Graphics.COLOR_WHITE);}
        } else if(!Sky.ready || Sky.sunVisible) {
            dc.drawCircle(x,y,r*0.7);
            for(var a=0;a<8;a++) {
                var t=a*Math.PI/4;var c=Math.cos(t);var s=Math.sin(t);
                dc.drawLine(x+c*r,y+s*r,x+c*r*1.35,y+s*r*1.35);
            }
        }
    }
}
