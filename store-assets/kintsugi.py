#!/usr/bin/env python3
# Kintsugi Real — drop SRH-KIN: porcelana rota, reparada en oro.
# 6 print files: camiseta, manga larga, hoodie, high tops (AOP), slip-on (AOP), calcetines.
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

NEGRO      = (12, 12, 14, 255)
TINTA      = (16, 15, 18, 255)
PORCELANA  = (244, 240, 231, 255)
PORCELANA2 = (231, 224, 210, 255)
ORO        = (192, 152, 62, 255)
ORO_MED    = (214, 175, 88, 255)
ORO_HI     = (243, 214, 138, 255)
SOMBRA     = (60, 44, 14, 255)
GRIS_CRAQ  = (196, 188, 172, 255)

SANS_B  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

def F(p, s): return ImageFont.truetype(p, s)

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))

# ---------------------------------------------------------------- crack engine
def gen_crack(rnd, start, angle, length, width, depth=0, max_depth=3):
    """Return list of (pts, widths) polylines: main path + branches."""
    paths = []
    pts, widths = [start], [width]
    x, y = start
    a = angle
    curve = rnd.gauss(0, 0.010)
    travelled = 0.0
    branches = []
    while travelled < length:
        step = rnd.uniform(9, 15)
        a += rnd.gauss(0, 0.085) + curve
        x += step * math.cos(a); y += step * math.sin(a)
        travelled += step
        frac = travelled / length
        w = max(width * (1.0 - 0.92 * frac), 1.0)
        pts.append((x, y)); widths.append(w)
        if depth < max_depth and len(pts) > 4 and rnd.random() < 0.055 and frac < 0.85:
            sgn = 1 if rnd.random() < 0.5 else -1
            branches.append(((x, y), a + sgn * rnd.uniform(0.45, 1.05),
                             length * rnd.uniform(0.25, 0.5), w * rnd.uniform(0.5, 0.7)))
    paths.append((pts, widths))
    for b in branches:
        paths += gen_crack(rnd, b[0], b[1], b[2], b[3], depth + 1, max_depth)
    return paths

def draw_polyline(layer, pts, widths, color_fn, scale=1.0):
    d = ImageDraw.Draw(layer)
    n = len(pts)
    for i in range(n - 1):
        t = i / max(n - 2, 1)
        w = max(widths[i] * scale, 0.8)
        d.line([pts[i], pts[i + 1]], fill=color_fn(t, pts[i]), width=max(int(round(w)), 1))
        r = w / 2
        x, y = pts[i + 1]
        d.ellipse([x - r, y - r, x + r, y + r], fill=color_fn(t, pts[i]))

def render_kintsugi(size, cracks, rnd, on_dark=True, ink_edge=False, dust=True):
    """Render crack paths as gold veins. Returns RGBA layer."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    # under-stroke (shadow/ink edge)
    if ink_edge:
        edge = Image.new("RGBA", size, (0, 0, 0, 0))
        for pts, widths in cracks:
            draw_polyline(edge, pts, widths, lambda t, p: (30, 26, 22, 255), scale=1.9)
        layer.alpha_composite(edge)
    else:
        sh = Image.new("RGBA", size, (0, 0, 0, 0))
        for pts, widths in cracks:
            draw_polyline(sh, pts, widths, lambda t, p: SOMBRA, scale=1.7)
        sh = sh.filter(ImageFilter.GaussianBlur(2.2))
        layer.alpha_composite(sh)
    # gold body with shimmer along the path
    for pts, widths in cracks:
        phase = rnd.uniform(0, math.tau)
        def gold(t, p, phase=phase):
            s = 0.5 + 0.5 * math.sin(phase + t * 5.2)
            return lerp(ORO, ORO_MED, s)
        draw_polyline(layer, pts, widths, gold)
    # bright core
    for pts, widths in cracks:
        phase = rnd.uniform(0, math.tau)
        def hi(t, p, phase=phase):
            s = 0.5 + 0.5 * math.sin(phase + t * 3.1)
            return lerp(ORO_MED, ORO_HI, s)
        draw_polyline(layer, pts, widths, hi, scale=0.38)
    # gold dust + pooled nodules at joints
    if dust:
        d = ImageDraw.Draw(layer)
        for pts, widths in cracks:
            for (x, y), w in zip(pts, widths):
                if rnd.random() < 0.045:
                    r = w * rnd.uniform(0.7, 1.35)
                    d.ellipse([x - r, y - r, x + r, y + r], fill=ORO_MED)
                    d.ellipse([x - r * .45, y - r * .5, x + r * .45, y + r * .35], fill=ORO_HI)
        w0, h0 = size
        for _ in range(int(w0 * h0 / 90000)):
            x, y = rnd.uniform(0, w0), rnd.uniform(0, h0)
            r = rnd.uniform(1.2, 3.2)
            d.ellipse([x - r, y - r, x + r, y + r], fill=lerp(ORO, ORO_HI, rnd.random()))
    return layer

def text_tracked(draw, xy, text, font, fill, tracking=0, center=False):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if center: x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking
    return total

def crown_pts(cx, cy, w, h):
    l = cx - w / 2; r = cx + w / 2; b = cy + h / 2; t = cy - h / 2
    dipy = b - h * 0.42
    return [(l, b), (l, t + h * 0.30), (l + w * 0.185, dipy),
            (cx - w * 0.155, t + h * 0.12), (cx, dipy - h * 0.02),
            (cx + w * 0.155, t + h * 0.12), (r - w * 0.185, dipy),
            (r, t + h * 0.30), (r, b)]

def porcelain_fill(size, seed, base=PORCELANA, base2=PORCELANA2):
    rnd = random.Random(seed)
    w, h = size
    img = Image.new("RGBA", size, base)
    d = ImageDraw.Draw(img)
    # soft diagonal tint
    for y in range(0, h, 4):
        t = y / h
        d.line([(0, y), (w, y)], fill=lerp(base, base2, t * 0.8), width=4)
    noise = Image.effect_noise(size, 14).convert("L")
    img = Image.composite(Image.new("RGBA", size, base2), img,
                          noise.point(lambda v: max(0, v - 190)))
    # hairline craquelure
    craq = Image.new("RGBA", size, (0, 0, 0, 0))
    for _ in range(int(w * h / 260000) + 3):
        st = (rnd.uniform(0, w), rnd.uniform(0, h))
        for pts, widths in gen_crack(rnd, st, rnd.uniform(0, math.tau),
                                     rnd.uniform(w * .2, w * .5), 1.6, max_depth=1):
            draw_polyline(craq, pts, widths, lambda t, p: GRIS_CRAQ)
    img.alpha_composite(craq)
    return img

# ---------------------------------------------------------------- 1. camiseta (2400x3200, transparente)
def d_tee():
    W, H = 2400, 3200
    rnd = random.Random(41)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cy, cw, ch = W / 2, 1150, 1560, 1060
    crown = crown_pts(cx, cy, cw, ch)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(crown, fill=255)
    band = (cx - cw / 2, cy + ch / 2 + ch * 0.055, cx + cw / 2, cy + ch / 2 + ch * 0.165)
    md.rounded_rectangle(band, radius=26, fill=255)
    porc = porcelain_fill((W, H), 7)
    img.paste(porc, (0, 0), mask)
    # inner shading for depth
    edge = mask.filter(ImageFilter.GaussianBlur(46))
    shade = Image.new("RGBA", (W, H), (146, 134, 112, 255))
    inner = Image.new("L", (W, H), 0)
    ImageDraw.Draw(inner).polygon(crown, fill=255)
    inner = Image.composite(Image.new("L", (W, H), 0), mask, edge.point(lambda v: 255 if v > 250 else 0))
    img.paste(shade, (0, 0), inner.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v // 4))
    # big kintsugi fractures across the crown
    cracks = []
    seeds = [((cx - cw * 0.34, cy - ch * 0.62), 1.35), ((cx + cw * 0.10, cy - ch * 0.70), 1.75),
             ((cx + cw * 0.46, cy - ch * 0.48), 2.35), ((cx - cw * 0.55, cy + ch * 0.05), 0.35),
             ((cx - cw * 0.05, cy + ch * 0.72), -1.45)]
    for (sx, sy), ang in seeds:
        cracks += gen_crack(rnd, (sx, sy), ang, ch * rnd.uniform(0.9, 1.25), 15)
    veins = render_kintsugi((W, H), cracks, rnd, on_dark=False, ink_edge=True)
    veins.putalpha(Image.composite(veins.split()[3], Image.new("L", (W, H), 0),
                                   mask.filter(ImageFilter.MaxFilter(9))))
    img.alpha_composite(veins)
    # lockup
    d = ImageDraw.Draw(img)
    y0 = band[3] + 150
    text_tracked(d, (W / 2, y0), "KINTSUGI REAL", F(SERIF_B, 128), ORO_MED, tracking=30, center=True)
    d.line([(W / 2 - 560, y0 + 208), (W / 2 + 560, y0 + 208)], fill=ORO, width=5)
    text_tracked(d, (W / 2, y0 + 248), "ROTO · REPARADO · CORONADO", F(SANS, 54), PORCELANA2, tracking=22, center=True)
    text_tracked(d, (W / 2, y0 + 350), "STREET ROYALTY HOOD — MMXXVI", F(SANS, 40), lerp(ORO, ORO_HI, .3), tracking=14, center=True)
    img.save(f"{OUT}/kin_tee_print.png")

# ---------------------------------------------------------------- 2. manga larga (2400x3000, transparente, fondo blanco prenda)
def gen_crack_pulled(rnd, start, target_angle, length, width, pull=0.10, max_depth=3):
    """Crack whose heading is pulled back toward target_angle — long directed fractures."""
    paths = []
    pts, widths = [start], [width]
    x, y = start
    a = target_angle
    travelled = 0.0
    branches = []
    while travelled < length:
        step = rnd.uniform(9, 15)
        a = a * (1 - pull) + target_angle * pull + rnd.gauss(0, 0.10)
        x += step * math.cos(a); y += step * math.sin(a)
        travelled += step
        frac = travelled / length
        w = max(width * (1.0 - 0.9 * frac), 1.2)
        pts.append((x, y)); widths.append(w)
        if len(pts) > 5 and rnd.random() < 0.075 and 0.06 < frac < 0.9:
            sgn = 1 if rnd.random() < 0.5 else -1
            branches.append(((x, y), a + sgn * rnd.uniform(0.5, 1.1),
                             length * rnd.uniform(0.18, 0.38), w * rnd.uniform(0.5, 0.68)))
    paths.append((pts, widths))
    for b in branches:
        paths += gen_crack(rnd, b[0], b[1], b[2], b[3], 1, max_depth)
    return paths

def d_longsleeve():
    W, H = 2400, 3000
    rnd = random.Random(31)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # one grand vertical fracture with branches, ink-edged gold on white garment
    cracks = gen_crack_pulled(rnd, (W * 0.55, -40), math.pi / 2, H * 1.06, 18)
    cracks += gen_crack_pulled(rnd, (W * 0.20, H * 0.30), 0.55, W * 0.42, 9)
    cracks += gen_crack_pulled(rnd, (W * 0.85, H * 0.62), math.pi - 0.5, W * 0.40, 9)
    img.alpha_composite(render_kintsugi((W, H), cracks, rnd, ink_edge=True))
    # small porcelain crown chip at the top of the seam
    ccx, ccy, ccw, cch = W * 0.52, H * 0.10, 300, 205
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(crown_pts(ccx, ccy, ccw, cch), fill=255)
    porc = porcelain_fill((W, H), 5)
    img.paste(porc, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.polygon(crown_pts(ccx, ccy, ccw, cch), outline=(30, 26, 22, 255), width=6)
    # lockup bottom-left, asymmetric
    y0 = H - 420
    text_tracked(d, (W * 0.13, y0), "KINTSUGI", F(SERIF_B, 118), (24, 22, 20, 255), tracking=26)
    text_tracked(d, (W * 0.13, y0 + 160), "PORCELANA & ORO", F(SANS, 52), ORO, tracking=20)
    d.line([(W * 0.13, y0 + 250), (W * 0.13 + 640, y0 + 250)], fill=(24, 22, 20, 255), width=5)
    text_tracked(d, (W * 0.13, y0 + 280), "SRHOOD — MMXXVI", F(SANS, 38), (90, 84, 76, 255), tracking=12)
    img.save(f"{OUT}/kin_ls_print.png")

# ---------------------------------------------------------------- 3. hoodie (1800x1800, transparente) — luna de porcelana
def d_hoodie():
    W, H = 1800, 1800
    rnd = random.Random(97)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cy, R = W / 2, 760, 560
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    porc = porcelain_fill((W, H), 13)
    img.paste(porc, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(70, 62, 50, 255), width=6)
    cracks = []
    for ang0 in (2.1, 0.4, 3.6, 5.2):
        sx = cx + (R * 1.0) * math.cos(ang0); sy = cy + (R * 1.0) * math.sin(ang0)
        cracks += gen_crack(rnd, (sx, sy), ang0 + math.pi + rnd.gauss(0, .3),
                            R * rnd.uniform(1.2, 1.7), 13)
    veins = render_kintsugi((W, H), cracks, rnd, ink_edge=True)
    veins.putalpha(Image.composite(veins.split()[3], Image.new("L", (W, H), 0),
                                   mask.filter(ImageFilter.MaxFilter(7))))
    img.alpha_composite(veins)
    # one escaped vein leaves the moon (kintsugi overflows the porcelain)
    esc = gen_crack(rnd, (cx + R * 0.62, cy + R * 0.78), 1.25, R * 0.8, 9, max_depth=1)
    img.alpha_composite(render_kintsugi((W, H), esc, rnd, ink_edge=False))
    y0 = cy + R + 120
    text_tracked(d, (W / 2, y0), "KINTSUGI REAL", F(SERIF_B, 92), ORO_MED, tracking=22, center=True)
    text_tracked(d, (W / 2, y0 + 132), "LUNA ROTA — SRHOOD MMXXVI", F(SANS, 36), PORCELANA2, tracking=14, center=True)
    img.save(f"{OUT}/kin_hoodie_print.png")

# ---------------------------------------------------------------- AOP helper
def aop(size, seed, base, n_nets, width, ink_edge, fname, craquelure=False):
    W, H = size
    rnd = random.Random(seed)
    img = Image.new("RGBA", size, base)
    if craquelure:
        img = porcelain_fill(size, seed + 1)
    cracks = []
    # seed from edges and interior for an even all-over spread
    for i in range(n_nets):
        side = rnd.random()
        if side < 0.25: st, ang = (rnd.uniform(0, W), -20), math.pi / 2
        elif side < 0.5: st, ang = (rnd.uniform(0, W), H + 20), -math.pi / 2
        elif side < 0.75: st, ang = (-20, rnd.uniform(0, H)), 0.0
        else: st, ang = (rnd.uniform(0.15 * W, 0.85 * W), rnd.uniform(0.15 * H, 0.85 * H)), rnd.uniform(0, math.tau)
        cracks += gen_crack(rnd, st, ang + rnd.gauss(0, 0.5),
                            rnd.uniform(0.45, 0.85) * min(W, H), width)
    img.alpha_composite(render_kintsugi(size, cracks, rnd, ink_edge=ink_edge))
    img.convert("RGB").save(f"{OUT}/{fname}", quality=95)

def d_hitops():   aop((2400, 2400), 71, TINTA, 9, 12, True,  "kin_hitops_print.png", craquelure=True)
def d_slipon():   aop((2600, 2600), 55, TINTA, 11, 13, False, "kin_slipon_print.png")
def d_socks():    aop((1400, 2400), 88, TINTA, 8, 11, False, "kin_socks_print.png")

if __name__ == "__main__":
    d_tee(); print("tee ok")
    d_longsleeve(); print("ls ok")
    d_hoodie(); print("hoodie ok")
    d_hitops(); print("hitops ok")
    d_slipon(); print("slipon ok")
    d_socks(); print("socks ok")
