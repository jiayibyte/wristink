module SidePanel {
    // Resolve the user's strategy before the hot per-second callback runs.
    function secondsMode(userMode,top,bottom,data){
        if(top!=0 || bottom!=0 || data!=0 || userMode==3){return 0;}
        return userMode==0 ? 2 : userMode;
    }
    function cardY(top,bottom,upper){
        if(top==0 || bottom==0){return FaceLayout.CARD_SINGLE_Y;}
        return upper ? FaceLayout.CARD_TOP_Y : FaceLayout.CARD_BOTTOM_Y;
    }
}
