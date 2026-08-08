#!/usr/bin/env python3
# Brand covers for SRHOOD capsule collections — same visual system as the
# existing brand-cover-* images (dark canvas, wordmark pattern, gold frame,
# line-art icon, serif title, tracked gold subtitle/footer).
import math, random, os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "covers")
os.makedirs(OUT, exist_ok=True)

S = 1600
NEGRO   = (16, 16, 19)
NEGRO_2 = (11, 11, 13)
PATRON  = (28, 28, 32)
CREMA   = (242, 234, 217)
ORO     = (201, 164, 76)
ORO_HI  = (222, 190, 116)
ORO_LO  = (150, 122, 62)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def F(path, size): return ImageFont.truetype(path, int(size))

def text_tracked(draw, xy, text, font, fill, tracking=0):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking

def vgrad(top, bottom):
    base = Image.new("RGB", (1, S))
    px = base.load()
    for y in range(S):
        t = y / (S - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((S, S))

def canvas():
    img = vgrad(NEGRO, NEGRO_2)
    d = ImageDraw.Draw(img)
    f = F(SANS_B, 150)
    unit = "SRHOOD · "
    uw = d.textlength(unit, font=f)
    for row, y in enumerate(range(-80, S + 80, 214)):
        x = -uw + (row % 3) * -260
        while x < S:
            d.text((x, y), unit, font=f, fill=PATRON)
            x += uw
    # gold frame with corner diamonds
    m = 62
    d.rectangle([m, m, S - m, S - m], outline=ORO, width=2)
    d.rectangle([m + 13, m + 13, S - m - 13, S - m - 13], outline=ORO_LO, width=1)
    for cx in (m, S - m):
        for cy in (m, S - m):
            d.polygon([(cx, cy - 16), (cx + 16, cy), (cx, cy + 16), (cx - 16, cy)], fill=ORO)
    return img, d

def compose(name, title, subtitle, icon):
    img, d = canvas()
    icon(img, d, S / 2, 450, 210)
    d.rectangle([350, 876, S - 350, 882], fill=ORO)
    size = 132
    ft = F(SERIF_B, size)
    while d.textlength(title, font=ft) > 1230 and size > 60:
        size -= 4
        ft = F(SERIF_B, size)
    d.text((S / 2, 1035), title, font=ft, fill=CREMA, anchor="mm")
    text_tracked(d, (S / 2, 1185), subtitle, F(SANS, 40), ORO, tracking=16)
    text_tracked(d, (S / 2, 1440), "STREET ROYALTY HOOD — MMXXVI", F(SANS, 27), ORO_LO, tracking=11)
    img.save(f"{OUT}/brand-cover-{name}.jpg", quality=90)
    print("done", name)

# ---------------------------------------------------------------- icon helpers
W_LINE = 11

def ring(d, cx, cy, r, w=W_LINE, col=ORO):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=w)

def loop(d, pts, w=W_LINE, col=ORO):
    d.line(list(pts) + [pts[0]], fill=col, width=w, joint="curve")

def crown_pts(cx, cy, w, h):
    l, r, t, b = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    dip = b - h * 0.40
    return [(l, b), (l, t + h * 0.30), (l + w * 0.185, dip), (cx - w * 0.155, t + h * 0.10),
            (cx, dip - h * 0.04), (cx + w * 0.155, t + h * 0.10), (r - w * 0.185, dip),
            (r, t + h * 0.30), (r, b)]

def crescent(d, cx, cy, r, bite_dx, bite_dy, w=W_LINE):
    c2 = (cx + bite_dx, cy + bite_dy)
    r2 = r * 0.95
    outer = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
             for a in range(0, 360, 2)]
    outer = [p for p in outer if math.hypot(p[0] - c2[0], p[1] - c2[1]) > r2]
    inner = [(c2[0] + r2 * math.cos(math.radians(a)), c2[1] + r2 * math.sin(math.radians(a)))
             for a in range(0, 360, 2)]
    inner = [p for p in inner if math.hypot(p[0] - cx, p[1] - cy) < r]
    def rotate_gap(pts):
        j = max(range(len(pts)), key=lambda i: math.dist(pts[i - 1], pts[i]))
        return pts[j:] + pts[:j]
    outer, inner = rotate_gap(outer), rotate_gap(inner)
    if math.dist(outer[-1], inner[0]) > math.dist(outer[-1], inner[-1]):
        inner = inner[::-1]
    loop(d, outer + inner, w)

def star4(d, cx, cy, r, col=ORO):
    d.polygon([(cx, cy - r), (cx + r * 0.3, cy), (cx, cy + r), (cx - r * 0.3, cy)], fill=col)
    d.polygon([(cx - r, cy), (cx, cy + r * 0.3), (cx + r, cy), (cx, cy - r * 0.3)], fill=col)

# ---------------------------------------------------------------- icons
def i_nocturna(img, d, cx, cy, s):
    crescent(d, cx - s * 0.1, cy + s * 0.05, s * 0.62, s * 0.30, -s * 0.24)
    star4(d, cx + s * 0.55, cy - s * 0.55, 34)
    star4(d, cx + s * 0.75, cy + 0, 22)
    star4(d, cx - s * 0.75, cy - s * 0.45, 22)

def i_telar(img, d, cx, cy, s):
    n, sp = 4, s * 0.42
    xs = [cx + (i - (n - 1) / 2) * sp for i in range(n)]
    ys = [cy + (i - (n - 1) / 2) * sp for i in range(n)]
    for x in xs:
        d.line([(x, cy - s * 0.8), (x, cy + s * 0.8)], fill=ORO, width=W_LINE)
    for k, y in enumerate(ys):
        x0 = cx - s * 0.8
        segs = [x0] + sorted(xs) + [cx + s * 0.8]
        for j in range(len(segs) - 1):
            over = (j + k) % 2 == 0
            a, b = segs[j], segs[j + 1]
            pad = 0 if over else 26
            d.line([(a + (pad if j else 0), y), (b - (pad if j < len(segs) - 2 else 0), y)],
                   fill=ORO if over else ORO_LO, width=W_LINE)

def i_deco(img, d, cx, cy, s):
    base = cy + s * 0.45
    d.line([(cx - s, base), (cx + s, base)], fill=ORO, width=W_LINE)
    for r in (s * 0.28, s * 0.45, s * 0.62):
        d.arc([cx - r, base - r, cx + r, base + r], 180, 360, fill=ORO, width=W_LINE)
    for i in range(-4, 5):
        a = math.radians(90 + i * 19)
        x1 = cx + math.cos(a) * s * 0.70; y1 = base - math.sin(a) * s * 0.70
        x2 = cx + math.cos(a) * s * 1.02; y2 = base - math.sin(a) * s * 1.02
        d.line([(x1, y1), (x2, y2)], fill=ORO, width=7)

def i_panuelo(img, d, cx, cy, s):
    pts = []
    for t in [i / 100 for i in range(101)]:
        a = math.pi * 0.5 + t * math.pi * 1.55
        r = s * 0.62 * (1 - 0.45 * t)
        pts.append((cx + r * math.cos(a) * 0.85, cy + s * 0.1 - r * math.sin(a)))
    d.line(pts, fill=ORO, width=W_LINE, joint="curve")
    pts2 = []
    for t in [i / 100 for i in range(101)]:
        a = math.pi * 0.5 - t * math.pi * 0.75
        r = s * 0.62 * (1 + 0.28 * t)
        pts2.append((cx + r * math.cos(a) * 0.85, cy + s * 0.1 - r * math.sin(a)))
    d.line(pts2, fill=ORO, width=W_LINE, joint="curve")
    ring(d, cx - s * 0.05, cy + s * 0.12, s * 0.16, w=8)
    d.ellipse([cx - s * 0.11, cy + s * 0.06, cx + s * 0.01, cy + s * 0.18], fill=ORO)

def i_azulejo(img, d, cx, cy, s):
    a = s * 0.72
    d.rectangle([cx - a, cy - a, cx + a, cy + a], outline=ORO, width=W_LINE)
    d.polygon([(cx, cy - a), (cx + a, cy), (cx, cy + a), (cx - a, cy)], outline=ORO, width=8)
    b = a * 0.45
    d.polygon([(cx, cy - b), (cx + b, cy), (cx, cy + b), (cx - b, cy)], outline=ORO, width=8)
    ring(d, cx, cy, a * 0.18, w=8)

def i_forma(img, d, cx, cy, s):
    ring(d, cx - s * 0.42, cy - s * 0.25, s * 0.42)
    a = s * 0.72
    d.polygon([(cx + s * 0.45, cy - s * 0.72), (cx + s * 0.95, cy + s * 0.18),
               (cx - s * 0.05, cy + s * 0.18)], outline=ORO, width=W_LINE)
    d.rectangle([cx - s * 0.72, cy + s * 0.28, cx + s * 0.10, cy + s * 0.85],
                outline=ORO, width=W_LINE)

def i_cianotipo(img, d, cx, cy, s):
    stem = [(cx + math.sin(t * 3) * s * 0.10, cy + s * 0.8 - t * s * 1.6)
            for t in [i / 40 for i in range(41)]]
    d.line(stem, fill=ORO, width=W_LINE, joint="curve")
    for k in range(1, 8):
        t = k / 8
        x = cx + math.sin(t * 3) * s * 0.10
        y = cy + s * 0.8 - t * s * 1.6
        ln = s * 0.42 * (1 - t * 0.75)
        for sgn in (-1, 1):
            d.line([(x, y), (x + sgn * ln, y - ln * 0.55)], fill=ORO, width=8)

def i_suminagashi(img, d, cx, cy, s):
    for k, r0 in enumerate((0.18, 0.36, 0.54, 0.72)):
        pts = []
        for a in range(0, 362, 3):
            r = s * r0 * (1 + 0.06 * math.sin(math.radians(a * 3) + k))
            pts.append((cx + r * math.cos(math.radians(a)) * 1.15,
                        cy + r * math.sin(math.radians(a)) * 0.85))
        d.line(pts, fill=ORO, width=7 if k % 2 else W_LINE, joint="curve")
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=ORO)

def i_relieve(img, d, cx, cy, s):
    rnd = random.Random(5)
    phases = [rnd.uniform(0, 6.28) for _ in range(3)]
    for k, r0 in enumerate((0.30, 0.50, 0.70, 0.90)):
        pts = []
        for a in range(0, 362, 3):
            w = 1 + 0.10 * math.sin(math.radians(a * 2) + phases[0]) \
                  + 0.07 * math.sin(math.radians(a * 3) + phases[1] + k)
            r = s * r0 * w
            pts.append((cx + r * math.cos(math.radians(a)) * 1.05,
                        cy + r * math.sin(math.radians(a)) * 0.72))
        d.line(pts, fill=ORO, width=7 if k % 2 else W_LINE, joint="curve")
    d.polygon([(cx, cy - 26), (cx + 24, cy + 18), (cx - 24, cy + 18)], fill=ORO)

def i_nube(img, d, cx, cy, s):
    for dx, r in ((-0.45, 0.30), (0.0, 0.46), (0.45, 0.30)):
        rr = s * r
        d.arc([cx + dx * s - rr, cy - rr, cx + dx * s + rr, cy + rr],
              160 if dx < 0 else (20 if dx > 0 else 180), 20 if dx < 0 else (380 if dx > 0 else 360),
              fill=ORO, width=W_LINE)
    d.line([(cx - s * 0.72, cy + s * 0.30), (cx + s * 0.72, cy + s * 0.30)], fill=ORO, width=W_LINE)
    for k, (x0, ln) in enumerate([(-0.35, 0.5), (0.05, 0.7), (0.45, 0.4)]):
        y = cy + s * (0.48 + 0.12 * k)
        d.line([(cx + x0 * s - ln * s * 0.2, y), (cx + x0 * s + ln * s * 0.35, y)], fill=ORO_LO, width=7)
    pts = [(cx + s * 0.30 * math.cos(a / 30) * a / 300, cy + s * 0.30 * math.sin(a / 30) * a / 300)
           for a in range(40, 300, 6)]
    d.line(pts, fill=ORO, width=8, joint="curve")

def i_salpicadura(img, d, cx, cy, s):
    rnd = random.Random(9)
    pts = []
    for a in range(0, 362, 4):
        r = s * 0.5 * (1 + 0.22 * math.sin(math.radians(a * 3) + 1.1)
                       + 0.14 * math.sin(math.radians(a * 5)))
        pts.append((cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))))
    loop(d, pts)
    for _ in range(9):
        a = rnd.uniform(0, 6.28); rr = rnd.uniform(s * 0.72, s * 0.98); r = rnd.uniform(7, 17)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.8
        d.ellipse([x - r, y - r, x + r, y + r], fill=ORO)

def i_via(img, d, cx, cy, s):
    d.line([(cx - s * 0.85, cy + s * 0.8), (cx - s * 0.22, cy - s * 0.8)], fill=ORO, width=W_LINE)
    d.line([(cx + s * 0.85, cy + s * 0.8), (cx + s * 0.22, cy - s * 0.8)], fill=ORO, width=W_LINE)
    for t0 in (0.02, 0.28, 0.54, 0.80):
        x1 = cx + (t0 - 0.5) * 0  # center dashes converge
        y1 = cy + s * 0.8 - t0 * s * 1.6
        y2 = y1 - s * 0.18
        d.line([(cx, y1), (cx, y2)], fill=ORO_HI, width=9)

def i_moire(img, d, cx, cy, s):
    for k in range(7):
        r = s * 0.16 + k * s * 0.115
        ring(d, cx - s * 0.16, cy, r, w=4)
        ring(d, cx + s * 0.16, cy, r, w=4)

def i_estatica(img, d, cx, cy, s):
    rnd = random.Random(4)
    y = cy - s * 0.8
    while y < cy + s * 0.8:
        h = rnd.randint(10, 26)
        off = rnd.choice([0, 0, rnd.randint(-70, 70)])
        w = rnd.uniform(0.5, 1.5)
        col = ORO if rnd.random() > 0.25 else ORO_LO
        d.rectangle([cx - s * 0.6 * w + off, y, cx + s * 0.6 * w + off, y + h], fill=col)
        y += h + rnd.randint(14, 40)

def i_trazo(img, d, cx, cy, s):
    rnd = random.Random(2)
    pts_top, pts_bot = [], []
    for t in [i / 30 for i in range(31)]:
        x = cx - s * 0.8 + t * s * 1.6
        y = cy + s * 0.35 - t * s * 0.7 + math.sin(t * 6) * s * 0.05
        wd = s * 0.16 * (1 - abs(t - 0.4)) + 6
        pts_top.append((x, y - wd)); pts_bot.append((x, y + wd))
    d.polygon(pts_top + pts_bot[::-1], fill=ORO)
    for _ in range(8):
        x = rnd.uniform(cx - s * 0.9, cx + s * 0.9); y = rnd.uniform(cy - s * 0.7, cy + s * 0.7)
        r = rnd.uniform(6, 15)
        d.ellipse([x - r, y - r, x + r, y + r], fill=ORO)

def i_observatorio(img, d, cx, cy, s):
    ring(d, cx, cy, s * 0.78, w=7)
    ring(d, cx, cy, s * 0.62, w=4)
    for a in range(0, 360, 30):
        x1 = cx + s * 0.70 * math.cos(math.radians(a)); y1 = cy + s * 0.70 * math.sin(math.radians(a))
        x2 = cx + s * 0.78 * math.cos(math.radians(a)); y2 = cy + s * 0.78 * math.sin(math.radians(a))
        d.line([(x1, y1), (x2, y2)], fill=ORO, width=5)
    for horiz in (0, 1):
        r1, r2 = s * 0.55, s * 0.14
        p = [(0, -r1), (r2 * 0.5, 0), (0, r1), (-r2 * 0.5, 0)]
        if horiz: p = [(y, x) for x, y in p]
        d.polygon([(cx + x, cy + y) for x, y in p], outline=ORO, width=7)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=ORO)

def i_vidriera(img, d, cx, cy, s):
    w, h = s * 0.62, s * 0.85
    d.arc([cx - w, cy - h, cx + w, cy + h * 0.5], 180, 360, fill=ORO, width=W_LINE)
    d.line([(cx - w, cy - h * 0.25), (cx - w, cy + h)], fill=ORO, width=W_LINE)
    d.line([(cx + w, cy - h * 0.25), (cx + w, cy + h)], fill=ORO, width=W_LINE)
    d.line([(cx - w, cy + h), (cx + w, cy + h)], fill=ORO, width=W_LINE)
    d.line([(cx, cy - h * 0.28), (cx, cy + h)], fill=ORO, width=7)
    d.line([(cx - w, cy + h * 0.35), (cx + w, cy + h * 0.35)], fill=ORO, width=7)
    ring(d, cx, cy - h * 0.42, s * 0.17, w=7)
    for a in range(0, 360, 60):
        d.line([(cx, cy - h * 0.42),
                (cx + s * 0.17 * math.cos(math.radians(a)), cy - h * 0.42 + s * 0.17 * math.sin(math.radians(a)))],
               fill=ORO, width=4)

def i_neon(img, d, cx, cy, s):
    d.rounded_rectangle([cx - s * 0.85, cy - s * 0.62, cx + s * 0.85, cy + s * 0.62],
                        radius=48, outline=ORO, width=W_LINE)
    bolt = [(cx + s * 0.10, cy - s * 0.45), (cx - s * 0.22, cy + s * 0.06), (cx - 0, cy + s * 0.06),
            (cx - s * 0.10, cy + s * 0.45), (cx + s * 0.25, cy - s * 0.08), (cx + s * 0.02, cy - s * 0.08)]
    d.polygon(bolt, outline=ORO_HI, width=8)
    for dx in (-0.62, 0.62):
        d.line([(cx + s * dx, cy + s * 0.62), (cx + s * dx * 1.15, cy + s * 0.85)], fill=ORO_LO, width=7)

def i_guilloche(img, d, cx, cy, s):
    n = 10
    for k in range(n):
        a = k * 2 * math.pi / n
        ring(d, cx + s * 0.30 * math.cos(a), cy + s * 0.30 * math.sin(a), s * 0.40, w=4)
    ring(d, cx, cy, s * 0.78, w=7)

def i_plumaje(img, d, cx, cy, s):
    d.line([(cx, cy + s * 0.9), (cx, cy + s * 0.1)], fill=ORO, width=W_LINE)
    for k in range(5):
        t = k / 5
        y = cy + s * (0.85 - t * 0.55)
        ln = s * (0.18 + t * 0.1)
        for sgn in (-1, 1):
            d.line([(cx, y), (cx + sgn * ln, y + ln * 0.5)], fill=ORO_LO, width=6)
    d.ellipse([cx - s * 0.42, cy - s * 0.75, cx + s * 0.42, cy + s * 0.32],
              outline=ORO, width=W_LINE)
    d.ellipse([cx - s * 0.26, cy - s * 0.55, cx + s * 0.26, cy + s * 0.12], outline=ORO, width=7)
    d.ellipse([cx - s * 0.12, cy - s * 0.36, cx + s * 0.12, cy - s * 0.06], fill=ORO)

def i_kintsugi(img, d, cx, cy, s):
    r = s * 0.75
    d.arc([cx - r, cy - r * 1.15, cx + r, cy + r * 0.85], 0, 180, fill=ORO, width=W_LINE)
    d.line([(cx - r, cy - r * 0.15), (cx + r, cy - r * 0.15)], fill=ORO, width=W_LINE)
    d.rectangle([cx - s * 0.22, cy + r * 0.85 - 6, cx + s * 0.22, cy + r * 0.85 + 26], outline=ORO, width=8)
    crack = [(cx - s * 0.05, cy - r * 0.15), (cx + s * 0.08, cy + s * 0.05), (cx - s * 0.06, cy + s * 0.22),
             (cx + s * 0.12, cy + s * 0.42), (cx + s * 0.04, cy + s * 0.58)]
    d.line(crack, fill=ORO_HI, width=9, joint="curve")
    d.line([(cx + s * 0.08, cy + s * 0.05), (cx + s * 0.28, cy + s * 0.18)], fill=ORO_HI, width=6)

def i_frecuencia(img, d, cx, cy, s):
    n = 15
    for k in range(n):
        t = (k - (n - 1) / 2) / ((n - 1) / 2)
        h = s * (0.15 + 0.65 * math.exp(-t * t * 3.2) * abs(math.cos(k * 1.7)))
        x = cx + t * s * 0.85
        d.line([(x, cy - h), (x, cy + h)], fill=ORO if k % 2 == 0 else ORO_LO, width=13)

def i_baraja(img, d, cx, cy, s):
    w, h = s * 0.60, s * 0.85
    d.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=30, outline=ORO, width=W_LINE)
    loop(d, crown_pts(cx, cy, s * 0.62, s * 0.34), w=8)
    d.rectangle([cx - s * 0.31, cy + s * 0.21, cx + s * 0.31, cy + s * 0.29], outline=ORO, width=8)
    f = F(SERIF_B, 64)
    d.text((cx - w + 44, cy - h + 48), "R", font=f, fill=ORO, anchor="mm")
    d.text((cx + w - 44, cy + h - 48), "R", font=f, fill=ORO, anchor="mm")

def i_laurel(img, d, cx, cy, s):
    r = s * 0.66
    for sgn in (-1, 1):
        pts = [(cx + sgn * r * math.sin(t), cy + s * 0.08 + r * math.cos(t))
               for t in [i / 30 * 2.35 for i in range(31)]]
        d.line(pts, fill=ORO, width=W_LINE, joint="curve")
        for k in range(1, 8):
            t = k / 8 * 2.35
            x = cx + sgn * r * math.sin(t)
            y = cy + s * 0.08 + r * math.cos(t)
            # tangent direction (moving upward along the branch)
            tx, ty = sgn * math.cos(t), -math.sin(t)
            for side in (-1, 1):
                # leaf angled off the branch
                lx = x + (tx * 0.16 + side * -ty * 0.13) * s
                ly = y + (ty * 0.16 + side * tx * 0.13) * s
                d.line([(x, y), (lx, ly)], fill=ORO_LO, width=7)
                d.ellipse([lx - 8, ly - 8, lx + 8, ly + 8], fill=ORO)
    star4(d, cx, cy - s * 0.06, 36)

def i_camo(img, d, cx, cy, s):
    rnd = random.Random(12)
    for k, (bx, by, br) in enumerate([(-0.55, -0.35, 0.30), (0.5, -0.5, 0.26), (0.55, 0.45, 0.30), (-0.5, 0.5, 0.26)]):
        pts = []
        for a in range(0, 362, 6):
            r = s * br * (1 + 0.25 * math.sin(math.radians(a * 3) + k * 2))
            pts.append((cx + bx * s + r * math.cos(math.radians(a)),
                        cy + by * s + r * math.sin(math.radians(a))))
        loop(d, pts, w=6, col=ORO_LO)
    loop(d, crown_pts(cx, cy + s * 0.02, s * 1.05, s * 0.60))
    d.rectangle([cx - s * 0.525, cy + s * 0.40, cx + s * 0.525, cy + s * 0.50], outline=ORO, width=W_LINE)

def i_eslabon(img, d, cx, cy, s):
    a, b, off = s * 0.62, s * 0.40, s * 0.38
    lbox = [cx - off - a, cy - b, cx - off + a, cy + b]
    rbox = [cx + off - a, cy - b, cx + off + a, cy + b]
    d.ellipse(rbox, outline=ORO, width=W_LINE)
    d.ellipse(lbox, outline=ORO, width=W_LINE)
    # left is on top at both crossings; flip the top crossing so right passes over
    bg = img.getpixel((int(cx), int(cy - b * 0.79 - 30)))
    d.arc(lbox, 299, 319, fill=bg, width=W_LINE + 14)
    d.arc(rbox, 205, 258, fill=ORO, width=W_LINE)

def i_tartan(img, d, cx, cy, s):
    a = s * 0.75
    d.rectangle([cx - a, cy - a, cx + a, cy + a], outline=ORO, width=W_LINE)
    for off, w in ((-0.42, 26), (-0.05, 9), (0.38, 15)):
        d.line([(cx + off * s, cy - a), (cx + off * s, cy + a)], fill=ORO_LO, width=w)
        d.line([(cx - a, cy + off * s), (cx + a, cy + off * s)], fill=ORO_LO, width=w)
    for off in (-0.42, 0.38):
        d.line([(cx + off * s, cy - a), (cx + off * s, cy + a)], fill=ORO, width=5)
        d.line([(cx - a, cy + off * s), (cx + a, cy + off * s)], fill=ORO, width=5)

def i_forja(img, d, cx, cy, s):
    pts = [(cx - s * 0.9, cy - s * 0.30), (cx + s * 0.55, cy - s * 0.30), (cx + s * 0.9, cy - s * 0.45),
           (cx + s * 0.9, cy - s * 0.12), (cx + s * 0.35, cy + s * 0.02), (cx + s * 0.28, cy + s * 0.32),
           (cx + s * 0.55, cy + s * 0.50), (cx - s * 0.55, cy + s * 0.50), (cx - s * 0.28, cy + s * 0.32),
           (cx - s * 0.35, cy + s * 0.02), (cx - s * 0.9, cy - s * 0.10)]
    loop(d, pts)
    d.line([(cx - s * 0.75, cy + s * 0.50), (cx + s * 0.75, cy + s * 0.50)], fill=ORO, width=W_LINE)
    star4(d, cx - s * 0.1, cy - s * 0.62, 26)

def i_brocado(img, d, cx, cy, s):
    for a0 in range(0, 360, 45):
        a = math.radians(a0)
        ex, ey = cx + s * 0.42 * math.cos(a), cy + s * 0.42 * math.sin(a)
        r1, r2 = (s * 0.34, s * 0.16) if a0 % 90 == 0 else (s * 0.22, s * 0.10)
        box = [ex - r1 * abs(math.cos(a)) - r2 * abs(math.sin(a)),
               ey - r1 * abs(math.sin(a)) - r2 * abs(math.cos(a)),
               ex + r1 * abs(math.cos(a)) + r2 * abs(math.sin(a)),
               ey + r1 * abs(math.sin(a)) + r2 * abs(math.cos(a))]
        d.ellipse(box, outline=ORO if a0 % 90 == 0 else ORO_LO, width=7)
    ring(d, cx, cy, s * 0.14, w=8)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=ORO)

def i_malaquita(img, d, cx, cy, s):
    d.line([(cx - s * 0.85, cy - s * 0.35), (cx + s * 0.85, cy - s * 0.35)], fill=ORO, width=W_LINE)
    for k, r0 in enumerate((0.20, 0.36, 0.52, 0.68, 0.84)):
        pts = []
        for a in range(0, 182, 3):
            r = s * r0 * (1 + 0.08 * math.sin(math.radians(a * 2.4) + k * 1.3))
            pts.append((cx + r * math.cos(math.radians(a)), cy - s * 0.35 + r * math.sin(math.radians(a)) * 0.9))
        d.line(pts, fill=ORO if k % 2 == 0 else ORO_LO, width=8 if k % 2 else W_LINE, joint="curve")

def i_meandro(img, d, cx, cy, s):
    u = s * 0.36
    x0, y0 = cx - s * 0.9, cy + s * 0.45
    pts = [(x0, y0)]
    def add(dx, dy): pts.append((pts[-1][0] + dx * u, pts[-1][1] + dy * u))
    for _ in range(3):
        add(0, -2.5); add(1.6, 0); add(0, 1.6); add(-0.8, 0); add(0, -0.8); add(0.9, 0)  # key unit-ish
        pts.append((pts[-1][0], y0));
    d.line(pts[:20], fill=ORO, width=W_LINE, joint="curve")

def i_marqueteria(img, d, cx, cy, s):
    a = s * 0.85
    d.polygon([(cx, cy - a), (cx + a * 0.72, cy), (cx, cy + a), (cx - a * 0.72, cy)], outline=ORO, width=W_LINE)
    b = a * 0.55
    d.polygon([(cx, cy - b), (cx + b * 0.72, cy), (cx, cy + b), (cx - b * 0.72, cy)], outline=ORO, width=7)
    d.line([(cx, cy - a), (cx, cy + a)], fill=ORO_LO, width=6)
    d.line([(cx - a * 0.72, cy), (cx + a * 0.72, cy)], fill=ORO_LO, width=6)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=ORO)

# ---------------------------------------------------------------- catalogue
COVERS = [
    ("serie-nocturna",  "SERIE NOCTURNA", "CÁPSULA BLACK + GOLD",   i_nocturna),
    ("capsula-telar",   "TELAR",          "ARTE TEXTIL",            i_telar),
    ("capsula-deco",    "DÉCO",           "ÉPOCA DORADA",           i_deco),
    ("capsula-panuelo", "PAÑUELO",        "PAISLEY REAL",           i_panuelo),
    ("capsula-azulejo", "AZULEJO",        "CERÁMICA REAL",          i_azulejo),
    ("capsula-forma-color", "FORMA & COLOR", "GEOMETRÍA MODERNA",   i_forma),
    ("capsula-cianotipo", "CIANOTIPO",    "HERBARIO DE PRUSIA",     i_cianotipo),
    ("capsula-suminagashi", "SUMINAGASHI", "TINTA AL AGUA",         i_suminagashi),
    ("capsula-relieve", "RELIEVE",        "TOPOGRAFÍA REAL",        i_relieve),
    ("capsula-nube-imperial", "NUBE IMPERIAL", "CIELO REAL",        i_nube),
    ("capsula-salpicadura", "SALPICADURA", "ATELIER REAL",          i_salpicadura),
    ("linea-via",       "VÍA",            "LÍNEA — ASFALTO",        i_via),
    ("linea-moire",     "MOIRÉ",          "LÍNEA — OP-ART",         i_moire),
    ("linea-estatica",  "ESTÁTICA",       "LÍNEA — GLITCH",         i_estatica),
    ("linea-trazo",     "TRAZO",          "LÍNEA — SPLATTER",       i_trazo),
    ("capsula-observatorio", "OBSERVATORIO", "CARTA DEL NORTE",     i_observatorio),
    ("capsula-vidriera", "VIDRIERA",      "LUZ REGIA",              i_vidriera),
    ("capsula-neon",    "NEÓN",           "LA CORONA NUNCA DUERME", i_neon),
    ("capsula-guilloche", "GUILLOCHÉ",    "GRABADO REAL",           i_guilloche),
    ("capsula-plumaje", "PLUMAJE",        "OJO DEL PAVO REAL",      i_plumaje),
    ("kintsugi-real",   "KINTSUGI",       "PORCELANA & ORO",        i_kintsugi),
    ("capsula-frecuencia", "FRECUENCIA",  "ONDAS DE SONIDO",        i_frecuencia),
    ("capsula-baraja",  "BARAJA",         "LA CORTE REAL",          i_baraja),
    ("capsula-laurel",  "LAUREL",         "VICTORIA REAL",          i_laurel),
    ("capsula-camo-real", "CAMO REAL",    "LA CORONA SE CAMUFLA",   i_camo),
    ("capsula-eslabon", "ESLABÓN",        "CADENA REAL",            i_eslabon),
    ("capsula-tartan",  "TARTÁN",         "HERENCIA REAL",          i_tartan),
    ("capsula-forja",   "FORJA",          "HIERRO Y ORO",           i_forja),
    ("capsula-brocado", "BROCADO",        "SEDA REAL",              i_brocado),
    ("capsula-malaquita", "MALAQUITA",    "PIEDRA REAL",            i_malaquita),
    ("capsula-meandro", "MEANDRO",        "LABERINTO REAL",         i_meandro),
    ("capsula-marqueteria", "MARQUETERÍA", "INTARSIA REAL",         i_marqueteria),
]

if __name__ == "__main__":
    import sys
    only = set(sys.argv[1:])
    for name, title, sub, icon in COVERS:
        if only and name not in only:
            continue
        compose(name, title, sub, icon)
