// Coordinates stay in the approved 176px design; assets are compiled at native scale.
import Toybox.Math;
import Toybox.Graphics;
import Toybox.Lang;
module DeviceDrawing {
    var _surface;
    var _circle;
    function target(dc){
        if(DeviceProfile.SCALE==1 && DeviceProfile.X==0 && DeviceProfile.Y==0){return dc;}
        if(_surface==null){_surface=new ScaledFaceDc(DeviceProfile.SCALE,DeviceProfile.X,DeviceProfile.Y);}
        _surface.bind(dc);return _surface;
    }
    function circleTarget(dc){
        if(DeviceProfile.CIRCLE_SCALE==DeviceProfile.SCALE && DeviceProfile.CIRCLE_X==DeviceProfile.X && DeviceProfile.CIRCLE_Y==DeviceProfile.Y){return dc;}
        if(_circle==null){_circle=new ScaledFaceDc(DeviceProfile.CIRCLE_SCALE,DeviceProfile.CIRCLE_X,DeviceProfile.CIRCLE_Y);}
        _circle.bind(dc instanceof ScaledFaceDc ? dc._dc : dc);return _circle;
    }
}
class ScaledFaceDc {
    var _dc;var _scale;var _x;var _y;
    function initialize(scale,x,y){_scale=scale;_x=x;_y=y;}
    function bind(dc){_dc=dc;}
    function rounded(v){if(Math has :round){return Math.round(v);}var shifted=v+0.5;var n=shifted.toNumber();return shifted<n ? n-1 : n;}
    function px(v){return rounded(_x+v*_scale);}
    function py(v){return rounded(_y+v*_scale);}
    function length(v){return rounded(v*_scale);}
    function setColor(ink,paper){_dc.setColor(ink,paper);}
    function clear(){_dc.clear();}
    function clearClip(){if(_dc has :clearClip){_dc.clearClip();}}
    function setClip(x,y,w,h){if(_dc has :setClip){_dc.setClip(px(x),py(y),px(x+w)-px(x),py(y+h)-py(y));}}
    function setPenWidth(w){var n=length(w);_dc.setPenWidth(n<1 ? 1 : n);}
    function getFontHeight(font){return _dc.getFontHeight(font)/_scale;}
    function getTextWidthInPixels(text,font){return _dc.getTextWidthInPixels(text,font)/_scale;}
    function drawText(x,y,font,text,justify){_dc.drawText(px(x),py(y),font,text,justify);}
    function drawBitmap(x,y,bitmap){_dc.drawBitmap(px(x),py(y),bitmap);}
    function drawLine(x1,y1,x2,y2){_dc.drawLine(px(x1),py(y1),px(x2),py(y2));}
    function drawPoint(x,y){var w=px(x+1)-px(x);var h=py(y+1)-py(y);_dc.fillRectangle(px(x),py(y),w<1 ? 1 : w,h<1 ? 1 : h);}
    function drawRectangle(x,y,w,h){_dc.drawRectangle(px(x),py(y),px(x+w)-px(x),py(y+h)-py(y));}
    function fillRectangle(x,y,w,h){_dc.fillRectangle(px(x),py(y),px(x+w)-px(x),py(y+h)-py(y));}
    function drawCircle(x,y,r){_dc.drawCircle(px(x),py(y),length(r));}
    function fillCircle(x,y,r){_dc.fillCircle(px(x),py(y),length(r));}
    function fillEllipse(x,y,a,b){_dc.fillEllipse(px(x),py(y),length(a),length(b));}
    function drawArc(x,y,r,dir,start,end){_dc.drawArc(px(x),py(y),length(r),dir,start,end);}
    function fillPolygon(points as Array){var output=new [points.size()];for(var i=0;i<points.size();i++){var point=points[i] as Array;output[i]=[px(point[0]),py(point[1])];}_dc.fillPolygon(output);}
}
