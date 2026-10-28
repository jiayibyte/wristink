import Toybox.Graphics;
import Toybox.Math;
import Toybox.Lang;
module DeviceDrawing {
    var _main;var _circle;var _mapCache;var _circleCache;
    function raw(dc) {return dc instanceof NativeFaceDc ? dc._dc : dc;}
    function target(dc) {
        if(DeviceProfile.SCALE==1 && DeviceProfile.X==0 && DeviceProfile.Y==0 && !DeviceProfile.COLOR) {return dc;}
        if(_main==null) {_main=new NativeFaceDc(DeviceProfile.SCALE,DeviceProfile.X,DeviceProfile.Y);}
        _main.bind(raw(dc));return _main;
    }
    function circle(dc) {
        if(DeviceProfile.CIRCLE_SCALE==1 && DeviceProfile.CIRCLE_X==0 && DeviceProfile.CIRCLE_Y==0 && !DeviceProfile.COLOR) {return raw(dc);}
        if(_circle==null) {_circle=new NativeFaceDc(DeviceProfile.CIRCLE_SCALE,DeviceProfile.CIRCLE_X,DeviceProfile.CIRCLE_Y);}
        _circle.bind(raw(dc));return _circle;
    }
    function cache(dc,isCircle) {
        var scale=isCircle ? DeviceProfile.CIRCLE_SCALE : DeviceProfile.SCALE;
        if(scale==1 && !DeviceProfile.COLOR) {return dc;}
        if(isCircle) {
            if(_circleCache==null) {_circleCache=new NativeFaceDc(scale,0,0);}
            _circleCache.bind(dc);return _circleCache;
        }
        if(_mapCache==null) {_mapCache=new NativeFaceDc(scale,0,0);}
        _mapCache.bind(dc);return _mapCache;
    }
    function size(v,scale) {var n=Math.round(v*scale).toNumber();return n<1 ? 1 : n;}
    function buffer(w,h,scale) {
        var options={:width=>size(w,scale),:height=>size(h,scale)};
        // MIP resources can carry device-specific transparent palette slots.
        // Retain the native MIP palette; AMOLED uses a bounded shared palette.
        if(Graphics has :createBufferedBitmap) {
            if(DeviceProfile.COLOR) {options[:palette]=[0x000000,DeviceProfile.PAPER,DeviceProfile.TEAL,DeviceProfile.AMBER,DeviceProfile.AOD_INK,Graphics.COLOR_TRANSPARENT];}
            return Graphics.createBufferedBitmap(options);
        }
        return new Graphics.BufferedBitmap(options);
    }
    function resolve(buffer) {return (buffer has :get) ? buffer.get() : buffer;}
    function metrics(bitmap) {return (bitmap has :getWidth) ? bitmap : bitmap.getDc();}
    function sprite(dc,bitmap,index,x,y,w,h,count) {
        if(dc instanceof NativeFaceDc) {dc.sprite(bitmap,index,x,y,w,h,count);return;}
        var shape=DeviceDrawing.metrics(bitmap);var nw=(shape.getWidth()/count).toNumber();var nh=shape.getHeight();
        dc.setClip(x,y,nw,nh);dc.drawBitmap(x-index*nw,y,bitmap);dc.clearClip();
    }
}
// Resource images and bitmap fonts are already native-size: no whole-frame
// buffer or scaled bitmap operation is performed by the watch at runtime.
class NativeFaceDc {
    var _dc;var _scale;var _x;var _y;var _emptyClip=false;
    function initialize(scale,x,y) {_scale=scale;_x=x;_y=y;}
    function bind(dc) {_dc=dc;_emptyClip=false;}
    function px(v) {return Math.round(_x+v*_scale).toNumber();}
    function py(v) {return Math.round(_y+v*_scale).toNumber();}
    function length(v) {return DeviceDrawing.size(v,_scale);}
    function setColor(ink,paper) {
        _dc.setColor(ink==Graphics.COLOR_WHITE ? DeviceProfile.PAPER : ink,paper==Graphics.COLOR_WHITE ? DeviceProfile.PAPER : paper);
    }
    function clear() {_dc.clear();}
    function clearClip() {_emptyClip=false;_dc.clearClip();}
    function setClip(x,y,w,h) {var nw=px(x+w)-px(x);var nh=py(y+h)-py(y);_emptyClip=nw<=0 || nh<=0;if(!_emptyClip) {_dc.setClip(px(x),py(y),nw,nh);}}
    function setPenWidth(w) {_dc.setPenWidth(length(w));}
    function getTextWidthInPixels(text,font) {return _dc.getTextWidthInPixels(text,font)/_scale;}
    function drawText(x,y,font,text,justify) {_dc.drawText(px(x),py(y),font,text,justify);}
    function drawBitmap(x,y,bitmap) {if(!_emptyClip) {_dc.drawBitmap(px(x),py(y),bitmap);}}
    function drawLine(x1,y1,x2,y2) {_dc.drawLine(px(x1),py(y1),px(x2),py(y2));}
    function drawPoint(x,y) {_dc.fillRectangle(px(x),py(y),length(1),length(1));}
    function fillRectangle(x,y,w,h) {_dc.fillRectangle(px(x),py(y),length(w),length(h));}
    function drawCircle(x,y,r) {_dc.drawCircle(px(x),py(y),length(r));}
    function fillCircle(x,y,r) {_dc.fillCircle(px(x),py(y),length(r));}
    function sprite(bitmap,index,x,y,w,h,count) {
        var shape=DeviceDrawing.metrics(bitmap);var nw=(shape.getWidth()/count).toNumber();var nh=shape.getHeight();var xx=px(x);var yy=py(y);
        _dc.setClip(xx,yy,nw,nh);_dc.drawBitmap(xx-index*nw,yy,bitmap);_dc.clearClip();
    }
}
