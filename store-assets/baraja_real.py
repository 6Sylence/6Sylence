#!/usr/bin/env python3
# Cápsula Baraja Real — royal playing-card capsule for Street Royalty Hood.
# 6 print files (one per product), rendered at 2x and downsampled for clean edges.
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

NEGRO   = (14, 13, 16, 255)
CARBON  = (26, 24, 28, 255)
CREMA   = (242, 234, 217, 255)
MARFIL  = (246, 241, 230, 255)
ARENA   = (216, 198, 160, 255)
ORO     = (201, 164, 76, 255)
ORO_HI  = (232, 202, 122, 255)
ORO_LO  = (150, 118, 52, 255)
BURDEOS = (94, 26, 38, 255)
BURDEOS_HI = (136, 44, 58, 255)
NAVY    = (26, 34, 56, 255)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def F(p, s): return ImageFont.truetype(p, int(s))

# ---------------------------------------------------------------- suit geometry
def heart_pts(cx, cy, s, flip=False):
    pts = []
    for i in range(120):
        t = 2 * math.pi * i / 120
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        if flip: y = -y
        pts.append((cx + x * s / 17.0, cy - y * s / 17.0))
    return pts

def stem_pts(cx, top_y, base_y, half_top, half_base):
    """Flared stem with concave sides (quadratic curves)."""
    left, right = [], []
    for i in range(21):
        t = i / 20
        y = top_y + (base_y - top_y) * t
        # concave flare: narrow at top, wide at base
        half = half_top + (half_base - half_top) * (t ** 2.2)
        left.append((cx - half, y)); right.append((cx + half, y))
    return left + right[::-1]

def draw_spade(d, cx, cy, s, fill):
    d.polygon(heart_pts(cx, cy - s * 0.10, s * 0.92, flip=True), fill=fill)
    d.polygon(stem_pts(cx, cy + s * 0.10, cy + s * 0.62, s * 0.045, s * 0.34), fill=fill)

def draw_heart(d, cx, cy, s, fill):
    d.polygon(heart_pts(cx, cy, s), fill=fill)

def draw_diamond(d, cx, cy, s, fill):
    w, h = s * 0.72, s * 1.0
    pts = []
    corners = [(cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy)]
    for i in range(4):
        x0, y0 = corners[i]; x1, y1 = corners[(i + 1) % 4]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        # bow sides slightly outward
        vx, vy = mx - cx, my - cy
        n = math.hypot(vx, vy) or 1
        mx, my = mx + vx / n * s * 0.06, my + vy / n * s * 0.06
        for t in [k / 12 for k in range(12)]:
            a = (1 - t) ** 2; b = 2 * (1 - t) * t; c = t ** 2
            pts.append((a * x0 + b * mx + c * x1, a * y0 + b * my + c * y1))
    d.polygon(pts, fill=fill)

def draw_club(d, cx, cy, s, fill):
    r = s * 0.40
    for ang in (-90, 30, 150):
        a = math.radians(ang)
        d.ellipse([cx + math.cos(a) * r * 0.98 - r, cy + math.sin(a) * r * 0.98 - r,
                   cx + math.cos(a) * r * 0.98 + r, cy + math.sin(a) * r * 0.98 + r], fill=fill)
    d.polygon(stem_pts(cx, cy + s * 0.08, cy + s * 0.62, s * 0.05, s * 0.32), fill=fill)

SUITS = {"spade": draw_spade, "heart": draw_heart, "diamond": draw_diamond, "club": draw_club}

def crown_pts(cx, cy, w, h):
    l = cx - w / 2; r = cx + w / 2; b = cy + h / 2; t = cy - h / 2
    dipy = b - h * 0.42
    pts = [(l, b), (l, t + h * 0.30), (l + w * 0.185, dipy),
           (cx - w * 0.155, t + h * 0.12), (cx, dipy - h * 0.02),
           (cx + w * 0.155, t + h * 0.12), (r - w * 0.185, dipy),
           (r, t + h * 0.30), (r, b)]
    band = (l, b + h * 0.06, r, b + h * 0.16)
    return pts, band

def draw_crown(d, cx, cy, w, h, fill, jewels=None):
    pts, band = crown_pts(cx, cy, w, h)
    d.polygon(pts, fill=fill)
    d.rectangle(band, fill=fill)
    if jewels:
        for jx, jy in [(cx - w * 0.5, cy - h * 0.20), (cx, cy - h * 0.44), (cx + w * 0.5, cy - h * 0.20)]:
            r = h * 0.075
            d.ellipse([jx - r, jy - r, jx + r, jy + r], fill=jewels)

def text_tracked(d, xy, text, font, fill, tracking=0, center=False):
    x, y = xy
    widths = [d.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if center: x -= total / 2
    for c, cw in zip(text, widths):
        d.text((x, y), c, font=font, fill=fill)
        x += cw + tracking
    return total

def finish(img, w, h):
    return img.resize((w, h), Image.LANCZOS)

# ---------------------------------------------------------------- 1. Camiseta — "Baraja Real" (2400x3200 transparent)
def tee():
    W, H = 4800, 6400
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # ornate card frame
    m = 260
    d.rounded_rectangle([m, m, W - m, H - m], radius=340, outline=ORO, width=26)
    d.rounded_rectangle([m + 90, m + 90, W - m - 90, H - m - 90], radius=270, outline=ORO_LO, width=10)
    # corner indices: K + spade
    fK = F(SERIF_B, 560)
    for (ix, iy, rot) in [(m + 220, m + 170, 0), (W - m - 220, H - m - 170, 180)]:
        tile = Image.new("RGBA", (900, 1350), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        td.text((450, 330), "K", font=fK, fill=CREMA, anchor="mm")
        draw_spade(td, 450, 950, 260, ORO)
        if rot: tile = tile.rotate(180)
        img.alpha_composite(tile, (int(ix - 450), int(iy - 170 if rot == 0 else iy - 1180)))
    # center: crowned spade with engraved bands
    cx, cy = W / 2, H * 0.455
    S = W * 0.255
    spade_mask = Image.new("L", (W, H), 0)
    smd = ImageDraw.Draw(spade_mask)
    draw_spade(smd, cx, cy, S, 255)
    # engraved horizontal bands inside the spade (gold gradient stripes)
    engraved = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(engraved)
    y0, y1 = cy - S * 1.1, cy + S * 0.75
    n = 38
    for i in range(n):
        t = i / (n - 1)
        yy = y0 + (y1 - y0) * t
        th = 14 + 30 * (0.5 + 0.5 * math.sin(t * math.pi))
        col = tuple(int(ORO[k] + (ORO_HI[k] - ORO[k]) * (0.5 + 0.5 * math.sin(t * 6.0))) for k in range(3)) + (255,)
        ed.rectangle([cx - S * 1.2, yy, cx + S * 1.2, yy + th], fill=col)
    img.paste(engraved, (0, 0), Image.composite(spade_mask, Image.new("L", (W, H), 0), spade_mask))
    # spade outline
    d.polygon(heart_pts(cx, cy - S * 0.10, S * 0.92, flip=True), outline=CREMA, width=16)
    d.polygon(stem_pts(cx, cy + S * 0.10, cy + S * 0.62, S * 0.045, S * 0.34), outline=CREMA, width=16)
    # crown over spade
    draw_crown(d, cx, cy - S * 1.28, S * 1.05, S * 0.52, CREMA, jewels=BURDEOS_HI)
    # flourish rules
    for sx in (-1, 1):
        x0 = cx + sx * S * 1.35; x1 = cx + sx * S * 2.35
        d.line([x0, cy, x1, cy], fill=ORO, width=12)
        d.ellipse([x1 - 26, cy - 26, x1 + 26, cy + 26], outline=ORO, width=10)
        for k, suit in enumerate(["heart", "diamond", "club"]):
            SUITS[suit](d, x0 + sx * (k + 0.55) * (x1 - x0) / 3.6, cy - S * 0.34, S * 0.11,
                        ORO if suit != "heart" else BURDEOS_HI)
    # lettering
    text_tracked(d, (W / 2, H * 0.685), "BARAJA REAL", F(SERIF_B, 300), CREMA, tracking=44, center=True)
    text_tracked(d, (W / 2, H * 0.742), "LA CORTE DE LA CALLE · EST. MMXXVI", F(SANS, 96), ARENA, tracking=32, center=True)
    # bottom banner
    text_tracked(d, (W / 2, H * 0.815), "STREET ROYALTY HOOD", F(SANS_B, 110), ORO, tracking=48, center=True)
    return finish(img, 2400, 3200)

# ---------------------------------------------------------------- 2. Hoodie Premium — "Rey de Picas" (1800x1800 transparent)
def hoodie():
    W = 3600
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    half = Image.new("RGBA", (W, W // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(half)
    cx = W / 2
    # crowned half-spade emblem (court-card style, mirrored later)
    S = W * 0.155
    cy = W * 0.335
    draw_spade(d, cx, cy, S, ORO)
    d.polygon(heart_pts(cx, cy - S * 0.10, S * 0.66, flip=True), fill=CARBON)
    draw_spade(d, cx, cy + S * 0.02, S * 0.42, ORO_HI)
    draw_crown(d, cx, cy - S * 1.30, S * 1.15, S * 0.56, CREMA, jewels=BURDEOS_HI)
    # side pips + rank letters
    fR = F(SERIF_B, 300)
    d.text((cx - S * 2.6, cy - S * 0.55), "K", font=fR, fill=CREMA, anchor="mm")
    d.text((cx + S * 2.6, cy - S * 0.55), "K", font=fR, fill=CREMA, anchor="mm")
    draw_spade(d, cx - S * 2.6, cy + S * 0.42, S * 0.26, ORO)
    draw_spade(d, cx + S * 2.6, cy + S * 0.42, S * 0.26, ORO)
    # arc caption
    text_tracked(d, (cx, W * 0.028), "· REY DE PICAS ·", F(SANS_B, 128), CREMA, tracking=42, center=True)
    img.alpha_composite(half, (0, 0))
    img.alpha_composite(half.rotate(180), (0, W // 2))
    # divider band
    d2 = ImageDraw.Draw(img)
    d2.line([W * 0.09, W / 2, W * 0.91, W / 2], fill=ORO, width=14)
    for k in range(7):
        x = W * 0.20 + k * W * 0.10
        suit = ["spade", "diamond", "club", "heart", "club", "diamond", "spade"][k]
        SUITS[suit](d2, x, W / 2, W * 0.024, BURDEOS_HI if suit == "heart" else ORO_HI)
    return finish(img, 1800, 1800)

# ---------------------------------------------------------------- 3. Sudadera — "Escalera Real" (2400x3000 transparent)
def card_face(rank, wpx, hpx):
    c = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 0, wpx - 1, hpx - 1], radius=int(wpx * 0.12), fill=MARFIL,
                        outline=NEGRO, width=max(6, wpx // 60))
    d.rounded_rectangle([int(wpx*0.07), int(wpx*0.07), wpx - int(wpx*0.07), hpx - int(wpx*0.07)],
                        radius=int(wpx * 0.08), outline=ORO_LO, width=max(4, wpx // 110))
    fR = F(SERIF_B, wpx * 0.24)
    d.text((wpx * 0.17, hpx * 0.115), rank, font=fR, fill=NEGRO, anchor="mm")
    draw_spade(d, wpx * 0.17, hpx * 0.235, wpx * 0.085, NEGRO)
    if rank == "K":
        draw_crown(d, wpx / 2, hpx * 0.44, wpx * 0.42, hpx * 0.13, ORO, jewels=BURDEOS_HI)
        draw_spade(d, wpx / 2, hpx * 0.62, wpx * 0.19, NEGRO)
    elif rank == "Q":
        draw_crown(d, wpx / 2, hpx * 0.45, wpx * 0.36, hpx * 0.10, ORO_HI, jewels=BURDEOS_HI)
        draw_heart(d, wpx / 2, hpx * 0.62, wpx * 0.18, BURDEOS_HI)
    elif rank == "J":
        d.polygon([(wpx*0.5, hpx*0.36), (wpx*0.63, hpx*0.52), (wpx*0.5, hpx*0.68), (wpx*0.37, hpx*0.52)], outline=NEGRO, width=max(6, wpx // 55))
        draw_spade(d, wpx / 2, hpx * 0.52, wpx * 0.115, NEGRO)
    elif rank == "A":
        draw_spade(d, wpx / 2, hpx * 0.53, wpx * 0.26, NEGRO)
        draw_spade(d, wpx / 2, hpx * 0.515, wpx * 0.15, ORO)
    else:  # 10
        for iy in range(2):
            for ix in range(2):
                draw_spade(d, wpx * (0.38 + 0.24 * ix), hpx * (0.44 + 0.16 * iy), wpx * 0.085, NEGRO)
        draw_spade(d, wpx / 2, hpx * 0.60 + hpx * 0.06, wpx * 0.085, NEGRO)
    # bottom index rotated
    idx = Image.new("RGBA", (int(wpx*0.34), int(hpx*0.26)), (0,0,0,0))
    idd = ImageDraw.Draw(idx)
    idd.text((idx.width/2, idx.height*0.30), rank, font=fR, fill=NEGRO, anchor="mm")
    draw_spade(idd, idx.width/2, idx.height*0.76, wpx*0.085, NEGRO)
    c.alpha_composite(idx.rotate(180), (wpx - idx.width - int(wpx*0.02), hpx - idx.height - int(wpx*0.03)))
    return c

def sweat():
    W, H = 4800, 6000
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cw, ch = int(W * 0.30), int(W * 0.42)
    ranks = ["10", "J", "Q", "K", "A"]
    n = len(ranks)
    pivot_x, pivot_y = W / 2, H * 0.52
    for i, rank in enumerate(ranks):
        ang = -26 + i * 13
        card = card_face(rank, cw, ch)
        pad = int(math.hypot(cw, ch)) + 40
        lay = Image.new("RGBA", (pad, pad), (0, 0, 0, 0))
        lay.alpha_composite(card, ((pad - cw) // 2, (pad - ch) // 2))
        lay = lay.rotate(-ang, resample=Image.BICUBIC, center=(pad / 2, pad / 2))
        a = math.radians(ang)
        # fan around a pivot below the cards
        r = H * 0.245
        cxp = pivot_x + math.sin(a) * r
        cyp = pivot_y - math.cos(a) * r * 0.88 + ch * 0.05
        img.alpha_composite(lay, (int(cxp - pad / 2), int(cyp - pad / 2)))
    d = ImageDraw.Draw(img)
    text_tracked(d, (W / 2, H * 0.70), "ESCALERA REAL", F(SERIF_B, 300), CREMA, tracking=40, center=True)
    text_tracked(d, (W / 2, H * 0.76), "TODO O NADA · STREET ROYALTY HOOD", F(SANS, 96), ORO_HI, tracking=30, center=True)
    return finish(img, 2400, 3000)

# ---------------------------------------------------------------- 4. Zapatillas Altas — tile 2400x2400 (negro/oro)
def hitops_tile():
    W = 4800
    img = Image.new("RGBA", (W, W), NEGRO)
    d = ImageDraw.Draw(img)
    # fine dot grid
    for gy in range(0, W, 120):
        for gx in range(0, W, 120):
            d.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], fill=(52, 48, 52, 255))
    # half-drop diagonal lattice of suits + crowns
    order = ["spade", "heart", "crown", "club", "diamond"]
    cols = ["gold", "burdeos", "cream"]
    step = W / 8
    idx = 0
    for row in range(-1, 10):
        off = (row % 2) * step / 2
        for col in range(-1, 10):
            cx = col * step + off + step / 2
            cy = row * step * 0.92 + step / 2
            kind = order[(row * 3 + col) % 5]
            tone = cols[(row + col * 2) % 3]
            fill = ORO if tone == "gold" else (BURDEOS_HI if tone == "burdeos" else CREMA)
            s = step * 0.30
            if kind == "crown":
                draw_crown(d, cx, cy, s * 1.5, s * 0.75, ORO_HI if tone == "gold" else fill)
            else:
                SUITS[kind](d, cx, cy, s, fill)
            idx += 1
    return finish(img.convert("RGB"), 2400, 2400)

# ---------------------------------------------------------------- 5. Zapatillas Deportivas Mujer — 1950x3300 (marfil)
def athletic_print():
    W, H = 3900, 6600
    img = Image.new("RGBA", (W, H), MARFIL)
    d = ImageDraw.Draw(img)
    rnd = random.Random(21)
    # scattered pips with offset-print double layer (misregistration look)
    kinds = ["spade", "heart", "diamond", "club", "crown"]
    placed = []
    tries = 0
    while len(placed) < 46 and tries < 4000:
        tries += 1
        s = rnd.uniform(0.045, 0.11) * W
        x = rnd.uniform(s * 1.3, W - s * 1.3)
        y = rnd.uniform(s * 1.3, H - s * 1.3)
        if any((x - px) ** 2 + (y - py) ** 2 < (1.75 * (s + ps)) ** 2 for px, py, ps in placed):
            continue
        placed.append((x, y, s))
        kind = kinds[len(placed) % 5]
        main = NAVY if kind in ("spade", "club") else (BURDEOS if kind != "crown" else ORO)
        ghost = ORO if main != ORO else BURDEOS
        rot = rnd.uniform(-24, 24)
        pad = int(s * 3.2)
        lay = Image.new("RGBA", (pad, pad), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        gdx, gdy = s * 0.14, s * 0.12
        if kind == "crown":
            draw_crown(ld, pad / 2 + gdx, pad / 2 + gdy, s * 1.6, s * 0.8, ghost + (150,) if len(ghost) == 3 else ghost)
            draw_crown(ld, pad / 2, pad / 2, s * 1.6, s * 0.8, main)
        else:
            SUITS[kind](ld, pad / 2 + gdx, pad / 2 + gdy, s, ghost[:3] + (150,))
            SUITS[kind](ld, pad / 2, pad / 2, s, main)
        lay = lay.rotate(rot, resample=Image.BICUBIC)
        img.alpha_composite(lay, (int(x - pad / 2), int(y - pad / 2)))
    # sparse micro dots
    for _ in range(240):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(4, 9)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(206, 192, 164, 255))
    return finish(img.convert("RGB"), 1950, 3300)

# ---------------------------------------------------------------- 6. Calcetines — 1400x2400 harlequin (negro/oro)
def socks_print():
    W, H = 2800, 4800
    img = Image.new("RGBA", (W, H), NEGRO)
    d = ImageDraw.Draw(img)
    # harlequin diamond lattice
    dw, dh = W / 5, W / 5 * 1.62
    for row in range(-1, int(H / dh * 2) + 2):
        for col in range(-1, 7):
            cx = col * dw + (row % 2) * dw / 2
            cy = row * dh / 2
            dark = (row + col) % 2 == 0
            pts = [(cx, cy - dh / 2), (cx + dw / 2, cy), (cx, cy + dh / 2), (cx - dw / 2, cy)]
            d.polygon(pts, fill=CARBON if dark else NEGRO, outline=(60, 54, 44, 255), width=4)
    # gold pips at lattice intersections (alternating suits)
    kinds = ["spade", "diamond", "club", "heart"]
    k = 0
    for row in range(0, int(H / dh * 2) + 1):
        for col in range(0, 6):
            cx = col * dw + (row % 2) * dw / 2
            cy = row * dh / 2
            if (row + col) % 2 == 0: continue
            kind = kinds[k % 4]; k += 1
            SUITS[kind](d, cx, cy, dw * 0.17, BURDEOS_HI if kind == "heart" else ORO)
    # top cuff band
    d.rectangle([0, 0, W, H * 0.075], fill=NEGRO)
    d.line([0, H * 0.075, W, H * 0.075], fill=ORO, width=12)
    text_tracked(d, (W / 2, H * 0.022), "S R H", F(SANS_B, 150), ORO_HI, tracking=60, center=True)
    return finish(img.convert("RGB"), 1400, 2400)

if __name__ == "__main__":
    jobs = {
        "brj_tee_print.png": tee,
        "brj_hoodie_print.png": hoodie,
        "brj_sweat_print.png": sweat,
        "brj_hitops_print.png": hitops_tile,
        "brj_athletic_print.png": athletic_print,
        "brj_socks_print.png": socks_print,
    }
    for name, fn in jobs.items():
        fn().save(os.path.join(OUT, name))
        print("done", name)
