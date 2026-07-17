#!/usr/bin/env python3
# Cápsula Cianotipo — Herbario de Prusia (SRHOOD)
# Botanical cyanotype (Anna Atkins style): white botanical photograms on Prussian blue.
# Generates 6 print artworks + composites them onto blank Printful mockups.
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "designs_cianotipo")
os.makedirs(OUT, exist_ok=True)
SCR = os.path.join(HERE, "..", "scratch")
OUTC = os.path.join(SCR, "out")
os.makedirs(OUTC, exist_ok=True)

# ---- palette (Prussian cyanotype) ----
PRUS_TOP = (19, 47, 76)
PRUS_BOT = (8, 24, 42)
PRUS_MID = (27, 64, 100)
CIAN     = (150, 196, 222)
TIZA     = (232, 242, 247)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def F(p, s): return ImageFont.truetype(p, s)

def prussian_wash(w, h, seed=1, vignette=True):
    """Mottled Prussian-blue cyanotype ground."""
    rnd = np.random.default_rng(seed)
    # vertical gradient
    ty = np.linspace(0, 1, h)[:, None]
    grad = np.zeros((h, w, 3), np.float32)
    for i in range(3):
        grad[..., i] = PRUS_TOP[i] + (PRUS_BOT[i] - PRUS_TOP[i]) * ty
    # low-frequency mottle (brush wash)
    low = rnd.normal(0, 1, (h // 24 + 2, w // 24 + 2)).astype(np.float32)
    low = np.array(Image.fromarray(((low - low.min()) / (np.ptp(low) + 1e-6) * 255).astype(np.uint8))
                   .resize((w, h), Image.BICUBIC), np.float32) / 255.0
    mottle = (low - 0.5) * 26.0
    for i in range(3):
        grad[..., i] += mottle * (0.7 + 0.3 * i / 2)
    # fine grain
    grain = rnd.normal(0, 5.0, (h, w)).astype(np.float32)
    grad += grain[..., None]
    if vignette:
        yy, xx = np.mgrid[0:h, 0:w]
        cx, cy = w / 2, h / 2
        d = np.sqrt(((xx - cx) / (w / 2)) ** 2 + ((yy - cy) / (h / 2)) ** 2)
        vg = np.clip(1.0 - 0.16 * np.clip(d - 0.5, 0, 1), 0, 1)
        grad *= vg[..., None]
    return Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8), "RGB")

def new_ink():
    """Transparent layer to draw white botanicals on."""
    return Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))

def stamp(bg, ink, glow=True):
    """Composite white ink onto bg with a soft photogram halo."""
    if glow:
        halo = ink.filter(ImageFilter.GaussianBlur(9))
        a = halo.split()[3].point(lambda v: int(v * 0.35))
        halo.putalpha(a)
        bg = Image.alpha_composite(bg.convert("RGBA"), halo)
    ink = ink.filter(ImageFilter.GaussianBlur(0.6))
    return Image.alpha_composite(bg.convert("RGBA"), ink)

# ----------------------- botanical primitives -----------------------
def leaflet(d, x, y, ang, ln, wd, col=TIZA, a=235):
    """A pointed leaflet (thin ellipse) rotated around its base."""
    pts = []
    for t in np.linspace(0, 1, 14):
        wcur = math.sin(t * math.pi) * wd * (1 - 0.15 * t)
        pts.append((t * ln, -wcur / 2))
    for t in np.linspace(1, 0, 14):
        wcur = math.sin(t * math.pi) * wd * (1 - 0.15 * t)
        pts.append((t * ln, wcur / 2))
    ca, sa = math.cos(ang), math.sin(ang)
    poly = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]
    d.polygon(poly, fill=col + (a,))

def fern(layer, x, y, length, ang=-90, side_len=54, seed=0, col=TIZA):
    d = ImageDraw.Draw(layer)
    rnd = random.Random(seed)
    n = 22
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    # stem
    x2, y2 = x + ca * length, y + sa * length
    d.line([(x, y), (x2, y2)], fill=col + (235,), width=max(3, int(side_len * 0.09)))
    for i in range(n):
        t = i / (n - 1)
        px = x + ca * length * t
        py = y + sa * length * t
        sl = side_len * (1.0 - 0.72 * t) * (0.9 + 0.2 * rnd.random())
        curl = 18 * (1 - t)
        leaflet(d, px, py, math.radians(ang - 52 - curl), sl, sl * 0.32, col)
        leaflet(d, px, py, math.radians(ang + 52 + curl), sl, sl * 0.32, col)
    # tip
    leaflet(d, x2, y2, math.radians(ang), side_len * 0.3, side_len * 0.12, col)

def broad_leaf(layer, cx, cy, h, ang=0, split=True, col=TIZA):
    """Ovate leaf photogram: pointed-tip blade with carved midrib + herringbone veins.
    ang=0 -> tip points up. `split` carves the veins (leaf detail)."""
    d = ImageDraw.Draw(layer)
    w = h * 0.62
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    def M(px, py):  # local (tip up = -y) -> world
        return (cx + px * ca - py * sa, cy + px * sa + py * ca)
    # ovate blade: narrow pointed tip at top (t=0), rounded base at bottom (t=1)
    N = 64
    right, left = [], []
    for i in range(N + 1):
        t = i / N
        yy = -h / 2 + h * t
        ww = (math.sin(t * math.pi) ** 0.62) * (w / 2) * (0.55 + 0.45 * t)
        right.append((ww, yy)); left.append((-ww, yy))
    poly = [M(*p) for p in right] + [M(*p) for p in reversed(left)]
    d.polygon(poly, fill=col + (235,))
    if split:
        cut = ImageDraw.Draw(layer)
        vw = max(3, int(h * 0.010))
        # midrib
        cut.line([M(0, -h/2 + h*0.02), M(0, h/2 - h*0.02)], fill=(0,0,0,0), width=vw+2)
        # herringbone lateral veins
        nv = 9
        for s in range(1, nv + 1):
            t = s / (nv + 1)
            yy = -h / 2 + h * t
            ww = (math.sin(t * math.pi) ** 0.62) * (w / 2) * (0.55 + 0.45 * t)
            for sign in (-1, 1):
                cut.line([M(0, yy), M(sign * ww * 0.86, yy + h * 0.075)], fill=(0,0,0,0), width=vw)

def algae(layer, x, y, length, ang=-90, seed=1, col=TIZA):
    """Feathery seaweed frond: wavy stem with fine filaments."""
    d = ImageDraw.Draw(layer)
    rnd = random.Random(seed)
    pts = []
    cur = ang
    px, py = x, y
    seglen = length / 26
    for i in range(26):
        cur += rnd.uniform(-10, 10)
        px += math.cos(math.radians(cur)) * seglen
        py += math.sin(math.radians(cur)) * seglen
        pts.append((px, py, cur))
    for i in range(len(pts) - 1):
        d.line([pts[i][:2], pts[i + 1][:2]], fill=col + (230,), width=max(2, int(6 * (1 - i / len(pts)))))
    for (fx, fy, fc) in pts[::1]:
        for sgn in (-1, 1):
            fl = 26 * (0.5 + rnd.random())
            leaflet(d, fx, fy, math.radians(fc + sgn * 62), fl, fl * 0.22, col, a=210)

def eucalyptus(layer, x, y, length, ang=-90, seed=2, col=TIZA, rscale=1.0):
    d = ImageDraw.Draw(layer)
    rnd = random.Random(seed)
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    x2, y2 = x + ca * length, y + sa * length
    d.line([(x, y), (x2, y2)], fill=col + (230,), width=max(3, int(4 * rscale)))
    n = int(13 * (0.7 + 0.5 * rscale))
    for i in range(n):
        t = (i + 0.5) / n
        px = x + ca * length * t
        py = y + sa * length * t
        r = 22 * rscale * (1.0 - 0.5 * t) * (0.9 + 0.2 * rnd.random())
        for sgn in (-1, 1):
            off = (14 + 8 * rscale) * (1 - 0.4 * t)
            lx = px + math.cos(math.radians(ang + sgn * 90)) * off
            ly = py + math.sin(math.radians(ang + sgn * 90)) * off
            # angle each leaf slightly outward/up
            la = math.radians(ang + sgn * 42)
            ex, ey = math.cos(la), math.sin(la)
            leaf_poly = []
            for tt in np.linspace(0, 1, 12):
                wc = math.sin(tt * math.pi) * r * 0.5
                leaf_poly.append((lx + ex * tt * r * 1.5 - ey * wc, ly + ey * tt * r * 1.5 + ex * wc))
            for tt in np.linspace(1, 0, 12):
                wc = math.sin(tt * math.pi) * r * 0.5
                leaf_poly.append((lx + ex * tt * r * 1.5 + ey * wc, ly + ey * tt * r * 1.5 - ex * wc))
            d.polygon(leaf_poly, fill=col + (225,))

# ----------------------- panel framing -----------------------
def text_tracked(d, xy, text, font, fill, tracking=0, center=False):
    x, y = xy
    ws = [d.textlength(c, font=font) for c in text]
    total = sum(ws) + tracking * (len(text) - 1)
    if center: x -= total / 2
    for c, cw in zip(text, ws):
        d.text((x, y), c, font=font, fill=fill)
        x += cw + tracking

def frame_panel(img, num, subtitle):
    """Add keyline border + wordmark, cyanotype label."""
    d = ImageDraw.Draw(img, "RGBA")
    m = int(SZ * 0.055)
    d.rectangle([m, m, SZ - m, SZ - m], outline=TIZA + (180,), width=3)
    # wordmark block bottom
    d.rectangle([SZ * 0.30, SZ * 0.845, SZ * 0.70, SZ * 0.847], fill=CIAN + (200,))
    text_tracked(d, (SZ / 2, SZ * 0.865), "STREET ROYALTY", F(SANS_B, int(SZ * 0.040)), TIZA + (255,),
                 tracking=int(SZ * 0.010), center=True)
    text_tracked(d, (SZ / 2, SZ * 0.915), subtitle, F(SANS, int(SZ * 0.021)), CIAN + (255,),
                 tracking=int(SZ * 0.006), center=True)
    text_tracked(d, (SZ * 0.5, SZ * 0.075), f"CIANOTIPO · Nº{num}", F(SANS, int(SZ * 0.019)), CIAN + (230,),
                 tracking=int(SZ * 0.004), center=True)
    return img

# ================= DESIGNS =================
SZ = 1600

def design_panel(kind, num, subtitle, seed):
    global SZ
    SZ = 1600
    bg = prussian_wash(SZ, SZ, seed=seed).convert("RGBA")
    ink = new_ink()
    if kind == "fern":
        for k, (x, ang, ln, sl) in enumerate([
            (SZ*0.30, -74, SZ*0.60, 78), (SZ*0.52, -90, SZ*0.66, 86),
            (SZ*0.72, -104, SZ*0.57, 74), (SZ*0.42, -84, SZ*0.40, 52),
            (SZ*0.62, -96, SZ*0.42, 54)]):
            fern(ink, x, SZ*0.80, ln, ang=ang, side_len=sl, seed=seed+k)
    elif kind == "euca":
        for k, (x, ang, ln) in enumerate([
            (SZ*0.32, -72, SZ*0.60), (SZ*0.50, -90, SZ*0.66), (SZ*0.68, -106, SZ*0.60),
            (SZ*0.42, -82, SZ*0.42), (SZ*0.60, -98, SZ*0.44)]):
            eucalyptus(ink, x, SZ*0.82, ln, ang=ang, seed=seed+k, rscale=1.7)
    elif kind == "monstera":
        broad_leaf(ink, SZ*0.50, SZ*0.46, SZ*0.60, ang=8, split=True)
        broad_leaf(ink, SZ*0.30, SZ*0.60, SZ*0.34, ang=-24, split=True)
        broad_leaf(ink, SZ*0.72, SZ*0.58, SZ*0.34, ang=26, split=True)
    bg = stamp(bg, ink)
    bg = frame_panel(bg, num, subtitle)
    return bg.convert("RGB")

def design_allover(kind, seed, sz=1600, dens=0.24, mscale=1.0):
    """Full-bleed botanical field for shoes/socks (no frame/text)."""
    global SZ
    SZ = sz
    bg = prussian_wash(sz, sz, seed=seed).convert("RGBA")
    ink = new_ink()
    rnd = random.Random(seed)
    step = int(sz * dens)
    for gy in range(-step, sz + step, step):
        for gx in range(-step, sz + step, step):
            jx = gx + rnd.randint(-step//4, step//4)
            jy = gy + rnd.randint(-step//4, step//4)
            ang = rnd.uniform(0, 360)
            pick = rnd.random()
            if kind == "sprig":
                if pick < 0.5:
                    fern(ink, jx, jy, sz*0.17*mscale, ang=ang, side_len=int(sz*0.030*mscale), seed=rnd.randint(0,9999))
                elif pick < 0.8:
                    eucalyptus(ink, jx, jy, sz*0.15*mscale, ang=ang, seed=rnd.randint(0,9999), rscale=mscale)
                else:
                    broad_leaf(ink, jx, jy, sz*0.11*mscale, ang=ang, split=False)
            elif kind == "mini":
                if pick < 0.62:
                    fern(ink, jx, jy, sz*0.13*mscale, ang=ang, side_len=int(sz*0.024*mscale), seed=rnd.randint(0,9999))
                elif pick < 0.85:
                    eucalyptus(ink, jx, jy, sz*0.11*mscale, ang=ang, seed=rnd.randint(0,9999), rscale=mscale)
                else:
                    broad_leaf(ink, jx, jy, sz*0.075*mscale, ang=ang, split=False)
    bg = stamp(bg, ink)
    return bg.convert("RGB")

# ================= COMPOSITING =================
def relight(panel_rgb, base_region_rgb, k=1.35):
    """Bake fabric folds from base luminance into panel via relative shading.
    Base luminance is heavily blurred so only large-scale folds transfer, not any
    printed logo/edges on the blank mockup."""
    p = np.asarray(panel_rgb, np.float32)
    w, h = base_region_rgb.size
    rad = max(6, int(max(w, h) * 0.06))
    bl = base_region_rgb.convert("L").filter(ImageFilter.GaussianBlur(rad))
    b = np.asarray(bl, np.float32)
    bmean = b.mean()
    delta = (b - bmean) / 255.0
    factor = np.clip(1.0 + k * delta, 0.5, 1.55)[..., None]
    out = np.clip(p * factor, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGB")

def paste_panel(base, panel, box, k=1.35, radius=18):
    """Paste a square design panel into box=(x0,y0,x1,y1) with fold shading + soft corners."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    panel = panel.resize((w, h), Image.LANCZOS)
    region = base.crop(box)
    shaded = relight(panel, region, k=k)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w-1, h-1], radius=radius, fill=255)
    base = base.copy()
    base.paste(shaded, (x0, y0), mask)
    return base

def paste_pattern_poly(base, pattern, poly, k=0.9, feather=3):
    """Paste an all-over pattern into an arbitrary polygon with fold relighting."""
    W, H = base.size
    pattern = pattern.resize((W, H), Image.LANCZOS)
    shaded = relight(pattern, base, k=k)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    if feather:
        mask = mask.filter(ImageFilter.GaussianBlur(feather))
    out = base.copy()
    out.paste(shaded, (0, 0), mask)
    return out

def composite_region_bright(base, pattern, bbox, thresh=140, k=1.1, feather=2):
    """Paste pattern where the base is bright within bbox (e.g. sock leg, excludes dark foot)."""
    W, H = base.size
    pattern = pattern.resize((W, H), Image.LANCZOS)
    shaded = relight(pattern, base, k=k)
    L = np.asarray(base.convert("L"))
    x0, y0, x1, y1 = bbox
    m = np.zeros((H, W), np.uint8)
    box = np.zeros((H, W), bool); box[y0:y1, x0:x1] = True
    m[(L >= thresh) & box] = 255
    mask = Image.fromarray(m).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(feather))
    out = base.copy()
    out.paste(shaded, (0, 0), mask)
    return out

def ellipse_poly(cx, cy, rx, ry, ang=0, n=48):
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        px, py = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + px * ca - py * sa, cy + px * sa + py * ca))
    return pts

def flood_bg(base, tol=18):
    """Mask of the shoe (True=shoe) by flood-filling white bg from corners."""
    im = base.convert("L")
    arr = np.asarray(im, np.int16)
    h, w = arr.shape
    from collections import deque
    seen = np.zeros((h, w), bool)
    dq = deque()
    for c in [(0,0),(0,w-1),(h-1,0),(h-1,w-1),(0,w//2),(h-1,w//2)]:
        dq.append(c); seen[c]=True
    base_val = 244
    while dq:
        y,x = dq.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and arr[ny,nx]>=base_val-tol:
                seen[ny,nx]=True; dq.append((ny,nx))
    shoe = ~seen
    from PIL import ImageFilter as IF
    m = Image.fromarray((shoe*255).astype(np.uint8)).filter(IF.MedianFilter(5))
    return m

def composite_allover_shoe(base, pattern, poly=None, k=1.15, keep_sole=None):
    """Composite all-over pattern onto shoe upper. poly restricts print region."""
    W,H = base.size
    pattern = pattern.resize((W,H), Image.LANCZOS)
    shoe = flood_bg(base)
    mask = np.asarray(shoe, np.uint8)
    if poly is not None:
        pm = Image.new("L",(W,H),0)
        ImageDraw.Draw(pm).polygon(poly, fill=255)
        mask = np.minimum(mask, np.asarray(pm))
    # shade pattern by base luminance (relative) to keep folds/creases
    shaded = relight(pattern, base, k=k)
    m = Image.fromarray(mask).filter(ImageFilter.GaussianBlur(1.2))
    out = base.copy()
    out.paste(shaded, (0,0), m)
    return out

if __name__ == "__main__":
    print("generating panels...")
    panels = {
        "01-fern":     ("fern", "01", "HERBARIO · HELECHO", 11),
        "02-euca":     ("euca", "02", "HERBARIO · EUCALIPTO", 23),
        "03-monstera": ("monstera", "03", "HERBARIO · MONSTERA", 31),
    }
    P = {}
    for name,(kind,num,sub,seed) in panels.items():
        img = design_panel(kind,num,sub,seed)
        img.save(f"{OUT}/panel-{name}.jpg", quality=92)
        P[name]=img
        print(" panel", name)
    print("generating all-overs...")
    ao_sprig = design_allover("sprig", 41, 1600, dens=0.125, mscale=0.62); ao_sprig.save(f"{OUT}/ao-sprig.jpg", quality=90)
    ao_ath   = design_allover("sprig", 57, 1600, dens=0.125, mscale=0.58); ao_ath.save(f"{OUT}/ao-ath.jpg", quality=90)
    ao_mini  = design_allover("mini", 63, 1200, dens=0.12, mscale=0.7);  ao_mini.save(f"{OUT}/ao-mini.jpg", quality=90)
    print("compositing garments...")
    # Tee (ash) 1000x1000
    tee = Image.open(f"{SCR}/blank_tee_ash.jpg").convert("RGB")
    tee = paste_panel(tee, P["01-fern"], (352, 210, 648, 506), k=1.3)
    tee.save(f"{OUTC}/mk_tee.jpg", quality=92)
    # Crew (black)
    crew = Image.open(f"{SCR}/base_crew_black.jpg").convert("RGB")
    crew = paste_panel(crew, P["02-euca"], (362, 196, 638, 472), k=1.55)
    crew.save(f"{OUTC}/mk_crew.jpg", quality=92)
    # Hoodie (grey)
    hood = Image.open(f"{SCR}/blank_hoodie_grey.jpg").convert("RGB")
    hood = paste_panel(hood, P["03-monstera"], (368, 284, 632, 548), k=1.4)
    hood.save(f"{OUTC}/mk_hoodie.jpg", quality=92)
    # Socks (white leg) — full-bleed sublimation via brightness mask on each leg
    socks = Image.open(f"{SCR}/base_socks.jpg").convert("RGB")
    socks = composite_region_bright(socks, ao_mini, (222, 70, 420, 505), thresh=95, k=1.15)
    socks = composite_region_bright(socks, ao_mini, (578, 70, 778, 505), thresh=95, k=1.15)
    socks.save(f"{OUTC}/mk_socks.jpg", quality=92)
    # High-top left — canvas side panel polygon (excludes white sole + toe cap)
    htop = Image.open(f"{SCR}/base_htop_left_clean.jpg").convert("RGB")
    # hug the full canvas: toe stitch -> vamp -> collar -> heel -> sole line
    poly = [(190,600),(180,520),(232,452),(300,372),(398,320),(520,282),(648,258),
            (712,250),(772,258),(842,296),(890,360),(902,470),(892,556),(864,612),
            (700,642),(430,650),(270,646),(200,632)]
    htop = paste_pattern_poly(htop, ao_sprig, poly, k=0.8, feather=2)
    htop.save(f"{OUTC}/mk_htop.jpg", quality=92)
    # Athletic top-down — one ellipse per shoe upper
    ath = Image.open(f"{SCR}/base_athletic_clean.jpg").convert("RGB")
    for cx, cy in [(360, 470), (648, 470)]:
        ath = paste_pattern_poly(ath, ao_ath, ellipse_poly(cx, cy, 168, 330, ang=0), k=0.8)
    ath.save(f"{OUTC}/mk_athletic.jpg", quality=92)
    print("done")
