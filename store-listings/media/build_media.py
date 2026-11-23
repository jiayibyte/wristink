"""Store artwork for Moke, Retro World and Alpine, laid out in HTML and rendered by headless Chrome.

Watch screens are real simulator captures (demo data) shown at integer scale where
they are low-resolution MIP screens; nothing on a watch screen is repainted.
Outputs go to store-listings/media/out/<app>/; JPEG screenshots stay under Garmin's 150 KB.

usage: python build_media.py [app ...]
"""
from pathlib import Path
import html, json, os, subprocess, sys, tempfile
from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
CAP = HERE / 'captures'
OUT = HERE / 'out'
TEXT = json.loads((HERE / 'text.json').read_text(encoding='utf-8'))
CHROME = next(p for p in [Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe'),
                          Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'),
                          Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
                          Path('/usr/bin/google-chrome'), Path('/usr/bin/chromium')] if p.exists())

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(w)dpx;height:%(h)dpx;overflow:hidden}
body{position:relative;font-family:'Bahnschrift','Segoe UI','Microsoft YaHei UI','Microsoft YaHei','Yu Gothic UI','Malgun Gothic','Leelawadee UI','Noto Sans','Noto Sans CJK SC','Noto Sans Thai',Arial,sans-serif;color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
.zh{font-family:'Microsoft YaHei UI','Microsoft YaHei','Bahnschrift','Noto Sans CJK SC',sans-serif}
.abs{position:absolute}
.eyebrow{font-size:26px;letter-spacing:.08em;color:var(--accent);font-weight:600}
.headline{font-weight:700;line-height:1.08;letter-spacing:-.01em}
.sub{color:var(--muted);line-height:1.45}
.badge{display:inline-block;padding:8px 18px;border-radius:999px;background:var(--badge-bg);color:var(--badge-ink);font-weight:700;font-size:20px;letter-spacing:.04em}
.note{color:var(--faint);font-size:16px}
.label{color:var(--muted);font-size:22px;text-align:center;font-weight:600;letter-spacing:.02em}
.watch{position:absolute;filter:drop-shadow(0 30px 40px rgba(0,0,0,.55))}
.watch .case{position:absolute;inset:0;border-radius:50%%;background:radial-gradient(circle at 32%% 22%%,#6b7078 0%%,#2a2d32 38%%,#121316 70%%,#08090a 100%%);box-shadow:inset 0 2px 2px rgba(255,255,255,.28),inset 0 -4px 8px rgba(0,0,0,.7)}
.watch .ring{position:absolute;border-radius:50%%;background:#050506;box-shadow:0 0 0 2px #3a3d42,inset 0 0 0 1px #000}
.watch .screen{position:absolute;border-radius:50%%;overflow:hidden;background:#000}
.watch img{position:absolute;inset:0;width:100%%;height:100%%;display:block}
.watch.inst .case{border-radius:24%%;background:linear-gradient(150deg,#4a4e55 0%%,#24272b 40%%,#121315 100%%)}
.watch.inst .ring{border-radius:12%%}
.watch.inst .screen{border-radius:0;clip-path:polygon(23%% 0,100%% 0,100%% 77%%,77%% 100%%,23%% 100%%,0 77%%,0 23%%)}
.watch.rect .case{border-radius:22%%}
.watch.rect .ring{border-radius:14%%}
.watch.rect .screen{border-radius:10%%}
.chips{display:flex;flex-wrap:wrap;gap:12px}
.chip{padding:9px 18px;border-radius:999px;border:1.5px solid var(--line);color:var(--ink);font-size:21px;background:rgba(255,255,255,.04)}
.dev{filter:drop-shadow(0 26px 36px rgba(0,0,0,.55))}
.dots{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.05) 1px,transparent 1.3px);background-size:22px 22px;pointer-events:none}
"""

PALETTES = {
    'moke': dict(bg='radial-gradient(1200px 800px at 75% 30%,#2a2b2f 0%,#121315 45%,#050506 100%)', ink='#f3efe6', accent='#e9e2d0',
                 muted='#a9a59b', faint='#6f6c66', line='#4a4844', **{'badge-bg': '#c8372d', 'badge-ink': '#fff6ee'}),
    'retro': dict(bg='radial-gradient(1200px 820px at 72% 35%,#1d3147 0%,#0e1828 48%,#060a12 100%)', ink='#f2f6fb', accent='#ffc35c',
                  muted='#9fb3c8', faint='#64788d', line='#36506b', **{'badge-bg': '#ffc35c', 'badge-ink': '#1a1206'}),
    'alpine': dict(bg='linear-gradient(180deg,#0d2347 0%,#15336a 45%,#0b1a36 100%)', ink='#f4f8fb', accent='#9fe3d2',
                   muted='#b7c9da', faint='#7b91a8', line='#3d5b82', **{'badge-bg': '#9fe3d2', 'badge-ink': '#06201b'}),
    'tide': dict(bg='radial-gradient(1200px 800px at 70% 30%,#0f3a4a 0%,#0a2230 48%,#04101a 100%)', ink='#eef8fa', accent='#5fe0c8',
                 muted='#9cc3cc', faint='#5f8792', line='#285463', **{'badge-bg': '#5fe0c8', 'badge-ink': '#04201c'}),
    'signal': dict(bg='radial-gradient(1200px 800px at 72% 32%,#2b2618 0%,#15130d 48%,#070605 100%)', ink='#f6efdc', accent='#ffb547',
                   muted='#c2b593', faint='#7d735c', line='#4a432f', **{'badge-bg': '#ffb547', 'badge-ink': '#211603'}),
}


def cap(name):
    path = CAP / f'{name}.png'
    if not path.exists():
        raise FileNotFoundError(path)
    if 'instinct' in name or '-i3-' in name:
        # Instinct screens are 1-bit: the simulator's faint grey residue and the
        # coloured window bezel are not visible on the watch. Map to pure black/white.
        mono = CAP / '_mono' / path.name
        mono.parent.mkdir(exist_ok=True)
        with Image.open(path) as im:
            im.convert('L').point(lambda v: 255 if v >= 128 else 0).convert('RGB').save(mono)
        return mono
    return path


sys.path.append(str(HERE.parents[1] / 'tools'))
import ciq_env  # noqa: E402
DEVICES = ciq_env.DEVICES


def device_of(name):
    for key, dev in (('instinct3solar45mm', 'instinct3solar45mm'), ('-i3-', 'instinct3solar45mm'), ('-f7-', 'fenix7'),
                     ('fenix7', 'fenix7'), ('venusq2', 'venusq2'), ('venu3', 'venu3'), ('epix2', 'epix2')):
        if key in name:
            return dev
    raise KeyError(name)


def device_art(dev):
    """Garmin's own SDK device render with its white backdrop removed (the screen hole is already clear)."""
    out = CAP / '_device' / f'{dev}.png'
    sim = json.loads((DEVICES / dev / 'simulator.json').read_text(encoding='utf-8'))
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(DEVICES / dev / sim['image']).convert('RGBA')
        w, h = im.size
        r, g, b, a = im.split()
        white = ImageChops.darker(ImageChops.darker(r, g), b).point(lambda v: 255 if v >= 236 else 0)
        flood = white.copy()
        for corner in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            if flood.getpixel(corner) == 255:
                ImageDraw.floodfill(flood, corner, 128)
        outside = flood.point(lambda v: 255 if v == 128 else 0)
        band = ImageChops.subtract(outside.filter(ImageFilter.MaxFilter(5)), outside)
        px = im.load(); ob = outside.load(); bb = band.load()
        for y in range(h):
            for x in range(w):
                if ob[x, y]:
                    px[x, y] = (0, 0, 0, 0)
                elif bb[x, y]:
                    cr, cg, cb, ca = px[x, y]
                    k = (255 - min(cr, cg, cb)) / 255
                    if k <= 0.02:
                        px[x, y] = (0, 0, 0, 0)
                    else:
                        un = lambda c: max(0, min(255, round((c - 255 * (1 - k)) / k)))
                        px[x, y] = (un(cr), un(cg), un(cb), round(ca * k))
        im.save(out)
    return out, sim['display']['location']


def composite(name, screen_px):
    """The capture inside the real watch render, scaled so the screen is screen_px wide, straps faded."""
    dev = device_of(name)
    art_path, loc = device_art(dev)
    s = screen_px / loc['width']
    dest = CAP / '_device' / f'{name}@{screen_px}.png'
    art = Image.open(art_path)
    aw, ah = round(art.width * s), round(art.height * s)
    art = art.resize((aw, ah), Image.Resampling.LANCZOS)
    with Image.open(cap(name)) as src:
        screen = src.convert('RGB')
    sw, sh = screen_px, round(loc['height'] * s)
    if screen.width <= 280:
        k = max(1, -(-sw // screen.width))
        screen = screen.resize((screen.width * k, screen.height * k), Image.Resampling.NEAREST)
    screen = screen.resize((sw, sh), Image.Resampling.LANCZOS if screen.width != sw else Image.Resampling.NEAREST)
    if loc['width'] == loc['height'] and dev not in ('instinct3solar45mm',):
        # Round screens: the capture square's corners are simulator backdrop, not screen.
        mask = Image.new('L', (sw * 4, sh * 4), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, sw * 4 - 1, sh * 4 - 1), fill=255)
        screen = screen.convert('RGBA')
        screen.putalpha(mask.resize((sw, sh), Image.Resampling.LANCZOS))
    screen = screen.convert('RGBA')
    canvas = Image.new('RGBA', (aw, ah), (0, 0, 0, 0))
    sx, sy = round(loc['x'] * s), round(loc['y'] * s)
    canvas.paste(screen, (sx, sy), screen)
    canvas.alpha_composite(art)
    cy = sy + sh / 2
    crop_h = min(ah, round(aw * 1.08))
    top = max(0, min(ah - crop_h, round(cy - crop_h / 2)))
    canvas = canvas.crop((0, top, aw, top + crop_h))
    fade = round(crop_h * 0.13)
    alpha = canvas.getchannel('A')
    ramp = Image.new('L', (1, crop_h), 255)
    for i in range(fade):
        v = round(255 * (i / fade) ** 1.4)
        ramp.putpixel((0, i), v); ramp.putpixel((0, crop_h - 1 - i), v)
    canvas.putalpha(ImageChops.multiply(alpha, ramp.resize((aw, crop_h))))
    canvas.save(dest)
    return dest, (sx + sw / 2, cy - top), canvas.size


def watch(name, screen_px, x, y, kind='round', pixel=None):
    """A real Garmin watch render with the capture on its screen, centred where the screen box was."""
    bezel = round(screen_px * (0.15 if kind == 'round' else 0.12))
    with Image.open(cap(name)) as im:
        native = im.size
    w = screen_px + 2 * bezel
    sh = round(screen_px * native[1] / native[0])
    h = sh + 2 * bezel
    path, (cx, cy), (cw, ch) = composite(name, screen_px)
    left = round(x + bezel + screen_px / 2 - cx)
    top = round(y + bezel + sh / 2 - cy)
    return (f'<img class="abs dev" src="{path.as_uri()}" style="left:{left}px;top:{top}px;width:{cw}px;height:{ch}px">'), w, h


def dev(name, device_w, cx, cy):
    """Real watch render device_w wide with its screen centred on (cx, cy). Returns markup and bottom y."""
    art_path, loc = device_art(device_of(name))
    with Image.open(art_path) as art:
        native_w = art.width
    path, (sx, sy), (cw, ch) = composite(name, round(device_w * loc['width'] / native_w))
    left, top = round(cx - sx), round(cy - sy)
    return (f'<img class="abs dev" src="{path.as_uri()}" style="left:{left}px;top:{top}px;width:{cw}px;height:{ch}px">', top + ch)


def label(text, cx, y, w=440):
    return f'<div class="abs label" style="left:{round(cx - w / 2)}px;top:{y}px;width:{w}px">{esc(text)}</div>'


def devs(items):
    """items: (name, device_w, cx, cy, label or None)."""
    out = []
    for name, w, cx, cy, lab in items:
        m, bottom = dev(name, w, cx, cy)
        out.append(m)
        if lab:
            out.append(label(lab, cx, bottom - 18))
    return ''.join(out)


def page(app, w, h, body, lang):
    css = BASE_CSS % dict(w=w, h=h)
    vars_ = ';'.join(f'--{k}:{v}' for k, v in PALETTES[app].items())
    cls = 'zh' if lang in ('zh', 'zh_CN') else ''
    code = BCP47.get(lang, lang)
    rtl = ' dir="rtl"' if lang == 'iw' else ''
    return (f'<!doctype html><html lang="{code}"><head><meta charset="utf-8"><style>{css}{LANG_CSS}:root{{{vars_}}}</style></head>'
            f'<body class="{cls}"{rtl}><div class="dots"></div>{body}</body></html>')


BCP47 = {'zh': 'zh-CN', 'zh_CN': 'zh-CN', 'zh_TW': 'zh-TW', 'in': 'id', 'iw': 'he', 'nb': 'nb', 'pt_BR': 'pt-BR', 'pt_PT': 'pt-PT'}
# Native CJK, Thai and Hebrew faces per storefront language (Chrome would otherwise borrow Chinese glyph forms).
LANG_CSS = (":lang(ja) body{font-family:'Bahnschrift','Yu Gothic UI','Yu Gothic','Meiryo',sans-serif}"
            ":lang(ko) body{font-family:'Bahnschrift','Malgun Gothic',sans-serif}"
            ":lang(zh-TW) body{font-family:'Bahnschrift','Microsoft JhengHei UI','Microsoft JhengHei',sans-serif}"
            ":lang(th) body{font-family:'Leelawadee UI','Segoe UI',sans-serif}"
            ":lang(he) body{font-family:'Segoe UI',Arial,sans-serif}")


def render(markup, out, w, h, limit=None):
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        page_path = Path(tmp) / 'page.html'
        page_path.write_text(markup, encoding='utf-8')
        png = Path(tmp) / 'shot.png'
        # A throwaway profile: never attach to (or open pages in) a running browser.
        subprocess.run([str(CHROME), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                        f'--user-data-dir={Path(tmp) / "profile"}', '--no-first-run', '--no-default-browser-check',
                        '--allow-file-access-from-files', f'--window-size={w},{h}', f'--screenshot={png}', page_path.as_uri()],
                       check=True, capture_output=True, timeout=120)
        im = Image.open(png).convert('RGB')
        assert im.size == (w, h), im.size
        if out.suffix == '.png':
            im.save(out, optimize=True)
        else:
            for q in (92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 66, 62, 58, 54, 50):
                im.save(out, quality=q, optimize=True, progressive=True, subsampling=0 if q >= 84 else 2)
                if limit is None or out.stat().st_size < limit:
                    break
    if limit is not None:
        assert out.stat().st_size < limit, (out, out.stat().st_size)
    print(out.relative_to(HERE), out.stat().st_size)


def esc(s):
    return html.escape(s).replace('\n', '<br>')


def text_block(t, x, y, width, size=72, sub_size=30, badge=None):
    parts = [f'<div class="abs" style="left:{x}px;top:{y}px;width:{width}px">']
    if t.get('eyebrow'):
        parts.append(f'<div class="eyebrow">{esc(t["eyebrow"])}</div>')
    parts.append(f'<div class="headline" style="font-size:{size}px;margin-top:18px">{esc(t["headline"])}</div>')
    if t.get('sub'):
        parts.append(f'<div class="sub" style="font-size:{sub_size}px;margin-top:22px">{esc(t["sub"])}</div>')
    if badge:
        parts.append(f'<div style="margin-top:30px"><span class="badge">{esc(badge)}</span></div>')
    parts.append('</div>')
    return ''.join(parts)


# ---------------------------------------------------------------- layouts
def hero(app, lang, t, watches):
    size = 76 if max(len(line) for line in t['hero']['headline'].split(chr(10))) <= 16 else 62
    body = text_block(t['hero'], 80 if lang != 'iw' else 740, 120, 620, size, 30, t.get('badge'))
    side = 'left' if lang != 'iw' else 'right'
    body += f'<div class="abs note" style="{side}:80px;bottom:40px">{esc(t["note"])}</div>'
    body += ''.join(watches)
    return page(app, 1440, 720, body, lang)


def alpine_locale(lang):
    """Banner text for one storefront language from alpine/store/localizations.json and the badge/note translations."""
    if lang in ('zh', 'en'):
        return TEXT['alpine'][lang]
    loc = json.loads((HERE.parents[1] / 'alpine/store/localizations.json').read_text(encoding='utf-8'))[lang]
    extra = {}
    for part in ('a', 'b'):
        extra.update(json.loads((HERE / 'i18n' / f'alpine-{part}.json').read_text(encoding='utf-8')))
    e = extra[lang]
    eyebrow = '山境 · Alpine' if lang == 'zh_TW' else 'ALPINE'
    return {'hero': {'eyebrow': eyebrow, 'headline': loc['headline'], 'sub': loc['tagline']}, 'badge': e['badge'], 'note': e['note']}


def hero_locale(app, lang):
    """Moke/Retro World banner text for one storefront language (i18n/hero-moke-retro.json; note shared with Alpine)."""
    if lang in ('zh', 'en'):
        return TEXT[app][lang]
    h = json.loads((HERE / 'i18n' / 'hero-moke-retro.json').read_text(encoding='utf-8'))[app][lang]
    eyebrow = h.get('eyebrow', TEXT[app]['en']['hero']['eyebrow'])
    return {'hero': {'eyebrow': eyebrow, 'headline': h['headline'], 'sub': h['sub']}, 'badge': h['badge'],
            'note': alpine_locale(lang)['note']}


def hero_watches(app, lang):
    """Device renders for the hero; mirrored for right-to-left Hebrew. Only Chinese has its own watch captures."""
    mirror = (lambda x: 1440 - x) if lang == 'iw' else (lambda x: x)
    if app == 'moke':
        face = 'zh' if lang == 'zh' else 'en'
        return [devs([(f'moke-{face}-f7-light', 300, mirror(790), 500, None), (f'moke-{face}-i3-dark', 470, mirror(1110), 360, None)])]
    return [devs([('retro-venu3-t1', 270, mirror(800), 510, None), ('retro-venu3-t5', 270, mirror(1290), 520, None),
                  ('retro-venu3-t0', 450, mirror(1050), 350, None)])]


def build_heroes(app, locales=None):
    """Hero banners for every storefront language (1440x720)."""
    folder = 'moke' if app == 'moke' else 'retro-world'
    for lang in locales or ALPINE_LOCALES:
        key = 'zh_CN' if lang == 'zh' else lang
        render(hero(app, lang, hero_locale(app, lang), hero_watches(app, lang)), OUT / folder / f'hero-{key}-1440x720.jpg',
               1440, 720, 1_000_000)


# ---------------------------------------------------------------- 5-slot store set
# Garmin allows five screenshots shared by every language, so each face gets two dense
# English/Chinese pairs plus one language-neutral device collage: en, zh, en, zh, devices.
COMBO = json.loads((HERE / 'i18n' / 'combo.json').read_text(encoding='utf-8'))


def combo_page(app, lang, eyebrow, title, sub, inner, note, title_size=58):
    head = (f'<div class="abs" style="left:80px;top:60px;width:1280px">'
            f'<div class="eyebrow">{esc(eyebrow)}</div>'
            f'<div class="headline" style="font-size:{title_size}px;margin-top:12px">{esc(title)}</div>'
            + (f'<div class="sub" style="font-size:27px;margin-top:14px;max-width:1240px">{esc(sub)}</div>' if sub else '') + '</div>')
    foot = f'<div class="abs note" style="left:80px;bottom:30px">{esc(note)}</div>' if note else ''
    return page(app, 1440, 1280, head + inner + foot, lang)


def stat_cards(stats):
    return ''.join(
        f'<div style="background:rgba(255,255,255,.05);border:1.5px solid var(--line);border-radius:22px;padding:24px 24px 22px">'
        f'<div style="font-size:52px;font-weight:700;color:var(--accent);line-height:1.05;white-space:nowrap">{esc(v)}</div>'
        f'<div class="sub" style="font-size:22px;margin-top:10px">{esc(c)}</div></div>' for v, c in stats)


def data_inner(watch_markup, pw, s):
    """Watch on the left; power/size cards, every data option and the extra note on the right; power tip across the foot."""
    style = 'font-size:20px;padding:7px 14px' if len(s['chips']) > 14 else 'font-size:23px;padding:9px 18px'
    chips = ''.join(f'<span class="chip" style="{style}">{esc(c)}</span>' for c in s['chips'])
    right = (f'<div class="abs" style="left:680px;top:295px;width:690px;display:flex;flex-direction:column;gap:30px">'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">{stat_cards(pw["stats"])}</div>'
             f'<div class="chips" style="gap:12px">{chips}</div>'
             f'<div class="sub" style="font-size:25px">{esc(s["extra"])}</div></div>')
    tip = (f'<div class="abs" style="left:80px;top:1120px;width:1280px;padding:18px 26px;border-radius:18px;'
           f'background:rgba(255,255,255,.05);border:1.5px solid var(--line)"><span class="sub" style="font-size:23px">{esc(pw["tip"])}</span></div>')
    return watch_markup + right + tip


def row(names, labels, device_w, cy, x0, x1):
    """One evenly spaced row of watches with labels between x0 and x1 (centres)."""
    n = len(names)
    step = (x1 - x0) / (n - 1) if n > 1 else 0
    return devs([(name, device_w, round(x0 + i * step), cy, lab) for i, (name, lab) in enumerate(zip(names, labels))])


def build_combo(app):
    key = 'retro' if app == 'retro' else app
    folder = {'moke': 'moke', 'retro': 'retro-world', 'alpine': 'alpine'}[app]
    o = OUT / folder
    for lang in ('en', 'zh'):
        t, c = TEXT[key][lang], COMBO[key][lang]
        s, pw, eb = t['screens'], t['power'], t['power']['eyebrow']
        if app == 'moke':
            src = cap(f'moke-{lang}-i3-dark').as_uri()
            zoom = (f'<div class="abs" style="left:780px;top:300px;width:480px;height:480px;border-radius:28px;overflow:hidden;'
                    f'box-shadow:0 0 0 2px var(--line),0 30px 50px rgba(0,0,0,.5);background:#000">'
                    f'<img src="{src}" style="position:absolute;width:{176 * 4}px;height:{176 * 4}px;left:{-8 * 4}px;top:{-64 * 4}px;image-rendering:pixelated"></div>'
                    + label(s[0]['zoom'], 1020, 796, 520))
            look = devs([(f'moke-{lang}-i3-dark', 500, 400, 545, None)]) + zoom
            look += row([f'moke-{lang}-i3-dark'] + [f'moke-en-i3-font{i}' for i in range(1, 6)], s[1]['labels'], 190, 1005, 140, 1300)
            data = data_inner(devs([(f'moke-{lang}-i3-dark', 580, 340, 690, None)]), pw, s[3])
            note = s[1]['note']
        elif app == 'retro':
            look = row([f'retro-venu3-t{i}' for i in range(6)], s[0]['labels'], 225, 465, 140, 1300)
            look += row(['retro-venu3-t0', 'retro-fenix7-t0', 'retro-instinct3solar45mm-t0', 'retro-venusq2-t1'], s[1]['labels'], 310, 880, 220, 1220)
            data = data_inner(devs([('retro-venu3-t2', 580, 340, 690, None)]), pw, s[2])
            note = s[1]['note']
        else:
            look = row([f'alpine-epix2-m{i}' for i in range(4)], s[0]['labels'], 290, 500, 200, 1240)
            look += row(['alpine-epix2-m0', 'alpine-fenix7-m2', 'alpine-instinct3solar45mm-m0'], s[1]['labels'], 320, 945, 280, 1160)
            data = data_inner(devs([('alpine-instinct3solar45mm-tl', 580, 340, 690, None)]), pw, s[2])
            note = s[1]['note']
        render(combo_page(key, lang, eb, c['look']['title'], c['look']['sub'], look, note), o / f'c1-look-{lang}.jpg', 1440, 1280, 148_000)
        render(combo_page(key, lang, eb, c['data']['title'], c['data']['sub'], data, pw['note']), o / f'c2-data-{lang}.jpg', 1440, 1280, 148_000)
    collage = {
        'moke': [[('moke-en-i3-dark', 'Instinct 3'), ('moke-en-i3-font3', 'Instinct 3'), ('moke-en-i3-light', 'Instinct 3')],
                 [('moke-en-f7-dark', 'fēnix 7'), ('moke-en-i3-font5', 'Instinct 3'), ('moke-en-f7-light', 'fēnix 7')]],
        'retro': [[('retro-fenix7-t0', 'fēnix 7'), ('retro-venu3-t1', 'Venu 3'), ('retro-instinct3solar45mm-t0', 'Instinct 3')],
                  [('retro-venusq2-t1', 'Venu Sq 2'), ('retro-venu3-t4', 'Venu 3'), ('retro-fenix7-t3', 'fēnix 7')]],
        'alpine': [[('alpine-epix2-m0', 'epix 2'), ('alpine-fenix7-m2', 'fēnix 7'), ('alpine-instinct3solar45mm-m0', 'Instinct 3')],
                   [('alpine-epix2-m1', 'epix 2'), ('alpine-instinct3solar45mm-m1', 'Instinct 3'), ('alpine-epix2-m3', 'epix 2')]],
    }[app]
    inner = ''.join(row([n for n, _ in r], [l for _, l in r], 360, cy, 270, 1170) for r, cy in zip(collage, (520, 975)))
    eyebrow = TEXT[key]['en']['hero']['eyebrow']
    render(combo_page(key, 'en', eyebrow, COMBO[key]['devices'], None, inner, 'Simulator captures · demo data', 52),
           o / 'c3-devices.jpg', 1440, 1280, 148_000)


def screenshot(app, lang, s, inner):
    body = (f'<div class="abs" style="left:80px;top:64px;width:1280px">'
            f'<div class="eyebrow">{esc(s.get("eyebrow", ""))}</div>'
            f'<div class="headline" style="font-size:62px;margin-top:14px">{esc(s["title"])}</div>'
            f'<div class="sub" style="font-size:28px;margin-top:16px">{esc(s["sub"])}</div></div>')
    body += inner
    body += f'<div class="abs note" style="left:80px;bottom:34px">{esc(s.get("note", ""))}</div>'
    return page(app, 1440, 1280, body, lang)


def grid(names, labels, screen_px, cols, top, kind='round', pixel=None, gap_y=70):
    """Evenly spaced watches with labels, centred in the 1440 canvas."""
    out = []
    probe = watch(names[0], screen_px, 0, 0, kind, pixel)
    w, h = probe[1], probe[2]
    cell = 1440 / cols
    for i, (name, label) in enumerate(zip(names, labels)):
        cx = cell * (i % cols) + cell / 2
        row = i // cols
        y = top + row * (h + gap_y)
        markup, ww, hh = watch(name, screen_px, round(cx - w / 2), y, kind, pixel)
        out.append(markup)
        out.append(f'<div class="abs label" style="left:{round(cx - 200)}px;top:{y + hh + 12}px;width:400px">{esc(label)}</div>')
    return ''.join(out)


def power(app, lang, pw, watch_markup):
    """Big-number cards for size and power facts, beside one watch."""
    cards = ''.join(
        f'<div style="background:rgba(255,255,255,.05);border:1.5px solid var(--line);border-radius:26px;padding:30px 30px 26px">'
        f'<div style="font-size:60px;font-weight:700;color:var(--accent);line-height:1.05;white-space:nowrap">{esc(v)}</div>'
        f'<div class="sub" style="font-size:23px;margin-top:14px">{esc(c)}</div></div>' for v, c in pw['stats'])
    side = (f'<div class="abs" style="left:640px;top:330px;width:720px;display:grid;grid-template-columns:1fr 1fr;gap:22px">{cards}</div>'
            f'<div class="abs sub" style="left:640px;top:900px;width:720px;font-size:25px">{esc(pw["tip"])}</div>')
    return screenshot(app, lang, dict(eyebrow=pw['eyebrow'], title=pw['title'], sub=pw['sub'], note=pw['note']), watch_markup + side)


def chips_block(s, left=760, top=400, width=600):
    chips = ''.join(f'<span class="chip">{esc(c)}</span>' for c in s['chips'])
    return (f'<div class="abs" style="left:{left}px;top:{top}px;width:{width}px"><div class="chips">{chips}</div>'
            f'<div class="sub" style="font-size:26px;margin-top:36px">{esc(s["extra"])}</div></div>')


def cover(app, name, device_w):
    m, _ = dev(name, device_w, 250, 250)
    return page(app, 500, 500, m, 'en')


def build_moke():
    for lang in ('zh', 'en'):
        t = TEXT['moke'][lang]
        s = t['screens']
        o = OUT / 'moke'
        render(hero('moke', lang, t, [devs([(f'moke-{lang}-f7-light', 300, 790, 500, None), (f'moke-{lang}-i3-dark', 470, 1110, 360, None)])]),
               o / f'hero-{lang}-1440x720.jpg', 1440, 720, 1_000_000)
        src = cap(f'moke-{lang}-i3-dark').as_uri()
        zoom = (f'<div class="abs" style="left:860px;top:400px;width:480px;height:480px;border-radius:28px;overflow:hidden;'
                f'box-shadow:0 0 0 2px var(--line),0 30px 50px rgba(0,0,0,.5);background:#000">'
                f'<img src="{src}" style="position:absolute;width:{176 * 4}px;height:{176 * 4}px;left:{-8 * 4}px;top:{-62 * 4}px;image-rendering:pixelated"></div>'
                + label(s[0]['zoom'], 1100, 900, 480))
        render(screenshot('moke', lang, s[0], devs([(f'moke-{lang}-i3-dark', 640, 400, 720, None)]) + zoom), o / f'01-pixels-{lang}.jpg', 1440, 1280, 148_000)
        render(power('moke', lang, t['power'], devs([(f'moke-{lang}-i3-dark', 560, 330, 690, None)])), o / f'02-power-{lang}.jpg', 1440, 1280, 148_000)
        names = [f'moke-{lang}-i3-dark'] + [f'moke-en-i3-font{i}' for i in range(1, 6)]
        items = [(n, 360, 240 + (i % 3) * 480, 470 + (i // 3) * 440, l) for i, (n, l) in enumerate(zip(names, s[1]['labels']))]
        render(screenshot('moke', lang, s[1], devs(items)), o / f'03-time-styles-{lang}.jpg', 1440, 1280, 148_000)
        inner = devs([(f'moke-{lang}-i3-dark', 390, 450, 470, None), (f'moke-{lang}-i3-light', 390, 990, 470, None),
                      (f'moke-{lang}-f7-dark', 330, 450, 950, None), (f'moke-{lang}-f7-light', 330, 990, 950, None)])
        inner += label(s[2]['labels'][0], 720, 676, 700) + label(s[2]['labels'][1], 720, 1140, 700)
        render(screenshot('moke', lang, s[2], inner), o / f'04-themes-round-{lang}.jpg', 1440, 1280, 148_000)
        render(screenshot('moke', lang, s[3], devs([(f'moke-{lang}-i3-dark', 560, 350, 700, None)]) + chips_block(s[3])),
               o / f'05-data-{lang}.jpg', 1440, 1280, 148_000)
    render(cover('moke', 'moke-en-i3-dark', 470), OUT / 'moke' / 'cover-500.png', 500, 500, 300_000)


def build_retro():
    for lang in ('zh', 'en'):
        t = TEXT['retro'][lang]
        s = t['screens']
        o = OUT / 'retro-world'
        render(hero('retro', lang, t, [devs([('retro-venu3-t1', 270, 800, 510, None), ('retro-venu3-t5', 270, 1290, 520, None),
                                             ('retro-venu3-t0', 450, 1050, 350, None)])]), o / f'hero-{lang}-1440x720.jpg', 1440, 720, 1_000_000)
        items = [(f'retro-venu3-t{i}', 330, 240 + (i % 3) * 480, 470 + (i // 3) * 440, s[0]['labels'][i]) for i in range(6)]
        render(screenshot('retro', lang, s[0], devs(items)), o / f'01-themes-{lang}.jpg', 1440, 1280, 148_000)
        render(power('retro', lang, t['power'], devs([('retro-venu3-t3', 520, 330, 690, None)])), o / f'02-power-{lang}.jpg', 1440, 1280, 148_000)
        items = [('retro-venu3-t0', 370, 360, 480, s[1]['labels'][0]), ('retro-fenix7-t0', 360, 1080, 480, s[1]['labels'][1]),
                 ('retro-instinct3solar45mm-t0', 390, 360, 930, s[1]['labels'][2]), ('retro-venusq2-t1', 320, 1080, 930, s[1]['labels'][3])]
        render(screenshot('retro', lang, s[1], devs(items)), o / f'03-screens-{lang}.jpg', 1440, 1280, 148_000)
        render(screenshot('retro', lang, s[2], devs([('retro-venu3-t2', 600, 370, 700, None)]) + chips_block(s[2], 760, 430)),
               o / f'04-data-{lang}.jpg', 1440, 1280, 148_000)
    render(cover('retro', 'retro-venu3-t0', 470), OUT / 'retro-world' / 'cover-500.png', 500, 500, 300_000)


ALPINE_LOCALES = ('zh', 'en', 'zh_TW', 'ja', 'ko', 'de', 'fr', 'es', 'it', 'pt_BR', 'pt_PT', 'nl', 'da', 'nb', 'sv', 'fi', 'pl',
                  'cs', 'sk', 'sl', 'hr', 'hu', 'ru', 'el', 'iw', 'th', 'in', 'ms')


def build_alpine(locales=ALPINE_LOCALES):
    for lang in locales:
        t = alpine_locale(lang)
        o = OUT / 'alpine'
        key = 'zh_CN' if lang == 'zh' else lang
        mirror = (lambda x: 1440 - x) if lang == 'iw' else (lambda x: x)
        render(hero('alpine', lang, t, [devs([('alpine-epix2-m2', 260, mirror(800), 510, None), ('alpine-epix2-m1', 260, mirror(1295), 520, None),
                                              ('alpine-epix2-m0', 440, mirror(1050), 350, None)])]), o / f'hero-{key}-1440x720.jpg', 1440, 720, 1_000_000)
        if lang not in ('zh', 'en'):
            continue
        s = t['screens']
        items = [(f'alpine-epix2-m{i}', 400, 400 + (i % 2) * 640, 480 + (i // 2) * 450, s[0]['labels'][i]) for i in range(4)]
        render(screenshot('alpine', lang, s[0], devs(items)), o / f'01-mountains-{lang}.jpg', 1440, 1280, 148_000)
        render(power('alpine', lang, t['power'], devs([('alpine-epix2-m3', 520, 330, 690, None)])), o / f'02-power-{lang}.jpg', 1440, 1280, 148_000)
        items = [('alpine-epix2-m0', 400, 250, 640, s[1]['labels'][0]), ('alpine-fenix7-m2', 380, 720, 640, s[1]['labels'][1]),
                 ('alpine-instinct3solar45mm-m0', 420, 1190, 640, s[1]['labels'][2])]
        render(screenshot('alpine', lang, s[1], devs(items)), o / f'03-screens-{lang}.jpg', 1440, 1280, 148_000)
        render(screenshot('alpine', lang, s[2], devs([('alpine-instinct3solar45mm-tl', 580, 360, 700, None)]) + chips_block(s[2])),
               o / f'04-data-{lang}.jpg', 1440, 1280, 148_000)
    render(cover('alpine', 'alpine-epix2-m0', 470), OUT / 'alpine' / 'cover-500.png', 500, 500, 300_000)


# ---------------------------------------------------------------- Tide Grid and Signal LCD
# Same set as Alpine: 28 localized heroes, a cover, and the five store screenshots
# (look and data pages in English and Chinese, plus a language-neutral collage).
NEW_FACES = {
    'tide': dict(folder='tide-grid', cover='tide-epix2-t0',
                 hero=[('tide-venu3-t2', 270, 800, 510), ('tide-venu3-t7', 270, 1290, 520), ('tide-epix2-t0', 450, 1050, 350)],
                 look=[['tide-epix2-t0', 'tide-fenix7-t1', 'tide-venu3-t7'], ['tide-venu3-t2', 'tide-venusq2-t9', 'tide-instinct3solar45mm-t4']],
                 data='tide-epix2-steps',
                 collage=[[('tide-epix2-t0', 'epix 2'), ('tide-fenix7-t1', 'fēnix 7'), ('tide-instinct3solar45mm-t4', 'Instinct 3')],
                          [('tide-venusq2-t9', 'Venu Sq 2'), ('tide-venu3-t7', 'Venu 3'), ('tide-venu3-t2', 'Venu 3')]]),
    'signal': dict(folder='signal-lcd', cover='signal-venu3-t1',
                   hero=[('signal-venu3-t9', 270, 800, 510), ('signal-epix2-t11', 270, 1290, 520), ('signal-venu3-t1', 450, 1050, 350)],
                   look=[['signal-venu3-t1', 'signal-epix2-t0', 'signal-fenix7-t7'], ['signal-venu3-t9', 'signal-epix2-t11', 'signal-instinct3solar45mm-t0']],
                   data='signal-venu3-t0',
                   collage=[[('signal-venu3-t1', 'Venu 3'), ('signal-fenix7-t7', 'fēnix 7'), ('signal-instinct3solar45mm-t0', 'Instinct 3')],
                            [('signal-epix2-t11', 'epix 2'), ('signal-venu3-t9', 'Venu 3'), ('signal-fenix7-t0', 'fēnix 7')]]),
}


def keep_together(sub):
    """No line break between a number and its noun, or before a ' · ' separator."""
    import re
    return re.sub(r'(\d) ', '\\1\u00a0', sub.replace(' · ', '\u00a0· '))


def new_face_locale(app, lang):
    """Hero text: zh/en from text.json, other storefronts from i18n/<app>.json (the demo note is shared with Alpine)."""
    if lang in ('zh', 'en'):
        t = json.loads(json.dumps(TEXT[app][lang]))
        t['hero']['sub'] = keep_together(t['hero']['sub'])
        return t
    h = json.loads((HERE / 'i18n' / f'{app}.json').read_text(encoding='utf-8'))['heroes'][lang]
    return {'hero': {'eyebrow': TEXT[app]['en']['hero']['eyebrow'], 'headline': h['headline'], 'sub': keep_together(h['sub'])},
            'badge': h['badge'], 'note': alpine_locale(lang)['note']}


def build_new_face(app, locales=ALPINE_LOCALES):
    f = NEW_FACES[app]
    o = OUT / f['folder']
    for lang in locales:
        key = 'zh_CN' if lang == 'zh' else lang
        mirror = (lambda x: 1440 - x) if lang == 'iw' else (lambda x: x)
        watches = [devs([(n, w, mirror(x), y, None) for n, w, x, y in f['hero']])]
        render(hero(app, lang, new_face_locale(app, lang), watches), o / f'hero-{key}-1440x720.jpg', 1440, 720, 1_000_000)
    combo = json.loads((HERE / 'i18n' / f'{app}.json').read_text(encoding='utf-8'))['combo']
    for lang in ('en', 'zh'):
        t, c = TEXT[app][lang], combo[lang]
        s, pw = t['screens'], t['power']
        look = row(f['look'][0], s[0]['labels'], 300, 500, 250, 1190) + row(f['look'][1], s[1]['labels'], 300, 945, 250, 1190)
        data = data_inner(devs([(f['data'], 580, 340, 690, None)]), pw, s[2])
        render(combo_page(app, lang, pw['eyebrow'], c['look']['title'], c['look']['sub'], look, s[1]['note']), o / f'c1-look-{lang}.jpg', 1440, 1280, 148_000)
        render(combo_page(app, lang, pw['eyebrow'], c['data']['title'], c['data']['sub'], data, pw['note']), o / f'c2-data-{lang}.jpg', 1440, 1280, 148_000)
    inner = ''.join(row([n for n, _ in r], [l for _, l in r], 360, cy, 270, 1170) for r, cy in zip(f['collage'], (520, 975)))
    render(combo_page(app, 'en', TEXT[app]['en']['hero']['eyebrow'], combo['devices'], None, inner, 'Simulator captures · demo data', 52),
           o / 'c3-devices.jpg', 1440, 1280, 148_000)
    render(cover(app, f['cover'], 470), o / 'cover-500.png', 500, 500, 300_000)


if __name__ == '__main__':
    apps = sys.argv[1:] or ['moke', 'retro', 'alpine']
    for app in apps:
        {'moke': build_moke, 'retro': build_retro, 'alpine': build_alpine,
         'moke-heroes': lambda: build_heroes('moke'), 'retro-heroes': lambda: build_heroes('retro'),
         'moke-combo': lambda: build_combo('moke'), 'retro-combo': lambda: build_combo('retro'),
         'alpine-combo': lambda: build_combo('alpine'),
         'tide': lambda: build_new_face('tide'), 'signal': lambda: build_new_face('signal')}[app]()
