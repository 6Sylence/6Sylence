#!/usr/bin/env python3
# Brand Covers — portadas de colección para Street Royalty Hood (run 2026-08-02)
# Genera las 4 imágenes de colección que faltaban: Home page, Verano Royal,
# Nómada Real y Bandanas, con la identidad de la casa (corona, oro, paleta neutra).
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "covers")
os.makedirs(OUT, exist_ok=True)

S = 1600  # square covers
NEGRO   = (12, 12, 14)
CREMA   = (242, 234, 217)
ARENA   = (216, 198, 160)
ORO     = (201, 164, 76)
ORO_HI  = (232, 202, 122)
BURDEOS = (74, 22, 32)
NAVY    = (23, 31, 51)
NAVY_HI = (36, 48, 78)
OLIVA   = (74, 78, 55)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def F(path, size): return ImageFont.truetype(path, size)

def grain(img):
    noise = Image.effect_noise(img.size, 10).convert("L")
    return Image.blend(img.convert("RGB"), Image.merge("RGB", (noise, noise, noise)), 0.045)

def vgrad(size, top, bottom):
    w, h = size
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((w, h))

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

def text_tracked(draw, xy, text, font, fill, tracking=0, anchor_center=False):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if anchor_center: x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking

def circular_text(img, center, radius, text, font, fill, start_deg=-90, clockwise=True):
    cx, cy = center
    tmp = ImageDraw.Draw(img)
    arcs = [max(tmp.textlength(c, font=font), font.size * 0.28) / radius for c in text]
    a = math.radians(start_deg) - (sum(arcs) / 2 if clockwise else -sum(arcs) / 2)
    for c, arc in zip(text, arcs):
        a_mid = a + (arc / 2 if clockwise else -arc / 2)
        x = cx + radius * math.cos(a_mid); y = cy + radius * math.sin(a_mid)
        size = int(font.size * 3)
        ch = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        cd = ImageDraw.Draw(ch)
        cd.text((size / 2, size / 2), c, font=font, fill=fill, anchor="mm")
        deg = math.degrees(a_mid) + (90 if clockwise else -90)
        ch = ch.rotate(-deg, resample=Image.BICUBIC, center=(size / 2, size / 2))
        img.paste(ch, (int(x - size / 2), int(y - size / 2)), ch)
        a += arc if clockwise else -arc

def gold_crown(draw, cx, cy, w, h):
    pts, band = crown_path(cx, cy, w, h)
    draw.polygon(pts, fill=ORO)
    draw.rectangle(band, fill=ORO)
    for px_, py_ in [(cx - w / 2 * 0.60, cy - h * 0.28), (cx, cy - h * 0.52),
                     (cx + w / 2 * 0.60, cy - h * 0.28)]:
        draw.ellipse([px_ - 12, py_ - 12, px_ + 12, py_ + 12], fill=ORO_HI)

# ------------------------------------------------------- 1. Home page — Crest
def cover_home():
    img = vgrad((S, S), (18, 18, 22), (8, 8, 10))
    draw = ImageDraw.Draw(img)
    cx, cy = S / 2, S * 0.40
    for i in range(-10, 11):
        a = math.radians(90 + i * 8.2)
        x2 = cx + math.cos(a) * S * 0.72
        y2 = cy - abs(math.sin(a)) * S * 0.72
        draw.line([cx, cy, x2, y2], fill=(ORO if i % 2 == 0 else (92, 76, 40)),
                  width=4 if i % 2 == 0 else 2)
    for rr, wd in [(S * 0.315, 7), (S * 0.345, 3)]:
        draw.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360, fill=ORO, width=wd)
    gold_crown(draw, cx, cy - S * 0.045, S * 0.34, S * 0.155)
    for ww, yy in [(0.52, 0.475), (0.40, 0.497), (0.28, 0.519)]:
        draw.rectangle([cx - S * ww / 2, S * yy, cx + S * ww / 2, S * yy + 7], fill=ORO)
    m = 56
    draw.rectangle([m, m, S - m, S - m], outline=ORO, width=4)
    draw.rectangle([m + 16, m + 16, S - m - 16, S - m - 16], outline=(120, 98, 52), width=2)
    for cxx in (m + 16, S - m - 16):
        for cyy in (m + 16, S - m - 16):
            draw.ellipse([cxx - 6, cyy - 6, cxx + 6, cyy + 6], fill=ORO)
    draw.text((S / 2, S * 0.655), "STREET ROYALTY", font=F(SERIF_B, 128), fill=CREMA, anchor="mm")
    draw.text((S / 2, S * 0.745), "HOOD", font=F(SERIF_B, 128), fill=CREMA, anchor="mm")
    text_tracked(draw, (S / 2, S * 0.828), "STAY ROYAL · EST. MMXXVI", F(SANS, 34), ORO_HI,
                 tracking=16, anchor_center=True)
    return grain(img)

# ------------------------------------------------- 2. Verano Royal — Baño & Playa
def cover_verano():
    img = vgrad((S, S), NAVY_HI, NAVY)
    draw = ImageDraw.Draw(img)
    cx, hy = S / 2, S * 0.52  # horizon
    # deco sun on the horizon
    R = S * 0.21
    for i in range(-8, 9):
        a = math.radians(90 + i * 10.5)
        x2 = cx + math.cos(a) * S * 0.46
        y2 = hy - abs(math.sin(a)) * S * 0.46
        draw.line([cx, hy, x2, y2], fill=(ORO if i % 2 == 0 else (110, 92, 48)),
                  width=5 if i % 2 == 0 else 2)
    draw.pieslice([cx - R, hy - R, cx + R, hy + R], 180, 360, fill=ORO)
    draw.pieslice([cx - R * 0.80, hy - R * 0.80, cx + R * 0.80, hy + R * 0.80], 180, 360, fill=ORO_HI)
    gold_crown(draw, cx, hy - R - S * 0.085, S * 0.155, S * 0.075)
    draw.rectangle([S * 0.10, hy, S * 0.90, hy + 6], fill=ORO)
    # crema waves below the horizon
    for row in range(4):
        y = hy + S * 0.055 + row * S * 0.052
        w_amp = 16 - row * 1.5
        col = CREMA if row % 2 == 0 else ARENA
        pts = []
        for x in range(int(S * 0.10), int(S * 0.90), 8):
            pts.append((x, y + math.sin((x / S) * math.pi * 10 + row) * w_amp))
        draw.line(pts, fill=col, width=5, joint="curve")
    draw.text((S / 2, S * 0.585), " ", font=F(SANS, 10), fill=NAVY)  # spacer noop
    draw.text((S / 2, S * 0.80), "VERANO ROYAL", font=F(SERIF_B, 118), fill=CREMA, anchor="mm")
    text_tracked(draw, (S / 2, S * 0.868), "BAÑO & PLAYA · SRHOOD", F(SANS, 34), ORO_HI,
                 tracking=15, anchor_center=True)
    return grain(img)

# --------------------------------------------- 3. Nómada Real — Patrones del Mundo
def cover_nomada():
    img = Image.new("RGB", (S, S), NEGRO)
    draw = ImageDraw.Draw(img)
    rnd = random.Random(7)
    band_h = S / 6
    # band 1: fleur-de-lis dots on navy
    draw.rectangle([0, 0, S, band_h], fill=NAVY)
    for gx in range(0, S, 130):
        for k, gy in enumerate(range(20, int(band_h) - 10, 90)):
            x = gx + (65 if k % 2 else 0)
            draw.polygon([(x, gy), (x - 16, gy + 30), (x, gy + 22), (x + 16, gy + 30)], fill=ORO)
    # band 2: ikat zigzag on burdeos
    y0 = band_h
    draw.rectangle([0, y0, S, y0 + band_h], fill=BURDEOS)
    for row in range(3):
        yy = y0 + 40 + row * 80
        pts = [(x, yy + (34 if (x // 70) % 2 else -34) + rnd.randint(-6, 6))
               for x in range(-20, S + 40, 70)]
        draw.line(pts, fill=CREMA if row % 2 == 0 else ARENA, width=9, joint="curve")
    # band 3: bogolán marks on arena
    y0 = band_h * 2
    draw.rectangle([0, y0, S, y0 + band_h], fill=ARENA)
    for gx in range(30, S, 90):
        for gy in range(int(y0) + 30, int(y0 + band_h) - 20, 70):
            m = rnd.random()
            if m < 0.4:
                draw.line([gx - 20, gy + 20, gx, gy, gx + 20, gy + 20], fill=NEGRO, width=7)
            elif m < 0.7:
                draw.ellipse([gx - 9, gy - 9, gx + 9, gy + 9], outline=NEGRO, width=6)
            else:
                draw.line([gx - 18, gy, gx + 18, gy], fill=NEGRO, width=7)
    # band 4: honeycomb on negro
    y0 = band_h * 3
    draw.rectangle([0, y0, S, y0 + band_h], fill=(18, 18, 20))
    r_hex = 46
    for col in range(-1, int(S / (r_hex * 1.55)) + 2):
        for row in range(4):
            hx = col * r_hex * 1.55
            hy2 = y0 + 30 + row * r_hex * 1.35 + (r_hex * 0.675 if col % 2 else 0)
            if hy2 > y0 + band_h - 10: continue
            hexpts = [(hx + r_hex * 0.9 * math.cos(math.radians(60 * i - 30)),
                       hy2 + r_hex * 0.9 * math.sin(math.radians(60 * i - 30))) for i in range(6)]
            draw.polygon(hexpts, outline=ORO, width=4)
    # band 5: pantera spots on oliva
    y0 = band_h * 4
    draw.rectangle([0, y0, S, y0 + band_h], fill=OLIVA)
    for _ in range(90):
        x = rnd.randint(10, S - 10); y = rnd.randint(int(y0) + 14, int(y0 + band_h) - 14)
        r = rnd.randint(10, 22)
        draw.arc([x - r, y - r, x + r, y + r], rnd.randint(0, 180), rnd.randint(200, 360),
                 fill=NEGRO, width=8)
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(30, 30, 24))
    # band 6: camo blobs
    y0 = band_h * 5
    draw.rectangle([0, y0, S, y0 + band_h], fill=(34, 38, 30))
    for col_c in [(52, 58, 44), (24, 26, 22), (110, 100, 70), ORO]:
        for _ in range(9 if col_c != ORO else 4):
            x = rnd.randint(0, S); y = rnd.randint(int(y0) + 10, S - 10)
            blob = [(x + rnd.randint(-90, 90), y + rnd.randint(-34, 34)) for _ in range(7)]
            draw.polygon(blob, fill=col_c)
    # gold rules between bands
    for i in range(1, 6):
        draw.rectangle([0, band_h * i - 3, S, band_h * i + 3], fill=ORO)
    # central medallion
    cx, cy, R = S / 2, S / 2, S * 0.235
    draw.ellipse([cx - R - 14, cy - R - 14, cx + R + 14, cy + R + 14], fill=ORO)
    draw.ellipse([cx - R, cy - R, cx + R, cy + R], fill=CREMA)
    draw.ellipse([cx - R * 0.86, cy - R * 0.86, cx + R * 0.86, cy + R * 0.86], outline=NEGRO, width=5)
    circular_text(img, (cx, cy), R * 0.93, "NÓMADA REAL · PATRONES DEL MUNDO · SRHOOD ·",
                  F(SANS_B, 40), NEGRO, start_deg=-90)
    draw = ImageDraw.Draw(img)
    pts, band = crown_path(cx, cy + S * 0.012, S * 0.185, S * 0.088)
    draw.line(pts + [pts[0]], fill=NEGRO, width=8, joint="curve")
    draw.rectangle(band, outline=NEGRO, width=8)
    return grain(img)

# --------------------------------------------------------------- 4. Bandanas
def cover_bandanas():
    img = Image.new("RGB", (S, S), BURDEOS)
    draw = ImageDraw.Draw(img)
    line = CREMA
    # frames
    for m, wd in [(56, 5), (86, 2), (120, 3)]:
        draw.rectangle([m, m, S - m, S - m], outline=line, width=wd)
    # dotted border between frames
    for x in range(140, S - 130, 34):
        for y in (103, S - 103):
            draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=ORO)
        for yv in range(140, S - 130, 34):
            for xv in (103, S - 103):
                draw.ellipse([xv - 5, yv - 5, xv + 5, yv + 5], fill=ORO)
    def boteh(cx, cy, scale, rot):
        """paisley teardrop, line art"""
        b = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
        bd = ImageDraw.Draw(b)
        bd.arc([60, 60, 340, 340], 100, 405, fill=line, width=10)
        bd.arc([120, 120, 280, 280], 100, 380, fill=line, width=7)
        bd.ellipse([185, 185, 215, 215], fill=ORO)
        for a_deg in range(110, 400, 36):
            a = math.radians(a_deg)
            x1 = 200 + 140 * math.cos(a); y1 = 200 + 140 * math.sin(a)
            x2 = 200 + 168 * math.cos(a); y2 = 200 + 168 * math.sin(a)
            bd.line([x1, y1, x2, y2], fill=ORO, width=6)
        b = b.rotate(rot, resample=Image.BICUBIC)
        b = b.resize((int(400 * scale), int(400 * scale)), Image.LANCZOS)
        img.paste(b, (int(cx - b.width / 2), int(cy - b.height / 2)), b)
    for cx, cy, rot in [(255, 255, 15), (S - 255, 255, 75), (255, S - 255, -75), (S - 255, S - 255, -165)]:
        boteh(cx, cy, 0.72, rot)
    # center medallion
    cx = cy = S / 2
    R = S * 0.205
    for rr, wd in [(R, 6), (R * 0.87, 3)]:
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=line, width=wd)
    circular_text(img, (cx, cy), R * 0.94, "BANDANAS · EL PAÑUELO DE LA CASA ·",
                  F(SANS_B, 36), CREMA, start_deg=-90)
    draw = ImageDraw.Draw(img)
    pts, band = crown_path(cx, cy + S * 0.010, S * 0.165, S * 0.080)
    draw.line(pts + [pts[0]], fill=line, width=8, joint="curve")
    draw.rectangle(band, outline=line, width=8)
    for a_deg in range(0, 360, 30):
        a = math.radians(a_deg)
        x = cx + R * 1.16 * math.cos(a); y = cy + R * 1.16 * math.sin(a)
        draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=ORO)
    text_tracked(draw, (S / 2, S * 0.885), "STREET ROYALTY HOOD · MMXXVI", F(SANS, 30), ORO_HI,
                 tracking=12, anchor_center=True)
    return grain(img)

covers = {
    "brand-cover-home": cover_home,
    "brand-cover-verano-royal": cover_verano,
    "brand-cover-nomada-real": cover_nomada,
    "brand-cover-bandanas": cover_bandanas,
}
if __name__ == "__main__":
    for name, fn in covers.items():
        fn().save(f"{OUT}/{name}.jpg", quality=92)
        print("done", name)
