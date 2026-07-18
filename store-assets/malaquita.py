#!/usr/bin/env python3
# Cápsula Malaquita — Piedra Real. Procedural malachite (banded stone) engine +
# 6 print files for the SRHOOD drop: tee / sweatshirt / hoodie (DTG PNG) and
# high-tops / athletic shoes / socks (all-over JPG).
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

def F(path, size): return ImageFont.truetype(path, size)

ORO = (206, 168, 74)
ORO_HI = (240, 212, 130)
ORO_LO = (140, 108, 40)

# Malachite band palette, dark→light (polished stone greens).
MALA = [
    (5, 32, 24), (8, 46, 33), (12, 62, 43), (17, 80, 54),
    (24, 100, 66), (35, 122, 80), (52, 144, 95), (76, 166, 112),
    (104, 186, 130), (134, 203, 149),
]

def _lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))

def value_noise(w, h, cells, seed, octaves=3, persistence=0.55):
    """Smooth fBm value noise in [0,1] built from PIL bicubic upscaling."""
    rnd = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(2, int(cells * (2 ** o)))
        g = (rnd.random((c, c), np.float32) * 255).astype(np.uint8)
        layer = Image.fromarray(g, "L").resize((w, h), Image.BICUBIC)
        out += np.asarray(layer, np.float32) / 255.0 * amp
        tot += amp
        amp *= persistence
    return out / tot

def band_profile(seed, n_bands=140, res=8192):
    """Irregular malachite band stack → (rgb lookup [res,3], gold mask [res])."""
    rnd = random.Random(seed)
    widths, cols = [], []
    for i in range(n_bands):
        # runs of thin bands between broad ones, like real malachite
        w = rnd.uniform(0.25, 1.0) if rnd.random() < 0.55 else rnd.uniform(1.2, 3.2)
        widths.append(w)
        base = rnd.choice(range(len(MALA)))
        cols.append(base)
    total = sum(widths)
    rgb = np.zeros((res, 3), np.float32)
    gold = np.zeros(res, np.float32)
    pos = 0.0
    for i, (w, ci) in enumerate(zip(widths, cols)):
        a = int(pos / total * res)
        b = max(a + 2, int((pos + w) / total * res))
        pos += w
        n = b - a
        t = np.linspace(0, 1, n, dtype=np.float32)
        # each band: dark rim → bright core → dark rim (polished depth)
        core = np.array(MALA[ci], np.float32)
        rim = np.array(MALA[max(0, ci - 3)], np.float32)
        prof = 0.5 - 0.5 * np.cos(t * math.pi * 2)  # 0 rim → 1 core → 0 rim
        seg = rim[None, :] + (core - rim)[None, :] * prof[:, None] ** 0.8
        rgb[a:b] = seg
        # occasional gold vein hugging a band boundary
        if rnd.random() < 0.24:
            vw = max(3, int(n * rnd.uniform(0.10, 0.20)))
            side = rnd.random() < 0.5
            s = a if side else b - vw
            gold[s:s + vw] = np.linspace(1, 0, vw) if side else np.linspace(0, 1, vw)
    return rgb, gold

def malachite(w, h, seed, n_seeds=5, freq=26.0, warp_amt=0.55, gold_amt=1.0):
    """Full malachite RGB array (h,w,3) uint8."""
    rnd = random.Random(seed)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    xs /= min(w, h); ys /= min(w, h)
    # domain warp
    wx = value_noise(w, h, 3, seed * 7 + 1, octaves=4) - 0.5
    wy = value_noise(w, h, 3, seed * 7 + 2, octaves=4) - 0.5
    xw = xs + wx * warp_amt
    yw = ys + wy * warp_amt
    # soft-min distance to nuclei → concentric "eyes"
    d = None
    for i in range(n_seeds):
        px, py = rnd.uniform(-0.2, w / min(w, h) + 0.2), rnd.uniform(-0.2, h / min(w, h) + 0.2)
        di = np.sqrt((xw - px) ** 2 + (yw - py) ** 2) * rnd.uniform(0.8, 1.25)
        d = di if d is None else -np.log(np.exp(-d * 9) + np.exp(-di * 9)) / 9
    phase = (d * freq) % 1.0
    stack = d * freq / 40.0  # slow drift through the profile
    prof_rgb, prof_gold = band_profile(seed * 13 + 5)
    idx = ((stack + phase) % 1.0 * (len(prof_rgb) - 1)).astype(np.int32)
    img = prof_rgb[idx]
    gold = prof_gold[idx] * gold_amt
    # fine micro-striations along the banding
    stria = value_noise(w, h, 60, seed * 7 + 3, octaves=2)
    img *= (0.92 + 0.16 * np.sin(d * freq * 14 + stria * 6)[..., None] * 0.5 + 0.04)
    # broad sheen
    sheen = value_noise(w, h, 2, seed * 7 + 4, octaves=2)
    img *= (0.88 + 0.28 * sheen[..., None])
    # lay gold veins with lit edge
    gcol = np.array(ORO, np.float32)
    ghi = np.array(ORO_HI, np.float32)
    gmask = np.clip(gold, 0, 1)[..., None]
    gshade = (0.65 + 0.6 * value_noise(w, h, 8, seed * 7 + 6, octaves=2))[..., None]
    gold_rgb = (gcol * 0.75 + ghi * 0.25) * gshade
    img = img * (1 - gmask) + gold_rgb * gmask
    # gentle S-curve for stone depth
    x = np.clip(img / 255.0, 0, 1)
    img = (x + (x - x * x) * (x * 2 - 1) * 0.55) * 255
    return np.clip(img, 0, 255).astype(np.uint8)

def malachite_img(w, h, seed, **kw):
    return Image.fromarray(malachite(w, h, seed, **kw), "RGB")

# ---------- shared drawing helpers ----------

def crown_mask(w, h):
    """Five-point crown + base band as a white-on-black L mask."""
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    cw, ch = w * 0.88, h * 0.76
    cx = w / 2
    l, r = cx - cw / 2, cx + cw / 2
    t, b = h * 0.05, h * 0.05 + ch
    dipy = b - ch * 0.40
    pts = [(l, b),
           (l, t + ch * 0.30), (l + cw * 0.185, dipy),
           (cx - cw * 0.155, t + ch * 0.12), (cx, dipy - ch * 0.02),
           (cx + cw * 0.155, t + ch * 0.12), (r - cw * 0.185, dipy),
           (r, t + ch * 0.30), (r, b)]
    d.polygon(pts, fill=255)
    # jewels on the three peaks
    for px, py in [(l, t + ch * 0.30), (cx, dipy - ch * 0.02), (r, t + ch * 0.30)]:
        rr = cw * 0.035
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=255)
    # base band
    bb_t = b + ch * 0.055
    d.rounded_rectangle([l, bb_t, r, bb_t + ch * 0.16], radius=ch * 0.05, fill=255)
    return m

def text_tracked(draw, xy, text, font, fill, tracking=0, center=False, stroke=0, stroke_fill=None):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if center: x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += cw + tracking
    return total

def circular_text(img, center, radius, text, font, fill, start_deg=-90, clockwise=True):
    cx, cy = center
    tmp = ImageDraw.Draw(img)
    arcs = [max(tmp.textlength(c, font=font), font.size * 0.30) / radius for c in text]
    total = sum(arcs)
    a = math.radians(start_deg) - (total / 2 if clockwise else -total / 2)
    for c, arc in zip(text, arcs):
        a_mid = a + (arc / 2 if clockwise else -arc / 2)
        x = cx + radius * math.cos(a_mid)
        y = cy + radius * math.sin(a_mid)
        size = font.size * 3
        ch = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        cd = ImageDraw.Draw(ch)
        cd.text((size / 2, size / 2), c, font=font, fill=fill, anchor="mm")
        deg = math.degrees(a_mid) + (90 if clockwise else -90)
        ch = ch.rotate(-deg, resample=Image.BICUBIC, center=(size / 2, size / 2))
        img.alpha_composite(ch, (int(x - size / 2), int(y - size / 2)))
        a += arc if clockwise else -arc

def outline_from_mask(mask, width):
    grow = mask.filter(ImageFilter.MaxFilter(width * 2 + 1))
    return Image.composite(Image.new("L", mask.size, 255), Image.new("L", mask.size, 0),
                           grow).point(lambda p: p) if False else grow

def gold_ring(draw, cx, cy, r, w):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ORO, width=w)

# ---------- 6 print files ----------

def tee_front():
    """3000x4000 transparent PNG — Corona de Malaquita chest piece."""
    W, H = 3000, 4000
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cw, chh = 2350, 1750
    cm = crown_mask(cw, chh)
    tex = malachite_img(cw, chh, seed=41, n_seeds=4, freq=22, warp_amt=0.5)
    crown = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    crown.paste(tex, (0, 0), cm)
    # gold contour
    edge = cm.filter(ImageFilter.MaxFilter(19))
    ring = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    gold_tex = Image.new("RGBA", (cw, chh), ORO + (255,))
    ring.paste(gold_tex, (0, 0), edge)
    base = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    base.alpha_composite(ring)
    base.alpha_composite(crown)
    x0 = (W - cw) // 2
    y0 = 520
    img.alpha_composite(base, (x0, y0))
    d = ImageDraw.Draw(img)
    ty = y0 + chh + 150
    text_tracked(d, (W / 2, ty), "STREET ROYALTY", F(SERIF_B, 168), ORO, tracking=46, center=True)
    text_tracked(d, (W / 2, ty + 260), "MALAQUITA REAL", F(SANS_B, 84), (223, 228, 224), tracking=110, center=True)
    text_tracked(d, (W / 2, ty + 440), "PIEDRA DE LA CORONA · MMXXVI", F(SERIF, 60), (170, 178, 172), tracking=24, center=True)
    img.save(os.path.join(OUT, "mal01_tee_front.png"))

def sweat_front():
    """3000x2400 transparent PNG — Estrato: banded stone slab + wordmark."""
    W, H = 3000, 2400
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sw, sh = 2620, 1180
    tex = malachite_img(sw, sh, seed=77, n_seeds=6, freq=30, warp_amt=0.62)
    slab = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(slab).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=90, fill=255)
    piece = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    piece.paste(tex, (0, 0), slab)
    pd = ImageDraw.Draw(piece)
    pd.rounded_rectangle([9, 9, sw - 10, sh - 10], radius=84, outline=ORO, width=14)
    pd.rounded_rectangle([44, 44, sw - 45, sh - 45], radius=62, outline=(0, 0, 0, 90), width=4)
    # engraved wordmark knocked into the stone
    knock = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    kd = ImageDraw.Draw(knock)
    text_tracked(kd, (sw / 2, sh / 2 - 185), "SRHOOD", F(SERIF_B, 370), (10, 26, 20, 235), tracking=48, center=True,
                 stroke=8, stroke_fill=ORO + (255,))
    piece.alpha_composite(knock)
    x0, y0 = (W - sw) // 2, 260
    img.alpha_composite(piece, (x0, y0))
    d = ImageDraw.Draw(img)
    ty = y0 + sh + 130
    text_tracked(d, (W / 2, ty), "ESTRATO REAL — MALAQUITA", F(SANS_B, 72), ORO, tracking=36, center=True)
    text_tracked(d, (W / 2, ty + 150), "FORMADO BAJO PRESIÓN · CORONADO POR NATURALEZA",
                 F(SERIF, 52), (185, 192, 187), tracking=10, center=True)
    img.save(os.path.join(OUT, "mal02_sweat_front.png"))

def hoodie_front():
    """3000x3200 transparent PNG — Sello de Malaquita medallion."""
    W, H = 3000, 3200
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    R = 1050
    cx, cy = W // 2, 520 + R
    disc = Image.new("L", (2 * R, 2 * R), 0)
    ImageDraw.Draw(disc).ellipse([0, 0, 2 * R - 1, 2 * R - 1], fill=255)
    tex = malachite_img(2 * R, 2 * R, seed=53, n_seeds=1, freq=34, warp_amt=0.42)
    med = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    med.paste(tex, (0, 0), disc)
    img.alpha_composite(med, (cx - R, cy - R))
    d = ImageDraw.Draw(img)
    for rr, wd in [(R + 14, 18), (R + 60, 8)]:
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=ORO, width=wd)
    # crown in gold at the medallion centre
    cm = crown_mask(760, 560)
    gold_crown = Image.new("RGBA", (760, 560), (0, 0, 0, 0))
    gold_crown.paste(Image.new("RGBA", (760, 560), ORO_HI + (255,)), (0, 0),
                     cm.filter(ImageFilter.MaxFilter(11)))
    inner = Image.new("RGBA", (760, 560), (0, 0, 0, 0))
    inner.paste(Image.new("RGBA", (760, 560), (10, 30, 23, 255)), (0, 0), cm)
    gold_crown.alpha_composite(inner)
    img.alpha_composite(gold_crown, (cx - 380, cy - 300))
    circular_text(img, (cx, cy), R - 150, "STREET ROYALTY HOOD", F(SERIF_B, 150), ORO_HI, start_deg=-90)
    circular_text(img, (cx, cy), R - 165, "EST. MMXXVI · PIEDRA REAL", F(SERIF_B, 110), ORO_HI,
                  start_deg=90, clockwise=False)
    ty = cy + R + 170
    text_tracked(d, (W / 2, ty), "MALAQUITA", F(SANS_B, 150), ORO, tracking=180, center=True)
    text_tracked(d, (W / 2, ty + 230), "LA CORONA ES MINERAL", F(SERIF, 68), (190, 196, 191), tracking=24, center=True)
    img.save(os.path.join(OUT, "mal03_hoodie_front.png"))

def hightop():
    """3000x3600 JPG AOP for men's high tops — bold banding."""
    tex = malachite_img(3000, 3600, seed=91, n_seeds=6, freq=30, warp_amt=0.6)
    tex.save(os.path.join(OUT, "mal04_hightop.jpg"), quality=92)

def athletic():
    """1950x3300 JPG AOP for women's athletic shoes — finer, lighter banding."""
    arr = malachite(1950, 3300, seed=29, n_seeds=7, freq=36, warp_amt=0.55)
    Image.fromarray(arr, "RGB").save(os.path.join(OUT, "mal05_athletic.jpg"), quality=92)

def socks():
    """1348x5657 JPG sublimated socks — dense eyes so pattern reads small."""
    tex = malachite_img(1348, 5657, seed=64, n_seeds=10, freq=34, warp_amt=0.5)
    tex.save(os.path.join(OUT, "mal06_socks.jpg"), quality=92)

ALL = {"tee": tee_front, "sweat": sweat_front, "hoodie": hoodie_front,
       "hightop": hightop, "athletic": athletic, "socks": socks}

if __name__ == "__main__":
    targets = sys.argv[1:] or list(ALL)
    for t in targets:
        print("render", t); ALL[t]()
    print("done →", OUT)
