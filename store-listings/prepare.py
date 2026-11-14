"""Turn reviewed browser translations into Garmin's 28 store-language records.

This does not change either application's runtime languages.
"""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parent
MOKE_TITLES={
'en':'Moke · Custom Data Watch Face','zh_CN':'墨刻·百变数据表盘','zh_TW':'墨刻 · 百變數據錶盤','ja':'Moke · カスタムデータ文字盤','ko':'Moke · 맞춤 데이터 워치페이스','in':'Moke · Tampilan Jam Data Kustom','ms':'Moke · Muka Jam Data Tersuai','cs':'Moke · Nastavitelný datový ciferník','da':'Moke · Urskive med tilpasselige data','de':'Moke · Anpassbares Datenzifferblatt','es':'Moke · Esfera de datos personalizable','fr':'Moke · Cadran de données personnalisable','hr':'Moke · Prilagodljivi podatkovni brojčanik','it':'Moke · Quadrante dati personalizzabile','hu':'Moke · Testreszabható adatkijelzős számlap','nl':'Moke · Aanpasbare gegevenswijzerplaat','nb':'Moke · Tilpassbar dataskive','pl':'Moke · Konfigurowalna tarcza danych','pt_BR':'Moke · Mostrador de dados personalizável','pt_PT':'Moke · Mostrador de dados personalizável','sk':'Moke · Prispôsobiteľný dátový ciferník','sl':'Moke · Prilagodljiva podatkovna številčnica','fi':'Moke · Mukautettava tietokellotaulu','sv':'Moke · Anpassningsbar dataurtavla','el':'Moke · Προσαρμόσιμη όψη δεδομένων','ru':'Moke · Настраиваемый циферблат данных','iw':'Moke · לוח שעון נתונים מותאם','th':'Moke · หน้าปัดข้อมูลปรับแต่งได้'}
RETRO_TITLES={
'en':'Retro World · Map Watch Face','zh_CN':'寰游时刻 · Retro World','zh_TW':'寰遊時刻 · Retro World','ja':'Retro World · 世界地図文字盤','ko':'Retro World · 세계 지도 워치페이스','in':'Retro World · Tampilan Jam Peta Dunia','ms':'Retro World · Muka Jam Peta Dunia','cs':'Retro World · Ciferník s mapou světa','da':'Retro World · Urskive med verdenskort','de':'Retro World · Weltkarten-Zifferblatt','es':'Retro World · Esfera con mapamundi','fr':'Retro World · Cadran carte du monde','hr':'Retro World · Brojčanik s kartom svijeta','it':'Retro World · Quadrante mappamondo','hu':'Retro World · Világtérképes számlap','nl':'Retro World · Wereldkaart-wijzerplaat','nb':'Retro World · Urskive med verdenskart','pl':'Retro World · Tarcza z mapą świata','pt_BR':'Retro World · Mostrador com mapa-múndi','pt_PT':'Retro World · Mostrador com mapa-múndi','sk':'Retro World · Ciferník s mapou sveta','sl':'Retro World · Številčnica z zemljevidom sveta','fi':'Retro World · Maailmankarttakellotaulu','sv':'Retro World · Urtavla med världskarta','el':'Retro World · Όψη ρολογιού με παγκόσμιο χάρτη','ru':'Retro World · Циферблат с картой мира','iw':'Retro World · לוח שעון מפת העולם','th':'Retro World · หน้าปัดแผนที่โลก'}

def split_copy(text):
    positions=[];pos=0
    for i in range(1,7):
        match=re.search(r'(?<![\d.])'+str(i)+r'[.．。]\s*',text[pos:])
        if not match:raise ValueError(f'Missing section {i}')
        start=pos+match.start();end=pos+match.end();positions.append((start,end));pos=end
    end=len(text)
    romanization=re.search(r'\n\s*1\s*[.。]',text[positions[-1][1]:])
    if romanization:end=min(end,positions[-1][1]+romanization.start())
    for marker in ['\n1.','\n1。','\n展开','\nstar_border']:
        index=text.find(marker,positions[-1][1])
        if index>=0:end=min(end,index)
    values=[]
    for i,(start,body) in enumerate(positions):
        stop=positions[i+1][0] if i<5 else end
        value=text[body:stop].strip().lstrip('ºª ').replace('BODYBATTERY_METRIC','Body Battery').replace('BODY BATTERY','Body Battery').replace('*','')
        value=value.replace('Body Battery (Body Battery)','Body Battery').replace('\u200b','').replace('\ufeff','')
        values.append(value)
    return values

def main():
    source=json.loads((ROOT/'source.json').read_text())
    raw=json.loads((ROOT/'translations.json').read_text())
    copies={code:split_copy(text) for code,text in raw['listing'].items()}
    for code,text in raw['retro'].items():
        first=re.search(r'(?<![\d.])1[.．。]\s*',text)
        second=re.search(r'(?<![\d.])2[.．。]\s*2\.1\.0',text[first.end():])
        assert second,code
        start=first.end()+second.start();body=first.end()+second.start()+2
        end=len(text)
        romanization=re.search(r'\n\s*1\s*[.。]',text[body:])
        if romanization:end=min(end,body+romanization.start())
        for marker in ['\n1.','\n1。','\n展开','\nstar_border']:
            pos=text.find(marker,body)
            if pos>=0:end=min(end,pos)
        copies[code][4]=text[first.end():start].strip().lstrip('ºª ').replace('\u200b','').replace('\ufeff','')
        copies[code][5]=text[body:end].strip().lstrip('ºª ').replace('\u200b','').replace('\ufeff','')
    copies['en']=source
    copies['zh_CN']=['百变数据表盘',
'''适用于兼容佳明 MIP 手表的黑白数据表盘，圆润醒目的数字时间搭配可配置数据区。免费使用，无订阅，无需开发者账号。

• 94 项设置、28 种数据选项，可调整或隐藏数据区、字体、字号、单位、图表和进度指示。
• 表盘与设置提供简体中文和英文，其他手表系统语言使用英文。
• 支持 12/24 小时制、深浅主题及可选秒数。简洁的默认布局在设备支持时显示身体电量（Body Battery）；装饰卡片、月相、风向和活动指示均可开关。
• 心率、步数、热量、海拔、天气和续航数据依赖手表能力与佳明系统缓存。缺失数据显示 --，表盘不主动启动 GPS。
• 装饰卡片不提供公交、门禁或支付功能。预览图片使用模拟数据。

数据在手表本地读取，开发者不收集或上传健康及位置数据。本应用独立开发，与 Garmin 无隶属关系。''',
'''1.2.0
• 新增圆角数字与更清爽的默认布局，右侧默认显示身体电量。
• 保留 94 项设置、28 种数据选项及中英文表盘界面。
• 视觉升级保留自定义卡片和数据选择。
• 优化设置写入时的内存处理，并改善极小图表数字的辨识度。''',
'世界地图表盘',
'''复古世界地图表盘，结合数字时间与模拟圆盘，提供 16 种地图样式、昼夜底纹、天气及日出日落。免费使用，无订阅，无需开发者账号。

• 21 项设置，包含 9 个可配置数据区、12/24 小时制、秒数、地图与定位点显示。
• 表盘内容始终保持英文，设置页提供简体中文与英文。
• 支持的 MIP 手表可使用持续局部走秒；AMOLED 常亮采用独立低亮、按分钟刷新的显示。具体能力随硬件及固件变化。
• 使用系统缓存的天气与位置，不主动启动 GPS。可选手动经纬度仅影响地图及太阳时间，不伪造天气。

缺失数据显示占位符。数据在手表本地读取，开发者不收集或上传健康及位置数据。预览图片使用模拟数据。本应用独立开发，与 Garmin 无隶属关系。''',
'''2.1.0
• 21 项设置及 9 个可配置数据区。
• 支持 12/24 小时制和可选小时前导零。
• 支持的 MIP 机型可持续局部走秒，AMOLED 保留独立常亮行为。
• 改善地区 API 兼容与太阳时间处理。
• 表盘内容继续保持英文。''']
    assert set(copies)==set(MOKE_TITLES)==set(RETRO_TITLES),(set(MOKE_TITLES)-set(copies),set(copies)-set(MOKE_TITLES))
    result={'moke':{},'retro-world':{}}
    for code,values in copies.items():
        for app,title,description,notes in [('moke',MOKE_TITLES[code],values[1],values[2]),('retro-world',RETRO_TITLES[code],values[4],values[5])]:
            assert len(title)<=50,(code,title,len(title))
            assert 100<len(description)<=4000 and 30<len(notes)<=4000,(code,app,len(description),len(notes))
            assert not any(marker in description+notes for marker in ['star_border','BODYBATTERY_METRIC','展开','\ufffd']),(app,code)
            result[app][code]=dict(title=title,description=description,whatsNew=notes)
    for app,languages in json.loads((ROOT/'overrides.json').read_text()).items():
        for code,fields in languages.items():result[app][code].update(fields)
    (ROOT/'copies.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Prepared 28 languages × 2 apps × title/description/release notes.')

if __name__=='__main__':main()
