"""Grid-native stroke glyphs for 1-bit MIP displays.

A 1-bit panel cannot anti-alias, so smoothness has to come from the glyph
construction itself: integer stroke widths, stems on whole pixels, symmetric
corner cuts and regular stair-steps on every diagonal. Nothing here goes
through FreeType, so the output is identical on every Pillow version.

Coordinates are pixel centres: pixel (x, y) is lit when its centre lies within
half a stroke width of the skeleton.
"""
from functools import lru_cache
import math
from PIL import Image


class Grid:
    def __init__(self, w, h):
        self.w, self.h = max(1, w), max(1, h)
        self.rows = [bytearray(self.w) for _ in range(self.h)]

    def dot(self, x, y, on=1):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.rows[y][x] = on

    def rect(self, x0, y0, x1, y1, on=1):
        for y in range(max(0, y0), min(self.h - 1, y1) + 1):
            for x in range(max(0, x0), min(self.w - 1, x1) + 1):
                self.rows[y][x] = on

    def hline(self, y, x0, x1, t=1):
        self.rect(min(x0, x1), y, max(x0, x1), y + t - 1)

    def vline(self, x, y0, y1, t=1):
        self.rect(x, min(y0, y1), x + t - 1, max(y0, y1))

    def slant(self, xa, ya, xb, yb, run=1):
        """Diagonal as shifted horizontal runs: constant width, even steps."""
        if ya > yb:
            xa, ya, xb, yb = xb, yb, xa, ya
        rows, cols, sign = yb - ya + 1, abs(xb - xa) + 1, (1 if xb >= xa else -1)
        for k in range(rows):
            first = xa + sign * (k * cols // rows)
            last = xa + sign * (((k + 1) * cols - 1) // rows)
            self.rect(min(first, last), ya + k, max(first, last) + run - 1, ya + k)

    def stroke(self, points, width, rho=0, closed=False):
        """Polyline with round joins of centre-line radius rho and round caps."""
        unique = []
        for p in points:
            # Degenerate boxes (one-pixel-wide glyphs) collapse neighbours.
            if not unique or tuple(p[:2]) != unique[-1][:2]:
                unique.append(tuple(p))
        if closed and len(unique) > 1 and unique[0][:2] == unique[-1][:2]:
            unique.pop()
        segments = _flatten(tuple(unique), rho, closed and len(unique) > 2)
        if not segments:
            return
        half = width / 2
        limit = half * half + 1e-9
        xs = [v for s in segments for v in (s[0], s[2])]
        ys = [v for s in segments for v in (s[1], s[3])]
        for y in range(max(0, math.floor(min(ys) - half)), min(self.h - 1, math.ceil(max(ys) + half)) + 1):
            row = self.rows[y]
            for x in range(max(0, math.floor(min(xs) - half)), min(self.w - 1, math.ceil(max(xs) + half)) + 1):
                if row[x]:
                    continue
                for x0, y0, x1, y1 in segments:
                    dx, dy = x1 - x0, y1 - y0
                    length = dx * dx + dy * dy
                    t = 0 if not length else min(1, max(0, ((x - x0) * dx + (y - y0) * dy) / length))
                    ex, ey = x - x0 - t * dx, y - y0 - t * dy
                    if ex * ex + ey * ey <= limit:
                        row[x] = 1
                        break

    def bolden(self):
        """Classic bitmap bold: thicken stems only, keep gaps between bars."""
        for row in self.rows:
            for x in range(self.w - 1, 0, -1):
                if row[x - 1]:
                    row[x] = 1

    def image(self):
        im = Image.new('L', (self.w, self.h))
        im.putdata([255 if v else 0 for row in self.rows for v in row])
        return im


@lru_cache(maxsize=4096)
def _flatten(points, rho, closed):
    n = len(points)
    if n == 1:
        x, y = points[0][:2]
        return ((x, y, x, y),)
    xy = [p[:2] for p in points]
    radius = [p[2] if len(p) > 2 else rho for p in points]
    chain = []
    for i in range(n):
        b = xy[i]
        if not closed and i in (0, n - 1):
            chain.append([b])
            continue
        a, c = xy[i - 1], xy[(i + 1) % n]
        la, lc = math.dist(a, b), math.dist(b, c)
        ua = ((a[0] - b[0]) / la, (a[1] - b[1]) / la)
        uc = ((c[0] - b[0]) / lc, (c[1] - b[1]) / lc)
        theta = math.acos(max(-1, min(1, ua[0] * uc[0] + ua[1] * uc[1])))
        r = radius[i]
        if r <= 0 or theta > math.pi - 1e-6 or theta < 1e-6:
            chain.append([b])
            continue
        # A neighbouring join shares the segment; an open end may be shorter
        # than the tangent length, in which case the arc is cut at the end.
        end_a = not closed and i - 1 == 0
        end_c = not closed and i + 1 == n - 1
        d = r / math.tan(theta / 2)
        d = min(d, la if end_a and la >= d else (d if end_a else la / 2), lc if end_c and lc >= d else (d if end_c else lc / 2))
        r = d * math.tan(theta / 2)
        bis = (ua[0] + uc[0], ua[1] + uc[1])
        norm = math.hypot(*bis)
        centre = (b[0] + bis[0] / norm * r / math.sin(theta / 2), b[1] + bis[1] / norm * r / math.sin(theta / 2))
        p = (b[0] + ua[0] * d, b[1] + ua[1] * d)
        q = (b[0] + uc[0] * d, b[1] + uc[1] * d)
        a0 = math.atan2(p[1] - centre[1], p[0] - centre[0])
        a1 = math.atan2(q[1] - centre[1], q[0] - centre[0])
        sweep = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        steps = max(4, math.ceil(abs(sweep) * r * 3))
        arc = [(centre[0] + r * math.cos(a0 + sweep * k / steps), centre[1] + r * math.sin(a0 + sweep * k / steps)) for k in range(steps + 1)]
        if end_a and la < d:
            arc = _clip(arc, a, ua)
        if end_c and lc < d:
            arc = _clip(arc[::-1], c, uc)[::-1]
        chain.append(arc)
    if not closed:
        # An end swallowed by its neighbour's arc is replaced by the cut arc.
        if n > 2 and math.dist(xy[0], xy[1]) < 1e-9 + _tangent(chain[1], xy[1]):
            chain[0] = []
        if n > 2 and math.dist(xy[-1], xy[-2]) < 1e-9 + _tangent(chain[-2][::-1], xy[-2]):
            chain[-1] = []
    flat = [pt for part in chain for pt in part]
    if closed:
        flat.append(flat[0])
    return tuple((flat[i][0], flat[i][1], flat[i + 1][0], flat[i + 1][1]) for i in range(len(flat) - 1))


def _tangent(arc, vertex):
    return math.dist(arc[0], vertex) if len(arc) > 1 else 0


def _clip(arc, end, outward):
    """Drop the part of an arc that lies beyond an open end of the path."""
    def beyond(pt):
        return (pt[0] - end[0]) * outward[0] + (pt[1] - end[1]) * outward[1]
    kept = []
    for i, pt in enumerate(arc):
        if beyond(pt) <= 1e-9:
            if not kept and i:
                prev, t0, t1 = arc[i - 1], beyond(arc[i - 1]), beyond(pt)
                t = t0 / (t0 - t1)
                kept.append((prev[0] + (pt[0] - prev[0]) * t, prev[1] + (pt[1] - prev[1]) * t))
            kept.append(pt)
    return kept or [arc[-1]]


def stroke_for(width, height, weight=0):
    """Whole-pixel stroke: relatively heavier at small sizes for legibility."""
    if width <= 3:
        return 1
    gain, bias = {0: (.10, .6), 1: (.125, .85), 2: (.085, .45)}[weight]
    stroke = max(1, round(height * gain + bias))
    if weight == 1:
        return min(stroke, max(1, (width - 1) // 2))
    return 1 if width <= 5 else min(stroke, max(1, (width - 2) // 2))


def radius_for(width, stroke):
    if stroke == 1:
        return 0 if width <= 3 else 2
    if stroke == 2:
        return 2 if width <= 7 else 3
    return max(stroke / 2 + 1, min(round(width * .27 * 2) / 2, (width - stroke) / 2))


TINY = dict(zip('0123456789', [
    ['111', '101', '101', '101', '111'], ['010', '110', '010', '010', '111'],
    ['111', '001', '111', '100', '111'], ['111', '001', '111', '001', '111'],
    ['101', '101', '111', '001', '001'], ['111', '100', '111', '001', '111'],
    ['111', '100', '111', '101', '111'], ['111', '001', '001', '001', '001'],
    ['111', '101', '111', '101', '111'], ['111', '101', '111', '001', '111'],
]))


def _tiny(char, width, height):
    """Three-column numerals: bars stay one row, only the stems stretch."""
    g = Grid(width, height)
    middle = (height - 1) // 2
    for y in range(height):
        source = 0 if y == 0 else (4 if y == height - 1 else (2 if y == middle else (1 if y < middle else 3)))
        for x in range(width):
            if TINY[char][source][min(2, x * 3 // width)] == '1':
                g.dot(x, y)
    return g


SEGMENTS = dict(zip('0123456789', ['abcdef', 'bc', 'abged', 'abgcd', 'fgbc', 'afgcd', 'afgedc', 'abc', 'abcdefg', 'abcdfg']))
DOTS = dict(zip('0123456789', [
    ['01110', '10001', '10001', '10001', '10001', '10001', '01110'], ['00100', '01100', '00100', '00100', '00100', '00100', '01110'],
    ['01110', '10001', '00001', '00110', '01000', '10000', '11111'], ['11110', '00001', '00001', '01110', '00001', '00001', '11110'],
    ['00010', '00110', '01010', '10010', '11111', '00010', '00010'], ['11111', '10000', '11110', '00001', '00001', '10001', '01110'],
    ['00110', '01000', '10000', '11110', '10001', '10001', '01110'], ['11111', '00001', '00010', '00100', '01000', '01000', '01000'],
    ['01110', '10001', '10001', '01110', '10001', '10001', '01110'], ['01110', '10001', '10001', '01111', '00001', '00010', '01100'],
]))


def _segment(char, width, height, s):
    """Seven-segment LCD numerals: hexagonal segments with a clean diagonal gap."""
    g = Grid(width, height)
    a = (s - 1) / 2
    gap = 1 if s < 5 else 2
    xl, xr = a, width - 1 - a
    yt, yb = a, height - 1 - a
    ym = (height - 1) / 2
    def horizontal(yc):
        for y in range(height):
            d = abs(y - yc)
            if d > a + 1e-9:
                continue
            g.rect(math.ceil(xl + gap + d), y, math.floor(xr - gap - d), y)
    def vertical(xc, y0, y1):
        for x in range(width):
            d = abs(x - xc)
            if d > a + 1e-9:
                continue
            g.rect(x, math.ceil(y0 + gap + d), x, math.floor(y1 - gap - d))
    parts = {'a': lambda: horizontal(yt), 'g': lambda: horizontal(ym), 'd': lambda: horizontal(yb),
             'f': lambda: vertical(xl, yt, ym), 'b': lambda: vertical(xr, yt, ym),
             'e': lambda: vertical(xl, ym, yb), 'c': lambda: vertical(xr, ym, yb)}
    for key in SEGMENTS[char]:
        parts[key]()
    return g


def _dots(char, width, height):
    """5 x 7 dot-matrix numerals: one rectangular LED dot per cell."""
    g = Grid(width, height)
    cw, ch = width / 5, height / 7
    gap = 1 if min(cw, ch) < 5 else 2
    for row, bits in enumerate(DOTS[char]):
        for col, bit in enumerate(bits):
            if bit == '1':
                x0, y0 = round(col * cw), round(row * ch)
                x1, y1 = round((col + 1) * cw) - 1 - gap, round((row + 1) * ch) - 1 - gap
                g.rect(x0, y0, max(x0, x1), max(y0, y1))
    return g


@lru_cache(maxsize=8192)
def digit(char, width, height, weight=0, stroke=None, style='round', grid_type=Grid):
    """Continuous instrument numerals built from horizontal and vertical strokes.

    style: 'round' (default), 'square' (sharp corners), 'segment' (seven-segment
    LCD) or 'dot' (5 x 7 dot matrix). All are built on the pixel grid.
    A coverage grid can rasterize the same paths above native resolution.
    """
    if width <= 3 or height <= 5:
        return _tiny(char, width, height).image()
    s = stroke or stroke_for(width, height, weight)
    if style == 'segment':
        # LCD segments are long and slim: about a tenth of the digit height,
        # whatever the stroke of the outline styles.
        return _segment(char, width, height, max(2, round(height * .095))).image()
    if style == 'dot' and width >= 5 and height >= 7:
        return _dots(char, width, height).image()
    a = (s - 1) / 2
    rho = 0 if style == 'square' else radius_for(width, s)
    l, r, t, b = a, width - 1 - a, a, height - 1 - a
    snap = lambda v: round(v - a) + a
    m = (height - 1) / 2 - (0 if (height - s) % 2 == 0 else .5)
    # Terminal hooks need open counter rows left over, otherwise 9 closes
    # into 8 and 2 into a second bowl.
    opening = (height - 3 * s) / 2
    hook = 0 if opening < (2.5 if s == 1 else 3) else (1 if height < 14 else max(2, round(height * .15)))
    g = grid_type(width, height)
    if char == '0':
        g.stroke([(l, t), (r, t), (r, b), (l, b)], s, rho, closed=True)
    elif char == '8':
        g.stroke([(l, t), (r, t), (r, m), (l, m)], s, rho, closed=True)
        g.stroke([(l, m), (r, m), (r, b), (l, b)], s, rho, closed=True)
    elif char == '1':
        stem = snap(l + (r - l) * .62)
        flag = max(1, min(round(width * .32), int(stem - a)))
        g.stroke([(stem, t), (stem, b)], s)
        g.stroke([(stem, t), (stem - flag, t + flag)], s)
    elif char == '2':
        g.stroke([(l, t + hook), (l, t), (r, t), (r, m), (l, m), (l, b, 0), (r, b)], s, rho)
    elif char == '3':
        g.stroke([(l, t + hook), (l, t), (r, t), (r, b), (l, b), (l, b - hook)], s, rho)
        g.stroke([(snap(l + (r - l) * (.45 if width > 5 else .3)), m), (r, m)], s)
    elif char == '4':
        bar = snap(t + (b - t) * .62)
        # A square elbow at small sizes: a rounded one reads as U or Y.
        g.stroke([(l, t), (l, bar), (r, bar)], s, 0 if s < 3 else rho)
        g.stroke([(r, t), (r, b)], s)
    elif char == '5':
        g.stroke([(r, t), (l, t, 0), (l, m, 0), (r, m), (r, b), (l, b), (l, b - hook)], s, rho)
    elif char == '6':
        g.stroke([(r, t + hook), (r, t), (l, t), (l, b), (r, b), (r, m), (l, m)], s, rho)
    elif char == '7':
        g.stroke([(l, t), (r, t)], s)
        foot = max(0, round((width - s) * .28))
        g.slant(width - s, s, foot, height - 1, s)
        if s >= 3:
            g.dot(width - 1, 0, 0)
    elif char == '9':
        g.stroke([(l, m), (r, m), (r, t), (l, t), (l, m)], s, rho, closed=False)
        g.stroke([(r, m), (r, b), (l, b), (l, b - hook)], s, rho)
    return g.image()


def _ring(g, x, y, size, stroke=1):
    if size <= 2:
        g.rect(x, y, x + size - 1, y + size - 1)
    elif size == 3:
        for dx, dy in ((1, 0), (0, 1), (2, 1), (1, 2)):
            g.dot(x + dx, y + dy)
    else:
        a = (stroke - 1) / 2
        g.stroke([(x + a, y + a), (x + size - 1 - a, y + a), (x + size - 1 - a, y + size - 1 - a), (x + a, y + size - 1 - a)],
                 stroke, 2 if stroke == 1 else 2.5, closed=True)


LATIN = set('kmifthPaCFSunMoTeWdrA%/°:.-')


@lru_cache(maxsize=8192)
def latin(char, width, height, stroke=1):
    """Unit and weekday letters on the same grid and stroke as the numerals."""
    g = Grid(width, height)
    # Keep the font's stroke wherever the letter still has room for its
    # counters; only genuinely cramped letters drop to a thinner stroke.
    if char in 'mMW':
        fit = (width - 2) // 3
    elif char in 'i:.-/%°':
        fit = width
    elif char in 'ftTFrk':
        fit = width // 2
    else:
        fit = (width - 1) // 2
    s = max(1, min(stroke, fit))
    a = (s - 1) / 2
    rho = 0 if width <= 3 else (2 if s == 1 else s + .5)
    l, r, t, b = a, width - 1 - a, a, height - 1 - a
    snap = lambda v: round(v - a) + a
    xh = min(height - 1, max(5, round(height * .72)))        # x-height in rows
    xt = height - xh + a
    c = snap((l + r) / 2)
    half = snap(t + (b - t) * .5)
    if char == 'k':
        g.stroke([(l, t), (l, b)], s)
        joint = round(xt - a + (xh - 1) * .55)
        reach = width - s - 1
        if reach >= 0:
            g.slant(width - s, round(xt - a), s, joint, s)
            g.slant(s, joint, width - s, height - 1, s)
    elif char in 'nh':
        g.stroke([(l, t if char == 'h' else xt), (l, b)], s)
        g.stroke([(l, xt), (r, xt), (r, b)], s, rho)
    elif char == 'm':
        g.stroke([(l, xt), (l, b)], s)
        g.stroke([(l, xt), (c, xt), (c, b)], s, rho)
        g.stroke([(c, xt), (r, xt), (r, b)], s, rho)
    elif char == 'u':
        g.stroke([(l, xt), (l, b), (r, b)], s, rho)
        g.stroke([(r, xt), (r, b)], s)
    elif char == 'i':
        g.stroke([(c, xt), (c, b)], s)
        g.stroke([(c, max(t, xt - s - 1))], s)
    elif char == 'f':
        stem = snap(l + (r - l) * .35) if width > 2 * s else l
        g.stroke([(r, t), (stem, t), (stem, b)], s, rho)
        g.stroke([(l, xt), (min(r, stem + s + (1 if width > 3 else 0)), xt)], s)
    elif char == 't':
        stem = snap(l + (r - l) * .35) if width > 2 * s else l
        g.stroke([(stem, max(t, xt - s - 1)), (stem, b), (r, b)], s, rho)
        g.stroke([(l, xt), (r, xt)], s)
    elif char == 'r':
        g.stroke([(l, xt), (l, b)], s)
        g.stroke([(l, xt + 1), (l, xt), (r, xt)], s, rho)
    elif char == 'o':
        g.stroke([(l, xt), (r, xt), (r, b), (l, b)], s, rho, closed=True)
    elif char == 'e':
        bar = snap(xt + (b - xt) * .5)
        g.stroke([(l, bar), (r, bar), (r, xt), (l, xt), (l, b), (r, b)], s, rho)
    elif char == 'd':
        g.stroke([(r, xt), (l, xt), (l, b), (r, b)], s, rho)
        g.stroke([(r, t), (r, b)], s)
    elif char == 'a':
        if xh >= 5 * s:
            bowl = snap(xt + (b - xt) * .5)
            g.stroke([(l, xt), (r, xt), (r, b)], s, rho)
            g.stroke([(r, bowl), (l, bowl), (l, b), (r, b)], s, rho)
        else:
            g.stroke([(r, xt), (l, xt), (l, b), (r, b)], s, rho)
            g.stroke([(r, xt), (r, b)], s)
    elif char == 'P':
        g.stroke([(l, t), (l, b)], s)
        g.stroke([(l, t), (r, t), (r, half), (l, half)], s, rho)
    elif char == 'F':
        g.stroke([(l, b), (l, t), (r, t)], s)
        g.stroke([(l, half), (max(l, r - 1), half)], s)
    elif char == 'T':
        g.stroke([(l, t), (r, t)], s)
        g.stroke([(c, t), (c, b)], s)
    elif char == 'C':
        hook = 1 if height >= 8 else 0
        g.stroke([(r, t + hook), (r, t), (l, t), (l, b), (r, b), (r, b - hook)], s, rho)
    elif char == 'S':
        hook = 1 if height >= 8 else 0
        g.stroke([(r, t + hook), (r, t), (l, t), (l, half), (r, half), (r, b), (l, b), (l, b - hook)], s, rho)
    elif char == 'A':
        g.stroke([(l, b), (l, t), (r, t), (r, b)], s, rho)
        g.stroke([(l, snap(t + (b - t) * .55)), (r, snap(t + (b - t) * .55))], s)
    elif char in 'MW':
        g.stroke([(l, t), (l, b)], s)
        g.stroke([(r, t), (r, b)], s)
        depth = max(1, min(height - s, round((width - 2 * s) / 2)))
        middle = (width - 1) / 2
        for k in range(depth + 1):
            y = k if char == 'M' else height - 1 - k
            for x in (s - 1 + k, width - s - k):
                if abs(x - middle) >= 0 and s - 1 <= x <= width - s:
                    g.rect(x, y, x + (s - 1 if x < middle else 0), y + s - 1 if char == 'M' else y)
                    if x > middle:
                        g.rect(x - (s - 1), y, x, y + s - 1 if char == 'M' else y)
            if s - 1 + k >= width - s - k:
                break
    elif char == '/':
        g.slant(width - s, 0, 0, height - 1, s)
    elif char == '%':
        q = (1 if width < 6 or height < 7 else 2) if width < 7 or height < 8 else max(3, min(round(height * .42), (width - 1) // 2))
        _ring(g, 0, 0, q, 1 if q < 7 else s)
        _ring(g, width - q, height - q, q, 1 if q < 7 else s)
        run = 1 if q < 7 else s
        if q <= 2:
            g.slant(width - 1, 0, 0, height - 1, 1)
        else:
            g.slant(width - run - (1 if q > 3 else 0), 0, 1 if q > 3 else 0, height - 1, run)
    elif char == '°':
        _ring(g, 0, 0, min(width, height), 1 if min(width, height) < 7 else 2)
    elif char in ':.':
        d = min(width, s)
        x = (width - d) / 2 + (d - 1) / 2
        x = math.floor((width - d) / 2) + (d - 1) / 2
        rows = [height - 1 - (d - 1) / 2] if char == '.' else [round(height * .3) - .5 + (d % 2) / 2, round(height * .72) - .5 + (d % 2) / 2]
        for y in rows:
            g.stroke([(x, min(height - 1 - (d - 1) / 2, y))], d)
    elif char == '-':
        thick = max(1, s - (1 if s > 2 else 0))
        top = (height - thick) // 2
        g.rect(0, top, width - 1, top + thick - 1)
    return g.image()


CAPS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')


@lru_cache(maxsize=8192)
def caps(char, width, height, stroke=1):
    """Full upper-case alphabet for label fonts, one construction for all sizes."""
    if char in 'ACFMPSTW':
        return latin(char, width, height, stroke)
    g = Grid(width, height)
    s = max(1, min(stroke, (width - 2) // 3 if char == 'N' else (width - 1) // 2 if char not in 'ILJ' else width))
    a = (s - 1) / 2
    rho = 0 if width <= 3 else (2 if s == 1 else s + .5)
    l, r, t, b = a, width - 1 - a, a, height - 1 - a
    snap = lambda v: round(v - a) + a
    m = snap(t + (b - t) * .5)
    c = snap((l + r) / 2)
    mid_row = round(m - a)
    if char == 'B':
        g.stroke([(l, t), (l, b)], s)
        g.stroke([(l, t), (r, t), (r, m), (l, m)], s, rho)
        g.stroke([(l, m), (r, m), (r, b), (l, b)], s, rho)
    elif char == 'D':
        g.stroke([(l, b), (l, t), (r, t, rho), (r, b, rho), (l, b)], s, 0)
    elif char == 'E':
        g.stroke([(r, t), (l, t), (l, b), (r, b)], s)
        g.stroke([(l, m), (max(l, r - 1), m)], s)
    elif char == 'G':
        hook = 1 if height >= 8 else 0
        g.stroke([(r, t + hook), (r, t), (l, t), (l, b), (r, b), (r, m), (c, m)], s, rho)
    elif char == 'H':
        g.stroke([(l, t), (l, b)], s)
        g.stroke([(r, t), (r, b)], s)
        g.stroke([(l, m), (r, m)], s)
    elif char == 'I':
        g.stroke([(c, t), (c, b)], s)
        if width >= 3 * s:
            g.stroke([(l, t), (r, t)], s)
            g.stroke([(l, b), (r, b)], s)
    elif char == 'J':
        g.stroke([(r, t), (r, b), (l, b), (l, b - max(1, height // 4))], s, rho)
    elif char == 'K':
        g.stroke([(l, t), (l, b)], s)
        if width - s > s:
            g.slant(width - s, 0, s, mid_row, s)
            g.slant(s, mid_row, width - s, height - 1, s)
    elif char == 'L':
        g.stroke([(l, t), (l, b), (r, b)], s)
    elif char == 'N':
        g.stroke([(l, t), (l, b)], s)
        g.stroke([(r, t), (r, b)], s)
        g.slant(s, 0, max(s, width - 2 * s), height - 1, s)
    elif char == 'O':
        g.stroke([(l, t), (r, t), (r, b), (l, b)], s, rho, closed=True)
    elif char == 'Q':
        g.stroke([(l, t), (r, t), (r, b), (l, b)], s, rho, closed=True)
        tail = max(2, height // 4)
        g.slant(width - s - tail + 1, height - tail, width - s, height - 1, s)
    elif char == 'R':
        g.stroke([(l, t), (l, b)], s)
        g.stroke([(l, t), (r, t), (r, m), (l, m)], s, rho)
        g.slant(max(s, width - s - (height - 1 - mid_row - s) if width > 2 * s else s), min(height - 1, mid_row + s), width - s, height - 1, s)
    elif char == 'U':
        g.stroke([(l, t), (l, b), (r, b), (r, t)], s, rho)
    elif char == 'V':
        left = (width - s) // 2
        g.slant(0, 0, left, height - 1, s)
        g.slant(width - s, 0, width - s - left, height - 1, s)
    elif char == 'X':
        g.slant(0, 0, width - s, height - 1, s)
        g.slant(width - s, 0, 0, height - 1, s)
    elif char == 'Y':
        left = (width - s) // 2
        g.slant(0, 0, left, mid_row, s)
        g.slant(width - s, 0, width - s - left, mid_row, s)
        g.rect(left, mid_row, width - s - left + s - 1, height - 1)
    elif char == 'Z':
        g.stroke([(l, t), (r, t)], s)
        g.stroke([(l, b), (r, b)], s)
        if height > 2 * s:
            g.slant(width - s, s, 0, height - 1 - s, s)
    return g.image()


CJK = set('年月日周一二三四五六天上午下')


@lru_cache(maxsize=4096)
def cjk(char, width, height, bold=False):
    """Hand-structured Chinese date characters; bars and stems never collide."""
    if bold and width >= 7:
        g = _cjk(char, width - 1, height)
        wide = Grid(width, height)
        for y, row in enumerate(g.rows):
            wide.rows[y][:len(row)] = row
        wide.bolden()
        return wide.image()
    return _cjk(char, width, height).image()


def _cjk(char, W, H):
    g = Grid(W, H)
    fx = lambda p: round(p * (W - 1))
    fy = lambda p: round(p * (H - 1))
    R, B, c = W - 1, H - 1, (W - 1) // 2

    def legs(y, left, right):
        """Paired sweeping strokes from row y down to both bottom corners."""
        rows = B - y + 1
        if rows <= 0:
            return
        g.slant(left, y, 0, B)
        g.slant(right, y, R, B)

    def sweep(x, y):
        """Lower end of a left-falling stroke: a short, even stair."""
        steps = min(x, B - y)
        for k in range(1, steps + 1):
            g.dot(x - k, y + k)

    if char == '一':
        g.hline(B // 2, 0, R)
    elif char == '二':
        g.hline(fy(.2), fx(.16), R - fx(.16))
        g.hline(fy(.84), 0, R)
    elif char == '三':
        g.hline(fy(.1), fx(.12), R - fx(.12))
        g.hline(B // 2, fx(.2), R - fx(.2))
        g.hline(B, 0, R)
    elif char == '日':
        xl = fx(.17)
        xr = R - xl
        g.vline(xl, 0, B)
        g.vline(xr, 0, B)
        for y in (0, B // 2, B):
            g.hline(y, xl, xr)
    elif char == '月':
        xl, xr = fx(.2), R - fx(.14)
        g.hline(0, xl, xr)
        g.vline(xr, 0, B)
        g.dot(xr - 1, B)
        stem = fy(.8)
        g.vline(xl, 0, stem)
        sweep(xl, stem)
        for y in (fy(.3), fy(.58)):
            g.hline(y, xl, xr)
    elif char == '四':
        top, bottom = (0, B) if H <= 9 else (fy(.08), fy(.92))
        g.vline(0, top, bottom)
        g.vline(R, top, bottom)
        g.hline(top, 0, R)
        g.hline(bottom, 0, R)
        xa, xb = fx(.34), R - fx(.34)
        knee = top + round((bottom - top) * .52)
        g.vline(xa, top, knee)
        g.vline(xb, top, knee)
        g.dot(xa - 1, knee + 1)
        g.hline(knee + 1, xb, R)
        if xa - 2 >= 1 and knee + 2 < bottom:
            g.dot(xa - 2, knee + 2)
    elif char == '五':
        inset = fx(.1)
        middle, xr, xm = fy(.44), fx(.78), fx(.42)
        g.hline(0, inset, R - inset)
        g.hline(middle, inset, max(xr, R - inset - 1))
        g.hline(B, 0, R)
        g.vline(xm, 0, middle)
        g.vline(max(inset, xm - 1) if W >= 7 else xm, middle, B)
        g.vline(xr, middle, B)
    elif char == '六':
        bar = fy(.3)
        g.vline(c, 0, bar)
        if W % 2 == 0:
            g.vline(c + 1, 0, bar)
        g.hline(bar, 0, R)
        start = min(B, bar + 2)
        reach = max(1, fx(.32))
        legs(start, reach, R - reach)
    elif char == '天':
        top, bar = (0, fy(.4)) if H <= 9 else (fy(.06), fy(.42))
        g.hline(top, fx(.14), R - fx(.14))
        g.hline(bar, 0, R)
        mid = [c] if W % 2 else [c, c + 1]
        spare = max(0, (B - bar) - c)
        for x in mid:
            g.vline(x, top, bar + spare)
        legs(bar + spare + 1, c - 1, (c + 1 if W % 2 else c + 2))
    elif char == '上':
        g.vline(c, 0, B)
        g.hline(fy(.42), c, R - fx(.12))
        g.hline(B, 0, R)
    elif char == '下':
        g.hline(0, 0, R)
        g.vline(c, 0, B)
        start = fy(.34)
        for k in range(max(2, round(W * .22))):
            g.dot(c + 1 + k, start + k)
    elif char == '午':
        x1, bar1, bar2 = fx(.2), max(1, fy(.16)), fy(.56)
        g.hline(bar1, x1, R - fx(.08))
        g.hline(bar2, 0, R)
        g.vline(c, bar1, B)
        for k in range(bar1):
            g.dot(x1 + 1, k)
        sweep(x1 + 1, bar1 - 1 if bar1 > 1 else 0)
        if bar1 == 1:
            g.dot(x1 + 1, 0)
            g.dot(max(0, x1 - 1), 2)
    elif char == '年':
        x1, bar1, bar3 = fx(.22), max(1, fy(.16)), fy(.74)
        bar2 = (bar1 + bar3) // 2
        stem = fx(.56)
        g.hline(bar1, x1, R - fx(.06))
        g.hline(bar2, x1, R - fx(.14))
        g.hline(bar3, 0, R)
        g.vline(x1, bar2, bar3)
        g.vline(stem, bar1, B)
        for k in range(bar1):
            g.dot(x1 + 1, k)
        if x1 >= 1:
            g.dot(x1 - 1, bar1 + 1)
    elif char == '周':
        xl, xr = max(1, fx(.1)), R
        g.hline(0, xl, xr)
        g.vline(xr, 0, B)
        g.dot(xr - 1, B)
        stem = fy(.74)
        g.vline(xl, 0, stem)
        sweep(xl, stem)
        i0, i1 = xl + 2, xr - 2
        ic = (i0 + i1) // 2
        if H >= 9:
            upper = 2
            lower = upper + 2
            g.vline(ic, 1, lower)
            g.hline(upper, i0, i1)
            g.hline(lower, i0, i1)
            box_top = lower + 2
            box_bottom = max(box_top + 1, min(B - 1, box_top + 3))
            g.vline(i0, box_top, box_bottom)
            g.vline(i1, box_top, box_bottom)
            g.hline(box_top, i0, i1)
            g.hline(box_bottom, i0, i1)
        else:
            g.vline(ic, 1, 3)
            g.hline(2, i0, i1)
            g.hline(min(B - 1, 5), i0, i1)
    return g
