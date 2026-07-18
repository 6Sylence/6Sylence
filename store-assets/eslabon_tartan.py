# -*- coding: utf-8 -*-
"""
SRHOOD — Cápsulas "Eslabón Real" (cadena de oro) y "Tartán Real" (heritage check).
Genera los print files para Printful (DTG + all-over print) en OUT_DIR.

Uso:  python3 eslabon_tartan.py [OUT_DIR]
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "./out"
os.makedirs(OUT, exist_ok=True)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def F(path, size):
    return ImageFont.truetype(path, int(size))


# ---------------------------------------------------------------- paleta
GOLD = (212, 175, 55)
GOLD_HI = (244, 221, 130)
GOLD_LO = (146, 112, 26)
GOLD_LINE = (40, 28, 6)
NEGRO = (10, 10, 13)
BURDEOS = (110, 26, 38)
NAVY = (26, 42, 74)
IVORY = (233, 225, 206)
K_HILO = (18, 16, 18)


# ---------------------------------------------------------------- helpers
def tracked(draw, xy, text, font, fill, tracking=0, stroke=0, stroke_fill=None):
    """Texto centrado en xy con tracking extra por carácter."""
    widths = [draw.textlength(c, font=font) + tracking for c in text]
    total = sum(widths) - tracking
    x = xy[0] - total / 2
    for c, w in zip(text, widths):
        draw.text((x, xy[1]), c, font=font, fill=fill, anchor="lm",
                  stroke_width=stroke, stroke_fill=stroke_fill)
        x += w


def arc_text(img, center, radius, text, font, fill, start_deg, end_deg, flip=False):
    """Texto sobre un arco entre start y end (grados, 0=este, CW pantalla)."""
    n = len(text)
    if n < 2:
        return
    for i, c in enumerate(text):
        ang = math.radians(start_deg + (end_deg - start_deg) * i / (n - 1))
        x = center[0] + radius * math.cos(ang)
        y = center[1] + radius * math.sin(ang)
        rot = -math.degrees(ang) - 90 if not flip else -math.degrees(ang) + 90
        size = font.size * 3
        tile = Image.new("RGBA", (int(size), int(size)), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        td.text((size / 2, size / 2), c, font=font, fill=fill, anchor="mm")
        tile = tile.rotate(rot, resample=Image.BICUBIC, center=(size / 2, size / 2))
        img.alpha_composite(tile, (int(x - size / 2), int(y - size / 2)))


def paste_rot(base, tile, cx, cy, angle_deg):
    tile = tile.rotate(angle_deg, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)))


# ---------------------------------------------------------------- cadena
def ring_img(rx, ry, thick, pal=None, ss=2):
    """Eslabón visto de frente: anillo con sombreado metálico (flat 3 tonos)."""
    pal = pal or {}
    base = pal.get("base", GOLD)
    hi = pal.get("hi", GOLD_HI)
    lo = pal.get("lo", GOLD_LO)
    line = pal.get("line", GOLD_LINE)
    W, H = (rx * 2 + thick * 2 + 16) * ss, (ry * 2 + thick * 2 + 16) * ss
    im = Image.new("RGBA", (int(W), int(H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = W / 2, H / 2
    box = [cx - rx * ss, cy - ry * ss, cx + rx * ss, cy + ry * ss]
    # contorno oscuro exterior + interior
    d.ellipse(box, outline=line, width=int((thick + 7) * ss))
    d.ellipse(box, outline=base, width=int(thick * ss))
    # brillo superior y sombra inferior
    d.arc(box, 195, 330, fill=hi, width=int(thick * 0.42 * ss))
    d.arc(box, 25, 150, fill=lo, width=int(thick * 0.45 * ss))
    return im.resize((int(W / ss), int(H / ss)), Image.LANCZOS)


def capsule_img(L, w, pal=None, ss=2):
    """Eslabón de canto: cápsula maciza (conector)."""
    pal = pal or {}
    base = pal.get("base", GOLD)
    hi = pal.get("hi", GOLD_HI)
    lo = pal.get("lo", GOLD_LO)
    line = pal.get("line", GOLD_LINE)
    W, H = (L + 16) * ss, (w + 16) * ss
    im = Image.new("RGBA", (int(W), int(H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = [8 * ss, (H - w * ss) / 2, W - 8 * ss, (H + w * ss) / 2]
    r = w * ss / 2
    d.rounded_rectangle(box, radius=r, fill=base, outline=line, width=int(3.5 * ss))
    # línea de brillo arriba / sombra abajo
    d.rounded_rectangle([box[0] + 6 * ss, box[1] + 4 * ss, box[2] - 6 * ss,
                         box[1] + w * ss * 0.34], radius=r * 0.5, fill=hi)
    d.rounded_rectangle([box[0] + 8 * ss, box[3] - w * ss * 0.26, box[2] - 8 * ss,
                         box[3] - 4 * ss], radius=r * 0.4, fill=lo)
    return im.resize((int(W / ss), int(H / ss)), Image.LANCZOS)


def resample_by_arclength(pts, step):
    """Puntos equiespaciados por longitud de arco sobre una polilínea."""
    out = [pts[0]]
    acc = 0.0
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        seg = math.hypot(x1 - x0, y1 - y0)
        while acc + seg >= step:
            t = (step - acc) / seg
            nx, ny = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            out.append((nx, ny))
            x0, y0 = nx, ny
            seg = math.hypot(x1 - x0, y1 - y0)
            acc = 0.0
        acc += seg
    return out


def chain_along(layer, path_pts, rx=72, ry=54, thick=30, pal=None):
    """Cadena clásica: anillos frontales alternados con conectores de canto."""
    step = rx * 1.62
    pts = resample_by_arclength(path_pts, step)
    ring = ring_img(rx, ry, thick, pal)
    caps = capsule_img(int(rx * 1.5), int(thick * 1.15), pal)
    # primero los conectores (quedan "debajo")
    for i in range(1, len(pts), 2):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[(i + 1) % len(pts)] if i + 1 < len(pts) else pts[i]
        ang = math.degrees(math.atan2(-(y1 - y0), x1 - x0))
        paste_rot(layer, caps, pts[i][0], pts[i][1], ang)
    for i in range(0, len(pts), 2):
        j0, j1 = max(i - 1, 0), min(i + 1, len(pts) - 1)
        x0, y0 = pts[j0]
        x1, y1 = pts[j1]
        ang = math.degrees(math.atan2(-(y1 - y0), x1 - x0))
        paste_rot(layer, ring, pts[i][0], pts[i][1], ang)


def circle_path(cx, cy, R, n=240, deg0=0, deg1=360):
    return [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))
            for a in np.linspace(deg0, deg1, n)]


# ---------------------------------------------------------------- corona
def crown_img(w, jewel=BURDEOS, pal=None, ss=2):
    """Corona real de 5 puntas con perlas y joyas, estilo serigrafía 3 tonos."""
    pal = pal or {}
    base = pal.get("base", GOLD)
    hi = pal.get("hi", GOLD_HI)
    lo = pal.get("lo", GOLD_LO)
    line = pal.get("line", GOLD_LINE)
    W = int(w * ss)
    H = int(w * 0.82 * ss)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bh = H * 0.24                      # alto banda
    by = H - bh - H * 0.04             # y banda
    margin = W * 0.06
    # puntas: 5, alternando altura, con curvas hacia la banda
    xs = np.linspace(margin, W - margin, 6)
    tip_h = [H * 0.52, H * 0.30, 0.16 * H, H * 0.30, H * 0.52]
    pts = [(margin, by)]
    for i in range(5):
        x0, x1 = xs[i], xs[i + 1]
        xm = (x0 + x1) / 2
        pts += [((x0 + xm) / 2, by - H * 0.10), (xm, tip_h[i] + H * 0.06)]
        pts += [((xm + x1) / 2, by - H * 0.10)]
    pts += [(W - margin, by)]
    d.polygon(pts, fill=base, outline=line)
    d.line(pts, fill=line, width=int(3 * ss), joint="curve")
    # perlas en las puntas
    for i in range(5):
        xm = (xs[i] + xs[i + 1]) / 2
        r = W * 0.035
        d.ellipse([xm - r, tip_h[i] - r + H * 0.02, xm + r, tip_h[i] + r + H * 0.02],
                  fill=hi, outline=line, width=int(2.5 * ss))
    # brillo lateral izquierdo del cuerpo
    d.polygon([(margin + W * 0.02, by), ((xs[0] + xs[1]) / 2, by - H * 0.12),
               (xs[0] * 0.9 + xs[1] * 0.1, tip_h[0] + H * 0.10),
               (margin + W * 0.05, by)], fill=hi)
    # banda
    d.rounded_rectangle([margin - W * 0.015, by, W - margin + W * 0.015, by + bh],
                        radius=bh * 0.32, fill=base, outline=line, width=int(3 * ss))
    d.rounded_rectangle([margin + W * 0.005, by + bh * 0.10, W - margin - W * 0.005,
                         by + bh * 0.34], radius=bh * 0.15, fill=hi)
    d.rounded_rectangle([margin + W * 0.01, by + bh * 0.72, W - margin - W * 0.01,
                         by + bh * 0.92], radius=bh * 0.12, fill=lo)
    # joyas (rombos) en la banda
    for fx in (0.25, 0.5, 0.75):
        cx = W * fx
        cy = by + bh * 0.5
        r = bh * 0.30
        d.polygon([(cx, cy - r), (cx + r * 0.8, cy), (cx, cy + r), (cx - r * 0.8, cy)],
                  fill=jewel, outline=line, width=int(2.5 * ss))
    return im.resize((int(W / ss), int(H / ss)), Image.LANCZOS)


# ---------------------------------------------------------------- tartán
TARTAN_SETT = [("R", 64), ("K", 7), ("G", 9), ("K", 7), ("R", 64),
               ("N", 46), ("I", 10), ("N", 46)]
TARTAN_COLORS = {"R": BURDEOS, "N": NAVY, "G": (198, 158, 58), "I": IVORY, "K": K_HILO}


def _thread_indices(total_px, px_per_thread):
    """color por hilo siguiendo el sett espejado."""
    seq = []
    for c, n in TARTAN_SETT:
        seq += [c] * n
    seq = seq + seq[::-1]           # sett simétrico
    n_threads = math.ceil(total_px / px_per_thread)
    idx = (np.arange(n_threads) % len(seq))
    colors = np.array([TARTAN_COLORS[seq[i]] for i in idx], dtype=np.float32)
    return np.repeat(colors, px_per_thread, axis=0)[:total_px]


def tartan_img(w, h, px_per_thread=3, seed=11):
    """Tartán tejido con sarga 2/2 y ruido de hilo."""
    warp = _thread_indices(w, px_per_thread)     # columnas
    weft = _thread_indices(h, px_per_thread)     # filas
    X = np.tile(warp[None, :, :], (h, 1, 1))
    Y = np.tile(weft[:, None, :], (1, w, 1))
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))
    twill = (((xx + yy) // (px_per_thread * 2)) % 2) == 0
    img = np.where(twill[:, :, None], X, Y)
    # sombreado sutil de sarga + ruido de hilo
    shade = 1.0 - 0.06 * (((xx + yy) // px_per_thread) % 2)
    img = img * shade[:, :, None]
    rng = np.random.default_rng(seed)
    img = img + rng.normal(0, 5.5, size=img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def fringe_strip(w, h, horizontal=True, seed=5):
    """Flecos de hilo para el borde de una banda de tartán."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(seed)
    cols = [BURDEOS, NAVY, IVORY, (198, 158, 58), K_HILO]
    if horizontal:                    # flecos que cuelgan hacia abajo
        x = 0
        while x < w:
            t = rng.randint(5, 9)
            ln = rng.randint(int(h * 0.55), h - 2)
            d.line([(x + t / 2, 0), (x + t / 2 + rng.randint(-4, 4), ln)],
                   fill=rng.choice(cols), width=t)
            x += t + rng.randint(2, 5)
    else:                             # flecos laterales
        y = 0
        while y < h:
            t = rng.randint(5, 9)
            ln = rng.randint(int(w * 0.55), w - 2)
            d.line([(0, y + t / 2), (ln, y + t / 2 + rng.randint(-4, 4))],
                   fill=rng.choice(cols), width=t)
            y += t + rng.randint(2, 5)
    return im


def gold_trim(w, h=18):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=GOLD)
    d.rectangle([0, 0, w, h * 0.33], fill=GOLD_HI)
    d.rectangle([0, h * 0.78, w, h], fill=GOLD_LO)
    return im


# ================================================================ ESLABÓN
def esl_tee():
    """Camiseta: círculo de cadena + corona colgante + lema."""
    W, H = 1800, 2400
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cy, R = W / 2, 1030, 640
    chain_along(im, circle_path(cx, cy, R, 300), rx=74, ry=56, thick=31)
    # cadenita vertical que conecta el aro con la corona colgante
    crw = crown_img(600)
    crown_top = cy - crw.height / 2 - 20
    chain_along(im, [(cx, cy - R + 10), (cx, crown_top + 40)], rx=34, ry=26, thick=15)
    im.alpha_composite(crw, (int(cx - crw.width / 2), int(crown_top)))
    d = ImageDraw.Draw(im)
    tracked(d, (cx, cy + 320), "SRHOOD", F(SANS_B, 92), GOLD, tracking=34)
    # tipografía inferior
    tracked(d, (cx, 1910), "ESLABÓN REAL", F(SERIF_B, 148), GOLD, tracking=16,
            stroke=4, stroke_fill=GOLD_LINE)
    tracked(d, (cx, 2050), "CADA ESLABÓN CUENTA", F(SANS, 60), (168, 137, 52),
            tracking=26)
    im.save(f"{OUT}/esl01_tee_front.png")


def esl_hoodie():
    """Hoodie premium: collar de cadena que cuelga del cuello con corona."""
    W, H = 1800, 1800
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # catenaria colgante: anclada arriba en los hombros, punto bajo en el centro
    a = 430.0
    x0, x1 = 235, W - 235
    cxm = W / 2
    y_anchor = -30.0                      # borde superior del área de impresión
    y0 = y_anchor + a * math.cosh((x0 - cxm) / a)
    pts = []
    for x in np.linspace(x0, x1, 400):
        y = y0 - a * math.cosh((x - cxm) / a)
        pts.append((x, y))
    low_y = y0 - a                        # punto más bajo (centro)
    chain_along(im, pts, rx=64, ry=48, thick=27)
    # bail solapado con la cadena + corona colgando
    bail = ring_img(30, 40, 16)
    im.alpha_composite(bail, (int(cxm - bail.width / 2), int(low_y - 12)))
    crw = crown_img(470)
    im.alpha_composite(crw, (int(cxm - crw.width / 2), int(low_y + 62)))
    d = ImageDraw.Draw(im)
    tracked(d, (cxm, low_y + 62 + 470 * 0.82 + 80), "SRHOOD", F(SANS_B, 74),
            GOLD, tracking=30)
    im.save(f"{OUT}/esl02_hoodie_front.png")


def esl_zip_back():
    """Zip hoodie (espalda): placa medallón colgada de dos cadenas."""
    W, H = 1800, 2400
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px, py = W / 2, 1310            # centro de la placa
    # dos cadenas desde los hombros hasta la placa
    for sx in (150, W - 150):
        pts = [(sx + (px - sx) * t, -40 + (py - 260 + 40) * t ** 1.12)
               for t in np.linspace(0, 1, 240)]
        chain_along(im, pts, rx=58, ry=44, thick=25)
    # placa
    d = ImageDraw.Draw(im)
    pw, ph = 900, 560
    box = [px - pw / 2, py - ph / 2, px + pw / 2, py + ph / 2]
    d.rounded_rectangle(box, radius=70, fill=NEGRO, outline=GOLD, width=16)
    d.rounded_rectangle([box[0] + 34, box[1] + 34, box[2] - 34, box[3] - 34],
                        radius=48, outline=GOLD_LO, width=6)
    crw = crown_img(300)
    im.alpha_composite(crw, (int(px - crw.width / 2), int(py - ph / 2 - 195)))
    d = ImageDraw.Draw(im)
    tracked(d, (px, py - 70), "SRHOOD", F(SERIF_B, 168), GOLD, tracking=18,
            stroke=3, stroke_fill=GOLD_LINE)
    tracked(d, (px, py + 78), "STREET ROYALTY HOOD", F(SANS, 56), (168, 137, 52),
            tracking=18)
    tracked(d, (px, py + 178), "EST. MMXXVI", F(SANS, 48), GOLD_LO, tracking=26)
    tracked(d, (px, py + ph / 2 + 150), "CADA ESLABÓN CUENTA", F(SANS_B, 64),
            GOLD, tracking=24)
    im.save(f"{OUT}/esl03_zip_back.png")


def esl_aop(w, h, name, rx=68, seed=3):
    """Patrón AOP: cadenas diagonales sobre negro con coronas ocultas."""
    im = Image.new("RGBA", (w, h), (*NEGRO, 255))
    diag = math.hypot(w, h)
    step_rows = int(rx * 4.6)
    n_rows = int(diag / step_rows) + 4
    rng = random.Random(seed)
    tiny_crown = crown_img(int(rx * 1.7))
    for k in range(-n_rows, n_rows):
        # línea a 45º: puntos desde fuera del lienzo
        off = k * step_rows
        p0 = (-diag / 2 + off, h + diag / 2 + off - (h - w) / 2)
        pts = [(p0[0] + t, p0[1] - t) for t in np.linspace(0, diag * 2, 200)]
        chain_along(im, pts, rx=rx, ry=int(rx * 0.75), thick=int(rx * 0.42))
        # coronas pequeñas entre filas
        for _ in range(max(1, int(diag / 1500))):
            t = rng.uniform(0.1, 0.9) * diag * 2
            cx = p0[0] + t + step_rows * 0.5 * rng.choice([-1, 1])
            cy = p0[1] - t + step_rows * 0.52 * rng.choice([-1, 1])
            if -tiny_crown.width < cx < w and -tiny_crown.height < cy < h:
                paste_rot(im, tiny_crown, cx, cy, rng.uniform(-24, 24))
    im.convert("RGB").save(f"{OUT}/{name}.jpg", quality=95)


def esl_socks():
    """Calcetines: cadena vertical + corona bajo el puño."""
    W, H = 1348, 5657
    im = Image.new("RGBA", (W, H), (*NEGRO, 255))
    crw = crown_img(560)
    im.alpha_composite(crw, (int(W / 2 - crw.width / 2), 260))
    pts = [(W / 2, 900), (W / 2, H)]
    chain_along(im, pts, rx=110, ry=84, thick=46)
    d = ImageDraw.Draw(im)
    # wordmark vertical junto a la cadena
    v = Image.new("RGBA", (900, 200), (0, 0, 0, 0))
    vd = ImageDraw.Draw(v)
    tracked(vd, (450, 100), "SRHOOD", F(SANS_B, 110), (168, 137, 52), tracking=44)
    v = v.rotate(90, expand=True)
    im.alpha_composite(v, (int(W / 2) - 480, 1500))
    im.convert("RGB").save(f"{OUT}/esl06_socks.jpg", quality=95)


# ================================================================ TARTÁN
def trt_tee():
    """Camiseta: escudo de tartán + corona + banner."""
    W, H = 1800, 2400
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # escudo
    sw, sh = 1150, 1290
    sx, sy = W / 2, 1120
    shield = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shield)
    pts = [(0, 0), (sw, 0), (sw, sh * 0.55)]
    # contorno de escudo clásico
    path = [(sw * 0.02, 0), (sw * 0.98, 0), (sw * 0.98, sh * 0.52)]
    n = 60
    for i in range(n + 1):
        t = i / n
        ang = math.pi * t
        x = sw * 0.98 - (sw * 0.48) * (1 - math.cos(ang)) / 1
        y = sh * 0.52 + math.sin(ang / 1) * sh * 0.46 * math.sin(min(t * 1.35, 1) * math.pi / 2)
    # más simple y robusto: polígono escudo
    path = [(sw * 0.03, sh * 0.02), (sw * 0.97, sh * 0.02), (sw * 0.97, sh * 0.50),
            (sw * 0.86, sh * 0.74), (sw * 0.5, sh * 0.98), (sw * 0.14, sh * 0.74),
            (sw * 0.03, sh * 0.50)]
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).polygon(path, fill=255)
    tar = tartan_img(sw, sh, px_per_thread=3, seed=21)
    shield.paste(tar, (0, 0), mask)
    # borde dorado doble
    sd.line(path + [path[0]], fill=GOLD, width=26, joint="curve")
    sd.line(path + [path[0]], fill=GOLD_LINE, width=6, joint="curve")
    inner = [(x * 0.94 + sw * 0.03, y * 0.94 + sh * 0.03) for x, y in path]
    sd.line(inner + [inner[0]], fill=GOLD_LO, width=8, joint="curve")
    im.alpha_composite(shield, (int(sx - sw / 2), int(sy - sh / 2)))
    # corona sobre el escudo
    crw = crown_img(520)
    im.alpha_composite(crw, (int(sx - crw.width / 2), int(sy - sh / 2 - 330)))
    # banner inferior
    d = ImageDraw.Draw(im)
    by = sy + sh / 2 + 105
    bw, bh = 1240, 190
    d.polygon([(sx - bw / 2, by - bh / 2), (sx + bw / 2, by - bh / 2),
               (sx + bw / 2 - 70, by), (sx + bw / 2, by + bh / 2),
               (sx - bw / 2, by + bh / 2), (sx - bw / 2 + 70, by)],
              fill=BURDEOS, outline=GOLD, width=12)
    tracked(d, (sx, by), "TARTÁN REAL", F(SERIF_B, 116), IVORY, tracking=14)
    tracked(d, (sx, by + 215), "SRHOOD — HERENCIA REAL", F(SANS, 54),
            (168, 137, 52), tracking=20)
    im.save(f"{OUT}/trt01_tee_front.png")


def trt_crewneck():
    """Sudadera granate: banda de tartán con flecos + medallón corona."""
    W, H = 1800, 2400
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    band_h = 560
    by = 760                        # banda a la altura del pecho
    tar = tartan_img(W, band_h, px_per_thread=3, seed=8)
    im.paste(tar, (0, by), Image.new("L", (W, band_h), 255))
    im.alpha_composite(gold_trim(W, 20), (0, by - 20))
    im.alpha_composite(gold_trim(W, 20), (0, by + band_h))
    im.alpha_composite(fringe_strip(W, 60, horizontal=True, seed=4), (0, by + band_h + 20))
    # medallón central
    d = ImageDraw.Draw(im)
    mc = (W / 2, by + band_h / 2)
    mr = 300
    d.ellipse([mc[0] - mr, mc[1] - mr, mc[0] + mr, mc[1] + mr], fill=NEGRO,
              outline=GOLD, width=18)
    d.ellipse([mc[0] - mr + 34, mc[1] - mr + 34, mc[0] + mr - 34, mc[1] + mr - 34],
              outline=GOLD_LO, width=6)
    crw = crown_img(330)
    im.alpha_composite(crw, (int(mc[0] - crw.width / 2), int(mc[1] - 215)))
    tracked(d, (mc[0], mc[1] + 130), "SRHOOD", F(SANS_B, 96), GOLD, tracking=24)
    tracked(d, (W / 2, by + band_h + 210), "TARTÁN REAL — MMXXVI", F(SANS, 56),
            (215, 190, 150), tracking=22)
    im.save(f"{OUT}/trt02_crew_front.png")


def trt_longsleeve():
    """Manga larga negra: banda diagonal (sash) de tartán con broche."""
    W, H = 1800, 2400
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # sash diagonal: banda grande rotada
    L = 3300
    bw = 430
    band = Image.new("RGBA", (L, bw + 80), (0, 0, 0, 0))
    tar = tartan_img(L, bw, px_per_thread=3, seed=31)
    band.paste(tar, (0, 40), Image.new("L", (L, bw), 255))
    band.alpha_composite(gold_trim(L, 18), (0, 22))
    band.alpha_composite(gold_trim(L, 18), (0, bw + 40))
    band = band.rotate(-38, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(band, (int(W / 2 - band.width / 2), int(1080 - band.height / 2)))
    # broche superior izquierdo (círculo dorado + corona)
    d = ImageDraw.Draw(im)
    bc = (410, 330)
    br = 210
    d.ellipse([bc[0] - br, bc[1] - br, bc[0] + br, bc[1] + br], fill=NEGRO,
              outline=GOLD, width=16)
    d.ellipse([bc[0] - br + 26, bc[1] - br + 26, bc[0] + br - 26, bc[1] + br - 26],
              outline=GOLD_LO, width=5)
    crw = crown_img(240)
    im.alpha_composite(crw, (int(bc[0] - crw.width / 2), int(bc[1] - 150)))
    tracked(d, (bc[0], bc[1] + 108), "SRH", F(SANS_B, 74), GOLD, tracking=18)
    tracked(d, (W / 2, 2170), "TARTÁN REAL", F(SERIF_B, 120), GOLD, tracking=16,
            stroke=3, stroke_fill=GOLD_LINE)
    im.save(f"{OUT}/trt03_ls_front.png")


def trt_aop(w, h, name, px_per_thread, seed=13):
    tartan_img(w, h, px_per_thread=px_per_thread, seed=seed).save(
        f"{OUT}/{name}.jpg", quality=95)


def trt_backpack():
    # cuerpo
    tartan_img(2175, 3075, px_per_thread=4, seed=17).save(
        f"{OUT}/trt06_bp_front.jpg", quality=95)
    tartan_img(4200, 1200, px_per_thread=4, seed=18).save(
        f"{OUT}/trt06_bp_top.jpg", quality=95)
    tartan_img(4200, 750, px_per_thread=4, seed=19).save(
        f"{OUT}/trt06_bp_bottom.jpg", quality=95)
    # bolsillo con emblema
    W, H = 1950, 1200
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.paste(tartan_img(W, H, px_per_thread=4, seed=20), (0, 0))
    d = ImageDraw.Draw(im)
    mc = (W / 2, H / 2)
    mr = 430
    d.ellipse([mc[0] - mr, mc[1] - mr, mc[0] + mr, mc[1] + mr], fill=NEGRO,
              outline=GOLD, width=20)
    arc_text(im, mc, mr - 96, "STREET ROYALTY HOOD", F(SANS_B, 74), GOLD, 200, 340)
    arc_text(im, mc, mr - 80, "TARTÁN REAL", F(SANS_B, 64), (168, 137, 52),
             155, 25, flip=True)
    crw = crown_img(300)
    im.alpha_composite(crw, (int(mc[0] - crw.width / 2), int(mc[1] - 175)))
    tracked(d, (mc[0], mc[1] + 145), "SRHOOD", F(SANS_B, 86), GOLD, tracking=22)
    im.convert("RGB").save(f"{OUT}/trt06_bp_pocket.jpg", quality=95)


if __name__ == "__main__":
    esl_tee()
    esl_hoodie()
    esl_zip_back()
    esl_aop(2250, 2250, "esl04_hightop", rx=66)
    esl_aop(1950, 3300, "esl05_athletic", rx=60, seed=7)
    esl_socks()
    trt_tee()
    trt_crewneck()
    trt_longsleeve()
    trt_aop(2250, 2250, "trt04_hightop", px_per_thread=3, seed=13)
    trt_aop(2325, 2325, "trt05_slipon", px_per_thread=2, seed=14)
    trt_backpack()
    print("OK ->", OUT)
