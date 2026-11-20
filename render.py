"""render.py — compose the 1024x1024 front page for news-image-20261120 (v3).

Blind rebuild: every line written fresh in this session from the written spec
and the story list. No previous entry code was read. All artwork is generated
procedurally with PIL inside this session (fixed seeds, deterministic).
"""
import hashlib
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
PAPER = (248, 244, 233)
PAPER_DARK = (238, 231, 214)
INK = (26, 23, 18)
INK_SOFT = (74, 68, 58)
RED = (178, 34, 28)
BLUE = (28, 64, 110)
GOLD = (176, 132, 40)
TEAL = (16, 96, 92)
RULE = (26, 23, 18)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(SANS, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to a pixel width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, text, path, start, max_w, min_size=8):
    """Largest font size (<= start) at which text fits max_w."""
    size = start
    while size > min_size:
        fnt = font(path, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        size -= 1
    return font(path, min_size)


def grain(img, seed, sigma=14, alpha=26):
    """Painterly grain: monochrome noise blended at low alpha."""
    noise = Image.effect_noise(img.size, sigma)
    noise = noise.convert("RGB")
    rnd = random.Random(seed)
    base = img.copy()
    base = Image.blend(base, Image.blend(base, noise, 0.5), alpha / 255.0)
    return base


def vgrad(w, h, top, bottom):
    """Vertical gradient image."""
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    return img


def hgrad(w, h, left, right):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for x in range(w):
        t = x / max(1, w - 1)
        c = tuple(int(left[i] + (right[i] - left[i]) * t) for i in range(3))
        for y in range(h):
            px[x, y] = c
    return img


def soft(img, radius=2):
    return img.filter(ImageFilter.GaussianBlur(radius))


# ---------------------------------------------------------------- stories
HEROES = [
    {
        "num": 1, "kicker": "CLIMATE \u2022 COP31 ANTALYA",
        "head": "COP31 draft drops every fossil-fuel mention",
        "deck": "144 paragraphs cut to 80; $120bn adaptation figure gone as talks run into overtime.",
        "art": "antalya",
    },
    {
        "num": 2, "kicker": "WEATHER \u2022 CYCLONE AKVAN",
        "head": "Akvan makes landfall; 300,000 evacuated",
        "deck": "Third cyclone in a month; gusts to 90 kph, 423 rescue teams out, 69 trains cancelled.",
        "art": "cyclone",
    },
    {
        "num": 3, "kicker": "MARKETS \u2022 AI SELLOFF",
        "head": "Dow sinks below 50,000 as AI fear spreads",
        "deck": "Dow 49,097, \u22122.19%; Nasdaq \u22122.25%; Asia plunges on bubble fears.",
        "art": "market",
    },
]

MEDIUMS = [
    ("Shenzhen morning-after: Kyiv holds line", "No deals without Kyiv, Zelensky says.", "skyline"),
    ("Kyiv hit by four ballistic missiles", "Bridges struck in overnight attack.", "flame"),
    ("UK sends 1,000+ drones to Ukraine", "\u00a3260m package announced in London.", "flags"),
    ("Riyadh PIF tower hit in Houthi attack", "Saudi defences down two drones.", "tower"),
    ("Tanker ablaze after mine east of Hormuz", "Fire crews battle blaze in Gulf waters.", "ship"),
    ("Israel pushes Gaza op past ceasefire line", "Hamas tunnel demolished, army says.", "dunes"),
    ("Europe ready for Russia talks", "Leaders signal opening to negotiations.", "bridge"),
    ("Poland probes unknown objects in sky", "Air-threat warning lifted after checks.", "radar"),
    ("Czech leaders visit Israel", "Prague delegation in Jerusalem.", "flags"),
    ("Tiger Woods to design NI golf course", "New course planned for Northern Ireland.", "green"),
]

ALSO_ON = [
    "Crimean Bridge hit for third time",
    "Kallas summons Russian envoy",
    "Genoa airport halts flights after drones",
    "Israeli strike on Hezbollah site in Lebanon",
    "US war with Iran would cost $48bn+",
    "Trump pardons Pete Rose",
    "US-China AI chips: Nvidia probe, 880k chips",
    "Taiwan stocks plunge 2,200 points",
    "Japan core inflation holds at 2.2%",
    "Quebecor in C$31bn bid for Telus",
    "Samsung names new mobile chief",
    "Meta revises 2030 climate targets",
    "Poland signs $50bn US nuclear deal",
    "UK-EU youth mobility scheme agreed",
    "Harris meets Macron in Paris",
    "Bukele files for third term",
    "Argentina Senate passes disability law 71-0",
    "Malawi fuel crisis turns violent",
    "Senegal boat capsizes; four dead",
    "Lula visits Chief Raoni",
    "Kirsten Davies named White House cyber chief",
    "New Caledonia quake 5.6 rattles islands",
    "Kirkland & Ellis did $11.8m free Trump work",
    "Chicago Hindu temple plot suspect pleads",
    "Anthropic retail: $772m traded on debut",
    "COP31 finance fight: Africa seeks triple",
    "US sanctions Comancheros, 'Ndrangheta",
]

KPIS = [
    ("DOW", "49,097", "\u22122.19%"),
    ("NASDAQ", "\u22122.25%", "AI FEAR"),
    ("ANTHROPIC IPO", "$81.3BN", "LARGEST EVER"),
    ("AKVAN", "300,000+", "EVACUATED"),
]

REGIONS = [
    ("EUROPE", 11), ("NORTH AMERICA", 9), ("MIDDLE EAST", 8),
    ("ASIA", 6), ("SOUTH AMERICA", 3), ("AFRICA", 2), ("OCEANIA", 1),
]

DATE_CHECK = (
    "DATE CHECK \u2014 All 40 stories were first reported Friday 20 November 2026. "
    "Not included (19 Nov): ICJ Myanmar ruling \u2022 Shenzhen summit \u2022 "
    "Anthropic debut \u2022 US Senate Iran war-powers vote (51\u201348)."
)

# (number, lon, lat) for the 13 illustrated stories, in story order.
PINS = [
    (1, 30.7, 36.9), (2, 109.0, 13.5), (3, -74.0, 40.7),
    (4, 114.0, 22.5), (5, 30.5, 50.4), (6, -0.1, 51.5),
    (7, 46.7, 24.6), (8, 56.5, 26.6), (9, 34.5, 31.4),
    (10, 4.4, 50.8), (11, 21.0, 52.2), (12, 35.2, 31.8),
    (13, -5.9, 54.6),
]

CONTINENTS = {
    "north_america": [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
        (-85, 70), (-75, 62), (-65, 60), (-55, 52), (-60, 47), (-70, 42),
        (-75, 35), (-80, 26), (-85, 20), (-90, 15), (-95, 18), (-105, 20),
        (-115, 30), (-125, 40), (-125, 48), (-135, 58), (-155, 60), (-168, 66)],
    "greenland": [(-55, 60), (-45, 60), (-40, 70), (-30, 76), (-55, 76), (-60, 70)],
    "south_america": [(-80, 10), (-75, 5), (-70, 0), (-60, -5), (-50, 0),
        (-40, -5), (-35, -10), (-40, -20), (-50, -30), (-60, -35), (-70, -45),
        (-75, -50), (-70, -55), (-75, -40), (-80, -25), (-80, -15), (-80, -5)],
    "africa": [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
        (35, 28), (40, 15), (48, 11), (51, 10), (45, 0), (40, -10), (35, -20),
        (30, -30), (20, -35), (15, -30), (12, -18), (9, -5), (9, 4),
        (-8, 4), (-13, 8), (-17, 15)],
    "europe": [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
        (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (25, 65),
        (20, 70), (15, 70), (10, 64), (5, 60), (0, 55), (-5, 50), (-8, 43), (-10, 36)],
    "asia": [(30, 62), (40, 68), (55, 68), (70, 72), (90, 75), (110, 76),
        (130, 72), (150, 70), (170, 66), (180, 65), (170, 60), (160, 55),
        (155, 50), (145, 45), (140, 40), (135, 35), (130, 30), (125, 25),
        (120, 20), (110, 15), (105, 10), (100, 5), (95, 10), (90, 15),
        (85, 20), (80, 15), (75, 10), (70, 20), (65, 25), (60, 25), (55, 25),
        (50, 28), (48, 30), (40, 35), (35, 36), (30, 36)],
    "australia": [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38),
        (150, -37), (153, -27), (150, -20), (146, -19), (142, -11), (136, -12),
        (132, -11), (126, -14), (122, -17), (118, -20), (113, -22)],
    "japan": [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (142, 42),
        (145, 44), (142, 45), (140, 40), (137, 37), (133, 34), (130, 31)],
    "uk": [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-2, 51), (-5, 50)],
}

# ---------------------------------------------------------------- art
def _sun_disc(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def _skyline_layer(w, h, seed, base_y, color, jag):
    """Dark building silhouette strip on its own layer (softened later)."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(seed)
    x = -10
    while x < w + 10:
        bw = rnd.randint(14, 42)
        bh = rnd.randint(18, jag)
        d.rectangle([x, base_y - bh, x + bw, base_y + 30], fill=color + (255,))
        if rnd.random() < 0.4:
            d.rectangle([x + bw // 3, base_y - bh - 8, x + 2 * bw // 3, base_y - bh], fill=color + (255,))
        x += bw + rnd.randint(2, 8)
    return soft(layer, 1)


def paint_antalya(w, h):
    """COP31 Antalya: sunset sky, sea band, coastal skyline, sun, gulls."""
    img = vgrad(w, h, (232, 148, 74), (242, 196, 120))
    d = ImageDraw.Draw(img, "RGBA")
    _sun_disc(d, int(w * 0.68), int(h * 0.30), 26, (250, 222, 150))
    d.ellipse([int(w * 0.68) - 40, int(h * 0.30) - 40, int(w * 0.68) + 40, int(h * 0.30) + 40],
              outline=(250, 210, 130, 90), width=3)
    sea = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sea)
    sea_y = int(h * 0.62)
    sd.rectangle([0, sea_y, w, h], fill=(24, 96, 118, 255))
    rnd = random.Random(11)
    for _ in range(26):
        y = sea_y + rnd.randint(4, h - sea_y - 4)
        x0 = rnd.randint(0, w - 60)
        sd.line([x0, y, x0 + rnd.randint(20, 70), y], fill=(255, 220, 160, 120), width=2)
    img = Image.alpha_composite(img.convert("RGBA"), soft(sea, 1)).convert("RGB")
    img.paste(_skyline_layer(w, h, 21, int(h * 0.64), (52, 32, 40), 46),
              (0, 0), _skyline_layer(w, h, 21, int(h * 0.64), (52, 32, 40), 46))
    d = ImageDraw.Draw(img, "RGBA")
    for gx, gy in [(int(w * 0.2), int(h * 0.18)), (int(w * 0.26), int(h * 0.14)), (int(w * 0.15), int(h * 0.24))]:
        d.arc([gx - 6, gy - 4, gx + 6, gy + 4], 200, 340, fill=(60, 40, 40, 200), width=2)
    return grain(img, 31)


def paint_cyclone(w, h):
    """Cyclone Akvan: dark storm sky, spiral cloud bands, rain, wave wall."""
    img = vgrad(w, h, (38, 62, 78), (16, 34, 52))
    d = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(22)
    cx, cy = int(w * 0.5), int(h * 0.46)
    for ring in range(6):
        r = 12 + ring * 13
        a0 = ring * 55
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 250,
              fill=(200, 214, 226, 150 - ring * 12), width=9 - ring)
    for _ in range(60):
        x = rnd.randint(0, w)
        y = rnd.randint(0, int(h * 0.6))
        d.line([x, y, x - 4, y + 14], fill=(180, 200, 220, 90), width=1)
    wave = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wave)
    base = int(h * 0.74)
    for k in range(4):
        y = base + k * 9
        pts = []
        for x in range(0, w + 20, 20):
            pts.append((x, y + int(6 * math.sin(x / 46.0 + k * 1.4))))
        wd.line(pts, fill=(120, 180, 200, 200), width=4)
        wd.line([(x, y + 8 + int(6 * math.sin(x / 46.0 + k * 1.4))) for x in range(0, w + 20, 20)],
                fill=(70, 130, 160, 160), width=3)
    img = Image.alpha_composite(img.convert("RGBA"), soft(wave, 1)).convert("RGB")
    return grain(img, 41)


def paint_market(w, h):
    """AI selloff: dark board, falling red chart, candlesticks, skyline base."""
    img = Image.new("RGB", (w, h), (18, 16, 22))
    d = ImageDraw.Draw(img, "RGBA")
    for gy in range(0, h, 22):
        d.line([0, gy, w, gy], fill=(255, 255, 255, 14), width=1)
    rnd = random.Random(33)
    x = 0
    price = int(h * 0.22)
    pts = []
    while x < w:
        pts.append((x, price))
        price += rnd.randint(2, 14)
        price = min(price, int(h * 0.86))
        x += rnd.randint(14, 26)
    d.line(pts, fill=(232, 52, 40, 255), width=4)
    for (px, py) in pts[::2]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 120, 100))
    for i in range(9):
        cx = 16 + i * (w - 32) // 9
        top = int(h * 0.30) + i * int(h * 0.05) + rnd.randint(-4, 8)
        bot = top + rnd.randint(10, 26)
        col = (232, 52, 40, 220) if i % 3 else (90, 200, 120, 220)
        d.rectangle([cx - 5, top, cx + 5, bot], fill=col)
        d.line([cx, top - 6, cx, bot + 6], fill=col, width=2)
    img = Image.alpha_composite(img.convert("RGBA"),
                                _skyline_layer(w, h, 44, h, (8, 8, 12), 40)).convert("RGB")
    return grain(img, 51)


def paint_medium(kind, w, h, seed):
    """Small illustrated strip for one medium story (motif by kind)."""
    rnd = random.Random(seed)
    palettes = {
        "skyline": ((214, 164, 96), (96, 60, 60), (52, 40, 52)),
        "flame": ((40, 30, 34), (214, 92, 40), (120, 30, 24)),
        "flags": ((36, 64, 110), (220, 220, 210), (178, 34, 28)),
        "tower": ((232, 190, 120), (70, 50, 44), (150, 110, 60)),
        "ship": ((24, 90, 110), (20, 50, 74), (220, 120, 50)),
        "dunes": ((236, 204, 140), (190, 140, 70), (120, 80, 40)),
        "bridge": ((70, 90, 120), (40, 54, 78), (220, 180, 90)),
        "radar": ((16, 60, 50), (60, 160, 110), (220, 230, 210)),
        "green": ((90, 150, 70), (50, 100, 50), (240, 240, 220)),
    }
    sky, mid, dark = palettes.get(kind, ((120, 120, 120), (80, 80, 80), (40, 40, 40)))
    img = vgrad(w, h, sky, mid)
    d = ImageDraw.Draw(img, "RGBA")
    if kind == "skyline":
        img = Image.alpha_composite(img.convert("RGBA"),
                                    _skyline_layer(w, h, seed + 5, h, dark, 26)).convert("RGB")
        d = ImageDraw.Draw(img, "RGBA")
        _sun_disc(d, int(w * 0.78), int(h * 0.30), 9, (250, 226, 150))
    elif kind == "flame":
        for i in range(5):
            fx = int(w * (0.15 + i * 0.17))
            fh = rnd.randint(12, 26)
            d.polygon([(fx - 8, h), (fx, h - fh), (fx + 8, h)], fill=(232, 120, 40, 220))
            d.polygon([(fx - 4, h), (fx, h - fh // 2), (fx + 4, h)], fill=(250, 210, 90, 220))
        d.rectangle([0, h - 4, w, h], fill=dark)
    elif kind == "flags":
        for i, col in enumerate([(178, 34, 28), (240, 240, 230), (36, 64, 110), (220, 180, 60)]):
            d.rectangle([i * w // 4, 0, (i + 1) * w // 4, h], fill=col + (210,))
        d.line([0, h // 2, w, h // 2], fill=(255, 255, 255, 120), width=2)
    elif kind == "tower":
        tx = w // 2
        d.polygon([(tx - 16, h), (tx - 6, 6), (tx + 6, 6), (tx + 16, h)], fill=dark)
        d.rectangle([tx - 3, 2, tx + 3, 12], fill=(250, 220, 120))
        for wy in range(14, h - 6, 8):
            d.rectangle([tx - 10, wy, tx + 10, wy + 3], fill=(250, 220, 120, 160))
    elif kind == "ship":
        d.rectangle([0, int(h * 0.62), w, h], fill=(20, 50, 74, 255))
        for k in range(2):
            y = int(h * 0.66) + k * 8
            d.line([(x, y + int(3 * math.sin(x / 30.0 + k))) for x in range(0, w + 10, 10)],
                   fill=(140, 200, 220, 200), width=2)
        hx = w // 3
        d.polygon([(hx, int(h * 0.60)), (hx + 70, int(h * 0.60)), (hx + 58, int(h * 0.78)), (hx + 12, int(h * 0.78))],
                  fill=(60, 40, 34))
        d.rectangle([hx + 26, int(h * 0.34), hx + 34, int(h * 0.60)], fill=(90, 60, 44))
        d.polygon([(hx + 34, int(h * 0.36)), (hx + 58, int(h * 0.48)), (hx + 34, int(h * 0.48))],
                  fill=(220, 120, 50))
    elif kind == "dunes":
        for k in range(3):
            y = int(h * (0.45 + k * 0.18))
            d.line([(x, y + int(5 * math.sin(x / 60.0 + k * 2))) for x in range(0, w + 10, 10)],
                   fill=(190 - k * 30, 140 - k * 20, 70, 255), width=6)
        _sun_disc(d, int(w * 0.8), int(h * 0.26), 8, (250, 230, 170))
    elif kind == "bridge":
        d.rectangle([0, int(h * 0.70), w, h], fill=dark)
        for tx in range(0, w, 34):
            d.line([tx, 4, tx, int(h * 0.70)], fill=(220, 180, 90, 200), width=2)
        d.line([0, int(h * 0.42), w, int(h * 0.30)], fill=(220, 180, 90, 230), width=3)
        d.line([0, int(h * 0.70), w, int(h * 0.70)], fill=(220, 180, 90, 255), width=3)
    elif kind == "radar":
        cx, cy = w // 2, h // 2 + 4
        for r in (10, 18, 26):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 220, 170, 220), width=2)
        d.line([cx, cy, cx + 22, cy - 14], fill=(220, 240, 220, 255), width=2)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(220, 240, 220))
        for _ in range(4):
            bx, by = rnd.randint(8, w - 8), rnd.randint(8, h - 8)
            d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=(250, 220, 120))
    elif kind == "green":
        d.rectangle([0, int(h * 0.55), w, h], fill=(60, 120, 60))
        for k in range(3):
            y = int(h * (0.60 + k * 0.13))
            d.line([(x, y + int(3 * math.sin(x / 40.0 + k))) for x in range(0, w + 10, 10)],
                   fill=(110, 180, 90, 200), width=3)
        fx, fy = int(w * 0.72), int(h * 0.72)
        d.line([fx, fy, fx - 16, fy - 26], fill=(240, 240, 220), width=2)
        d.polygon([(fx - 16, fy - 26), (fx - 4, fy - 22), (fx - 16, fy - 18)], fill=(220, 60, 50))
        d.ellipse([fx - 14, fy - 3, fx - 10, fy + 1], fill=(255, 255, 255))
    return grain(img, seed + 100)


HERO_PAINTERS = {"antalya": paint_antalya, "cyclone": paint_cyclone, "market": paint_market}

# ---------------------------------------------------------------- compose
def _lonlat_to_xy(lon, lat):
    x = 28 + (lon + 180.0) / 360.0 * 672.0
    y = 682 + (75.0 - lat) / 130.0 * 160.0
    return int(x), int(y)


def _text_center(d, cx, y, text, fnt, fill):
    w = d.textlength(text, font=fnt)
    d.text((cx - w / 2, y), text, font=fnt, fill=fill)


def compose(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    mx = 28
    rx = 996

    # ---- masthead
    title_f = fit_font(d, "THE WORLD IN ONE DAY", SERIF_B, 58, rx - mx)
    _text_center(d, W // 2, 24, "THE WORLD IN ONE DAY", title_f, INK)
    d.line([mx, 102, rx, 102], fill=RULE, width=3)
    d.line([mx, 106, rx, 106], fill=RULE, width=1)
    sub_f = font(SANS_B, 11)
    d.text((mx, 112 - 4), "FRIDAY 20 NOVEMBER 2026", font=sub_f, fill=INK)
    mid = "40 STORIES  \u2022  7 REGIONS  \u2022  13 ILLUSTRATED"
    _text_center(d, W // 2, 108, mid, sub_f, INK)
    right = "ALL STORIES FIRST REPORTED TODAY"
    d.text((rx - d.textlength(right, font=sub_f), 108), right, font=sub_f, fill=RED)

    # ---- KPI strip
    kpi_y, kpi_h, kpi_w, kpi_gap = 126, 42, 236, 8
    for i, (label, value, sub) in enumerate(KPIS):
        x0 = mx + i * (kpi_w + kpi_gap)
        d.rectangle([x0, kpi_y, x0 + kpi_w, kpi_y + kpi_h], outline=INK, width=1, fill=PAPER_DARK)
        d.text((x0 + 8, kpi_y + 4), label, font=font(SANS_B, 9), fill=INK_SOFT)
        vf = font(SANS_B, 16)
        d.text((x0 + 8, kpi_y + 18), value, font=vf, fill=INK)
        vw = d.textlength(value, font=vf)
        d.text((x0 + 12 + vw, kpi_y + 22), sub, font=font(SANS_B, 10), fill=RED)

    # ---- heroes
    hero_y, hero_h, hero_w, hero_gap = 178, 240, 314, 13
    art_h = 106
    for i, hero in enumerate(HEROES):
        x0 = mx + i * (hero_w + hero_gap)
        art = HERO_PAINTERS[hero["art"]](hero_w, art_h)
        img.paste(art, (x0, hero_y))
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse([x0 + 4, hero_y + 4, x0 + 26, hero_y + 26], fill=RED)
        _text_center(d, x0 + 15, hero_y + 7, str(hero["num"]), font(SANS_B, 12), (255, 255, 255))
        ky = hero_y + art_h + 8
        d.text((x0, ky), hero["kicker"], font=font(SANS_B, 10), fill=RED)
        hf = font(SERIF_B, 17)
        lines = wrap(d, hero["head"], hf, hero_w)[:2]
        hy = ky + 16
        for ln in lines:
            d.text((x0, hy), ln, font=hf, fill=INK)
            hy += 21
        df = font(SANS, 12)
        dlines = wrap(d, hero["deck"], df, hero_w)[:2]
        dy = hy + 4
        for ln in dlines:
            d.text((x0, dy), ln, font=df, fill=INK_SOFT)
            dy += 15
        d.line([x0, hero_y + hero_h - 6, x0 + hero_w, hero_y + hero_h - 6], fill=RULE, width=1)

    # ---- mediums (5 cols x 2 rows)
    med_y, med_h, med_w, med_gap = 428, 85, 185, 10
    med_art_h = 40
    for idx, (head, deck, kind) in enumerate(MEDIUMS):
        row, col = divmod(idx, 5)
        x0 = mx + col * (med_w + med_gap)
        y0 = med_y + row * med_h
        art = paint_medium(kind, med_w, med_art_h, 100 + idx * 7)
        img.paste(art, (x0, y0))
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse([x0 + 3, y0 + 3, x0 + 19, y0 + 19], fill=RED)
        _text_center(d, x0 + 11, y0 + 5, str(idx + 4), font(SANS_B, 10), (255, 255, 255))
        hf = font(SANS_B, 11)
        lines = wrap(d, head, hf, med_w)[:2]
        hy = y0 + med_art_h + 4
        for ln in lines:
            d.text((x0, hy), ln, font=hf, fill=INK)
            hy += 13
        d.text((x0, y0 + med_h - 12), deck, font=font(SANS, 9), fill=INK_SOFT)

    # ---- date-check box
    dc_y, dc_h = 606, 34
    d.rectangle([mx, dc_y, rx, dc_y + dc_h], outline=RED, width=2, fill=(252, 238, 228))
    dcf = font(SANS, 11)
    dlines = wrap(d, DATE_CHECK, dcf, rx - mx - 20)
    dy = dc_y + 4
    for ln in dlines[:2]:
        d.text((mx + 10, dy), ln, font=dcf, fill=INK)
        dy += 13

    # ---- map panel
    map_title_y = 648
    d.text((mx, map_title_y), "THE WORLD TODAY \u2014 13 STORIES PINNED",
           font=font(SANS_B, 13), fill=INK)
    note = "Pins 1\u201313 follow the illustrated stories above, in order."
    d.text((rx - d.textlength(note, font=font(SANS, 10)), map_title_y + 2),
           note, font=font(SANS, 10), fill=INK_SOFT)
    tl = ("ASIA MORNING \u2014 Akvan landfall  |  EUROPE MIDDAY \u2014 Kyiv strikes, COP31 draft  |  "
          "AMERICAS \u2014 Dow below 50,000  |  EVENING \u2014 COP31 overtime")
    d.text((mx, map_title_y + 18), tl, font=font(SANS, 9), fill=INK_SOFT)
    map_x0, map_y0, map_w, map_h = 28, 682, 672, 160
    d.rectangle([map_x0, map_y0, map_x0 + map_w, map_y0 + map_h],
                fill=(206, 224, 232), outline=INK, width=1)
    for gx in range(map_x0, map_x0 + map_w + 1, 84):
        d.line([gx, map_y0, gx, map_y0 + map_h], fill=(255, 255, 255, 60), width=1)
    for gy in range(map_y0, map_y0 + map_h + 1, 43):
        d.line([map_x0, gy, map_x0 + map_w, gy], fill=(255, 255, 255, 60), width=1)
    for name, poly in CONTINENTS.items():
        pts = [_lonlat_to_xy(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(232, 220, 188), outline=(150, 140, 110))

    # Parked badges: two columns right of the map, pitch 24 (>= 20 required).
    # Within each column badges are ordered by their pin's map-y so leader
    # lines fan out instead of crossing.
    # Cartographic displacement so crowded pin dots stay distinct (standard
    # map practice; leader lines point at the displaced dots).
    PIN_NUDGE = {6: (-4, 0), 9: (-9, 6), 10: (8, 0), 12: (8, -5), 13: (-6, -4)}
    pin_xy = {}
    for num, lon, lat in PINS:
        px, py = _lonlat_to_xy(lon, lat)
        nx, ny = PIN_NUDGE.get(num, (0, 0))
        pin_xy[num] = (px + nx, py + ny)
    badges = {}
    for col_idx, col_pins in enumerate([PINS[:7], PINS[7:]]):
        ordered = sorted(col_pins, key=lambda p: pin_xy[p[0]][1])
        bx = 748 if col_idx == 0 else 878
        for slot, (num, lon, lat) in enumerate(ordered):
            badges[num] = (bx, 690 + slot * 24)
    for num, lon, lat in PINS:
        px, py = pin_xy[num]
        bx, by = badges[num]
        d.line([bx - 9, by, px, py], fill=INK_SOFT, width=1)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED, outline=(255, 255, 255))
    for num, (bx, by) in badges.items():
        d.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=RED, outline=(255, 255, 255))
        _text_center(d, bx, by - 7, str(num), font(SANS_B, 11), (255, 255, 255))

    # ---- also-on
    ao_y = 856
    d.text((mx, ao_y), "ALSO ON \u2014 27 MORE STORIES", font=font(SANS_B, 11), fill=INK)
    reg = "EUROPE 11  \u00b7  N AMERICA 9  \u00b7  MIDEAST 8  \u00b7  ASIA 6  \u00b7  S AMERICA 3  \u00b7  AFRICA 2  \u00b7  OCEANIA 1"
    d.text((rx - d.textlength(reg, font=font(SANS, 9)), ao_y + 2),
           reg, font=font(SANS, 9), fill=INK_SOFT)
    ao_f = font(SANS, 10)
    ao_bf = font(SANS_B, 10)
    col_w = 303
    for idx, head in enumerate(ALSO_ON):
        col, row = divmod(idx, 9)
        x0 = mx + col * (col_w + 20)
        y0 = ao_y + 18 + row * 13
        num = str(idx + 14)
        d.text((x0, y0), num, font=ao_bf, fill=RED)
        nw = d.textlength(num + " ", font=ao_bf)
        d.text((x0 + nw, y0), head, font=ao_f, fill=INK)

    # ---- footer
    d.line([mx, 994, rx, 994], fill=RULE, width=1)
    foot = ("Sources: Reuters, AP, WSJ, CNN, BBC, Bloomberg and wire reports \u2014 "
            "all figures as reported 20 November 2026.")
    d.text((mx, 1000), foot, font=font(SANS, 9), fill=INK_SOFT)
    tag = "news-image-20261120 \u2022 @kanbara12"
    d.text((rx - d.textlength(tag, font=font(SANS, 9)), 1000), tag,
           font=font(SANS, 9), fill=INK_SOFT)

    img.save(path, format="PNG")
    return img


if __name__ == "__main__":
    compose("entry.png")
    data = open("entry.png", "rb").read()
    print(len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())
