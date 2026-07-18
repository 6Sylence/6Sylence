#!/usr/bin/env python3
# Cápsula Escaque — Jaque Real + Cápsula Camo Real
# 12 print files (DTG frontals RGBA + all-over covers RGB) for Street Royalty Hood.
# Run 2026-07-18. Rendered at 2x supersampling, LANCZOS downscale.
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

EBANO   = (13, 13, 16)
MARFIL  = (243, 235, 218)
ORO     = (198, 160, 74)
ORO_HI  = (236, 208, 130)
CARMESI = (116, 28, 42)
NOCHE   = (15, 22, 31)
BOSQUE  = (34, 48, 38)
OLIVA   = (74, 82, 58)
PIEDRA  = (147, 143, 121)
HUMO    = (52, 58, 52)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def F(p, s): return ImageFont.truetype(p, s)

def gold_grad(w, h, top=ORO_HI, bot=ORO):
    g = Image.new("RGB", (1, h))
    px = g.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    return g.resize((w, h))

def fill_mask(base, mask, color_img):
    base.paste(color_img, (0, 0), mask)

def crown_pts(cx, cy, w, h):
    l, r, t, b = cx - w/2, cx + w/2, cy - h/2, cy + h/2
    dip = b - h * 0.40
    return [(l, b), (l, t + h*0.30), (l + w*0.185, dip),
            (cx - w*0.155, t + h*0.10), (cx, dip - h*0.04),
            (cx + w*0.155, t + h*0.10), (r - w*0.185, dip),
            (r, t + h*0.30), (r, b)]

def draw_crown(dr, cx, cy, w, h, fill, outline=None, ow=0, jewels=None, band=True):
    dr.polygon(crown_pts(cx, cy, w, h), fill=fill, outline=outline, width=ow)
    if band:
        dr.rounded_rectangle([cx - w/2, cy + h/2 + h*0.05, cx + w/2, cy + h/2 + h*0.17],
                             radius=h*0.05, fill=fill, outline=outline, width=ow)
    if jewels:
        r = h * 0.055
        for jx in (cx - w*0.33, cx, cx + w*0.33):
            dr.ellipse([jx - r, cy - h*0.62 - r, jx + r, cy - h*0.62 + r], fill=jewels)

def tracked(dr, xy, text, font, fill, tr=0, center=True, stroke=0, sfill=None):
    x, y = xy
    ws = [dr.textlength(c, font=font) for c in text]
    total = sum(ws) + tr * (len(text) - 1)
    if center: x -= total / 2
    for c, w in zip(text, ws):
        dr.text((x, y), c, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)
        x += w + tr
    return total

def arc_text(img, center, radius, text, font, fill, start=-90, clockwise=True, spread=None):
    cx, cy = center
    tmp = ImageDraw.Draw(img)
    arcs = [max(tmp.textlength(c, font=font), font.size*0.30)/radius for c in text]
    total = sum(arcs)
    if spread: total = spread
    a = math.radians(start) - (total/2 if clockwise else -total/2)
    step = (total / max(sum(arcs), 1e-6))
    for c, arc in zip(text, arcs):
        arc *= step
        mid = a + (arc/2 if clockwise else -arc/2)
        x = cx + radius*math.cos(mid); y = cy + radius*math.sin(mid)
        s = font.size * 3
        ch = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        cd = ImageDraw.Draw(ch)
        cd.text((s/2, s/2), c, font=font, fill=fill, anchor="mm")
        deg = math.degrees(mid) + (90 if clockwise else -90)
        ch = ch.rotate(-deg, resample=Image.BICUBIC, center=(s/2, s/2))
        img.alpha_composite(ch, (int(x - s/2), int(y - s/2)))
        a += arc if clockwise else -arc

def save(img, name, final_size):
    img = img.resize(final_size, Image.LANCZOS)
    img.save(os.path.join(OUT, name))
    print("wrote", name, img.size)

# ---------------------------------------------------------------- camo engine
def camo_layers(w, h, seed, scales, blobs=140):
    """Return list of L-mode masks, one per scale, organic camo patches."""
    masks = []
    for i, sc in enumerate(scales):
        rnd = random.Random(seed + i * 101)
        lay = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(lay)
        for _ in range(blobs):
            x, y = rnd.uniform(-0.05, 1.05) * w, rnd.uniform(-0.05, 1.05) * h
            rx, ry = rnd.uniform(0.4, 1.0) * sc, rnd.uniform(0.35, 0.9) * sc
            d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=255)
        lay = lay.filter(ImageFilter.GaussianBlur(sc * 0.42))
        lay = lay.point(lambda v: 255 if v > 128 else 0)
        masks.append(lay)
    return masks

def camo_field(w, h, seed, palette, scale=1.0, blobs=140):
    base = Image.new("RGB", (w, h), palette[0])
    scales = [s * scale for s in (150, 118, 88, 60)]
    for mask, col in zip(camo_layers(w, h, seed, scales, blobs), palette[1:]):
        base.paste(Image.new("RGB", (w, h), col), (0, 0), mask)
    return base

def scatter_crowns(img, seed, n, size, color, outline_only=True, ow=6, alpha=255):
    rnd = random.Random(seed)
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for _ in range(n):
        cx, cy = rnd.uniform(0.06, 0.94) * img.size[0], rnd.uniform(0.06, 0.94) * img.size[1]
        s = size * rnd.uniform(0.75, 1.25)
        rot = rnd.uniform(-20, 20)
        tile = Image.new("RGBA", (int(s * 2), int(s * 2)), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        if outline_only:
            draw_crown(td, s, s, s * 1.3, s * 0.9, None, outline=color + (alpha,), ow=ow)
        else:
            draw_crown(td, s, s, s * 1.3, s * 0.9, color + (alpha,))
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
        over.alpha_composite(tile, (int(cx - tile.size[0]/2), int(cy - tile.size[1]/2)))
    out = img.convert("RGBA")
    out.alpha_composite(over)
    return out.convert("RGB")

def grain(img, strength=0.05, amount=26):
    n = Image.effect_noise(img.size, amount).convert("L")
    return Image.blend(img.convert("RGB"), Image.merge("RGB", (n, n, n)), strength)

# ------------------------------------------------------------- checker engine
def warped_checker(w, h, cell, warp, lam, pal_a, pal_b, phase=0.0):
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    u = xs + warp * np.sin(ys / lam + phase) + 0.35 * warp * np.sin(ys / (lam * 0.37) + 1.7)
    v = ys + warp * np.sin(xs / (lam * 1.21) + 0.6 + phase)
    c = ((np.floor(u / cell) + np.floor(v / cell)) % 2).astype(np.uint8)
    a = np.array(pal_a, dtype=np.uint8); b = np.array(pal_b, dtype=np.uint8)
    out = np.where(c[..., None] == 0, a, b)
    return Image.fromarray(out, "RGB")

def chess_king(dr, cx, base_y, H, fill, cross=ORO):
    """Stylized chess king: stepped base, waisted stem, collar, orb, gold cross."""
    u = H / 100.0
    # base plinths
    for i, (bw, bh) in enumerate([(46, 7), (38, 6), (30, 5)]):
        y1 = base_y - sum(x[1] for x in [(46,7),(38,6),(30,5)][:i]) * u
        dr.rounded_rectangle([cx - bw*u/2, y1 - bh*u, cx + bw*u/2, y1], radius=2.2*u, fill=fill)
    stem_top = base_y - 18*u - 46*u
    # waisted stem (polygon)
    dr.polygon([(cx - 13*u, base_y - 18*u), (cx - 5.5*u, stem_top),
                (cx + 5.5*u, stem_top), (cx + 13*u, base_y - 18*u)], fill=fill)
    # collar rings
    for off, rw in [(0, 18), (5, 14)]:
        dr.rounded_rectangle([cx - rw*u/2, stem_top - (4 + off)*u, cx + rw*u/2, stem_top - off*u],
                             radius=1.6*u, fill=fill)
    # orb
    orb_r = 11*u
    orb_cy = stem_top - 9*u - orb_r
    dr.ellipse([cx - orb_r, orb_cy - orb_r, cx + orb_r, orb_cy + orb_r], fill=fill)
    # cross
    t = 3.4*u; ch = 16*u; cw = 11*u; cy0 = orb_cy - orb_r - 2*u
    dr.rectangle([cx - t/2, cy0 - ch, cx + t/2, cy0], fill=cross)
    dr.rectangle([cx - cw/2, cy0 - ch*0.68, cx + cw/2, cy0 - ch*0.68 + t], fill=cross)

def chess_rook(dr, cx, base_y, H, fill):
    u = H / 100.0
    for i, (bw, bh) in enumerate([(52, 8), (42, 6)]):
        y1 = base_y - sum(x[1] for x in [(52,8),(42,6)][:i]) * u
        dr.rounded_rectangle([cx - bw*u/2, y1 - bh*u, cx + bw*u/2, y1], radius=2*u, fill=fill)
    body_top = base_y - 14*u - 58*u
    dr.polygon([(cx - 17*u, base_y - 14*u), (cx - 13*u, body_top),
                (cx + 13*u, body_top), (cx + 17*u, base_y - 14*u)], fill=fill)
    dr.rectangle([cx - 21*u, body_top - 6*u, cx + 21*u, body_top], fill=fill)
    # crenellations
    for k in (-1.5, -0.5, 0.5, 1.5):
        mx = cx + k * 12.5*u
        dr.rectangle([mx - 4.6*u, body_top - 18*u, mx + 4.6*u, body_top - 5*u], fill=fill)

# =============================================================== ESCAQUE ====
def esc_tee():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = W / 2
    # arch frame
    top, bot = 760, 3560
    aw = 2260
    l, r = cx - aw/2, cx + aw/2
    arch_r = aw / 2
    # perspective checker floor inside arch
    horizon = 1900
    floor_top, floor_bot = horizon, bot - 60
    rows, cols = 9, 11
    for i in range(rows):
        t0, t1 = i / rows, (i + 1) / rows
        y0 = floor_top + (floor_bot - floor_top) * t0**1.85
        y1 = floor_top + (floor_bot - floor_top) * t1**1.85
        w0 = aw * (0.16 + 0.84 * t0**1.25)
        w1 = aw * (0.16 + 0.84 * t1**1.25)
        for j in range(cols):
            if (i + j) % 2: continue
            x00 = cx - w0/2 + w0 * j/cols;  x01 = cx - w0/2 + w0 * (j+1)/cols
            x10 = cx - w1/2 + w1 * j/cols;  x11 = cx - w1/2 + w1 * (j+1)/cols
            dr.polygon([(x00, y0), (x01, y0), (x11, y1), (x10, y1)], fill=MARFIL + (255,))
    # king on the board
    king = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kd = ImageDraw.Draw(king)
    chess_king(kd, cx, floor_bot - 260, 1750, MARFIL + (255,), cross=ORO)
    img.alpha_composite(king)
    # arch outline (double)
    def arch(dd, inset, wd, col):
        li, ri, ti = l + inset, r - inset, top + inset
        rr = (ri - li) / 2
        dd.arc([li, ti, ri, ti + 2*rr], 180, 360, fill=col, width=wd)
        dd.line([li, ti + rr, li, bot - inset], fill=col, width=wd)
        dd.line([ri, ti + rr, ri, bot - inset], fill=col, width=wd)
        dd.line([li, bot - inset, ri, bot - inset], fill=col, width=wd)
    arch(dr, 0, 16, ORO + (255,))
    arch(dr, 56, 6, MARFIL + (255,))
    # crown above arch
    gcrown = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gcrown)
    draw_crown(gd, cx, 470, 560, 330, ORO + (255,), outline=MARFIL + (255,), ow=6, jewels=CARMESI + (255,))
    img.alpha_composite(gcrown)
    # typography
    f_big = F(SERIF_B, 340); f_sm = F(SANS_B, 96); f_tag = F(SANS_B, 74)
    tracked(dr, (cx, 3760), "JAQUE REAL", f_big, MARFIL + (255,), tr=26)
    tracked(dr, (cx, 4260), "CÁPSULA ESCAQUE", f_sm, ORO + (255,), tr=64)
    tracked(dr, (cx, 4460), "STREET ROYALTY HOOD · MMXXVI", f_tag, MARFIL + (235,), tr=30)
    save(img, "esc_tee_front.png", (1800, 2400))

def esc_sweat():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = W / 2
    # rotated checker diamond emblem
    side = 2050
    tile = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    n = 8; cs = side / n
    for i in range(n):
        for j in range(n):
            col = EBANO if (i + j) % 2 == 0 else MARFIL
            td.rectangle([i*cs, j*cs, (i+1)*cs, (j+1)*cs], fill=col + (255,))
    tile = tile.rotate(45, resample=Image.BICUBIC, expand=True)
    dy = 640
    img.alpha_composite(tile, (int(cx - tile.size[0]/2), dy))
    dcy = dy + tile.size[1] / 2
    # gold diamond frame
    hw = tile.size[0] / 2
    for inset, wd in [(0, 20), (70, 8)]:
        pts = [(cx, dcy - hw + inset), (cx + hw - inset, dcy),
               (cx, dcy + hw - inset), (cx - hw + inset, dcy)]
        dr.polygon(pts, outline=ORO + (255,), width=wd)
    # rook medallion at center
    med_r = 620
    dr.ellipse([cx - med_r, dcy - med_r, cx + med_r, dcy + med_r], fill=EBANO + (255,))
    dr.ellipse([cx - med_r, dcy - med_r, cx + med_r, dcy + med_r], outline=ORO + (255,), width=18)
    rook = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rook)
    chess_rook(rd, cx, dcy + 440, 860, MARFIL + (255,))
    img.alpha_composite(rook)
    crown_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(crown_l)
    draw_crown(cd, cx, dcy - 320, 300, 180, ORO + (255,))
    img.alpha_composite(crown_l)
    # typography
    tracked(dr, (cx, 240), "STREET ROYALTY", F(SANS_B, 150), EBANO + (255,), tr=58)
    f_line = F(SERIF_B, 168)
    tracked(dr, (cx, dy + tile.size[1] + 160), "DEFIENDE LA CORONA", f_line, EBANO + (255,), tr=14)
    tracked(dr, (cx, dy + tile.size[1] + 430), "CÁPSULA ESCAQUE · SRHOOD", F(SANS_B, 82), CARMESI + (255,), tr=36)
    save(img, "esc_sweat_front.png", (1800, 2400))

def esc_hoodie():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = W / 2
    cyc = 1560
    R = 1150
    # checkered ring
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    seg = 44
    for k in range(seg):
        a0 = k * 360 / seg; a1 = (k + 1) * 360 / seg
        col = MARFIL if k % 2 == 0 else ORO
        rd.pieslice([cx - R, cyc - R, cx + R, cyc + R], a0, a1, fill=col + (255,))
    hole = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(hole)
    hd.ellipse([cx - R + 150, cyc - R + 150, cx + R - 150, cyc + R - 150], fill=255)
    ring.paste((0, 0, 0, 0), (0, 0), hole)
    img.alpha_composite(ring)
    dr.ellipse([cx - R, cyc - R, cx + R, cyc + R], outline=ORO + (255,), width=14)
    ir = R - 150
    dr.ellipse([cx - ir, cyc - ir, cx + ir, cyc + ir], outline=ORO + (255,), width=14)
    # king inside
    king = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kd = ImageDraw.Draw(king)
    chess_king(kd, cx, cyc + 700, 1330, MARFIL + (255,), cross=ORO)
    img.alpha_composite(king)
    # arc text inside ring? place above and below
    arc_text(img, (cx, cyc), R + 210, "CÁPSULA ESCAQUE", F(SANS_B, 132), ORO + (255,), start=-90)
    arc_text(img, (cx, cyc), R + 190, "JAQUE REAL · MMXXVI", F(SANS_B, 110), MARFIL + (245,), start=90, clockwise=False)
    tracked(dr, (cx, cyc + R + 330), "SRHOOD", F(SERIF_B, 300), MARFIL + (255,), tr=90)
    save(img, "esc_hoodie_front.png", (1800, 2400))

def esc_shoe_m():
    W, H = 2250, 2250
    img = warped_checker(W, H, cell=185, warp=64, lam=210, pal_a=EBANO, pal_b=MARFIL)
    img = scatter_crowns(img, seed=41, n=9, size=95, color=ORO, outline_only=False)
    img = grain(img, 0.035)
    img.save(os.path.join(OUT, "esc_shoe_m.png")); print("wrote esc_shoe_m.png")

def esc_shoe_w():
    W, H = 1950, 3300
    img = warped_checker(W, H, cell=120, warp=42, lam=150, pal_a=MARFIL, pal_b=(226, 214, 190), phase=1.3)
    # ebony flow ribbon: overlay a second, larger warped checker only inside a diagonal band
    dark = warped_checker(W, H, cell=175, warp=70, lam=220, pal_a=EBANO, pal_b=MARFIL)
    band = Image.new("L", (W, H), 0)
    bd = ImageDraw.Draw(band)
    bd.polygon([(0, H*0.42), (W, H*0.10), (W, H*0.52), (0, H*0.86)], fill=255)
    band = band.filter(ImageFilter.GaussianBlur(38))
    img.paste(dark, (0, 0), band)
    img = scatter_crowns(img, seed=77, n=7, size=80, color=ORO, outline_only=False)
    img = grain(img, 0.03)
    img.save(os.path.join(OUT, "esc_shoe_w.png")); print("wrote esc_shoe_w.png")

def esc_socks():
    W, H = 1348, 5657
    img = Image.new("RGB", (W, H), EBANO)
    dr = ImageDraw.Draw(img)
    # checker gradient: cells shrink toward ankle
    y = 0; row = 0
    sizes = np.linspace(200, 92, 24)
    for cs in sizes:
        cs = float(cs)
        n = math.ceil(W / cs)
        for j in range(n):
            if (row + j) % 2 == 0:
                dr.rectangle([j*cs, y, (j+1)*cs, y + cs], fill=MARFIL)
        y += cs; row += 1
        if y > H * 0.62: break
    # gold divider + crowns row
    dr.rectangle([0, y, W, y + 26], fill=ORO)
    cyc = y + 260
    for k in range(3):
        cxx = W * (0.25 + 0.25 * k)
        draw_crown(dr, cxx, cyc, 210, 130, ORO)
    dr.rectangle([0, cyc + 320, W, cyc + 346], fill=ORO)
    f = F(SANS_B, 118)
    tracked(dr, (W/2, cyc + 560), "SRHOOD", f, MARFIL, tr=42)
    img = grain(img, 0.035)
    img.save(os.path.join(OUT, "esc_socks.png")); print("wrote esc_socks.png")

# ================================================================= CAMO ====
CAMO_PAL_M = [NOCHE, BOSQUE, OLIVA, HUMO, (8, 10, 9)]
CAMO_PAL_W = [(233, 226, 209), PIEDRA, (168, 172, 148), OLIVA, NOCHE]

def camo_tee():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = W / 2
    # shield crest filled with camo
    sw, sh = 1980, 2320
    stop = 1150
    shield = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shield)
    pts = [(cx - sw/2, stop), (cx + sw/2, stop),
           (cx + sw/2, stop + sh*0.55), (cx, stop + sh), (cx - sw/2, stop + sh*0.55)]
    sd.polygon(pts, fill=255)
    camo = camo_field(W, H, seed=5, palette=CAMO_PAL_M, scale=1.35, blobs=170).convert("RGBA")
    img.paste(camo, (0, 0), shield)
    dr.polygon(pts, outline=ORO + (255,), width=22)
    inner = [(cx - sw/2 + 70, stop + 70), (cx + sw/2 - 70, stop + 70),
             (cx + sw/2 - 70, stop + sh*0.55 - 22), (cx, stop + sh - 118),
             (cx - sw/2 + 70, stop + sh*0.55 - 22)]
    dr.polygon(inner, outline=MARFIL + (235,), width=8)
    # gold crown centered on shield
    gc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gc)
    draw_crown(gd, cx, stop + sh*0.42, 760, 470, ORO + (255,), jewels=NOCHE + (255,))
    img.alpha_composite(gc)
    # crown over shield tip
    tracked(dr, (cx, 420), "STREET ROYALTY", F(SANS_B, 168), MARFIL + (255,), tr=54)
    tracked(dr, (cx, 700), "HOOD", F(SANS_B, 120), ORO + (255,), tr=180)
    # banner below
    by = stop + sh + 170
    dr.polygon([(cx - 1150, by), (cx + 1150, by), (cx + 1010, by + 300), (cx - 1010, by + 300)],
               fill=NOCHE + (255,), outline=ORO + (255,), width=14)
    tracked(dr, (cx, by + 62), "CAMO REAL", F(SERIF_B, 190), ORO_HI + (255,), tr=40)
    tracked(dr, (cx, by + 440), "SE CAMUFLA, NUNCA SE RINDE", F(SANS_B, 86), MARFIL + (240,), tr=30)
    save(img, "camo_tee_front.png", (1800, 2400))

def camo_zip_back():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cyc = W/2, 2120
    # big crown silhouette filled with camo
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    draw_crown(md, cx, cyc, 2520, 1560, 255, jewels=None)
    camo = camo_field(W, H, seed=23, palette=[BOSQUE, NOCHE, OLIVA, HUMO, (10, 12, 10)],
                      scale=1.5, blobs=170).convert("RGBA")
    img.paste(camo, (0, 0), mask)
    # gold outline of the crown
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(out)
    draw_crown(od, cx, cyc, 2520, 1560, None, outline=ORO + (255,), ow=26)
    img.alpha_composite(out)
    dr = ImageDraw.Draw(img)
    r = 92
    for jx in (cx - 2520*0.33, cx, cx + 2520*0.33):
        dr.ellipse([jx - r, cyc - 1560*0.62 - r, jx + r, cyc - 1560*0.62 + r],
                   fill=ORO + (255,), outline=MARFIL + (255,), width=10)
    arc_text(img, (cx, cyc + 150), 1780, "LA CORONA SE CAMUFLA", F(SANS_B, 150), MARFIL + (255,), start=-90)
    tracked(dr, (cx, cyc + 1180), "NUNCA SE RINDE", F(SERIF_B, 210), ORO + (255,), tr=30)
    tracked(dr, (cx, cyc + 1520), "CÁPSULA CAMO REAL · SRHOOD · MMXXVI", F(SANS_B, 78), MARFIL + (235,), tr=28)
    save(img, "camo_zip_back.png", (1800, 2400))

def camo_hoodie():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = W / 2
    # camo chevron band
    band_top, band_h = 1350, 1080
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.polygon([(150, band_top), (W - 150, band_top), (W - 150, band_top + band_h),
                (cx, band_top + band_h + 330), (150, band_top + band_h)], fill=255)
    camo = camo_field(W, H, seed=57, palette=[NOCHE, (26, 38, 52), BOSQUE, OLIVA, (9, 12, 16)],
                      scale=1.3, blobs=170).convert("RGBA")
    img.paste(camo, (0, 0), mask)
    md2 = ImageDraw.Draw(img)
    md2.polygon([(150, band_top), (W - 150, band_top), (W - 150, band_top + band_h),
                 (cx, band_top + band_h + 330), (150, band_top + band_h)],
                outline=ORO + (255,), width=18)
    # crown breaking out of the band
    gc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gc)
    draw_crown(gd, cx, band_top + 40, 900, 560, ORO + (255,), outline=None, jewels=NOCHE + (255,))
    img.alpha_composite(gc)
    tracked(dr, (cx, 330), "SRHOOD", F(SERIF_B, 330), MARFIL + (255,), tr=100)
    tracked(dr, (cx, band_top + band_h + 480), "CAMO REAL", F(SANS_B, 170), ORO + (255,), tr=76)
    tracked(dr, (cx, band_top + band_h + 760), "STREET ROYALTY DIVISION", F(SANS_B, 84), MARFIL + (235,), tr=40)
    save(img, "camo_hoodie_front.png", (1800, 2400))

def camo_shoe_m():
    img = camo_field(2250, 2250, seed=91, palette=CAMO_PAL_M, scale=1.0, blobs=150)
    img = scatter_crowns(img, seed=15, n=10, size=88, color=ORO, outline_only=True, ow=8)
    img = grain(img, 0.045)
    img.save(os.path.join(OUT, "camo_shoe_m.png")); print("wrote camo_shoe_m.png")

def camo_slip_w():
    img = camo_field(2325, 2325, seed=133, palette=CAMO_PAL_W, scale=0.9, blobs=150)
    img = scatter_crowns(img, seed=29, n=9, size=82, color=ORO, outline_only=True, ow=8)
    img = grain(img, 0.035)
    img.save(os.path.join(OUT, "camo_slip_w.png")); print("wrote camo_slip_w.png")

def camo_bandana():
    W = 4125
    img = camo_field(W, W, seed=201, palette=[NOCHE, BOSQUE, OLIVA, HUMO, (8, 10, 9)], scale=1.6, blobs=160)
    img = scatter_crowns(img, seed=61, n=14, size=120, color=ORO, outline_only=True, ow=10)
    dr = ImageDraw.Draw(img)
    # double gold frame
    for inset, wd in [(190, 26), (300, 10)]:
        dr.rectangle([inset, inset, W - inset, W - inset], outline=ORO, width=wd)
    # corner crowns
    for cxx, cyy in [(470, 470), (W - 470, 470), (470, W - 470), (W - 470, W - 470)]:
        draw_crown(dr, cxx, cyy, 300, 190, ORO, jewels=NOCHE)
    # center medallion
    cx = W / 2; mr = 660
    dr.ellipse([cx - mr, cx - mr, cx + mr, cx + mr], fill=NOCHE, outline=ORO, width=20)
    dr.ellipse([cx - mr + 90, cx - mr + 90, cx + mr - 90, cx + mr - 90], outline=MARFIL, width=8)
    draw_crown(dr, cx, cx - 120, 560, 350, ORO, jewels=CARMESI)
    rgba = img.convert("RGBA")
    d2 = ImageDraw.Draw(rgba)
    tracked(d2, (cx, cx + 330), "CAMO REAL", F(SERIF_B, 160), ORO_HI + (255,), tr=22)
    tracked(d2, (cx, cx + 550), "SRHOOD", F(SANS_B, 96), (243, 235, 218, 255), tr=60)
    img = grain(rgba.convert("RGB"), 0.04)
    img.save(os.path.join(OUT, "camo_bandana.png")); print("wrote camo_bandana.png")

def tongue_esc():
    # 1050x600 fit — gold crown on ebony for hi-top tongue
    img = Image.new("RGBA", (1050, 600), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([10, 10, 1040, 590], radius=60, fill=EBANO + (255,), outline=ORO + (255,), width=10)
    draw_crown(dr, 525, 250, 340, 210, ORO + (255,), jewels=CARMESI + (255,))
    tracked(dr, (525, 430), "SRHOOD", F(SANS_B, 92), MARFIL + (255,), tr=26)
    img.save(os.path.join(OUT, "esc_tongue.png")); print("wrote esc_tongue.png")

def tongue_camo():
    img = Image.new("RGBA", (1050, 600), (0, 0, 0, 0))
    base = camo_field(1050, 600, seed=171, palette=CAMO_PAL_M, scale=0.55, blobs=130).convert("RGBA")
    mask = Image.new("L", (1050, 600), 0)
    ImageDraw.Draw(mask).rounded_rectangle([10, 10, 1040, 590], radius=60, fill=255)
    img.paste(base, (0, 0), mask)
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([10, 10, 1040, 590], radius=60, outline=ORO + (255,), width=10)
    draw_crown(dr, 525, 240, 330, 200, ORO + (255,), jewels=NOCHE + (255,))
    tracked(dr, (525, 420), "CAMO REAL", F(SANS_B, 84), (243, 235, 218, 255), tr=22)
    img.save(os.path.join(OUT, "camo_tongue.png")); print("wrote camo_tongue.png")

if __name__ == "__main__":
    esc_tee(); esc_sweat(); esc_hoodie(); esc_shoe_m(); esc_shoe_w(); esc_socks()
    camo_tee(); camo_zip_back(); camo_hoodie(); camo_shoe_m(); camo_slip_w(); camo_bandana()
    tongue_esc(); tongue_camo()
    print("done")
