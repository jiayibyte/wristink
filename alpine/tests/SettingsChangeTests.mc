import Toybox.Application;
import Toybox.Lang;
import Toybox.Test;

(:test)
function phoneSettingsAcceptLooseTypes(logger) {
    // Garmin Connect may hand values back as Long, Float or a numeric String.
    Test.assertEqual(Settings.toNumber(2),2);
    Test.assertEqual(Settings.toNumber(2l),2);
    Test.assertEqual(Settings.toNumber(2.0),2);
    Test.assertEqual(Settings.toNumber("2"),2);
    Test.assert(Settings.toNumber("x")==null);
    Test.assert(Settings.toNumber(null)==null);
    Test.assertEqual(Settings.number("NoSuchKey",3,0,9),3);
    Test.assertEqual(Settings.flag("NoSuchKey",true),true);
    return true;
}

(:test)
function phoneSettingsChangeReachesTheFace(logger) {
    var app=Application.getApp() as AlpineApp;
    var view=new AlpineView();app.view=view;
    var keys=["Mountain","PanelStyle","Left","Seconds","TimeFormat"];var old=[];
    for(var i=0;i<keys.size();i++) {old.add(Application.Properties.getValue(keys[i]));}
    Application.Properties.setValue("Mountain",2);
    Application.Properties.setValue("PanelStyle",3);
    Application.Properties.setValue("Left",4);
    Application.Properties.setValue("Seconds",false);
    Application.Properties.setValue("TimeFormat",2);
    view._minute=100;
    app.onSettingsChanged();
    Test.assertEqual(Settings.mountain,2);
    Test.assertEqual(Settings.panelStyle,3);
    Test.assertEqual(Settings.left,4);
    Test.assertEqual(Settings.seconds,false);
    Test.assertEqual(Settings.timeFormat,2);
    // The next frame is a full redraw that loads the new mountain.
    Test.assertEqual(view._minute,-1);
    for(var i=0;i<keys.size();i++) {Application.Properties.setValue(keys[i],old[i]);}
    app.onSettingsChanged();app.view=null;
    return true;
}
