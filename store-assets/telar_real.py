#!/usr/bin/env python3
# Telar Real — Cápsula Arte Textil SRH: 6 diseños originales inspirados en
# oficios textiles clásicos (damasco, asanoha, bargello, seigaiha, celosía, espiga).
# Ningún patrón repetido de series anteriores (Nocturna, Street Lab, Royal Ink...).
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

NEGRO      = (13, 12, 14)
CARBON     = (26, 24, 28)
CREMA      = (241, 233, 216)
ORO        = (199, 162, 75)
ORO_HI     = (235, 206, 124)
ORO_LO     = (148, 116, 52)
BURDEOS    = (86, 22, 34)
BURDEOS_HI = (128, 42, 58)
NAVY       = (22, 30, 52)
NAVY_HI    = (42, 56, 90)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

def F(path, size): return ImageFont.truetype(path, size)

def grain(img, blend=0.035, seed=7):
    noise = Image.effect_noise(img.size, 14).convert("L")
    return Image.blend(img.convert("RGB"), Image.merge("RGB", (noise,) * 3), blend)

def text_tracked(draw, xy, text, font, fill, tracking=0, center=True):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if center: x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking
    return total

def taper_stroke(draw, pts, w0, w1, fill):
    """Filled polygon strip along polyline pts with linearly tapering width."""
    if len(pts) < 2: return
    left, right = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        if i == 0: dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1: dx, dy = x - pts[i-1][0], y - pts[i-1][1]
        else: dx, dy = pts[i+1][0] - pts[i-1][0], pts[i+1][1] - pts[i-1][1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    draw.polygon(left + right[::-1], fill=fill)

def spiral(cx, cy, r0, r1, a0, a1, steps=120):
    """Log-spiral polyline from angle a0..a1 (rad), radius r0..r1."""
    pts = []
    b = math.log(max(r1, 1) / max(r0, 1)) / (a1 - a0) if a1 != a0 else 0
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        r = r0 * math.exp(b * (a - a0))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def leaf(draw, x, y, ang, ln, wd, fill):
    """Teardrop leaf pointing along ang."""
    pts = []
    for i in range(25):
        t = i / 24
        w = wd * math.sin(math.pi * t) * (1 - t * 0.35)
        px, py = x + ln * t, 0
        pts.append((px, py - w / 2))
    for i in range(24, -1, -1):
        t = i / 24
        w = wd * math.sin(math.pi * t) * (1 - t * 0.35)
        px = x + ln * t
        pts.append((px, w / 2))
    ca, sa = math.cos(ang), math.sin(ang)
    rot = [(x + (px - x) * ca - py * sa, y + (px - x) * sa + py * ca) for px, py in pts]
    draw.polygon(rot, fill=fill)

def crown(draw, cx, cy, w, h, fill, outline=None, ow=0):
    l, r, b, t = cx - w/2, cx + w/2, cy + h/2, cy - h/2
    dip = b - h * 0.42
    pts = [(l, b), (l, t + h*.30), (l + w*.185, dip), (cx - w*.155, t + h*.12),
           (cx, dip - h*.02), (cx + w*.155, t + h*.12), (r - w*.185, dip), (r, t + h*.30), (r, b)]
    draw.polygon(pts, fill=fill, outline=outline, width=ow)
    draw.rectangle((l, b + h*.06, r, b + h*.16), fill=fill)

def bez(p0, p1, p2, p3, steps=90):
    pts = []
    for i in range(steps + 1):
        t = i / steps; u = 1 - t
        x = u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts

# ---------------------------------------------------------------- 1. DAMASCO
def damasco():
    S = 2
    W, H = 3600 * S, 4800 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = W // 2, int(H * 0.40)
    half = Image.new("RGBA", (W // 2, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(half)
    hx = W // 2  # mirror axis at right edge of half canvas

    def scroll_curve(pts, w0, w1, col, nleaves, lmax, lmin, lcol, side=1, curl=True):
        """Tapered stroke along pts with leaves on one side, sizes ramping down."""
        taper_stroke(hd, pts, w0, w1, col)
        for k in range(nleaves):
            t = 0.12 + 0.78 * k / max(nleaves - 1, 1)
            i = int(t * (len(pts) - 1))
            x, y = pts[i]
            dx = pts[min(i+3, len(pts)-1)][0] - pts[max(i-3, 0)][0]
            dy = pts[min(i+3, len(pts)-1)][1] - pts[max(i-3, 0)][1]
            ang = math.atan2(dy, dx) + side * math.pi / 2
            sz = lmax + (lmin - lmax) * k / max(nleaves - 1, 1)
            leaf(hd, x, y, ang, sz, sz * 0.40, lcol)
        if curl:  # terminal curl at the end of the stem
            ex, ey = pts[-1]
            dx = pts[-1][0] - pts[-6][0]; dy = pts[-1][1] - pts[-6][1]
            a0 = math.atan2(dy, dx)
            taper_stroke(hd, spiral(ex, ey, 4*S, 60*S, a0 + math.pi*2.2, a0, 60), w1, 2*S, col)

    # --- big mirrored S-scroll framing the medallion (ogee shape)
    s_main = bez((hx - 30*S, cy + 620*S), (hx - 720*S, cy + 480*S),
                 (hx - 700*S, cy - 520*S), (hx - 70*S, cy - 720*S), 110)
    scroll_curve(s_main, 26*S, 7*S, ORO, 7, 200*S, 80*S, ORO, side=1)
    # crema echo inside, thin and quiet
    s_echo = bez((hx - 30*S, cy + 500*S), (hx - 560*S, cy + 380*S),
                 (hx - 545*S, cy - 400*S), (hx - 60*S, cy - 570*S), 90)
    taper_stroke(hd, s_echo, 6*S, 3*S, CREMA)
    # lower outward flourish
    s_low = bez((hx - 60*S, cy + 640*S), (hx - 420*S, cy + 760*S),
                (hx - 700*S, cy + 900*S), (hx - 840*S, cy + 1160*S), 80)
    scroll_curve(s_low, 18*S, 5*S, ORO_LO, 4, 150*S, 70*S, ORO_LO, side=-1)
    # berries tucked along the main scroll, deliberate placement
    for t, r, col in [(0.18, 22, ORO_HI), (0.42, 16, BURDEOS_HI), (0.66, 20, ORO_HI), (0.88, 14, BURDEOS_HI)]:
        i = int(t * (len(s_main) - 1))
        x, y = s_main[i]
        dx = s_main[min(i+3, len(s_main)-1)][0] - s_main[max(i-3, 0)][0]
        dy = s_main[min(i+3, len(s_main)-1)][1] - s_main[max(i-3, 0)][1]
        l = math.hypot(dx, dy) or 1
        x -= dy / l * 90 * S * -1; y += dx / l * 90 * S * -1
        hd.ellipse((x - r*S, y - r*S, x + r*S, y + r*S), fill=col)

    img.paste(half, (0, 0), half)
    flip = half.transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(flip, (W // 2, 0), flip)

    # --- crest palmette (fan) above
    py = cy - 850 * S
    for k in range(9):
        a = -math.pi/2 + (k - 4) * math.pi / 13
        sz = 250*S - abs(k - 4) * 34 * S
        leaf(d, cx + math.cos(a) * 90 * S, py + math.sin(a) * 90 * S, a, sz, sz * 0.38,
             ORO_HI if k % 2 == 0 else ORO)
    d.arc((cx - 110*S, py - 110*S, cx + 110*S, py + 110*S), 0, 360, fill=CREMA, width=6*S)

    # --- pendant drop below
    by = cy + 700 * S
    dd = 46 * S
    d.polygon([(cx, by - dd), (cx + dd, by), (cx, by + dd), (cx - dd, by)], fill=ORO_HI)
    leaf(d, cx, by + 60*S, math.pi / 2, 210*S, 80*S, ORO)
    d.ellipse((cx - 12*S, by + 300*S, cx + 12*S, by + 324*S), fill=CREMA)

    # central palmette + crown
    d.ellipse((cx - 340*S, cy - 340*S, cx + 340*S, cy + 340*S), fill=NEGRO + (255,))
    d.ellipse((cx - 340*S, cy - 340*S, cx + 340*S, cy + 340*S), outline=ORO, width=14*S)
    d.ellipse((cx - 296*S, cy - 296*S, cx + 296*S, cy + 296*S), outline=ORO_LO, width=5*S)
    crown(d, cx, cy - 20*S, 300*S, 220*S, ORO, ORO_HI, 6*S)
    for i in range(16):  # sunburst ticks
        a = i * math.pi * 2 / 16
        x1, y1 = cx + 360*S*math.cos(a), cy + 360*S*math.sin(a)
        x2, y2 = cx + 410*S*math.cos(a), cy + 410*S*math.sin(a)
        d.line((x1, y1, x2, y2), fill=ORO_LO, width=8*S)
    d.text((cx, cy + 170*S), "1996", font=F(SERIF_B, 90*S), fill=CREMA, anchor="mm")

    # base text
    ty = int(H * 0.80)
    d.line((cx - 700*S, ty - 60*S, cx + 700*S, ty - 60*S), fill=ORO_LO, width=6*S)
    text_tracked(d, (cx, ty), "STREET ROYALTY", F(SERIF_B, 150*S), CREMA, tracking=70*S)
    text_tracked(d, (cx, ty + 230*S), "DAMASCO REAL · CÁPSULA TELAR", F(SERIF, 62*S), ORO, tracking=26*S)
    d.line((cx - 700*S, ty + 360*S, cx + 700*S, ty + 360*S), fill=ORO_LO, width=6*S)

    img = img.resize((3600, 4800), Image.LANCZOS)
    img.save(f"{OUT}/telar_damasco.png")

# ---------------------------------------------------------------- 2. ASANOHA
def asanoha():
    S = 2
    W, H = 3600 * S, 4800 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cy = W // 2, int(H * 0.42)
    rw, rh = 1450 * S, 1750 * S   # rhombus half-widths
    rhomb = [(cx, cy - rh), (cx + rw, cy), (cx, cy + rh), (cx - rw, cy)]

    lattice = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lattice)
    rnd = random.Random(3)
    t = 300 * S  # triangle side
    hgt = t * math.sqrt(3) / 2
    row = 0
    y = cy - rh - hgt
    while y < cy + rh + hgt:
        x = cx - rw - t
        off = (t / 2) if row % 2 else 0
        while x < cx + rw + t:
            for up in (True, False):
                if up: v = [(x + off, y + hgt), (x + off + t, y + hgt), (x + off + t/2, y)]
                else:  v = [(x + off + t/2, y), (x + off + t*1.5, y), (x + off + t, y + hgt)]
                gx = sum(p[0] for p in v) / 3
                gy = sum(p[1] for p in v) / 3
                col = ORO_HI if rnd.random() < 0.14 else ORO
                wdt = 9 * S
                for p in v:
                    ld.line((gx, gy, p[0], p[1]), fill=col, width=wdt)
                ld.line(v + [v[0]], fill=ORO_LO, width=wdt)
            x += t
        y += hgt
        row += 1

    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(rhomb, fill=255)
    img.paste(lattice, (0, 0), Image.composite(lattice.split()[3], Image.new("L", (W, H), 0), mask))

    d = ImageDraw.Draw(img)
    def rsc(s):  # scaled rhombus
        return [(cx + (px - cx) * s, cy + (py - cy) * s) for px, py in rhomb]
    d.polygon(rsc(1.0), outline=ORO, width=16 * S)
    d.polygon(rsc(1.05), outline=ORO_LO, width=6 * S)
    for px, py in rsc(1.05):  # corner diamonds
        dd = 34 * S
        d.polygon([(px, py - dd), (px + dd, py), (px, py + dd), (px - dd, py)], fill=ORO_HI)

    # central medallion
    d.ellipse((cx - 300*S, cy - 300*S, cx + 300*S, cy + 300*S), fill=BURDEOS + (255,))
    d.ellipse((cx - 300*S, cy - 300*S, cx + 300*S, cy + 300*S), outline=ORO, width=12*S)
    d.ellipse((cx - 256*S, cy - 256*S, cx + 256*S, cy + 256*S), outline=ORO_LO, width=5*S)
    crown(d, cx, cy - 10*S, 260*S, 190*S, ORO_HI)

    ty = cy + rh + 240 * S
    text_tracked(d, (cx, ty), "STREET ROYALTY", F(SERIF_B, 130*S), CREMA, tracking=60*S)
    text_tracked(d, (cx, ty + 200*S), "ASANOHA DE ORO · CÁPSULA TELAR", F(SERIF, 58*S), ORO, tracking=22*S)

    img = img.resize((3600, 4800), Image.LANCZOS)
    img.save(f"{OUT}/telar_asanoha.png")

# ---------------------------------------------------------------- 3. BARGELLO
def bargello():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    px0, py0, px1, py1 = 300, 500, 3300, 3900
    d.rounded_rectangle((px0, py0, px1, py1), 60, fill=NEGRO + (255,))

    ramp = [NAVY, NAVY_HI, ORO_LO, ORO, ORO_HI, CREMA, ORO_HI, ORO, ORO_LO,
            BURDEOS_HI, BURDEOS, BURDEOS_HI, ORO_LO]
    cw, ch, gap = 60, 150, 5
    rnd = random.Random(5)
    ncols = (px1 - px0) // cw
    patch = Image.new("RGB", (px1 - px0, py1 - py0), NEGRO)
    pd = ImageDraw.Draw(patch)
    for c in range(ncols):
        # classic flame: sum of two triangle waves
        def tri(x, p): return abs((x % p) - p / 2) / (p / 2)
        offset = tri(c, 16) * 520 + tri(c + 4, 7) * 240
        y = -ch * 2 - offset % ch
        k = int(offset / ch)
        while y < py1 - py0:
            base = ramp[(k) % len(ramp)]
            j = rnd.uniform(-14, 14)
            col = tuple(max(0, min(255, int(v + j))) for v in base)
            pd.rounded_rectangle((c * cw + 1, y + offset % ch, (c + 1) * cw - gap,
                                  y + offset % ch + ch - gap), 8, fill=col)
            y += ch
            k += 1
    patch = grain(patch, 0.05)
    mask = Image.new("L", (px1 - px0, py1 - py0), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, px1 - px0, py1 - py0), 60, fill=255)
    img.paste(patch, (px0, py0), mask)

    d.rounded_rectangle((px0, py0, px1, py1), 60, outline=ORO, width=16)
    d.rounded_rectangle((px0 - 40, py0 - 40, px1 + 40, py1 + 40), 80, outline=ORO_LO, width=6)

    # woven label band
    bw, bh = 1720, 210
    bx, by = W // 2, py1 + 260
    d.rectangle((bx - bw/2, by, bx + bw/2, by + bh), fill=BURDEOS + (255,), outline=ORO, width=8)
    dd = ImageDraw.Draw(img)
    text_tracked(dd, (bx, by + 48), "BARGELLO IMPERIAL", F(SERIF_B, 96), CREMA, tracking=30)
    text_tracked(dd, (bx, by + bh + 90), "STREET ROYALTY · CÁPSULA TELAR · PUNTO DE LLAMA",
                 F(SERIF, 52), ORO, tracking=18)
    img.save(f"{OUT}/telar_bargello.png")

# ---------------------------------------------------------------- 4. SEIGAIHA
def seigaiha():
    S = 2
    W = H = 2325 * S
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    R = 210 * S
    stepy = int(R * 0.58)
    rnd = random.Random(9)
    golds = []
    row = 0
    y = -R
    while y < H + R:
        xoff = 0 if row % 2 == 0 else R  # half of the 2R horizontal period
        x = -R + xoff
        while x < W + R:
            gold = rnd.random() < 0.08
            ring_col = ORO_HI if gold else CREMA
            base = (30, 24, 16) if gold else (16, 22, 40)
            d.ellipse((x - R, y - R, x + R, y + R), fill=base)
            for i in range(5):
                rr = R * (1 - 0.15 * (i + 1))
                w = max(6 * S - i, 3) if not gold else 7 * S - i
                d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=ring_col, width=int(w))
            if gold:
                golds.append((x, y))
            x += 2 * R
        y += stepy
        row += 1
    # crowns on the visible crest band of a few gold scallops
    for x, y in golds[::3]:
        crown(d, x, y - R + stepy * 0.52, R * 0.30, R * 0.20, ORO_HI)
    img = grain(img, 0.04)
    img = img.resize((2325, 2325), Image.LANCZOS)
    img.save(f"{OUT}/telar_seigaiha.png")

# ---------------------------------------------------------------- 5. CELOSÍA
def celosia():
    S = 2
    W = H = 2325 * S
    img = Image.new("RGB", (W, H), NEGRO)
    d = ImageDraw.Draw(img)
    T = 465 * S  # tile size
    rnd = random.Random(4)

    def star8(cx, cy, r):
        """8-pointed star = two squares rotated 45°; returns outline points."""
        pts = []
        for i in range(16):
            a = math.pi / 8 * i - math.pi / 2 + math.pi/8
            rr = r if i % 2 == 0 else r * 0.62
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        return pts

    for gy in range(-1, H // T + 2):
        for gx in range(-1, W // T + 2):
            cx, cy = gx * T + T // 2, gy * T + T // 2
            r = T * 0.52
            star = star8(cx, cy, r)
            # shadow then bright line = depth
            d.polygon([(x + 5*S, y + 5*S) for x, y in star], outline=ORO_LO, width=7 * S)
            d.polygon(star, outline=ORO, width=8 * S)
            d.polygon(star8(cx, cy, r * 0.72), outline=ORO_LO, width=4 * S)
            # connecting cross lines between stars
            d.line((cx - T // 2, cy, cx + T // 2, cy), fill=ORO_LO, width=4 * S)
            d.line((cx, cy - T // 2, cx, cy + T // 2), fill=ORO_LO, width=4 * S)
            if rnd.random() < 0.22:
                dd = 26 * S
                d.polygon([(cx, cy - dd), (cx + dd, cy), (cx, cy + dd), (cx - dd, cy)],
                          fill=BURDEOS_HI)
            else:
                d.ellipse((cx - 12*S, cy - 12*S, cx + 12*S, cy + 12*S), fill=ORO_HI)
    img = grain(img, 0.045)
    img = img.resize((2325, 2325), Image.LANCZOS)
    img.save(f"{OUT}/telar_celosia.png")

# ---------------------------------------------------------------- 6. ESPIGA
def espiga():
    S = 2
    W, H = 1400 * S, 2400 * S
    img = Image.new("RGB", (W, H), BURDEOS)
    d = ImageDraw.Draw(img)
    col_w = 100 * S
    pitch = 46 * S
    rnd = random.Random(8)
    for c in range(W // col_w + 1):
        x0 = c * col_w
        up = c % 2 == 0
        y = -col_w
        while y < H + col_w:
            jitter = rnd.uniform(-3, 3) * S
            col = (66, 15, 25) if (y // pitch) % 2 else BURDEOS_HI
            if up:
                d.line((x0, y + col_w + jitter, x0 + col_w, y + jitter), fill=col, width=9 * S)
            else:
                d.line((x0, y + jitter, x0 + col_w, y + col_w + jitter), fill=col, width=9 * S)
            y += pitch
        if c % 4 == 3:  # gold pinstripe on the seam
            d.line((x0 + col_w, 0, x0 + col_w, H), fill=ORO, width=5 * S)
        else:
            d.line((x0 + col_w, 0, x0 + col_w, H), fill=(50, 10, 18), width=3 * S)
    img = grain(img, 0.05)
    img = img.resize((1400, 2400), Image.LANCZOS)
    img.save(f"{OUT}/telar_espiga.png")

if __name__ == "__main__":
    for fn in (damasco, asanoha, bargello, seigaiha, celosia, espiga):
        fn()
        print("ok", fn.__name__)
