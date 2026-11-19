import Toybox.Lang;
import Toybox.Math;
import Toybox.Position;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.Weather;

class TideData {
    const STEP = 1800;
    const SAMPLES = 71;
    const DEGREES = Math.PI/180.0;
    const ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    private var active = false;
    private var selection = 0;
    private var station as Array or Null;
    private var portPosition;
    private var locationAt = -1;
    private var anchor = -1;
    private var start = 0;
    private var haveLocation = false;
    private var levels as Array<Float> = new Float[SAMPLES];

    function reset(wanted) {
        active = wanted;
        selection = Preferences.read("TidePlace", 0, TideCatalog.PORTS.size()+1);
        station = selection > 0 ? TideCatalog.PORTS[selection-1] : null;
        portPosition = null;
        locationAt = -1;
        anchor = -1;
        haveLocation = false;
    }

    function nearest(lat, lon) {
        if (lat == null || lon == null || lat < -90 || lat > 90 || lon < -180 || lon > 180) { return null; }
        var scale = Math.cos(lat * DEGREES);
        // Close-range equirectangular distance. 0.55 degrees is about 61 km.
        var bestDistance = .55*.55;
        var nearestPort = null;
        for (var i=0; i<TideCatalog.PORTS.size(); i++) {
            var port = TideCatalog.PORTS[i];
            var dy = port[1]-lat;
            var dx = port[2]-lon;
            if (dx > 180) { dx -= 360; }
            if (dx < -180) { dx += 360; }
            dx *= scale;
            var distance = dx*dx+dy*dy;
            if (distance < bestDistance) {
                bestDistance = distance;
                nearestPort = port;
            }
        }
        return nearestPort;
    }

    function weatherPort(now) {
        var wx = Weather.getCurrentConditions();
        if (wx == null || !(wx has :observationLocationPosition) ||
            wx.observationLocationPosition == null || wx.observationTime == null) {
            haveLocation = false;
            return null;
        }
        var age = now-wx.observationTime.value();
        if (age < 0 || age > 21600) {
            haveLocation = false;
            return null;
        }
        var coords = wx.observationLocationPosition.toDegrees();
        haveLocation = true;
        return nearest(coords[0], coords[1]);
    }

    function update(now) {
        if (!active || now < 0) { return false; }
        var changed = false;
        if (selection == 0 && (locationAt < 0 || now < locationAt || now-locationAt >= 900)) {
            locationAt = now;
            var match = weatherPort(now);
            if (match != station) {
                station = match;
                portPosition = null;
                anchor = -1;
                changed = true;
            }
        }
        if (station != null) {
            var slot = now/STEP*STEP;
            if (slot != anchor) {
                anchor = slot;
                start = slot-6*STEP;
                calculate(start, station[3]);
            }
        }
        return changed;
    }

    function name() {
        return station == null ? null : station[0];
    }

    function position() {
        if (!active || station == null) { return null; }
        if (portPosition == null) {
            portPosition = new Position.Location({
                :latitude => station[1], :longitude => station[2], :format => :degrees
            });
        }
        return portPosition;
    }

    function status() {
        return haveLocation ? "CHOOSE PORT" : "WAIT LOCATION";
    }

    function calculate(epoch, harmonics) {
        var days = epoch/86400-TideCatalog.EPOCH_DAY;
        var ticks = (epoch%86400)/1800.0;
        var node = TideCatalog.NODE[0]+TideCatalog.NODE[1]*(days+ticks/48.0);
        var nodalCos = Math.cos(node);
        var nodalSin = Math.sin(node);
        for (var k=0; k<SAMPLES; k++) { levels[k] = 0.0; }
        for (var n=0; n<TideCatalog.TERMS.size(); n++) {
            var term = TideCatalog.TERMS[n];
            var offset = n*3;
            var code = (ALPHABET.find(harmonics.substring(offset, offset+1)) << 12) |
                       (ALPHABET.find(harmonics.substring(offset+1, offset+2)) << 6) |
                       ALPHABET.find(harmonics.substring(offset+2, offset+3));
            var amplitude = (term[3]+term[4]*nodalCos)*(code >> 9)*.5;
            var lag = (code & 511)*(2*Math.PI/512);
            var phase = term[0]+days*term[1]+ticks*term[2]+term[5]*nodalSin-lag;
            var real = amplitude*Math.cos(phase);
            var imag = amplitude*Math.sin(phase);
            var stepCos = Math.cos(term[2]);
            var stepSin = Math.sin(term[2]);
            // Rotate the constituent once per sample. No trig calls per point.
            for (var k=0; k<SAMPLES; k++) {
                levels[k] += real;
                var nextReal = real*stepCos-imag*stepSin;
                imag = imag*stepCos+real*stepSin;
                real = nextReal;
            }
        }
    }

    function nextExtreme(now, high) as Array<Numeric> or Null {
        if (station == null || anchor < 0) { return null; }
        for (var i=1; i<SAMPLES-1; i++) {
            var left = levels[i-1];
            var center = levels[i];
            var right = levels[i+1];
            if (high == 1 ? center <= left || center < right : center >= left || center > right) { continue; }
            // Refine the turning point between half-hour samples.
            var curve = left-2*center+right;
            var fraction = (left-right)/(2*curve);
            var time = start+i*STEP+(fraction*STEP).toNumber();
            if (time >= now) {
                var height = center - .25*(left-right)*fraction;
                return [time, height];
            }
        }
        return null;
    }

    function next(now, high, clockFormat) {
        var event = nextExtreme(now, high);
        if (event == null) { return null; }
        var nearestMinute = (event[0].toNumber()+30)/60*60;
        var local = Gregorian.info(new Time.Moment(nearestMinute), Time.FORMAT_SHORT);
        var hour = clockFormat ? (local.hour+11)%12+1 : local.hour;
        var suffix = clockFormat && local.hour >= 12 ? "P" : "";
        return hour.format("%d") + ":" + local.min.format("%02d") + suffix;
    }

    function height(now, high) {
        var event = nextExtreme(now, high);
        return event == null ? null : event[1].format("%.0f") + "CM";
    }

    function fill(now, values as Array<Numeric or Null>) {
        if (station == null || anchor < 0) { return; }
        var offset = now-anchor;
        var fraction = offset.toFloat()/STEP;
        for (var i=0; i<values.size(); i++) {
            values[i] = levels[i]+(levels[i+1]-levels[i])*fraction;
        }
    }
}
