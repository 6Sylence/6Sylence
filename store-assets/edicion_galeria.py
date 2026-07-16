#!/usr/bin/env python3
# Royal Ink — Edición Galería (Nº10–13): 4 premium poster designs for Street Royalty Hood
# Step up from royal_ink.py: numpy heightfields, generative contours, star glow,
# multi-stop gradients, vignette + film grain, plus detail-crop shots per piece.
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

W, H = 1600, 2400
NEGRO   = (12, 12, 14)
CREMA   = (242, 234, 217)
ARENA   = (216, 198, 160)
ORO     = (201, 164, 76)
ORO_HI  = (232, 202, 122)
BURDEOS = (74, 22, 32)
BURDEOS_HI = (122, 41, 55)
NAVY    = (23, 31, 51)
NAVY_D  = (13, 18, 33)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
MONO   = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

def F(path, size): return ImageFont.truetype(path, size)

# ---------------------------------------------------------------- shared helpers
def multi_grad(size, stops):
    """Vertical multi-stop gradient. stops = [(t, (r,g,b)), ...] with t in 0..1."""
    w, h = size
    ys = np.linspace(0, 1, h)
    out = np.zeros((h, 3))
    ts = [s[0] for s in stops]; cs = np.array([s[1] for s in stops], dtype=float)
    for c in range(3):
        out[:, c] = np.interp(ys, ts, cs[:, c])
    return Image.fromarray(np.repeat(out[:, None, :], w, axis=1).astype(np.uint8))

def vignette(img, strength=0.30):
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    m = 1 - strength * np.clip(d - 0.55, 0, 1) ** 1.6
    return Image.fromarray(np.clip(a * m[:, :, None], 0, 255).astype(np.uint8))

def grain(img, amount=0.05, seed=7):
    a = np.asarray(img).astype(np.float32)
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 255 * amount * 0.5, a.shape[:2])[:, :, None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))

def crown_path(cx, cy, w, h):
    l = cx - w / 2; r = cx + w / 2; b = cy + h / 2; t = cy - h / 2
    dipy = b - h * 0.42
    pts = [(l, b),
           (l, t + h * 0.30), (l + w * 0.185, dipy),
           (cx - w * 0.155, t + h * 0.12), (cx, dipy - h * 0.02),
           (cx + w * 0.155, t + h * 0.12), (r - w * 0.185, dipy),
           (r, t + h * 0.30), (r, b)]
    band = (l, b + h * 0.06, r, b + h * 0.16)
    return pts, band

def crown_field(cx, cy, cw, ch, blur=90):
    """Blurred crown mask as float array 0..1 (heightfield core)."""
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    pts, band = crown_path(cx, cy, cw, ch)
    md.polygon(pts, fill=255)
    md.rectangle(band, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(mask).astype(np.float32) / 255.0

def smooth_noise(seed, scale=8, amp=1.0):
    rng = np.random.default_rng(seed)
    small = rng.random((scale * 3, scale * 2)).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    return (np.asarray(im).astype(np.float32) / 255.0) * amp

def text_tracked(draw, xy, text, font, fill, tracking=0, anchor_center=False):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if anchor_center: x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking
    return total

def circular_text(img, center, radius, text, font, fill, start_deg=-90):
    cx, cy = center
    tmp = ImageDraw.Draw(img)
    arcs = [max(tmp.textlength(c, font=font), font.size * 0.28) / radius for c in text]
    a = math.radians(start_deg) - sum(arcs) / 2
    for c, arc in zip(text, arcs):
        a_mid = a + arc / 2
        x = cx + radius * math.cos(a_mid); y = cy + radius * math.sin(a_mid)
        size = int(font.size * 3)
        ch = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        cd = ImageDraw.Draw(ch)
        cd.text((size / 2, size / 2), c, font=font, fill=fill, anchor="mm")
        ch = ch.rotate(-(math.degrees(a_mid) + 90), resample=Image.BICUBIC, center=(size / 2, size / 2))
        img.paste(ch, (int(x - size / 2), int(y - size / 2)), ch)
        a += arc

def footer(draw, text_main, color, y=H - 150, sub="STREET ROYALTY HOOD — EDICIÓN GALERÍA · MMXXVI", color_sub=None):
    text_tracked(draw, (W / 2, y), text_main, F(SANS_B, 34), color, tracking=14, anchor_center=True)
    text_tracked(draw, (W / 2, y + 52), sub, F(SANS, 24), color_sub or color, tracking=8, anchor_center=True)

def add_glow(canvas, x, y, radius, color, intensity=1.0):
    """Additive radial glow onto float array canvas (h,w,3)."""
    x0, x1 = max(0, int(x - radius)), min(W, int(x + radius))
    y0, y1 = max(0, int(y - radius)), min(H, int(y + radius))
    if x0 >= x1 or y0 >= y1: return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d2 = ((xx - x) ** 2 + (yy - y) ** 2) / (radius ** 2)
    fall = np.clip(1 - np.sqrt(d2), 0, 1) ** 2.2 * intensity
    canvas[y0:y1, x0:x1] += fall[:, :, None] * np.array(color, dtype=np.float32)

# ---------------------------------------------------------------- Nº10 Ocaso Real (Madrid skyline at dusk)
def d10():
    sky = multi_grad((W, H), [
        (0.00, (10, 14, 30)), (0.28, (26, 24, 48)), (0.46, (74, 30, 44)),
        (0.58, (154, 82, 52)), (0.66, (214, 152, 78)), (1.00, (16, 13, 16)),
    ])
    a = np.asarray(sky).astype(np.float32)
    horizon = H * 0.66
    # sun with layered halo
    sx, sy, sr = W * 0.5, H * 0.505, W * 0.155
    add_glow(a, sx, sy, sr * 3.4, (120, 70, 30), 0.55)
    add_glow(a, sx, sy, sr * 1.8, (200, 130, 50), 0.6)
    # stars (upper sky only)
    rng = np.random.default_rng(10)
    for _ in range(150):
        x = rng.uniform(30, W - 30); y = rng.uniform(30, H * 0.40)
        add_glow(a, x, y, rng.uniform(1.6, 4.5), (235, 225, 205), rng.uniform(0.35, 1.0) * (y / (H * 0.4)) ** -0.0)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    draw = ImageDraw.Draw(img)
    # solid sun disk + crown silhouette inside
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(238, 190, 110))
    pts, band = crown_path(sx, sy - sr * 0.10, sr * 0.92, sr * 0.50)
    draw.polygon(pts, fill=(110, 44, 38))
    draw.rectangle(band, fill=(110, 44, 38))
    # skyline silhouette (Madrid-inspired)
    sil = (14, 11, 15)
    base = horizon
    rnd = random.Random(4)
    x = 0
    buildings = []
    while x < W:
        bw = rnd.randint(70, 150)
        bh = rnd.randint(90, 340)
        buildings.append((x, bw, bh))
        x += bw - rnd.randint(0, 22)
    for (bx, bw, bh) in buildings:
        draw.rectangle([bx, base - bh, bx + bw, base], fill=sil)
        if rnd.random() < 0.5:  # rooftop details
            draw.rectangle([bx + bw * 0.35, base - bh - 16, bx + bw * 0.65, base - bh], fill=sil)
    # landmark: leaning KIO towers
    for (kx, lean) in [(W * 0.165, 1), (W * 0.300, -1)]:
        kw, kh = 78, 330
        sk = lean * 52
        draw.polygon([(kx, base), (kx + kw, base), (kx + kw + sk, base - kh), (kx + sk, base - kh)], fill=sil)
    # landmark: 4 towers right side
    for i, (tx, th) in enumerate([(W * 0.68, 520), (W * 0.76, 600), (W * 0.84, 560), (W * 0.91, 480)]):
        tw = 58
        draw.rectangle([tx, base - th, tx + tw, base], fill=sil)
        draw.line([tx + tw / 2, base - th, tx + tw / 2, base - th - 60], fill=sil, width=7)
    # lit windows
    for (bx, bw, bh) in buildings:
        for _ in range(int(bw * bh / 2400)):
            wx = rnd.uniform(bx + 8, bx + bw - 10); wy = rnd.uniform(base - bh + 10, base - 12)
            if rnd.random() < 0.6:
                draw.rectangle([wx, wy, wx + 5, wy + 8], fill=(224, 168, 92))
    # ground + light path
    draw.rectangle([0, base, W, H], fill=(16, 13, 16))
    ga = np.asarray(img).astype(np.float32)
    for k in range(60):
        t = k / 59
        add_glow(ga, sx + rng.uniform(-90, 90) * (0.3 + t), base + 6 + t * (H * 0.16),
                 34 + t * 26, (150, 92, 40), 0.11 * (1 - t))
    img = Image.fromarray(np.clip(ga, 0, 255).astype(np.uint8))
    draw = ImageDraw.Draw(img)
    draw.line([(0, base), (W, base)], fill=(232, 176, 96), width=3)
    f_big = F(SERIF_B, 118)
    draw.text((W / 2, H * 0.82), "OCASO REAL", font=f_big, fill=CREMA, anchor="mm")
    text_tracked(draw, (W / 2, H * 0.865), "MADRID · 40.4168° N — 3.7038° W", F(MONO, 30), ORO_HI, tracking=6, anchor_center=True)
    footer(draw, "ROYAL INK · Nº 10", ORO, y=H - 130, color_sub=(150, 128, 102))
    return grain(vignette(img, 0.34), 0.045, seed=10)

# ---------------------------------------------------------------- Nº11 Topografía Real (generative contour map)
def d11():
    field = crown_field(W / 2, H * 0.42, W * 0.60, H * 0.28, blur=110) * 1.0
    field += smooth_noise(11, scale=7, amp=0.34)
    field += 0.16 * (1 - np.sqrt(((np.mgrid[0:H, 0:W][1] - W / 2) / W) ** 2 +
                                 ((np.mgrid[0:H, 0:W][0] - H * 0.42) / H) ** 2) * 2)
    field = (field - field.min()) / (field.max() - field.min())
    img = multi_grad((W, H), [(0, (13, 13, 16)), (1, (8, 8, 10))])
    a = np.asarray(img).copy()
    levels = np.linspace(0.14, 0.97, 22)
    for i, lvl in enumerate(levels):
        b = field > lvl
        interior = b & np.roll(b, 1, 0) & np.roll(b, -1, 0) & np.roll(b, 1, 1) & np.roll(b, -1, 1)
        edge = b & ~interior
        major = (i % 5 == 0)
        if major:  # thicken
            e = edge | np.roll(edge, 1, 0) | np.roll(edge, 1, 1) | np.roll(edge, (1, 1), (0, 1))
        else:
            e = edge
        t = i / (len(levels) - 1)
        col = np.array([int(120 + (232 - 120) * t), int(96 + (202 - 96) * t), int(48 + (122 - 48) * t)])
        a[e] = col
    # mask out borders / text zones
    a[:int(H * 0.055), :] = a[:int(H * 0.055), :] // 3
    a[int(H * 0.70):, :] = (a[int(H * 0.70):, :] * 0.25).astype(a.dtype)
    img = Image.fromarray(a)
    draw = ImageDraw.Draw(img)
    # elevation labels along a survey line
    f_lab = F(MONO, 26)
    for (lx, ly, cota) in [(W * 0.30, H * 0.250, "0250"), (W * 0.62, H * 0.352, "0500"),
                           (W * 0.42, H * 0.470, "0750"), (W * 0.52, H * 0.415, "1000")]:
        draw.ellipse([lx - 5, ly - 5, lx + 5, ly + 5], outline=ORO_HI, width=2)
        draw.text((lx + 14, ly - 14), f"COTA {cota}", font=f_lab, fill=ARENA)
    # frame
    m = 64
    draw.rectangle([m, m, W - m, H - m], outline=(90, 76, 44), width=2)
    f_big = F(SERIF_B, 118)
    draw.text((W / 2, H * 0.775), "TOPOGRAFÍA", font=f_big, fill=CREMA, anchor="mm")
    text_tracked(draw, (W / 2, H * 0.820), "RELIEVE DE LA CORONA · LEVANTAMIENTO SRH", F(SANS, 32), ARENA, tracking=12, anchor_center=True)
    footer(draw, "ROYAL INK · Nº 11", ORO, color_sub=(120, 112, 96))
    return grain(vignette(img, 0.26), 0.04, seed=11)

# ---------------------------------------------------------------- Nº12 Carta Estelar (star chart constellation)
def d12():
    img = multi_grad((W, H), [(0, (16, 22, 42)), (0.5, NAVY_D), (1, (8, 11, 22))])
    a = np.asarray(img).astype(np.float32)
    cx, cy, R = W / 2, H * 0.42, W * 0.400
    rng = np.random.default_rng(12)
    # milky way diagonal band + field stars (inside chart circle)
    for _ in range(520):
        ang = rng.uniform(0, 2 * math.pi); rr = R * math.sqrt(rng.uniform(0, 1)) * 0.985
        x = cx + rr * math.cos(ang); y = cy + rr * math.sin(ang)
        band_d = abs((y - cy) - 0.55 * (x - cx)) / R
        p = 0.9 if band_d < 0.22 else 0.35
        if rng.uniform(0, 1) > p: continue
        add_glow(a, x, y, rng.uniform(1.5, 5.0), (210, 215, 235), rng.uniform(0.25, 0.9))
    # crown constellation: main stars on crown vertices
    pts, band = crown_path(cx, cy + R * 0.10, R * 1.05, R * 0.55)
    stars = pts[1:-1] + [(band[0] + 30, band[3]), (band[2] - 30, band[3])]
    for (x, y) in stars:
        add_glow(a, x, y, 26, (255, 228, 150), 1.5)
        add_glow(a, x, y, 9, (255, 245, 210), 2.4)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    draw = ImageDraw.Draw(img)
    # graticule
    for rr, wd in [(R, 4), (R * 0.86, 1), (R * 0.62, 1), (R * 0.38, 1)]:
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(84, 96, 130), width=wd)
    draw.ellipse([cx - R - 14, cy - R - 14, cx + R + 14, cy + R + 14], outline=(120, 130, 160), width=2)
    for k in range(24):
        ang = k * math.pi / 12
        x1 = cx + R * 0.97 * math.cos(ang); y1 = cy + R * 0.97 * math.sin(ang)
        x2 = cx + R * (0.90 if k % 2 else 0.92) * math.cos(ang); y2 = cy + R * (0.90 if k % 2 else 0.92) * math.sin(ang)
        draw.line([x1, y1, x2, y2], fill=(120, 130, 160), width=2)
    # constellation lines (dashed)
    seq = stars[:7]
    for (x1, y1), (x2, y2) in zip(seq, seq[1:]):
        steps = int(math.hypot(x2 - x1, y2 - y1) / 26)
        for s in range(steps):
            t0, t1 = s / steps, (s + 0.55) / steps
            draw.line([x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0,
                       x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1], fill=ORO_HI, width=3)
    # base band of crown as line
    draw.line([stars[-2], stars[-1]], fill=ORO_HI, width=2)
    circular_text(img, (cx, cy), R * 1.12, "CONSTELACIÓN DE LA CORONA  ·  HEMISFERIO NORTE  ·  CATÁLOGO SRH  ·",
                  F(SANS_B, 40), (168, 178, 205))
    draw = ImageDraw.Draw(img)
    f_big = F(SERIF_B, 118)
    draw.text((W / 2, H * 0.80), "CARTA ESTELAR", font=f_big, fill=CREMA, anchor="mm")
    text_tracked(draw, (W / 2, H * 0.845), "LA REALEZA SE LEE EN EL CIELO", F(SANS, 32), (150, 160, 190), tracking=12, anchor_center=True)
    footer(draw, "ROYAL INK · Nº 12", ORO_HI, y=H - 130, color_sub=(110, 120, 150))
    return grain(vignette(img, 0.30), 0.045, seed=12)

# ---------------------------------------------------------------- Nº13 Marea Real (ridgeline waves)
def d13():
    img = multi_grad((W, H), [(0, (58, 17, 26)), (0.6, BURDEOS), (1, (40, 12, 19))])
    draw = ImageDraw.Draw(img)
    field = crown_field(W / 2, H * 0.40, W * 0.55, H * 0.26, blur=70)
    noise = smooth_noise(13, scale=10, amp=1.0)
    rows = 44
    y_top, y_bot = H * 0.115, H * 0.660
    rnd = random.Random(13)
    bg_top = np.array((58, 17, 26)); bg_bot = np.array((40, 12, 19))
    for i in range(rows):
        ty = i / (rows - 1)
        ybase = y_top + (y_bot - y_top) * ty
        pts_line = []
        for x in range(60, W - 60, 8):
            fx = field[int(ybase), x]
            nx = noise[int(ybase), x]
            amp = fx * 150 + nx * 26 * (0.35 + fx)
            wob = math.sin(x * 0.011 + i * 1.7) * 6 * (0.3 + fx)
            pts_line.append((x, ybase - amp - wob))
        # occlusion fill below the line
        t_bg = ty * 0.85
        fill_col = tuple((bg_top + (bg_bot - bg_top) * t_bg).astype(int))
        draw.polygon(pts_line + [(W - 60, ybase + 3), (60, ybase + 3)], fill=fill_col)
        peak = max(field[int(ybase), 60:W - 60:8])
        col = ORO_HI if peak > 0.55 and i % 2 == 0 else CREMA
        wd = 4 if col == ORO_HI else 3
        draw.line(pts_line, fill=col, width=wd, joint="curve")
    f_big = F(SERIF_B, 118)
    draw.text((W / 2, H * 0.78), "MAREA REAL", font=f_big, fill=CREMA, anchor="mm")
    text_tracked(draw, (W / 2, H * 0.825), "LA CORONA EMERGE · FRECUENCIA SRH", F(SANS, 32), (216, 170, 150), tracking=12, anchor_center=True)
    footer(draw, "ROYAL INK · Nº 13", ORO_HI, color_sub=(180, 130, 118))
    return grain(vignette(img, 0.28), 0.045, seed=13)

# ---------------------------------------------------------------- mockup + detail
def mockup(poster, wall=(226, 222, 214)):
    MW, MH = 1600, 2000
    img = multi_grad((MW, MH), [(0, tuple(min(255, c + 16) for c in wall)),
                                (1, tuple(max(0, c - 22) for c in wall))])
    # warm light sweep from upper left
    a = np.asarray(img).astype(np.float32)
    yy, xx = np.mgrid[0:MH, 0:MW]
    sweep = np.clip(1 - np.sqrt(((xx - MW * 0.2) / MW) ** 2 + ((yy - MH * 0.05) / MH) ** 2), 0, 1) ** 2
    a += sweep[:, :, None] * np.array((22, 18, 10))
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    ph = int(MH * 0.72); pw = int(ph * W / H)
    px, py = (MW - pw) // 2, int(MH * 0.10)
    frame_pad = 26; matte = 46
    sh = Image.new("RGBA", (MW, MH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rectangle([px - frame_pad - matte + 14, py - frame_pad - matte + 26,
                  px + pw + frame_pad + matte + 30, py + ph + frame_pad + matte + 44], fill=(0, 0, 0, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rectangle([px - frame_pad - matte, py - frame_pad - matte,
                    px + pw + frame_pad + matte, py + ph + frame_pad + matte], fill=(24, 22, 20))
    draw.rectangle([px - matte, py - matte, px + pw + matte, py + ph + matte], fill=(248, 246, 240))
    img.paste(poster.resize((pw, ph), Image.LANCZOS), (px, py))
    draw.rectangle([0, int(MH * 0.94), MW, MH], fill=tuple(max(0, c - 34) for c in wall))
    return img

def detail(poster, cx=0.5, cy=0.40, size=0.52):
    s = int(W * size)
    x0 = int(W * cx - s / 2); y0 = int(H * cy - s / 2)
    x0 = max(0, min(W - s, x0)); y0 = max(0, min(H - s, y0))
    crop = poster.crop((x0, y0, x0 + s, y0 + s)).resize((1600, 1600), Image.LANCZOS)
    return crop.filter(ImageFilter.UnsharpMask(radius=3, percent=90, threshold=2))

designs = {
    "royal-ink-10-ocaso-real":  (d10, dict(cx=0.50, cy=0.56)),
    "royal-ink-11-topografia":  (d11, dict(cx=0.50, cy=0.40)),
    "royal-ink-12-carta-estelar": (d12, dict(cx=0.50, cy=0.46)),
    "royal-ink-13-marea-real":  (d13, dict(cx=0.50, cy=0.38)),
}
if __name__ == "__main__":
    for name, (fn, dkw) in designs.items():
        art = fn()
        art.save(f"{OUT}/{name}.jpg", quality=93)
        mockup(art).save(f"{OUT}/{name}-wall.jpg", quality=90)
        detail(art, **dkw).save(f"{OUT}/{name}-detail.jpg", quality=92)
        print("done", name)
