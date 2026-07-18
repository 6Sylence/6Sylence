#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cápsula Celeste — Corona Boreal (SRHOOD)
Genera los archivos de impresión (Printful) de la cápsula: carta estelar de la
constelación Corona Borealis (la "Corona del Norte") en oro y marfil sobre
medianoche. Cartografía celeste real: posiciones J2000 y magnitudes de las
siete estrellas del arco (θ–β–α–γ–δ–ε–ι), retícula de ascensión recta y
declinación, anillo de graduación y rotulación latina.

Salidas (dimensiones exactas de printfile Printful):
  tee_front.png      1800×2400  DTG pecho    (Bella+Canvas 3001, negro)
  ls_front.png       1800×2400  DTG pecho    (Bella+Canvas 3501, navy)
  hoodie_front.png   1800×1800  DTG pecho    (Cotton Heritage M2580, navy blazer)
  zip_back.png       1800×2400  DTG espalda  (Gildan 18600, negro)
  shoe_quarters.png  2250×2250  AOP          (Women's High Top Canvas 525)
  shoe_athletic.png  1950×3300  AOP          (Men's Athletic Shoes 657)
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "designs"
FONTS = sys.argv[2] if len(sys.argv) > 2 else "fonts"
os.makedirs(OUT, exist_ok=True)

SS = 2  # supersampling

# Paleta
GOLD = (201, 164, 92, 255)        # oro viejo
GOLD_HI = (233, 207, 159, 255)    # oro claro
GOLD_DIM = (201, 164, 92, 110)    # oro tenue (retícula)
IVORY = (244, 239, 228, 255)      # estrellas
NIGHT_C = (16, 23, 52)            # fondo centro (calzado)
NIGHT_E = (7, 10, 27)             # fondo borde (calzado)

# Corona Borealis — J2000: (nombre, letra griega, RA°, Dec°, magnitud)
CRB = [
    ("theta",   "θ", 233.232, 31.359, 4.14),
    ("beta",    "β", 231.957, 29.106, 3.68),
    ("alpha",   "α", 233.672, 26.715, 2.23),   # Alphecca
    ("gamma",   "γ", 235.686, 26.296, 3.84),
    ("delta",   "δ", 237.398, 26.068, 4.63),
    ("epsilon", "ε", 239.395, 26.878, 4.15),
    ("iota",    "ι", 240.361, 29.851, 4.99),
]
RA0, DEC0 = 236.1, 28.4  # centro de proyección


def F(name, size, weight=None):
    path = os.path.join(FONTS, name)
    f = ImageFont.truetype(path, size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def fonts(ss):
    return {
        "title":  lambda s: F("Cinzel[wght].ttf", s * ss, 560),
        "small":  lambda s: F("Cinzel[wght].ttf", s * ss, 450),
        "text":   lambda s: F("CormorantGaramond[wght].ttf", s * ss, 500),
        "greek":  lambda s: ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", s * ss),
    }


def project(ra, dec, scale):
    """Proyección plana centrada en (RA0, DEC0). RA crece hacia la izquierda."""
    x = (RA0 - ra) * math.cos(math.radians(dec)) * scale
    y = (DEC0 - dec) * scale
    return x, y


def star_glow(layer, x, y, r, color, spikes=0.0):
    """Estrella con halo suave y, opcionalmente, puntas de difracción."""
    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([x - r * 3, y - r * 3, x + r * 3, y + r * 3],
              fill=color[:3] + (60,))
    glow = glow.filter(ImageFilter.GaussianBlur(r * 1.2))
    layer.alpha_composite(glow)
    d = ImageDraw.Draw(layer)
    if spikes:
        L = r * spikes
        for ang in (0, 90):
            a = math.radians(ang)
            dx, dy = math.cos(a) * L, math.sin(a) * L
            d.line([x - dx, y - dy, x + dx, y + dy],
                   fill=color[:3] + (150,), width=max(2, int(r * 0.22)))
    d.ellipse([x - r, y - r, x + r, y + r], fill=color)
    d.ellipse([x - r * 0.45, y - r * 0.45, x + r * 0.45, y + r * 0.45],
              fill=(255, 255, 250, 255))


def dashed_line(d, p1, p2, dash, gap, fill, width):
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0:
        return
    ux, uy = (x2 - x1) / dist, (y2 - y1) / dist
    t = 0.0
    while t < dist:
        t2 = min(t + dash, dist)
        d.line([x1 + ux * t, y1 + uy * t, x1 + ux * t2, y1 + uy * t2],
               fill=fill, width=width)
        t = t2 + gap


def dashed_circle(d, cx, cy, r, n, fill, width, arc_len=3.2):
    for i in range(n):
        a0 = 360.0 * i / n
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + arc_len,
              fill=fill, width=width)


def arc_text(img, cx, cy, r, text, font, fill, a_start, a_end, outward=True):
    """Texto sobre un arco: cada glifo rotado tangencialmente."""
    if not text:
        return
    widths = [font.getbbox(ch)[2] - font.getbbox(ch)[0] if ch != " "
              else font.size * 0.35 for ch in text]
    total_w = sum(widths)
    span = math.radians(a_end - a_start)
    # ángulo proporcional al ancho de cada glifo; para texto interior (parte
    # baja del anillo) se recorre en sentido inverso para que se lea de
    # izquierda a derecha
    if not outward:
        a = math.radians(a_end)
        span = -span
    else:
        a = math.radians(a_start)
    for ch, w in zip(text, widths):
        da = span * (w / total_w)
        am = a + da / 2
        x = cx + r * math.cos(am)
        y = cy + r * math.sin(am)
        if ch != " ":
            bbox = font.getbbox(ch)
            gw, gh = bbox[2] - bbox[0] + 8, bbox[3] - bbox[1] + 8
            tile = Image.new("RGBA", (gw * 2, gh * 2), (0, 0, 0, 0))
            td = ImageDraw.Draw(tile)
            td.text((gw / 2, gh / 2), ch, font=font, fill=fill)
            deg = math.degrees(am) + (90 if outward else -90)
            tile = tile.rotate(-deg, resample=Image.BICUBIC,
                               center=(gw / 2 + bbox[0], gh / 2 + bbox[1]))
            img.alpha_composite(tile, (int(x - gw / 2 - bbox[0]),
                                       int(y - gh / 2 - bbox[1])))
        a += da


def crown_mark(d, cx, cy, w, color, lw):
    """Corona lineal de tres puntas — sello de la casa."""
    h = w * 0.72
    base_y = cy + h * 0.30
    # tres picos simétricos (el central más alto) sobre una base horizontal
    pts = [(cx - w / 2, base_y),
           (cx - w / 2, base_y - h * 0.42),
           (cx - w / 6, base_y - h * 0.18),
           (cx, base_y - h * 0.95),
           (cx + w / 6, base_y - h * 0.18),
           (cx + w / 2, base_y - h * 0.42),
           (cx + w / 2, base_y)]
    d.line(pts, fill=color, width=lw, joint="curve")
    d.line([(cx - w / 2, base_y), (cx + w / 2, base_y)], fill=color, width=lw)
    d.line([(cx - w / 2, base_y + lw * 2.2), (cx + w / 2, base_y + lw * 2.2)],
           fill=color, width=lw)
    for (px, py) in (pts[1], pts[3], pts[5]):
        r = lw * 1.7
        d.ellipse([px - r, py - r * 3.4, px + r, py - r * 1.4], fill=color)


def draw_planisphere(size, ss, with_ring_text=True, legend_star=True):
    """Planisferio circular sobre fondo transparente. `size` = diámetro final."""
    S = size * ss
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fs = fonts(ss)
    cx = cy = S / 2
    R = S * 0.485
    lw = max(2, int(S * 0.0022))          # hairline
    lw2 = max(3, int(S * 0.0034))         # línea media

    # ── anillo exterior: doble círculo + graduación
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=GOLD, width=lw2)
    R2 = R * 0.925
    d.ellipse([cx - R2, cy - R2, cx + R2, cy + R2], outline=GOLD, width=lw)
    for i in range(180):
        a = math.radians(i * 2)
        major = (i % 5 == 0)
        r_in = R2 + (0 if major else (R - R2) * 0.45)
        d.line([cx + r_in * math.cos(a), cy + r_in * math.sin(a),
                cx + R * math.cos(a), cy + R * math.sin(a)],
               fill=GOLD if major else GOLD_DIM,
               width=lw2 if major else lw)

    # ── banda de texto circular
    if with_ring_text:
        R3 = R2 * 0.925
        d.ellipse([cx - R3, cy - R3, cx + R3, cy + R3], outline=GOLD_DIM, width=lw)
        ft = fs["small"](int(size * 0.036))
        arc_text(img, cx, cy, (R2 + R3) / 2 * 0.997, "CORONA BOREALIS",
                 ft, GOLD_HI, -90 - 52, -90 + 52, outward=True)
        arc_text(img, cx, cy, (R2 + R3) / 2, "SEPTEM STELLAE · MMXXVI",
                 ft, GOLD, 90 - 48, 90 + 48, outward=False)
        # diamantes separadores E-O
        for ang in (0, 180):
            a = math.radians(ang)
            px, py = cx + (R2 + R3) / 2 * math.cos(a), cy + (R2 + R3) / 2 * math.sin(a)
            s = S * 0.008
            d.polygon([(px, py - s), (px + s, py), (px, py + s), (px - s, py)],
                      outline=GOLD_HI, width=lw)
        Rf = R3
    else:
        Rf = R2

    # ── campo interior: retícula RA/Dec (arcos suaves)
    field = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fd = ImageDraw.Draw(field)
    scale = (Rf * 2) / 13.5      # ≈13.5° de cielo dentro del campo
    for ra in range(228, 246, 2):        # meridianos
        pts = []
        for dec10 in range(215, 355, 4):
            x, y = project(ra, dec10 / 10.0, scale)
            pts.append((cx + x, cy + y))
        fd.line(pts, fill=GOLD_DIM, width=lw)
    for dec in range(22, 36, 2):         # paralelos
        pts = []
        for ra10 in range(2260, 2470, 8):
            x, y = project(ra10 / 10.0, dec, scale)
            pts.append((cx + x, cy + y))
        fd.line(pts, fill=GOLD_DIM, width=lw)
    # máscara circular del campo
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([cx - Rf * 0.985, cy - Rf * 0.985,
                                  cx + Rf * 0.985, cy + Rf * 0.985], fill=255)
    field.putalpha(Image.composite(field.split()[3], Image.new("L", (S, S), 0), mask))
    img.alpha_composite(field)

    # ── estrellas de fondo (deterministas)
    rnd = random.Random(1616)
    star_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(star_layer)
    for _ in range(90):
        a = rnd.uniform(0, 2 * math.pi)
        rr = Rf * 0.96 * math.sqrt(rnd.random())
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        r = rnd.uniform(0.8, 2.2) * S / 1500
        sd.ellipse([x - r, y - r, x + r, y + r],
                   fill=IVORY[:3] + (rnd.randint(70, 160),))
    img.alpha_composite(star_layer)

    # ── constelación
    pos = {}
    for name, gl, ra, dec, mag in CRB:
        x, y = project(ra, dec, scale)
        pos[name] = (cx + x, cy + y, gl, mag)
    chain = ["theta", "beta", "alpha", "gamma", "delta", "epsilon", "iota"]
    for a_, b_ in zip(chain, chain[1:]):
        p1, p2 = pos[a_][:2], pos[b_][:2]
        # acortar para no tocar las estrellas
        vx, vy = p2[0] - p1[0], p2[1] - p1[1]
        L = math.hypot(vx, vy)
        ux, uy = vx / L, vy / L
        m = S * 0.018
        dashed_line(d, (p1[0] + ux * m, p1[1] + uy * m),
                    (p2[0] - ux * m, p2[1] - uy * m),
                    dash=S * 0.008, gap=S * 0.006, fill=GOLD_HI[:3] + (170,),
                    width=lw)
    fg = fs["greek"](int(size * 0.034))
    fl = fs["small"](int(size * 0.026))
    for name, (x, y, gl, mag) in pos.items():
        r = (2.35 - 0.32 * mag) * S / 110
        star_glow(img, x, y, r, IVORY, spikes=7 if name == "alpha" else 0)
        d = ImageDraw.Draw(img)
        d.text((x + r * 2.2, y - r * 2.2), gl, font=fg, fill=GOLD_HI)
    ax, ay = pos["alpha"][:2]
    d.text((ax - S * 0.015, ay + S * 0.035), "ALPHECCA",
           font=fl, fill=GOLD, anchor="la")
    # R CrB — la variable "Blaze Star" como guiño de sabihondos
    rx, ry = project(238.872, 28.157, scale)
    rx, ry = cx + rx, cy + ry
    dashed_circle(d, rx, ry, S * 0.012, 12, GOLD_DIM, lw)
    d.text((rx + S * 0.018, ry - S * 0.008), "R", font=fl, fill=GOLD_DIM)

    # ── corona al norte
    crown_mark(d, cx, cy - Rf - (R - Rf) * 0 - S * 0.0, S * 0.0, GOLD, lw)  # no-op safe
    return img, pos


def compose_planisphere_with_crown(size, ss, **kw):
    """Planisferio + corona centrada sobre el punto norte del anillo."""
    img, pos = draw_planisphere(size, ss, **kw)
    S = size * ss
    d = ImageDraw.Draw(img)
    lw = max(2, int(S * 0.0026))
    crown_mark(d, S / 2, S * 0.028, S * 0.052, GOLD_HI, lw)
    return img


def save(img, name, w, h):
    img = img.resize((w, h), Image.LANCZOS)
    img.save(os.path.join(OUT, name))
    print("✓", name, img.size)


# ═══════════════════════ 1. Camiseta (negro) — 1800×2400 ═══════════════════
def tee_front():
    W, H = 1800, 2400
    S = SS
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    fs = fonts(S)
    plani = compose_planisphere_with_crown(1560, S)
    img.alpha_composite(plani, ((W - 1560) // 2 * S, 150 * S))
    d = ImageDraw.Draw(img)
    ft = fs["title"](86)
    d.text((W * S / 2, 1900 * S), "STREET ROYALTY", font=ft,
           fill=GOLD_HI, anchor="mm")
    # regla con diamante
    y = 1990 * S
    d.line([(W / 2 - 330) * S, y, (W / 2 - 40) * S, y], fill=GOLD, width=3 * S)
    d.line([(W / 2 + 40) * S, y, (W / 2 + 330) * S, y], fill=GOLD, width=3 * S)
    s = 12 * S
    d.polygon([(W * S / 2, y - s), (W * S / 2 + s, y), (W * S / 2, y + s),
               (W * S / 2 - s, y)], outline=GOLD_HI, width=3 * S)
    fsub = fs["small"](40)
    d.text((W * S / 2, 2060 * S), "OBSERVATORIVM · LAT XL° N",
           font=fsub, fill=GOLD, anchor="mm")
    save(img, "tee_front.png", W, H)


# ═══════════════ 2. Manga larga (navy) — "columna celeste" ══════════════════
def ls_front():
    W, H = 1800, 2400
    S = SS
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fs = fonts(S)
    lw = 3 * S
    cx = W * S / 2

    # corona en cabecera
    crown_mark(d, cx, 130 * S, 120 * S, GOLD_HI, lw)

    # meridiano central graduado
    top, bot = 260 * S, 2020 * S
    d.line([cx, top, cx, bot], fill=GOLD, width=lw)
    for i in range(89):
        y = top + (bot - top) * i / 88
        major = (i % 8 == 0)
        t = (26 if major else 12) * S
        d.line([cx - t, y, cx + t, y], fill=GOLD if major else GOLD_DIM,
               width=lw if major else max(2, 2 * S))

    # estrellas de la Corona en escalera sobre el meridiano
    fg = fs["greek"](58)
    fl = fs["small"](36)
    chain = ["theta", "beta", "alpha", "gamma", "delta", "epsilon", "iota"]
    coords = []
    for i, name in enumerate(chain):
        rec = next(c for c in CRB if c[0] == name)
        _, gl, ra, dec, mag = rec
        frac = i / (len(chain) - 1)
        y = top + (bot - top) * (0.10 + 0.62 * frac)
        # zig-zag suave alrededor del eje, según declinación
        x = cx + (dec - DEC0) * 34 * S * (1 if i % 2 == 0 else 1)
        x = cx + (dec - DEC0) * 40 * S
        coords.append((x, y, gl, mag, name))
    for (p1, p2) in zip(coords, coords[1:]):
        dashed_line(d, p1[:2], p2[:2], dash=14 * S, gap=10 * S,
                    fill=GOLD_HI[:3] + (170,), width=max(2, 2 * S))
    for x, y, gl, mag, name in coords:
        r = (2.5 - 0.33 * mag) * 16 * S
        star_glow(img, x, y, r, IVORY, spikes=7 if name == "alpha" else 0)
        d = ImageDraw.Draw(img)
        d.text((x + r * 2.4, y - r * 2.0), gl, font=fg, fill=GOLD_HI)
    ax, ay = next((x, y) for x, y, gl, m, n in coords if n == "alpha")
    d.text((ax + 90 * S, ay + 40 * S), "ALPHECCA", font=fl, fill=GOLD)

    # tres marcas de instrumento (círculos concéntricos) en el lado libre
    for (mx, my, mr) in [(cx - 420 * S, 700 * S, 90 * S),
                         (cx + 430 * S, 1350 * S, 70 * S),
                         (cx - 440 * S, 1750 * S, 55 * S)]:
        for k, rr in enumerate([1.0, 0.62, 0.18]):
            d.ellipse([mx - mr * rr, my - mr * rr, mx + mr * rr, my + mr * rr],
                      outline=GOLD_DIM if k else GOLD, width=max(2, 2 * S))
        d.line([mx - mr * 1.25, my, mx + mr * 1.25, my], fill=GOLD_DIM,
               width=max(2, 2 * S))
        d.line([mx, my - mr * 1.25, mx, my + mr * 1.25], fill=GOLD_DIM,
               width=max(2, 2 * S))

    # pie
    ft = fs["title"](64)
    d.text((cx, 2160 * S), "CORONA BOREALIS", font=ft, fill=GOLD_HI, anchor="mm")
    d.text((cx, 2250 * S), "ASCENSIO RECTA · XVI H", font=fs["small"](38),
           fill=GOLD, anchor="mm")
    save(img, "ls_front.png", W, H)


# ═══════════════ 3. Hoodie premium (navy) — astrolabio 1800×1800 ════════════
def hoodie_front():
    W = H = 1800
    S = SS
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    plani = compose_planisphere_with_crown(1660, S)
    img.alpha_composite(plani, ((W - 1660) // 2 * S, ((H - 1660) // 2 + 20) * S))
    save(img, "hoodie_front.png", W, H)


# ═══════════════ 4. Zip hoodie (negro) — gran carta de espalda ══════════════
def zip_back():
    W, H = 1800, 2400
    S = SS
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    fs = fonts(S)
    plani = compose_planisphere_with_crown(1620, S)
    img.alpha_composite(plani, ((W - 1620) // 2 * S, 90 * S))
    d = ImageDraw.Draw(img)

    # cartucho-leyenda
    x0, y0, x1, y1 = 240 * S, 1830 * S, 1560 * S, 2280 * S
    lw = 3 * S
    d.rectangle([x0, y0, x1, y1], outline=GOLD, width=lw)
    m = 14 * S
    d.rectangle([x0 + m, y0 + m, x1 - m, y1 - m], outline=GOLD_DIM,
                width=max(2, 2 * S))
    cx = W * S / 2
    d.text((cx, y0 + 90 * S), "CARTA CÆLESTIS", font=fs["title"](66),
           fill=GOLD_HI, anchor="mm")
    d.text((cx, y0 + 175 * S), "CORONA BOREALIS · SEPTEM STELLAE",
           font=fs["small"](40), fill=GOLD, anchor="mm")
    # escala de magnitudes: estrellas decrecientes + numerales
    mags = [(1, 30), (2, 24), (3, 19), (4, 15), (5, 11)]
    total = 640 * S
    step = total / (len(mags) - 1)
    bx = cx - total / 2
    by = y0 + 285 * S
    fnum = fs["small"](34)
    for i, (roman, r) in enumerate(zip(["I", "II", "III", "IV", "V"],
                                       [m[1] for m in mags])):
        x = bx + step * i
        star_glow(img, x, by, r * S * 0.9, IVORY)
        d = ImageDraw.Draw(img)
        d.text((x, by + 70 * S), roman, font=fnum, fill=GOLD, anchor="mm")
    d.text((cx, y1 - 55 * S), "STREET ROYALTY HOOD · MMXXVI",
           font=fs["small"](36), fill=GOLD, anchor="mm")
    save(img, "zip_back.png", W, H)


# ═══════════════ Fondo nocturno para calzado ════════════════════════════════
def night_bg(W, H, S):
    """Gradiente radial medianoche + niebla estelar."""
    img = Image.new("RGB", (W * S, H * S), NIGHT_E)
    # gradiente radial por máscara
    grad = Image.new("L", (W * S, H * S), 0)
    gd = ImageDraw.Draw(grad)
    cx, cy = W * S * 0.5, H * S * 0.42
    maxr = math.hypot(max(cx, W * S - cx), max(cy, H * S - cy))
    steps = 60
    for i in range(steps, 0, -1):
        r = maxr * i / steps
        val = int(255 * (1 - i / steps) ** 1.6)
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=val)
    center = Image.new("RGB", (W * S, H * S), NIGHT_C)
    img = Image.composite(center, img, grad)
    # niebla (nebulosa tenue)
    rnd = random.Random(2718)
    fog = Image.new("L", (W * S // 8, H * S // 8), 0)
    fd = ImageDraw.Draw(fog)
    for _ in range(30):
        x, y = rnd.uniform(0, fog.width), rnd.uniform(0, fog.height)
        r = rnd.uniform(fog.width * 0.05, fog.width * 0.22)
        fd.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(10, 26))
    fog = fog.resize((W * S, H * S)).filter(
        ImageFilter.GaussianBlur(W * S * 0.05))
    tint = Image.new("RGB", (W * S, H * S), (46, 58, 105))
    img = Image.composite(tint, img, fog)
    return img.convert("RGBA")


def starfield(img, n, seed, margin=0.0):
    S1 = img.size[0]
    rnd = random.Random(seed)
    W, H = img.size
    for _ in range(n):
        x = rnd.uniform(W * margin, W * (1 - margin))
        y = rnd.uniform(H * margin, H * (1 - margin))
        mag = rnd.random()
        r = (0.8 + 3.4 * mag ** 3) * W / 2250
        alpha = rnd.randint(80, 220)
        if mag > 0.93:
            star_glow(img, x, y, r * 1.6, IVORY)
        else:
            d = ImageDraw.Draw(img)
            d.ellipse([x - r, y - r, x + r, y + r],
                      fill=IVORY[:3] + (alpha,))


def shoe_common(W, H, seed, const_center, const_scale, ring=None):
    S = 1  # los printfiles AOP ya son grandes; sin supersampling extra
    img = night_bg(W, H, S)
    d = ImageDraw.Draw(img)
    lw = max(2, W // 900)

    # retícula ligera inclinada (arcos amplios)
    for i in range(-3, 9):
        r = W * (0.55 + i * 0.16)
        cx, cy = -W * 0.25, H * 1.15
        d.arc([cx - r, cy - r, cx + r, cy + r], -90, 10,
              fill=GOLD[:3] + (38,), width=lw)
    for i in range(-2, 8):
        r = W * (0.5 + i * 0.18)
        cx, cy = W * 1.3, -H * 0.12
        d.arc([cx - r, cy - r, cx + r, cy + r], 90, 200,
              fill=GOLD[:3] + (30,), width=lw)

    starfield(img, int(W * H / 16000), seed)

    # constelación protagonista
    ccx, ccy = const_center
    scale = const_scale
    pos = {}
    for name, gl, ra, dec, mag in CRB:
        x, y = project(ra, dec, scale)
        pos[name] = (ccx + x, ccy + y, gl, mag)
    chain = ["theta", "beta", "alpha", "gamma", "delta", "epsilon", "iota"]
    d = ImageDraw.Draw(img)
    for a_, b_ in zip(chain, chain[1:]):
        p1, p2 = pos[a_][:2], pos[b_][:2]
        vx, vy = p2[0] - p1[0], p2[1] - p1[1]
        L = math.hypot(vx, vy)
        ux, uy = vx / L, vy / L
        m = W * 0.015
        dashed_line(d, (p1[0] + ux * m, p1[1] + uy * m),
                    (p2[0] - ux * m, p2[1] - uy * m),
                    dash=W * 0.012, gap=W * 0.008,
                    fill=GOLD_HI[:3] + (200,), width=lw)
    for name, (x, y, gl, mag) in pos.items():
        r = (2.4 - 0.31 * mag) * W / 130
        star_glow(img, x, y, r, IVORY, spikes=6 if name == "alpha" else 0)

    # anillo de graduación decorativo (parcial)
    if ring:
        rx, ry, rr = ring
        d = ImageDraw.Draw(img)
        d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr],
                  outline=GOLD[:3] + (150,), width=lw)
        for i in range(72):
            a = math.radians(i * 5)
            major = (i % 3 == 0)
            r_in = rr - (rr * 0.045 if major else rr * 0.025)
            d.line([rx + r_in * math.cos(a), ry + r_in * math.sin(a),
                    rx + rr * math.cos(a), ry + rr * math.sin(a)],
                   fill=GOLD[:3] + (150 if major else 90,), width=lw)
        dashed_circle(d, rx, ry, rr * 0.82, 60, GOLD[:3] + (90,), lw)
    return img


def shoe_quarters():
    W = H = 2250
    img = shoe_common(W, H, seed=31415,
                      const_center=(W * 0.52, H * 0.40), const_scale=95,
                      ring=(W * 0.16, H * 0.86, W * 0.30))
    save(img.convert("RGB"), "shoe_quarters.png", W, H)


def shoe_athletic():
    W, H = 1950, 3300
    img = shoe_common(W, H, seed=27182,
                      const_center=(W * 0.50, H * 0.26), const_scale=88,
                      ring=(W * 0.88, H * 0.80, W * 0.42))
    save(img.convert("RGB"), "shoe_athletic.png", W, H)


if __name__ == "__main__":
    tee_front()
    ls_front()
    hoodie_front()
    zip_back()
    shoe_quarters()
    shoe_athletic()
    print("Cápsula Celeste — archivos generados en", OUT)
