"""Native pixel QA. Measurements are diagnostics, never an aesthetic score."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageChops


def compare(reference, actual, out, scale=4, regions=None, mask=None):
    ref, cur = Image.open(reference).convert('RGB'), Image.open(actual).convert('RGB')
    if ref.size != cur.size:
        raise ValueError('Native dimensions differ; align explicitly, do not auto-stretch.')
    if not 1 <= scale <= 8:
        raise ValueError('Review magnification must be 1..8.')
    valid = Image.open(mask).convert('L') if mask else Image.new('L', ref.size, 255)
    if valid.size != ref.size:
        raise ValueError('Mask must match the native framebuffer.')
    valid = valid.point(lambda p: 255 if p >= 128 else 0)
    if valid.getbbox() is None:
        raise ValueError('Mask has no visible pixels.')
    regions = regions or {'screen': [0, 0, ref.width, ref.height]}
    result = {'size': list(ref.size), 'scale': scale, 'regions': {},
              'meaning': 'Same-fixture aligned pixel differences; not a similarity or beauty score.'}
    delta = ImageChops.difference(ref, cur)
    heat = Image.new('RGB', ref.size)
    values = []
    for rgb, visible in zip(delta.getdata(), valid.getdata()):
        amount = max(rgb) if visible else 0
        values.append((amount, 0, amount))
    heat.putdata(values)
    for name, rect in regions.items():
        if len(rect) != 4 or any(type(v) is not int for v in rect):
            raise ValueError(f'{name}: region must be four integer pixels.')
        x, y, w, h = rect
        if x < 0 or y < 0 or w <= 0 or h <= 0 or x+w > ref.width or y+h > ref.height:
            raise ValueError(f'{name}: region outside framebuffer.')
        box = (x, y, x+w, y+h)
        samples = [rgb for rgb, visible in zip(delta.crop(box).getdata(), valid.crop(box).getdata()) if visible]
        if not samples:
            raise ValueError(f'{name}: region contains no visible pixels.')
        changed = sum(max(rgb) > 0 for rgb in samples)
        result['regions'][name] = {'rect': rect, 'visible_pixels': len(samples),
            'changed_pixels': changed, 'changed_fraction': changed/len(samples),
            'mean_channel_error_0_255': sum(sum(rgb) for rgb in samples)/(3*len(samples))}
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    strip = Image.new('RGB', (ref.width*3, ref.height))
    for i, img in enumerate((ref, cur, heat)):
        strip.paste(img, (i*ref.width, 0))
    strip.save(out/'native-reference-actual-diff.png')
    strip.resize((strip.width*scale, strip.height*scale), Image.Resampling.NEAREST).save(out/'magnified-reference-actual-diff.png')
    for label, path in (('reference', reference), ('actual', actual)):
        result[label+'_sha256'] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    (out/'pixel-report.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def atlas(font, out, ink='dark'):
    font = Path(font)
    pages, chars = {}, {}
    for line in font.read_text().splitlines():
        if line.startswith('page '):
            match = re.search(r'\bid=(\d+)\s+file="([^"]+)"', line)
            if not match:
                raise ValueError('Unsupported BMFont page declaration.')
            pages[int(match[1])] = Image.open(font.parent/match[2]).convert('RGBA')
        elif line.startswith('char '):
            row = {k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)', line)}
            chars[row['id']] = row
    if not pages or not chars:
        raise ValueError('Expected text BMFont with page and char entries.')
    errors, glyphs, signatures = [], {}, {}
    for code, row in chars.items():
        page = pages.get(row.get('page', 0))
        x,y,w,h = (row[k] for k in ('x','y','width','height'))
        if page is None or min(x,y,w,h) < 0 or x+w > page.width or y+h > page.height:
            errors.append(f'Glyph {code} has an invalid page or rectangle.')
            continue
        if code not in range(48,58):
            continue
        tile = page.crop((x,y,x+w,y+h))
        # Transparent atlases use coverage; opaque ones need explicit ink polarity.
        alpha = page.getchannel('A')
        if alpha.getextrema()[0] < 255:
            shape = tile.getchannel('A').point(lambda p:255 if p>=128 else 0)
        else:
            shape = tile.convert('L').point(lambda p:255 if ((p<128) if ink=='dark' else (p>=128)) else 0)
        box = shape.getbbox()
        glyphs[chr(code)] = {'box':[x,y,w,h], 'ink_bbox':list(box) if box else None,
                            'advance':row.get('xadvance'), 'yoffset':row.get('yoffset')}
        if box is None:
            errors.append(f'Digit {chr(code)} is blank.')
            continue
        cropped = shape.crop(box)
        key = (cropped.size, cropped.tobytes())
        if key in signatures:
            errors.append(f'Digits {signatures[key]} and {chr(code)} have identical ink.')
        signatures[key] = chr(code)
    missing = sorted(set('0123456789')-glyphs.keys())
    if missing:
        errors.append('Missing digits: '+''.join(missing))
    result = {'font':font.name,'glyphs':glyphs,'errors':errors,'passed':not errors}
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='mode',required=True)
    c = sub.add_parser('compare')
    c.add_argument('reference'); c.add_argument('actual'); c.add_argument('--out',required=True)
    c.add_argument('--scale',type=int,default=4); c.add_argument('--regions'); c.add_argument('--mask')
    a = sub.add_parser('atlas')
    a.add_argument('font'); a.add_argument('--out',required=True)
    a.add_argument('--ink',choices=['dark','light'],default='dark')
    args = p.parse_args()
    if args.mode == 'compare':
        regions = json.loads(Path(args.regions).read_text()) if args.regions else None
        result = compare(args.reference,args.actual,args.out,args.scale,regions,args.mask)
    else:
        result = atlas(args.font,args.out,args.ink)
    print(json.dumps(result,indent=2))
    return 1 if result.get('errors') else 0


if __name__ == '__main__':
    raise SystemExit(main())
