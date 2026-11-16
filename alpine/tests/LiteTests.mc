import Toybox.Test;import Toybox.WatchUi;
(:test) function classicBackgroundIsNativeAndExclusive(logger){
 var bitmap=WatchUi.loadResource(Rez.Drawables.Classic);
 Test.assertEqual(bitmap.getWidth(),Device.W);Test.assertEqual(bitmap.getHeight(),Device.H);
 Test.assertEqual(SlotCatalog.choiceKeys.size(),2);
 Test.assert(!SlotCatalog.isChoice("Scene"));Test.assert(!SlotCatalog.isChoice("Festival"));Test.assert(!SlotCatalog.isChoice("SkyDecor"));
 Settings.load();Test.assertEqual(Settings.scene,2);Test.assert(!Settings.smart);return true;
}

(:test) function classicLandscapeCacheSurvivesRepeatedPaints(logger){
 var view=new AlpineView();view.prepareBackground();var first=view._background;
 view.prepareBackground();Test.assert(view._background==first);
 view.onHide();Test.assert(view._background==null);view.prepareBackground();Test.assert(view._background!=null);
 view.releaseFaceResources();return true;
}
