import Toybox.Graphics;
import Toybox.Math;
module AlwaysOn {
    var _digits;
    function draw(dc,atlas,hour,minute,stamp) {
        dc=DeviceDrawing.raw(dc);dc.clearClip();dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_BLACK);dc.clear();dc.setPenWidth(1);
        var w=(atlas.getWidth()/10).toNumber();var h=atlas.getHeight();
        var gap=DeviceDrawing.size(2,DeviceProfile.SCALE);var colon=DeviceDrawing.size(5,DeviceProfile.SCALE);
        var width=4*w+2*gap+colon;
        var phase=stamp%4;var dx=phase%2==0 ? -3 : 3;var dy=phase<2 ? -3 : 3;
        var x=((DeviceProfile.WIDTH-width)/2).toNumber()+dx;var y=((DeviceProfile.HEIGHT-h)/2).toNumber()+dy;
        digit(dc,atlas,(hour/10).toNumber(),x,y,w,h);digit(dc,atlas,hour%10,x+w+gap,y,w,h);
        var mx=x+2*w+gap+colon;
        digit(dc,atlas,(minute/10).toNumber(),mx,y,w,h);digit(dc,atlas,minute%10,mx+w+gap,y,w,h);
        if(stamp%2==0) {
            dc.setColor(DeviceProfile.AOD_INK,Graphics.COLOR_BLACK);
            var dot=DeviceDrawing.size(1,DeviceProfile.SCALE);
            dc.fillRectangle(x+2*w+gap+((colon-dot)/2).toNumber(),y+(h/3).toNumber(),dot,dot);
            dc.fillRectangle(x+2*w+gap+((colon-dot)/2).toNumber(),y+(2*h/3).toNumber(),dot,dot);
        }
        // A global diagonal mask guarantees every physical pixel rests at least
        // once in four minute frames, even where shifted digit outlines overlap.
        dc.setClip(x,y,width,h);dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_BLACK);
        var start=x-h;
        while((start-y+4096)%4!=phase) {start++;}
        for(var line=start;line<x+width;line+=4) {dc.drawLine(line,y,line+h-1,y+h-1);}
        dc.clearClip();
    }
    function digit(dc,atlas,n,x,y,w,h) {dc.setClip(x,y,w,h);dc.drawBitmap(x-n*w,y,atlas);dc.clearClip();}
}
