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


def atlas(font, out, ink='dark', one_bit=False):
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
    errors, warnings, glyphs, signatures, spans = [], [], {}, {}, {}
    levels = set()
    for page in pages.values():
        levels |= set(page.getchannel('A').getdata())
    if one_bit and levels - {0, 255}:
        # The compiler thresholds grey coverage on a 1-bit target; the result
        # is not the shape that was reviewed.
        errors.append('Atlas has grey coverage but the target is 1-bit.')
    for code, row in chars.items():
        page = pages.get(row.get('page', 0))
        x,y,w,h = (row[k] for k in ('x','y','width','height'))
        if page is None or min(x,y,w,h) < 0 or x+w > page.width or y+h > page.height:
            errors.append(f'Glyph {code} has an invalid page or rectangle.')
            continue
        tile = page.crop((x,y,x+w,y+h))
        # Transparent atlases use coverage; opaque ones need explicit ink polarity.
        alpha = page.getchannel('A')
        if alpha.getextrema()[0] < 255:
            shape = tile.getchannel('A').point(lambda p:255 if p>=128 else 0)
        else:
            shape = tile.convert('L').point(lambda p:255 if ((p<128) if ink=='dark' else (p>=128)) else 0)
        box = shape.getbbox()
        if box and 'xadvance' in row:
            # Ink columns relative to the pen, as drawText places them.
            spans[code] = (row.get('xoffset', 0)+box[0], row.get('xoffset', 0)+box[2], row['xadvance'])
        if code not in range(48,58):
            continue
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
    # Isolated tiles hide the commonest legibility defect: ink wider than the
    # advance, so neighbours touch once the glyphs are set as running text.
    def gap(left, right):
        return spans[left][2]+spans[right][0]-spans[left][1]
    digits = [code for code in range(48,58) if code in spans]
    touching = [chr(a)+chr(b) for a in digits for b in digits if gap(a,b) < 1]
    if touching:
        errors.append('Digits touch or overlap in running text: '+' '.join(touching[:12])+
                      (f' (+{len(touching)-12} more)' if len(touching) > 12 else ''))
    crowded = [chr(code) for code in spans if code not in range(48,58) and gap(code,code) < 1]
    if crowded:
        warnings.append('Glyphs touch a repeat of themselves: '+''.join(crowded))
    result = {'font':font.name,'glyphs':glyphs,'alpha_levels':len(levels),
              'min_digit_gap':min((gap(a,b) for a in digits for b in digits), default=None),
              'warnings':warnings,'errors':errors,'passed':not errors}
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
    a.add_argument('--one-bit',action='store_true',help='fail on grey coverage (two-colour panels)')
    args = p.parse_args()
    if args.mode == 'compare':
        regions = json.loads(Path(args.regions).read_text()) if args.regions else None
        result = compare(args.reference,args.actual,args.out,args.scale,regions,args.mask)
    else:
        result = atlas(args.font,args.out,args.ink,args.one_bit)
    print(json.dumps(result,indent=2))
    return 1 if result.get('errors') else 0


if __name__ == '__main__':
    raise SystemExit(main())
