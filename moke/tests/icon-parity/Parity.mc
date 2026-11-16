import Toybox.Application;import Toybox.WatchUi;import Toybox.Test;import Toybox.Graphics;
class ParityApp extends Application.AppBase{function initialize(){AppBase.initialize();}function getInitialView(){return [new WatchUi.WatchFace()];}}
class CommandDc {var calls="";function record(op,args){calls+=op+":";for(var i=0;i<args.size();i++){calls+=args[i].format("%.4f")+",";}calls+=";";}
function setColor(a0,a1){record("setColor",[a0,a1]);}
function setPenWidth(a0){record("setPenWidth",[a0]);}
function drawLine(a0,a1,a2,a3){record("drawLine",[a0,a1,a2,a3]);}
function drawRectangle(a0,a1,a2,a3){record("drawRectangle",[a0,a1,a2,a3]);}
function fillRectangle(a0,a1,a2,a3){record("fillRectangle",[a0,a1,a2,a3]);}
function drawCircle(a0,a1,a2){record("drawCircle",[a0,a1,a2]);}
function fillCircle(a0,a1,a2){record("fillCircle",[a0,a1,a2]);}
function fillEllipse(a0,a1,a2,a3){record("fillEllipse",[a0,a1,a2,a3]);}
function drawPoint(a0,a1){record("drawPoint",[a0,a1]);}
function fillPolygon(points){var flat=[];for(var i=0;i<points.size();i++){flat.add(points[i][0]);flat.add(points[i][1]);}record("fillPolygon",flat);}}
(:test) function compactIconsPreserveEveryDrawingCommand(logger){
for(var theme=0;theme<2;theme++){for(var kind=0;kind<=28;kind++){var a=new CommandDc();var b=new CommandDc();var ink=theme==0 ? Graphics.COLOR_BLACK : Graphics.COLOR_WHITE;var paper=theme==0 ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK;ReferenceIcons.draw(a,kind,21,31,ink,paper,86,4);LegacyIcons.draw(b,kind,21,31,ink,paper,86,4);Test.assertEqual(a.calls,b.calls);}}return true;}
