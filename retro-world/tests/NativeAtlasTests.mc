import Toybox.Test;
class AtlasSizeFixture {
 function getWidth() {return 380;}
 function getHeight() {return 60;}
}
class NativeAtlasDcProbe {
 var clipWidth=0;var clipHeight=0;var clipX=0;var bitmapX=0;
 function setClip(x,y,w,h) {clipX=x;clipWidth=w;clipHeight=h;}
 function drawBitmap(x,y,bitmap) {bitmapX=x;}
 function clearClip() {}
}
(:test)
function fractionalScaleUsesActualAtlasStrideWithoutAdjacentDigitBleed(logger) {
 // Venu Sq 2: 22 * rounded scale is 37.49999, but native cells are 38px.
 var dc=new NativeAtlasDcProbe();var wrapper=new NativeFaceDc(1.704545,10,30);wrapper.bind(dc);
 wrapper.sprite(new AtlasSizeFixture(),8,102,111,22,35,10);
 Test.assertEqual(dc.clipWidth,38);Test.assertEqual(dc.clipHeight,60);
 Test.assertEqual(dc.clipX-dc.bitmapX,304);
 return true;
}

class AlwaysOnDcProbe {
 var pen=7;var badStroke=false;var lines=0;
 function clearClip() {}
 function setClip(x,y,w,h) {}
 function setColor(ink,paper) {}
 function clear() {}
 function setPenWidth(width) {pen=width;}
 function drawBitmap(x,y,bitmap) {}
 function fillRectangle(x,y,w,h) {}
 function drawLine(x1,y1,x2,y2) {lines++;if(pen!=1) {badStroke=true;}}
}
(:test)
function alwaysOnRestMaskResetsInheritedAnalogPenWidth(logger) {
 var dc=new AlwaysOnDcProbe();AlwaysOn.draw(dc,new AtlasSizeFixture(),14,50,2);
 Test.assert(dc.lines>0);Test.assert(!dc.badStroke);Test.assertEqual(dc.pen,1);
 return true;
}

class LegacyBufferFixture {
 function getDc() {return new AtlasSizeFixture();}
}
(:test)
function legacyBufferedBitmapDimensionsComeFromItsDrawingContext(logger) {
 var dc=new NativeAtlasDcProbe();var wrapper=new NativeFaceDc(1.704545,10,30);wrapper.bind(dc);
 wrapper.sprite(new LegacyBufferFixture(),0,17,56,89,29,1);
 Test.assertEqual(dc.clipWidth,380);Test.assertEqual(dc.clipHeight,60);
 return true;
}
