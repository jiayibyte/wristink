import Toybox.Graphics;
import Toybox.Math;
import Toybox.WatchUi;
import Toybox.Lang;

module FaceDraw {
    var foreground=Graphics.COLOR_WHITE;var background=Graphics.COLOR_BLACK;
    var batteryPercent=0;var bodyBattery=null;var cellsProgress=null;var intensityProgress=null;
    var _energyBitmap;var _energyCount=0;
    var _energyKey=-1;var _chart;var _topCard;var _bottomCard;var _topCardKey=-1;var _bottomCardKey=-1;var _secondsFont;
    var _hrFontTwo;var _hrFontThree;var _hrInk;var _hrPaper;var _hrStyle=0;var _hrGoal=0;var _hrCellsStyle=0;var _hrPlain=false;
    var _hrPlainTop=23;var _hrPlainHeight=29;var _hrCenterY=38;
    function initialize(){}
    function enterSettings(){FontCatalog.reset();NativeStyle.reset();_energyBitmap=null;_energyCount=0;_energyKey=-1;_chart=null;_topCard=null;_bottomCard=null;_topCardKey=-1;_bottomCardKey=-1;_secondsFont=null;releaseLiveHeart();}
    function releaseLiveHeart(){_hrFontTwo=null;_hrFontThree=null;_hrPlain=false;}
    function prepareLiveHeart(dc,ink,paper){
        releaseLiveHeart();_hrInk=ink;_hrPaper=paper;
        _hrStyle=FacePrefs.get("circleStyle");_hrGoal=FacePrefs.get("circleGoal");_hrCellsStyle=FacePrefs.get("cellsStyle");
        _hrPlain=NativeStyle.enabled() && paper==Graphics.COLOR_WHITE && FacePrefs.get("cellsSource")==0 && FacePrefs.get("ringSource")==0 && _hrStyle<=1;
        if(_hrPlain){
            var withIcon=FacePrefs.flag("showCircleIcon") && _hrStyle!=1;
            _hrPlainTop=withIcon ? 23 : 16;_hrPlainHeight=withIcon ? 29 : 30;_hrCenterY=withIcon ? 38 : 31;
            FontCatalog.reset();
            _hrFontTwo=WhiteHeartFonts.load(FacePrefs.get("circleFont"),FacePrefs.get("circleSize"));_hrFontThree=_hrFontTwo;
        }else if(_hrStyle<=1){
            _hrFontTwo=FontCatalog.fit(dc,"liveheart",FacePrefs.get("circleFont"),FacePrefs.get("circleSize")+1,"888",34,23);
            _hrFontThree=_hrFontTwo;
        }else{
            _hrFontTwo=FontCatalog.fit(dc,"data",FacePrefs.get("dataFont"),FacePrefs.get("dataSize")+2,LiveHeart.text(300,_hrStyle,_hrGoal),34,22);
            _hrFontThree=_hrFontTwo;
        }
    }
    function drawLiveHeart(dc,value){
        var text=LiveHeart.text(value,_hrStyle,_hrGoal);
        if(_hrPlain){dc.setClip(121,_hrPlainTop,47,_hrPlainHeight);}else{dc.setClip(126,25,36,25);}
        dc.setColor(_hrInk,Graphics.COLOR_TRANSPARENT);
        var font=text.length()>2 ? _hrFontThree : _hrFontTwo;
        var y=_hrPlain ? _hrCenterY-dc.getFontHeight(font)/2 : (text.length()==3 ? FaceLayout.HEART_SMALL_VALUE_Y : FaceLayout.HEART_VALUE_Y);
        dc.drawText(144,y,font,text,Graphics.TEXT_JUSTIFY_CENTER);
        dc.clearClip();
    }
    function refreshLiveHeart(dc,value){
        if(_hrFontTwo==null || _hrFontThree==null){return;}
        // This rectangle clears 2/3-digit transitions without touching the heart or outer ring.
        dc.setColor(_hrPaper,_hrPaper);
        if(_hrPlain){dc.setClip(121,_hrPlainTop,47,_hrPlainHeight);dc.fillRectangle(121,_hrPlainTop,47,_hrPlainHeight);}
        else{dc.setClip(126,25,36,25);dc.fillRectangle(126,25,36,25);}
        // Restore the small parts of the energy texture behind the digits; no resource loads.
        if(!_hrPlain && cellsProgress!=null && cellsProgress>0){
            dc.setColor(_hrInk,_hrPaper);
            if(_hrCellsStyle==2){
                dc.setPenWidth(6);
                if(cellsProgress>=1){dc.drawCircle(144,31,23);}else{dc.drawArc(144,31,23,Graphics.ARC_CLOCKWISE,90,90-cellsProgress*360);}
                dc.setPenWidth(1);
            }else{
                if(_energyBitmap!=null){dc.drawBitmap(113+EnergyCatalog.X[_energyCount-1],EnergyCatalog.Y[_energyCount-1],_energyBitmap);}
            }
        }
        drawLiveHeart(dc,value);dc.clearClip();dc.setColor(foreground,background);
    }
    function setTheme(dark){foreground=dark ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK;background=dark ? Graphics.COLOR_BLACK : Graphics.COLOR_WHITE;}
    (:extendedCode)
    function dateFont(){return FontCatalog.data(FacePrefs.fontFamily("date"),FacePrefs.fontSize("date")+2);}
    (:extendedCode)
    function date(dc,text){
        var reserved=FacePrefs.flag("showMoveBar") && FacePrefs.get("moveSource")!=0;
        var compact=FacePrefs.get("topThree")!=0 && FacePrefs.flag("showMoon");
        var width=reserved ? (compact ? 59 : 61) : (compact ? 83 : 103);
        var height=FacePrefs.flag("showTime") && FacePrefs.get("timeFormat")==1 ? 13 : 18;
        var font=FontCatalog.fit(dc,"data",FacePrefs.fontFamily("date"),FacePrefs.fontSize("date")+2,text,width,height);
        dc.setClip(8,49,width,height);dc.setColor(foreground,background);dc.drawText(8,49,font,text,Graphics.TEXT_JUSTIFY_LEFT);dc.clearClip();
    }
    (:extendedCode)
    function time(dc,hour,minute){
        var text=FaceFormat.timeText(hour,minute);
        var font=FontCatalog.fit(dc,"time",FacePrefs.get("timeFont"),FacePrefs.get("timeSize")+1,text,124,56);
        dc.setClip(8,FaceLayout.TIME_Y,126,56);dc.setColor(foreground,background);dc.drawText(9,FaceLayout.TIME_Y,font,text,Graphics.TEXT_JUSTIFY_LEFT);dc.clearClip();
        // Do not keep the largest font alive through card/slot property lookups or menu return.
        font=null;FontCatalog.reset();
        if(FacePrefs.get("timeFormat")==1){dc.drawText(8,63,FontCatalog.data(0,1),FaceLocale.period(hour),Graphics.TEXT_JUSTIFY_LEFT);}
    }
    function seconds(dc,value){
        var text=value.format("%02d");
        if(_secondsFont==null){prepareSeconds(dc);}
        dc.drawText(DeviceProfile.SECONDS_X,DeviceProfile.SECONDS_Y,_secondsFont,text,Graphics.TEXT_JUSTIFY_CENTER);
    }
    function prepareSeconds(dc){_secondsFont=FontCatalog.fit(dc,"seconds",FacePrefs.get("secondsFont"),FacePrefs.get("secondsSize")+1,"88",DeviceProfile.SECONDS_WIDTH-1,DeviceProfile.SECONDS_HEIGHT);}
    function releaseSeconds(){_secondsFont=null;}
    (:extendedCode)
    function walletCards(dc,top,bottom){
        var light=background==Graphics.COLOR_WHITE;
        if(top!=0){
            var key=top*2+(light ? 1 : 0);
            if(_topCard==null || key!=_topCardKey){_topCard=WatchUi.loadResource(CardArtwork.resource(top,light));_topCardKey=key;}
            drawCard(dc,top,DeviceProfile.ANALOG ? 63 : SidePanel.cardY(top,bottom,true),_topCard,DeviceProfile.ANALOG ? (bottom!=0 ? 116 : 132) : FaceLayout.CARD_X);
        }else{_topCard=null;_topCardKey=-1;}
        if(bottom!=0){
            var key=bottom*2+(light ? 1 : 0);
            if(_bottomCard==null || key!=_bottomCardKey){_bottomCard=bottom>=3 && top>=3 ? _topCard : WatchUi.loadResource(CardArtwork.resource(bottom,light));_bottomCardKey=key;}
            drawCard(dc,bottom,DeviceProfile.ANALOG ? 63 : SidePanel.cardY(top,bottom,false),_bottomCard,DeviceProfile.ANALOG ? (top!=0 ? 146 : 132) : FaceLayout.CARD_X);
        }else{_bottomCard=null;_bottomCardKey=-1;}
    }
    (:extendedCode)
    function drawCard(dc,kind,y,bitmap,x){
        if(kind<=2){dc.drawBitmap(x,y,bitmap);}
        else{dc.setClip(x,y,28,13);dc.drawBitmap(x-(kind-3)*28,y,bitmap);dc.clearClip();}
    }
    (:extendedCode)
    function sideData(dc,kind,value){
        dc.setClip(136,73,35,30);dc.setColor(foreground,background);
        if(FacePrefs.flag("showIcons")){icon(dc,kind,146,73,foreground,background);}
        var font=FontCatalog.fit(dc,"data",FacePrefs.fontFamily("side"),FacePrefs.fontSize("side")+1,value,32,14);
        dc.drawText(153,89,font,value,Graphics.TEXT_JUSTIFY_CENTER);dc.clearClip();
    }
    (:extendedCode)
    function moveBar(dc,ratio,compact){
        var x=compact ? FaceLayout.MOVE_COMPACT_X : FaceLayout.MOVE_X;var y=FaceLayout.MOVE_Y;
        moveBarAt(dc,ratio,x,y,compact);
    }
    (:extendedCode)
    function moveBarAt(dc,ratio,x,y,compact){
        var width=compact ? 3 : 4;var gap=compact ? 0 : 1;
        dc.setColor(foreground,background);
        var source=FacePrefs.get("moveSource");
        if(source==2){dc.drawRectangle(x,y+3,8,6);dc.fillRectangle(x+8,y+5,1,2);}
        else if(source==1){dc.fillCircle(x+2,y+4,2);dc.fillCircle(x+6,y+4,2);dc.fillPolygon([[x,y+5],[x+8,y+5],[x+4,y+10]]);}
        else{
            if(NativeStyle.enabled()){NativeStyle.activity(dc,x,y,foreground,background);}
            else{
            dc.fillCircle(x+4,y+1,1);dc.drawLine(x+4,y+4,x+4,y+8);dc.drawLine(x+1,y+7,x+4,y+4);
            dc.drawLine(x+4,y+4,x+7,y+7);dc.drawLine(x+4,y+8,x+2,y+12);dc.drawLine(x+4,y+8,x+6,y+12);
            }
        }
        if(ratio==null){dc.drawLine(x+15,y+6,x+18,y+6);dc.drawLine(x+22,y+6,x+25,y+6);return;}
        if(ratio<0){ratio=0;}if(ratio>1){ratio=1;}
        var style=FacePrefs.get("moveStyle");
        if(style==2){var label=(ratio*100).format("%.0f")+"%";dc.drawText(x+12,y+3,FontCatalog.fit(dc,"data",FacePrefs.fontFamily("move"),1,label,24,10),label,Graphics.TEXT_JUSTIFY_LEFT);return;}
        if(style==1){dc.drawRectangle(x+12,y+5,24,4);if(ratio>0){dc.fillRectangle(x+13,y+6,Math.ceil(22*ratio),2);}return;}
        var count=Math.ceil(ratio*5);
        for(var i=0;i<5;i++){var left=x+12+i*(width+gap);dc.drawRectangle(left,y+4,width,6);if(i<count){dc.fillRectangle(left+1,y+5,width-2,4);}}
    }
    (:extendedCode)
    function heartPanel(dc,values as Array<Number or Null>,limits as Array<Number or Null>) as Void {
        if(_chart==null){_chart=WatchUi.loadResource(Rez.Fonts.Chart);}
        var left=FaceLayout.GRAPH_X;var top=FaceLayout.GRAPH_Y;dc.setClip(left,top,FaceLayout.GRAPH_WIDTH,FaceLayout.GRAPH_HEIGHT);dc.setColor(foreground,background);
        var low=limits[0];var high=limits[1];var labels=FacePrefs.flag("showChartLabels");
        if(labels){
            var labelFont=_chart;var selected=FacePrefs.get("chartLabelFont");
            if(selected!=0){labelFont=FontCatalog.fit(dc,"data",selected-1,1,high!=null ? high.toString() : "--",15,10);}
            var lowY=top+FaceLayout.GRAPH_HEIGHT-2-dc.getFontHeight(labelFont);
            dc.drawText(left+15,top,labelFont,high!=null ? high.toString() : "--",Graphics.TEXT_JUSTIFY_RIGHT);
            dc.drawText(left+15,lowY,labelFont,low!=null ? low.toString() : "--",Graphics.TEXT_JUSTIFY_RIGHT);
        }
        var px=left+(labels ? 18 : 1);var py=top+1;var w=FaceLayout.GRAPH_WIDTH-(labels ? 20 : 3);var h=FaceLayout.GRAPH_HEIGHT-FaceLayout.GRAPH_BOTTOM_INSET;
        dc.drawLine(px,py,px,py+h);dc.drawLine(px,py+h,px+w,py+h);
        if(values.size()>0 && low!=null && high!=null){
            var span=high-low;if(span==0){span=1;}
            var prevX=null as Numeric or Null;var prevY=null as Numeric or Null;var style=FacePrefs.get("chartStyle");
            for(var i=0;i<values.size();i++){
                var rate=values[i];if(rate==null){prevX=null;prevY=null;continue;}
                var x=px+(values.size()>1 ? i.toFloat()*w/(values.size()-1) : w/2);
                var y=high==low ? py+h/2 : py+h-(rate-low).toFloat()*h/span;
                if(style==1 || style==2){dc.drawLine(x,y,x,py+h);}
                if(style!=2 && prevX!=null && prevY!=null){dc.drawLine(prevX,prevY,x,y);}
                dc.drawPoint(x,y);prevX=x;prevY=y;
            }
        }
        dc.clearClip();
    }
    (:extendedCode)
    function slotFont(dc,key,label,width,height,maxIndex){
        var size=FacePrefs.fontSize(key)+2;if(maxIndex!=null && size>maxIndex){size=maxIndex;}
        return FontCatalog.fit(dc,"data",FacePrefs.fontFamily(key),size,label,width,height);
    }
    (:extendedCode)
    function slot(dc,key,label,ratio,x,y,width,height,fontOverride){
        var kind=FacePrefs.get(key);if(kind==0){return;}
        var style=FacePrefs.get(key+"Style");var showIcon=style!=1 && FacePrefs.flag("showIcons");
        var offset=showIcon ? (y>=120 ? FaceLayout.LOWER_TEXT_OFFSET : 17) : 0;
        var gauge=style==4 || style==5;var labelHeight=gauge ? height-4 : height-1;
        var font=fontOverride!=null ? fontOverride : slotFont(dc,key,label,width-offset,labelHeight,null);
        dc.setClip(x,y,width,height);dc.setColor(foreground,background);
        if(showIcon){icon(dc,kind,x,y+(y>=120 || gauge ? 0 : 3),foreground,background);}
        dc.drawText(x+offset,y+1,font,label,Graphics.TEXT_JUSTIFY_LEFT);
        if(gauge){
            var p=ratio;if(p!=null){p=p<0 ? 0 : (p>1 ? 1 : p);}
            var gx=x+offset;var gw=width-offset-1;var gy=y+height-3;
            if(style==4){dc.drawLine(gx,gy+2,gx+gw,gy+2);if(p!=null && p>0){dc.fillRectangle(gx,gy,Math.ceil(gw*p),2);}}
            else{
                var cell=(gw-7)/8;var count=p!=null ? Math.ceil(p*8) : 0;
                for(var i=0;i<8;i++){var xx=gx+i*(cell+1);if(i<count){dc.fillRectangle(xx,gy,cell,3);}else{dc.drawLine(xx,gy+2,xx+cell-1,gy+2);}}
            }
        }
        dc.clearClip();
    }
    (:extendedCode)
    function footerRow(dc,leftLabel,leftRatio,rightLabel,rightRatio){
        if(FacePrefs.get("footerLeft")==0 && FacePrefs.get("footerRight")==0){return;}
        var leftFont=null;var rightFont=null;
        if(FacePrefs.flag("linkFooterFonts")){
            var size=FacePrefs.fontSize("footerLeft")+2;var rightSize=FacePrefs.fontSize("footerRight")+2;if(rightSize<size){size=rightSize;}
            var leftOffset=FacePrefs.get("footerLeftStyle")==1 || !FacePrefs.flag("showIcons") ? 0 : FaceLayout.LOWER_TEXT_OFFSET;
            var rightOffset=FacePrefs.get("footerRightStyle")==1 || !FacePrefs.flag("showIcons") ? 0 : FaceLayout.LOWER_TEXT_OFFSET;
            for(;size>=0;size--){
                leftFont=FontCatalog.data(FacePrefs.fontFamily("footerLeft"),size);rightFont=FontCatalog.data(FacePrefs.fontFamily("footerRight"),size);
                if(dc.getTextWidthInPixels(leftLabel,leftFont)<=FaceLayout.LOWER_LEFT_WIDTH-leftOffset && dc.getTextWidthInPixels(rightLabel,rightFont)<=FaceLayout.FOOTER_RIGHT_WIDTH-rightOffset && dc.getFontHeight(leftFont)<=18 && dc.getFontHeight(rightFont)<=18){break;}
                leftFont=null;rightFont=null;
            }
        }
        slot(dc,"footerLeft",leftLabel,leftRatio,FaceLayout.LOWER_LEFT_X,FaceLayout.FOOTER_Y,FaceLayout.LOWER_LEFT_WIDTH,20,leftFont);
        slot(dc,"footerRight",rightLabel,rightRatio,FaceLayout.LOWER_RIGHT_X,FaceLayout.FOOTER_Y,FaceLayout.FOOTER_RIGHT_WIDTH,20,rightFont);
    }
    (:extendedCode)
    function circle(dc,kind,value,heartValue){
        var cx=144;var cy=31;var bg=FacePrefs.get("circleBackground");
        var paper=bg==1 || (bg==2 && background==Graphics.COLOR_WHITE) ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK;
        var ink=paper==Graphics.COLOR_BLACK ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK;
        dc.setColor(paper,paper);dc.fillCircle(cx,cy,31);
        if(cellsProgress==null || cellsProgress<=0 || FacePrefs.get("cellsStyle")==2){_energyBitmap=null;_energyKey=-1;_energyCount=0;}
        if(cellsProgress!=null && cellsProgress>0){
            var style=FacePrefs.get("cellsStyle");
            if(style==2){dc.setColor(ink,paper);dc.setPenWidth(6);if(cellsProgress>=1){dc.drawCircle(cx,cy,23);}else{dc.drawArc(cx,cy,23,Graphics.ARC_CLOCKWISE,90,90-cellsProgress*360);}dc.setPenWidth(1);}
            else{
                var count=FitnessProgress.segmentCount(cellsProgress*100);
                var variant=style*2+(ink==Graphics.COLOR_BLACK ? 1 : 0);var assetKey=variant*9+count;
                if(assetKey!=_energyKey){_energyBitmap=EnergyCatalog.load(variant,count);_energyKey=assetKey;_energyCount=count;}
                dc.drawBitmap(cx-31+EnergyCatalog.X[count-1],cy-31+EnergyCatalog.Y[count-1],_energyBitmap);
            }
        }
        dc.setColor(ink,paper);
        if(intensityProgress!=null && intensityProgress>0){
            var style=FacePrefs.get("ringStyle");var start=[90,0,270,180][FacePrefs.get("ringStart")];
            dc.setPenWidth(style==0 ? 1 : (style==2 ? 3 : 2));
            if(style==3){var count=FitnessProgress.segmentCount(intensityProgress*100);for(var i=0;i<count;i++){dc.drawArc(cx,cy,29,Graphics.ARC_CLOCKWISE,start-i*45-2,start-i*45-43);}}
            else if(intensityProgress>=1){dc.drawCircle(cx,cy,29);}else{dc.drawArc(cx,cy,29,Graphics.ARC_CLOCKWISE,start,start-intensityProgress*360);}
            dc.setPenWidth(1);
        }
        if(kind!=0){
            if(FacePrefs.flag("showCircleIcon") && FacePrefs.get("circleStyle")!=1){
                if(!(NativeStyle.enabled() && NativeStyle.circleIcon(dc,kind,cx,FaceLayout.HEART_ICON_Y,ink,paper))){icon(dc,kind,cx-7,FaceLayout.HEART_ICON_Y,ink,paper);}
            }
            if(kind==6){prepareLiveHeart(dc,ink,paper);drawLiveHeart(dc,heartValue);}
            else{
                var index=FacePrefs.get("circleSize")+1;if(value.length()>=3){index=index-1;}if(index<0){index=0;}
                var font=FontCatalog.fit(dc,"circle",FacePrefs.get("circleFont"),index,value,32,23);
                if(kind==17 || value.length()>=4){font=null;FontCatalog.reset();font=FontCatalog.fit(dc,"data",FacePrefs.get("dataFont"),FacePrefs.get("dataSize")+2,value,34,22);}
                dc.setColor(ink,Graphics.COLOR_TRANSPARENT);
                dc.drawText(cx,value.length()==3 ? FaceLayout.HEART_SMALL_VALUE_Y : FaceLayout.HEART_VALUE_Y,font,value,Graphics.TEXT_JUSTIFY_CENTER);
            }
        }
        dc.setColor(foreground,background);
    }
    (:extendedCode)
    function moon(dc, cx, cy, phase, ink, paper) {
        if(NativeStyle.enabled()){NativeStyle.moon(dc,cx,cy,phase,ink,paper);return;}
        dc.setColor(ink, paper);
        dc.fillCircle(cx, cy, 7); dc.setColor(paper, paper);
        for (var y = -6; y <= 6; y++) {
            var span = Math.sqrt(36 - y * y); var edge = Math.cos(phase * 2 * Math.PI) * span;
            if (phase < 0.5) { dc.drawLine(cx + edge, cy + y, cx + span, cy + y); }
            else { dc.drawLine(cx - span, cy + y, cx - edge, cy + y); }
        }
        dc.setColor(ink, paper); dc.drawCircle(cx, cy, 7);
    }
    (:extendedCode)
    function sun(dc, x, y) {
        dc.drawCircle(x + 7, y + 6, 4);
        dc.drawLine(x + 7, y - 1, x + 7, y + 1); dc.drawLine(x + 7, y + 11, x + 7, y + 13);
        dc.drawLine(x, y + 6, x + 2, y + 6); dc.drawLine(x + 12, y + 6, x + 14, y + 6);
        dc.drawLine(x + 2, y + 1, x + 3, y + 2); dc.drawLine(x + 11, y + 10, x + 12, y + 11);
        dc.drawLine(x + 2, y + 11, x + 3, y + 10); dc.drawLine(x + 11, y + 2, x + 12, y + 1);
    }
    (:extendedCode)
    function icon(dc, kind, x, y, ink, paper) {
        if(NativeStyle.enabled() && NativeStyle.icon(dc,kind,x,y,ink,paper)){return;}
        dc.setColor(ink, paper);
        switch (kind) {
            case 1: case 17:
                dc.drawRectangle(x, y + 2, 12, 8); dc.fillRectangle(x + 12, y + 4, 2, 4);
                var fill = Math.floor(batteryPercent * 8 / 100);
                if (fill > 8) { fill = 8; }
                if (fill > 0) { dc.fillRectangle(x + 2, y + 4, fill, 4); }
                break;
            case 2: dc.fillEllipse(x + 3, y + 4, 2, 4); dc.fillEllipse(x + 9, y + 6, 2, 4); dc.fillCircle(x + 3, y + 11, 1); dc.fillCircle(x + 9, y + 13, 1); break;
            case 3: dc.drawCircle(x + 6, y + 4, 4); dc.fillPolygon([[x + 2, y + 7], [x + 10, y + 7], [x + 6, y + 14]]); break;
            case 4: dc.setPenWidth(2); dc.drawLine(x, y + 12, x + 4, y + 12); dc.drawLine(x + 4, y + 12, x + 4, y + 7); dc.drawLine(x + 4, y + 7, x + 9, y + 7); dc.drawLine(x + 9, y + 7, x + 9, y + 2); dc.drawLine(x + 9, y + 2, x + 14, y + 2); dc.setPenWidth(1); break;
            case 5: dc.fillPolygon([[x + 7, y], [x + 12, y + 7], [x + 11, y + 12], [x + 5, y + 14], [x + 1, y + 10], [x + 2, y + 6], [x + 5, y + 8]]); dc.setColor(paper, paper); dc.fillEllipse(x + 7, y + 11, 2, 2); dc.setColor(ink, paper); break;
            case 6: dc.fillCircle(x + 4, y + 4, 3); dc.fillCircle(x + 10, y + 4, 3); dc.fillPolygon([[x + 1, y + 5], [x + 13, y + 5], [x + 7, y + 13]]); break;
            case 7: WeatherIcons.draw(dc, x, y, ink, paper); break;
            case 8: case 9: sun(dc, x, y); dc.setColor(paper, paper); dc.fillRectangle(x - 1, y + 7, 17, 7); dc.setColor(ink, paper); dc.drawLine(x, y + 8, x + 14, y + 8); dc.drawLine(x + 3, y + 11, x + 11, y + 11); break;
            case 10: dc.drawCircle(x + 7, y + 9, 4); dc.drawLine(x + 3, y + 8, x + 7, y); dc.drawLine(x + 11, y + 8, x + 7, y); break;
            case 11: dc.drawRectangle(x + 1, y + 1, 11, 8); dc.drawLine(x + 3, y + 9, x + 3, y + 13); dc.drawLine(x + 3, y + 13, x + 7, y + 9); break;
            case 12: dc.drawCircle(x + 7, y + 6, 6); dc.drawCircle(x + 7, y + 6, 3); dc.fillCircle(x + 7, y + 6, 1); break;
            case 13: dc.drawLine(x, y + 4, x + 12, y + 4); dc.drawLine(x + 2, y + 8, x + 14, y + 8); dc.drawLine(x + 5, y + 12, x + 11, y + 12); break;
            case 14: moon(dc, x + 7, y + 6, 0.35, ink, paper); break;
            case 15: dc.drawCircle(x + 7, y + 6, 6); dc.drawLine(x + 1, y + 6, x + 4, y + 6); dc.drawLine(x + 4, y + 6, x + 6, y + 2); dc.drawLine(x + 6, y + 2, x + 8, y + 10); dc.drawLine(x + 8, y + 10, x + 10, y + 6); break;
            case 16: dc.drawCircle(x + 7, y + 10, 3); dc.drawRectangle(x + 6, y, 2, 9); dc.drawLine(x + 10, y + 2, x + 13, y + 2); dc.drawLine(x + 10, y + 5, x + 12, y + 5); break;
            case 18:
                // Garmin's altimeter silhouette, scaled from the official controls icon.
                dc.fillPolygon([[x + 12, y + 5], [x + 10, y + 7], [x + 6, y + 2], [x, y + 12], [x + 16, y + 12]]);
                break;
            case 19:
                dc.drawRectangle(x+2,y+3,10,9);dc.drawLine(x+5,y+1,x+9,y+1);
                dc.fillPolygon([[x+8,y+4],[x+4,y+8],[x+7,y+8],[x+5,y+12],[x+11,y+6],[x+8,y+6]]);break;
            case 20:case 21:case 22:case 23:
                dc.drawCircle(x+7,y+7,6);dc.drawLine(x+7,y+7,x+7,y+3);dc.drawLine(x+7,y+7,x+10,y+8);break;
            case 24:
                dc.fillCircle(x+7,y+2,1);dc.drawLine(x+7,y+5,x+7,y+9);dc.drawLine(x+3,y+8,x+7,y+5);dc.drawLine(x+7,y+5,x+11,y+8);dc.drawLine(x+7,y+9,x+4,y+14);dc.drawLine(x+7,y+9,x+10,y+14);break;
            case 25:
                dc.drawCircle(x+7,y+7,6);dc.drawLine(x+7,y+7,x+7,y+3);dc.drawLine(x+7,y+7,x+3,y+7);break;
            case 26:
                dc.drawLine(x,y+9,x+3,y+9);dc.drawLine(x+3,y+9,x+5,y+3);dc.drawLine(x+5,y+3,x+8,y+12);dc.drawLine(x+8,y+12,x+11,y+6);dc.drawLine(x+11,y+6,x+14,y+6);break;
            case 27:
                dc.drawLine(x+7,y,x+7,y+7);dc.drawCircle(x+4,y+9,3);dc.drawCircle(x+10,y+9,3);break;
            case 28:
                dc.drawCircle(x+7,y+7,6);dc.drawLine(x+7,y+7,x+11,y+3);dc.drawLine(x+2,y+11,x+12,y+11);break;
        }
    }
}
