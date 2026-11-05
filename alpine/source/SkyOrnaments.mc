import Toybox.Graphics;
import Toybox.Math;
import Toybox.WatchUi;
// Tiny original native-size sprites; no resources are loaded while disabled.
module SkyOrnaments {
 function p(v as Numeric) as Number {return Math.round(v*Device.S).toNumber();}
 function glyph(dc,bitmap,x,y) {
  var w=bitmap.getWidth();var h=bitmap.getHeight();var left=p(x)-(w/2).toNumber();var top=p(y)-(h/2).toNumber();
  var edge=Device.H;
  for(var i=left;i<left+w;i++) {
   if(i<0 || i>=Device.W) {continue;}
   var ridge=Device.SKYLINE[i]-Device.SKYSHIFT;if(ridge<edge) {edge=ridge;}
  }
  var bottom=top+h;if(bottom>edge) {bottom=edge;}
  if(Device.MONO && Settings.top!=11 && top<p(20)) {top=p(20);}
  if(bottom>top) {dc.setClip(left,top,w,bottom-top);dc.drawBitmap(left,p(y)-(h/2).toNumber(),bitmap);dc.clearClip();}
 }
 function draw(dc,mode,stamp) {
  if(mode<1 || mode>3) {return;}
  var night=Sky.phase==4;var drift=(stamp/300).toNumber()%9-4;
  var bitmap=null;
  if(mode==1 || mode==3) {
   bitmap=WatchUi.loadResource(night ? Rez.Drawables.BirdNight : Rez.Drawables.BirdDay);
   glyph(dc,bitmap,(Device.MONO ? 24 : 44)+drift,Device.MONO ? 28 : 63);
   glyph(dc,bitmap,(Device.MONO ? 43 : 65)+drift,Device.MONO ? 22 : 53);bitmap=null;
  }
  if(mode==2 || mode==3) {
   bitmap=WatchUi.loadResource(night ? Rez.Drawables.PlaneNight : Rez.Drawables.PlaneDay);
   glyph(dc,bitmap,(Device.MONO ? 88 : 210)-drift,Device.MONO ? 24 : 57);
  }
 }
}
