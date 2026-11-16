"""Build compact offline festival dates from attributed HKO calendar facts."""
from pathlib import Path
import datetime,json

ROOT=Path(__file__).resolve().parents[1]

def generate():
    rows=json.loads((ROOT/'assets/festivals/dates.json').read_text())
    assert [r['year'] for r in rows]==list(range(2020,2041))
    days=lambda key:[datetime.date.fromisoformat(r[key]).timetuple().tm_yday for r in rows]
    (ROOT/'source/Festival.mc').write_text('''import Toybox.Lang;
// Calendar facts: Hong Kong Observatory, assets/festivals/dates.json.
// IDs: 0 ordinary, 1 Spring Festival, 2 Christmas, 3 Halloween, 4 Mid-Autumn.
module Festival {
 var spring as Array<Number> = '''+str(days('spring'))+''';
 var autumn as Array<Number> = '''+str(days('mid_autumn'))+''';
 function dayOfYear(year,month,day) {
  var before = [0,31,59,90,120,151,181,212,243,273,304,334] as Array<Number>;
  var leap=year%4==0 && (year%100!=0 || year%400==0);
  return before[month-1]+day+(leap && month>2 ? 1 : 0);
 }
 function choose(year,month,day,setting) {
  if(setting==1) {return 0;}
  if(setting>=2 && setting<=5) {return setting-1;}
  if(month==12 && day>=24 && day<=26) {return 2;}
  if(month==10 && day==31) {return 3;}
  if(year<2020 || year>2040 || month<1 || month>12 || day<1 || day>31) {return 0;}
  var index=year-2020;var doy=dayOfYear(year,month,day);
  // Eve through lunar Jan 7; Mid-Autumn on lunar Aug 15 (not a leap month).
  if(doy>=spring[index]-1 && doy<=spring[index]+6) {return 1;}
  return doy==autumn[index] ? 4 : 0;
 }
 function accent(holiday,fallback) {
  if(Device.MONO || holiday==0) {return fallback;}
  return holiday==1 ? 0xFFCC66 : (holiday==2 ? 0x99DDCC : (holiday==3 ? 0xFFAA55 : 0xDDCC99));
 }
}
''')

if __name__=='__main__':generate()
