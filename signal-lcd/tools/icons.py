"""Data and status pictograms drawn on an 11-pixel grid.

The data symbols follow the public Garmin manual pictograms listed in the
README, redrawn as original pixel art. MIP screens show these masks exactly;
grayscale screens trace the same masks into smooth outlines (see `smooth`).
Every diagonal is a 45-degree stair, every corner pixel of a box is cut,
so the 1-bit masks read as rounded shapes rather than jagged ones.
"""
from functools import lru_cache

from PIL import Image, ImageFilter

# Field symbols b..k, then face status symbols l..s.
PIXELS = {
    # heart
    "b": """
        .###...###.
        #####.#####
        ###########
        ###########
        ###########
        .#########.
        ..#######..
        ...#####...
        ....###....
        .....#.....
    """,
    # battery, three quarters
    "c": """
        .########..
        #........#.
        #.#####..##
        #.#####..##
        #.#####..##
        #........#.
        .########..
    """,
    # steps: two footprints
    "d": """
        ......##.
        .....####
        .##..####
        ####.####
        ####.####
        ####..##.
        ####.....
        .##..###.
        .....###.
        .###.....
        .###.....
    """,
    # calories: flame
    "e": """
        ....#....
        ...##....
        ...###...
        ..####...
        ..#####.#
        .#######.
        ##########
        ####.####
        ###...###
        .##...##.
        ..#####..
    """,
    # distance: dimension line between two stops
    "f": """
        #.........#
        #..#...#..#
        #.#.....#.#
        ###########
        #.#.....#.#
        #..#...#..#
        #.........#
    """,
    # temperature: thermometer
    "g": """
        ..###..
        ..#.#..
        ..#.#..
        ..#.#..
        ..###..
        ..###..
        .#####.
        #######
        #######
        #######
        .#####.
    """,
    # notifications: speech bubble
    "h": """
        .#########.
        ###########
        ###########
        ##.##.##.##
        ###########
        ###########
        .#########.
        ..##.......
        ..#........
    """,
    # elevation: two peaks
    "i": """
        ....#......
        ...###.....
        ..#####.#..
        .#########.
        ###########
        ###########
        ###########
    """,
    # floors: staircase
    "j": """
        ......####
        ......####
        ......####
        ...#######
        ...#######
        ...#######
        ##########
        ##########
        ##########
    """,
    # seconds: stopwatch
    "k": """
        ...###...
        ....#....
        ..#####..
        .##...##.
        ##..#..##
        ##..#..##
        ##..##.##
        ##.....##
        .##...##.
        ..#####..
    """,
    # alarm: bell
    "l": """
        ....#....
        ..#####..
        .#######.
        .#######.
        .#######.
        .#######.
        #########
        #########
        .........
        ...###...
    """,
    # phone connected: Bluetooth rune (a phone outline reads as a 0 beside the time)
    "m": """
        ...#...
        ...##..
        .#.#.#.
        ..##..#
        ...#.#.
        ...##..
        ...#.#.
        ..##..#
        .#.#.#.
        ...##..
        ...#...
    """,
    # tones off: speaker and cross
    "n": """
        ...#.......
        ..##.......
        ####.#...#.
        ####..#.#..
        ####...#...
        ####..#.#..
        ####.#...#.
        ..##.......
        ...#.......
    """,
    # do not disturb: crescent moon
    "o": """
        ..####...
        .###.....
        ###......
        ###......
        ###......
        ###......
        .###....#
        ..#######
        ...####..
    """,
    # battery low
    "p": """
        .########..
        #........#.
        #.##.....##
        #.##.....##
        #.##.....##
        #........#.
        .########..
    """,
    # vibration off: buzzing phone and cross, like tones off
    "q": """
        ..#####......
        ..#...#......
        #.#...#.#...#
        #.#...#..#.#.
        ..#...#...#..
        #.#...#..#.#.
        #.#...#.#...#
        ..#...#......
        ..#####......
    """,
    # phone disconnected: Bluetooth rune and cross, like tones off
    "r": """
        ...#.........
        ...##........
        .#.#.#.......
        ..##..#.#...#
        ...#.#...#.#.
        ...##.....#..
        ...#.#...#.#.
        ..##..#.#...#
        .#.#.#.......
        ...##........
        ...#.........
    """,
    # Tide Grid only: next high tide, next low tide, weekday calendar.
    "H": """
        ....#....
        ...###...
        ..#####..
        ....#....
        ....#....
        .........
        .##...##.
        #..###..#
        .........
        #########
    """,
    "L": """
        ....#....
        ....#....
        ..#####..
        ...###...
        ....#....
        .........
        .##...##.
        #..###..#
        .........
        #########
    """,
    "W": """
        .#.....#.
        #########
        #########
        #.......#
        #.#.#.#.#
        #.......#
        #.#.#.#.#
        #.......#
        #########
    """,
    # charging: lightning bolt
    "s": """
        ....###
        ...###.
        ..###..
        .###...
        #######
        ...###.
        ..###..
        .###...
        .##....
        .#.....
    """,
}
GRID = 11


@lru_cache(maxsize=None)
def mask(c):
    """The exact 1-bit master, trimmed to its ink."""
    rows = [line.strip() for line in PIXELS[c].strip().splitlines()]
    width = max(len(row) for row in rows)
    image = Image.new("L", (width, len(rows)))
    for y, row in enumerate(rows):
        for x, bit in enumerate(row):
            if bit == "#":
                image.putpixel((x, y), 255)
    return image.crop(image.getbbox())


@lru_cache(maxsize=None)
def smooth(c, height):
    """Trace the master into a smooth outline, then box-filter to `height`.

    The mask is magnified, softened by a fraction of one master pixel and cut
    at half coverage. Stairs become straight edges and cut corners become
    arcs, while one-pixel strokes survive. The result is area-sampled at the
    target size for grayscale displays.
    """
    master = mask(c)
    zoom = 16
    big = master.resize((master.width * zoom, master.height * zoom), Image.Resampling.NEAREST)
    pad = zoom
    canvas = Image.new("L", (big.width + 2 * pad, big.height + 2 * pad))
    canvas.paste(big, (pad, pad))
    # A third of a master pixel rounds corners and straightens stairs; the
    # cut just under half coverage keeps one-pixel diagonals continuous.
    traced = canvas.filter(ImageFilter.GaussianBlur(zoom * .34)).point(lambda v: 255 if v >= 104 else 0)
    traced = traced.crop((pad, pad, pad + big.width, pad + big.height))
    scale = height / GRID
    size = (max(1, round(master.width * scale)), max(1, round(master.height * scale)))
    return traced.resize(size, Image.Resampling.BOX)


def glyph(c, height, aa):
    """Symbol cell: master ink centred vertically in a `height` row."""
    ink = smooth(c, height) if aa else mask(c)
    cell = Image.new("L", (ink.width, max(height, ink.height)))
    cell.paste(ink, (0, (cell.height - ink.height) // 2))
    return cell
