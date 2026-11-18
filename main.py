#!/usr/bin/env python3
"""Draw a 1024x1024 newspaper-front-page infographic of the world news of
Tuesday 17 November 2026 and write it to <MAKEFUN_OUTPUT_DIR>/entry.png.

PURE Python 3.13 standard library only: no PIL, no font files, no network,
no randomness. The framebuffer is a bytearray, text is an embedded 5x7
bitmap font rendered in UPPERCASE, and the PNG is written by hand
(zlib-compressed scanlines). Output is byte-identical on every run, including
under `python3 -S -P -s` (no site-packages) on python:3.13-slim.
"""
import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 243, 232)
WHITE = (255, 255, 255)
INK = (18, 18, 18)
RED = (178, 34, 34)
NAVY = (31, 58, 95)
SKY = (188, 214, 232)
SEA = (46, 95, 138)
STEEL = (96, 104, 112)
DARK_STEEL = (70, 76, 84)
SMOKE = (120, 120, 118)
ICON_BG = (226, 232, 238)
RULE = (18, 18, 18)
BODY = (40, 40, 40)
SUN = (240, 200, 90)
FLAME = (232, 120, 40)

fb = bytearray(W * H * 3)


# ---------------------------------------------------------------- framebuffer

def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        fb[i] = color[0]
        fb[i + 1] = color[1]
        fb[i + 2] = color[2]


def fill_rect(x, y, w, h, color):
    if w <= 0 or h <= 0:
        return
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    row = bytes(color) * (x1 - x0)
    n = len(row)
    for yy in range(y0, y1):
        s = (yy * W + x0) * 3
        fb[s:s + n] = row


def rect_outline(x, y, w, h, color, width=1):
    fill_rect(x, y, w, width, color)
    fill_rect(x, y + h - width, w, width, color)
    fill_rect(x, y, width, h, color)
    fill_rect(x + w - width, y, width, h, color)


def draw_line(x0, y0, x1, y1, color, width=1):
    """Bresenham line; width>1 stamps width x width squares along it."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    half = width // 2
    while True:
        if width == 1:
            set_px(x0, y0, color)
        else:
            fill_rect(x0 - half, y0 - half, width, width, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def fill_circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def draw_circle(cx, cy, r, color, width=1):
    x, y, d = 0, r, 1 - r
    half = width // 2
    while x <= y:
        for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                       (cx + x, cy - y), (cx - x, cy - y),
                       (cx + y, cy + x), (cx - y, cy + x),
                       (cx + y, cy - x), (cx - y, cy - x)):
            if width == 1:
                set_px(px, py, color)
            else:
                fill_rect(px - half, py - half, width, width, color)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1


def fill_ellipse(cx, cy, rx, ry, color):
    for dy in range(-ry, ry + 1):
        t = 1.0 - (dy * dy) / float(ry * ry)
        dx = int(rx * (t ** 0.5)) if t > 0 else 0
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def draw_ellipse(cx, cy, rx, ry, color, width=1):
    # Parametric outline, sampled densely enough that stamps overlap.
    steps = max(24, int(3.14159 * (rx + ry)))
    prev = None
    for i in range(steps + 1):
        a = 2 * math.pi * i / steps
        px = int(round(cx + rx * math.cos(a)))
        py = int(round(cy + ry * math.sin(a)))
        if prev is not None:
            draw_line(prev[0], prev[1], px, py, color, width)
        prev = (px, py)


def fill_polygon(points, color):
    ys = [p[1] for p in points]
    ymin, ymax = min(ys), max(ys)
    n = len(points)
    for y in range(ymin, ymax + 1):
        xs = []
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            xa = int(xs[i] + 0.5)
            xb = int(xs[i + 1] + 0.5)
            fill_rect(xa, y, xb - xa + 1, 1, color)


def draw_polygon(points, color, width=1):
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        draw_line(x0, y0, x1, y1, color, width)


def draw_arc(x0, y0, x1, y1, color, width=1):
    """Upper half of the ellipse in the box (x0,y0)-(x1,y1): a wave crest."""
    cx = (x0 + x1) / 2.0
    cy = y1
    rx = (x1 - x0) / 2.0
    ry = (y1 - y0)
    prev = None
    for deg in range(0, 181, 5):
        a = deg * math.pi / 180.0
        px = int(round(cx + rx * math.cos(a)))
        py = int(round(cy - ry * math.sin(a)))
        if prev is not None:
            draw_line(prev[0], prev[1], px, py, color, width)
        prev = (px, py)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 cells; '1' is ink, '0' is blank.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ";": ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "\u2013": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "\u00d7": ("00000", "10001", "01010", "00100", "01010", "10001", "00000"),
    "\u2022": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

_BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")
# Curly quotes become straight ones; everything renders UPPERCASE.
_NORMALIZE = {"\u201c": '"', "\u201d": '"', "\u2019": "'", "\u2018": "'"}


def _clean(text):
    return "".join(_NORMALIZE.get(ch, ch) for ch in text).upper()


def _adv(scale):
    return 5 * scale + max(1, scale // 2)


def text_width(text, scale):
    return len(_clean(text)) * _adv(scale)


def draw_text(x, y, text, scale, color):
    ax = x
    adv = _adv(scale)
    for ch in _clean(text):
        glyph = FONT.get(ch, _BLANK)
        for r, row in enumerate(glyph):
            for c, bit in enumerate(row):
                if bit == "1":
                    fill_rect(ax + c * scale, y + r * scale,
                              scale, scale, color)
        ax += adv
    return ax


def draw_text_centered(cx, y, text, scale, color):
    draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap(text, scale, max_w):
    """Greedy word wrap; returns lines that fit max_w pixels."""
    adv = _adv(scale)
    lines, cur = [], ""
    for word in _clean(text).split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) * adv <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(x, y, lines, scale, color, leading):
    for i, line in enumerate(lines):
        draw_text(x, y + i * leading, line, scale, color)
    return y + len(lines) * leading

# ---------------------------------------------------------------- pictograms
# Flat icons drawn in a 72x72 box at (bx, by), same designs as before.

def icon_globe(bx, by):
    draw_circle(bx + 36, by + 34, 28, NAVY, 4)
    draw_ellipse(bx + 36, by + 34, 10, 28, NAVY, 2)
    draw_line(bx + 8, by + 34, bx + 64, by + 34, NAVY, 2)
    draw_line(bx + 14, by + 18, bx + 58, by + 18, NAVY, 2)
    draw_line(bx + 14, by + 50, bx + 58, by + 50, NAVY, 2)


def icon_ship(bx, by):
    fill_polygon([(bx + 8, by + 34), (bx + 64, by + 34),
                  (bx + 56, by + 52), (bx + 16, by + 52)], NAVY)
    fill_rect(bx + 26, by + 18, 20, 16, RED)
    draw_line(bx + 36, by + 8, bx + 36, by + 18, INK, 3)
    for wx in (bx + 8, bx + 30, bx + 52):
        draw_arc(wx, by + 56, wx + 14, by + 66, SEA, 3)


def icon_drone(bx, by):
    for cx, cy in ((bx + 14, by + 14), (bx + 58, by + 14),
                   (bx + 14, by + 54), (bx + 58, by + 54)):
        draw_circle(cx, cy, 9, INK, 3)
    draw_line(bx + 14, by + 14, bx + 58, by + 54, INK, 3)
    draw_line(bx + 58, by + 14, bx + 14, by + 54, INK, 3)
    fill_circle(bx + 36, by + 34, 8, RED)


def icon_bank(bx, by):
    fill_polygon([(bx + 6, by + 24), (bx + 36, by + 8),
                  (bx + 66, by + 24)], NAVY)
    for cx in (bx + 16, bx + 36, bx + 56):
        fill_rect(cx - 4, by + 28, 8, 26, NAVY)
    fill_rect(bx + 6, by + 54, 60, 6, NAVY)


def icon_rocket(bx, by):
    fill_polygon([(bx + 36, by + 4), (bx + 48, by + 26),
                  (bx + 24, by + 26)], RED)
    fill_rect(bx + 24, by + 26, 24, 26, NAVY)
    fill_polygon([(bx + 24, by + 40), (bx + 12, by + 54),
                  (bx + 24, by + 50)], RED)
    fill_polygon([(bx + 48, by + 40), (bx + 60, by + 54),
                  (bx + 48, by + 50)], RED)
    fill_polygon([(bx + 30, by + 52), (bx + 42, by + 52),
                  (bx + 36, by + 66)], FLAME)


def icon_clipboard(bx, by):
    rect_outline(bx + 14, by + 10, 44, 52, NAVY, 4)
    fill_rect(bx + 28, by + 4, 16, 10, NAVY)
    for yy in (by + 24, by + 34, by + 44):
        draw_line(bx + 22, yy, bx + 50, yy, NAVY, 3)
    draw_line(bx + 20, by + 52, bx + 30, by + 60, RED, 4)
    draw_line(bx + 30, by + 60, bx + 48, by + 38, RED, 4)


def icon_shield(bx, by):
    draw_polygon([(bx + 36, by + 6), (bx + 62, by + 16),
                  (bx + 62, by + 38), (bx + 36, by + 64),
                  (bx + 10, by + 38), (bx + 10, by + 16)], NAVY, 4)
    draw_line(bx + 36, by + 18, bx + 36, by + 50, RED, 4)
    draw_line(bx + 26, by + 28, bx + 46, by + 28, RED, 4)


def icon_jet(bx, by):
    fill_polygon([(bx + 6, by + 34), (bx + 30, by + 28),
                  (bx + 62, by + 34), (bx + 30, by + 40)], NAVY)
    fill_polygon([(bx + 26, by + 30), (bx + 38, by + 14),
                  (bx + 44, by + 30)], NAVY)
    fill_polygon([(bx + 26, by + 38), (bx + 38, by + 54),
                  (bx + 44, by + 38)], NAVY)
    fill_polygon([(bx + 62, by + 34), (bx + 70, by + 30),
                  (bx + 70, by + 38)], RED)


# ---------------------------------------------------------------- content
# Stories, headlines and footer text are unchanged from the PIL version,
# except tile summaries are shortened so each fits two lines at scale 3
# (the monospace bitmap font is wider than proportional DejaVu).

TILES = [
    ("ASIA", "TRUMP ENDS ASIA TRIP IN CHINA",
     "ASEAN stop, Thai pact; talks with Xi, Putin.",
     icon_globe),
    ("MIDDLE EAST", "TANKERS HIT BY MINES IN HORMUZ",
     "Mines hit two tankers; US carrier arrives.",
     icon_ship),
    ("MIDDLE EAST", "IRAN DRONES HIT US RADAR IN BAHRAIN",
     "Drones downed; Tehran plots a 'dirty bomb'.",
     icon_drone),
    ("MARKETS", "JPMORGAN BLAMES BUG FOR OUTAGE",
     "Bug, not attack: bank; Nvidia reports earnings.",
     icon_bank),
    ("WORLD", "VULCAN ROCKET FAILS, 40 SATELLITES LOST",
     "40 Amazon Leo satellites destroyed.",
     icon_rocket),
    ("WORLD", "PENTAGON FAILS AUDIT FOR 9TH YEAR",
     "$4.8T assets unverified, auditors say.",
     icon_clipboard),
    ("EUROPE", "UK SANCTIONS 8 ISRAELI FIRMS",
     "Over settlements; a 72-year-old killed.",
     icon_shield),
    ("ASIA", "JAPAN SCRAMBLES JETS ON RUSSIAN INCURSION",
     "Russian jets violate Japanese airspace.",
     icon_jet),
]

FOOTER_LINES = [
    "Depardieu pleads guilty in Paris; Netanyahu camp accused over election-day arrests.",
    "13 US babies born with congenital measles \u2014 the most since 1991.",
    "Houthis advance in Yemen; government forces retreat toward Aden.",
]

HERO_HEADLINE = "UKRAINE STRIKE BRINGS DOWN PART OF KERCH BRIDGE"
HERO_SUMMARY = (
    "Road span collapses after Kyiv's \u201cunprecedented operation\u201d; "
    "Russia hits Kyiv's Dnipro bridges, cutting heat, water and power.")


def draw_hero_scene():
    """Flat scene of the collapsed Kerch Bridge: sky, sea, deck, broken span."""
    x0, y0, x1, y1 = 12, 100, 1012, 264
    fill_rect(x0, y0, x1 - x0, y1 - y0, SKY)
    # sun
    fill_circle(x1 - 68, y0 + 34, 22, SUN)
    # sea
    fill_rect(x0, 234, x1 - x0, y1 - 234, SEA)
    fill_rect(x0, 234, x1 - x0, 2, WHITE)
    # bridge pylons
    for px in (150, 850):
        fill_rect(px, 162, 12, 72, DARK_STEEL)
    # intact deck, left and right of the gap
    fill_rect(x0, 204, 430 - x0, 16, STEEL)
    fill_rect(620, 204, x1 - 620, 16, STEEL)
    # deck posts
    for px in range(30, 430, 44):
        fill_rect(px, 190, 4, 14, DARK_STEEL)
    for px in range(640, 1000, 44):
        fill_rect(px, 190, 4, 14, DARK_STEEL)
    # broken span: the two deck ends sag down into the sea in a V
    draw_line(430, 208, 505, 252, DARK_STEEL, 14)
    draw_line(620, 208, 545, 252, DARK_STEEL, 14)
    fill_rect(488, 246, 74, 14, STEEL)
    # smoke over the gap
    for cx, cy, r in ((500, 160, 26), (530, 140, 32), (565, 162, 24),
                      (520, 120, 20)):
        fill_circle(cx, cy, r, SMOKE)
    # small flame at the break
    fill_polygon([(505, 204), (525, 204), (515, 186)], FLAME)
    # waves around the fallen span
    for wx in (440, 500, 560):
        draw_arc(wx, 256, wx + 26, 266, WHITE, 3)


# ---------------------------------------------------------------- PNG writer

def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += fb[y * W * 3:(y + 1) * W * 3]
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- page

def main():
    fill_rect(0, 0, W, H, PAPER)

    # ---- masthead ----
    draw_text_centered(W // 2, 6, "THE WORLD IN ONE PAGE", 4, INK)
    draw_text_centered(W // 2, 38, "TUESDAY 17 NOVEMBER 2026", 6, RED)
    fill_rect(12, 88, 1000, 3, RULE)
    fill_rect(12, 93, 1000, 1, RULE)

    # ---- hero panel ----
    draw_hero_scene()
    rect_outline(12, 264, 1000, 178, RULE, 2)
    draw_text(24, 272, "UKRAINE  \u2022  HERO STORY", 2, RED)
    hero_lines = wrap(HERO_HEADLINE, 5, 976)
    text_block(24, 292, hero_lines, 5, INK, 38)
    hero_sum = wrap(HERO_SUMMARY, 3, 976)
    text_block(24, 372, hero_sum, 3, BODY, 22)

    # ---- grid of 8 story tiles ----
    gx, gy = 12, 450
    tw, th, gap = 494, 118, 12
    for i, (tag, headline, summary, icon) in enumerate(TILES):
        col, row = i % 2, i // 2
        x = gx + col * (tw + gap)
        y = gy + row * (th + 8)
        fill_rect(x, y, tw, th, WHITE)
        rect_outline(x, y, tw, th, RULE, 1)
        fill_rect(x + 10, y + 34, 72, 72, ICON_BG)
        icon(x + 10, y + 34)
        draw_text(x + 94, y + 6, tag, 2, RED)
        head_lines = wrap(headline, 3, tw - 104)[:2]
        text_block(x + 94, y + 22, head_lines, 3, INK, 23)
        sum_lines = wrap(summary, 3, tw - 104)[:2]
        text_block(x + 94, y + 72, sum_lines, 3, BODY, 21)

    # ---- footer: also in brief ----
    fy = 952
    fill_rect(12, fy, 1000, 2, RULE)
    draw_text(12, fy + 6, "ALSO IN BRIEF", 2, RED)
    date_w = text_width("17 NOVEMBER 2026", 2)
    draw_text(1012 - date_w, fy + 6, "17 NOVEMBER 2026", 2, INK)
    for i, line in enumerate(FOOTER_LINES):
        draw_text(12, fy + 24 + i * 16, "\u2022  " + line, 2, INK)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
