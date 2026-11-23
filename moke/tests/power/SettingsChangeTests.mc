import Toybox.Application;
import Toybox.Lang;
import Toybox.Test;

(:test)
function phoneSettingsAcceptLooseTypes(logger) {
    // Garmin Connect may hand values back as Long, Float or a numeric String.
    Test.assertEqual(FacePrefs.toNumber(2),2);
    Test.assertEqual(FacePrefs.toNumber(2l),2);
    Test.assertEqual(FacePrefs.toNumber(2.0),2);
    Test.assertEqual(FacePrefs.toNumber("2"),2);
    Test.assert(FacePrefs.toNumber("x")==null);
    Test.assertEqual(FacePrefs.toFlag("false"),false);
    Test.assertEqual(FacePrefs.toFlag(1),true);
    Test.assert(FacePrefs.toFlag(null)==null);
    return true;
}

(:test)
function phoneSettingsChangeReachesTheFace(logger) {
    var app=Application.getApp() as InstinctFaceApp;
    // timeFormat: 0 = 24 hours, 1 = 12 hours.
    var old=Application.Properties.getValue("timeFormat");var revision=FacePrefs.revision;
    var target=old==1 ? 0 : 1;
    Application.Properties.setValue("timeFormat",target);
    app.onSettingsChanged();
    Test.assertEqual(FacePrefs.get("timeFormat"),target);
    // The render plan is rebuilt from the new values on the next frame.
    Test.assert(FacePrefs.revision!=revision);
    Application.Properties.setValue("timeFormat",old);app.onSettingsChanged();
    return true;
}
