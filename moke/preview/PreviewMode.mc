// This file is included only by preview.jungle; never in the installable live build.
import Toybox.Lang;
import Toybox.Weather;
module PreviewMode {
    const ENABLED = true;
    const BODY_BATTERY = 62;
    const INTENSITY_MINUTES = 12;
    const INTENSITY_WEEK_GOAL = 150;
    function currentHeartRate(stamp) {var phase=stamp%20;return phase<10 ? 94+phase : 113-phase;}
    function bodyBattery() { return BODY_BATTERY; }
    function intensityProgress() { return FitnessProgress.completion(INTENSITY_MINUTES, INTENSITY_WEEK_GOAL / 7.0); }
    const MOVE_BAR_LEVEL = 3;
    function moveBarLevel() { return MOVE_BAR_LEVEL; }
    function weatherCondition() { return Weather.CONDITION_RAIN; }
    function number(kind) {switch(kind){case 1:return 86;case 2:return 8608;case 3:return 9.7;case 4:return 22;case 5:return 1688;case 6:return 96;case 7:return 24;case 10:return 56;case 11:return 3;case 12:return 86;case 13:return 13;case 14:return 72;case 16:return 25;case 17:return 28;case 18:return 128;case 19:return 62;case 20:return 12;case 21:return 108;case 22:return 56;case 23:return 72;case 24:return 3;case 25:return 18;case 26:return 28;case 27:return 14;case 28:return 1013;}return null;}
    function trend(kind) as Array<Number or Null> {
        if(kind==19){return [42,45,49,52,54,58,60,63,66,68,65,62];}
        if(kind==18){return [100,102,109,108,111,115,118,120,125,129,131,128];}
        if(kind==7){return [21,22,22,23,24,25,24,26,25,24,24,24];}
        if(kind==28){return [1009,1010,1011,1010,1012,1013,1012,1014,1013,1013,1014,1013];}
        return history();
    }
    function metric(kind) {return kind==8 ? "17:18" : (kind==9 ? "06:04" : "--");}
    function history() as Array<Number or Null> { return [60, 64, 61, 67, 63, 66, 62, 70, 65, 68, 64, 73, 67, 71, 65, 69, 66, 76, 69, 72, 67, 79, 72, 76, 70, 82, 74, 78, 72, 85, 77, 81, 75, 88, 79, 85, 80, 94, 84, 89, 85, 104, 92, 98, 125, 109, 101, 96]; }
}
