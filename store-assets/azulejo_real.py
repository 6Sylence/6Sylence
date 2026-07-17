#!/usr/bin/env python3
# Cápsula Azulejo — Cerámica Real · SRHOOD
# 6 print files: camiseta, sudadera, hoodie, zapatillas altas (quarters+tongue),
# slip-on mujer (seamless), calcetines. Cobalto + blanco + oro.
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azulejo")
os.makedirs(OUT, exist_ok=True)

COBALTO = (22, 56, 124)
AZUL    = (44, 96, 172)
CELESTE = (136, 178, 220)
GLAZE   = (247, 247, 242)   # blanco esmalte
ORO     = (200, 162, 74)
ORO_HI  = (232, 204, 126)
JUNTA   = (208, 209, 200)   # junta entre azulejos

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def F(p, s): return ImageFont.truetype(p, s)

def text_tracked(draw, xy, text, font, fill, tracking=0, center=False):
    x, y = xy
    ws = [draw.textlength(c, font=font) for c in text]
    total = sum(ws) + tracking * (len(text) - 1)
    if center: x -= total / 2
    for c, cw in zip(text, ws):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking
    return total

def crown_path(cx, cy, w, h):
    l = cx - w / 2; r = cx + w / 2; b = cy + h / 2; t = cy - h / 2
    dipy = b - h * 0.42
    pts = [(l, b), (l, t + h * 0.30), (l + w * 0.185, dipy),
           (cx - w * 0.155, t + h * 0.12), (cx, dipy - h * 0.02),
           (cx + w * 0.155, t + h * 0.12), (r - w * 0.185, dipy),
           (r, t + h * 0.30), (r, b)]
    band = (l, b + h * 0.06, r, b + h * 0.16)
    return pts, band

def star8(cx, cy, R, rot=0.0):
    """Eight-point star (two rotated squares) vertex list."""
    pts = []
    for i in range(16):
        a = rot + math.pi * i / 8
        r = R if i % 2 == 0 else R * 0.415
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def glaze_texture(img, seed=5, strength=0.05):
    rnd = random.Random(seed)
    noise = Image.effect_noise(img.size, 14).convert("L")
    return Image.blend(img.convert("RGB"),
                       Image.merge("RGB", (noise, noise, noise)), strength)

# ---------------------------------------------------------------- tile primitives
def clipped_tile(fn, s, **kw):
    """Render a tile on its own square so nothing bleeds into neighbours."""
    t = Image.new("RGB", (int(s), int(s)))
    fn(ImageDraw.Draw(t), 0, 0, int(s), **kw)
    return t

def tile_rosette(d, x, y, s, fg=COBALTO, bg=GLAZE, acc=None):
    """Classic azulejo: central rosette + quarter-circle corners."""
    d.rectangle([x, y, x + s, y + s], fill=bg)
    cx, cy = x + s / 2, y + s / 2
    # corner quarter fans
    for ox, oy in ((x, y), (x + s, y), (x, y + s), (x + s, y + s)):
        r = s * 0.30
        d.ellipse([ox - r, oy - r, ox + r, oy + r], fill=fg)
        r2 = s * 0.20
        d.ellipse([ox - r2, oy - r2, ox + r2, oy + r2], fill=bg)
        r3 = s * 0.115
        d.ellipse([ox - r3, oy - r3, ox + r3, oy + r3], fill=fg)
    # central 8-petal rosette
    for i in range(8):
        a = math.pi * i / 4
        px, py = cx + s * 0.26 * math.cos(a), cy + s * 0.26 * math.sin(a)
        r = s * 0.115
        d.ellipse([px - r, py - r, px + r, py + r], fill=fg)
    r = s * 0.15
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=acc or fg)
    r2 = s * 0.065
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=bg)

def tile_star_cross(d, x, y, s, fg=COBALTO, bg=GLAZE, acc=None):
    """Star-cross (khatam) tile: 8-point star centered, cross arms to edges."""
    d.rectangle([x, y, x + s, y + s], fill=fg)
    cx, cy = x + s / 2, y + s / 2
    d.polygon(star8(cx, cy, s * 0.46, rot=math.pi / 8), fill=bg)
    d.polygon(star8(cx, cy, s * 0.30, rot=math.pi / 8), fill=acc or AZUL)
    d.polygon(star8(cx, cy, s * 0.15, rot=math.pi / 8), fill=bg)
    # quarter-diamonds at the corners (kept inside the tile)
    for ox, oy in ((x, y), (x + s, y), (x, y + s), (x + s, y + s)):
        q = s * 0.16
        d.polygon([(ox - q, oy), (ox, oy - q), (ox + q, oy), (ox, oy + q)], fill=bg)
        q2 = s * 0.085
        d.polygon([(ox - q2, oy), (ox, oy - q2), (ox + q2, oy), (ox, oy + q2)], fill=acc or AZUL)

def tile_crown(d, x, y, s, fg=COBALTO, bg=GLAZE, acc=ORO):
    """Crown medallion tile."""
    d.rectangle([x, y, x + s, y + s], fill=bg)
    cx, cy = x + s / 2, y + s / 2
    R = s * 0.44
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=fg, width=max(3, int(s * 0.035)))
    R2 = s * 0.375
    d.ellipse([cx - R2, cy - R2, cx + R2, cy + R2], outline=acc, width=max(2, int(s * 0.02)))
    pts, band = crown_path(cx, cy + s * 0.02, s * 0.42, s * 0.22)
    d.polygon(pts, fill=fg)
    d.rectangle(band, fill=fg)
    for jx in (cx - s * 0.21 * 0.74, cx, cx + s * 0.21 * 0.74):
        jy = cy - s * 0.115 if jx == cx else cy - s * 0.075
        r = s * 0.028
        d.ellipse([jx - r, jy - r, jx + r, jy + r], fill=acc)

def cenefa_band(d, x0, x1, y, h, fg=COBALTO, bg=GLAZE, acc=ORO):
    """Border band: alternating diamonds and dots between two rules."""
    lw = max(4, int(h * 0.08))
    d.rectangle([x0, y, x1, y + lw], fill=fg)
    d.rectangle([x0, y + h - lw, x1, y + h], fill=fg)
    s = h * 0.62
    cy = y + h / 2
    n = int((x1 - x0) // s)
    pad = ((x1 - x0) - n * s) / 2
    for i in range(n):
        cx = x0 + pad + i * s + s / 2
        q = s * 0.36
        if i % 2 == 0:
            d.polygon([(cx - q, cy), (cx, cy - q), (cx + q, cy), (cx, cy + q)], fill=fg)
            q2 = s * 0.17
            d.polygon([(cx - q2, cy), (cx, cy - q2), (cx + q2, cy), (cx, cy + q2)], fill=bg)
        else:
            r = s * 0.13
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=acc)

# ---------------------------------------------------------------- 1. Camiseta — panel de azulejos
def camiseta():
    W, H = 3600, 4800
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)
    cols, rows = 4, 4
    m = 320                      # outer margin of the panel
    gap = 24                     # grout gap
    s = (W - 2 * m - (cols - 1) * gap) / cols
    top = 900
    # grout backing behind the panel only
    panel_w = cols * s + (cols - 1) * gap
    panel_h = rows * s + (rows - 1) * gap
    d.rectangle([m - 30, top - 30, m + panel_w + 30, top + panel_h + 30], fill=JUNTA + (255,))
    for r in range(rows):
        for c in range(cols):
            x = int(m + c * (s + gap))
            y = int(top + r * (s + gap))
            if (1 <= c <= 2) and (1 <= r <= 2):
                continue
            if (r + c) % 2 == 0:
                t = clipped_tile(tile_rosette, s, fg=COBALTO, bg=GLAZE)
            else:
                t = clipped_tile(tile_star_cross, s, fg=COBALTO, bg=GLAZE, acc=AZUL)
            art.paste(t, (x, y))
    # central 2x2 crown medallion
    X = int(m + 1 * (s + gap)); Y = int(top + 1 * (s + gap))
    S = 2 * s + gap
    art.paste(clipped_tile(tile_crown, S, fg=COBALTO, bg=GLAZE, acc=ORO), (X, Y))
    # cenefa top & bottom
    cenefa_band(d, m, W - m, top - 220, 140, fg=COBALTO + (255,), bg=GLAZE + (255,), acc=ORO + (255,))
    bot = top + panel_h
    cenefa_band(d, m, W - m, bot + 80, 140, fg=COBALTO + (255,), bg=GLAZE + (255,), acc=ORO + (255,))
    # lettering
    text_tracked(d, (W / 2, 330), "STREET ROYALTY", F(SANS_B, 200), COBALTO + (255,), tracking=48, center=True)
    text_tracked(d, (W / 2, bot + 330), "AZULEJO REAL", F(SERIF_B, 190), COBALTO + (255,), tracking=64, center=True)
    text_tracked(d, (W / 2, bot + 590), "CERÁMICA · SRHOOD · MMXXVI", F(SANS, 100), AZUL + (255,), tracking=36, center=True)
    return art

# ---------------------------------------------------------------- 2. Sudadera — cenefa mosaico
def sudadera():
    W, H = 3600, 4800
    art = Image.new("RGB", (W, H), GLAZE)
    d = ImageDraw.Draw(art)
    # wide central band of star-cross tessellation
    band_top, band_h = 1500, 1800
    s = 450
    for r in range(4):
        for c in range(8):
            x = c * s; y = band_top + r * s
            if (r + c) % 2 == 0:
                t = clipped_tile(tile_star_cross, s, fg=COBALTO, bg=GLAZE, acc=AZUL)
            else:
                t = clipped_tile(tile_rosette, s, fg=AZUL, bg=GLAZE, acc=ORO)
            art.paste(t, (int(x), int(y)))
    # frame the band
    for yy in (band_top - 40, band_top + 4 * s + 8):
        d.rectangle([0, yy, W, yy + 32], fill=COBALTO)
    cenefa_band(d, 0, W, band_top - 240, 150, fg=COBALTO, acc=ORO)
    cenefa_band(d, 0, W, band_top + 4 * s + 90, 150, fg=COBALTO, acc=ORO)
    # wordmark above
    text_tracked(d, (W / 2, 660), "SRHOOD", F(SANS_B, 300), COBALTO, tracking=90, center=True)
    text_tracked(d, (W / 2, 1030), "MOSAICO REAL — MMXXVI", F(SANS, 100), AZUL, tracking=40, center=True)
    # crown seal below
    pts, band = crown_path(W / 2, 4130, 560, 300)
    d.polygon(pts, fill=COBALTO)
    d.rectangle(band, fill=COBALTO)
    for jx, jy in [(W/2 - 560*0.5*0.74, 4130 - 300*0.14), (W/2, 4130 - 300*0.30), (W/2 + 560*0.5*0.74, 4130 - 300*0.14)]:
        d.ellipse([jx - 26, jy - 26, jx + 26, jy + 26], fill=ORO)
    return glaze_texture(art, strength=0.035)

# ---------------------------------------------------------------- 3. Hoodie — estrella de ocho (zellige)
def hoodie():
    W, H = 3600, 4800
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)
    # big interlaced 8-point star, white + celeste + gold on royal garment
    cx, cy = W / 2, 1980
    R = 1500
    d.polygon(star8(cx, cy, R, rot=math.pi / 8), fill=GLAZE + (255,))
    d.polygon(star8(cx, cy, R * 0.86, rot=math.pi / 8), fill=(20, 40, 96, 255))
    d.polygon(star8(cx, cy, R * 0.72, rot=math.pi / 8), fill=CELESTE + (255,))
    d.polygon(star8(cx, cy, R * 0.58, rot=math.pi / 8), fill=(20, 40, 96, 255))
    d.polygon(star8(cx, cy, R * 0.44, rot=math.pi / 8), fill=GLAZE + (255,))
    # gold ring + crown center
    d.ellipse([cx - 560, cy - 560, cx + 560, cy + 560], outline=ORO + (255,), width=26)
    pts, band = crown_path(cx, cy + 30, 620, 330)
    d.polygon(pts, fill=ORO + (255,))
    d.rectangle(band, fill=ORO + (255,))
    for jx, jy in [(cx - 310*0.74, cy - 30), (cx, cy - 78), (cx + 310*0.74, cy - 30)]:
        d.ellipse([jx - 30, jy - 30, jx + 30, jy + 30], fill=GLAZE + (255,))
    # radiating mini stars in the star's outer field
    rnd = random.Random(4)
    for i in range(8):
        a = math.pi / 8 + math.pi * i / 4
        px, py = cx + R * 1.12 * math.cos(a), cy + R * 1.12 * math.sin(a)
        if py < 120 or py > 3660: continue
        d.polygon(star8(px, py, 130, rot=math.pi / 8), fill=ORO_HI + (255,))
    # lettering
    dd = ImageDraw.Draw(art)
    text_tracked(dd, (W / 2, 3760), "ESTRELLA DE OCHO", F(SANS_B, 170), GLAZE + (255,), tracking=52, center=True)
    text_tracked(dd, (W / 2, 3990), "ZELLIGE · STREET ROYALTY · MMXXVI", F(SANS, 92), CELESTE + (255,), tracking=34, center=True)
    return art

# ---------------------------------------------------------------- 4. Hi-top quarters + tongue
def hitop_quarters():
    S = 2250
    art = Image.new("RGB", (S, S), GLAZE)
    d = ImageDraw.Draw(art)
    s = S / 5
    for r in range(5):
        for c in range(5):
            if (r + c) % 2 == 0:
                t = clipped_tile(tile_star_cross, s, fg=COBALTO, bg=GLAZE, acc=AZUL)
            else:
                t = clipped_tile(tile_rosette, s, fg=AZUL, bg=GLAZE, acc=ORO)
            art.paste(t, (int(c * s), int(r * s)))
    return glaze_texture(art, strength=0.03)

def hitop_tongue():
    S = 2250
    art = Image.new("RGB", (S, S), COBALTO)
    d = ImageDraw.Draw(art)
    tile_crown(d, S * 0.15, S * 0.15, S * 0.70, fg=GLAZE, bg=COBALTO, acc=ORO)
    text_tracked(d, (S / 2, S * 0.88), "SRHOOD", F(SANS_B, 150), GLAZE, tracking=48, center=True)
    return glaze_texture(art, strength=0.03)

# ---------------------------------------------------------------- 5. Slip-on mujer — trencadís
def trencadis():
    S = 3000
    art = Image.new("RGB", (S, S), (233, 230, 222))   # mortar
    d = ImageDraw.Draw(art)
    rnd = random.Random(23)
    # dense mosaic: jittered grid of near-touching shards, seamless by wrapping
    step = 210
    pts = {}
    n = S // step
    for gy in range(n):
        for gx in range(n):
            pts[(gx, gy)] = ((gx + 0.5 + rnd.uniform(-0.22, 0.22)) * step,
                             (gy + 0.5 + rnd.uniform(-0.22, 0.22)) * step)
    palette = [COBALTO, AZUL, CELESTE, GLAZE, COBALTO, AZUL, COBALTO, GLAZE, CELESTE, ORO]
    for (gx, gy), (px, py) in pts.items():
        col = palette[rnd.randrange(len(palette))]
        # shard: irregular polygon nearly filling its cell
        nv = rnd.randint(5, 8)
        verts = []
        for i in range(nv):
            a = 2 * math.pi * i / nv + rnd.uniform(-0.18, 0.18)
            r = step * rnd.uniform(0.52, 0.74)
            verts.append((px + r * math.cos(a), py + r * math.sin(a)))
        for ox in (-S, 0, S):
            for oy in (-S, 0, S):
                d.polygon([(vx + ox, vy + oy) for vx, vy in verts], fill=col,
                          outline=(218, 215, 206), width=10)
    # a few gold crown shards
    for _ in range(5):
        px, py = rnd.uniform(S*0.12, S*0.88), rnd.uniform(S*0.12, S*0.88)
        pts_c, band_c = crown_path(px, py, 260, 140)
        d.polygon(pts_c, fill=ORO)
        d.rectangle(band_c, fill=ORO)
        d.line(pts_c + [pts_c[0]], fill=(218, 215, 206), width=10)
    return glaze_texture(art, strength=0.03)

# ---------------------------------------------------------------- 6. Calcetines — cuerda seca
def calcetines():
    W, H = 1400, 2400
    art = Image.new("RGB", (W, H), COBALTO)
    d = ImageDraw.Draw(art)
    s = 200
    for r in range(H // s + 2):
        for c in range(W // s + 2):
            cx = c * s + (s / 2 if r % 2 else 0)
            cy = r * s * 0.86
            col = GLAZE if (r + c) % 3 else ORO_HI
            d.polygon(star8(cx, cy, s * 0.30, rot=math.pi / 8), fill=col)
            d.polygon(star8(cx, cy, s * 0.13, rot=math.pi / 8), fill=COBALTO)
    # crown band near cuff
    d.rectangle([0, 260, W, 300], fill=ORO)
    d.rectangle([0, 640, W, 680], fill=ORO)
    pts, band = crown_path(W / 2, 470, 300, 160)
    d.polygon(pts, fill=GLAZE)
    d.rectangle(band, fill=GLAZE)
    return glaze_texture(art, strength=0.03)

jobs = {
    "azulejo_tee_front.png": camiseta,
    "azulejo_sudadera_front.png": sudadera,
    "azulejo_hoodie_front.png": hoodie,
    "azulejo_hitop_quarters.png": hitop_quarters,
    "azulejo_hitop_tongue.png": hitop_tongue,
    "azulejo_sliphon_trencadis.png": trencadis,
    "azulejo_socks.png": calcetines,
}
if __name__ == "__main__":
    for name, fn in jobs.items():
        img = fn()
        img.save(os.path.join(OUT, name))
        print("done", name, img.size)
