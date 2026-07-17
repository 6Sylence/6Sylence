#!/usr/bin/env python3
"""Cápsula Pañuelo — Paisley Real (SRHOOD).

Genera los archivos de impresión de la cápsula paisley/bandana:
  tee_front      1800x2400  Camiseta (Soft Cream)          — medallón bandana
  ls_front       1800x2400  Manga larga (Military Green)   — cascada de botehs
  zip_front      2250x1500  Hoodie cremallera (Forest)     — banda pecho
  zip_back       1800x2400  Hoodie cremallera (Forest)     — boteh gigante
  hitop_quarters 2250x2250  Zapatillas altas H (Black)     — tile all-over
  hitop_tongue   2250x2250  Zapatillas altas H (Black)     — medallón lengüeta
  athletic_shoe  1950x3300  Deportivas M (White)           — scatter crema
  bucket_out     2700x3150  Bucket reversible — exterior crema
  bucket_in      2700x3150  Bucket reversible — interior forest

Uso: python3 paisley_real.py [--preview] [salida_dir]
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# Paleta
FOREST = (29, 58, 41, 255)        # verde bosque
FOREST_DEEP = (19, 40, 28, 255)   # sombra
CREMA = (243, 236, 216, 255)
RUST = (184, 92, 46, 255)         # óxido
INK = (23, 28, 23, 255)
TRANSP = (0, 0, 0, 0)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

SS = 2  # supersampling


def bezier(p0, p1, p2, p3, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


BULB = (0.0, -0.17)  # centro del bulbo tras recentrar


def boteh_outline(inset=1.0):
    """Contorno paisley clásico (bezier ajustado a mano): bulbo abajo, punta
    arriba con rizo a la derecha y muesca cóncava. y-arriba, alto ~1,
    recentrado para que (0,0) sea el centro visual."""
    A = (0.0, 0.0)
    pts = []
    pts += bezier(A, (-0.34, 0.02), (-0.38, 0.30), (-0.28, 0.48))
    pts += bezier((-0.28, 0.48), (-0.20, 0.66), (-0.10, 0.80), (0.10, 0.97))[1:]
    pts += bezier((0.10, 0.97), (0.24, 0.93), (0.24, 0.82), (0.15, 0.75))[1:]
    pts += bezier((0.15, 0.75), (0.06, 0.68), (0.10, 0.60), (0.20, 0.58))[1:]
    pts += bezier((0.20, 0.58), (0.34, 0.50), (0.38, 0.28), (0.30, 0.12))[1:]
    pts += bezier((0.30, 0.12), (0.24, 0.00), (0.12, -0.04), A)[1:]
    pts = [(x, y - 0.45) for x, y in pts]
    if inset != 1.0:
        bx, by = BULB
        pts = [(bx + (x - bx) * inset, by + (y - by) * inset) for x, y in pts]
    return pts


BOTEH = boteh_outline()
BOTEH_MID = boteh_outline(0.74)
BOTEH_IN = boteh_outline(0.50)
BOTEH_DOTS = boteh_outline(0.86)


def transform(pts, cx, cy, scale, rot_deg=0.0, flip=False, y_down=True):
    rot = math.radians(rot_deg)
    cr, sr = math.cos(rot), math.sin(rot)
    out = []
    for x, y in pts:
        if flip:
            x = -x
        xr = x * cr - y * sr
        yr = x * sr + y * cr
        if y_down:
            yr = -yr
        out.append((cx + xr * scale, cy + yr * scale))
    return out


def offset_inward(pts, dist):
    """Offset aproximado hacia el interior del polígono (por normales)."""
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1]
               - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts)))
    sign = 1.0 if area > 0 else -1.0
    out = []
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[(i - 2) % n]
        x1, y1 = pts[(i + 2) % n]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L * sign, dx / L * sign
        out.append((pts[i][0] + nx * dist, pts[i][1] + ny * dist))
    return out


def centroid(pts):
    xs = sum(p[0] for p in pts) / len(pts)
    ys = sum(p[1] for p in pts) / len(pts)
    return xs, ys


def shrink(pts, factor, toward=None):
    cx, cy = toward or centroid(pts)
    return [(cx + (x - cx) * factor, cy + (y - cy) * factor) for x, y in pts]


def draw_boteh(d, cx, cy, scale, rot=0.0, flip=False, line=CREMA, fill=None,
               accent=RUST, lw=None, detail=True, dots=True):
    """Boteh paisley con contornos anidados, puntos sobre la espina y florón."""
    lw = lw or max(2, int(scale * 0.05))
    outer = transform(BOTEH, cx, cy, scale, rot, flip)
    if fill:
        d.polygon(outer, fill=fill)
    d.line(outer + outer[:1], fill=line, width=lw, joint="curve")
    if not detail:
        return
    mid = transform(BOTEH_MID, cx, cy, scale, rot, flip)
    d.line(mid + mid[:1], fill=line, width=max(1, int(lw * 0.45)),
           joint="curve")
    if dots:
        # puntos acento entre los dos contornos, siguiendo el lado convexo
        band = transform(BOTEH_DOTS, cx, cy, scale, rot, flip)
        rr = max(2, int(scale * 0.024))
        for i in range(0, int(len(band) * 0.55), 9):
            x, y = band[i]
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=accent)
    # florón: círculo + pétalos en el centro del bulbo
    bx, by = transform([BULB], cx, cy, scale, rot, flip)[0]
    fr = scale * 0.10
    d.ellipse([bx - fr, by - fr, bx + fr, by + fr], outline=line,
              width=max(1, int(lw * 0.45)))
    pr = scale * 0.042
    for k in range(6):
        a = math.radians(60 * k)
        px, py = bx + math.cos(a) * fr * 1.6, by + math.sin(a) * fr * 1.6
        d.ellipse([px - pr, py - pr, px + pr, py + pr], outline=line,
                  width=max(1, int(lw * 0.45)))
    cr2 = scale * 0.045
    d.ellipse([bx - cr2, by - cr2, bx + cr2, by + cr2], fill=accent)


def draw_crown(d, cx, cy, w, color, lw=None, fill=None):
    """Corona SRHOOD de tres puntas, trazo geométrico."""
    lw = lw or max(2, int(w * 0.045))
    h = w * 0.62
    base_y = cy + h * 0.38
    top_y = cy - h * 0.62
    mid_y = cy - h * 0.30
    pts = [
        (cx - w / 2, base_y), (cx - w / 2, mid_y), (cx - w * 0.25, top_y * 0.0 + mid_y * 0.0 + (mid_y + top_y) / 2 + (base_y - mid_y) * 0),
    ]
    # polilínea de la corona: base izquierda -> 3 picos -> base derecha
    pts = [
        (cx - w / 2, base_y),
        (cx - w / 2, mid_y),
        (cx - w / 6, (mid_y + top_y) / 2),
        (cx - w / 4, top_y + (base_y - top_y) * 0.0 + 0),
    ]
    # construcción limpia: picos en -w/2, 0, w/2 con valles
    peak = top_y
    valley = mid_y + (base_y - mid_y) * 0.15
    pts = [
        (cx - w / 2, base_y),
        (cx - w / 2, peak + (valley - peak) * 0.25),
        (cx - w / 4, valley),
        (cx, peak),
        (cx + w / 4, valley),
        (cx + w / 2, peak + (valley - peak) * 0.25),
        (cx + w / 2, base_y),
    ]
    if fill:
        d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=color, width=lw, joint="curve")
    r = w * 0.055
    for px, py in [(cx - w / 2, peak + (valley - peak) * 0.25), (cx, peak),
                   (cx + w / 2, peak + (valley - peak) * 0.25)]:
        d.ellipse([px - r, py - r * 1 - 0, px + r, py + r], fill=color)
    d.line([(cx - w / 2, base_y + lw * 1.6), (cx + w / 2, base_y + lw * 1.6)],
           fill=color, width=lw)


def dotted_rule(d, x0, y0, x1, y1, color, r, gap):
    length = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(length / gap))
    for i in range(n + 1):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)


def text_tracked(d, cx, y, txt, size, color, tracking=0.32, anchor="mm"):
    f = ImageFont.truetype(FONT_BOLD, size)
    widths = [d.textlength(ch, font=f) for ch in txt]
    tr = size * tracking
    total = sum(widths) + tr * (len(txt) - 1)
    x = cx - total / 2
    for ch, w in zip(txt, widths):
        d.text((x, y), ch, font=f, fill=color, anchor="lm")
        x += w + tr


def canvas(w, h, bg=TRANSP):
    img = Image.new("RGBA", (w * SS, h * SS), bg)
    return img, ImageDraw.Draw(img)


def finish(img, w, h, path):
    img = img.resize((w, h), Image.LANCZOS)
    img.save(path)
    print("ok", path, img.size)


# ---------------------------------------------------------------- diseños

def tee_front(path):
    """Medallón bandana 45° con corona central y anillo de 8 botehs."""
    W, H = 1800, 2400
    img, d = canvas(W, H)
    S = SS
    cx, cy = 900 * S, 1050 * S
    half = 780 * S
    # marco exterior: rombo (cuadrado a 45°) doble + puntos
    for k, lw in [(1.0, 10 * S), (0.94, 4 * S)]:
        pts = [(cx, cy - half * k), (cx + half * k, cy), (cx, cy + half * k),
               (cx - half * k, cy)]
        d.line(pts + [pts[0]], fill=FOREST, width=lw, joint="curve")
    ring = [(cx, cy - half * 0.97), (cx + half * 0.97, cy),
            (cx, cy + half * 0.97), (cx - half * 0.97, cy)]
    for i in range(4):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % 4]
        dotted_rule(d, x0, y0, x1, y1, RUST, 5 * S, 46 * S)
    # botehs en los 4 vértices del rombo, curvándose alrededor del centro
    for i, (bx, by, rot) in enumerate([
            (cx, cy - half * 0.62, 180), (cx + half * 0.62, cy, 90),
            (cx, cy + half * 0.62, 0), (cx - half * 0.62, cy, 270)]):
        draw_boteh(d, bx, by, 250 * S, rot=rot, flip=(i % 2 == 1),
                   line=FOREST, accent=RUST)
    # anillo interior de 6 botehs alrededor de la corona
    rad = half * 0.40
    for k in range(6):
        a = math.radians(60 * k - 90)
        bx, by = cx + math.cos(a) * rad * 1.02, cy + math.sin(a) * rad * 0.98
        if k in (0, 3):
            continue  # despeja arriba y abajo para los botehs de vértice
        draw_boteh(d, bx, by, 165 * S, rot=-math.degrees(a) - 90,
                   flip=(k % 2 == 0), line=FOREST, accent=RUST, dots=False)
    # corona central con doble círculo
    for rr, lw in [(255 * S, 10 * S), (228 * S, 4 * S)]:
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=FOREST, width=lw)
    dotted_rule_circle(d, cx, cy, 200 * S, RUST, 5 * S, 40 * S)
    draw_crown(d, cx, cy - 6 * S, 220 * S, FOREST)
    # wordmark
    text_tracked(d, cx, cy + half + 130 * S, "SRHOOD", 96 * S, FOREST, 0.42)
    text_tracked(d, cx, cy + half + 215 * S, "STREET ROYALTY EST. MMXXV",
                 30 * S, RUST, 0.38)
    finish(img, W, H, path)


def dotted_rule_circle(d, cx, cy, rad, color, r, gap):
    n = max(8, int(2 * math.pi * rad / gap))
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = cx + math.cos(a) * rad, cy + math.sin(a) * rad
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)


def ls_front(path):
    """Cascada vertical de botehs alternos + wordmark (print crema)."""
    W, H = 1800, 2400
    img, d = canvas(W, H)
    S = SS
    cx = 900 * S
    for i, y in enumerate([420, 1020, 1620]):
        flip = i % 2 == 1
        off = -150 if flip else 150
        draw_boteh(d, (cx / S + off) * S / 1, y * S, 340 * S,
                   rot=18 if flip else -18, flip=flip, line=CREMA, accent=RUST)
        sx = cx + (-330 * S if flip else 330 * S) * -1
        draw_boteh(d, sx, (y + 160) * S, 150 * S, rot=-35 if flip else 35,
                   flip=not flip, line=CREMA, accent=RUST, dots=False)
    dotted_rule(d, cx - 360 * S, 2085 * S, cx + 360 * S, 2085 * S, RUST,
                6 * S, 44 * S)
    text_tracked(d, cx, 2190 * S, "SRHOOD", 100 * S, CREMA, 0.46)
    text_tracked(d, cx, 2285 * S, "PAISLEY REAL", 38 * S, RUST, 0.5)
    finish(img, W, H, path)


def zip_front(path):
    """Banda horizontal de botehs para el pecho del zip hoodie (se parte en
    la cremallera): fila alterna entre dos reglas punteadas (print crema)."""
    W, H = 2250, 1500
    img, d = canvas(W, H)
    S = SS
    cy = 750 * S
    dotted_rule(d, 60 * S, cy - 330 * S, (W - 60) * S, cy - 330 * S, RUST,
                6 * S, 52 * S)
    dotted_rule(d, 60 * S, cy + 330 * S, (W - 60) * S, cy + 330 * S, RUST,
                6 * S, 52 * S)
    d.line([(40 * S, cy - 385 * S), ((W - 40) * S, cy - 385 * S)], fill=CREMA,
           width=8 * S)
    d.line([(40 * S, cy + 385 * S), ((W - 40) * S, cy + 385 * S)], fill=CREMA,
           width=8 * S)
    n = 6
    for k in range(n):
        x = (200 + k * (W - 400) / (n - 1)) * S
        up = k % 2 == 0
        draw_boteh(d, x, cy + (95 * S if up else -95 * S), 250 * S,
                   rot=0 if up else 180, flip=not up, line=CREMA, accent=RUST)
    finish(img, W, H, path)


def zip_back(path):
    """Boteh gigante con corona en el bulbo + arco de texto (print crema)."""
    W, H = 1800, 2400
    img, d = canvas(W, H)
    S = SS
    cx, cy = 860 * S, 1500 * S
    big = 1150 * S
    # boteh gigante: contorno + doble línea interior por offset de normales
    outer = transform(BOTEH, cx, cy, big, 0, False)
    d.line(outer + outer[:1], fill=CREMA, width=18 * S, joint="curve")
    for dist, lw in [(46 * S, 8 * S), (86 * S, 4 * S)]:
        o = offset_inward(outer, dist)
        d.line(o + o[:1], fill=CREMA, width=lw, joint="curve")
    # puntos rust entre las dos líneas interiores
    band = offset_inward(outer, 66 * S)
    for i in range(0, len(band), 9):
        x, y = band[i]
        d.ellipse([x - 8 * S, y - 8 * S, x + 8 * S, y + 8 * S], fill=RUST)
    # corona dentro del bulbo con anillo punteado
    bx, by = transform([BULB], cx, cy, big, 0, False)[0]
    dotted_rule_circle(d, bx, by, 175 * S, RUST, 6 * S, 48 * S)
    draw_crown(d, bx, by, 150 * S, CREMA, lw=10 * S)
    # botehs satélite
    for bx, by, sc, rot, fl in [(390, 620, 190, 205, False),
                                (1500, 900, 150, 150, True),
                                (1420, 1980, 170, 25, False)]:
        draw_boteh(d, bx * S, by * S, sc * S, rot=rot, flip=fl, line=CREMA,
                   accent=RUST, dots=False)
    text_tracked(d, 900 * S, 210 * S, "STREET ROYALTY", 66 * S, CREMA, 0.5)
    dotted_rule(d, 900 * S - 400 * S, 305 * S, 900 * S + 400 * S, 305 * S,
                RUST, 6 * S, 46 * S)
    finish(img, W, H, path)


def paisley_tile(w, h, bg, line, accent, scale, d=None, img=None):
    """Rellena el lienzo con paisley semi-caído (half-drop)."""
    if img is None:
        img, d = canvas(w, h, bg)
    S = SS
    sx = int(scale * S)
    stepx, stepy = int(sx * 1.55), int(sx * 1.9)
    row = 0
    y = -stepy // 2
    while y < h * S + stepy:
        x = -stepx // 2 + (stepx // 2 if row % 2 else 0)
        col = 0
        while x < w * S + stepx:
            rot = 26 if (row + col) % 2 == 0 else -26
            flip = (row + col) % 2 == 1
            draw_boteh(d, x, y, sx, rot=rot, flip=flip, line=line,
                       accent=accent, dots=(col + row) % 2 == 0)
            x += stepx
            col += 1
        y += stepy
        row += 1
    return img


def hitop_quarters(path):
    W = H = 2250
    img = paisley_tile(W, H, FOREST, CREMA, RUST, 300)
    finish(img, W, H, path)


def hitop_tongue(path):
    W = H = 2250
    img, d = canvas(W, H, FOREST)
    S = SS
    cx, cy = W * S // 2, H * S // 2
    for rr, lw in [(560 * S, 16 * S), (505 * S, 6 * S)]:
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=CREMA, width=lw)
    dotted_rule_circle(d, cx, cy, 450 * S, RUST, 9 * S, 70 * S)
    draw_crown(d, cx, cy - 60 * S, 420 * S, CREMA, lw=20 * S)
    text_tracked(d, cx, cy + 250 * S, "SRHOOD", 120 * S, CREMA, 0.4)
    # botehs esquineros
    for bx, by, rot, fl in [(320, 320, 135, False), (W - 320, 320, -135, True),
                            (320, H - 320, 45, True), (W - 320, H - 320, -45, False)]:
        draw_boteh(d, bx * S, by * S, 270 * S, rot=rot, flip=fl, line=CREMA,
                   accent=RUST, dots=False)
    finish(img, W, H, path)


def athletic_shoe(path):
    """Deportivas mujer: crema con scatter de botehs a línea forest."""
    W, H = 1950, 3300
    img = paisley_tile(W, H, CREMA, FOREST, RUST, 250)
    finish(img, W, H, path)


def bucket_out(path):
    W, H = 2700, 3150
    img = paisley_tile(W, H, CREMA, FOREST, RUST, 330)
    finish(img, W, H, path)


def bucket_in(path):
    """Interior: forest con botehs crema espaciados (lado reversible)."""
    W, H = 2700, 3150
    img, d = canvas(W, H, FOREST)
    S = SS
    step = 560 * S
    row = 0
    y = step // 2
    while y < H * S:
        x = step // 2 + (step // 2 if row % 2 else 0)
        while x < W * S:
            draw_boteh(d, x, y, 150 * S, rot=18 if row % 2 else -18,
                       flip=row % 2 == 1, line=CREMA, accent=RUST, dots=False)
            x += step
        y += step
        row += 1
    finish(img, W, H, path)


DESIGNS = {
    "tee_front": tee_front,
    "ls_front": ls_front,
    "zip_front": zip_front,
    "zip_back": zip_back,
    "hitop_quarters": hitop_quarters,
    "hitop_tongue": hitop_tongue,
    "athletic_shoe": athletic_shoe,
    "bucket_out": bucket_out,
    "bucket_in": bucket_in,
}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    preview = "--preview" in sys.argv
    outdir = args[0] if args else "."
    os.makedirs(outdir, exist_ok=True)
    global SS
    if preview:
        SS = 1
    for name, fn in DESIGNS.items():
        fn(os.path.join(outdir, f"paisley_{name}.png"))
    if preview:
        # hoja de contacto sobre fondos representativos
        cells = []
        bgmap = {
            "tee_front": (238, 232, 210), "ls_front": (74, 84, 62),
            "zip_front": (34, 66, 47), "zip_back": (34, 66, 47),
            "hitop_quarters": None, "hitop_tongue": None,
            "athletic_shoe": None, "bucket_out": None, "bucket_in": None,
        }
        for name in DESIGNS:
            im = Image.open(os.path.join(outdir, f"paisley_{name}.png"))
            im.thumbnail((520, 520))
            bg = bgmap.get(name)
            base = Image.new("RGB", (560, 560), bg or (200, 200, 200))
            base.paste(im, ((560 - im.width) // 2, (560 - im.height) // 2),
                       im if im.mode == "RGBA" else None)
            cells.append((name, base))
        sheet = Image.new("RGB", (560 * 3, 560 * 3 + 40), (255, 255, 255))
        dd = ImageDraw.Draw(sheet)
        f = ImageFont.truetype(FONT_BOLD, 22)
        for i, (name, cell) in enumerate(cells):
            x, y = (i % 3) * 560, (i // 3) * 560
            sheet.paste(cell, (x, y))
            dd.text((x + 8, y + 8), name, font=f, fill=(255, 60, 60))
        sheet.save(os.path.join(outdir, "contact_sheet.jpg"), quality=88)
        print("sheet", os.path.join(outdir, "contact_sheet.jpg"))


if __name__ == "__main__":
    main()
