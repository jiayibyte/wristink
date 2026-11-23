import Toybox.Application;
import Toybox.Lang;
import Toybox.Test;

(:test)
function phoneSettingsAcceptLooseTypes(logger) {
    // Garmin Connect may hand values back as Long, Float or a numeric String.
    Test.assertEqual(FaceSettings.bounded(2,0,0,2),2);
    Test.assertEqual(FaceSettings.bounded(2l,0,0,2),2);
    Test.assertEqual(FaceSettings.bounded(2.0,0,0,2),2);
    Test.assertEqual(FaceSettings.bounded("2",0,0,2),2);
    Test.assertEqual(FaceSettings.bounded("x",0,0,2),0);
    Test.assertEqual(FaceSettings.bounded(3,0,0,2),0);
    Test.assertEqual(FaceSettings.number("NoSuchKey",5,0,9),5);
    Test.assertEqual(FaceSettings.flag("NoSuchKey",true),true);
    return true;
}

(:test)
function phoneSettingsChangeReachesTheFaceOnEveryApi(logger) {
    // onSettingsChanged used WatchUi.getCurrentView() (API 3.4). On API 3.2-3.3
    // watches such as Instinct 2 this threw, and phone changes never applied.
    var app=Application.getApp() as RetroWorldApp;
    var view=new SecondsDrawingProbe();app._view=view;
    var keys=["TimeFormat","ShowDate","Field1"];var old=[];
    for(var i=0;i<keys.size();i++) {old.add(Application.Properties.getValue(keys[i]));}
    Theme.load(FaceSettings.theme);
    Application.Properties.setValue("TimeFormat",2);
    Application.Properties.setValue("ShowDate",false);
    Application.Properties.setValue("Field1",9);
    view._minute=100;view._dataMinute=100;
    app.onSettingsChanged();
    Test.assertEqual(FaceSettings.timeFormat,2);
    Test.assertEqual(FaceSettings.showDate,false);
    Test.assertEqual(FaceSettings.slots[0],9);
    Test.assertEqual(view._minute,-1);Test.assertEqual(view._dataMinute,-1);
    for(var i=0;i<keys.size();i++) {Application.Properties.setValue(keys[i],old[i]);}
    app.onSettingsChanged();app._view=null;
    return true;
}
