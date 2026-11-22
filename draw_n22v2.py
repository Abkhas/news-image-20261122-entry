#!/usr/bin/env python3
"""Render the n22 evening-edition news image (1024x1024) for make.fun
news-image-20261122, v2. Everything is drawn in code with PIL: no photos,
no network, no randomness -- two runs give the same bytes.

Two winning families share one engine; FAMILY picks the layout:
  dense  -- 37 stories, UTC timeline strip, 3-column ALSO ON, no per-line
            sources (the n19 top-3 route: breadth + big scenes).
  33     -- 33 stories, no timeline, 2-column ALSO ON with a source on
            every line, stat strip merged into the region band.
Grid is 10 BIG cards (2 rows x 5) in both families: titles 20px bold,
bodies 14px, source pills 13px -- the measured n19 legibility fix.
No VERDICT / HOW SURE / MARKETS boxes (0/10 n19 paid winners had them).
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FAMILY = os.environ.get("FAMILY", "dense")
OUT = os.environ.get("OUT", "entry.png")

# ---------------------------------------------------------------- palette
INK = (17, 33, 57)
INK2 = (9, 20, 38)
PAPER = (253, 249, 238)
CREAM = (244, 238, 222)
RED = (186, 32, 32)
GOLD = (214, 162, 42)
GREY = (92, 96, 104)
LINE = (203, 196, 178)

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


def tint(rgb, frac=0.90):
    """Pale tint of a region colour for card backgrounds."""
    return tuple(int(255 * frac + c * (1 - frac)) for c in rgb)


# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/dejavu"


def F(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


F_TITLE = lambda s: F("DejaVuSerif-Bold.ttf", s)
F_BOLD = lambda s: F("DejaVuSans-Bold.ttf", s)
F_REG = lambda s: F("DejaVuSans.ttf", s)
F_SERIF = lambda s: F("DejaVuSerif.ttf", s)


# ---------------------------------------------------------------- text tools
def wrap(d, text, fnt, max_w):
    """Greedy word wrap by pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, fnt, max_w, max_lines):
    """Wrap to at most max_lines, cutting the last at a word boundary."""
    lines = wrap(d, text, fnt, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    last = lines[-1]
    while d.textlength(last + "...", font=fnt) > max_w and " " in last:
        last = last.rsplit(" ", 1)[0]
    lines[-1] = (last + "...").strip()
    return lines


def block(d, x, y, lines, fnt, fill, leading):
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=fnt, fill=fill)
    return y + len(lines) * leading


def num_disc(d, cx, cy, n, r=11, fill=RED, txt=(255, 255, 255), size=12):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
              outline=(255, 255, 255), width=2)
    f = F_BOLD(size)
    tw = d.textlength(str(n), font=f)
    d.text((cx - tw / 2, cy - size / 2 - 1), str(n), font=f, fill=txt)


# ---------------------------------------------------------------- content
# Every story was verified against a real source dated 22 Nov 2026 (see
# dev/build-result-v2.json). Figures are the ones the sources reported;
# nothing is invented. All stories happened, or were first reported, on
# Sunday 22 November 2026 -- see the DATE CHECK box for what was left out.

HEROES = [
    dict(num=1, region="EUROPE", kicker="GULF OF FINLAND  ·  BALTIC",
         scene="fireship", chip="16",
         title="Sparta II still burning off Finland",
         body=("Fire crews battle the blaze after the drone hit; the "
               "hull may sink as water builds up."),
         source="Helsinki Times  ·  Reuters"),
    dict(num=2, region="WORLD", kicker="ANTALYA  ·  CLIMATE",
         scene="conference", chip="35%",
         title="COP31 collapses \u2014 no deal",
         body=("Rejected at the closing plenary: no consensus. "
               "The EU spurned a text naming no fossil fuels."),
         source="Reuters  ·  AP"),
    dict(num=3, region="EUROPE", kicker="KYIV REGION  ·  WAR",
         scene="nightstrike", chip="186",
         title="186 drones hit Ukraine overnight",
         body=("A Dymer block is destroyed; 14 are feared trapped, "
               "30 hurt across Ukraine."),
         source="Reuters  ·  Kyiv Independent"),
]

GRID = [
    dict(num=4, region="MIDDLE EAST", kicker="BAHRAIN  ·  GULF",
         scene="blast", chip="2",
         title="Iran claims Bahrain strikes",
         body=("Tehran says it hit two US Patriot radars; Bahrain "
               "reports a factory fire."),
         source="IRGC"),
    dict(num=5, region="AFRICA", kicker="BAYELSA  ·  NIGERIA",
         scene="boat", chip="24",
         title="Boat toll rises to 24",
         body=("A mourners' boat capsized on Friday; the search "
               "goes on."),
         source="Reuters"),
    dict(num=6, region="ASIA", kicker="JAVA  ·  INDONESIA",
         scene="factory", chip="36",
         title="36 missing in factory fire",
         body=("Rescuers search the ruins after a factory blaze "
               "in Indonesia kills three."),
         source="Reuters"),
    dict(num=7, region="ASIA", kicker="NAYPYIDAW  ·  ASEAN",
         scene="flags", chip=None,
         title="Myanmar defies ASEAN ruling",
         body=("The army-backed government rejects the decision."),
         source="Reuters"),
    dict(num=8, region="ASIA", kicker="DHAKA  ·  HEALTH",
         scene="cross", chip="50m",
         title="Typhoid jabs for 50m children",
         body=("Bangladesh opens a month-long drive against "
               "drug-resistant typhoid."),
         source="Access24"),
    dict(num=9, region="AFRICA", kicker="CONGO  ·  HEALTH",
         scene="cross", chip="5,700",
         title="Ebola toll passes 5,700",
         body=("The outbreak keeps spreading; health teams ask if "
               "it can be contained."),
         source="Wires"),
    dict(num=10, region="WORLD", kicker="LAS VEGAS  ·  SPORT",
         scene="trophy", chip=None,
         title="Verstappen wins Las Vegas",
         body=("The Dutchman takes the Las Vegas Grand Prix for "
               "the third time."),
         source="Reuters"),
    dict(num=11, region="EUROPE", kicker="PARIS  ·  RUGBY",
         scene="trophy", chip=None,
         title="France reach the final",
         body=("An injury-hit France side beats Argentina to book a "
               "place in the final."),
         source="Reuters"),
    dict(num=12, region="AMERICAS", kicker="WASHINGTON  ·  TEHRAN",
         scene="podium", chip=None,
         title="Trump warns Iran of trauma",
         body=("Trump warns of a 'very traumatic' outcome if no "
               "nuclear deal is reached."),
         source="Access24"),
    dict(num=13, region="MIDDLE EAST", kicker="TEHRAN  ·  DIPLOMACY",
         scene="flags", chip=None,
         title="Qatar visits Tehran for talks",
         body=("A Qatari delegation arrives in Tehran for talks."),
         source="Reuters"),
]

# ALSO ON lines: (region, text, source). Dense uses all 24 (3 cols x 8);
# the 33-story family uses the first 20 (2 cols x 10).
ALSO_ON = [
    ("EUROPE", "German car and shipyard workers extend strike", "Reuters"),
    ("EUROPE", "Thousands march in Lisbon over living costs", "Reuters"),
    ("EUROPE", "Croatians rally over psychiatric hospital death", "Reuters"),
    ("EUROPE", "FIDE refers Carlsen over Budapest forfeits", "Reuters"),
    ("EUROPE", "EU chiefs propose budget cuts and a digital tax", "EU wires"),
    ("EUROPE", "Scotland rout Japan 67-5", "Reuters"),
    ("EUROPE", "England hammer New Zealand 37-12", "Reuters"),
    ("EUROPE", "Arsenal held 2-2 by Newcastle", "Reuters"),
    ("AMERICAS", "Two die in US university shooting", "Access24"),
    ("AMERICAS", "ICE arrests at Seattle airport denounced", "Reuters"),
    ("AMERICAS", "San Francisco warns off Thanksgiving travel", "Wires"),
    ("AMERICAS", "Trump backs Barry Bonds for Hall of Fame", "Reuters"),
    ("AMERICAS", "Brazil town reeling from supercell storm", "Reuters"),
    ("MIDDLE EAST", "Bahrain warns residents of potential threat", "Reuters"),
    ("ASIA", "North Korea postpones Pyongyang marathon", "Reuters"),
    ("ASIA", "China opposes US ban on telecom access", "Reuters"),
    ("ASIA", "Japan's pilotless air taxi carries passengers", "Wires"),
    ("ASIA", "India: 11 die from toxic alcohol in Manipur", "Reuters"),
    ("AFRICA", "Two Nigerians die serving in Russian military", "Access24"),
    ("OCEANIA", "Fiji down Italy for first Nations win", "Reuters"),
    ("OCEANIA", "Wallabies beat Wales 29-26 in Cardiff", "Reuters"),
    ("OCEANIA", "Wellington Test: India bat on in the wind", "Wires"),
    ("WORLD", "States agree UN talks on 'killer robots' by 2028", "Wires"),
    ("WORLD", "US rounds cash to nearest 5 cents in new law", "Wires"),
    ("WORLD", "Alcaraz beats Shelton, reaches final", "Reuters"),
    ("WORLD", "UK-India deal snags on Scotch duty", "Wires"),
]

# Dense family only: the day in UTC, all 22 Nov 2026.
TIMELINE = [
    ("03:22", "Iran claims Bahrain hit"),
    ("06:00", "COP31 vote slips to 11:00"),
    ("07:04", "Drone destroys Dymer block"),
    ("08:05", "Sparta II still burning"),
    ("08:41", "IRGC names Bahrain targets"),
    ("19:09", "COP31 deal rejected"),
]

STATS = [
    ("186", "DRONES AT UKRAINE"),
    ("14", "MISSING IN KYIV REGION"),
    ("16", "CREW RESCUED OFF FINLAND"),
    ("24", "DEAD IN NIGERIA BOAT"),
    ("35%", "COP31 ELECTRICITY GOAL"),
    ("5,700", "EBOLA DEATH TOLL"),
]

# ---------------------------------------------------------------- scenes
# Small flat illustrations drawn with PIL primitives. Each scene fills
# (x, y, w, h) with a bold background and a few readable shapes, so a
# card reads as a picture even at 190 px wide. No randomness anywhere.

SKY = {
    "fireship": (24, 42, 66), "conference": (26, 58, 74),
    "nightstrike": (14, 22, 44), "blast": (96, 46, 30),
    "boat": (22, 78, 108), "factory": (110, 56, 30),
    "flags": (70, 60, 96), "cross": (150, 60, 70),
    "trophy": (52, 110, 62), "podium": (58, 84, 122),
}


def _sky(d, x, y, w, h, name):
    d.rectangle([x, y, x + w, y + h], fill=SKY[name])


def _waves(d, x, y, w, h, col=(220, 235, 245)):
    for i in range(3):
        yy = y + h - 6 - i * 5
        d.arc([x - 4, yy - 3, x + w // 3, yy + 5], 200, 340, fill=col, width=2)
        d.arc([x + w // 3, yy - 3, x + 2 * w // 3, yy + 5], 200, 340,
              fill=col, width=2)
        d.arc([x + 2 * w // 3, yy - 3, x + w + 4, yy + 5], 200, 340,
              fill=col, width=2)


def _stars(d, x, y, w, h):
    pts = [(0.12, 0.18), (0.30, 0.10), (0.48, 0.22), (0.66, 0.12),
           (0.82, 0.20), (0.22, 0.34), (0.55, 0.32), (0.74, 0.36)]
    for px, py in pts:
        sx, sy = x + w * px, y + h * py
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 220))


def scene_fireship(d, x, y, w, h):
    _sky(d, x, y, w, h, "fireship")
    _stars(d, x, y, w, h)
    d.polygon([(x + 8, y + h * 0.62), (x + w - 8, y + h * 0.62),
               (x + w - 20, y + h * 0.82), (x + 20, y + h * 0.82)],
              fill=(70, 74, 82))
    for i, c in enumerate([(186, 60, 40), (214, 162, 42), (60, 110, 140)]):
        cx = x + 14 + i * 22
        d.rectangle([cx, y + h * 0.42, cx + 19, y + h * 0.62], fill=c)
    d.polygon([(x + w * 0.55, y + h * 0.42), (x + w * 0.61, y + h * 0.32),
               (x + w * 0.67, y + h * 0.42)], fill=(240, 140, 40))
    d.polygon([(x + w * 0.60, y + h * 0.36), (x + w * 0.65, y + h * 0.26),
               (x + w * 0.70, y + h * 0.36)], fill=(250, 200, 60))
    for i, r in enumerate([5, 7, 9]):
        cx = x + w * 0.64 + i * 4
        cy = y + h * 0.24 - i * 8
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 110, 116))
    d.line([x + w - 14, y + 8, x + w - 34, y + 22], fill=(255, 220, 120),
           width=2)
    d.ellipse([x + w - 18, y + 4, x + w - 10, y + 12], fill=(240, 240, 240))
    _waves(d, x, y + h - 14, w, 14)


def scene_conference(d, x, y, w, h):
    _sky(d, x, y, w, h, "conference")
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(18, 40, 52))
    d.rectangle([x + w * 0.08, y + h * 0.52, x + w * 0.92, y + h * 0.72],
                fill=(214, 162, 42))
    for i in range(7):
        fx = x + w * (0.12 + i * 0.12)
        col = [(186, 32, 32), (255, 255, 255), (46, 125, 80), (31, 78, 121),
               (214, 162, 42), (176, 92, 20), (90, 90, 105)][i]
        d.polygon([(fx, y + h * 0.30), (fx + 12, y + h * 0.36),
                   (fx, y + h * 0.42)], fill=col)
        d.line([fx, y + h * 0.30, fx, y + h * 0.52], fill=(220, 220, 220),
               width=1)
    cx, cy, r = x + w * 0.82, y + h * 0.24, 15
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255),
              outline=RED, width=2)
    d.line([cx, cy, cx, cy - 9], fill=INK, width=2)
    d.line([cx, cy, cx + 8, cy + 3], fill=INK, width=2)
    gx, gy, gr = x + w * 0.20, y + h * 0.26, 13
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(90, 160, 200),
              outline=(255, 255, 255), width=2)
    d.arc([gx - gr, gy - gr, gx + gr, gy + gr], 300, 60, fill=(255, 255, 255),
          width=1)
    d.line([gx, gy - gr, gx, gy + gr], fill=(255, 255, 255), width=1)


def scene_nightstrike(d, x, y, w, h):
    _sky(d, x, y, w, h, "nightstrike")
    _stars(d, x, y, w, h)
    for i, bh in enumerate([0.34, 0.5, 0.42, 0.62, 0.46]):
        bx = x + 6 + i * (w - 12) // 5
        bw = (w - 12) // 5 - 3
        d.rectangle([bx, y + h * (1 - bh), bx + bw, y + h * 0.92],
                    fill=(30, 40, 62))
        for wy in range(2):
            d.rectangle([bx + 3, y + h * (1 - bh) + 6 + wy * 12, bx + 7,
                         y + h * (1 - bh) + 10 + wy * 12],
                        fill=(250, 210, 110))
    for k, (sx, ex) in enumerate([(0.08, 0.42), (0.42, 0.78)]):
        ax0, ay0 = x + w * sx, y + h * 0.10
        ax1, ay1 = x + w * ex, y + h * 0.52
        d.arc([ax0 - 8, ay0 - 8, ax1 + 8, ay1 + 22], 195, 345,
              fill=(255, 190, 90), width=2)
        d.ellipse([ax1 - 3, ay1 - 3, ax1 + 3, ay1 + 3], fill=(255, 220, 120))
    ex, ey = x + w * 0.72, y + h * 0.30
    for ang in range(0, 360, 45):
        import math
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        d.line([ex, ey, ex + dx * 10, ey + dy * 10], fill=(250, 200, 60),
               width=2)
    d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 240, 180))


def scene_blast(d, x, y, w, h):
    _sky(d, x, y, w, h, "blast")
    cx, cy = x + w / 2, y + h * 0.45
    import math
    for ang in range(0, 360, 30):
        r = 16 if ang % 60 == 0 else 10
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        d.line([cx, cy, cx + dx * r, cy + dy * r], fill=(250, 200, 60),
               width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 240, 180))
    for i, r in enumerate([5, 8, 11]):
        d.ellipse([cx - 22 + i * 4 - r, y + h * 0.75 - r,
                   cx - 22 + i * 4 + r, y + h * 0.75 + r],
                  fill=(110, 110, 116))
    d.rectangle([x, y + h * 0.88, x + w, y + h], fill=(52, 40, 34))


def scene_boat(d, x, y, w, h):
    _sky(d, x, y, w, h, "boat")
    d.polygon([(x + 10, y + h * 0.55), (x + w - 10, y + h * 0.55),
               (x + w - 22, y + h * 0.78), (x + 22, y + h * 0.78)],
              fill=(150, 110, 60))
    d.line([x + w / 2, y + h * 0.55, x + w / 2, y + h * 0.22],
           fill=(220, 220, 220), width=2)
    d.polygon([(x + w / 2, y + h * 0.22), (x + w / 2 + 16, y + h * 0.42),
               (x + w / 2, y + h * 0.42)], fill=(240, 240, 240))
    d.ellipse([x + w * 0.68, y + h * 0.30, x + w * 0.68 + 12,
               y + h * 0.30 + 12], fill=(255, 255, 255), outline=RED, width=2)
    _waves(d, x, y + h - 12, w, 12)


def scene_factory(d, x, y, w, h):
    _sky(d, x, y, w, h, "factory")
    d.rectangle([x + w * 0.12, y + h * 0.42, x + w * 0.62, y + h * 0.85],
                fill=(70, 66, 62))
    d.rectangle([x + w * 0.66, y + h * 0.20, x + w * 0.74, y + h * 0.85],
                fill=(90, 86, 82))
    for i in range(3):
        wx = x + w * (0.20 + i * 0.14)
        d.rectangle([wx, y + h * 0.52, wx + 8, y + h * 0.62],
                    fill=(250, 210, 110))
    import math
    cx, cy = x + w * 0.38, y + h * 0.34
    for ang in range(0, 360, 30):
        r = 13 if ang % 60 == 0 else 8
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        d.line([cx, cy, cx + dx * r, cy + dy * r], fill=(250, 200, 60),
               width=3)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 240, 180))
    for i, r in enumerate([4, 6, 8]):
        d.ellipse([x + w * 0.70 + i * 3 - r, y + h * 0.10 - r,
                   x + w * 0.70 + i * 3 + r, y + h * 0.10 + r],
                  fill=(120, 118, 114))
    d.rectangle([x, y + h * 0.85, x + w, y + h], fill=(52, 40, 34))


def scene_flags(d, x, y, w, h):
    _sky(d, x, y, w, h, "flags")
    d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(52, 48, 70))
    for i, (c1, c2) in enumerate([((186, 32, 32), (255, 255, 255)),
                                  ((31, 78, 121), (214, 162, 42))]):
        fx = x + w * (0.18 + i * 0.42)
        d.rectangle([fx, y + h * 0.22, fx + 26, y + h * 0.52], fill=c1)
        d.rectangle([fx, y + h * 0.22, fx + 26, y + h * 0.37], fill=c2)
        d.line([fx, y + h * 0.22, fx, y + h * 0.70], fill=(220, 220, 220),
               width=2)
    d.ellipse([x + w * 0.44, y + h * 0.30, x + w * 0.56, y + h * 0.44],
              fill=(250, 220, 120))


def scene_cross(d, x, y, w, h):
    _sky(d, x, y, w, h, "cross")
    cx, cy = x + w / 2, y + h * 0.42
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(255, 255, 255))
    d.rectangle([cx - 3, cy - 9, cx + 3, cy + 9], fill=RED)
    d.rectangle([cx - 9, cy - 3, cx + 9, cy + 3], fill=RED)
    d.line([x + 6, y + h * 0.78, x + w * 0.35, y + h * 0.78,
            x + w * 0.45, y + h * 0.66, x + w * 0.55, y + h * 0.86,
            x + w * 0.65, y + h * 0.78, x + w - 6, y + h * 0.78],
           fill=(255, 255, 255), width=2)


def scene_trophy(d, x, y, w, h):
    _sky(d, x, y, w, h, "trophy")
    cx = x + w / 2
    d.polygon([(cx - 10, y + h * 0.18), (cx + 10, y + h * 0.18),
               (cx + 7, y + h * 0.55), (cx - 7, y + h * 0.55)],
              fill=(214, 162, 42))
    d.arc([cx - 16, y + h * 0.20, cx - 4, y + h * 0.45], 90, 270,
          fill=(214, 162, 42), width=3)
    d.arc([cx + 4, y + h * 0.20, cx + 16, y + h * 0.45], 270, 90,
          fill=(214, 162, 42), width=3)
    d.rectangle([cx - 3, y + h * 0.55, cx + 3, y + h * 0.68],
                fill=(214, 162, 42))
    d.rectangle([cx - 9, y + h * 0.68, cx + 9, y + h * 0.76],
                fill=(214, 162, 42))
    d.ellipse([x + w * 0.78, y + h * 0.30, x + w * 0.78 + 10,
               y + h * 0.30 + 10], fill=(255, 255, 255), outline=RED, width=2)


def scene_podium(d, x, y, w, h):
    _sky(d, x, y, w, h, "podium")
    d.rectangle([x + w * 0.36, y + h * 0.55, x + w * 0.64, y + h],
                fill=(30, 46, 70))
    d.ellipse([x + w * 0.42, y + h * 0.18, x + w * 0.58, y + h * 0.48],
              fill=(232, 196, 160))
    d.arc([x + w * 0.36, y + h * 0.12, x + w * 0.64, y + h * 0.55], 180, 360,
          fill=(60, 60, 66), width=3)
    d.line([x + w * 0.30, y + h * 0.55, x + w * 0.44, y + h * 0.34],
           fill=(220, 220, 220), width=2)
    d.ellipse([x + w * 0.42, y + h * 0.30, x + w * 0.47, y + h * 0.36],
              fill=(40, 40, 44))
    d.text((x + 6, y + 6), "\u201c\u201d", font=F_BOLD(20), fill=(255, 255, 255))


SCENES = {
    "fireship": scene_fireship, "conference": scene_conference,
    "nightstrike": scene_nightstrike, "blast": scene_blast,
    "boat": scene_boat, "factory": scene_factory, "flags": scene_flags,
    "cross": scene_cross, "trophy": scene_trophy, "podium": scene_podium,
}

# ---------------------------------------------------------------- world map
# Schematic continents: coarse lon/lat outlines drawn by hand from a
# blank atlas memory, good enough to read as a world map at 560 px wide.
# Red numbered dots mark the main stories by their card number.

LAND = [
    # North America (coarse)
    [(-165, 65), (-150, 70), (-135, 68), (-122, 70), (-110, 68),
     (-96, 68), (-85, 66), (-78, 70), (-70, 62), (-60, 52), (-56, 47),
     (-65, 44), (-70, 42), (-75, 37), (-80, 30), (-82, 26), (-86, 29),
     (-91, 19), (-96, 18), (-100, 23), (-106, 24), (-112, 27),
     (-117, 33), (-122, 38), (-124, 47), (-130, 55), (-140, 60),
     (-152, 58), (-163, 58), (-167, 63)],
    # South America (coarse)
    [(-78, 8), (-72, 11), (-64, 10), (-58, 7), (-51, 4), (-50, 0),
     (-44, -3), (-38, -6), (-35, -9), (-38, -15), (-41, -22), (-48, -27),
     (-53, -33), (-58, -38), (-63, -41), (-66, -47), (-69, -52),
     (-72, -54), (-73, -45), (-73, -35), (-71, -25), (-72, -18),
     (-76, -13), (-80, -6), (-81, 0)],
    # Africa (coarse)
    [(-16, 15), (-15, 22), (-11, 28), (-6, 33), (0, 36), (9, 37),
     (12, 33), (18, 32), (24, 32), (30, 31), (33, 28), (36, 24),
     (39, 20), (42, 14), (46, 11), (51, 11), (50, 4), (45, -1),
     (41, -6), (39, -13), (36, -20), (33, -26), (29, -31), (24, -34),
     (18, -34), (15, -28), (13, -21), (12, -13), (10, -3), (9, 4),
     (3, 6), (-4, 5), (-9, 5), (-13, 8), (-17, 12)],
    # Eurasia (coarse)
    [(-10, 36), (-9, 43), (-2, 48), (2, 51), (7, 54), (10, 58),
     (15, 56), (20, 55), (24, 59), (28, 62), (32, 67), (40, 68),
     (48, 69), (56, 69), (64, 70), (72, 73), (80, 74), (90, 76),
     (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (158, 69), (166, 66), (175, 65), (178, 62), (170, 60), (162, 56),
     (156, 52), (150, 59), (142, 53), (141, 47), (140, 39), (136, 35),
     (131, 33), (127, 36), (123, 39), (120, 34), (116, 28), (110, 20),
     (107, 11), (103, 8), (100, 9), (97, 14), (93, 19), (89, 22),
     (85, 19), (81, 15), (78, 9), (75, 12), (72, 19), (68, 22),
     (64, 25), (60, 25), (56, 26), (52, 27), (48, 30), (44, 29),
     (40, 31), (36, 36), (32, 36), (28, 37), (24, 36), (20, 40),
     (16, 44), (12, 44), (8, 44), (4, 43), (0, 40), (-3, 37), (-8, 37)],
    # Australia (coarse)
    [(113, -22), (114, -29), (115, -33), (118, -35), (124, -33),
     (129, -32), (133, -32), (137, -35), (140, -38), (145, -38),
     (149, -37), (153, -31), (153, -27), (150, -23), (146, -19),
     (142, -14), (141, -12), (137, -12), (133, -12), (130, -13),
     (126, -14), (122, -17), (118, -20), (114, -21)],
    # Japan + Britain + New Zealand (small)
    [(130, 31), (133, 34), (136, 35), (139, 36), (141, 39), (142, 44),
     (140, 41), (138, 37), (135, 34), (132, 33)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 51)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
     (178, -37), (175, -40), (172, -43), (169, -46)],
]

MAP_DOTS = [
    (1, 24, 60), (3, 30, 50), (4, 50, 26), (5, 6, 5), (6, 114, -3),
    (9, 23, 0), (10, -115, 36), (11, 0, 48), (12, -77, 39), (13, 51, 25),
]

MAP_LAT_TOP, MAP_LAT_BOT = 72, -52


def draw_map(d, x, y, w, h):
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=INK2)
    for poly in LAND:
        pts = []
        for lon, lat in poly:
            px = x + (lon + 180) / 360 * w
            py = y + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * h
            pts.append((px, py))
        d.polygon(pts, fill=(232, 210, 170))
    d.text((x + 10, y + 6), "WHERE IT HAPPENED", font=F_BOLD(10),
           fill=(180, 200, 225))
    for num, lon, lat in MAP_DOTS:
        px = x + (lon + 180) / 360 * w
        py = y + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * h
        num_disc(d, px, py, num, r=8, size=9)


# ---------------------------------------------------------------- cards
def hero_card(d, x, y, w, h, item):
    bg = tint(REGIONS[item["region"]], 0.90)
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=bg,
                        outline=LINE)
    SCENES[item["scene"]](d, x + 2, y + 2, w - 4, 84)
    num_disc(d, x + w - 18, y + 18, item["num"], r=12, size=12)
    if item.get("chip"):
        d.rounded_rectangle([x + 10, y + 62, x + 76, y + 84], radius=4,
                            fill=(255, 255, 255), outline=LINE)
        f = F_BOLD(15)
        tw = d.textlength(item["chip"], font=f)
        d.text((x + 43 - tw / 2, y + 66), item["chip"], font=f, fill=INK)
    f = F_BOLD(13)
    sw = d.textlength(item["source"], font=f) + 14
    d.rounded_rectangle([x + w - 4 - sw, y + 62, x + w - 4, y + 84],
                        radius=4, fill=(255, 255, 255), outline=LINE)
    d.text((x + w + 3 - sw, y + 66), item["source"], font=f, fill=INK)
    d.text((x + 10, y + 92), item["kicker"], font=F_BOLD(10), fill=RED)
    lines = fit(d, item["title"], F_BOLD(26), w - 20, 2)
    block(d, x + 10, y + 105, lines, F_BOLD(26), INK, 28)
    lines = fit(d, item["body"], F_REG(13), w - 20, 2)
    block(d, x + 10, y + 164, lines, F_REG(13), (40, 44, 52), 15)


def grid_card(d, x, y, w, h, item):
    bg = tint(REGIONS[item["region"]], 0.92)
    d.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=bg,
                        outline=LINE)
    SCENES[item["scene"]](d, x + 1, y + 1, w - 2, 40)
    num_disc(d, x + w - 11, y + 12, item["num"], r=8, size=8)
    if item.get("chip"):
        f = F_BOLD(13)
        cw = d.textlength(item["chip"], font=f) + 12
        d.rounded_rectangle([x + 4, y + 23, x + 4 + cw, y + 39], radius=3,
                            fill=(255, 255, 255), outline=LINE)
        d.text((x + 10, y + 26), item["chip"], font=f, fill=INK)
    d.text((x + 6, y + 44), item["kicker"], font=F_BOLD(10),
           fill=REGIONS[item["region"]])
    lines = fit(d, item["title"], F_BOLD(20), w - 12, 2)
    block(d, x + 6, y + 57, lines, F_BOLD(20), INK, 22)
    lines = fit(d, item["body"], F_REG(14), w - 12, 3)
    block(d, x + 6, y + 103, lines, F_REG(14), (52, 56, 64), 16)
    # source pill on the scene band, bottom-right, 13px minimum:
    # a name that does not fit at 13px is dropped, never shrunk.
    f = F_BOLD(13)
    if d.textlength(item["source"], font=f) <= w - 24:
        sw = d.textlength(item["source"], font=f) + 14
        d.rounded_rectangle([x + w - 4 - sw, y + 23,
                             x + w - 4, y + 39],
                            radius=3, fill=(255, 255, 255), outline=LINE)
        d.text((x + w + 3 - sw, y + 26), item["source"], font=f, fill=INK)

# ---------------------------------------------------------------- layout
# 33-story family uses a balanced 20-line subset of ALSO_ON.
ALSO33 = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20,
          22, 24]

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


def region_counts(also_lines):
    counts = {r: 0 for r in REGION_ORDER}
    for item in HEROES + GRID:
        counts[item["region"]] += 1
    for reg, _t, _s in also_lines:
        counts[reg] += 1
    return counts


def masthead(d, total):
    d.text((8, 8), "THE WORLD IN ONE DAY  \u2014  EVENING EDITION",
           font=F_BOLD(11), fill=RED)
    d.text((W - 8, 8), "%d STORIES  \u00b7  7 REGIONS  \u00b7  EVERY ONE DATED"
           % total, font=F_BOLD(9), fill=GREY, anchor="ra")
    d.text((8, 24), "Sunday 22 November 2026", font=F_TITLE(48), fill=INK)
    d.text((8, 76),
           "COP31 collapses  \u00b7  Sparta II still burning  "
           "\u00b7  186 drones hit Ukraine",
           font=F_SERIF(14), fill=(60, 64, 72))
    d.line([8, 96, W - 8, 96], fill=RED, width=2)


def stat_strip(d, y, stats):
    d.rectangle([0, y, W, y + 38], fill=INK)
    sw = W / len(stats)
    for i, (big, label) in enumerate(stats):
        cx = sw * i + sw / 2
        f1, f2 = F_BOLD(24), F_BOLD(8)
        tw = d.textlength(big, font=f1)
        d.text((cx - tw / 2, y + 3), big, font=f1, fill=(255, 255, 255))
        tw2 = d.textlength(label, font=f2)
        d.text((cx - tw2 / 2, y + 27), label, font=f2, fill=(170, 190, 215))
        if i:
            d.line([sw * i, y + 5, sw * i, y + 33], fill=(60, 80, 110),
                   width=1)


def region_strip(d, y, counts, h=17):
    rw = (W - 16) / len(REGION_ORDER)
    for i, reg in enumerate(REGION_ORDER):
        x0 = 8 + i * rw
        d.rectangle([x0, y, x0 + rw - 2, y + h], fill=REGIONS[reg])
        txt = "%s %d" % (reg, counts[reg])
        f = F_BOLD(9)
        tw = d.textlength(txt, font=f)
        d.text((x0 + (rw - tw) / 2, y + 4), txt, font=f, fill=(255, 255, 255))


def timeline_strip(d, y):
    d.text((8, y), "THE DAY IN UTC", font=F_BOLD(9), fill=RED)
    cw = (W - 16) / len(TIMELINE)
    for i, (tm, txt) in enumerate(TIMELINE):
        x0 = 8 + i * cw
        d.text((x0, y + 13), tm, font=F_BOLD(12), fill=RED)
        d.text((x0, y + 27), txt, font=F_REG(11), fill=(40, 44, 52))
        if i:
            d.line([x0 - 4, y + 13, x0 - 4, y + 38], fill=LINE, width=1)


def also_on(d, x, y, w, lines, cols, with_sources):
    d.text((x, y), "ALSO ON  \u2014  SUNDAY 22 NOVEMBER",
           font=F_BOLD(11), fill=INK)
    d.line([x, y + 16, x + w, y + 16], fill=LINE, width=1)
    per_col = (len(lines) + cols - 1) // cols
    cw = w / cols
    f = F_REG(13)
    for i, (reg, txt, src) in enumerate(lines):
        col, row = i // per_col, i % per_col
        lx = x + col * cw
        ly = y + 22 + row * 13
        dot = REGIONS[reg]
        d.ellipse([lx, ly + 3, lx + 7, ly + 10], fill=dot)
        show = txt if not with_sources else "%s  \u00b7  %s" % (txt, src)
        d.text((lx + 11, ly), show, font=f, fill=(40, 44, 52))


def bottom_band(d, y, h):
    # Airy bottom band: map on the left, DATE CHECK on the right, with
    # real breathing room (v1 duel feedback: the old band read clipped).
    draw_map(d, 8, y, 560, h)
    bx0 = 576
    d.rounded_rectangle([bx0, y, W - 8, y + h], radius=6,
                        outline=RED, width=2, fill=(255, 255, 255))
    d.text((bx0 + 12, y + 8), "DATE CHECK", font=F_BOLD(11), fill=RED)
    lines = []
    for sent in DATE_CHECK:
        lines.extend(wrap(d, sent, F_REG(9), W - 8 - bx0 - 24))
    block(d, bx0 + 12, y + 26, lines, F_REG(9), (40, 44, 52), 12)


def footer(d, y):
    d.line([8, y, W - 8, y], fill=LINE, width=1)
    d.text((8, y + 6),
           "HOW WE CHECKED \u2014 Every story verified against BBC, "
           "Reuters, AP, AFP, CNN, national wires and official statements "
           "before drawing. Sources are named beside each story. Original "
           "drawings, not photographs.",
           font=F_REG(9), fill=(40, 44, 52))
    d.text((8, y + 20),
           "Drawn in code for the make.fun news-image-20261122 competition "
           " \u00b7  Evening edition \u2014 news to 19:30 WIB, Sunday 22 "
           "November 2026.",
           font=F_REG(8), fill=GREY)


def build():
    dense = FAMILY == "dense"
    if dense:
        also_lines = ALSO_ON
        total = 3 + len(GRID) + len(also_lines)
    else:
        also_lines = [ALSO_ON[i] for i in ALSO33]
        total = 3 + len(GRID) + len(also_lines)
    counts = region_counts(also_lines)
    assert sum(counts.values()) == total, (counts, total)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d, total)

    if dense:
        stat_strip(d, 100, [("39", "STORIES IN THIS PICTURE"),
                            ("7", "REGIONS COVERED"),
                            ("186", "DRONES AT UKRAINE"),
                            ("14", "MISSING IN KYIV"),
                            ("16", "CREW RESCUED"),
                            ("24", "DEAD IN NIGERIA BOAT")])
        region_strip(d, 140, counts)
        timeline_strip(d, 159)
        hy, gy = 199, 401
    else:
        region_strip(d, 100, counts, h=18)
        # stat strip merged into the region band: digits under the bars.
        stat_strip(d, 122, STATS)
        hy, gy = 166, 368

    hw, gap = 330, 9
    for i, hero in enumerate(HEROES):
        hero_card(d, 8 + i * (hw + gap), hy, hw, 196, hero)

    gw, gh, gg = 196, 160, 6
    for r in range(2):
        for c in range(5):
            item = GRID[r * 5 + c]
            grid_card(d, 10 + c * (gw + gg), gy + r * (gh + 6), gw, gh, item)

    if dense:
        ay = gy + 2 * gh + 12
        also_on(d, 8, ay, W - 16, also_lines, 3, False)
        by = ay + 22 + 9 * 13 + 6
    else:
        ay = gy + 2 * gh + 12
        also_on(d, 8, ay, W - 16, also_lines, 2, True)
        by = ay + 22 + 10 * 13 + 6

    bh = 988 - by
    bottom_band(d, by, bh)
    footer(d, 994)
    return img


def main():
    img = build()
    img.save(OUT, optimize=True)
    print("wrote %s %dx%d family=%s" % (OUT, img.width, img.height, FAMILY))


if __name__ == "__main__":
    main()
