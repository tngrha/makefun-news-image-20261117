#!/usr/bin/env python3
"""Draw a 1024x1024 newspaper-front-page infographic of the world news of
Tuesday 17 November 2026 and write it to <MAKEFUN_OUTPUT_DIR>/entry.png.

PIL only, DejaVu fonts, no network, no randomness: the output is byte-identical
on every run.
"""
import os

from PIL import Image, ImageDraw, ImageFont

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

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading):
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


def centered(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


# ---- pictograms (flat, drawn in a 72x72 box at bx, by) ----

def icon_globe(d, bx, by):
    d.ellipse([bx + 8, by + 6, bx + 64, by + 62], outline=NAVY, width=4)
    d.ellipse([bx + 26, by + 6, bx + 46, by + 62], outline=NAVY, width=2)
    d.line([bx + 8, by + 34, bx + 64, by + 34], fill=NAVY, width=2)
    d.line([bx + 14, by + 18, bx + 58, by + 18], fill=NAVY, width=2)
    d.line([bx + 14, by + 50, bx + 58, by + 50], fill=NAVY, width=2)


def icon_ship(d, bx, by):
    d.polygon([(bx + 8, by + 34), (bx + 64, by + 34), (bx + 56, by + 52),
               (bx + 16, by + 52)], fill=NAVY)
    d.rectangle([bx + 26, by + 18, bx + 46, by + 34], fill=RED)
    d.line([bx + 36, by + 8, bx + 36, by + 18], fill=INK, width=3)
    for wx in (bx + 8, bx + 30, bx + 52):
        d.arc([wx, by + 56, wx + 14, by + 66], 0, 180, fill=SEA, width=3)


def icon_drone(d, bx, by):
    for cx, cy in ((bx + 14, by + 14), (bx + 58, by + 14),
                   (bx + 14, by + 54), (bx + 58, by + 54)):
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=INK, width=3)
    d.line([bx + 14, by + 14, bx + 58, by + 54], fill=INK, width=3)
    d.line([bx + 58, by + 14, bx + 14, by + 54], fill=INK, width=3)
    d.ellipse([bx + 28, by + 26, bx + 44, by + 42], fill=RED)


def icon_bank(d, bx, by):
    d.polygon([(bx + 6, by + 24), (bx + 36, by + 8), (bx + 66, by + 24)],
              fill=NAVY)
    for cx in (bx + 16, bx + 36, bx + 56):
        d.rectangle([cx - 4, by + 28, cx + 4, by + 54], fill=NAVY)
    d.rectangle([bx + 6, by + 54, bx + 66, by + 60], fill=NAVY)


def icon_rocket(d, bx, by):
    d.polygon([(bx + 36, by + 4), (bx + 48, by + 26), (bx + 24, by + 26)],
              fill=RED)
    d.rectangle([bx + 24, by + 26, bx + 48, by + 52], fill=NAVY)
    d.polygon([(bx + 24, by + 40), (bx + 12, by + 54), (bx + 24, by + 50)],
              fill=RED)
    d.polygon([(bx + 48, by + 40), (bx + 60, by + 54), (bx + 48, by + 50)],
              fill=RED)
    d.polygon([(bx + 30, by + 52), (bx + 42, by + 52), (bx + 36, by + 66)],
              fill=(232, 140, 40))


def icon_clipboard(d, bx, by):
    d.rectangle([bx + 14, by + 10, bx + 58, by + 62], outline=NAVY, width=4)
    d.rectangle([bx + 28, by + 4, bx + 44, by + 14], fill=NAVY)
    for i, yy in enumerate((by + 24, by + 34, by + 44)):
        d.line([bx + 22, yy, bx + 50, yy], fill=NAVY, width=3)
    d.line([bx + 20, by + 52, bx + 30, by + 60], fill=RED, width=4)
    d.line([bx + 30, by + 60, bx + 48, by + 38], fill=RED, width=4)


def icon_shield(d, bx, by):
    d.polygon([(bx + 36, by + 6), (bx + 62, by + 16), (bx + 62, by + 38),
               (bx + 36, by + 64), (bx + 10, by + 38), (bx + 10, by + 16)],
              outline=NAVY, width=4)
    d.line([bx + 36, by + 18, bx + 36, by + 50], fill=RED, width=4)
    d.line([bx + 26, by + 28, bx + 46, by + 28], fill=RED, width=4)


def icon_jet(d, bx, by):
    d.polygon([(bx + 6, by + 34), (bx + 30, by + 28), (bx + 62, by + 34),
               (bx + 30, by + 40)], fill=NAVY)
    d.polygon([(bx + 26, by + 30), (bx + 38, by + 14), (bx + 44, by + 30)],
              fill=NAVY)
    d.polygon([(bx + 26, by + 38), (bx + 38, by + 54), (bx + 44, by + 38)],
              fill=NAVY)
    d.polygon([(bx + 62, by + 34), (bx + 70, by + 30), (bx + 70, by + 38)],
              fill=RED)


TILES = [
    ("ASIA", "TRUMP ENDS ASIA TRIP IN CHINA",
     "Manila ASEAN stop and Thai trade pact; three-way talks with Xi and Putin.",
     icon_globe),
    ("MIDDLE EAST", "TANKERS HIT BY MINES IN HORMUZ",
     "IRGC: two oil tankers ablaze after mine strikes; third US carrier arrives.",
     icon_ship),
    ("MIDDLE EAST", "IRAN DRONES HIT US RADAR IN BAHRAIN",
     "Drones intercepted, no casualties; US officials say Tehran plots a 'dirty bomb'.",
     icon_drone),
    ("MARKETS", "JPMORGAN BLAMES BUG FOR OUTAGE",
     "Not a cyberattack, bank says; Nvidia reports first earnings since Huang exit.",
     icon_bank),
    ("WORLD", "VULCAN ROCKET FAILS, 40 SATELLITES LOST",
     "ULA rocket lost in flight; Amazon's 40 Leo internet satellites destroyed.",
     icon_rocket),
    ("WORLD", "PENTAGON FAILS AUDIT FOR 9TH YEAR",
     "$4.8 trillion in assets unverified, auditors say.",
     icon_clipboard),
    ("EUROPE", "UK SANCTIONS 8 ISRAELI FIRMS",
     "Over West Bank settlements; settlers killed a 72-year-old near Jericho.",
     icon_shield),
    ("ASIA", "JAPAN SCRAMBLES JETS ON RUSSIAN INCURSION",
     "Suspected Russian aircraft violate Japanese airspace.",
     icon_jet),
]

FOOTER_LINES = [
    "Depardieu pleads guilty in Paris; Netanyahu camp accused over election-day arrests.",
    "13 US babies born with congenital measles \u2014 the most since 1991.",
    "Houthis advance in Yemen; government forces retreat toward Aden.",
]


def draw_hero_scene(d):
    """Flat scene of the collapsed Kerch Bridge: sky, sea, deck, broken span."""
    x0, y0, x1, y1 = 12, 106, 1012, 280
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    # sun
    d.ellipse([x1 - 90, y0 + 12, x1 - 46, y0 + 56], fill=(240, 200, 90))
    # sea
    d.rectangle([x0, 240, x1, y1], fill=SEA)
    d.line([x0, 240, x1, 240], fill=(255, 255, 255), width=2)
    # bridge pylons
    for px in (150, 850):
        d.rectangle([px, 168, px + 12, 240], fill=DARK_STEEL)
    # intact deck, left and right of the gap
    d.rectangle([x0, 210, 430, 226], fill=STEEL)
    d.rectangle([620, 210, x1, 226], fill=STEEL)
    # deck posts
    for px in range(30, 430, 44):
        d.line([px, 196, px, 210], fill=DARK_STEEL, width=4)
    for px in range(640, 1000, 44):
        d.line([px, 196, px, 210], fill=DARK_STEEL, width=4)
    # broken span: the two deck ends sag down into the sea in a V
    d.line([430, 214, 505, 258], fill=DARK_STEEL, width=14)
    d.line([620, 214, 545, 258], fill=DARK_STEEL, width=14)
    d.rectangle([488, 252, 562, 266], fill=STEEL)
    # smoke over the gap
    for cx, cy, r in ((500, 166, 26), (530, 146, 32), (565, 168, 24),
                      (520, 126, 20)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SMOKE)
    # small flame at the break
    d.polygon([(505, 210), (525, 210), (515, 192)], fill=(232, 120, 40))
    # waves around the fallen span
    for wx in (440, 500, 560):
        d.arc([wx, 268, wx + 26, 278], 0, 180, fill=(255, 255, 255), width=3)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_mast = font(BOLD, 30)
    f_date = font(BOLD, 46)
    f_kicker = font(BOLD, 15)
    f_hero = font(BOLD, 34)
    f_hero_sum = font(REG, 17)
    f_tag = font(BOLD, 12)
    f_head = font(BOLD, 24)
    f_sum = font(REG, 15)
    f_foot = font(REG, 14)
    f_foot_b = font(BOLD, 14)

    # ---- masthead ----
    centered(d, W // 2, 8, "THE WORLD IN ONE PAGE", f_mast, INK)
    centered(d, W // 2, 44, "TUESDAY 17 NOVEMBER 2026", f_date, RED)
    d.line([12, 96, 1012, 96], fill=RULE, width=3)
    d.line([12, 101, 1012, 101], fill=RULE, width=1)

    # ---- hero panel ----
    draw_hero_scene(d)
    d.rectangle([12, 280, 1012, 436], outline=RULE, width=2)
    d.text((24, 288), "UKRAINE  \u2022  HERO STORY", font=f_kicker, fill=RED)
    hero_lines = wrap(d, "UKRAINE STRIKE BRINGS DOWN PART OF KERCH BRIDGE",
                      f_hero, 976)
    text_block(d, 24, 308, hero_lines, f_hero, INK, 39)
    hero_sum = wrap(
        d,
        "Road span collapses after Kyiv's \u201cunprecedented operation\u201d; "
        "Russia hits Kyiv's Dnipro bridges, cutting heat, water and power.",
        f_hero_sum, 976)
    text_block(d, 24, 388, hero_sum, f_hero_sum, (40, 40, 40), 21)

    # ---- grid of 8 story tiles ----
    gx, gy = 12, 444
    tw, th, gap = 494, 118, 12
    for i, (tag, headline, summary, icon) in enumerate(TILES):
        col, row = i % 2, i // 2
        x = gx + col * (tw + gap)
        y = gy + row * (th + 8)
        d.rectangle([x, y, x + tw, y + th], fill=WHITE, outline=RULE, width=1)
        d.rectangle([x + 10, y + 34, x + 82, y + 106], fill=ICON_BG)
        icon(d, x + 10, y + 34)
        d.text((x + 94, y + 8), tag, font=f_tag, fill=RED)
        tx = x + 94
        tw_text = tw - 104
        head_lines = wrap(d, headline, f_head, tw_text)[:2]
        text_block(d, tx, y + 26, head_lines, f_head, INK, 27)
        sum_lines = wrap(d, summary, f_sum, tw_text)[:2]
        text_block(d, tx, y + 82, sum_lines, f_sum, (40, 40, 40), 18)

    # ---- footer: also in brief ----
    fy = 948
    d.line([12, fy, 1012, fy], fill=RULE, width=2)
    d.text((12, fy + 6), "ALSO IN BRIEF", font=f_foot_b, fill=RED)
    date_w = d.textlength("17 NOVEMBER 2026", font=f_foot_b)
    d.text((1012 - date_w, fy + 6), "17 NOVEMBER 2026", font=f_foot_b,
           fill=INK)
    for i, line in enumerate(FOOTER_LINES):
        d.text((12, fy + 24 + i * 16), "\u2022  " + line, font=f_foot,
               fill=INK)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "entry.png"), "PNG")


if __name__ == "__main__":
    main()
