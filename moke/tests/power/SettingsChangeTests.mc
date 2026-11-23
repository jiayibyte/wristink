import Toybox.Graphics;
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

(:test)
function colourThemeLeavesMonochromeScreensBlackAndWhite(logger) {
    // The power tests build for Instinct 3 Solar (1-bit): a colour theme chosen
    // on the phone must not tint anything there.
    var old=Application.Properties.getValue("colorTheme");
    Application.Properties.setValue("colorTheme",3);FacePrefs.reload();
    Test.assertEqual(FacePalette.theme(),0);
    FaceDraw.setTheme(true);
    Test.assertEqual(FaceDraw.accent,FaceDraw.foreground);
    Test.assertEqual(FaceDraw.heart,FaceDraw.foreground);
    Test.assertEqual(FaceDraw.soft,FaceDraw.foreground);
    Test.assertEqual(FacePalette.accentOn(Graphics.COLOR_WHITE),Graphics.COLOR_BLACK);
    FaceDraw.setTheme(false);
    Test.assertEqual(FaceDraw.accent,Graphics.COLOR_BLACK);
    Application.Properties.setValue("colorTheme",old);FacePrefs.reload();FaceDraw.setTheme(true);
    return true;
}
