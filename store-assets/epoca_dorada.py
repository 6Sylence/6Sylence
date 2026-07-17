#!/usr/bin/env python3
"""Cápsula Déco — Época Dorada · SRHOOD
Genera los 6 archivos de impresión (Printful) de la cápsula Art Déco:
  1. deco_rayos.png        3600×4800  Camiseta (frente, fondo transparente)
  2. guilloche_real.png    3600×4800  Sudadera (frente, fondo transparente)
  3. abanico_deco.png      3600×4800  Hoodie   (frente, fondo transparente)
  4. plumaje_real.png      4500×4500  Zapatillas altas (patrón sin costuras)
  5. escama_deco.png       4650×4650  Slip-on  (patrón sin costuras)
  6. zigurat_deco.png      1400×2400  Calcetines (plantilla sublimación)
Todo se dibuja con supermuestreo 2× y se reduce con LANCZOS.
"""
import math
import os
import sys
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
SS = 2  # supersampling

# Paleta Época Dorada
GOLD_D, GOLD_M, GOLD_L = (122, 92, 24), (201, 153, 46), (247, 221, 143)
CREAM = (242, 232, 208, 255)
CREAM_RGB = (242, 232, 208)
NAVY = (22, 33, 62, 255)
NAVY_DEEP = (16, 26, 51, 255)
BURG = (110, 20, 35, 255)
BURG_L = (128, 28, 46, 255)
EMER = (18, 86, 63, 255)
INK_BG = (12, 18, 16, 255)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def gold_gradient(w, h):
    """Degradado metálico vertical con brillo sinusoidal y grano sutil."""
    img = Image.new("RGB", (w, h))
    px = img.load()
    rnd = random.Random(46)
    for y in range(h):
        t = y / max(h - 1, 1)
        s = 0.5 + 0.5 * math.sin(t * math.pi * 2.6 - 0.9)
        if t < 0.45:
            u = t / 0.45
            base = tuple(int(GOLD_D[i] + (GOLD_L[i] - GOLD_D[i]) * u) for i in range(3))
        else:
            u = (t - 0.45) / 0.55
            base = tuple(int(GOLD_L[i] + (GOLD_M[i] - GOLD_L[i]) * u) for i in range(3))
        base = tuple(min(255, int(c * (0.88 + 0.24 * s))) for c in base)
        for x in range(0, w, 4):
            n = rnd.randint(-6, 6)
            c = tuple(max(0, min(255, base[i] + n)) for i in range(3))
            for dx in range(4):
                if x + dx < w:
                    px[x + dx, y] = c
    return img


def paste_gold(canvas, mask):
    grad = gold_gradient(canvas.width, canvas.height)
    canvas.paste(grad, (0, 0), mask)


def tracked_text(draw, cx, cy, text, font, fill, tracking):
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for c, w in zip(text, widths):
        draw.text((x, cy), c, font=font, fill=fill, anchor="lm")
        x += w + tracking


def crown_polys(cx, cy, w, h):
    """Corona geométrica de tres puntas; devuelve (polígonos, círculos)."""
    base_h = h * 0.26
    tip_h = h - base_h
    half = w / 2
    polys = [
        [(cx - half, cy + h / 2 - base_h), (cx + half, cy + h / 2 - base_h),
         (cx + half, cy + h / 2), (cx - half, cy + h / 2)],
        [(cx - half, cy + h / 2 - base_h), (cx - half, cy - h / 2 + tip_h * 0.30),
         (cx - half * 0.42, cy + h / 2 - base_h)],
        [(cx - half * 0.36, cy + h / 2 - base_h), (cx, cy - h / 2),
         (cx + half * 0.36, cy + h / 2 - base_h)],
        [(cx + half, cy + h / 2 - base_h), (cx + half, cy - h / 2 + tip_h * 0.30),
         (cx + half * 0.42, cy + h / 2 - base_h)],
    ]
    r = w * 0.052
    circles = [(cx - half, cy - h / 2 + tip_h * 0.30, r), (cx, cy - h / 2, r),
               (cx + half, cy - h / 2 + tip_h * 0.30, r)]
    return polys, circles


def draw_crown(target, cx, cy, w, h):
    d = ImageDraw.Draw(target)
    polys, circles = crown_polys(cx, cy, w, h)
    for p in polys:
        d.polygon(p, fill=255 if target.mode == "L" else (255, 255, 255, 255))
    for x, y, r in circles:
        d.ellipse([x - r, y - r, x + r, y + r],
                  fill=255 if target.mode == "L" else (255, 255, 255, 255))


# ──────────────────────────────────────────────────────────────────────────
def camiseta_rayos():
    W, H = 3600 * SS, 4800 * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gold_mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    g = ImageDraw.Draw(gold_mask)

    cx, cy = W / 2, 1980 * SS
    R = 1060 * SS

    # Abanico de rayos: 22 cuñas alternas (oro / navy) en el semicírculo superior
    n = 22
    for i in range(n):
        a0 = 180 + i * (180 / n)
        a1 = a0 + (180 / n) - 1.6
        box = [cx - R, cy - R, cx + R, cy + R]
        if i % 2 == 0:
            g.pieslice(box, a0, a1, fill=255)
        else:
            d.pieslice(box, a0, a1, fill=NAVY)
    # recorte interior para convertir cuñas en anillo
    hole = 470 * SS
    d.ellipse([cx - hole, cy - hole, cx + hole, cy + hole], fill=(0, 0, 0, 0))
    g.ellipse([cx - hole, cy - hole, cx + hole, cy + hole], fill=0)

    # arcos finos de oro alrededor
    for rr, wd in ((R + 34 * SS, 7), (R + 66 * SS, 4)):
        g.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360, fill=255, width=wd * SS)
    # arco punteado exterior
    rr = R + 108 * SS
    for adeg in range(182, 359, 4):
        a = math.radians(adeg)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        r = 7 * SS
        g.ellipse([x - r, y - r, x + r, y + r], fill=255)
    # puntas: rombos de oro en cada frontera de cuña
    for i in range(n + 1):
        a = math.radians(180 + i * (180 / n))
        x, y = cx + (R + 8 * SS) * math.cos(a), cy + (R + 8 * SS) * math.sin(a)
        s = 13 * SS
        g.polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)], fill=255)

    # medallón central: burdeos con doble anillo de oro y corona
    r1 = 430 * SS
    d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=BURG)
    for rr, wd in ((r1 - 14 * SS, 8), (r1 - 52 * SS, 4)):
        g.arc([cx - rr, cy - rr, cx + rr, cy + rr], 0, 360, fill=255, width=wd * SS)
    draw_crown(gold_mask, cx, cy - 40 * SS, 380 * SS, 300 * SS)
    f_med = ImageFont.truetype(SANS, 66 * SS)
    tracked_text(ImageDraw.Draw(gold_mask), cx, cy + 250 * SS, "MMXXVI", f_med, 255, 26 * SS)

    # barras de horizonte escalonadas (con hueco central para el medallón)
    bars = [(690, 2010, 60, True), (850, 2120, 42, False), (1010, 2205, 30, True)]
    gap = 540 * SS
    for x0, y0, hgt, gold in bars:
        x0, y0, hgt = x0 * SS, y0 * SS, hgt * SS
        for rect in ([x0, y0, cx - gap, y0 + hgt], [cx + gap, y0, W - x0, y0 + hgt]):
            if gold:
                g.rectangle(rect, fill=255)
            else:
                d.rectangle(rect, fill=NAVY)
        s = hgt * 0.9
        for xe in (x0 - 30 * SS, W - x0 + 30 * SS, cx - gap + 30 * SS, cx + gap - 30 * SS):
            ye = y0 + hgt / 2
            g.polygon([(xe, ye - s), (xe + s, ye), (xe, ye + s), (xe - s, ye)], fill=255)

    # tipografía
    f_big = ImageFont.truetype(SERIF, 168 * SS)
    tmp = Image.new("L", (W, H), 0)
    tracked_text(ImageDraw.Draw(tmp), cx, 2580 * SS, "STREET ROYALTY", f_big, 255, 40 * SS)
    navy_layer = Image.new("RGBA", (W, H), NAVY)
    img.paste(navy_layer, (0, 0), tmp)
    f_small = ImageFont.truetype(SANS, 84 * SS)
    tracked_text(g, cx, 2780 * SS, "HOOD · ÉPOCA DORADA", f_small, 255, 30 * SS)

    paste_gold(img, gold_mask)
    img = img.resize((3600, 4800), Image.LANCZOS)
    img.save(os.path.join(OUT, "deco_rayos.png"))
    print("deco_rayos.png OK")


# ──────────────────────────────────────────────────────────────────────────
def sudadera_guilloche():
    W, H = 3600 * SS, 4800 * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gold_mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    g = ImageDraw.Draw(gold_mask)
    cx, cy = W / 2, 1980 * SS

    def ring(R0, A, nlobes, phase, width, gold=True):
        pts = []
        for k in range(1441):
            t = k / 1440 * 2 * math.pi
            rho = (R0 + A * math.sin(nlobes * t + phase)) * SS
            pts.append((cx + rho * math.cos(t), cy + rho * math.sin(t)))
        tgt = g if gold else d
        tgt.line(pts, fill=255 if gold else CREAM, width=width * SS, joint="curve")

    # rosetón guilloché entretejido
    ring(920, 85, 18, 0.0, 6, True)
    ring(920, -85, 18, 0.0, 6, True)
    ring(905, 60, 36, 0.4, 3, False)
    ring(795, 55, 24, 0.0, 4, True)
    ring(795, -55, 24, 0.6, 4, False)
    ring(690, 75, 12, 0.0, 5, True)
    ring(690, -75, 12, 0.5, 5, True)
    ring(600, 38, 30, 0.2, 3, False)

    # banda exterior grabada con marcas de reloj
    for rr, wd in ((1075, 8), (1108, 4)):
        rr *= SS
        g.arc([cx - rr, cy - rr, cx + rr, cy + rr], 0, 360, fill=255, width=wd * SS)
    for adeg in range(0, 360, 3):
        a = math.radians(adeg)
        r_in, r_out = 1082 * SS, (1101 if adeg % 15 else 1120) * SS
        g.line([cx + r_in * math.cos(a), cy + r_in * math.sin(a),
                cx + r_out * math.cos(a), cy + r_out * math.sin(a)], fill=255, width=3 * SS)

    # núcleo: anillo crema doble + corona de oro
    for rr, wd in ((470, 8), (430, 4)):
        rr *= SS
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 0, 360, fill=CREAM, width=wd * SS)
    disc = 400 * SS
    d.ellipse([cx - disc, cy - disc, cx + disc, cy + disc], fill=NAVY_DEEP)
    draw_crown(gold_mask, cx, cy - 45 * SS, 360 * SS, 285 * SS)
    f_srh = ImageFont.truetype(SERIF, 96 * SS)
    tmp = Image.new("L", (W, H), 0)
    tracked_text(ImageDraw.Draw(tmp), cx, cy + 210 * SS, "S · R · H", f_srh, 255, 18 * SS)
    cream_layer = Image.new("RGBA", (W, H), CREAM)
    img.paste(cream_layer, (0, 0), tmp)

    # rótulo inferior con filetes
    yt = 3360 * SS
    f_word = ImageFont.truetype(SERIF, 132 * SS)
    tmp2 = Image.new("L", (W, H), 0)
    tracked_text(ImageDraw.Draw(tmp2), cx, yt, "STREET ROYALTY HOOD", f_word, 255, 34 * SS)
    img.paste(cream_layer, (0, 0), tmp2)
    for dy in (-135, 135):
        g.rectangle([620 * SS, yt + dy * SS - 3 * SS, W - 620 * SS, yt + dy * SS + 3 * SS], fill=255)
    for xe in (440 * SS, W - 440 * SS):
        s = 26 * SS
        g.polygon([(xe, yt - s), (xe + s, yt), (xe, yt + s), (xe - s, yt)], fill=255)

    paste_gold(img, gold_mask)
    img = img.resize((3600, 4800), Image.LANCZOS)
    img.save(os.path.join(OUT, "guilloche_real.png"))
    print("guilloche_real.png OK")


# ──────────────────────────────────────────────────────────────────────────
def hoodie_abanico():
    W, H = 3600 * SS, 4800 * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gold_mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    g = ImageDraw.Draw(gold_mask)
    cx, cy = W / 2, 2260 * SS

    def fan(fx, fy, r_in, r_out, a0, a1, blades, style="full"):
        """Abanico de láminas alternas oro / crema / burdeos."""
        step = (a1 - a0) / blades
        for i in range(blades):
            b0 = a0 + i * step + 1.2
            b1 = a0 + (i + 1) * step - 1.2
            box = [fx - r_out, fy - r_out, fx + r_out, fy + r_out]
            if style == "line":
                g.arc(box, b0, b1, fill=255, width=4 * SS)
                for ang in (b0, b1):
                    a = math.radians(ang)
                    g.line([fx + r_in * math.cos(a), fy + r_in * math.sin(a),
                            fx + r_out * math.cos(a), fy + r_out * math.sin(a)],
                           fill=255, width=4 * SS)
                continue
            if i % 3 == 0:
                g.pieslice(box, b0, b1, fill=255)
            elif i % 3 == 1:
                d.pieslice(box, b0, b1, fill=CREAM)
            else:
                d.pieslice(box, b0, b1, fill=BURG_L)
            # punta redondeada
            am = math.radians((b0 + b1) / 2)
            tx, ty = fx + (r_out + 34 * SS) * math.cos(am), fy + (r_out + 34 * SS) * math.sin(am)
            rr = 26 * SS
            if i % 3 == 0:
                g.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=255)
            else:
                d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr],
                          fill=CREAM if i % 3 == 1 else BURG_L)
        # recorte interior
        d.pieslice([fx - r_in, fy - r_in, fx + r_in, fy + r_in], a0 - 2, a1 + 2, fill=(0, 0, 0, 0))
        g.pieslice([fx - r_in, fy - r_in, fx + r_in, fy + r_in], a0 - 2, a1 + 2, fill=0)

    # abanicos laterales en línea (detrás)
    fan(cx - 960 * SS, cy + 240 * SS, 220 * SS, 580 * SS, 200, 320, 7, style="line")
    fan(cx + 960 * SS, cy + 240 * SS, 220 * SS, 580 * SS, 220, 340, 7, style="line")
    # abanico central
    fan(cx, cy, 320 * SS, 1150 * SS, 195, 345, 15)

    # arco punteado sobre el abanico
    rr = 1290 * SS
    for adeg in range(197, 344, 3):
        a = math.radians(adeg)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        r = 8 * SS
        g.ellipse([x - r, y - r, x + r, y + r], fill=255)

    # pivote: medallón burdeos con corona
    r1 = 250 * SS
    d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=BURG)
    rr2 = r1 - 12 * SS
    g.arc([cx - rr2, cy - rr2, cx + rr2, cy + rr2], 0, 360, fill=255, width=6 * SS)
    draw_crown(gold_mask, cx, cy - 10 * SS, 230 * SS, 180 * SS)

    # barras y rótulo
    y0 = cy + 330 * SS
    g.rectangle([980 * SS, y0, W - 980 * SS, y0 + 14 * SS], fill=255)
    f_word = ImageFont.truetype(SERIF, 138 * SS)
    tmp = Image.new("L", (W, H), 0)
    tracked_text(ImageDraw.Draw(tmp), cx, y0 + 160 * SS, "STREET ROYALTY", f_word, 255, 36 * SS)
    cream_layer = Image.new("RGBA", (W, H), CREAM)
    img.paste(cream_layer, (0, 0), tmp)
    f_small = ImageFont.truetype(SANS, 76 * SS)
    tracked_text(g, cx, y0 + 330 * SS, "CÁPSULA DÉCO", f_small, 255, 42 * SS)

    paste_gold(img, gold_mask)
    img = img.resize((3600, 4800), Image.LANCZOS)
    img.save(os.path.join(OUT, "abanico_deco.png"))
    print("abanico_deco.png OK")


# ──────────────────────────────────────────────────────────────────────────
def wrapped(draw_fn, W, H):
    """Ejecuta draw_fn(dx, dy) en 9 offsets para patrón sin costuras."""
    for dx in (-W, 0, W):
        for dy in (-H, 0, H):
            draw_fn(dx, dy)


def zapatillas_plumaje():
    Wf = 4500
    W = H = Wf * SS
    img = Image.new("RGB", (W, H), INK_BG[:3])
    gold_mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    g = ImageDraw.Draw(gold_mask)

    cols, rows = 6, 5
    cw, ch = W / cols, H / rows

    def eye(cx, cy, scale, accent_burg):
        """Ojo de pluma de pavo real geométrico (déco)."""
        h = 340 * SS * scale
        w = 250 * SS * scale
        # barbas: trazos radiales cortos alrededor del arco superior
        for adeg in range(-215, 36, 10):
            a = math.radians(adeg)
            r0, r1 = h * 0.72, h * 0.98 if adeg % 20 else h * 1.12
            g.line([cx + r0 * math.cos(a), cy + r0 * math.sin(a),
                    cx + r1 * math.cos(a), cy + r1 * math.sin(a)], fill=255, width=5 * SS)
        # lágrima exterior (esmeralda) — polígono suavizado
        pts = []
        for k in range(73):
            t = k / 72 * 2 * math.pi
            rho = 1 / (1 + 0.28 * math.sin(t))  # forma de gota
            pts.append((cx + w * 0.62 * rho * math.sin(t) * 1.05,
                        cy - h * 0.60 * rho * math.cos(t)))
        d.polygon(pts, fill=EMER[:3])
        # contorno oro
        g.line(pts + [pts[0]], fill=255, width=6 * SS, joint="curve")
        # óvalo interior
        ow, oh = w * 0.42, h * 0.40
        inner = (27, 42, 74) if not accent_burg else BURG_L[:3]
        d.ellipse([cx - ow, cy - oh * 0.72, cx + ow, cy + oh * 1.05], fill=inner)
        # iris de oro + punto crema
        r2w, r2h = w * 0.22, h * 0.20
        g.ellipse([cx - r2w, cy - r2h * 0.55, cx + r2w, cy + r2h * 1.10], fill=255)
        r3 = w * 0.10
        d.ellipse([cx - r3, cy - r3 * 0.4, cx + r3, cy + r3 * 1.2], fill=CREAM_RGB)

    def cell(dx, dy):
        for j in range(rows):
            for i in range(cols):
                cx = (i + 0.5) * cw + (cw / 2 if j % 2 else 0) + dx
                cy = (j + 0.5) * ch + dy
                eye(cx, cy, 1.0 if (i + j) % 2 == 0 else 0.82, (i * 3 + j * 5) % 4 == 0)
        # puntos de oro en las esquinas de celda
        for j in range(rows):
            for i in range(cols):
                px_, py_ = i * cw + dx, j * ch + dy
                r = 9 * SS
                g.ellipse([px_ - r, py_ - r, px_ + r, py_ + r], fill=255)

    wrapped(cell, W, H)
    paste_gold(img, gold_mask)
    img = img.resize((Wf, Wf), Image.LANCZOS)
    img.save(os.path.join(OUT, "plumaje_real.png"))
    print("plumaje_real.png OK")


# ──────────────────────────────────────────────────────────────────────────
def slipon_escama():
    Wf = 4650
    W = H = Wf * SS
    BGC = (244, 236, 217)
    img = Image.new("RGB", (W, H), BGC)
    gold_mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    g = ImageDraw.Draw(gold_mask)

    cols = 6
    sw = W / cols          # ancho de escama
    R = sw / 2
    rows = 12
    rh = H / rows          # espaciado vertical = R → las cúpulas encajan sin huecos

    def scale_at(cx, cy, kind):
        box = [cx - R, cy - R, cx + R, cy + R]
        if kind == "burg":
            d.pieslice(box, 180, 360, fill=BURG[:3])
            ray_col, ray_gold = CREAM_RGB, False
        elif kind == "navy":
            d.pieslice(box, 180, 360, fill=NAVY[:3])
            ray_col, ray_gold = CREAM_RGB, False
        elif kind == "alt":
            d.pieslice(box, 180, 360, fill=(238, 227, 201))
            ray_col, ray_gold = None, True
        else:
            d.pieslice(box, 180, 360, fill=BGC)
            ray_col, ray_gold = None, True
        # abanico de radios
        for adeg in range(200, 341, 20):
            a = math.radians(adeg)
            x1, y1 = cx + (R * 0.94) * math.cos(a), cy + (R * 0.94) * math.sin(a)
            if ray_gold:
                g.line([cx, cy, x1, y1], fill=255, width=5 * SS)
            else:
                d.line([cx, cy, x1, y1], fill=ray_col, width=5 * SS)
        # doble contorno de oro
        g.arc(box, 180, 360, fill=255, width=9 * SS)
        rr = R - 26 * SS
        g.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360, fill=255, width=4 * SS)
        # perla en el vértice
        r = 11 * SS
        g.ellipse([cx - r, cy - r * 0.2, cx + r, cy + r * 1.8], fill=255)

    def kind_for(i, j):
        k = (i * 7 + j * 3) % 12
        if k == 0:
            return "burg"
        if k == 5:
            return "navy"
        if k in (2, 8):
            return "alt"
        return "base"

    def cell(dx, dy):
        for j in range(-1, rows + 1):    # filas de arriba a abajo, las bajas solapan
            off = (sw / 2) if j % 2 else 0
            for i in range(-1, cols + 1):
                cx = i * sw + sw / 2 + off + dx
                cy = j * rh + dy
                scale_at(cx, cy, kind_for(i % cols, j % rows))

    # patrón (dibujado con envoltura manual: filas y columnas extra ya cubren bordes)
    cell(0, 0)
    paste_gold(img, gold_mask)
    img = img.resize((Wf, Wf), Image.LANCZOS)
    img.save(os.path.join(OUT, "escama_deco.png"))
    print("escama_deco.png OK")


# ──────────────────────────────────────────────────────────────────────────
def calcetines_zigurat():
    Wf, Hf = 1400, 2400
    W, H = Wf * SS, Hf * SS
    BGC = (21, 33, 60)
    img = Image.new("RGB", (W, H), BGC)
    gold_mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    g = ImageDraw.Draw(gold_mask)

    period = 350 * SS
    unit = 400 * SS

    def zigurat_line(y_base, amp, thickness, target, color):
        """Zigzag escalonado (perfil de zigurat) que cruza todo el ancho."""
        pts = []
        steps = 4
        for x0 in range(-period, W + period, period):
            for s in range(steps + 1):
                xx = x0 + (s / steps) * (period / 2)
                yy = y_base - (s / steps) * amp
                pts.append((xx, yy))
                if s < steps:
                    pts.append((x0 + ((s + 1) / steps) * (period / 2), yy))
            for s in range(steps + 1):
                xx = x0 + period / 2 + (s / steps) * (period / 2)
                yy = y_base - amp + (s / steps) * amp
                pts.append((xx, yy))
                if s < steps:
                    pts.append((x0 + period / 2 + ((s + 1) / steps) * (period / 2), yy))
        if target == "gold":
            g.line(pts, fill=255, width=thickness)
        else:
            d.line(pts, fill=color, width=thickness)

    for yb in range(0, H + unit, unit):
        zigurat_line(yb + 260 * SS, 150 * SS, 26 * SS, "gold", None)
        zigurat_line(yb + 300 * SS, 150 * SS, 10 * SS, "col", CREAM_RGB)
        zigurat_line(yb + 345 * SS, 150 * SS, 16 * SS, "col", BURG_L[:3])
        # fila de rombos entre bandas
        for x in range(0, W, 175 * SS):
            yy = yb + 40 * SS
            s = 16 * SS
            g.polygon([(x, yy - s), (x + s, yy), (x, yy + s), (x - s, yy)], fill=255)
            s2 = 7 * SS
            xx = x + 87 * SS
            d.polygon([(xx, yy - s2), (xx + s2, yy), (xx, yy + s2), (xx - s2, yy)],
                      fill=CREAM_RGB)

    paste_gold(img, gold_mask)
    img = img.resize((Wf, Hf), Image.LANCZOS)
    img.save(os.path.join(OUT, "zigurat_deco.png"))
    print("zigurat_deco.png OK")


if __name__ == "__main__":
    camiseta_rayos()
    sudadera_guilloche()
    hoodie_abanico()
    zapatillas_plumaje()
    slipon_escama()
    calcetines_zigurat()
