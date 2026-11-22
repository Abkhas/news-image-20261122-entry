#!/usr/bin/env python3
"""Render the n22 news image (1024x1024) for make.fun news-image-20261122,
v3 -- the first build under the 3-gate doctrine (structure + eye + duel
as confirmation). Everything is drawn in code with PIL: no photos, no
network, no randomness -- repeated runs give identical bytes.

Layout (the "33-story family + chips" route, from the n19 paid-top-10
analysis and the n22 top-3 study):
  30 stories: 3 heroes + 12 grid cards + 15 ALSO ON lines.
  A verification-status chip on EVERY card and EVERY also-on line
  (CONFIRMED / CLAIM / REPORTED / PENDING) plus a one-line legend.
  Heroes 210px tall (>= 1/5 of the page); grid titles 20px bold, bodies
  14px, two lines max; stat digits 34px; map in its own clean band with
  zero overlap; DATE CHECK in a red border labelled READ THIS FIRST.
  No VERDICT / HOW SURE / MARKETS boxes (0/10 n19 paid winners had them).
  No UTC timeline strip (the 33-story family drops it).
Heroes keep the verified Sunday truth: COP31 COLLAPSED (the closing
plenary rejected the deal -- never framed as "deal lands"), Sparta II
still burning, 186 drones over Ukraine.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.environ.get("OUT", "entry.png")

# ------------------------------------------------------------------ palette
INK = (17, 33, 57)
INK2 = (9, 20, 38)
PAPER = (253, 249, 238)
CREAM = (244, 238, 222)
RED = (186, 32, 32)
GOLD = (214, 162, 42)
GREY = (92, 96, 104)
LINE = (203, 196, 178)
BODY = (40, 44, 52)

REGIONS = {
    "EUROPE": (31, 78, 121),
    "AMERICAS": (176, 92, 20),
    "MIDDLE EAST": (146, 110, 58),
    "ASIA": (46, 125, 80),
    "AFRICA": (178, 132, 30),
    "OCEANIA": (30, 130, 140),
    "WORLD": (90, 90, 105),
}
REGION_ORDER = ["EUROPE", "AMERICAS", "MIDDLE EAST", "ASIA",
                "AFRICA", "OCEANIA", "WORLD"]

# Verification-status chips: the device the n22 winners use and we lacked.
STATUS = {
    "CONFIRMED": (34, 120, 60),
    "REPORTED": (31, 78, 121),
    "CLAIM": (176, 92, 20),
    "PENDING": (110, 90, 140),
}

OVERFLOWS = []  # (where, text) -- the fit check must stay empty


def tint(rgb, frac=0.90):
    """Pale tint of a region colour, for card backgrounds."""
    return tuple(int(255 * frac + c * (1 - frac)) for c in rgb)


# ------------------------------------------------------------------ fonts
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def serif_b(size):
    return load_font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return load_font("DejaVuSerif.ttf", size)


def sans_b(size):
    return load_font("DejaVuSans-Bold.ttf", size)


def sans(size):
    return load_font("DejaVuSans.ttf", size)


# ------------------------------------------------------------------ text
def wrap_text(d, text, font, max_w):
    """Greedy word wrap; returns a list of lines that all fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(d, where, text, font, max_w, max_lines):
    """Wrap text to at most max_lines; truncate the last line with '...'
    and record the overflow (the build check requires zero of these)."""
    lines = wrap_text(d, text, font, max_w)
    if len(lines) > max_lines:
        OVERFLOWS.append((where, text))
        lines = lines[:max_lines]
        cut = lines[-1]
        while cut and d.textlength(cut + "...", font=font) > max_w:
            cut = cut[:-1]
        lines[-1] = cut + "..."
    return lines


def draw_lines(d, x, y, lines, font, fill, leading):
    for i, line in enumerate(lines):
        d.text((x, y + i * leading), line, font=font, fill=fill)


def disc(d, cx, cy, n, r=11, fill=RED, size=12):
    """Numbered disc, white number on a coloured circle."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    f = sans_b(size)
    label = str(n)
    tw = d.textlength(label, font=f)
    th = f.size
    d.text((cx - tw / 2, cy - th / 2 - 1), label, font=f,
           fill=(255, 255, 255))


def status_pill(d, x, y, status, size=13, height=17):
    """Verification-status chip: white pill, coloured outline and text.
    Returns the pill width."""
    colour = STATUS[status]
    f = sans_b(size)
    tw = d.textlength(status, font=f)
    w = int(tw + 14)
    d.rounded_rectangle([x, y, x + w, y + height], radius=4,
                        fill=(255, 255, 255), outline=colour, width=2)
    d.text((x + 7, y + (height - size) / 2 - 1), status, font=f, fill=colour)
    return w


def source_pill(d, x_right, y, name, size=13, height=17, max_w=120):
    """Source-name pill anchored at its right edge; returns its width,
    or None when the name does not fit at the minimum size (dropped,
    never shrunk -- a name in 9px type is unreadable at judge size)."""
    f = sans_b(size)
    tw = d.textlength(name, font=f)
    w = int(tw + 14)
    if w > max_w:
        return None
    d.rounded_rectangle([x_right - w, y, x_right, y + height], radius=4,
                        fill=(255, 255, 255), outline=LINE, width=1)
    d.text((x_right - w + 7, y + (height - size) / 2 - 1), name, font=f,
           fill=INK)
    return w


# ------------------------------------------------------------------ scenes
# Every scene is a small geometric drawing in its own box (d, x, y, w, h).
# Original compositions for this build; no photographs anywhere.

def _night_sky(d, x, y, w, h, top=(12, 24, 48), bot=(38, 60, 96)):
    for i in range(h):
        c = tuple(int(top[k] + (bot[k] - top[k]) * i / max(h - 1, 1))
                  for k in range(3))
        d.line([x, y + i, x + w, y + i], fill=c)
    for sx, sy in [(0.12, 0.15), (0.3, 0.08), (0.55, 0.2), (0.78, 0.1),
                   (0.9, 0.25), (0.45, 0.3), (0.66, 0.05)]:
        d.ellipse([x + w * sx - 1, y + h * sy - 1,
                   x + w * sx + 1, y + h * sy + 1], fill=(255, 255, 255))


def _sea(d, x, y, w, h, base=(24, 68, 110)):
    d.rectangle([x, y, x + w, y + h], fill=base)
    for i, frac in enumerate([0.25, 0.55, 0.85]):
        yy = y + int(h * frac)
        for k in range(4):
            x0 = x + 8 + k * (w // 4)
            aw, ah = int(w * 0.09), max(2, int(h * 0.16))
            d.arc([x0, yy - ah // 2, x0 + aw, yy + ah // 2], 180, 360,
                  fill=(190, 220, 240), width=2)


def scene_ship(d, x, y, w, h):
    """Sparta II burning at night off Finland."""
    _night_sky(d, x, y, w, h)
    _sea(d, x, y + int(h * 0.62), w, h - int(h * 0.62))
    hx, hy = x + int(w * 0.18), y + int(h * 0.52)
    hw, hh = int(w * 0.64), max(3, int(h * 0.14))
    d.rectangle([hx, hy, hx + hw, hy + hh], fill=(20, 22, 28))
    d.rectangle([hx + int(hw * 0.55), hy - max(3, int(h * 0.12)),
                 hx + int(hw * 0.8), hy], fill=(40, 44, 54))
    for fx, fwf, fhf in [(0.30, 0.05, 0.26), (0.45, 0.06, 0.34),
                         (0.62, 0.045, 0.22)]:
        bx = x + int(w * fx)
        fw, fh = int(w * fwf), int(h * fhf)
        d.polygon([(bx, hy), (bx + fw / 2, hy - fh), (bx + fw, hy)],
                  fill=(240, 120, 30))
        d.polygon([(bx + 3, hy), (bx + fw / 2, hy - fh * 0.55),
                   (bx + fw - 3, hy)], fill=(250, 200, 60))
    sd = max(6, int(h * 0.22))
    d.ellipse([x + int(w * 0.72), y + int(h * 0.08),
               x + int(w * 0.72) + sd, y + int(h * 0.08) + sd],
              fill=(120, 120, 130))


def scene_summit(d, x, y, w, h):
    """COP31 plenary table: flags, a long table, a broken ring (no deal)."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 72, 86))
    for fx, col in [(0.16, (200, 60, 60)), (0.30, (60, 120, 200)),
                    (0.44, (240, 200, 60))]:
        px = x + int(w * fx)
        d.line([px, y + int(h * 0.12), px, y + int(h * 0.5)],
               fill=(220, 220, 220), width=2)
        d.polygon([(px, y + int(h * 0.12)), (px + int(w * 0.055),
                                             y + int(h * 0.18)),
                   (px, y + int(h * 0.24))], fill=col)
    ty = y + int(h * 0.58)
    d.rectangle([x + 8, ty, x + w - 8, ty + max(3, int(h * 0.12))],
                fill=(120, 84, 50))
    d.rectangle([x + 8, ty + max(3, int(h * 0.12)), x + w - 8,
                 ty + max(5, int(h * 0.16))], fill=(90, 62, 36))
    cx, cy, r = x + int(w * 0.78), y + int(h * 0.32), max(5, int(h * 0.16))
    d.arc([cx - r, cy - r, cx + r, cy + r], 30, 300, fill=(255, 255, 255),
          width=3)
    d.line([cx - r // 2, cy + r - 1, cx + r // 2 + 2, cy - r + 1],
           fill=RED, width=max(2, int(h * 0.04)))


def scene_drones(d, x, y, w, h):
    """Night sky over Kyiv: drones, searchlights, a distant blast."""
    _night_sky(d, x, y, w, h)
    for bx, by in [(0.2, 0.55), (0.5, 0.72), (0.8, 0.6)]:
        x0, y0 = x + int(w * bx), y + int(h * by)
        d.polygon([(x0, y0), (x0 + int(w * 0.14), y0 + int(h * 0.3)),
                   (x0 + int(w * 0.07), y0 + int(h * 0.12))],
                  fill=(255, 240, 180))
    arm = max(3, int(h * 0.08))
    for dx, dy in [(0.25, 0.25), (0.55, 0.15), (0.8, 0.3)]:
        cx, cy = x + int(w * dx), y + int(h * dy)
        d.line([cx - arm, cy, cx + arm, cy], fill=(230, 230, 230), width=2)
        d.line([cx, cy - arm // 2, cx, cy + arm // 2],
               fill=(230, 230, 230), width=2)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
    d.rectangle([x, y + h - max(2, int(h * 0.06)), x + w, y + h],
                fill=(10, 14, 22))


def scene_blast(d, x, y, w, h):
    """Missile blast over a Gulf base at dusk."""
    d.rectangle([x, y, x + w, y + h], fill=(60, 30, 40))
    cx, cy = x + int(w * 0.5), y + int(h * 0.45)
    for rf, col in [(0.42, (240, 120, 30)), (0.3, (250, 180, 60)),
                    (0.17, (255, 230, 150))]:
        r = max(3, int(h * rf))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    for bx in [0.08, 0.3, 0.72, 0.88]:
        bw, bh = int(w * 0.1), int(h * 0.3)
        d.rectangle([x + int(w * bx), y + h - bh, x + int(w * bx) + bw,
                     y + h], fill=(20, 16, 20))
    sd = max(4, int(h * 0.2))
    d.ellipse([cx - int(w * 0.18), cy - int(h * 0.46),
               cx - int(w * 0.18) + sd, cy - int(h * 0.46) + sd],
              fill=(90, 80, 90))
    d.ellipse([cx + int(w * 0.07), cy - int(h * 0.52),
               cx + int(w * 0.07) + sd, cy - int(h * 0.52) + sd],
              fill=(90, 80, 90))


def scene_boat(d, x, y, w, h):
    """Capsized boat on a river: hull up, waves, a rescue ring."""
    d.rectangle([x, y, x + w, y + h], fill=(140, 190, 210))
    _sea(d, x, y + int(h * 0.5), w, h - int(h * 0.5), base=(30, 90, 130))
    hx, hy = x + int(w * 0.3), y + int(h * 0.42)
    hh = max(4, int(h * 0.45))
    d.polygon([(hx, hy), (hx + int(w * 0.4), hy),
               (hx + int(w * 0.32), hy + hh), (hx + int(w * 0.08), hy + hh)],
              fill=(120, 60, 30))
    rd = max(6, int(h * 0.5))
    d.ellipse([x + int(w * 0.72), y + int(h * 0.32) - rd // 2,
               x + int(w * 0.72) + rd, y + int(h * 0.32) + rd // 2],
              outline=RED, width=3)


def scene_factory(d, x, y, w, h):
    """Factory fire: sawtooth roof, chimney, flames and smoke."""
    d.rectangle([x, y, x + w, y + h], fill=(180, 170, 150))
    d.rectangle([x + int(w * 0.1), y + int(h * 0.55), x + int(w * 0.85),
                 y + h], fill=(70, 66, 60))
    for i in range(3):
        x0 = x + int(w * (0.12 + i * 0.24))
        d.polygon([(x0, y + int(h * 0.55)), (x0 + int(w * 0.06),
                                             y + int(h * 0.4)),
                   (x0 + int(w * 0.12), y + int(h * 0.55))],
                  fill=(70, 66, 60))
    d.rectangle([x + int(w * 0.8), y + int(h * 0.25), x + int(w * 0.88),
                 y + int(h * 0.55)], fill=(90, 84, 78))
    for fx, fwf, fhf in [(0.35, 0.06, 0.2), (0.55, 0.07, 0.26)]:
        bx = x + int(w * fx)
        fw, fh = int(w * fwf), int(h * fhf)
        d.polygon([(bx, y + int(h * 0.55)), (bx + fw / 2,
                                             y + int(h * 0.55) - fh),
                   (bx + fw, y + int(h * 0.55))], fill=(240, 120, 30))
    sd = max(5, int(h * 0.2))
    d.ellipse([x + int(w * 0.7), y + int(h * 0.04),
               x + int(w * 0.7) + sd, y + int(h * 0.04) + sd],
              fill=(110, 105, 100))


def scene_vaccine(d, x, y, w, h):
    """Vaccination drive: white cross, vials, a queue of dots."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 110, 90))
    cx, cy = x + int(w * 0.3), y + int(h * 0.5)
    arm, thick = max(5, int(h * 0.3)), max(2, int(h * 0.09))
    d.rectangle([cx - thick, cy - arm, cx + thick, cy + arm],
                fill=(255, 255, 255))
    d.rectangle([cx - arm, cy - thick, cx + arm, cy + thick],
                fill=(255, 255, 255))
    for i in range(3):
        vx = x + int(w * (0.6 + i * 0.12))
        d.rectangle([vx, y + int(h * 0.3), vx + max(3, int(w * 0.03)),
                     y + int(h * 0.7)], fill=(220, 240, 235),
                    outline=(255, 255, 255))
    for i in range(5):
        dx = x + 8 + i * max(6, int(w * 0.04))
        d.ellipse([dx, y + h - max(4, int(h * 0.1)),
                   dx + max(3, int(w * 0.02)), y + h - 4],
                  fill=(255, 255, 255))


def scene_ebola(d, x, y, w, h):
    """Outbreak ward: red ground, white cross, warning triangle."""
    d.rectangle([x, y, x + w, y + h], fill=(120, 30, 30))
    cx, cy = x + int(w * 0.32), y + int(h * 0.5)
    arm, thick = max(4, int(h * 0.25)), max(2, int(h * 0.07))
    d.rectangle([cx - thick, cy - arm, cx + thick, cy + arm],
                fill=(255, 255, 255))
    d.rectangle([cx - arm, cy - thick, cx + arm, cy + thick],
                fill=(255, 255, 255))
    tx, ty = x + int(w * 0.72), y + int(h * 0.5)
    th = max(5, int(h * 0.27))
    d.polygon([(tx, ty - th), (tx + th, ty + th), (tx - th, ty + th)],
              outline=(255, 220, 80), width=3)
    d.text((tx - 2, ty - max(4, int(h * 0.14))), "!",
           font=sans_b(max(8, int(h * 0.35))), fill=(255, 220, 80))


def scene_race(d, x, y, w, h):
    """Las Vegas night race: track, a low car, a chequered flag."""
    d.rectangle([x, y, x + w, y + h], fill=(14, 16, 34))
    d.rectangle([x, y + int(h * 0.62), x + w, y + int(h * 0.7)],
                fill=(50, 50, 60))
    d.line([x, y + int(h * 0.66), x + w, y + int(h * 0.66)],
           fill=(255, 220, 80), width=2)
    cx, cy = x + int(w * 0.42), y + int(h * 0.5)
    cw, chh = int(w * 0.3), max(3, int(h * 0.1))
    d.rectangle([cx, cy, cx + cw, cy + chh], fill=(220, 40, 40))
    wd = max(3, int(w * 0.04))
    d.ellipse([cx + 4, cy + chh, cx + 4 + wd, cy + chh + wd],
              fill=(10, 10, 10))
    d.ellipse([cx + cw - 4 - wd, cy + chh, cx + cw - 4, cy + chh + wd],
              fill=(10, 10, 10))
    fx, fy = x + int(w * 0.82), y + int(h * 0.08)
    sq = max(2, int(h * 0.05))
    for r in range(3):
        for c in range(3):
            if (r + c) % 2 == 0:
                d.rectangle([fx + c * sq, fy + r * sq, fx + c * sq + sq,
                             fy + r * sq + sq], fill=(255, 255, 255))


def scene_rugby(d, x, y, w, h):
    """Rugby pitch: green, white lines, posts, an oval ball."""
    d.rectangle([x, y, x + w, y + h], fill=(40, 130, 60))
    d.line([x, y + int(h * 0.5), x + w, y + int(h * 0.5)],
           fill=(255, 255, 255), width=2)
    px = x + int(w * 0.75)
    d.line([px, y + int(h * 0.06), px, y + int(h * 0.55)],
           fill=(255, 255, 255), width=2)
    d.line([px - int(w * 0.05), y + int(h * 0.06),
            px + int(w * 0.05), y + int(h * 0.06)],
           fill=(255, 255, 255), width=2)
    bw, bh = max(6, int(w * 0.09)), max(4, int(h * 0.13))
    d.ellipse([x + int(w * 0.3), y + int(h * 0.62),
               x + int(w * 0.3) + bw, y + int(h * 0.62) + bh],
              fill=(200, 170, 110), outline=(120, 90, 40))


def scene_carrier(d, x, y, w, h):
    """Aircraft carrier at sea: grey deck, tower, two jets."""
    d.rectangle([x, y, x + w, y + h], fill=(150, 180, 205))
    _sea(d, x, y + int(h * 0.55), w, h - int(h * 0.55), base=(30, 80, 120))
    d.rectangle([x + int(w * 0.08), y + int(h * 0.42), x + int(w * 0.92),
                 y + int(h * 0.55)], fill=(90, 95, 105))
    d.rectangle([x + int(w * 0.62), y + int(h * 0.28), x + int(w * 0.72),
                 y + int(h * 0.42)], fill=(70, 75, 85))
    for jx, jy in [(0.25, 0.2), (0.45, 0.12)]:
        px, py = x + int(w * jx), y + int(h * jy)
        d.polygon([(px, py), (px + int(w * 0.07), py + max(2, int(h * 0.04))),
                   (px, py + max(3, int(h * 0.08)))],
                  fill=(220, 220, 230))


def scene_strike(d, x, y, w, h):
    """Strike line: factory behind, placards held high."""
    d.rectangle([x, y, x + w, y + h], fill=(190, 180, 160))
    d.rectangle([x + int(w * 0.1), y + int(h * 0.5), x + int(w * 0.9),
                 y + h], fill=(80, 76, 70))
    for i, frac in enumerate([0.2, 0.45, 0.7]):
        px = x + int(w * frac)
        d.line([px, y + int(h * 0.3), px, y + int(h * 0.62)],
               fill=(60, 55, 50), width=2)
        sw, shh = max(5, int(w * 0.05)), max(5, int(h * 0.18))
        d.rectangle([px - sw, y + int(h * 0.14), px + sw,
                     y + int(h * 0.14) + shh], fill=(255, 255, 255),
                    outline=RED, width=2)


def scene_bridge(d, x, y, w, h):
    """Golden Gate in rain: two towers, cables, slanting rain."""
    d.rectangle([x, y, x + w, y + h], fill=(140, 160, 180))
    for tx in [0.25, 0.7]:
        px = x + int(w * tx)
        tw = max(2, int(w * 0.012))
        d.rectangle([px - tw, y + int(h * 0.06), px + tw,
                     y + int(h * 0.8)], fill=(200, 70, 50))
        d.rectangle([px - max(4, int(w * 0.05)), y + int(h * 0.06),
                     px + max(4, int(w * 0.05)), y + int(h * 0.12)],
                    fill=(200, 70, 50))
    d.line([x + int(w * 0.25), y + int(h * 0.1), x + int(w * 0.7),
            y + int(h * 0.1)], fill=(200, 70, 50), width=2)
    for i in range(6):
        rx = x + int(w * (0.1 + i * 0.14))
        d.line([rx, y + int(h * 0.08), rx - max(2, int(w * 0.025)),
                y + int(h * 0.26)], fill=(220, 230, 240), width=1)


def scene_eu(d, x, y, w, h):
    """EU flag and coins: blue field, ring of stars, gold discs."""
    d.rectangle([x, y, x + w, y + h], fill=(20, 50, 130))
    cx, cy, r = x + int(w * 0.32), y + int(h * 0.5), max(5, int(h * 0.28))
    import math
    for i in range(12):
        a = 2 * math.pi * i / 12 - math.pi / 2
        sx, sy = cx + int(r * math.cos(a)), cy + int(r * math.sin(a))
        sd = max(1, int(w * 0.008))
        d.ellipse([sx - sd, sy - sd, sx + sd, sy + sd],
                  fill=(250, 210, 60))
    for i in range(3):
        gx = x + int(w * (0.62 + i * 0.12))
        cd = max(5, int(h * 0.45))
        d.ellipse([gx, y + int(h * 0.35), gx + cd, y + int(h * 0.35) + cd],
                  fill=GOLD, outline=(180, 130, 20))


def scene_stadium(d, x, y, w, h):
    """Floodlit stadium: stands, lights, a ball on the pitch."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 20, 40))
    for i in range(3):
        yy = y + int(h * 0.08) + i * max(3, int(h * 0.08))
        for k in range(9):
            dx = x + 8 + k * (w // 9)
            dd = max(2, int(w * 0.015))
            d.ellipse([dx, yy, dx + dd, yy + dd], fill=(200, 200, 210))
    for lx in [0.15, 0.85]:
        px = x + int(w * lx)
        d.line([px, y + int(h * 0.04), px, y + int(h * 0.3)],
               fill=(255, 255, 255), width=2)
        ld = max(3, int(h * 0.08))
        d.ellipse([px - ld, y + int(h * 0.02), px + ld,
                   y + int(h * 0.02) + ld], fill=(255, 240, 160))
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(40, 130, 60))
    bw, bh = max(6, int(w * 0.07)), max(4, int(h * 0.11))
    d.ellipse([x + int(w * 0.45), y + int(h * 0.7),
               x + int(w * 0.45) + bw, y + int(h * 0.7) + bh],
              fill=(200, 170, 110), outline=(120, 90, 40))


SCENES = {
    "ship": scene_ship, "summit": scene_summit, "drones": scene_drones,
    "blast": scene_blast, "boat": scene_boat, "factory": scene_factory,
    "vaccine": scene_vaccine, "ebola": scene_ebola, "race": scene_race,
    "rugby": scene_rugby, "carrier": scene_carrier,
    "strike": scene_strike, "bridge": scene_bridge, "eu": scene_eu,
    "stadium": scene_stadium,
}

# ------------------------------------------------------------------ map
# Coarse continent outlines (lon, lat), drawn from geography for this
# build; the map is 560x102, so rough shapes read fine at that size.
LAND = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 62),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-145, 60),
     (-165, 60)],
    [(-80, 10), (-60, 5), (-50, 0), (-40, -5), (-35, -10), (-40, -20),
     (-48, -28), (-58, -35), (-65, -45), (-70, -54), (-73, -40),
     (-73, -25), (-77, -12), (-80, -3)],
    [(-18, 35), (-10, 31), (0, 36), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (35, -20),
     (32, -28), (26, -34), (19, -35), (12, -18), (9, 4), (-8, 5),
     (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (10, 57), (18, 56),
     (21, 55), (24, 59), (28, 60), (30, 62), (40, 68), (55, 68), (70, 72),
     (90, 75), (110, 74), (130, 72), (150, 70), (170, 66), (178, 65),
     (170, 60), (162, 55), (150, 59), (140, 55), (135, 45), (130, 42),
     (127, 40), (122, 38), (120, 32), (110, 20), (105, 10), (100, 8),
     (95, 15), (90, 22), (80, 13), (77, 8), (72, 20), (66, 25), (60, 25),
     (56, 26), (52, 28), (48, 30), (44, 29), (40, 31), (36, 36), (30, 36),
     (26, 40), (22, 37), (19, 42), (12, 44), (8, 44), (3, 43), (-2, 37),
     (-6, 36)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (129, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
     (141, 38), (141, 41), (143, 42), (145, 44), (143, 42), (140, 39)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
     (174, -41), (172, -43), (168, -46)],
]

# Story number -> (lon, lat) for the map pins (heroes 1-3, grid 4-15).
MAP_PINS = [
    (1, 26, 60), (2, 30, 37), (3, 30.5, 50.5), (4, 50.5, 26), (5, 6, 5),
    (6, 107, -6.5), (7, 90, 24), (8, 23, -2), (9, -115, 36),
    (10, 2.3, 48.8), (11, -77, 39), (12, 13.4, 52.5), (13, -122, 38),
    (14, 4.4, 50.8), (15, -3.2, 51.5),
]
LAT_TOP, LAT_BOT = 72, -52


def draw_map(d, x, y, w, h):
    """The map gets its own clean band: navy field, land in sand,
    numbered pins for the 15 illustrated stories, nothing on top of it."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=INK2)
    for poly in LAND:
        pts = []
        for lon, lat in poly:
            px = x + (lon + 180) / 360 * w
            py = y + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * h
            pts.append((px, py))
        d.polygon(pts, fill=(232, 210, 170))
    d.text((x + 10, y + h - 16), "WHERE IT HAPPENED", font=sans_b(10),
           fill=(180, 200, 225))
    for num, lon, lat in MAP_PINS:
        px = x + (lon + 180) / 360 * w
        py = y + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * h
        disc(d, px, py, num, r=8, size=9)


# ------------------------------------------------------------------ cards
def hero_card(d, x, y, w, h, item):
    bg = tint(REGIONS[item["region"]], 0.90)
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=bg,
                        outline=LINE)
    SCENES[item["scene"]](d, x + 2, y + 2, w - 4, 100)
    disc(d, x + w - 18, y + 18, item["num"], r=12, size=12)
    status_pill(d, x + 10, y + 76, item["status"], size=15, height=22)
    source_pill(d, x + w - 4, y + 76, item["source"], size=13, height=22,
                max_w=140)
    d.text((x + 10, y + 106), item["kicker"], font=sans_b(10), fill=RED)
    lines = fit_text(d, "hero%d-title" % item["num"], item["title"],
                     serif_b(26), w - 20, 2)
    draw_lines(d, x + 10, y + 119, lines, serif_b(26), INK, 28)
    lines = fit_text(d, "hero%d-body" % item["num"], item["body"],
                     sans(13), w - 20, 2)
    draw_lines(d, x + 10, y + 177, lines, sans(13), BODY, 15)


def grid_card(d, x, y, w, h, item):
    bg = tint(REGIONS[item["region"]], 0.92)
    d.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=bg,
                        outline=LINE)
    SCENES[item["scene"]](d, x + 1, y + 1, w - 2, 30)
    disc(d, x + w - 11, y + 12, item["num"], r=8, size=8)
    status_pill(d, x + 5, y + 12, item["status"], size=13, height=17)
    source_pill(d, x + w - 4, y + 12, item["source"], size=13, height=17,
                max_w=110)
    d.text((x + 6, y + 36), item["kicker"], font=sans_b(9),
           fill=REGIONS[item["region"]])
    lines = fit_text(d, "grid%d-title" % item["num"], item["title"],
                     sans_b(20), w - 12, 2)
    draw_lines(d, x + 6, y + 47, lines, sans_b(20), INK, 21)
    lines = fit_text(d, "grid%d-body" % item["num"], item["body"],
                     sans(14), w - 12, 2)
    draw_lines(d, x + 6, y + 91, lines, sans(14), (52, 56, 64), 15)


# ------------------------------------------------------------------ data
# All 30 stories happened, or were first reported, on Sunday 22 Nov 2026
# (verified against same-day primary sources in the v2 build record;
# COP31's collapse is the Reuters 12:09 UTC wire, second-sourced).
HEROES = [
    {"num": 1, "region": "EUROPE", "scene": "ship", "status": "CONFIRMED",
     "source": "Helsinki Times", "kicker": "FINLAND \u00b7 SHIP ON FIRE",
     "title": "Sparta II still burning",
     "body": "Firefighting goes on into Sunday; the hull takes on water "
             "and 16 crew were taken off."},
    {"num": 2, "region": "WORLD", "scene": "summit", "status": "CONFIRMED",
     "source": "Reuters", "kicker": "TURKEY \u00b7 CLIMATE TALKS",
     "title": "COP31 collapses \u2014 no deal",
     "body": "The closing plenary rejects the text: no consensus, "
             "nothing adopted."},
    {"num": 3, "region": "EUROPE", "scene": "drones", "status": "CONFIRMED",
     "source": "Reuters", "kicker": "UKRAINE \u00b7 OVERNIGHT ATTACK",
     "title": "186 drones hit Ukraine",
     "body": "161 are shot down by morning; a block of flats in Dymer is "
             "destroyed, 14 feared trapped."},
]

GRID = [
    {"num": 4, "region": "MIDDLE EAST", "scene": "blast",
     "status": "CLAIM", "source": "Iran Press", "kicker": "BAHRAIN \u00b7 GULF",
     "title": "Iran claims Bahrain strikes",
     "body": "Tehran says US radars hit; Bahrain reports one site ablaze."},
    {"num": 5, "region": "AFRICA", "scene": "boat", "status": "REPORTED",
     "source": "Reuters", "kicker": "NIGERIA \u00b7 BOAT DISASTER",
     "title": "Boat toll rises to 24",
     "body": "NEMA counts 24 bodies; police first said four died."},
    {"num": 6, "region": "ASIA", "scene": "factory", "status": "REPORTED",
     "source": "Reuters", "kicker": "INDONESIA \u00b7 FACTORY FIRE",
     "title": "36 missing in factory fire",
     "body": "Rescuers search after a blaze kills three at the plant."},
    {"num": 7, "region": "ASIA", "scene": "vaccine", "status": "CONFIRMED",
     "source": "Access24", "kicker": "BANGLADESH \u00b7 HEALTH",
     "title": "50m children to be vaccinated",
     "body": "A month-long typhoid drive against drug-resistant strains."},
    {"num": 8, "region": "AFRICA", "scene": "ebola", "status": "REPORTED",
     "source": "Wires", "kicker": "CONGO \u00b7 OUTBREAK",
     "title": "Ebola toll passes 5,700",
     "body": "The outbreak's death toll climbs past 5,700, wires report."},
    {"num": 9, "region": "WORLD", "scene": "race", "status": "CONFIRMED",
     "source": "Reuters", "kicker": "LAS VEGAS \u00b7 MOTOR RACING",
     "title": "Verstappen wins in Las Vegas",
     "body": "A third win in four years under the lights on the Strip."},
    {"num": 10, "region": "EUROPE", "scene": "rugby", "status": "CONFIRMED",
     "source": "Reuters", "kicker": "FRANCE \u00b7 RUGBY",
     "title": "France reach the rugby final",
     "body": "Bonus-point win over Argentina sends France through."},
    {"num": 11, "region": "MIDDLE EAST", "scene": "carrier",
     "status": "REPORTED", "source": "Reuters",
     "kicker": "WASHINGTON \u00b7 IRAN",
     "title": "Trump warns Iran again",
     "body": "Warns of a 'very traumatic' outcome if the nuclear deal fails."},
    {"num": 12, "region": "EUROPE", "scene": "strike", "status": "REPORTED",
     "source": "Reuters", "kicker": "GERMANY \u00b7 STRIKE",
     "title": "German workers extend strike",
     "body": "IG Metall widens its walkout at car and shipyard plants."},
    {"num": 13, "region": "AMERICAS", "scene": "bridge", "status": "REPORTED",
     "source": "Reuters", "kicker": "SAN FRANCISCO \u00b7 STORM",
     "title": "City warns off Thanksgiving travel",
     "body": "An atmospheric river heads for the Bay Area for the holiday."},
    {"num": 14, "region": "EUROPE", "scene": "eu", "status": "REPORTED",
     "source": "Reuters", "kicker": "BRUSSELS \u00b7 EU BUDGET",
     "title": "EU chiefs propose budget cuts",
     "body": "Cuts for 2028\u201334 plus a digital tax are put on the table."},
    {"num": 15, "region": "OCEANIA", "scene": "stadium",
     "status": "CONFIRMED", "source": "Reuters", "kicker": "CARDIFF \u00b7 RUGBY",
     "title": "Wallabies edge Wales 29\u201326",
     "body": "Australia hold on in Cardiff to take the win."},
]

# ALSO ON: (region, short text, status, source) -- one line each, three
# columns of five. Texts are kept short so the status pill and the source
# both fit on the line at 13px.
ALSO_ON = [
    ("EUROPE", "Lisbon cost-of-living march", "REPORTED", "Reuters"),
    ("EUROPE", "Zagreb hospital-death rally", "REPORTED", "Reuters"),
    ("EUROPE", "FIDE refers Carlsen", "CONFIRMED", "Reuters"),
    ("EUROPE", "Scotland 67\u20135 Japan", "CONFIRMED", "Reuters"),
    ("EUROPE", "England beat NZ 37\u201312", "CONFIRMED", "Reuters"),
    ("EUROPE", "Arsenal 2\u20132 Newcastle", "CONFIRMED", "Reuters"),
    ("AMERICAS", "Seattle ICE arrests decried", "REPORTED", "Reuters"),
    ("AMERICAS", "Trump backs Bonds for HOF", "REPORTED", "Reuters"),
    ("AMERICAS", "Brazil town hit by supercell", "REPORTED", "Reuters"),
    ("AMERICAS", "University shooting kills two", "REPORTED", "Reuters"),
    ("WORLD", "UN killer-robot talks, 2028", "REPORTED", "Reuters"),
    ("WORLD", "US cash rounds to 5 cents", "REPORTED", "Reuters"),
    ("ASIA", "Japan pilotless air taxi", "CONFIRMED", "Access24"),
    ("ASIA", "Manipur toxic alcohol kills 11", "REPORTED", "Reuters"),
    ("OCEANIA", "Wellington Test continues", "PENDING", "Reuters"),
]

DATE_CHECK = [
    "Every story happened, or was first reported, on Sunday 22 November "
    "2026.",
    "Left out as earlier news: Peru quake, Basra fire, Akvan landfall "
    "(20-21 Nov), Iran's 18 Nov Kuwait strikes, Russia's 20 Nov air "
    "assault, the EU-Indonesia deal (signed Sat), South Africa's "
    "elections (4 Nov).",
    "COP31 collapsed on Sunday -- the closing plenary rejected the "
    "deal: no consensus, nothing adopted.",
    "Nothing here is from before 13 November 2026.",
]

STATS = [("30", "STORIES IN THIS PICTURE"),
         ("7", "REGIONS COVERED"),
         ("186", "DRONES AT UKRAINE"),
         ("14", "MISSING IN KYIV"),
         ("16", "CREW RESCUED"),
         ("24", "DEAD IN NIGERIA BOAT")]


# ------------------------------------------------------------------ layout
def masthead(d, total):
    d.text((8, 8), "THE WORLD IN ONE DAY  \u2014  EVENING EDITION",
           font=sans_b(11), fill=RED)
    d.text((W - 8, 8), "%d STORIES  \u00b7  7 REGIONS  \u00b7  EVERY ONE DATED"
           % total, font=sans_b(9), fill=GREY, anchor="ra")
    d.text((8, 24), "Sunday 22 November 2026", font=serif_b(52), fill=INK)
    d.text((8, 80),
           "COP31 collapses  \u00b7  Sparta II still burning  "
           "\u00b7  186 drones hit Ukraine",
           font=serif(15), fill=(60, 64, 72))
    d.line([8, 98, W - 8, 98], fill=RED, width=2)


def stat_strip(d, y, stats):
    d.rectangle([0, y, W, y + 46], fill=INK)
    sw = W / len(stats)
    for i, (big, label) in enumerate(stats):
        cx = sw * i + sw / 2
        f1, f2 = sans_b(34), sans_b(8)
        tw = d.textlength(big, font=f1)
        d.text((cx - tw / 2, y + 3), big, font=f1, fill=(255, 255, 255))
        tw2 = d.textlength(label, font=f2)
        d.text((cx - tw2 / 2, y + 36), label, font=f2, fill=(170, 190, 215))
        if i:
            d.line([sw * i, y + 6, sw * i, y + 40], fill=(60, 80, 110),
                   width=1)


def region_strip(d, y, counts, h=18):
    rw = (W - 16) / len(REGION_ORDER)
    for i, reg in enumerate(REGION_ORDER):
        x0 = 8 + i * rw
        d.rectangle([x0, y, x0 + rw - 2, y + h], fill=REGIONS[reg])
        txt = "%s %d" % (reg, counts[reg])
        f = sans_b(9)
        tw = d.textlength(txt, font=f)
        d.text((x0 + (rw - tw) / 2, y + 4), txt, font=f,
               fill=(255, 255, 255))


def also_on(d, x, y, w, lines):
    """ALSO ON: three columns of five lines; every line carries its
    region dot, its verification-status pill and its source."""
    d.text((x, y), "ALSO ON  \u2014  SUNDAY 22 NOVEMBER",
           font=sans_b(11), fill=INK)
    d.line([x, y + 16, x + w, y + 16], fill=LINE, width=1)
    cols = 3
    per_col = 5
    cw = w / cols
    for i, (reg, txt, status, src) in enumerate(lines):
        col, row = i // per_col, i % per_col
        lx = x + col * cw
        ly = y + 22 + row * 14
        d.ellipse([lx, ly + 3, lx + 7, ly + 10], fill=REGIONS[reg])
        tx = lx + 11
        pw = status_pill(d, tx, ly, status, size=10, height=13)
        tx += pw + 6
        f = sans(13)
        tw = d.textlength(txt, font=f)
        d.text((tx, ly), txt, font=f, fill=BODY)
        tx += tw + 6
        d.text((tx, ly + 1), "\u00b7 " + src, font=sans(10), fill=GREY)
        full = (11 + pw + 6 + tw + 6 +
                d.textlength("\u00b7 " + src, font=sans(10)))
        if full > cw - 4:
            OVERFLOWS.append(("also_on_%d" % i, txt))


def date_check_box(d, x, y, w, h):
    """DATE CHECK in a red border, labelled READ THIS FIRST -- the
    winners' device (r3 labels it exactly this way)."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=6,
                        outline=RED, width=2, fill=(255, 255, 255))
    d.text((x + 12, y + 7), "READ THIS FIRST \u2014 DATE CHECK",
           font=sans_b(11), fill=RED)
    lines = []
    for sent in DATE_CHECK:
        lines.extend(wrap_text(d, sent, sans(9), w - 24))
    if len(lines) > 7:
        OVERFLOWS.append(("date_check_lines", "%d lines" % len(lines)))
    draw_lines(d, x + 12, y + 24, lines[:7], sans(9), BODY, 11)


def footer(d, y):
    d.line([8, y, W - 8, y], fill=LINE, width=1)
    d.text((8, y + 6),
           "TAGS \u2014 CONFIRMED: verified twice or more  \u00b7  "
           "REPORTED: the day's wires  \u00b7  CLAIM: one side's account  "
           "\u00b7  PENDING: outcome still open",
           font=sans(9), fill=BODY)
    d.text((8, y + 19),
           "Sources: Reuters, AP, AFP, Helsinki Times, TBS News, Iran "
           "Press, Access24, national wires and official statements. "
           "Drawn in code for make.fun news-image-20261122 \u2014 "
           "original drawings, not photographs.",
           font=sans(8), fill=GREY)


def region_counts():
    counts = {r: 0 for r in REGION_ORDER}
    for item in HEROES + GRID:
        counts[item["region"]] += 1
    for reg, _t, _s, _src in ALSO_ON:
        counts[reg] += 1
    return counts


def build():
    total = len(HEROES) + len(GRID) + len(ALSO_ON)
    counts = region_counts()
    assert sum(counts.values()) == total, (counts, total)
    assert total == 30, total

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d, total)
    stat_strip(d, 102, STATS)
    region_strip(d, 152, counts)

    hw, gap = 330, 9
    for i, hero in enumerate(HEROES):
        hero_card(d, 8 + i * (hw + gap), 176, hw, 210, hero)

    gw, gh, gg = 246, 126, 8
    for r in range(3):
        for c in range(4):
            item = GRID[r * 4 + c]
            grid_card(d, 8 + c * (gw + gg), 394 + r * (gh + 6), gw, gh,
                      item)

    also_on(d, 8, 792, W - 16, ALSO_ON)
    draw_map(d, 8, 886, 560, 102)
    date_check_box(d, 576, 886, W - 8 - 576, 102)
    footer(d, 994)
    return img


def main():
    img = build()
    img.save(OUT, optimize=True)
    print("wrote %s %dx%d" % (OUT, img.width, img.height))
    print("TRUNCATIONS: %d" % len(OVERFLOWS))
    for where, text in OVERFLOWS:
        print("  OVERFLOW %s: %s" % (where, text))


if __name__ == "__main__":
    main()
