#!/usr/bin/env python3
# Cápsula Damasco — Seda Real · SRHOOD
# Seamless baroque damask (ogee lattice + crowned medallion) in emerald & gold.
# Outputs: print files for tee / crewneck / premium hoodie / high-tops / slip-ons /
# reversible bucket hat. All pattern tiles are wrap-around seamless.
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def F(p, s): return ImageFont.truetype(p, s)

# ---------------------------------------------------------------- palettes
ESM_OSCURO = (10, 26, 21)     # near-black emerald field (men's shoes)
ESM        = (23, 82, 67)     # emerald
ESM_HI     = (46, 139, 103)   # light emerald
ORO_DIM    = (140, 110, 56)
ORO        = (201, 164, 76)
ORO_HI     = (232, 202, 122)
MARFIL     = (239, 232, 216)
MARFIL_HI  = (248, 244, 234)

# ---------------------------------------------------------------- curve helpers
def catmull_rom(pts, samples=18):
    """Smooth open curve through pts (Catmull-Rom), returns polyline."""
    if len(pts) < 3:
        return list(pts)
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for s in range(samples):
            t = s / samples
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out

def stroke_taper(draw, pts, color, w0, w1):
    """Polyline with linearly tapering width (dots along path)."""
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        r = (w0 + (w1 - w0) * (i / max(1, n - 1))) / 2
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

def spiral(cx, cy, r0, r1, a0, a1, turns_samples=90, mirror=1):
    """Archimedean spiral polyline from angle a0..a1 (deg), radius r0..r1."""
    pts = []
    for i in range(turns_samples + 1):
        t = i / turns_samples
        a = math.radians(a0 + (a1 - a0) * t)
        r = r0 + (r1 - r0) * t
        pts.append((cx + mirror * r * math.cos(a), cy + r * math.sin(a)))
    return pts

def petal(draw, cx, cy, w, h, angle_deg, fill, outline=None, ow=0):
    """Teardrop petal sprite pasted rotated is expensive; draw as polygon."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for i in range(37):
        t = i / 36 * 2 * math.pi
        # teardrop: pointed at +y tip
        px = (w / 2) * math.sin(t) * (1 - 0.55 * (1 + math.cos(t)) / 2)
        py = (h / 2) * math.cos(t)
        pts.append((cx + px * ca - py * sa, cy + px * sa + py * ca))
    draw.polygon(pts, fill=fill, outline=outline, width=ow)

def crown(draw, cx, cy, w, h, fill, pearl, line=None, lw=0):
    l, r = cx - w / 2, cx + w / 2
    b, t = cy + h / 2, cy - h / 2
    dip = b - h * 0.40
    pts = [(l, b), (l, t + h * 0.32), (l + w * 0.19, dip),
           (cx - w * 0.16, t + h * 0.10), (cx, dip - h * 0.04),
           (cx + w * 0.16, t + h * 0.10), (r - w * 0.19, dip),
           (r, t + h * 0.32), (r, b)]
    if fill:
        draw.polygon(pts, fill=fill)
        draw.rectangle([l, b + h * 0.07, r, b + h * 0.20], fill=fill)
    if line:
        draw.line(pts + [pts[0]], fill=line, width=lw, joint="curve")
        draw.rectangle([l, b + h * 0.07, r, b + h * 0.20], outline=line, width=lw)
    pr = h * 0.075
    for px, py in [(l, t + h * 0.32), (cx - w * 0.16, t + h * 0.10),
                   (cx, dip - h * 0.04), (cx + w * 0.16, t + h * 0.10),
                   (r, t + h * 0.32)]:
        draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=pearl)

# ---------------------------------------------------------------- medallion sprite
def medallion(size, col_frame, col_leaf, col_crown, col_pearl, col_accent,
              with_lattice_tips=True):
    """Crowned damask medallion, bilaterally symmetric. RGBA sprite.
    size = (w, h) of sprite; artwork drawn in half, mirrored."""
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w / 2
    # ---- ogee frame (pointed oval), double stroke
    def ogee(scale, width):
        half = [(cx, h * 0.015)]
        half += catmull_rom([(cx, h * 0.015),
                             (cx + w * 0.26 * scale, h * 0.20),
                             (cx + w * 0.42 * scale, h * 0.46),
                             (cx + w * 0.30 * scale, h * 0.74),
                             (cx, h * 0.985)], 16)
        d.line(half, fill=col_frame, width=width, joint="curve")
        mir = [(2 * cx - x, y) for x, y in half]
        d.line(mir, fill=col_frame, width=width, joint="curve")
    lw = max(3, int(w * 0.012))
    ogee(1.00, lw * 2)
    ogee(0.90, lw)
    # pearls on frame
    pr = w * 0.014
    for t in (0.20, 0.46, 0.74):
        for s in (1, -1):
            x = cx + s * (w * 0.26 if t in (0.20,) else w * (0.42 if t == 0.46 else 0.30))
            y = h * t
            d.ellipse([x - pr, y - pr, x + pr, y + pr], fill=col_pearl)
    # ---- finials (fleur) top & bottom
    for ytip, sgn in [(h * 0.015, 1), (h * 0.985, -1)]:
        petal(d, cx, ytip + sgn * h * 0.045, w * 0.055, h * 0.075, 180 if sgn == 1 else 0, col_frame)
        for s in (-1, 1):
            petal(d, cx + s * w * 0.035, ytip + sgn * h * 0.055, w * 0.04, h * 0.055,
                  (150 if s < 0 else 210) if sgn == 1 else (30 if s > 0 else -30), col_accent)
    # ---- central crown
    crown(d, cx, h * 0.315, w * 0.30, h * 0.115, col_crown, col_pearl)
    # ---- palmette fan under crown (radiating petals)
    fy = h * 0.60
    n = 9
    for i in range(n):
        a = -90 + (i - (n - 1) / 2) * 21
        L = h * (0.155 - 0.018 * abs(i - (n - 1) / 2))
        px = cx + math.cos(math.radians(a)) * L * 0.62
        py = fy + math.sin(math.radians(a)) * L * 0.62
        petal(d, px, py, w * 0.052, L, a + 90, col_leaf if i % 2 == 0 else col_accent)
    d.ellipse([cx - w * 0.045, fy - w * 0.045, cx + w * 0.045, fy + w * 0.045], fill=col_crown)
    d.ellipse([cx - w * 0.022, fy - w * 0.022, cx + w * 0.022, fy + w * 0.022], fill=col_pearl)
    # ---- acanthus scrolls flanking bottom
    for s in (-1, 1):
        pts = spiral(cx + s * w * 0.17, h * 0.80, w * 0.20, w * 0.02, 90, 420, 80, mirror=s)
        stroke_taper(d, pts, col_leaf, lw * 1.9, lw * 0.5)
        # leaf tips on scroll
        for tt in (0.25, 0.55):
            ix = int(len(pts) * tt)
            x, y = pts[ix]
            petal(d, x, y, w * 0.035, h * 0.05, s * 40, col_accent)
    # ---- upper scrolls (smaller, inverted)
    for s in (-1, 1):
        pts = spiral(cx + s * w * 0.15, h * 0.175, w * 0.14, w * 0.015, 270, 620, 70, mirror=s)
        stroke_taper(d, pts, col_leaf, lw * 1.5, lw * 0.4)
    # ---- lattice connection tips (tiny diamonds at the 4 compass points)
    if with_lattice_tips:
        for x, y in [(cx, h * 0.002), (cx, h * 0.998)]:
            r = w * 0.016
            d.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=col_pearl)
    return img

def rosette(size, col_petal, col_alt, col_core):
    """8-petal secondary rosette, RGBA sprite."""
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s / 2
    for i in range(8):
        a = i * 45
        px = c + math.cos(math.radians(a)) * s * 0.26
        py = c + math.sin(math.radians(a)) * s * 0.26
        petal(d, px, py, s * 0.18, s * 0.40, a + 90, col_petal if i % 2 == 0 else col_alt)
    d.ellipse([c - s * 0.09, c - s * 0.09, c + s * 0.09, c + s * 0.09], fill=col_core)
    d.ellipse([c - s * 0.04, c - s * 0.04, c + s * 0.04, c + s * 0.04], fill=col_petal)
    return img

# ---------------------------------------------------------------- seamless tile
def paste_wrapped(base, sprite, x, y):
    """Paste sprite centered at (x, y) with wrap-around on the tile."""
    W, H = base.size
    sw, sh = sprite.size
    x0, y0 = int(x - sw / 2), int(y - sh / 2)
    for dx in (-W, 0, W):
        for dy in (-H, 0, H):
            px, py = x0 + dx, y0 + dy
            if px + sw < 0 or py + sh < 0 or px >= W or py >= H:
                continue
            base.paste(sprite, (px, py), sprite)

def damask_tile(TW, TH, field, frame, leaf, crown_c, pearl, accent, lattice,
                supersample=2):
    """Seamless damask tile: ogee lattice + central medallion + corner rosettes."""
    W, H = TW * supersample, TH * supersample
    img = Image.new("RGB", (W, H), field)
    d = ImageDraw.Draw(img)
    # ogee lattice: sinusoid families with period H vertical, W horizontal
    lwd = max(2, int(W * 0.004))
    big = Image.new("RGB", (3 * W, 3 * H), field)
    bd = ImageDraw.Draw(big)
    A = W * 0.24
    for k in range(-1, 7):
        base_x = k * (W / 2)
        phase = math.pi * k
        pts = [(base_x + A * math.sin(2 * math.pi * y / H + phase), y)
               for y in range(0, 3 * H + 1, max(4, H // 160))]
        bd.line(pts, fill=lattice, width=lwd, joint="curve")
    img.paste(big.crop((W, H, 2 * W, 2 * H)), (0, 0))
    d = ImageDraw.Draw(img)
    # medallion at center
    med = medallion((int(W * 0.62), int(H * 0.86)), frame, leaf, crown_c, pearl, accent)
    paste_wrapped(img, med, W / 2, H / 2)
    # corner rosettes (wrap to all four corners)
    ros = rosette(int(W * 0.30), leaf, accent, crown_c)
    paste_wrapped(img, ros, 0, 0)
    # edge mid-point buds
    bud = rosette(int(W * 0.13), accent, frame, pearl)
    paste_wrapped(img, bud, W / 2, 0)
    paste_wrapped(img, bud, 0, H / 2)
    out = img.resize((TW, TH), Image.LANCZOS)
    return out

def tiled(tile, nx, ny):
    tw, th = tile.size
    img = Image.new("RGB", (tw * nx, th * ny))
    for i in range(nx):
        for j in range(ny):
            img.paste(tile, (i * tw, j * th))
    return img

# ---------------------------------------------------------------- garment prints
def text_tracked(draw, xy, text, font, fill, tracking=0, center=True):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if center:
        x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking
    return total

def print_tee():
    """Front print: grand medallion + wordmark. Transparent PNG 3000x4000."""
    W, H = 3000, 4000
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    med = medallion((int(W * 0.88), int(H * 0.62)), ORO, ESM_HI, ORO, ORO_HI, ESM,
                    with_lattice_tips=False)
    img.paste(med, (int(W * 0.06), int(H * 0.06)), med)
    d = ImageDraw.Draw(img)
    y = H * 0.745
    d.rectangle([W * 0.20, y, W * 0.80, y + 6], fill=ORO)
    text_tracked(d, (W / 2, y + 60), "STREET ROYALTY", F(SERIF_B, 190), MARFIL, tracking=26)
    text_tracked(d, (W / 2, y + 330), "SEDA REAL · DAMASCO", F(SANS, 92), ORO, tracking=48)
    text_tracked(d, (W / 2, y + 490), "SRHOOD — MMXXVI", F(SANS, 62), (150, 150, 150), tracking=30)
    return img

def print_hoodie():
    """Front print: compact medallion, arch text above. Transparent PNG."""
    W, H = 3000, 3200
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # arch text
    cx, cy, R = W / 2, H * 0.53, W * 0.42
    txt = "· STREET ROYALTY HOOD ·"
    f = F(SERIF_B, 120)
    arcs = [max(d.textlength(c, font=f), f.size * 0.30) / R for c in txt]
    a = -math.pi / 2 - sum(arcs) / 2
    for c, arc in zip(txt, arcs):
        am = a + arc / 2
        x, y = cx + R * math.cos(am), cy + R * math.sin(am)
        s = f.size * 3
        ch = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        cd = ImageDraw.Draw(ch)
        cd.text((s / 2, s / 2), c, font=f, fill=ORO, anchor="mm")
        ch = ch.rotate(-math.degrees(am) - 90, resample=Image.BICUBIC, center=(s / 2, s / 2))
        img.paste(ch, (int(x - s / 2), int(y - s / 2)), ch)
        a += arc
    med = medallion((int(W * 0.60), int(H * 0.60)), ORO, ESM_HI, ORO, ORO_HI, ESM,
                    with_lattice_tips=False)
    img.paste(med, (int(W * 0.20), int(H * 0.26)), med)
    d = ImageDraw.Draw(img)
    text_tracked(d, (W / 2, H * 0.895), "SEDA REAL", F(SANS_B, 110), MARFIL, tracking=90)
    return img

def print_sweat():
    """Chest band of damask strip + wordmark, gold on forest green. PNG."""
    W, H = 3000, 2400
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # band: three small medallions row, clipped by rules
    band_y0, band_y1 = H * 0.10, H * 0.52
    d.rectangle([W * 0.06, band_y0, W * 0.94, band_y0 + 8], fill=ORO)
    d.rectangle([W * 0.06, band_y1, W * 0.94, band_y1 + 8], fill=ORO)
    mw = int(W * 0.235)
    med = medallion((mw, int(band_y1 - band_y0 - 60)), ORO, ORO_HI, ORO, MARFIL, ORO_DIM,
                    with_lattice_tips=False)
    for i in range(3):
        x = W / 2 + (i - 1) * W * 0.30 - mw / 2
        img.paste(med, (int(x), int(band_y0 + 30)), med)
    ros = rosette(int(W * 0.075), ORO, ORO_HI, MARFIL)
    for i in (-1, 1):
        img.paste(ros, (int(W / 2 + i * W * 0.45 - ros.size[0] / 2),
                        int((band_y0 + band_y1) / 2 - ros.size[0] / 2)), ros)
    d = ImageDraw.Draw(img)
    text_tracked(d, (W / 2, H * 0.60), "STREET ROYALTY", F(SERIF_B, 200), MARFIL, tracking=24)
    text_tracked(d, (W / 2, H * 0.79), "DAMASCO · TEJIDO EN ORO · MMXXVI", F(SANS, 80), ORO_HI, tracking=34)
    return img

def print_bucket_inside():
    """Ivory diaper pattern: sparse gold buds on marfil. Seamless tile."""
    T = 600
    img = Image.new("RGB", (T, T), MARFIL)
    bud = rosette(int(T * 0.16), ORO, ESM, ORO_DIM)
    paste_wrapped(img, bud, T * 0.25, T * 0.25)
    paste_wrapped(img, bud, T * 0.75, T * 0.75)
    dot = Image.new("RGBA", (14, 14), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dot)
    dd.ellipse([3, 3, 11, 11], fill=ORO_DIM)
    paste_wrapped(img, dot, T * 0.75, T * 0.25)
    paste_wrapped(img, dot, T * 0.25, T * 0.75)
    return img

# ---------------------------------------------------------------- build all
if __name__ == "__main__":
    # 1) men's high-tops: emerald-on-dark tile
    t_dark = damask_tile(1000, 1200, ESM_OSCURO, ORO, ESM, ORO, ORO_HI, ESM_HI,
                         lattice=(20, 46, 37))
    tiled(t_dark, 3, 3).save(f"{OUT}/dam04_hightop.jpg", quality=95)
    # 2) women's slip-ons: emerald-on-ivory tile
    t_ivory = damask_tile(1000, 1200, MARFIL, ESM, ESM, ORO, ORO, ESM_HI,
                          lattice=(214, 202, 176))
    tiled(t_ivory, 3, 3).save(f"{OUT}/dam05_slipon.jpg", quality=95)
    # 3) bucket hat outside: gold-on-emerald tile
    t_emer = damask_tile(1000, 1200, (18, 56, 44), ORO, ORO_HI, ORO, MARFIL, ORO_DIM,
                         lattice=(30, 76, 60))
    tiled(t_emer, 3, 3).crop((0, 0, 2400, 2400)).save(f"{OUT}/dam06_bucket_out.jpg", quality=95)
    tiled(print_bucket_inside(), 4, 4).save(f"{OUT}/dam06_bucket_in.jpg", quality=95)
    # 4) garment prints
    print_tee().save(f"{OUT}/dam01_tee_front.png")
    print_sweat().save(f"{OUT}/dam02_sweat_front.png")
    print_hoodie().save(f"{OUT}/dam03_hoodie_front.png")
    print("done:", sorted(os.listdir(OUT)))
