import Toybox.Application;
import Toybox.Lang;
module Mode {
 const DEMO=true;const SCENE=0;const LAT=39.9d;const LON=116.4d;
 var STAMP=0;var MINUTES=0;var WEATHER=1;var DATE="";
 function refresh() {
  var i=Application.Properties.getValue("PreviewFrame");if(!(i instanceof Number) || i<0 || i>=10) {i=0;}
  STAMP=[1782014400, 1781988600, 1782042000, 1793026800, 1793005020, 1793058300, 1782014400, 1782014400, 1782014400, 1782014400][i];
  MINUTES=[720, 290, 1180, 1380, 1017, 465, 720, 720, 720, 720][i];
  WEATHER=[1, 1, 1, 1, 1, 1, 4, 5, 3, 7][i];
  DATE=["SUN 06/21", "SUN 06/21", "SUN 06/21", "MON 10/26", "MON 10/26", "TUE 10/27", "SUN 06/21", "SUN 06/21", "SUN 06/21", "SUN 06/21"][i];
 }
}
