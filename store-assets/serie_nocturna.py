#!/usr/bin/env python3
"""Serie Nocturna — diseños originales SRHOOD (run 2026-07-17).

Seis familias de patrón nuevas, no usadas antes en la tienda:
  1. corona_boreal   — carta astral con constelación en forma de corona (hoodie, 3600x4800, transparente)
  2. marea_real      — marmoleado suminagashi en crema/oro (camiseta, 3600x4800, transparente)
  3. terrazzo        — medallón terrazzo con teselas burdeos/navy/oro (sudadera, 3600x4800, transparente)
  4. isometrica      — teselado de cubos isométricos con acentos oro (zapatillas lona hombre, 2325x2325)
  5. jardin_nocturno — botánica line-art oro/crema/burdeos sobre negro (altas mujer, 2325x2325)
  6. meandro         — greca meandro oro sobre negro (calcetines, 1400x2400)

Todo se dibuja con supersampling 2x y se reduce con LANCZOS para bordes limpios.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = "/tmp/claude-0/-home-user-6Sylence/e5995c57-4764-51f3-9253-83fef775468f/scratchpad/designs"

CREMA = (239, 230, 212, 255)
BLANCO = (248, 246, 240, 255)
ORO = (201, 162, 75, 255)
ORO_CLARO = (226, 194, 120, 255)
BURDEOS = (110, 31, 46, 255)
NAVY = (31, 42, 68, 255)
NEGRO = (12, 12, 16, 255)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def canvas(w, h, bg=(0, 0, 0, 0), ss=2):
    img = Image.new("RGBA", (w * ss, h * ss), bg)
    return img, ImageDraw.Draw(img), ss


def save(img, name, w, h):
    img = img.resize((w, h), Image.LANCZOS)
    img.save(f"{OUT}/{name}.png")
    print(name, img.size)


def spaced_text(draw, xy, text, font, fill, tracking, anchor_mid_x=None):
    """Texto con letter-spacing; centrado en x si anchor_mid_x."""
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (anchor_mid_x - total / 2) if anchor_mid_x is not None else xy[0]
    y = xy[1]
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking


def star(draw, x, y, r, fill, glow_layer=None):
    """Estrella de 4 puntas (diamante curvo) + núcleo."""
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)
    if glow_layer is not None:
        g = ImageDraw.Draw(glow_layer)
        g.ellipse([x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2],
                  fill=(fill[0], fill[1], fill[2], 40))


# ────────────────────────────── 1. CORONA BOREAL ──────────────────────────────
def corona_boreal():
    W, H = 3600, 4800
    img, d, ss = canvas(W, H)
    rnd = random.Random(20260717)
    cx, cy, R = W * ss // 2, int(H * ss * 0.44), int(W * ss * 0.44)

    # anillos de carta astral
    for rr, alpha, wd in [(R, 200, 10), (R - 90 * ss, 130, 5), (int(R * 0.62), 115, 5)]:
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=CREMA[:3] + (alpha,), width=wd)
    # marcas de grados en el anillo exterior
    for i in range(72):
        ang = math.tau * i / 72
        ln = 34 * ss if i % 6 == 0 else 16 * ss
        x1 = cx + (R - ln) * math.cos(ang); y1 = cy + (R - ln) * math.sin(ang)
        x2 = cx + R * math.cos(ang); y2 = cy + R * math.sin(ang)
        d.line([x1, y1, x2, y2], fill=CREMA[:3] + (185,), width=4 * ss)

    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))

    # campo de estrellas dentro del círculo
    for _ in range(320):
        ang = rnd.uniform(0, math.tau)
        rad = R * math.sqrt(rnd.uniform(0.02, 0.96))
        x, y = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
        r = rnd.choice([4, 4, 5, 5, 6, 7, 9, 11]) * ss
        col = rnd.choice([CREMA, BLANCO, BLANCO, ORO_CLARO])
        if r <= 5 * ss:
            d.ellipse([x - r, y - r, x + r, y + r], fill=col[:3] + (rnd.randint(185, 255),))
        else:
            star(d, x, y, r, col, glow if r >= 7 * ss else None)

    # cruces finas dispersas (estilo carta de navegación)
    for _ in range(30):
        ang = rnd.uniform(0, math.tau)
        rad = R * math.sqrt(rnd.uniform(0.05, 0.9))
        x, y = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
        s = rnd.randint(8, 14) * ss
        d.line([x - s, y, x + s, y], fill=CREMA[:3] + (150,), width=3 * ss)
        d.line([x, y - s, x, y + s], fill=CREMA[:3] + (150,), width=3 * ss)

    # constelación CORONA: arco de 7 estrellas principales con picos
    base_pts = [(-0.72, 0.30), (-0.48, -0.07), (-0.24, 0.16), (0.0, -0.26),
                (0.24, 0.16), (0.48, -0.07), (0.72, 0.30)]
    scale = R * 0.78
    cpts = [(cx + px * scale, cy + py * scale * 0.9 - R * 0.05) for px, py in base_pts]
    # línea base de la corona (une los puntos bajos)
    for a, b in zip(cpts, cpts[1:]):
        d.line([a, b], fill=ORO_CLARO[:3] + (245,), width=9 * ss)
    lows = [cpts[0], cpts[2], cpts[4], cpts[6]]
    for a, b in zip(lows, lows[1:]):
        d.line([a, b], fill=ORO[:3] + (185,), width=5 * ss)
    for i, (x, y) in enumerate(cpts):
        big = i % 2 == 1 or i in (0, 6)
        r = (22 if big else 15) * ss
        star(d, x, y, r, ORO_CLARO if big else CREMA, glow)
        d.ellipse([x - r * 1.7, y - r * 1.7, x + r * 1.7, y + r * 1.7],
                  outline=ORO[:3] + (190,), width=3 * ss)

    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(18 * ss)))
    d = ImageDraw.Draw(img)

    # rótulos
    f1 = ImageFont.truetype(FONT_B, 92 * ss)
    f2 = ImageFont.truetype(FONT, 58 * ss)
    spaced_text(d, (0, cy + R + 150 * ss), "CORONA BOREAL", f1, CREMA, 46 * ss, anchor_mid_x=cx)
    spaced_text(d, (0, cy + R + 300 * ss), "SRH · CARTA ASTRAL · MMXXVI", f2,
                ORO[:3] + (230,), 30 * ss, anchor_mid_x=cx)
    save(img, "nocturna_corona_boreal", W, H)


# ────────────────────────────── 2. MAREA REAL ──────────────────────────────
def marea_real():
    W, H = 3600, 4800
    img, d, ss = canvas(W, H)
    rnd = random.Random(1707)
    cx, cy = W * ss // 2, int(H * ss * 0.44)
    Rmax = int(W * ss * 0.45)
    n_rings = 40

    # armónicos compartidos que evolucionan suavemente ring a ring → vetas coherentes
    harmonics = [(rnd.randint(2, 5), rnd.uniform(0, math.tau), rnd.uniform(0.012, 0.035))
                 for _ in range(4)]
    drift = [rnd.uniform(-0.12, 0.12) for _ in harmonics]

    for k in range(n_rings):
        t = k / (n_rings - 1)
        base = 80 * ss + t * (Rmax * 0.82 - 90 * ss)
        pts = []
        for s in range(361):
            th = math.tau * s / 360
            r = base
            for (f, ph, amp), dph in zip(harmonics, drift):
                r += base * amp * math.sin(f * th + ph + dph * k)
            # pellizco tipo tinta arrastrada, contenido
            r += base * 0.06 * math.sin(th + k * 0.35)
            r = min(r, Rmax * 0.985)
            pts.append((cx + r * math.cos(th), cy + r * 0.96 * math.sin(th)))
        if k % 6 == 3:
            col, wd = ORO[:3] + (235,), rnd.randint(9, 12) * ss
        elif k % 6 == 0:
            col, wd = BLANCO[:3] + (200,), rnd.randint(5, 7) * ss
        else:
            col, wd = CREMA[:3] + (rnd.randint(150, 210),), rnd.randint(4, 8) * ss
        d.line(pts + [pts[0]], fill=col, width=wd, joint="curve")

    # gota central: pequeño núcleo concéntrico
    for rr, col in [(46, ORO), (28, CREMA), (12, ORO_CLARO)]:
        d.ellipse([cx - rr * ss, cy - rr * ss, cx + rr * ss, cy + rr * ss],
                  outline=col[:3] + (240,), width=5 * ss)

    f1 = ImageFont.truetype(FONT_B, 92 * ss)
    f2 = ImageFont.truetype(FONT, 58 * ss)
    ybase = cy + Rmax + 130 * ss
    spaced_text(d, (0, ybase), "MAREA REAL", f1, CREMA, 52 * ss, anchor_mid_x=cx)
    spaced_text(d, (0, ybase + 150 * ss), "SRH · TINTA SOBRE AGUA · MMXXVI", f2,
                ORO[:3] + (230,), 28 * ss, anchor_mid_x=cx)
    save(img, "nocturna_marea_real", W, H)


# ────────────────────────────── 3. TERRAZZO IMPERIAL ──────────────────────────────
def chip(draw, x, y, size, col, rnd):
    n = rnd.randint(4, 7)
    angs = sorted(rnd.uniform(0, math.tau) for _ in range(n))
    pts = [(x + size * rnd.uniform(0.62, 1.0) * math.cos(a),
            y + size * rnd.uniform(0.62, 1.0) * math.sin(a)) for a in angs]
    draw.polygon(pts, fill=col)


def terrazzo():
    W, H = 3600, 4800
    img, d, ss = canvas(W, H)
    rnd = random.Random(4747)
    cx, cy, R = W * ss // 2, int(H * ss * 0.45), int(W * ss * 0.45)

    # medallón base
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(22, 22, 26, 255))
    # teselas grandes (clip circular manual: descartar fuera de radio)
    cols = [CREMA, CREMA, BURDEOS, NAVY, ORO, (154, 154, 158, 255)]
    placed = []
    tries = 0
    while len(placed) < 90 and tries < 4000:
        tries += 1
        size = rnd.randint(55, 165) * ss
        rad = (R - size - 26 * ss) * math.sqrt(rnd.random())
        ang = rnd.uniform(0, math.tau)
        x, y = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
        if any((x - px) ** 2 + (y - py) ** 2 < (size + psz) ** 2 * 0.72 for px, py, psz in placed):
            continue
        chip(d, x, y, size, rnd.choice(cols), rnd)
        placed.append((x, y, size))
    # speckles pequeños
    for _ in range(340):
        size = rnd.randint(8, 26) * ss
        rad = (R - size - 14 * ss) * math.sqrt(rnd.random())
        ang = rnd.uniform(0, math.tau)
        x, y = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
        chip(d, x, y, size, rnd.choice(cols), rnd)

    # anillos del medallón
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=ORO, width=14 * ss)
    r2 = R - 40 * ss
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=CREMA[:3] + (170,), width=4 * ss)

    f1 = ImageFont.truetype(FONT_B, 92 * ss)
    f2 = ImageFont.truetype(FONT, 58 * ss)
    ybase = cy + R + 140 * ss
    spaced_text(d, (0, ybase), "TERRAZZO IMPERIAL", f1, CREMA, 40 * ss, anchor_mid_x=cx)
    spaced_text(d, (0, ybase + 150 * ss), "SRH · PIEDRA Y ORO · MMXXVI", f2,
                ORO[:3] + (230,), 28 * ss, anchor_mid_x=cx)
    save(img, "nocturna_terrazzo", W, H)


# ────────────────────────────── 4. ISOMÉTRICA (calzado hombre) ──────────────────────────────
def isometrica():
    S = 2325
    img, d, ss = canvas(S, S, bg=(16, 16, 20, 255))
    rnd = random.Random(9090)
    a = 105 * ss  # arista
    h = a * math.sqrt(3) / 2

    greys = [((46, 46, 53), (27, 27, 32), (17, 17, 21)),
             ((56, 56, 64), (33, 33, 39), (20, 20, 25)),
             ((40, 40, 46), (24, 24, 29), (15, 15, 19))]
    gold = ((208, 172, 92), (166, 127, 51), (126, 95, 36))

    rows = int(S * ss / (a * 1.5)) + 3
    cols_n = int(S * ss / (2 * h)) + 3
    for row in range(-1, rows):
        for col in range(-1, cols_n):
            x = col * 2 * h + (h if row % 2 else 0)
            y = row * 1.5 * a
            top, left, right = gold if rnd.random() < 0.055 else rnd.choice(greys)
            # cara superior (rombo)
            d.polygon([(x, y - a), (x + h, y - a / 2), (x, y), (x - h, y - a / 2)], fill=top + (255,))
            # cara izquierda
            d.polygon([(x - h, y - a / 2), (x, y), (x, y + a), (x - h, y + a / 2)], fill=left + (255,))
            # cara derecha
            d.polygon([(x + h, y - a / 2), (x, y), (x, y + a), (x + h, y + a / 2)], fill=right + (255,))
            # aristas sutiles
            d.line([(x, y), (x, y + a)], fill=(10, 10, 13, 255), width=2 * ss)
            d.line([(x - h, y - a / 2), (x, y), (x + h, y - a / 2)], fill=(10, 10, 13, 255), width=2 * ss)
    save(img, "nocturna_isometrica", S, S)


# ────────────────────────────── 5. JARDÍN NOCTURNO (altas mujer) ──────────────────────────────
def flower(d, x, y, sc, rot, npet, col, ss, rnd):
    """Flor line-art: pétalos = pares de arcos bezier aproximados con polilíneas."""
    for i in range(npet):
        ang = rot + math.tau * i / npet
        tipx, tipy = x + sc * math.cos(ang), y + sc * math.sin(ang)
        perp = ang + math.pi / 2
        wx, wy = math.cos(perp) * sc * 0.34, math.sin(perp) * sc * 0.34
        for sgn in (1, -1):
            pts = []
            for t in [j / 14 for j in range(15)]:
                bx = (1 - t) ** 2 * x + 2 * (1 - t) * t * ((x + tipx) / 2 + sgn * wx) + t ** 2 * tipx
                by = (1 - t) ** 2 * y + 2 * (1 - t) * t * ((y + tipy) / 2 + sgn * wy) + t ** 2 * tipy
                pts.append((bx, by))
            d.line(pts, fill=col, width=max(3, int(sc * 0.045)), joint="curve")
    core = max(5 * ss, sc * 0.14)
    d.ellipse([x - core, y - core, x + core, y + core], outline=CREMA, width=3 * ss)
    d.ellipse([x - core * 0.4, y - core * 0.4, x + core * 0.4, y + core * 0.4], fill=ORO_CLARO)


def jardin_nocturno():
    S = 2325
    img, d, ss = canvas(S, S, bg=(12, 12, 16, 255))
    rnd = random.Random(3131)
    total = S * ss

    # tallos ondulantes de fondo
    for _ in range(26):
        x0, y0 = rnd.uniform(0, total), rnd.uniform(0, total)
        ang = rnd.uniform(0, math.tau)
        pts, x, y = [], x0, y0
        for t in range(30):
            x += math.cos(ang) * 26 * ss
            y += math.sin(ang) * 26 * ss
            ang += rnd.uniform(-0.28, 0.28)
            pts.append((x, y))
        d.line(pts, fill=(96, 106, 84, 200), width=4 * ss, joint="curve")
        # hojitas
        for i in range(4, len(pts) - 4, 7):
            px, py = pts[i]
            la = math.atan2(pts[i + 1][1] - py, pts[i + 1][0] - px) + rnd.choice([1.0, -1.0])
            lx, ly = px + math.cos(la) * 40 * ss, py + math.sin(la) * 40 * ss
            d.line([px, py, lx, ly], fill=(96, 106, 84, 200), width=3 * ss)
            d.ellipse([lx - 12 * ss, ly - 12 * ss, lx + 12 * ss, ly + 12 * ss],
                      outline=(96, 106, 84, 200), width=3 * ss)

    # flores principales (poisson-ish)
    placed = []
    tries = 0
    while len(placed) < 26 and tries < 3000:
        tries += 1
        sc = rnd.randint(85, 200) * ss
        x, y = rnd.uniform(0, total), rnd.uniform(0, total)
        if any((x - px) ** 2 + (y - py) ** 2 < (sc + ps) ** 2 * 1.05 for px, py, ps in placed):
            continue
        col = rnd.choice([ORO, ORO, CREMA, (156, 61, 79, 255)])
        flower(d, x, y, sc, rnd.uniform(0, math.tau), rnd.choice([5, 6, 6, 8]), col, ss, rnd)
        placed.append((x, y, sc))

    # polen / estrellitas
    for _ in range(160):
        x, y = rnd.uniform(0, total), rnd.uniform(0, total)
        r = rnd.randint(3, 7) * ss
        d.ellipse([x - r, y - r, x + r, y + r],
                  fill=rnd.choice([ORO_CLARO[:3] + (150,), CREMA[:3] + (110,)]))
    save(img, "nocturna_jardin", S, S)


# ────────────────────────────── 6. MEANDRO REAL (calcetines) ──────────────────────────────
def meandro():
    W, H = 1400, 2400
    img, d, ss = canvas(W, H, bg=(16, 16, 19, 255))
    unit = 100 * ss   # celda del meandro
    wd = 16 * ss      # grosor del trazo

    def greek_column(x0, mirror=1):
        """Columna vertical de greca (meandro) descendente."""
        pts = [(x0, -unit)]
        y = -unit
        x = x0
        while y < H * ss + unit:
            seq = [(0, unit), (mirror * unit, 0), (0, -unit * 0.6), (-mirror * unit * 0.6, 0),
                   (0, unit * 0.3), (mirror * unit * 0.3, 0), (0, unit * 0.3 + unit * 0.6 - unit * 0.3)]
            for dx, dy in seq:
                x += dx; y += dy
                pts.append((x, y))
            x = x0
            pts.append((x, y))
        d.line(pts, fill=ORO, width=wd, joint="curve")

    xs = [W * ss * 0.18, W * ss * 0.5, W * ss * 0.82]
    for i, x0 in enumerate(xs):
        greek_column(x0, mirror=1 if i % 2 == 0 else -1)
        # pinstripes crema entre columnas
    for xp in [W * ss * 0.34, W * ss * 0.66]:
        d.line([(xp, 0), (xp, H * ss)], fill=CREMA[:3] + (140,), width=4 * ss)
    save(img, "nocturna_meandro", W, H)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    corona_boreal()
    marea_real()
    terrazzo()
    isometrica()
    jardin_nocturno()
    meandro()
