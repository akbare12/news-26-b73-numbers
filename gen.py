#!/usr/bin/env python3
"""news-26 b73 — layout V71. Renders entry.png (1024x1024), 50 stories.
V71: masthead -> DATE CHECK 2 lines -> LEFT 45%: 3 hero bands stacked +
map strip below -> RIGHT 55%: cards 2x5 above + ALSO 3 cols below ->
timeline strip -> footer (tag legend + sources).
"""
import hashlib
import math
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DEJAVU_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

INK = (16, 20, 28)
PAPER = (250, 247, 238)
RED = (178, 34, 28)
BLUE = (18, 58, 110)
GOLD = (176, 124, 20)
TEAL = (14, 92, 84)
GREY = (92, 96, 104)
LIGHT = (232, 228, 218)
CARD_BG = (255, 255, 255)
HERO_BG = (255, 255, 255)
MAP_BG = (214, 228, 235)
LAND = (196, 205, 178)
LINE = (180, 174, 160)

_fcache = {}


def F(size, bold=False):
    key = (size, bold)
    if key not in _fcache:
        _fcache[key] = ImageFont.truetype(DEJAVU_B if bold else DEJAVU, size)
    return _fcache[key]


def text_w(text, font):
    b = font.getbbox(text)
    return b[2] - b[0]


def wrap(text, font, maxw):
    """Greedy wrap; returns list of lines, each fits maxw."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if text_w(cand, font) <= maxw or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, lines, x, y, font, fill, lh):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y

# ---------------------------------------------------------------- data
HEROES = [
    {
        "kicker": "NEW YORK  |  THANKSGIVING DAY",
        "head": "MACY'S 100TH PARADE POSTPONED",
        "deck": "First weather delay ever as a storm brings 60 mph gusts",
        "why": "WHY IT MATTERS: A centenary ritual halted by weather shows the storm's scale.",
        "stat": "RESCHEDULED SAT 28 NOV  |  08:30 ET",
        "art": "100TH",
        "art_sub": "FIRST DELAY EVER",
        "bg": (24, 64, 110),
        "tag": "[C]",
    },
    {
        "kicker": "STRAIT OF HORMUZ  |  IRAN WAR DAY 272",
        "head": "IRGC CLAIMS 2 TANKERS HIT BY MINES",
        "deck": "Supertanker carrying 2M barrels struck near Khasab, Iran says",
        "why": "WHY IT MATTERS: A mine claim in the key oil chokepoint lifts war risk fast.",
        "stat": "BRENT $93.8  |  +0.9% THU",
        "art": "2M",
        "art_sub": "BARRELS ABOARD",
        "bg": (122, 28, 20),
        "tag": "[CL]",
    },
    {
        "kicker": "GLOBAL MARKETS  |  TARIFF FALLOUT",
        "head": "TARIFF SHOCK FADES AS MARKETS REBOUND",
        "deck": "STOXX +1.6% as new levies look milder than feared",
        "why": "WHY IT MATTERS: Investors read the 14-partner salvo as negotiable, not war.",
        "stat": "14 PARTNERS  |  CHINA 20%",
        "art": "+1.6%",
        "art_sub": "STOXX 600",
        "bg": (14, 92, 84),
        "tag": "[C]",
    },
]

CARDS = [
    {"city": "DEIR AL-BALAH", "head": "GAZA STRIKE KILLS HAMAS EDUCATION DEPUTY",
     "deck": "Khaled Abu Nada and his wife killed in an overnight strike",
     "stat": "9 KILLED  |  3RD NIGHT", "tag": "[C]"},
    {"city": "KYIV", "head": "BALLISTIC MISSILES HIT KYIV MALL",
     "deck": "Desnianskyi mall struck as 113 drones fill the night sky",
     "stat": "7 HURT  |  113 DRONES", "tag": "[C]"},
    {"city": "BOGOR", "head": "FLOODED GOLD MINE KILLS 13 IN BOGOR",
     "deck": "Illegal mine floods 100m underground after heavy rain",
     "stat": "13 DEAD  |  13 MISSING", "tag": "[C]"},
    {"city": "JERUSALEM", "head": "JUDGE URGES DROP OF NETANYAHU BRIBERY CASE",
     "deck": "Prosecutors told to drop Case 4000, the only bribery charge",
     "stat": "CASE 4000", "tag": "[C]"},
    {"city": "PYONGYANG", "head": "KIM TOURS NUCLEAR PLANT, URGES TACTICAL ARMS",
     "deck": "North Korea's leader pushes wider tactical nuclear use",
     "stat": "TACTICAL PUSH", "tag": "[C]"},
    {"city": "WASHINGTON", "head": "FCC CLEARS SPACEX 1M ORBITAL DATA MODULES",
     "deck": "Starmind approval opens the first space data centres",
     "stat": "1M SATELLITES  |  25 NOV", "tag": "[CL]"},
    {"city": "LONDON", "head": "UK NET MIGRATION FALLS TO 77,000",
     "deck": "Lowest since 1997 outside the pandemic, ONS figures show",
     "stat": "77,000  |  LOWEST SINCE 1997", "tag": "[C]"},
    {"city": "MOSCOW", "head": "RUSSIA APPROVES RECORD MILITARY BUDGET",
     "deck": "Biggest post-Soviet defence budget clears the Duma",
     "stat": "RECORD BUDGET", "tag": "[C]"},
    {"city": "BANGKOK", "head": "BLAST AT BANGKOK OIL DEPOT INJURES 7",
     "deck": "Explosion triggers an evacuation alert; fire tamed in 30 minutes",
     "stat": "7 HURT", "tag": "[C]"},
    {"city": "COLOGNE", "head": "TWO HELD OVER SYNAGOGUE ATTACK PLOT",
     "deck": "Iraqi suspects arrested in Cologne and Heidelberg raids",
     "stat": "2 HELD", "tag": "[C]"},
]

# ALSO: 37 items, each (tag, text). [CL] items are 25 Nov events.
ALSO = [
    ("[C]", "Eisenkot seals coalition deal"),
    ("[C]", "Merz warns Russia's aims go beyond Ukraine"),
    ("[R]", "UK on drone alert at air bases"),
    ("[C]", "Norse Atlantic suspends all flights, warns of bankruptcy"),
    ("[C]", "Poundland enters administration; 11,000 jobs at risk"),
    ("[C]", "Malaysia sues Google for $146M over harmful content"),
    ("[C]", "Kenya court halts US-backed Ebola facility"),
    ("[C]", "Belarus offers to fly Zelensky to Moscow; he refuses"),
    ("[C]", 'Kushner calls Putin "historic figure", "grandmaster of politics"'),
    ("[C]", "Estonia decides to close border"),
    ("[C]", "Copernicus confirms longest stretch above 2\u00b0C warming"),
    ("[R]", "Nvidia halts AI server shipments to 4 countries"),
    ("[C]", "US Bitcoin funds hit record $4.94bn"),
    ("[CL]", "Houthi claim hits Ras Tanura refinery, 25 Nov"),
    ("[CL]", "Saudi downs 2 missiles headed for Riyadh, 25 Nov"),
    ("[CL]", "Jazan Port suffers minor damage in attacks, 25 Nov"),
    ("[CL]", "Eurostar walkout disrupts services, 25 Nov"),
    ("[CL]", "Syria Captagon seizure reported, 25 Nov"),
    ("[CL]", "Volker T\u00fcrk warns of atrocity crimes risk, 25 Nov"),
    ("[CL]", "Myanmar rejects ICJ ruling, 25 Nov"),
    ("[CL]", "UKMTO 223-26: tanker attacked east of Khasab, 25 Nov"),
    ("[CL]", "S&P 500 closes Wed -0.25%, Nasdaq -0.62%, 25 Nov"),
    ("[C]", "Guinea-Bissau delays election to Nov 2028"),
    ("[C]", "Babcock wins \u00a38bn nuclear submarine deal"),
    ("[C]", 'Zelensky to BBC: "US too focused on Middle East"'),
    ("[C]", "DR Congo Ebola outbreak reaches 12,021 cases"),
    ("[C]", "Kuwait drone strike kills 2 Italian technicians"),
    ("[C]", "Thanksgiving storm: 900,000+ lose power, 2,200+ flights delayed"),
    ("[C]", "Gold falls to $3,572/oz, down 8% in a month"),
    ("[C]", "Nvidia shares close -3.91% at $149.30"),
    ("[C]", "Ukraine drones damage 5 jets at Savasleyka base"),
    ("[C]", "UKMTO 222-26: blast near tanker west of Dubai"),
    ("[C]", "OPEC+ meets 29 Nov on 2027 output"),
    ("[C]", "Dollar flat at 103.71"),
    ("[C]", "Couple aged 37 and 38 killed in Kharkiv apartment strike"),
    ("[C]", "18 hurt in Kryvyi Rih strikes"),
    ("[C]", "Subkhankulovo pump station burns after drone hit"),
]

# Map pins: (label, lon, lat). 12 pins, real lon/lat of each story.
PINS = [
    ("NEW YORK", -74.0, 40.7),
    ("KHASAB", 56.25, 26.18),
    ("GAZA", 34.47, 31.5),
    ("BOGOR", 106.8, -6.6),
    ("PYONGYANG", 125.75, 39.03),
    ("LONDON", -0.12, 51.5),
    ("MOSCOW", 37.6, 55.75),
    ("BANGKOK", 100.5, 13.75),
    ("DELHI", 77.2, 28.6),
    ("KINSHASA", 15.3, -4.32),
    ("OSLO", 10.75, 59.9),
    ("NAIROBI", 36.8, -1.29),
]

TIMELINE = [
    ("00:30", "NIGHT STRIKES"),
    ("06:00", "MARKETS OPEN"),
    ("12:00", "MIDDAY BRIEF"),
    ("18:00", "EVENING WRAP"),
    ("23:00", "NIGHT BRIEF"),
]

DATE_L1 = "DATE CHECK  \u2014  THURSDAY 26 NOV 2026  \u00b7  50 STORIES IN THIS EDITION"
DATE_L2 = ("LEFT OUT: COP31 NO-DEAL (22 NOV)  \u00b7  DOW ABOVE 50,000 (24 NOV)  \u00b7  "
           "HUAWEI VERDICT (24 NOV)  \u00b7  [CL] ITEMS ARE 25 NOV EVENTS")

# Rough continent polygons in (lon, lat).
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-60, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21),
     (-97, 16), (-105, 20), (-115, 30), (-125, 40), (-140, 60), (-165, 60)],
    [(-80, 10), (-60, 10), (-50, 0), (-40, -5), (-35, -10), (-40, -20),
     (-50, -30), (-60, -38), (-70, -50), (-75, -40), (-75, -20), (-80, -5)],
    [(-10, 36), (-5, 44), (0, 50), (5, 58), (10, 58), (18, 56), (25, 60),
     (30, 62), (30, 70), (20, 70), (10, 65), (5, 60), (-2, 55), (-5, 50),
     (-9, 43), (-9, 37)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (48, 11), (51, 12), (40, 0), (35, -10), (30, -20), (20, -35),
     (15, -30), (12, -18), (13, -5), (9, 4), (-8, 5), (-15, 11)],
    [(35, 36), (45, 40), (55, 45), (60, 50), (70, 55), (80, 60), (90, 65),
     (100, 70), (120, 73), (140, 72), (160, 70), (170, 66), (160, 60),
     (150, 55), (140, 45), (130, 40), (127, 35), (120, 30), (110, 20),
     (105, 10), (100, 5), (95, 15), (90, 22), (80, 15), (75, 8), (70, 20),
     (60, 25), (55, 26), (50, 30), (45, 30), (40, 36)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (136, -12), (130, -13), (122, -14),
     (114, -21)],
]

# Layout geometry (1024x1024).
MX = 12
MASTHEAD = (0, 66)
DATEBOX = (66, 116)
MAIN_TOP = 124
MAIN_BOT = 892
LEFT_X0, LEFT_X1 = MX, 458
RIGHT_X0, RIGHT_X1 = 470, 1012
HERO_H = 168
HERO_GAP = 8
MAP_TOP = MAIN_TOP + 3 * HERO_H + 2 * HERO_GAP + 8
CARD_ROWS = 5
CARD_W = 265
CARD_H = 80
CARD_GAPX, CARD_GAPY = 12, 8
ALSO_TOP = MAIN_TOP + CARD_ROWS * CARD_H + (CARD_ROWS - 1) * CARD_GAPY + 8
TIMELINE_BOX = (900, 962)
FOOTER = (970, 1016)

# ---------------------------------------------------------------- render
FULL_TEXT = []  # every rendered story-bearing string, for asserts
LABEL_BOXES = []  # (x0, y0, x1, y1) final map label boxes
DOT_CENTERS = []  # (x, y) map dot centers
ART_LABELS = []  # (box, art box) hero art label geometry


def tag_color(tag):
    return {"[C]": (14, 92, 84), "[R]": (176, 124, 20), "[CL]": (178, 34, 28)}[tag]


def draw_masthead(d):
    d.rectangle([0, 0, W, MASTHEAD[1]], fill=INK)
    d.text((MX, 8), "THE WORLD IN ONE PAGE", font=F(30, True), fill=(250, 247, 238))
    d.text((MX, 42), "THURSDAY 26 NOVEMBER 2026", font=F(14, True), fill=(212, 175, 55))
    right = "50 STORIES  \u00b7  NEWS-IMAGE-20261126"
    d.text((W - MX - text_w(right, F(14, True)), 42), right, font=F(14, True),
           fill=(250, 247, 238))
    d.rectangle([0, MASTHEAD[1] - 3, W, MASTHEAD[1]], fill=RED)


def draw_datecheck(d):
    y0, y1 = DATEBOX
    d.rectangle([MX, y0, W - MX, y1], fill=(255, 252, 240), outline=LINE, width=1)
    d.rectangle([MX, y0, MX + 6, y1], fill=RED)
    f1, f2 = F(15, True), F(12)
    assert text_w(DATE_L1, f1) <= (W - 2 * MX - 24), "DATE L1 too wide"
    assert text_w(DATE_L2, f2) <= (W - 2 * MX - 24), "DATE L2 too wide"
    d.text((MX + 16, y0 + 5), DATE_L1, font=f1, fill=INK)
    d.text((MX + 16, y0 + 27), DATE_L2, font=f2, fill=(60, 60, 60))
    FULL_TEXT.append(DATE_L1)
    FULL_TEXT.append(DATE_L2)


def draw_hero(d, hero, y0):
    x0, x1 = LEFT_X0, LEFT_X1
    h = HERO_H
    d.rectangle([x0, y0, x1, y0 + h], fill=HERO_BG, outline=LINE, width=1)
    d.rectangle([x0, y0, x0 + 5, y0 + h], fill=hero["bg"])
    art_w = int((x1 - x0) * 0.30)
    ax0, ay0, ax1, ay1 = x0 + 10, y0 + 8, x0 + 10 + art_w, y0 + h - 8
    d.rectangle([ax0, ay0, ax1, ay1], fill=hero["bg"])
    # art decoration: diagonal rays, clamped in art box
    for i in range(5):
        yy = ay0 + 14 + i * 26
        d.line([(ax0, yy), (ax1, yy - 10)], fill=(255, 255, 255), width=2)
    # opaque chip under the big art label so no line touches glyphs
    lab_font = F(30, True)
    lab = hero["art"]
    lw = text_w(lab, lab_font)
    chip_w, chip_h = lw + 16, 44
    cx0 = ax0 + (art_w - chip_w) // 2
    cy0 = ay0 + (ay1 - ay0 - chip_h) // 2 - 8
    assert cx0 >= ax0 + 2 and cx0 + chip_w <= ax1 - 2, "art chip outside art box"
    assert cy0 >= ay0 + 2 and cy0 + chip_h <= ay1 - 2, "art chip outside art box"
    d.rectangle([cx0, cy0, cx0 + chip_w, cy0 + chip_h], fill=(255, 255, 255))
    d.text((cx0 + 8, cy0 + 5), lab, font=lab_font, fill=hero["bg"])
    ART_LABELS.append(((cx0, cy0, cx0 + chip_w, cy0 + chip_h), (ax0, ay0, ax1, ay1)))
    sub_font = F(10, True)
    sub = hero["art_sub"]
    assert text_w(sub, sub_font) <= art_w - 8, "art sub too wide"
    d.text((ax0 + (art_w - text_w(sub, sub_font)) // 2, ay1 - 22),
           sub, font=sub_font, fill=(255, 255, 255))
    # text column
    tx = ax1 + 12
    tw_ = x1 - 10 - tx
    d.text((tx, y0 + 8), hero["kicker"] + "  " + hero["tag"], font=F(10, True),
           fill=tag_color(hero["tag"]))
    head_lines = wrap(hero["head"], F(19, True), tw_)
    assert len(head_lines) <= 2, "hero head >2 lines: %s" % hero["head"]
    y = draw_lines(d, head_lines, tx, y0 + 26, F(19, True), INK, 23)
    deck_lines = wrap(hero["deck"], F(12), tw_)
    assert len(deck_lines) <= 2, "hero deck >2 lines"
    y = draw_lines(d, deck_lines, tx, y + 2, F(12), (40, 40, 40), 15)
    why_lines = wrap(hero["why"], F(11), tw_)
    assert len(why_lines) <= 2, "hero why >2 lines"
    why_bottom = draw_lines(d, why_lines, tx, y + 4, F(11), (60, 60, 60), 14)
    # divider above stat bar, must not touch text
    stat_y = y0 + h - 24
    assert stat_y - why_bottom >= 6, "WHY too close to stat bar"
    d.line([(tx, stat_y - 6), (x1 - 10, stat_y - 6)], fill=LINE, width=1)
    stat_font = F(12, True)
    assert text_w(hero["stat"], stat_font) <= tw_, "hero stat too wide"
    d.text((tx, stat_y), hero["stat"], font=stat_font, fill=hero["bg"])
    FULL_TEXT.extend([hero["kicker"], hero["head"], hero["deck"], hero["why"],
                  hero["stat"], hero["art"], hero["art_sub"]])


def draw_card(d, card, x0, y0):
    x1, y1 = x0 + CARD_W, y0 + CARD_H
    d.rectangle([x0, y0, x1, y1], fill=CARD_BG, outline=LINE, width=1)
    d.rectangle([x0, y0, x0 + 4, y1], fill=tag_color(card["tag"]))
    tx = x0 + 10
    tw_ = x1 - 8 - tx
    d.text((tx, y0 + 4), card["city"] + "  " + card["tag"], font=F(9, True),
           fill=tag_color(card["tag"]))
    head_lines = wrap(card["head"], F(13, True), tw_)
    assert len(head_lines) <= 2, "card head >2 lines: %s" % card["head"]
    y = draw_lines(d, head_lines, tx, y0 + 16, F(13, True), INK, 14)
    deck_lines = wrap(card["deck"], F(10), tw_)
    assert len(deck_lines) <= 2, "card deck >2 lines: %s" % card["head"]
    y = draw_lines(d, deck_lines, tx, y + 1, F(10), (50, 50, 50), 11)
    assert y + 11 <= y1 - 1, "card overflow: %s" % card["head"]
    d.text((tx, y1 - 12), card["stat"], font=F(10, True), fill=BLUE)
    FULL_TEXT.extend([card["city"], card["head"], card["deck"], card["stat"]])


def draw_also(d):
    x0, x1 = RIGHT_X0, RIGHT_X1
    y0 = ALSO_TOP
    d.rectangle([x0, y0, x1, MAIN_BOT], fill=(255, 252, 240), outline=LINE, width=1)
    d.text((x0 + 8, y0 + 6), "ALSO TODAY  \u2014  37 MORE STORIES", font=F(13, True), fill=INK)
    d.line([(x0 + 8, y0 + 26), (x1 - 8, y0 + 26)], fill=LINE, width=1)
    cols = [ALSO[i::3] for i in range(3)]
    col_w = (x1 - x0 - 16 - 2 * 10) // 3
    y_start = y0 + 34
    for ci, col in enumerate(cols):
        cx = x0 + 8 + ci * (col_w + 10)
        y = y_start
        for tag, text in col:
            full = tag + " " + text
            lines = wrap(full, F(9), col_w)
            assert len(lines) <= 2, "ALSO >2 lines: %s" % full
            y = draw_lines(d, lines, cx, y, F(9), (30, 30, 30), 10)
            y += 2
            assert y <= MAIN_BOT - 4, "ALSO overflow col %d" % ci
            FULL_TEXT.append(full)


def project(lon, lat, mx0, my0, mw, mh):
    # lon -180..180, lat -55..75
    x = mx0 + (lon + 180.0) / 360.0 * mw
    y = my0 + (75.0 - lat) / 130.0 * mh
    return x, y


def draw_map(d):
    x0, x1 = LEFT_X0, LEFT_X1
    y0, y1 = MAP_TOP, MAIN_BOT
    d.rectangle([x0, y0, x1, y1], fill=MAP_BG, outline=LINE, width=1)
    d.text((x0 + 8, y0 + 5), "WHERE IT HAPPENED  \u2014  12 PINS", font=F(12, True), fill=INK)
    mx0, my0 = x0 + 6, y0 + 26
    mw, mh = (x1 - x0 - 12), (y1 - y0 - 32)
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx0, my0, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=(150, 160, 130))
    font = F(9, True)
    dots = []
    for label, lon, lat in PINS:
        px, py = project(lon, lat, mx0, my0, mw, mh)
        dots.append((label, px, py))
    for (label, px, py) in dots:
        for (label2, qx, qy) in dots:
            if label2 <= label:
                continue
            dist = math.hypot(px - qx, py - qy)
            assert dist >= 18, "pins too close: %s/%s %.1f" % (label, label2, dist)
    # place each label: try 8 directions x 3 distances; keep >=17px centre-to-box
    # from EVERY dot (own dot included) and no overlap with placed labels
    for (label, px, py) in dots:
        lw = text_w(label, font)
        bw, bh = lw + 8, 15
        placed = None
        for dist in (18, 30, 42, 54, 66):
            cands = [
                (px + dist, py - bh / 2),
                (px - dist - bw, py - bh / 2),
                (px - bw / 2, py - dist - bh),
                (px - bw / 2, py + dist),
                (px + dist, py - dist - bh),
                (px - dist - bw, py - dist - bh),
                (px + dist, py + dist),
                (px - dist - bw, py + dist),
            ]
            for (bx, by) in cands:
                box = (bx, by, bx + bw, by + bh)
                if box[0] < mx0 or box[1] < my0 or box[2] > mx0 + mw or box[3] > my0 + mh:
                    continue
                ok = True
                for (label2, qx, qy) in dots:
                    dx = max(box[0] - qx, 0, qx - box[2])
                    dy = max(box[1] - qy, 0, qy - box[3])
                    if math.hypot(dx, dy) < 17:
                        ok = False
                        break
                if ok:
                    for (ox0, oy0, ox1, oy1) in LABEL_BOXES:
                        if not (box[2] < ox0 or box[0] > ox1 or
                                box[3] < oy0 or box[1] > oy1):
                            ok = False
                            break
                if ok:
                    placed = box
                    break
            if placed is not None:
                break
        assert placed is not None, "no label placement for %s" % label
        LABEL_BOXES.append(placed)
        d.rectangle(placed, fill=(255, 255, 255), outline=INK, width=1)
        d.text((placed[0] + 4, placed[1] + 2), label, font=font, fill=INK)
    for (label, px, py) in dots:
        DOT_CENTERS.append((px, py))
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=2)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255))


def draw_timeline(d):
    y0, y1 = TIMELINE_BOX
    d.rectangle([MX, y0, W - MX, y1], fill=INK)
    d.text((MX + 10, y0 + 6), "THURSDAY 26 NOV  \u2014  THE DAY IN FIVE BEATS",
           font=F(12, True), fill=(212, 175, 55))
    seg_w = (W - 2 * MX - 20) / len(TIMELINE)
    for i, (t, label) in enumerate(TIMELINE):
        cx = MX + 10 + i * seg_w + seg_w / 2
        d.ellipse([cx - 4, y0 + 30, cx + 4, y0 + 38], fill=(212, 175, 55))
        if i:
            d.line([(cx - seg_w / 2, y0 + 34), (cx - 4, y0 + 34)],
                   fill=(212, 175, 55), width=2)
        tt = t + "  " + label
        assert text_w(tt, F(10, True)) <= seg_w - 6, "timeline label too wide"
        d.text((cx - text_w(tt, F(10, True)) / 2, y0 + 42), tt,
               font=F(10, True), fill=(250, 247, 238))
        FULL_TEXT.append(tt)


def draw_footer(d):
    y0, y1 = FOOTER
    d.rectangle([MX, y0, W - MX, y1], fill=(255, 252, 240), outline=LINE, width=1)
    legend = "[C] CONFIRMED   \u00b7   [R] REPORTED   \u00b7   [CL] CLAIM / 25 NOV EVENT"
    d.text((MX + 10, y0 + 6), legend, font=F(12, True), fill=INK)
    src = "SOURCES: REUTERS  \u00b7  AP  \u00b7  BBC  \u00b7  CNN  \u00b7  UKMTO  \u00b7  ONS  \u00b7  KCNA"
    d.text((MX + 10, y0 + 24), src, font=F(10), fill=(60, 60, 60))
    right = "50 STORIES"
    d.text((W - MX - 10 - text_w(right, F(12, True)), y0 + 6), right,
           font=F(12, True), fill=RED)
    FULL_TEXT.append(legend)
    FULL_TEXT.append(src)


# ---------------------------------------------------------------- asserts
STOP = set("""a an the and or of to in on for at by with from as is are was were be
been it its this that these those not no nor but if then than so such into over
under after before between through during per via he she they we you i his her
their our your my me him us them who what when where which while all any both
each few more most other some own same too very can will just should now
nov 25 26 2026 thu thursday wed wednesday""".split())

NUM_RE = re.compile(r"\$?\d+(?:\.\d+)?%?")


def norm_num(tok):
    m = NUM_RE.fullmatch(tok)
    if m:
        try:
            v = float(tok.replace("$", "").replace("%", ""))
            return "N%.2f" % v
        except ValueError:
            return tok
    return tok


def distinctive(text):
    toks = re.findall(r"[a-z0-9$%.]+", text.lower())
    out = set()
    for t in toks:
        if NUM_RE.fullmatch(t):
            continue  # bare numbers (incl. advisory no. fragments) are not distinctive
        t = norm_num(t)
        if t in STOP or len(t) < 3:
            continue
        out.add(t)
    return out


def assert_all(img):
    full = "\n".join(FULL_TEXT)
    low = full.lower()
    assert "third senior" not in low and "3rd senior" not in low, "banned phrase"
    assert "bangchak" not in low, "banned word Bangchak"
    assert low.count("ras tanura") == 1, "Ras Tanura count %d" % low.count("ras tanura")
    assert low.count("riyadh") <= 1, "Riyadh count %d" % low.count("riyadh")
    assert "\u2026" not in full, "ellipsis present (silent truncation)"
    assert "every story below happened" not in low, "dishonest DATE CHECK claim"
    # counts: 3 hero + 10 cards + 37 ALSO
    assert len(HEROES) == 3 and len(CARDS) == 10 and len(ALSO) == 37
    # every card + ALSO bears a tag; 25 Nov items bear [CL]
    for c in CARDS:
        assert c["tag"] in ("[C]", "[R]", "[CL]"), c["head"]
        if "25 nov" in (c["deck"] + c["stat"]).lower():
            assert c["tag"] == "[CL]", c["head"]
    for tag, text in ALSO:
        assert tag in ("[C]", "[R]", "[CL]"), text
        if "25 nov" in text.lower():
            assert tag == "[CL]", text
    # left-out items must appear exactly once (only inside DATE CHECK)
    for phrase in ("cop31", "dow above 50,000", "huawei verdict"):
        assert low.count(phrase) == 1, "left-out phrase count %s=%d" % (
            phrase, low.count(phrase))
    # dup scan over story corpus (hero head/deck/why/stat + card + ALSO)
    items = []
    for h in HEROES:
        items.append(("hero:" + h["head"], h["head"] + " " + h["deck"] + " " +
                      h["why"] + " " + h["stat"]))
    for c in CARDS:
        items.append(("card:" + c["head"], c["head"] + " " + c["deck"] + " " + c["stat"]))
    for tag, text in ALSO:
        items.append(("also:" + text, text))
    sets = [(name, distinctive(t)) for name, t in items]
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            shared = sets[i][1] & sets[j][1]
            assert len(shared) < 3, "dup %s <-> %s shared=%s" % (
                sets[i][0], sets[j][0], sorted(shared))
    # art labels fully inside art boxes, >=2px from edges
    for (lab_box, art_box) in ART_LABELS:
        assert lab_box[0] >= art_box[0] + 2 and lab_box[1] >= art_box[1] + 2
        assert lab_box[2] <= art_box[2] - 2 and lab_box[3] <= art_box[3] - 2
    # pixel scan: 0 red pixels inside map label boxes
    px = img.load()
    for (x0, y0, x1, y1) in LABEL_BOXES:
        for xx in range(int(x0), int(x1)):
            for yy in range(int(y0), int(y1)):
                r, g, b = px[xx, yy][:3]
                assert not (r > 150 and g < 90 and b < 90), \
                    "red pixel inside map label at %d,%d" % (xx, yy)
    # WHY ends with '.'
    for h in HEROES:
        assert h["why"].rstrip().endswith("."), "WHY must end with '.'"
        assert h["why"].startswith("WHY IT MATTERS:"), "WHY label missing"
    print("ASSERTS OK: heroes=%d cards=%d also=%d pins=%d" %
          (len(HEROES), len(CARDS), len(ALSO), len(PINS)))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_datecheck(d)
    y = MAIN_TOP
    for h in HEROES:
        draw_hero(d, h, y)
        y += HERO_H + HERO_GAP
    draw_map(d)
    for i, c in enumerate(CARDS):
        cx = RIGHT_X0 + (i % 2) * (CARD_W + CARD_GAPX)
        cy = MAIN_TOP + (i // 2) * (CARD_H + CARD_GAPY)
        draw_card(d, c, cx, cy)
    draw_also(d)
    draw_timeline(d)
    draw_footer(d)
    assert_all(img)
    img.save(OUT)
    data = open(OUT, "rb").read()
    print("WROTE %s %d bytes sha256=%s" %
          (OUT, len(data), hashlib.sha256(data).hexdigest()))
    print("COUNTS: 3 hero + 10 cards + 37 also = 50 stories")


if __name__ == "__main__":
    main()
