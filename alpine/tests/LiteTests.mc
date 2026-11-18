import Toybox.Test;import Toybox.WatchUi;import Toybox.Application;
(:test) function mountainBackgroundsAreNativeAndSelectable(logger){
 // Four selectable mountains, each drawn at the native screen size.
 for(var i=0;i<4;i++) {
  var bitmap=WatchUi.loadResource(LandscapeArt.id(i));
  Test.assertEqual(bitmap.getWidth(),Device.W);Test.assertEqual(bitmap.getHeight(),Device.H);bitmap=null;
 }
 Test.assertEqual(SlotCatalog.choiceKeys.size(),3);Test.assert(SlotCatalog.isChoice("Mountain"));
 var old=Application.Properties.getValue("Mountain");
 Test.assert(Settings.setChoice("Mountain",2));Test.assertEqual(Settings.mountain,2);Test.assert(!Settings.setChoice("Mountain",4));
 Application.Properties.setValue("Mountain",old==null ? 0 : old);Settings.load();
 Test.assert(!SlotCatalog.isChoice("Scene"));Test.assert(!SlotCatalog.isChoice("Festival"));Test.assert(!SlotCatalog.isChoice("SkyDecor"));
 Settings.load();Test.assertEqual(Settings.scene,2);Test.assert(!Settings.smart);return true;
}

(:test) function classicLandscapeCacheSurvivesRepeatedPaints(logger){
 var view=new AlpineView();view.prepareBackground();var first=view._background;
 view.prepareBackground();Test.assert(view._background==first);
 view.onHide();Test.assert(view._background==null);view.prepareBackground();Test.assert(view._background!=null);
 view.releaseFaceResources();return true;
}

(:test) function instinctTimeLeftFieldIsOptional(logger){
 // Store review request: a data field left of the time on Instinct, beside AM/PM and seconds.
 Test.assert(SlotCatalog.isSlot("TimeLeft"));
 var old=Application.Properties.getValue("TimeLeft");
 Application.Properties.setValue("TimeLeft",11);Settings.load();Test.assertEqual(Settings.timeLeft,11);
 Test.assert(Settings.setSlot("TimeLeft",1));Test.assertEqual(Settings.getSlot("TimeLeft"),1);
 // A heart-rate value there must trigger the full redraw on Instinct, never on colour screens.
 Test.assertEqual(Settings.headersUse(1),Device.MONO || Settings.top==1 || Settings.upperLeft==1 || Settings.upperRight==1);
 Test.assert(Settings.uses(1));Test.assert(!Settings.setSlot("TimeLeft",12));
 Application.Properties.setValue("TimeLeft",99);Settings.load();Test.assertEqual(Settings.timeLeft,11);
 Application.Properties.setValue("TimeLeft",old==null ? 11 : old);Settings.load();return true;
}
