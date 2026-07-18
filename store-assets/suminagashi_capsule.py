# -*- coding: utf-8 -*-
"""
Cápsula Suminagashi — Tinta al Agua  +  cierre Cápsula Cianotipo (calzado).
Genera patrones originales y mockups flat-lay 1600x1600 para SRHOOD.

Suminagashi: algoritmo clásico de marmolado por gotas (inverse mapping):
cada gota (c, r) desplaza el plano; render iterando gotas en orden inverso.
Anillos finos de tinta (paso pequeño) sobre anchos de papel (paso grande),
después "tines" suaves (soplado) como warps de línea.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

PAPER = (243, 240, 232)   # papel arroz
INK = (24, 24, 27)        # tinta sumi
SEAL = (178, 44, 38)      # sello bermellón
PRUSSIA = (18, 42, 84)    # azul de Prusia (cápsula cianotipo)
CHALK = (238, 243, 246)   # blanco tiza
BG = (238, 236, 231)      # fondo estudio flat-lay

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# ---------------------------------------------------------------- suminagashi
def suminagashi(w, h, seed, n_centers=6, rings=(18, 26), tines=3, ss=2):
    W, H = w * ss, h * ss
    rng = random.Random(seed)
    drops = []
    for _ in range(n_centers):
        cx = rng.uniform(0.12, 0.88) * W
        cy = rng.uniform(0.12, 0.88) * H
        r = rng.uniform(0.008, 0.016) * W
        n = rng.randint(*rings)
        for k in range(n):
            jx = cx + rng.uniform(-8, 8) * ss
            jy = cy + rng.uniform(-8, 8) * ss
            drops.append((jx, jy, r, k % 2 == 0))
            # tinta: anillo fino / agua: banda ancha
            r *= rng.uniform(1.020, 1.045) if k % 2 == 0 else rng.uniform(1.10, 1.20)

    ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
    px, py = xs, ys

    for _ in range(tines):
        ang = rng.uniform(0, math.pi)
        ux, uy = math.cos(ang), math.sin(ang)
        nx, ny = -uy, ux
        ax = rng.uniform(0, W)
        ay = rng.uniform(0, H)
        z = rng.uniform(0.02, 0.06) * W
        c = rng.uniform(0.15, 0.30) * W
        d = (px - ax) * nx + (py - ay) * ny
        f = z * np.exp(-np.abs(d) / c)
        px = px - ux * f
        py = py - uy * f

    color = np.zeros((H, W), dtype=np.int8)
    claimed = np.zeros((H, W), dtype=bool)
    for (cx, cy, r, is_ink) in reversed(drops):
        dx = px - cx
        dy = py - cy
        d2 = dx * dx + dy * dy
        inside = (~claimed) & (d2 <= r * r)
        if is_ink:
            color[inside] = 1
        claimed |= inside
        d = np.sqrt(np.maximum(d2, 1e-9))
        scale = np.sqrt(np.maximum(d2 - r * r, 0.0)) / d
        upd = ~claimed
        px = np.where(upd, cx + dx * scale, px)
        py = np.where(upd, cy + dy * scale, py)

    img = np.empty((H, W, 3), dtype=np.uint8)
    img[color == 0] = PAPER
    img[color == 1] = INK
    out = Image.fromarray(img).resize((w, h), Image.LANCZOS)
    noise = np.random.default_rng(seed).normal(0, 4, (h, w, 1)).repeat(3, 2)
    arr = np.clip(np.asarray(out).astype(np.int16) + noise.astype(np.int16), 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def seal_stamp(size=92):
    s = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.rounded_rectangle([2, 2, size - 3, size - 3], radius=size // 9,
                        fill=SEAL + (235,))
    w = size
    cw = (245, 240, 232)
    # corona
    d.polygon([(w * .20, w * .58), (w * .17, w * .30), (w * .34, w * .46),
               (w * .50, w * .22), (w * .66, w * .46), (w * .83, w * .30),
               (w * .80, w * .58)], fill=cw)
    d.rectangle([w * .20, w * .62, w * .80, w * .72], fill=cw)
    f = ImageFont.truetype(FONT_B, int(size * 0.20))
    d.text((w / 2, w * .85), "SR", font=f, fill=cw, anchor="mm")
    return s


# ------------------------------------------------------------------ cianotipo
def fern(draw, x0, y0, length, angle, color, width=4, depth=0):
    steps = 26
    pts = []
    a = angle
    x, y = x0, y0
    for i in range(steps):
        t = i / steps
        a += math.sin(t * 3.1) * 0.035 + 0.012
        seg = length / steps
        x += seg * math.cos(a)
        y -= seg * math.sin(a)
        pts.append((x, y, a, t))
    for i in range(1, len(pts)):
        draw.line([pts[i - 1][:2], pts[i][:2]], fill=color, width=width)
    for (x, y, a, t) in pts[2:]:
        plen = length * 0.16 * (1 - t) ** 1.1 + 3
        for side in (1, -1):
            pa = a + side * 1.15
            ex = x + plen * math.cos(pa)
            ey = y - plen * math.sin(pa)
            draw.line([(x, y), (ex, ey)], fill=color, width=max(2, width - 2))
            if depth == 0 and plen > 14:
                n = int(plen / 7)
                for j in range(1, n):
                    tt = j / n
                    bx = x + plen * tt * math.cos(pa)
                    by = y - plen * tt * math.sin(pa)
                    bl = plen * 0.30 * (1 - tt)
                    for s2 in (1, -1):
                        ba = pa + s2 * 1.0
                        draw.line(
                            [(bx, by), (bx + bl * math.cos(ba), by - bl * math.sin(ba))],
                            fill=color, width=2)


def eucalyptus(draw, x0, y0, length, angle, color):
    steps = 22
    x, y = x0, y0
    a = angle
    prev = (x, y)
    for i in range(steps):
        t = i / steps
        a += 0.02 * math.cos(t * 5)
        x += (length / steps) * math.cos(a)
        y -= (length / steps) * math.sin(a)
        draw.line([prev, (x, y)], fill=color, width=4)
        prev = (x, y)
        if i % 2 == 0 and i > 1:
            r = 16 * (1 - t * 0.55) + 4
            for side in (1, -1):
                la = a + side * 1.25
                cx = x + (r + 6) * math.cos(la)
                cy = y - (r + 6) * math.sin(la)
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def cyanotype_panel(w, h, seed, motif="fern"):
    rng = random.Random(seed)
    img = Image.new("RGB", (w, h), PRUSSIA)
    d = ImageDraw.Draw(img)
    col = CHALK
    if motif == "fern":
        for _ in range(4):
            fern(d, rng.uniform(0.1, 0.6) * w, rng.uniform(0.85, 1.0) * h,
                 rng.uniform(0.55, 0.8) * h, math.pi / 2 + rng.uniform(-0.5, 0.5),
                 col, width=4)
    else:
        for _ in range(4):
            eucalyptus(d, rng.uniform(0.1, 0.7) * w, rng.uniform(0.85, 1.0) * h,
                       rng.uniform(0.5, 0.75) * h, math.pi / 2 + rng.uniform(-0.6, 0.6),
                       col)
    img = img.filter(ImageFilter.GaussianBlur(1.0))
    noise = np.random.default_rng(seed).normal(0, 6, (h, w, 1)).repeat(3, 2)
    arr = np.clip(np.asarray(img).astype(np.int16) + noise.astype(np.int16), 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


# ------------------------------------------------------------------- mockups
S = 1600


def canvas():
    im = Image.new("RGB", (S, S), BG)
    d = ImageDraw.Draw(im)
    for i in range(S):
        t = i / S
        v = int(238 - 10 * t)
        d.line([(0, i), (S, i)], fill=(v, v - 1, v - 4))
    return im


def drop_shadow(base, mask, dy=26, blur=28, opacity=70):
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    black = Image.new("RGBA", base.size, (20, 20, 20, opacity))
    sh.paste(black, (0, dy), mask)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(sh)


def fabric_texture(img, seed=1, strength=6):
    h, w = img.size[1], img.size[0]
    rng = np.random.default_rng(seed)
    n = rng.normal(0, strength, (h, w, 1)).repeat(3, 2)
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))


def sym(points):
    right = [(2 * 800 - x, y) for (x, y) in reversed(points[:-1])]
    return points + right


def tee_mask(long_sleeve=False):
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    if not long_sleeve:
        body = sym([(800, 285), (640, 300), (555, 330), (300, 430), (365, 640),
                    (520, 585), (520, 1270), (545, 1300), (800, 1310)])
    else:
        body = sym([(800, 285), (640, 300), (555, 330), (390, 400), (300, 480),
                    (250, 900), (245, 1120), (330, 1140), (395, 1130), (430, 660),
                    (520, 620), (520, 1270), (545, 1300), (800, 1310)])
    d.polygon(body, fill=255)
    return m


def draw_tee(pattern, garment_rgb, path, long_sleeve=False, seed=7):
    base = canvas().convert("RGBA")
    mask = tee_mask(long_sleeve)
    drop_shadow(base, mask)
    garment = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fill = fabric_texture(Image.new("RGB", (S, S), garment_rgb), seed=seed, strength=5)
    garment.paste(fill, (0, 0), mask)
    d = ImageDraw.Draw(garment)
    dk = _dark(garment_rgb, 40)
    d.arc([700, 255, 900, 355], 15, 165, fill=dk, width=14)
    d.line([(560, 332), (703, 302)], fill=_dark(garment_rgb, 25), width=3)
    d.line([(1040, 332), (897, 302)], fill=_dark(garment_rgb, 25), width=3)
    base.alpha_composite(garment)
    pw, ph = 480, 600
    px0, py0 = 800 - pw // 2, 480
    panel = pattern.resize((pw, ph)).convert("RGBA")
    panel.alpha_composite(seal_stamp(72), (pw - 92, ph - 92))
    base.alpha_composite(panel, (px0, py0))
    dd = ImageDraw.Draw(base)
    dd.rectangle([px0, py0, px0 + pw, py0 + ph], outline=(0, 0, 0, 30), width=2)
    f = ImageFont.truetype(FONT_B, 30)
    tcol = (235, 232, 226) if sum(garment_rgb) < 300 else (40, 40, 42)
    dd.text((800, py0 + ph + 46), "S R H O O D", font=f, fill=tcol, anchor="mm")
    base.convert("RGB").save(path, quality=92)


def hoodie_mask():
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    body = sym([(800, 330), (655, 340), (560, 370), (395, 440), (290, 530),
                (240, 930), (235, 1140), (330, 1165), (400, 1150), (435, 700),
                (515, 660), (515, 1280), (545, 1310), (800, 1320)])
    d.polygon(body, fill=255)
    # capucha: forma redondeada detrás del cuello
    d.rounded_rectangle([600, 210, 1000, 420], radius=110, fill=255)
    return m


def draw_hoodie(pattern, garment_rgb, path, seed=9):
    base = canvas().convert("RGBA")
    mask = hoodie_mask()
    drop_shadow(base, mask)
    garment = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fill = fabric_texture(Image.new("RGB", (S, S), garment_rgb), seed=seed, strength=5)
    garment.paste(fill, (0, 0), mask)
    d = ImageDraw.Draw(garment)
    dk = _dark(garment_rgb, 45)
    lt = _light(garment_rgb, 22)
    # apertura de capucha
    d.arc([650, 240, 950, 460], 190, 350, fill=lt, width=10)
    d.arc([700, 340, 900, 460], 10, 170, fill=lt, width=12)
    # cordones
    d.line([(762, 452), (754, 560)], fill=lt, width=8)
    d.line([(838, 452), (846, 560)], fill=lt, width=8)
    d.ellipse([746, 554, 762, 570], fill=lt)
    d.ellipse([838, 554, 854, 570], fill=lt)
    # bolsillo canguro
    d.polygon([(660, 1010), (940, 1010), (980, 1250), (620, 1250)],
              outline=lt, width=6)
    # puños y bajo
    d.line([(238, 1128), (398, 1138)], fill=lt, width=6)
    d.line([(1202, 1138), (1362, 1128)], fill=lt, width=6)
    d.line([(520, 1288), (1080, 1288)], fill=lt, width=6)
    base.alpha_composite(garment)
    pw, ph = 430, 400
    px0, py0 = 800 - pw // 2, 560
    panel = pattern.resize((pw, ph)).convert("RGBA")
    panel.alpha_composite(seal_stamp(64), (pw - 82, ph - 82))
    base.alpha_composite(panel, (px0, py0))
    dd = ImageDraw.Draw(base)
    dd.rectangle([px0, py0, px0 + pw, py0 + ph], outline=(0, 0, 0, 30), width=2)
    base.convert("RGB").save(path, quality=92)


def draw_hitop(pattern, path, sole_rgb=(250, 250, 248)):
    base = canvas().convert("RGBA")
    upper = [(230, 1050), (255, 760), (420, 700), (560, 430), (830, 410),
             (900, 560), (1050, 700), (1290, 820), (1360, 900), (1370, 1050)]
    mask = Image.new("L", (S, S), 0)
    dm = ImageDraw.Draw(mask)
    dm.polygon(upper, fill=255)
    full = mask.copy()
    dm2 = ImageDraw.Draw(full)
    dm2.rounded_rectangle([210, 1040, 1390, 1170], radius=60, fill=255)
    drop_shadow(base, full, dy=30)
    shoe = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shoe.paste(pattern.resize((S, S)), (0, 0), mask)
    d = ImageDraw.Draw(shoe)
    white = (250, 250, 248)
    edge = (198, 196, 190)
    grey = (120, 118, 114)
    # lengüeta + panel de cordones
    d.polygon([(600, 470), (830, 452), (872, 980), (585, 1000)], fill=white,
              outline=edge, width=3)
    lx0, ly0 = 655, 520   # columna izq. (sobre el panel)
    rx0, ry0 = 815, 508
    steps = 6
    for i in range(steps):
        t = i / (steps - 1)
        xl = lx0 - 42 * t
        yl = ly0 + 440 * t
        xr = rx0 + 42 * t
        yr = ry0 + 440 * t
        if i < steps - 1:
            t2 = (i + 1) / (steps - 1)
            xl2 = lx0 - 42 * t2
            yl2 = ly0 + 440 * t2
            xr2 = rx0 + 42 * t2
            yr2 = ry0 + 440 * t2
            d.line([(xl, yl), (xr2, yr2)], fill=(235, 233, 228), width=15)
            d.line([(xr, yr), (xl2, yl2)], fill=(235, 233, 228), width=15)
        d.ellipse([xl - 11, yl - 11, xl + 11, yl + 11], fill=grey)
        d.ellipse([xr - 11, yr - 11, xr + 11, yr + 11], fill=grey)
    # suela y puntera
    d.rounded_rectangle([210, 1040, 1390, 1170], radius=60, fill=sole_rgb,
                        outline=edge, width=4)
    d.line([(230, 1105), (1370, 1105)], fill=(205, 203, 197), width=5)
    d.pieslice([1090, 880, 1430, 1120], 235, 360, fill=sole_rgb,
               outline=edge, width=4)
    # parche tobillo
    d.ellipse([300, 800, 420, 920], fill=(245, 243, 238), outline=(180, 178, 172),
              width=4)
    st = seal_stamp(74)
    shoe.alpha_composite(st, (323, 823))
    base.alpha_composite(shoe)
    base.convert("RGB").save(path, quality=92)


def draw_slipon(pattern, path, sole_rgb=(250, 250, 248)):
    base = canvas().convert("RGBA")
    upper = [(250, 1050), (285, 830), (430, 770), (620, 745), (880, 700),
             (1010, 720), (1160, 800), (1300, 890), (1355, 960), (1365, 1050)]
    mask = Image.new("L", (S, S), 0)
    dm = ImageDraw.Draw(mask)
    dm.polygon(upper, fill=255)
    full = mask.copy()
    dm2 = ImageDraw.Draw(full)
    dm2.rounded_rectangle([230, 1040, 1385, 1165], radius=55, fill=255)
    drop_shadow(base, full, dy=28)
    shoe = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shoe.paste(pattern.resize((S, S)), (0, 0), mask)
    d = ImageDraw.Draw(shoe)
    edge = (198, 196, 190)
    d.rounded_rectangle([230, 1040, 1385, 1165], radius=55, fill=sole_rgb,
                        outline=edge, width=4)
    d.pieslice([1100, 890, 1420, 1120], 240, 360, fill=sole_rgb,
               outline=edge, width=4)
    # elástico lateral
    d.polygon([(600, 760), (760, 730), (770, 850), (620, 880)], fill=(70, 70, 74))
    for i in range(5):
        d.line([(615 + i * 30, 755), (628 + i * 30, 866)], fill=(110, 110, 115),
               width=4)
    d.line([(430, 775), (620, 748), (880, 705), (1010, 725)],
           fill=(60, 60, 64), width=10, joint="curve")
    st = seal_stamp(70)
    shoe.alpha_composite(st, (315, 905))
    base.alpha_composite(shoe)
    base.convert("RGB").save(path, quality=92)


def draw_cap(pattern, visor_rgb, path):
    base = canvas().convert("RGBA")
    dome = [420, 440, 1180, 1200]
    mask = Image.new("L", (S, S), 0)
    dm = ImageDraw.Draw(mask)
    dm.pieslice(dome, 180, 360, fill=255)
    dm.rectangle([420, 815, 1180, 870], fill=255)
    full = mask.copy()
    dm2 = ImageDraw.Draw(full)
    dm2.ellipse([330, 830, 1270, 1060], fill=255)
    drop_shadow(base, full, dy=24)
    cap = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cap.paste(pattern.resize((S, S)), (0, 0), mask)
    d = ImageDraw.Draw(cap)
    sew = (0, 0, 0, 60)
    # costuras de paneles
    d.arc(dome, 180, 360, fill=(0, 0, 0, 90), width=5)
    d.line([(800, 445), (800, 830)], fill=sew, width=4)
    d.arc([560, 430, 1040, 1100], 205, 335, fill=sew, width=4)
    d.arc([260, 430, 1340, 1240], 235, 305, fill=sew, width=4)
    # botón
    d.ellipse([778, 424, 822, 468], fill=_dark(visor_rgb, 0))
    # visera curvada
    visor = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dv = ImageDraw.Draw(visor)
    dv.ellipse([330, 830, 1270, 1060], fill=visor_rgb)
    dv.arc([330, 830, 1270, 1060], 0, 180, fill=(0, 0, 0, 90), width=6)
    dv.arc([330, 760, 1270, 990], 25, 155, fill=(255, 255, 255, 40), width=5)
    cap.alpha_composite(visor)
    st = seal_stamp(70)
    cap.alpha_composite(st, (1010, 700))
    base.alpha_composite(cap)
    base.convert("RGB").save(path, quality=92)


def _dark(rgb, amt):
    return tuple(max(0, c - amt) for c in rgb)


def _light(rgb, amt):
    return tuple(min(255, c + amt) for c in rgb)


if __name__ == "__main__":
    random.seed(20260718)
    print("generando patrones suminagashi…")
    pat_tee = suminagashi(1000, 1250, seed=11)
    pat_ls = suminagashi(1000, 1250, seed=23, n_centers=5)
    pat_hood = suminagashi(1080, 1000, seed=37, n_centers=6)
    pat_shoe_h = suminagashi(1600, 1600, seed=52, n_centers=8, rings=(14, 22))
    pat_shoe_m = suminagashi(1600, 1600, seed=67, n_centers=7, rings=(16, 24))
    pat_cap = suminagashi(1600, 1600, seed=83, n_centers=8, rings=(12, 20))

    print("mockups suminagashi…")
    draw_tee(pat_tee, (250, 250, 248), f"{OUT}/sum-tee.jpg")
    draw_tee(pat_ls, (235, 229, 214), f"{OUT}/sum-longsleeve.jpg", long_sleeve=True)
    draw_hoodie(pat_hood, (32, 32, 36), f"{OUT}/sum-hoodie.jpg")
    draw_hitop(pat_shoe_h, f"{OUT}/sum-hitop.jpg")
    draw_slipon(pat_shoe_m, f"{OUT}/sum-slipon.jpg")
    draw_cap(pat_cap, (28, 28, 32), f"{OUT}/sum-cap.jpg")

    print("cianotipo calzado…")
    cy_hi = cyanotype_panel(1600, 1600, seed=91, motif="fern")
    cy_slip = cyanotype_panel(1600, 1600, seed=97, motif="eucalyptus")
    draw_hitop(cy_hi, f"{OUT}/cia-hitop.jpg")
    draw_slipon(cy_slip, f"{OUT}/cia-slipon.jpg")

    suminagashi(1600, 900, seed=101, n_centers=7, rings=(14, 22)).save(
        f"{OUT}/sum-collection.jpg", quality=92)
    print("ok:", sorted(os.listdir(OUT)))
