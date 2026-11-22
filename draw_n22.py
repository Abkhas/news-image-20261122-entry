#!/usr/bin/env python3
"""Render the n22 morning-edition news image (1024x1024) for
make.fun news-image-20261122. Everything is drawn in code with PIL:
no photos, no network, no randomness -- two runs give the same bytes.

Layout (own design, following the winning newspaper-front-page shape):
masthead -> red stat strip -> region strip -> 3 hero cards -> 30-card
grid -> navy world map + date check -> how-we-checked footer.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
INK = (17, 33, 57)          # deep navy
INK2 = (9, 20, 38)          # darker navy
PAPER = (253, 249, 238)     # warm paper
CREAM = (244, 238, 222)     # card paper
RED = (186, 32, 32)
RED_DK = (138, 22, 22)
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


def tint(rgb, frac=0.88):
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
    """Wrap text to at most max_lines, truncating the last at a word
    boundary with ..."""
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


def chip(d, x, y, big, label, w, bg=(255, 255, 255), fg=INK):
    """White stat chip: big figure over a small label."""
    d.rounded_rectangle([x, y, x + w - 2, y + 44], radius=4, fill=bg,
                        outline=LINE)
    f1, f2 = F_BOLD(15), F_REG(8)
    tw = d.textlength(big, font=f1)
    d.text((x + (w - tw) / 2, y + 4), big, font=f1, fill=fg)
    tw2 = d.textlength(label, font=f2)
    d.text((x + (w - tw2) / 2, y + 26), label, font=f2, fill=GREY)


# ---------------------------------------------------------------- content
# Every story was verified against a real source on 22 Nov 2026 (see
# dev/build-result-v1.json for the source list). Figures are the ones the
# sources reported; nothing is invented. Stories are the weekend's news
# as of Sunday morning -- first reported 20-22 Nov 2026.

HEROES = [
    dict(num=1, region="EUROPE", kicker="GULF OF FINLAND  ·  BALTIC",
         scene="sparta", chip="16",
         title="Burning Russian ship towed from Finnish waters",
         body=("Drones hit the Sparta II, bound for Kaliningrad. Finland says "
               "Ukraine was likely behind the strike; the 16 crew were rescued."),
         source="Reuters  ·  Finnish Border Guard"),
    dict(num=2, region="WORLD", kicker="ANTALYA  ·  CLIMATE",
         scene="cop31", chip="~200",
         title="COP31 deadlocked deep into overtime",
         body=("Talks ran past their Friday deadline with no deal on fossil "
               "fuels or finance. The EU warns: a good deal or no deal at all."),
         source="Reuters  ·  AP"),
    dict(num=3, region="EUROPE", kicker="KYIV  ·  WAR",
         scene="ukraine", chip="400+",
         title="Russia's biggest air assault of the year",
         body=("More than 400 drones and 110 missiles hit Ukraine; at least 9 "
               "killed. Missiles also came down in Poland; NATO calls it a "
               "grave violation."),
         source="Zelensky  ·  AP  ·  Reuters"),
]

CARDS = [
    # --- Europe
    dict(num=4, region="EUROPE", kicker="KYIV  ·  POLITICS", scene="speech",
         chip=None, title="Zelensky: Putin is a \u2018killer\u2019",
         body=("Trump called Putin a \u2018friend\u2019; Zelensky told CNN he "
               "\u2018is killing each day and night\u2019."),
         source="CNN  ·  BBC"),
    dict(num=5, region="EUROPE", kicker="COPENHAGEN  ·  SECURITY", scene="shield",
         chip=None, title="Denmark expels Russian attach\u00e9",
         body=("Copenhagen blames Russian intelligence for a foiled plot to "
               "kill rapper Kyivstoner."),
         source="BBC  ·  Reuters"),
    dict(num=6, region="EUROPE", kicker="TALLINN  ·  BORDER", scene="barrier",
         chip="1 Dec", title="Estonia to shut Russia border",
         body=("All road crossings close from 1 December after a GRU "
               "sabotage attempt."),
         source="Estonian MFA"),
    dict(num=7, region="EUROPE", kicker="WARSAW  ·  NATO", scene="plane",
         chip=None, title="NATO chief heads to Warsaw",
         body=("Mark Rutte visits Poland on Saturday after Russian missiles "
               "landed during allied drills."),
         source="Helsinki Times"),
    dict(num=8, region="EUROPE", kicker="LONDON  ·  CHRISTMAS", scene="tree",
         chip=None, title="Oslo tree sails for London",
         body=("Trafalgar Square\u2019s Christmas tree sets off from Oslo on its "
               "journey to London."),
         source="BBC"),
    dict(num=9, region="EUROPE", kicker="BRUSSELS  ·  BUDGET", scene="market",
         chip=None, title="EU chiefs propose budget cuts",
         body=("Leaders propose cuts to the 2028\u201334 EU budget and suggest a "
               "tax on digital platforms."),
         source="EU wires, 22 Nov"),
    # --- Middle East
    dict(num=10, region="MIDDLE EAST", kicker="STRAIT OF HORMUZ", scene="ship",
         chip="2", title="Two tankers hit off Oman",
         body=("UK maritime agency reports two tankers struck by projectiles "
               "near Khasab."),
         source="UKMTO  ·  Al Jazeera"),
    dict(num=11, region="MIDDLE EAST", kicker="WASHINGTON  ·  TEHRAN", scene="flags",
         chip=None, title="Trump seeks \u2018permanent\u2019 Iran deal",
         body=("Washington pushes for a lasting nuclear deal as tanker attacks "
               "mount in the Strait of Hormuz."),
         source="AP  ·  Reuters"),
    dict(num=12, region="MIDDLE EAST", kicker="QESHM ISLAND", scene="blast",
         chip=None, title="Iran: Qeshm blasts were disposal",
         body=("Tehran says blasts on Qeshm Island were US munitions disposal, "
               "not a fresh attack."),
         source="Times of India, 22 Nov"),
    dict(num=13, region="MIDDLE EAST", kicker="GAZA", scene="rubble",
         chip="6", title="Israeli strikes kill six in Gaza",
         body=("Six people are killed in Israeli strikes in Gaza, monitors "
               "report."),
         source="Juba Global"),
    # --- Africa
    dict(num=14, region="AFRICA", kicker="BAYELSA  ·  NIGERIA", scene="boat",
         chip="23", title="Boat toll rises to 23",
         body=("The death toll climbs in Nigeria\u2019s Bayelsa boat accident; "
               "the governor orders a probe."),
         source="Punch  ·  Channels TV"),
    dict(num=15, region="AFRICA", kicker="MOGADISHU  ·  DIPLOMACY", scene="flags",
         chip=None, title="Somalia expels UAE envoy",
         body=("Mogadishu orders out the Emirates ambassador as a diplomatic "
               "row deepens in the Horn."),
         source="Juba Global"),
    dict(num=16, region="AFRICA", kicker="ADDIS ABABA  ·  CONFLICT", scene="people",
         chip="700k", title="700,000 flee Ethiopia fighting",
         body=("Conflict in southern Ethiopia displaces around 700,000 people, "
               "monitors report."),
         source="Juba Global"),
    dict(num=17, region="AFRICA", kicker="CAIRO  ·  ECONOMY", scene="bank",
         chip="$2.3bn", title="Egypt nears $2.3bn IMF payout",
         body=("A staff-level deal could unlock fresh IMF financing as Egypt\u2019s "
               "recovery gains pace."),
         source="Trendsnafrica"),
    dict(num=18, region="AFRICA", kicker="CONGO  ·  HEALTH", scene="health",
         chip=None, title="Ebola child deaths alarm WHO",
         body=("The WHO warns of high child deaths in the Congo Ebola outbreak."),
         source="WHO  ·  Juba Global"),
    dict(num=19, region="AFRICA", kicker="CAF  ·  FOOTBALL", scene="sport",
         chip="6", title="AFCON 2027 host cities named",
         body=("CAF names six host cities across Kenya, Tanzania and Uganda for "
               "the 2027 finals."),
         source="CAF"),
    # --- Asia
    dict(num=20, region="ASIA", kicker="KATHMANDU  ·  DELHI", scene="flags",
         chip=None, title="Nepal PM starts India visit",
         body=("Balendra Shah begins his first India visit; talks with Modi "
               "on Monday."),
         source="Indian wires"),
    dict(num=21, region="ASIA", kicker="TOKYO  ·  DEFENCE", scene="missile",
         chip=None, title="Japan to train live-fire in India",
         body=("Tokyo and Delhi sign a deal letting Japanese forces fire "
               "missiles at Indian ranges."),
         source="India-Japan 2+2 statement"),
    dict(num=22, region="ASIA", kicker="PATNA  ·  BIHAR", scene="bridge",
         chip=None, title="Modi opens Nitish Setu",
         body=("The prime minister inaugurates the Nitish Setu bridge linking "
               "Patna and Vaishali in Bihar."),
         source="Daily Jagran"),
    dict(num=23, region="ASIA", kicker="SEOUL  ·  EXAMS", scene="exam",
         chip="$75k", title="$75,000 for exam-cheat tips",
         body=("South Korea repeats a $75,000 bounty for reports of "
               "cheating on exams."),
         source="Wires, 22 Nov"),
    dict(num=24, region="ASIA", kicker="WELLINGTON  ·  CRICKET", scene="sport",
         chip=None, title="India dig in at Wellington",
         body=("India\u2019s batters stand firm in windy Wellington against "
               "New Zealand."),
         source="Wires"),
    # --- Americas
    dict(num=25, region="AMERICAS", kicker="OTTAWA  ·  WASHINGTON", scene="flags",
         chip=None, title="Hegseth redraws Canada ties",
         body=("The US defence chief sets fresh limits on military ties with "
               "Canada."),
         source="Wires, 22 Nov"),
    dict(num=26, region="AMERICAS", kicker="WASHINGTON  ·  CYBER", scene="tech",
         chip=None, title="FBI probes database hack",
         body=("The bureau is investigating an apparent hack of its criminal "
               "database."),
         source="BBC"),
    dict(num=27, region="AMERICAS", kicker="USA  ·  AVIATION", scene="plane",
         chip="6m", title="Airlines warned over al-Qaeda calls",
         body=("FBI, DHS and TSA warn carriers of copycat-attack calls ahead of "
               "Thanksgiving; no specific threat."),
         source="CNN"),
    dict(num=28, region="AMERICAS", kicker="NEW YORK  ·  COURTS", scene="court",
         chip="19y", title="Gupta gets 19 years in Pannun plot",
         body=("A US court jails Nikhil Gupta for 235 months over the plot "
               "to kill activist Pannun."),
         source="Reuters"),
    dict(num=29, region="AMERICAS", kicker="SINALOA  ·  MEXICO", scene="shield",
         chip="11", title="Cartel boss seized; 11 killed",
         body=("Mexico captures FBI most-wanted \u2018El Chapo Isidro\u2019; "
               "gunmen torch trucks, halt a ball game."),
         source="AP"),
    dict(num=30, region="AMERICAS", kicker="BRASILIA  ·  BRAZIL", scene="health",
         chip=None, title="Bolsonaro in intensive care",
         body=("Brazil\u2019s jailed ex-president is stable with a bowel "
               "obstruction; no discharge date set."),
         source="Reuters"),
    # --- Oceania
    dict(num=31, region="OCEANIA", kicker="CANBERRA  ·  CRICKET", scene="sport",
         chip=None, title="Cummins keeps captaincy",
         body=("Pat Cummins wins Cricket Australia\u2019s unanimous backing to "
               "stay on as Test captain."),
         source="Daily Jagran"),
    # --- World
    dict(num=32, region="WORLD", kicker="SAN FRANCISCO  ·  TECH", scene="rocket",
         chip="$81bn", title="Anthropic\u2019s $81.3bn debut",
         body=("The AI firm\u2019s listing is the biggest stock-market debut "
               "in history."),
         source="Reuters"),
    dict(num=33, region="WORLD", kicker="MARKETS", scene="market",
         chip="-3%", title="Markets sell off; oil slides",
         body=("Stocks fall on AI and rate worries as Nvidia tumbles; crude "
               "drops more than 3%."),
         source="Wires"),
]

STATS = [
    ("33", "STORIES IN THIS PICTURE"),
    ("7", "REGIONS COVERED"),
    ("400+", "DRONES FIRED AT UKRAINE"),
    ("110", "MISSILES IN THE BARRAGE"),
    ("16", "CREW RESCUED OFF FINLAND"),
]

# ---------------------------------------------------------------- scenes
# Small flat illustrations drawn with PIL primitives. Each scene fills
# (x, y, w, h) with a sky/background colour and a few bold shapes, so a
# card reads as a picture even at 160 px wide. Palettes are per-card.

SKY = {
    "sparta": (24, 42, 66), "cop31": (26, 58, 74), "ukraine": (14, 22, 44),
    "speech": (58, 84, 122), "shield": (46, 80, 60), "barrier": (120, 74, 40),
    "plane": (96, 140, 180), "tree": (34, 84, 58), "market": (58, 64, 96),
    "ship": (30, 66, 96), "flags": (70, 60, 96), "blast": (96, 46, 30),
    "boat": (22, 78, 108), "people": (120, 84, 44), "money": (40, 96, 64),
    "health": (150, 60, 70), "sport": (52, 110, 62), "missile": (52, 58, 88),
    "bridge": (90, 110, 140), "exam": (120, 96, 52), "tech": (44, 62, 96),
    "court": (72, 72, 96),
}


def _sky(d, x, y, w, h, name):
    d.rectangle([x, y, x + w, y + h], fill=SKY[name])


def _stars(d, x, y, w, h, n=8, seed=7):
    import random
    rnd = random.Random(seed)
    for _ in range(n):
        sx = x + rnd.randint(2, max(3, w - 3))
        sy = y + rnd.randint(2, max(3, h // 2))
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 220))


def _waves(d, x, y, w, h, col=(220, 235, 245)):
    for i in range(3):
        yy = y + h - 6 - i * 5
        d.arc([x - 4, yy - 3, x + w // 3, yy + 5], 200, 340, fill=col, width=2)
        d.arc([x + w // 3, yy - 3, x + 2 * w // 3, yy + 5], 200, 340,
              fill=col, width=2)
        d.arc([x + 2 * w // 3, yy - 3, x + w + 4, yy + 5], 200, 340,
              fill=col, width=2)


def scene_sparta(d, x, y, w, h):
    _sky(d, x, y, w, h, "sparta")
    _stars(d, x, y, w, h, n=10, seed=3)
    # burning cargo ship: hull, containers, smoke, fire glow
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
    # drone with trail
    d.line([x + w - 14, y + 8, x + w - 34, y + 22], fill=(255, 220, 120),
           width=2)
    d.ellipse([x + w - 18, y + 4, x + w - 10, y + 12], fill=(240, 240, 240))
    _waves(d, x, y + h - 14, w, 14)


def scene_cop31(d, x, y, w, h):
    _sky(d, x, y, w, h, "cop31")
    # conference hall: stage, flags, big clock reading overtime
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
    # clock
    cx, cy, r = x + w * 0.82, y + h * 0.24, 15
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255),
              outline=RED, width=2)
    d.line([cx, cy, cx, cy - 9], fill=INK, width=2)
    d.line([cx, cy, cx + 8, cy + 3], fill=INK, width=2)
    # globe
    gx, gy, gr = x + w * 0.20, y + h * 0.26, 13
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(90, 160, 200),
              outline=(255, 255, 255), width=2)
    d.arc([gx - gr, gy - gr, gx + gr, gy + gr], 300, 60, fill=(255, 255, 255),
          width=1)
    d.line([gx, gy - gr, gx, gy + gr], fill=(255, 255, 255), width=1)


def scene_ukraine(d, x, y, w, h):
    _sky(d, x, y, w, h, "ukraine")
    _stars(d, x, y, w, h, n=12, seed=11)
    # skyline
    for i, bh in enumerate([0.34, 0.5, 0.42, 0.62, 0.46]):
        bx = x + 6 + i * (w - 12) // 5
        bw = (w - 12) // 5 - 3
        d.rectangle([bx, y + h * (1 - bh), bx + bw, y + h * 0.92],
                    fill=(30, 40, 62))
        for wy in range(2):
            d.rectangle([bx + 3, y + h * (1 - bh) + 6 + wy * 12, bx + 7,
                         y + h * (1 - bh) + 10 + wy * 12],
                        fill=(250, 210, 110))
    # missile arcs with fire
    for k, (sx, ex) in enumerate([(0.08, 0.42), (0.42, 0.78)]):
        ax0, ay0 = x + w * sx, y + h * 0.10
        ax1, ay1 = x + w * ex, y + h * 0.52
        d.arc([ax0 - 8, ay0 - 8, ax1 + 8, ay1 + 22], 195, 345,
              fill=(255, 190, 90), width=2)
        d.ellipse([ax1 - 3, ay1 - 3, ax1 + 3, ay1 + 3], fill=(255, 220, 120))
    # explosion star
    ex, ey = x + w * 0.72, y + h * 0.30
    for ang in range(0, 360, 45):
        import math
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        d.line([ex, ey, ex + dx * 10, ey + dy * 10], fill=(250, 200, 60),
               width=2)
    d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 240, 180))


def scene_speech(d, x, y, w, h):
    _sky(d, x, y, w, h, "speech")
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


def scene_shield(d, x, y, w, h):
    _sky(d, x, y, w, h, "shield")
    cx = x + w / 2
    d.polygon([(cx - 13, y + 4), (cx + 13, y + 4), (cx + 13, y + h * 0.45),
               (cx, y + h * 0.85), (cx - 13, y + h * 0.45)],
              fill=(220, 226, 232), outline=(255, 255, 255), width=2)
    d.line([cx - 6, y + h * 0.42, cx - 1, y + h * 0.55, cx + 7, y + h * 0.28],
           fill=(46, 125, 80), width=3)


def scene_barrier(d, x, y, w, h):
    _sky(d, x, y, w, h, "barrier")
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(60, 58, 54))
    for i in range(3):
        bx = x + 6 + i * (w - 12) // 3
        d.rectangle([bx, y + h * 0.30, bx + (w - 12) // 3 - 4, y + h * 0.52],
                    fill=(240, 240, 240) if i % 2 == 0 else RED)
    d.line([x + 4, y + h * 0.30, x + w - 4, y + h * 0.30], fill=(30, 30, 30),
           width=2)
    d.line([x + 8, y + h * 0.52, x + 8, y + h * 0.62], fill=(30, 30, 30),
           width=2)
    d.line([x + w - 8, y + h * 0.52, x + w - 8, y + h * 0.62],
           fill=(30, 30, 30), width=2)


def scene_plane(d, x, y, w, h):
    _sky(d, x, y, w, h, "plane")
    for cx, cy, r in [(0.2, 0.3, 6), (0.75, 0.2, 8), (0.55, 0.7, 5)]:
        d.ellipse([x + w * cx - r, y + h * cy - r // 2,
                   x + w * cx + r, y + h * cy + r // 2],
                  fill=(255, 255, 255))
    # fuselage
    d.ellipse([x + w * 0.12, y + h * 0.42, x + w * 0.88, y + h * 0.58],
              fill=(245, 245, 245))
    d.polygon([(x + w * 0.45, y + h * 0.50), (x + w * 0.62, y + h * 0.78),
               (x + w * 0.72, y + h * 0.78), (x + w * 0.58, y + h * 0.50)],
              fill=(210, 215, 220))
    d.polygon([(x + w * 0.45, y + h * 0.50), (x + w * 0.58, y + h * 0.26),
               (x + w * 0.66, y + h * 0.26), (x + w * 0.55, y + h * 0.50)],
              fill=(210, 215, 220))
    for i in range(4):
        d.ellipse([x + w * (0.24 + i * 0.12), y + h * 0.47,
                   x + w * (0.24 + i * 0.12) + 5, y + h * 0.53],
                  fill=(30, 60, 100))


def scene_tree(d, x, y, w, h):
    _sky(d, x, y, w, h, "tree")
    cx = x + w / 2
    d.polygon([(cx, y + 2), (cx - 12, y + h * 0.45), (cx + 12, y + h * 0.45)],
              fill=(46, 125, 80))
    d.polygon([(cx, y + h * 0.28), (cx - 16, y + h * 0.72),
               (cx + 16, y + h * 0.72)], fill=(36, 105, 66))
    d.rectangle([cx - 3, y + h * 0.72, cx + 3, y + h * 0.92],
                fill=(120, 84, 44))
    for gx, gy in [(0.38, 0.35), (0.60, 0.5), (0.44, 0.6)]:
        d.ellipse([x + w * gx - 2, y + h * gy - 2, x + w * gx + 2,
                   y + h * gy + 2], fill=(250, 210, 110))
    d.ellipse([cx - 3, y - 1, cx + 3, y + 5], fill=(250, 220, 120))


def scene_market(d, x, y, w, h):
    _sky(d, x, y, w, h, "market")
    base = y + h * 0.85
    bars = [0.25, 0.45, 0.35, 0.6, 0.4]
    for i, bh in enumerate(bars):
        bx = x + 6 + i * (w - 12) // 5
        d.rectangle([bx, base - h * bh, bx + (w - 12) // 5 - 4, base],
                    fill=(214, 162, 42) if i == 3 else (150, 160, 190))
    d.line([x + 4, base, x + w - 4, base], fill=(255, 255, 255), width=2)
    d.line([x + w * 0.15, y + h * 0.55, x + w * 0.5, y + h * 0.30,
            x + w * 0.85, y + h * 0.45], fill=RED, width=2)
    d.polygon([(x + w * 0.85, y + h * 0.45), (x + w * 0.78, y + h * 0.42),
               (x + w * 0.82, y + h * 0.52)], fill=RED)


def scene_ship(d, x, y, w, h):
    _sky(d, x, y, w, h, "ship")
    d.polygon([(x + 6, y + h * 0.60), (x + w - 6, y + h * 0.60),
               (x + w - 18, y + h * 0.82), (x + 18, y + h * 0.82)],
              fill=(64, 68, 76))
    for i, c in enumerate([(186, 60, 40), (214, 162, 42), (60, 110, 140),
                           (46, 125, 80)]):
        cx = x + 12 + i * 18
        d.rectangle([cx, y + h * 0.40, cx + 15, y + h * 0.60], fill=c)
    _waves(d, x, y + h - 12, w, 12)


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


def scene_people(d, x, y, w, h):
    _sky(d, x, y, w, h, "people")
    for i, (px, s) in enumerate([(0.25, 1.0), (0.5, 1.15), (0.75, 1.0)]):
        cx = x + w * px
        r = 7 * s
        d.ellipse([cx - r, y + h * 0.30 - r, cx + r, y + h * 0.30 + r],
                  fill=(232, 196, 160))
        d.pieslice([cx - r * 1.6, y + h * 0.30 + r, cx + r * 1.6,
                    y + h * 0.30 + r * 4.4], 180, 360,
                   fill=(70 + i * 30, 90, 120))
    d.rectangle([x, y + h * 0.88, x + w, y + h], fill=(60, 58, 54))


def scene_money(d, x, y, w, h):
    _sky(d, x, y, w, h, "money")
    for i, (cx, cy, r) in enumerate([(0.30, 0.55, 12), (0.55, 0.45, 14),
                                     (0.78, 0.58, 11)]):
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=(214, 162, 42),
                  outline=(255, 235, 170), width=2)
        d.text((x + w * cx - 3, y + h * cy - 6), "$", font=F_BOLD(11),
               fill=(120, 84, 20))
    d.line([x + 6, y + h * 0.25, x + w - 6, y + h * 0.18], fill=(255, 255, 255),
           width=2)


def scene_health(d, x, y, w, h):
    _sky(d, x, y, w, h, "health")
    cx, cy = x + w / 2, y + h * 0.42
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(255, 255, 255))
    d.rectangle([cx - 3, cy - 9, cx + 3, cy + 9], fill=RED)
    d.rectangle([cx - 9, cy - 3, cx + 9, cy + 3], fill=RED)
    d.line([x + 6, y + h * 0.78, x + w * 0.35, y + h * 0.78,
            x + w * 0.45, y + h * 0.66, x + w * 0.55, y + h * 0.86,
            x + w * 0.65, y + h * 0.78, x + w - 6, y + h * 0.78],
           fill=(255, 255, 255), width=2)


def scene_sport(d, x, y, w, h):
    _sky(d, x, y, w, h, "sport")
    # trophy cup
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


def scene_missile(d, x, y, w, h):
    _sky(d, x, y, w, h, "missile")
    _stars(d, x, y, w, h, n=6, seed=5)
    d.line([x + w * 0.25, y + h * 0.85, x + w * 0.55, y + h * 0.30],
           fill=(255, 200, 120), width=2)
    mx, my = x + w * 0.58, y + h * 0.26
    d.polygon([(mx, my - 8), (mx + 5, my + 2), (mx - 5, my + 2)],
              fill=(240, 240, 240))
    d.rectangle([mx - 5, my + 2, mx + 5, my + 12], fill=(220, 220, 220))
    d.polygon([(mx - 5, my + 12), (mx - 9, my + 18), (mx - 2, my + 12)],
              fill=(200, 200, 200))
    d.polygon([(mx + 5, my + 12), (mx + 9, my + 18), (mx + 2, my + 12)],
              fill=(200, 200, 200))
    d.polygon([(mx - 3, my + 12), (mx, my + 22), (mx + 3, my + 12)],
              fill=(250, 180, 60))
    d.rectangle([x, y + h * 0.88, x + w, y + h], fill=(30, 34, 44))


def scene_bridge(d, x, y, w, h):
    _sky(d, x, y, w, h, "bridge")
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(70, 90, 120))
    d.arc([x + w * 0.10, y + h * 0.30, x + w * 0.90, y + h * 1.10], 180, 360,
          fill=(255, 255, 255), width=3)
    d.rectangle([x + w * 0.10, y + h * 0.66, x + w * 0.90, y + h * 0.74],
                fill=(240, 240, 240))
    for px in [0.2, 0.5, 0.8]:
        d.rectangle([x + w * px - 2, y + h * 0.66, x + w * px + 2,
                     y + h * 0.74], fill=(200, 200, 200))


def scene_exam(d, x, y, w, h):
    _sky(d, x, y, w, h, "exam")
    d.rectangle([x + w * 0.28, y + h * 0.14, x + w * 0.72, y + h * 0.86],
                fill=(255, 255, 255))
    for i in range(4):
        ly = y + h * (0.28 + i * 0.14)
        d.line([x + w * 0.34, ly, x + w * 0.66, ly], fill=(120, 120, 130),
               width=1)
    d.line([x + w * 0.34, y + h * 0.70, x + w * 0.50, y + h * 0.82,
            x + w * 0.66, y + h * 0.62], fill=(46, 125, 80), width=2)
    d.polygon([(x + w * 0.78, y + h * 0.30), (x + w * 0.86, y + h * 0.34),
               (x + w * 0.80, y + h * 0.62), (x + w * 0.76, y + h * 0.60)],
              fill=(214, 162, 42))


def scene_tech(d, x, y, w, h):
    _sky(d, x, y, w, h, "tech")
    d.rectangle([x + w * 0.18, y + h * 0.20, x + w * 0.82, y + h * 0.70],
                fill=(18, 28, 48), outline=(200, 210, 230), width=2)
    for i, ln in enumerate([0.55, 0.75, 0.45]):
        ly = y + h * (0.32 + i * 0.12)
        d.line([x + w * 0.24, ly, x + w * (0.24 + ln), ly],
               fill=(110, 200, 140), width=2)
    # padlock
    lx, ly = x + w * 0.62, y + h * 0.52
    d.arc([lx - 6, ly - 12, lx + 6, ly], 180, 360, fill=(250, 220, 120),
          width=2)
    d.rectangle([lx - 8, ly - 2, lx + 8, ly + 10], fill=(250, 220, 120))
    d.rectangle([x + w * 0.42, y + h * 0.70, x + w * 0.58, y + h * 0.80],
                fill=(150, 160, 180))


def scene_court(d, x, y, w, h):
    _sky(d, x, y, w, h, "court")
    d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(52, 48, 60))
    for i in range(3):
        cx = x + w * (0.22 + i * 0.28)
        d.rectangle([cx - 4, y + h * 0.30, cx + 4, y + h * 0.70],
                    fill=(240, 240, 240))
    d.rectangle([x + w * 0.12, y + h * 0.22, x + w * 0.88, y + h * 0.30],
                fill=(240, 240, 240))
    d.polygon([(x + w * 0.12, y + h * 0.22), (x + w * 0.50, y + h * 0.06),
               (x + w * 0.88, y + h * 0.22)], fill=(220, 220, 220))


def scene_rubble(d, x, y, w, h):
    _sky(d, x, y, w, h, "blast")
    # broken skyline with a smoke plume
    for i, bh in enumerate([0.42, 0.60, 0.34, 0.52]):
        bx = x + 6 + i * (w - 12) // 4
        bw = (w - 12) // 4 - 4
        d.rectangle([bx, y + h * (1 - bh), bx + bw, y + h * 0.92],
                    fill=(58, 52, 48))
        d.polygon([(bx, y + h * (1 - bh)), (bx + bw // 2,
                   y + h * (1 - bh) - 6), (bx + bw, y + h * (1 - bh))],
                  fill=(58, 52, 48))
    for i, r in enumerate([5, 8, 11]):
        cx = x + w * 0.72 + i * 3
        cy = y + h * 0.30 - i * 7
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(130, 128, 124))
    d.rectangle([x, y + h * 0.92, x + w, y + h], fill=(52, 40, 34))


def scene_bank(d, x, y, w, h):
    _sky(d, x, y, w, h, "money")
    cx = x + w / 2
    d.polygon([(cx - 20, y + h * 0.22), (cx, y + h * 0.08),
               (cx + 20, y + h * 0.22)], fill=(240, 240, 240))
    d.rectangle([cx - 20, y + h * 0.22, cx + 20, y + h * 0.30],
                fill=(240, 240, 240))
    for i in range(3):
        px = cx - 14 + i * 14
        d.rectangle([px - 3, y + h * 0.30, px + 3, y + h * 0.72],
                    fill=(230, 230, 230))
    d.rectangle([cx - 24, y + h * 0.72, cx + 24, y + h * 0.80],
                fill=(240, 240, 240))
    d.ellipse([cx - 8, y + h * 0.34, cx + 8, y + h * 0.50],
              fill=(214, 162, 42))
    d.text((cx - 3, y + h * 0.36), "$", font=F_BOLD(10), fill=(120, 84, 20))


def scene_rocket(d, x, y, w, h):
    _sky(d, x, y, w, h, "tech")
    # rising chart arrow
    d.line([x + 6, y + h * 0.75, x + w * 0.35, y + h * 0.60,
            x + w * 0.60, y + h * 0.66, x + w * 0.88, y + h * 0.22],
           fill=(110, 200, 140), width=3)
    d.polygon([(x + w * 0.88, y + h * 0.22), (x + w * 0.80, y + h * 0.22),
               (x + w * 0.88, y + h * 0.32)], fill=(110, 200, 140))
    for i, bh in enumerate([0.18, 0.30, 0.24, 0.42]):
        bx = x + 8 + i * (w - 16) // 4
        d.rectangle([bx, y + h * 0.88 - h * bh, bx + (w - 16) // 4 - 5,
                     y + h * 0.88], fill=(90, 130, 190))
    d.line([x + 4, y + h * 0.88, x + w - 4, y + h * 0.88],
           fill=(255, 255, 255), width=2)


SCENES = {
    "sparta": scene_sparta, "cop31": scene_cop31, "ukraine": scene_ukraine,
    "speech": scene_speech, "shield": scene_shield, "barrier": scene_barrier,
    "plane": scene_plane, "tree": scene_tree, "market": scene_market,
    "ship": scene_ship, "flags": scene_flags, "blast": scene_blast,
    "boat": scene_boat, "people": scene_people, "money": scene_money,
    "health": scene_health, "sport": scene_sport, "missile": scene_missile,
    "bridge": scene_bridge, "exam": scene_exam, "tech": scene_tech,
    "court": scene_court, "rubble": scene_rubble, "bank": scene_bank,
    "rocket": scene_rocket,
}

# ---------------------------------------------------------------- world map
# Schematic continents: coarse lon/lat outlines drawn by hand, good enough
# to read as a world map at 600 px wide. Red numbered dots mark the main
# stories by their card number.

LAND = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68), (-105, 68),
     (-95, 69), (-88, 68), (-82, 66), (-78, 71), (-72, 62), (-64, 60),
     (-56, 52), (-60, 47), (-66, 44), (-70, 42), (-74, 39), (-76, 35),
     (-80, 31), (-81, 26), (-84, 30), (-88, 29), (-91, 19), (-95, 19),
     (-97, 24), (-102, 25), (-106, 24), (-110, 23), (-114, 29), (-117, 33),
     (-122, 37), (-124, 42), (-124, 48), (-130, 55), (-140, 60), (-152, 58),
     (-162, 58), (-166, 60)],
    # South America
    [(-79, 8), (-75, 10), (-70, 12), (-64, 10), (-60, 8), (-54, 6), (-51, 4),
     (-50, 0), (-46, -2), (-40, -5), (-35, -8), (-37, -13), (-40, -20),
     (-46, -24), (-50, -29), (-54, -34), (-58, -38), (-63, -41), (-66, -45),
     (-68, -50), (-70, -54), (-73, -50), (-73, -40), (-72, -30), (-71, -20),
     (-75, -15), (-79, -8), (-81, -4), (-80, 1)],
    # Africa
    [(-17, 15), (-16, 21), (-13, 27), (-9, 31), (-5, 35), (0, 36), (8, 37),
     (11, 34), (15, 32), (20, 32), (25, 32), (30, 31), (32, 31), (35, 28),
     (38, 22), (40, 18), (43, 12), (48, 11), (51, 12), (50, 5), (46, 0),
     (42, -4), (40, -10), (39, -16), (36, -22), (33, -26), (31, -29),
     (27, -33), (20, -35), (17, -32), (15, -27), (13, -20), (12, -14),
     (10, -4), (9, 4), (4, 6), (-2, 5), (-8, 5), (-13, 8), (-17, 12)],
    # Europe + Asia
    [(-10, 36), (-9, 43), (-2, 48), (2, 51), (7, 54), (10, 58), (14, 56),
     (18, 56), (21, 55), (24, 59), (28, 61), (30, 66), (34, 68), (42, 68),
     (50, 69), (58, 69), (66, 70), (74, 73), (82, 74), (92, 76), (102, 77),
     (112, 74), (122, 73), (132, 72), (142, 72), (152, 70), (160, 69),
     (168, 66), (178, 65), (178, 62), (170, 61), (162, 56), (158, 52),
     (150, 59), (142, 54), (141, 48), (140, 40), (136, 36), (132, 34),
     (129, 32), (127, 36), (124, 40), (120, 36), (118, 30), (112, 22),
     (109, 18), (106, 10), (104, 9), (100, 8), (98, 12), (95, 16), (92, 21),
     (89, 22), (86, 20), (82, 16), (80, 13), (77, 8), (75, 12), (73, 18),
     (70, 20), (67, 24), (64, 25), (61, 25), (58, 26), (55, 26), (52, 26),
     (50, 29), (48, 30), (44, 29), (41, 31), (38, 32), (36, 36), (33, 36),
     (30, 36), (27, 37), (23, 36), (20, 40), (16, 44), (12, 44), (8, 44),
     (4, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37)],
    # Australia
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (136, -35), (139, -37), (140, -38), (145, -38), (148, -37),
     (150, -37), (153, -32), (153, -27), (150, -23), (146, -19), (143, -15),
     (142, -11), (140, -17), (137, -12), (135, -12), (132, -12), (130, -13),
     (127, -14), (124, -16), (121, -19), (118, -20), (115, -21)],
    # Japan, Britain, New Zealand (small)
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
     (141, 38), (141, 41), (142, 44), (140, 42), (139, 38), (137, 36),
     (135, 34), (132, 33)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 51)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38), (178, -37),
     (176, -40), (174, -41), (172, -43), (169, -46)],
]

MAP_DOTS = [
    (1, 24, 60), (3, 30, 50), (5, 12, 55), (7, 21, 52), (10, 56, 26),
    (13, 34, 31), (14, 6, 5), (16, 39, 9), (18, 15, -4), (20, 85, 28),
    (24, 175, -41), (29, -108, 25), (30, -48, -16),
]

MAP_LAT_TOP, MAP_LAT_BOT = 72, -52


def draw_map(d, x, y, w, h):
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=INK2)
    d.text((x + 10, y + 6), "WHERE IT HAPPENED", font=F_BOLD(9),
           fill=(180, 200, 225))
    for poly in LAND:
        pts = []
        for lon, lat in poly:
            px = x + (lon + 180) / 360 * w
            py = y + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * h
            pts.append((px, py))
        d.polygon(pts, fill=(232, 210, 170))
    for num, lon, lat in MAP_DOTS:
        px = x + (lon + 180) / 360 * w
        py = y + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * h
        num_disc(d, px, py, num, r=7, size=8)


# ---------------------------------------------------------------- layout
def hero_card(d, x, y, w, h, item):
    bg = tint(REGIONS[item["region"]], 0.90)
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=bg,
                        outline=LINE)
    # scene band
    SCENES[item["scene"]](d, x + 2, y + 2, w - 4, 104)
    num_disc(d, x + w - 18, y + 18, item["num"], r=12, size=12)
    if item.get("chip"):
        d.rounded_rectangle([x + 10, y + 76, x + 76, y + 100], radius=4,
                            fill=(255, 255, 255), outline=LINE)
        f = F_BOLD(15)
        tw = d.textlength(item["chip"], font=f)
        d.text((x + 43 - tw / 2, y + 80), item["chip"], font=f, fill=INK)
    d.text((x + 10, y + 112), item["kicker"], font=F_BOLD(9), fill=RED)
    lines = fit(d, item["title"], F_BOLD(17), w - 20, 2)
    block(d, x + 10, y + 126, lines, F_BOLD(17), INK, 20)
    lines = fit(d, item["body"], F_REG(10), w - 20, 3)
    block(d, x + 10, y + 168, lines, F_REG(10), (40, 44, 52), 13)
    d.text((x + 10, y + h - 14), "Source: " + item["source"],
           font=F_REG(8), fill=GREY)


def grid_card(d, x, y, w, h, item):
    bg = tint(REGIONS[item["region"]], 0.92)
    d.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=bg,
                        outline=LINE)
    SCENES[item["scene"]](d, x + 1, y + 1, w - 2, 30)
    num_disc(d, x + w - 11, y + 12, item["num"], r=8, size=8)
    if item.get("chip"):
        cw = 12 + 6 * len(item["chip"])
        d.rounded_rectangle([x + 4, y + 12, x + 4 + cw, y + 27], radius=3,
                            fill=(255, 255, 255), outline=LINE)
        f = F_BOLD(9)
        tw = d.textlength(item["chip"], font=f)
        d.text((x + 4 + (cw - tw) / 2, y + 15), item["chip"], font=f,
               fill=INK)
    d.text((x + 6, y + 33), item["kicker"], font=F_BOLD(7),
           fill=REGIONS[item["region"]])
    lines = fit(d, item["title"], F_BOLD(11), w - 12, 2)
    block(d, x + 6, y + 43, lines, F_BOLD(11), INK, 12)
    lines = fit(d, item["body"], F_REG(8), w - 12, 2)
    block(d, x + 6, y + 68, lines, F_REG(8), (52, 56, 64), 10)
    d.text((x + 6, y + h - 10), "Source: " + item["source"],
           font=F_REG(7), fill=GREY)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- masthead
    d.text((8, 8), "THE WORLD IN ONE DAY  \u2014  MORNING EDITION",
           font=F_BOLD(11), fill=RED)
    d.text((W - 8, 8), "33 STORIES  \u00b7  7 REGIONS  \u00b7  EVERY ONE DATED",
           font=F_BOLD(9), fill=GREY, anchor="ra")
    d.text((8, 26), "Sunday 22 November 2026", font=F_TITLE(52), fill=INK)
    d.text((8, 84),
           "COP31 deadlocked in overtime  \u00b7  Burning Russian ship towed "
           "from Finnish waters  \u00b7  Russia\u2019s biggest air assault "
           "of the year",
           font=F_SERIF(14), fill=(60, 64, 72))
    d.line([8, 102, W - 8, 102], fill=RED, width=2)

    # --- stat strip (navy band, white figures)
    d.rectangle([0, 104, W, 146], fill=INK)
    sw = W / len(STATS)
    for i, (big, label) in enumerate(STATS):
        cx = sw * i + sw / 2
        f1, f2 = F_BOLD(26), F_BOLD(8)
        tw = d.textlength(big, font=f1)
        d.text((cx - tw / 2, 108), big, font=f1, fill=(255, 255, 255))
        tw2 = d.textlength(label, font=f2)
        d.text((cx - tw2 / 2, 134), label, font=f2, fill=(170, 190, 215))
        if i:
            d.line([sw * i, 110, sw * i, 140], fill=(60, 80, 110), width=1)

    # --- region strip
    counts = {"EUROPE": 8, "AMERICAS": 6, "MIDDLE EAST": 4, "ASIA": 5,
              "AFRICA": 6, "OCEANIA": 1, "WORLD": 3}
    rw = (W - 16) / len(REGION_ORDER)
    for i, reg in enumerate(REGION_ORDER):
        x0 = 8 + i * rw
        d.rectangle([x0, 148, x0 + rw - 2, 168], fill=REGIONS[reg])
        txt = "%s %d" % (reg, counts[reg])
        f = F_BOLD(9)
        tw = d.textlength(txt, font=f)
        d.text((x0 + (rw - tw) / 2, 154), txt, font=f, fill=(255, 255, 255))

    # --- heroes
    hw, gap = 330, 9
    for i, hero in enumerate(HEROES):
        hero_card(d, 8 + i * (hw + gap), 170, hw, 216, hero)

    # --- grid: 6 cols x 5 rows
    gw, gh, gg = 163, 96, 6
    for r in range(5):
        for c in range(6):
            item = CARDS[r * 6 + c]
            grid_card(d, 8 + c * (gw + gg), 392 + r * (gh + 5), gw, gh, item)

    # --- bottom band: map + date check
    draw_map(d, 8, 890, 600, 92)
    bx0, by0 = 616, 890
    d.rounded_rectangle([bx0, by0, W - 8, by0 + 92], radius=6,
                        outline=RED, width=2, fill=(255, 255, 255))
    d.text((bx0 + 10, by0 + 6), "DATE CHECK", font=F_BOLD(10), fill=RED)
    dc_lines = []
    for sent in [
        "Every story above happened, or was first reported, on 20\u201322 "
        "November 2026 \u2014 the weekend\u2019s news as of Sunday morning.",
        "Nothing here is from before 13 November 2026.",
        "Later Sunday news (a COP31 deal, if one lands) is not in this "
        "picture.",
    ]:
        dc_lines.extend(wrap(d, sent, F_REG(9), W - 8 - bx0 - 20))
    block(d, bx0 + 10, by0 + 22, dc_lines, F_REG(9), (40, 44, 52), 12)

    # --- footer
    d.line([8, 988, W - 8, 988], fill=LINE, width=1)
    d.text((8, 994),
           "HOW WE CHECKED \u2014 Every story verified against BBC, Reuters, "
           "AP, AFP, CNN, national wires and official statements before "
           "drawing. Sources are named beside each story. Original drawings, "
           "not photographs.",
           font=F_REG(9), fill=(40, 44, 52))
    d.text((8, 1008),
           "Drawn in code for the make.fun news-image-20261122 competition  "
           "\u00b7  Morning edition \u2014 news to 07:30 WIB, Sunday 22 "
           "November 2026.",
           font=F_REG(8), fill=GREY)
    return img


def main():
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, optimize=True)
    print("wrote %s %dx%d" % (out, img.width, img.height))


if __name__ == "__main__":
    main()
