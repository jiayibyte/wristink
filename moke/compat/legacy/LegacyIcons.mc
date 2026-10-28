import Toybox.Graphics;
import Toybox.Math;
module LegacyIcons {
    function weather(dc,x,y,condition){var rows=WeatherGlyphs.pixels(condition);for(var yy=0;yy<15;yy++){for(var xx=0;xx<15;xx++){if((rows[yy]&(1<<xx))!=0){dc.drawPoint(x+xx,y+yy);}}}}
    function moon(dc, cx, cy, phase, ink, paper) {
        dc.setColor(ink, paper);
        dc.fillCircle(cx, cy, 7); dc.setColor(paper, paper);
        for (var y = -6; y <= 6; y++) {
            var span = Math.sqrt(36 - y * y); var edge = Math.cos(phase * 2 * Math.PI) * span;
            if (phase < 0.5) { dc.drawLine(cx + edge, cy + y, cx + span, cy + y); }
            else { dc.drawLine(cx - span, cy + y, cx - edge, cy + y); }
        }
        dc.setColor(ink, paper); dc.drawCircle(cx, cy, 7);
    }
    function sun(dc, x, y) {
        dc.drawCircle(x + 7, y + 6, 4);
        dc.drawLine(x + 7, y - 1, x + 7, y + 1); dc.drawLine(x + 7, y + 11, x + 7, y + 13);
        dc.drawLine(x, y + 6, x + 2, y + 6); dc.drawLine(x + 12, y + 6, x + 14, y + 6);
        dc.drawLine(x + 2, y + 1, x + 3, y + 2); dc.drawLine(x + 11, y + 10, x + 12, y + 11);
        dc.drawLine(x + 2, y + 11, x + 3, y + 10); dc.drawLine(x + 11, y + 2, x + 12, y + 1);
    }
    function draw(dc, kind, x, y, ink, paper, battery, condition) {
        dc.setColor(ink, paper);
        switch (kind) {
            case 1: case 17:
                dc.drawRectangle(x, y + 2, 12, 8); dc.fillRectangle(x + 12, y + 4, 2, 4);
                var fill = Math.floor((battery!=null ? battery : 0) * 8 / 100);
                if (fill > 8) { fill = 8; }
                if (fill > 0) { dc.fillRectangle(x + 2, y + 4, fill, 4); }
                break;
            case 2: dc.fillEllipse(x + 3, y + 4, 2, 4); dc.fillEllipse(x + 9, y + 6, 2, 4); dc.fillCircle(x + 3, y + 11, 1); dc.fillCircle(x + 9, y + 13, 1); break;
            case 3: dc.drawCircle(x + 6, y + 4, 4); dc.fillPolygon([[x + 2, y + 7], [x + 10, y + 7], [x + 6, y + 14]]); break;
            case 4: dc.setPenWidth(2); dc.drawLine(x, y + 12, x + 4, y + 12); dc.drawLine(x + 4, y + 12, x + 4, y + 7); dc.drawLine(x + 4, y + 7, x + 9, y + 7); dc.drawLine(x + 9, y + 7, x + 9, y + 2); dc.drawLine(x + 9, y + 2, x + 14, y + 2); dc.setPenWidth(1); break;
            case 5: dc.fillPolygon([[x + 7, y], [x + 12, y + 7], [x + 11, y + 12], [x + 5, y + 14], [x + 1, y + 10], [x + 2, y + 6], [x + 5, y + 8]]); dc.setColor(paper, paper); dc.fillEllipse(x + 7, y + 11, 2, 2); dc.setColor(ink, paper); break;
            case 6: dc.fillCircle(x + 4, y + 4, 3); dc.fillCircle(x + 10, y + 4, 3); dc.fillPolygon([[x + 1, y + 5], [x + 13, y + 5], [x + 7, y + 13]]); break;
            case 7: weather(dc,x,y,condition); break;
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
