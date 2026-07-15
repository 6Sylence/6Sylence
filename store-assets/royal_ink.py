#!/usr/bin/env python3
# Royal Ink — Serie de Arte SRH: 6 original poster designs for Street Royalty Hood
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

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
OLIVA   = (74, 78, 55)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF  = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
MONO   = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

def F(path, size): return ImageFont.truetype(path, size)

def grain(img, amount=10, seed=7):
    rnd = random.Random(seed)
    noise = Image.effect_noise(img.size, amount).convert("L")
    g = img.convert("RGB")
    return Image.blend(g, Image.merge("RGB", (noise, noise, noise)), 0.045)

def vgrad(size, top, bottom):
    w, h = size
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((w, h))

def crown_path(cx, cy, w, h):
    """Five-point crown polygon + base band, returns (polygon, band_rect)."""
    l = cx - w / 2; r = cx + w / 2; b = cy + h / 2; t = cy - h / 2
    dipy = b - h * 0.42
    pts = [(l, b),
           (l, t + h * 0.30), (l + w * 0.185, dipy),
           (cx - w * 0.155, t + h * 0.12), (cx, dipy - h*0.02),
           (cx + w * 0.155, t + h * 0.12), (r - w * 0.185, dipy),
           (r, t + h * 0.30), (r, b)]
    band = (l, b + h * 0.06, r, b + h * 0.16)
    return pts, band

def text_tracked(draw, xy, text, font, fill, tracking=0, anchor_center=False, stroke=0, stroke_fill=None):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if anchor_center: x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += cw + tracking
    return total

def circular_text(img, center, radius, text, font, fill, start_deg=-90, clockwise=True):
    cx, cy = center
    # measure per-char angular widths
    tmp = ImageDraw.Draw(img)
    arcs = []
    for c in text:
        w = max(tmp.textlength(c, font=font), font.size * 0.28)
        arcs.append(w / radius)
    total = sum(arcs)
    a = math.radians(start_deg) - (total / 2 if clockwise else -total / 2)
    for c, arc in zip(text, arcs):
        a_mid = a + (arc / 2 if clockwise else -arc / 2)
        x = cx + radius * math.cos(a_mid)
        y = cy + radius * math.sin(a_mid)
        size = int(font.size * 3)
        ch = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        cd = ImageDraw.Draw(ch)
        cd.text((size / 2, size / 2), c, font=font, fill=fill, anchor="mm")
        deg = math.degrees(a_mid) + (90 if clockwise else -90)
        ch = ch.rotate(-deg, resample=Image.BICUBIC, center=(size / 2, size / 2))
        img.paste(ch, (int(x - size / 2), int(y - size / 2)), ch)
        a += arc if clockwise else -arc

def footer(draw, text_main, color, y=H - 150, sub="STREET ROYALTY HOOD — MMXXVI", color_sub=None):
    f1 = F(SANS_B, 34)
    f2 = F(SANS, 24)
    text_tracked(draw, (W / 2, y), text_main, f1, color, tracking=14, anchor_center=True)
    text_tracked(draw, (W / 2, y + 52), sub, f2, color_sub or color, tracking=8, anchor_center=True)

# ---------------------------------------------------------------- 1. Corona Halftone
def d1():
    img = vgrad((W, H), (16, 16, 20), (8, 8, 10))
    draw = ImageDraw.Draw(img)
    # crown mask
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    pts, band = crown_path(W / 2, H * 0.44, W * 0.62, H * 0.30)
    md.polygon(pts, fill=255)
    md.rectangle(band, fill=255)
    # halftone dots
    step = 34
    rnd = random.Random(3)
    mpx = mask.load()
    for gy in range(0, H, step):
        for gx in range(0, W, step):
            cx = gx + step / 2; cy = gy + step / 2
            if cx >= W or cy >= H: continue
            inside = mpx[int(cx), int(cy)] > 0
            t = (cy / H)
            if inside:
                r = step * (0.46 - 0.10 * math.sin(t * math.pi * 3))
                col = tuple(int(ORO[i] + (ORO_HI[i] - ORO[i]) * (1 - t * 1.3 % 1)) for i in range(3))
            else:
                if rnd.random() > 0.16: continue
                r = step * 0.05
                col = (60, 58, 54)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # thin rule + title
    draw.rectangle([W * 0.2, H * 0.685, W * 0.8, H * 0.687], fill=ORO)
    f_big = F(SERIF_B, 110)
    draw.text((W / 2, H * 0.76), "CORONA", font=f_big, fill=CREMA, anchor="mm")
    text_tracked(draw, (W / 2, H * 0.805), "HALFTONE EDITION", F(SANS, 34), ARENA, tracking=18, anchor_center=True)
    footer(draw, "ROYAL INK · Nº 01", ORO, color_sub=(120, 112, 96))
    return grain(img)

# ---------------------------------------------------------------- 2. Wordmark Repeat
def d2():
    img = vgrad((W, H), (20, 27, 45), (14, 19, 32))
    draw = ImageDraw.Draw(img)
    rows = 13
    f = F(SANS_B, 118)
    y0 = H * 0.085
    dy = (H * 0.78) / rows
    for i in range(rows):
        y = y0 + i * dy
        x_off = -60 + (i % 3) * 40
        gold = i == 6
        if gold:
            text_tracked(draw, (W / 2 + x_off, y), "STREET ROYALTY", f, ORO_HI, tracking=2, anchor_center=True)
        elif i % 2 == 0:
            text_tracked(draw, (W / 2 + x_off, y), "STREET ROYALTY", f, (46, 57, 88), tracking=2, anchor_center=True)
        else:
            # outline only
            text_tracked(draw, (W / 2 + x_off, y), "STREET ROYALTY", f, (20, 27, 45), tracking=2,
                         anchor_center=True, stroke=2, stroke_fill=(88, 100, 138))
    footer(draw, "ROYAL INK · Nº 02", CREMA, color_sub=(110, 120, 150))
    return grain(img)

# ---------------------------------------------------------------- 3. Art-Deco Crest
def d3():
    img = vgrad((W, H), BURDEOS_HI, BURDEOS)
    draw = ImageDraw.Draw(img)
    cx, cy = W / 2, H * 0.47
    # deco rays
    for i in range(-9, 10):
        a = math.radians(90 + i * 8.6)
        x2 = cx + math.cos(a) * H * 0.62
        y2 = cy - abs(math.sin(a)) * H * 0.62
        draw.line([cx, cy, x2, y2], fill=(ORO if i % 2 == 0 else (150, 112, 52)), width=5 if i % 2 == 0 else 2)
    # concentric arcs
    for rr, wd in [(H * 0.30, 8), (H * 0.325, 3), (H * 0.36, 2)]:
        draw.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360, fill=ORO, width=wd)
    # crown filled
    pts, band = crown_path(cx, cy - H * 0.075, W * 0.30, H * 0.135)
    draw.polygon(pts, fill=ORO)
    draw.rectangle(band, fill=ORO)
    for px_, py_ in [(cx - W * 0.15, cy - H * 0.075 - H * 0.135 * 0.20),
                     (cx, cy - H * 0.075 - H * 0.135 * 0.44),
                     (cx + W * 0.15, cy - H * 0.075 - H * 0.135 * 0.20)]:
        r = 13
        draw.ellipse([px_ - r, py_ - r, px_ + r, py_ + r], fill=ORO_HI)
    # base platform lines
    for k, (ww, yy) in enumerate([(0.56, 0.560), (0.44, 0.582), (0.32, 0.604)]):
        draw.rectangle([cx - W * ww / 2, H * yy, cx + W * ww / 2, H * yy + 8], fill=ORO)
    # border frame double
    m = 70
    draw.rectangle([m, m, W - m, H - m], outline=ORO, width=4)
    draw.rectangle([m + 18, m + 18, W - m - 18, H - m - 18], outline=(150, 112, 52), width=2)
    # corners
    for cxx in (m + 18, W - m - 18):
        for cyy in (m + 18, H - m - 18):
            draw.ellipse([cxx - 7, cyy - 7, cxx + 7, cyy + 7], fill=ORO)
    f_big = F(SERIF_B, 128)
    draw.text((W / 2, H * 0.73), "ROYALTY", font=f_big, fill=CREMA, anchor="mm")
    text_tracked(draw, (W / 2, H * 0.785), "HERITAGE CREST · EST. MMXXVI", F(SANS, 33), ORO_HI, tracking=14, anchor_center=True)
    footer(draw, "ROYAL INK · Nº 03", ORO, y=H - 165, color_sub=(190, 150, 110))
    return grain(img)

# ---------------------------------------------------------------- 4. Circuito Urbano
def d4():
    img = Image.new("RGB", (W, H), CREMA)
    draw = ImageDraw.Draw(img)
    rnd = random.Random(42)
    # crown reserve mask (negative space)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    pts, band = crown_path(W / 2, H * 0.40, W * 0.52, H * 0.24)
    md.polygon(pts, fill=255)
    md.rectangle(band, fill=255)
    mask = mask.filter(ImageFilter.MaxFilter(9))
    mpx = mask.load()
    # manhattan pipes
    step = 40
    margin = 110
    for _ in range(260):
        x = rnd.randrange(margin, W - margin, step)
        y = rnd.randrange(int(H * 0.08), int(H * 0.66), step)
        pts_line = [(x, y)]
        dx, dy = rnd.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        for _s in range(rnd.randint(3, 9)):
            if rnd.random() < 0.55:
                dx, dy = (dy, dx) if rnd.random() < 0.5 else (-dy, -dx)
            nx = pts_line[-1][0] + dx * step * rnd.randint(1, 3)
            ny = pts_line[-1][1] + dy * step * rnd.randint(1, 3)
            nx = max(margin, min(W - margin, nx)); ny = max(int(H * 0.08), min(int(H * 0.66), ny))
            if mpx[int(nx), int(ny)] > 0: break
            pts_line.append((nx, ny))
        if len(pts_line) > 1 and all(mpx[int(px_), int(py_)] == 0 for px_, py_ in pts_line):
            col = NEGRO if rnd.random() > 0.12 else ORO
            draw.line(pts_line, fill=col, width=6, joint="curve")
            for e in (pts_line[0], pts_line[-1]):
                draw.ellipse([e[0] - 8, e[1] - 8, e[0] + 8, e[1] + 8],
                             fill=CREMA, outline=col, width=5)
    # crown outline inside negative space
    pts2, band2 = crown_path(W / 2, H * 0.40, W * 0.40, H * 0.185)
    draw.line(pts2 + [pts2[0]], fill=NEGRO, width=9, joint="curve")
    draw.rectangle(band2, outline=NEGRO, width=9)
    f_big = F(SANS_B, 122)
    draw.text((W / 2, H * 0.755), "CIRCUITO", font=f_big, fill=NEGRO, anchor="mm")
    text_tracked(draw, (W / 2, H * 0.81), "LA CALLE ES EL MAPA · SRHOOD", F(SANS, 33), (105, 96, 78), tracking=13, anchor_center=True)
    footer(draw, "ROYAL INK · Nº 04", NEGRO, color_sub=(150, 138, 114))
    return grain(img)

# ---------------------------------------------------------------- 5. Sello Lineart
def d5():
    img = Image.new("RGB", (W, H), (246, 240, 227))
    draw = ImageDraw.Draw(img)
    cx, cy = W / 2, H * 0.44
    R = W * 0.335
    for rr, wd in [(R, 6), (R * 0.87, 3)]:
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=NEGRO, width=wd)
    circular_text(img, (cx, cy), R * 0.935, "STREET ROYALTY HOOD  ·  EST. 2026  ·  MADRID  ·",
                  F(SANS_B, 44), NEGRO, start_deg=-90, clockwise=True)
    # crown lineart
    pts, band = crown_path(cx, cy + H * 0.004, W * 0.30, H * 0.14)
    draw.line(pts + [pts[0]], fill=NEGRO, width=8, joint="curve")
    draw.rectangle(band, outline=NEGRO, width=8)
    for px_, py_ in [(cx - W * 0.15, cy - H * 0.062 + H * 0.035),
                     (cx, cy - H * 0.062 - H * 0.0),
                     (cx + W * 0.15, cy - H * 0.062 + H * 0.035)]:
        draw.ellipse([px_ - 11, py_ - 11, px_ + 11, py_ + 11], outline=NEGRO, width=7)
    # burdeos wax accent
    wx, wy = W * 0.78, H * 0.685
    draw.ellipse([wx - 52, wy - 52, wx + 52, wy + 52], fill=BURDEOS)
    draw.ellipse([wx - 40, wy - 40, wx + 40, wy + 40], outline=(160, 96, 106), width=3)
    tmp_f = F(SERIF_B, 44)
    draw.text((wx, wy), "SR", font=tmp_f, fill=(226, 196, 186), anchor="mm")
    f_big = F(SERIF_B, 116)
    draw.text((W / 2, H * 0.77), "EL SELLO", font=f_big, fill=NEGRO, anchor="mm")
    text_tracked(draw, (W / 2, H * 0.825), "LINEART SEAL · TINTA SOBRE PAPEL", F(SANS, 32), (120, 110, 92), tracking=12, anchor_center=True)
    footer(draw, "ROYAL INK · Nº 05", NEGRO, color_sub=(150, 138, 114))
    return grain(img)

# ---------------------------------------------------------------- 6. Glitch Monogram
def d6():
    img = vgrad((W, H), (10, 10, 12), (18, 16, 14))
    # big monogram on its own layer for slicing
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    ld = ImageDraw.Draw(layer)
    f_mono = F(SANS_B, 620)
    ld.text((W / 2, H * 0.42), "SRH", font=f_mono, fill=CREMA, anchor="mm")
    rnd = random.Random(11)
    draw = ImageDraw.Draw(img)
    y = 0
    while y < H:
        sh = rnd.randint(14, 90)
        band = layer.crop((0, y, W, min(H, y + sh)))
        off = 0
        if rnd.random() < 0.38:
            off = rnd.randint(-70, 70)
        img.paste(band, (off, y), band.convert("L").point(lambda v: 255 if v > 12 else 0))
        y += sh
    # gold accent slices
    for _ in range(7):
        yy = rnd.randint(int(H * 0.18), int(H * 0.62))
        hh = rnd.randint(6, 16)
        xx = rnd.randint(0, int(W * 0.55))
        ww = rnd.randint(int(W * 0.2), int(W * 0.45))
        draw.rectangle([xx, yy, xx + ww, yy + hh], fill=ORO)
    # scanlines
    for yy in range(0, H, 6):
        draw.line([(0, yy), (W, yy)], fill=(0, 0, 0), width=1)
    text_tracked(draw, (W / 2, H * 0.72), "SEÑAL REAL · NO STATIC", F(SANS_B, 44), CREMA, tracking=16, anchor_center=True)
    text_tracked(draw, (W / 2, H * 0.76), "40.4168° N — 3.7038° W", F(MONO, 30), ORO_HI, tracking=6, anchor_center=True)
    footer(draw, "ROYAL INK · Nº 06", ORO, color_sub=(110, 104, 92))
    return grain(img)

# ---------------------------------------------------------------- wall mockup
def mockup(poster, wall=(226, 222, 214)):
    MW, MH = 1600, 2000
    img = vgrad((MW, MH), tuple(min(255, c + 12) for c in wall), tuple(max(0, c - 18) for c in wall))
    # poster area
    ph = int(MH * 0.72); pw = int(ph * W / H)
    px, py = (MW - pw) // 2, int(MH * 0.10)
    frame_pad = 26; matte = 46
    # shadow
    sh = Image.new("RGBA", (MW, MH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rectangle([px - frame_pad - matte + 14, py - frame_pad - matte + 26,
                  px + pw + frame_pad + matte + 30, py + ph + frame_pad + matte + 44], fill=(0, 0, 0, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    draw = ImageDraw.Draw(img)
    # frame, matte, art
    draw.rectangle([px - frame_pad - matte, py - frame_pad - matte,
                    px + pw + frame_pad + matte, py + ph + frame_pad + matte], fill=(24, 22, 20))
    draw.rectangle([px - matte, py - matte, px + pw + matte, py + ph + matte], fill=(248, 246, 240))
    img.paste(poster.resize((pw, ph), Image.LANCZOS), (px, py))
    # floor line hint
    draw.rectangle([0, int(MH * 0.94), MW, MH], fill=tuple(max(0, c - 34) for c in wall))
    return img

designs = {
    "royal-ink-01-corona-halftone": d1,
    "royal-ink-02-wordmark-navy": d2,
    "royal-ink-03-heritage-crest": d3,
    "royal-ink-04-circuito-urbano": d4,
    "royal-ink-05-sello-lineart": d5,
    "royal-ink-06-glitch-monogram": d6,
}
for name, fn in designs.items():
    art = fn()
    art.save(f"{OUT}/{name}.jpg", quality=92)
    mockup(art).save(f"{OUT}/{name}-wall.jpg", quality=90)
    print("done", name)
