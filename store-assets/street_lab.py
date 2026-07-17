#!/usr/bin/env python3
"""
Street Lab — Serie Gráfica (run 2026-07-17)
Genera los 6 print files de la cápsula, cada uno con un patrón inédito en la tienda:

  1. onda_optica.png   3600x4800 RGBA  — camiseta (DTG front): op-art de líneas con lente esférica
  2. oro_roto.png      3600x4800 RGBA  — sudadera (DTG front): kintsugi, vetas de oro
  3. topografia.png    3600x4800 RGBA  — hoodie (DTG front): curvas de nivel tonales
  4. vitral.png        2250x2250 RGB   — zapatillas altas mujer (cut&sew): vidriera Voronoi
  5. mosaico.png       2325x2325 RGB   — slip-on hombre (cut&sew): azulejo geométrico cobalto
  6. domino.png        1400x2400 RGB   — calcetines (sublimación): fichas de dominó

Uso:  python3 street_lab.py <output_dir>
"""
import math
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

SS = 2  # supersampling


def font(path, size):
    return ImageFont.truetype(path, size)


def tracked_text(draw, xy, text, fnt, fill, tracking=0.35, anchor="mm"):
    """Texto con espaciado entre letras (tracking relativo al tamaño de fuente)."""
    sizes = [draw.textlength(c, font=fnt) for c in text]
    gap = fnt.size * tracking
    total = sum(sizes) + gap * (len(text) - 1)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    cur = x
    for c, w in zip(text, sizes):
        draw.text((cur, y), c, font=fnt, fill=fill, anchor="l" + anchor[1])
        cur += w + gap


# ----------------------------------------------------------------------------
# 1. ONDA ÓPTICA — camiseta
# ----------------------------------------------------------------------------
def onda_optica(W=3600, H=4800):
    w, h = W * SS, H * SS
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    side = int(w * 0.86)
    x0 = (w - side) // 2
    y0 = int(h * 0.08)
    cx, cy = x0 + side / 2, y0 + side / 2
    R = side * 0.36          # radio de la "lente"
    K = 0.55                 # fuerza de la deformación

    n_lines = 52
    step = side / (n_lines - 1)
    for i in range(n_lines):
        ly = y0 + i * step
        pts = []
        widths = []
        for xi in range(0, side + 1, 6 * SS):
            px = x0 + xi
            dx, dy = px - cx, ly - cy
            r = math.hypot(dx, dy)
            if r < R and r > 1e-6:
                # expansión radial suave: burbuja esférica
                f = 1 + K * math.cos(r / R * math.pi / 2) ** 2
                py = cy + dy * f
                bulge = math.cos(r / R * math.pi / 2) ** 2
            else:
                py = ly
                bulge = 0.0
            pts.append((px, py))
            widths.append(bulge)
        # trazo por segmentos con grosor variable (más grueso dentro de la lente)
        base_w = int(step * 0.30)
        for a, b, bg in zip(pts[:-1], pts[1:], widths):
            lw = max(2, int(base_w * (1 + 0.9 * bg)))
            d.line([a, b], fill=(255, 255, 255, 255), width=lw)

    # rótulos
    f_big = font(FONT_BOLD, int(w * 0.052))
    f_sm = font(FONT_BOLD, int(w * 0.020))
    ty = y0 + side + int(h * 0.055)
    tracked_text(d, (w / 2, ty), "ONDA ÓPTICA", f_big, (255, 255, 255, 255), 0.42)
    tracked_text(d, (w / 2, ty + int(w * 0.062)), "STREET ROYALTY HOOD · MMXXVI",
                 f_sm, (255, 255, 255, 230), 0.55)
    return img.resize((W, H), Image.LANCZOS)


# ----------------------------------------------------------------------------
# 2. ORO ROTO — sudadera (kintsugi)
# ----------------------------------------------------------------------------
def oro_roto(W=3600, H=4800, seed=47):
    rng = random.Random(seed)
    w, h = W * SS, H * SS
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def draw_tapered(pts, w_start, w_end, color):
        n = len(pts) - 1
        for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
            lw = max(2, int(w_start + (w_end - w_start) * i / n))
            d.line([a, b], fill=color, width=lw)
            r = lw / 2
            d.ellipse([b[0] - r, b[1] - r, b[0] + r, b[1] + r], fill=color)

    def crack_path(x, y, heading, length, jag=0.55):
        """Grieta dentada: rumbo con reversión a la media y quiebros secos."""
        pts = [(x, y)]
        base = heading
        travelled = 0.0
        while travelled < length:
            step = rng.uniform(0.035, 0.075) * w
            if rng.random() < 0.30:
                heading += rng.choice([-1, 1]) * rng.uniform(0.35, jag)   # quiebro
            heading += (base - heading) * 0.35 + rng.uniform(-0.12, 0.12)
            x += step * math.cos(heading)
            y += step * math.sin(heading)
            pts.append((x, y))
            travelled += step
        return pts

    GOLD_DEEP = (122, 90, 28, 255)
    GOLD_MID = (204, 164, 44, 255)
    GOLD_HI = (246, 216, 110, 255)

    mains = [
        crack_path(w * 0.06, h * 0.10, math.radians(38), w * 1.05),
        crack_path(w * 0.94, h * 0.02, math.radians(128), w * 0.95),
        crack_path(w * 0.14, h * 0.72, math.radians(-18), w * 0.85),
    ]
    branches = []
    for pts in mains:
        for _ in range(rng.randint(2, 3)):
            i = rng.randint(len(pts) // 4, 3 * len(pts) // 4)
            bx, by = pts[i]
            ang = math.atan2(pts[i + 1][1] - by, pts[i + 1][0] - bx)
            ang += rng.choice([-1, 1]) * rng.uniform(0.6, 1.2)
            branches.append(crack_path(bx, by, ang, w * rng.uniform(0.18, 0.35)))

    for pts in mains:
        base_w = w * rng.uniform(0.011, 0.014)
        draw_tapered(pts, base_w, base_w * 0.25, GOLD_DEEP)
        draw_tapered(pts, base_w * 0.62, base_w * 0.16, GOLD_MID)
        draw_tapered(pts, base_w * 0.30, base_w * 0.08, GOLD_HI)
    for pts in branches:
        base_w = w * 0.006
        draw_tapered(pts, base_w, base_w * 0.2, GOLD_MID)
        draw_tapered(pts, base_w * 0.5, base_w * 0.12, GOLD_HI)

    # motas de oro dispersas junto a las vetas
    for pts in mains + branches:
        for p in pts[::2]:
            if rng.random() < 0.30:
                r = rng.uniform(2.5, 6.5) * SS
                ox, oy = rng.uniform(-40, 40) * SS, rng.uniform(-40, 40) * SS
                d.ellipse([p[0] + ox - r, p[1] + oy - r, p[0] + ox + r, p[1] + oy + r],
                          fill=(228, 192, 80, 255))

    f_big = font(FONT_BOLD, int(w * 0.056))
    f_sm = font(FONT_BOLD, int(w * 0.020))
    tracked_text(d, (w / 2, h * 0.875), "ORO ROTO", f_big, (240, 210, 100, 255), 0.45)
    tracked_text(d, (w / 2, h * 0.875 + w * 0.066), "DE LAS GRIETAS NACE EL ORO — SRH",
                 f_sm, (240, 210, 100, 235), 0.42)
    return img.resize((W, H), Image.LANCZOS)


# ----------------------------------------------------------------------------
# 3. TOPOGRAFÍA DEL BARRIO — hoodie
# ----------------------------------------------------------------------------
def topografia(W=3600, H=4800, seed=7):
    rng = np.random.default_rng(seed)
    w, h = W, H  # el campo se calcula a resolución final (las bandas ya salen suaves)

    # ruido de valor: rejilla aleatoria reescalada en bicúbico
    field = np.zeros((h, w), dtype=np.float32)
    for cells, amp in [(5, 1.0), (11, 0.45), (23, 0.18)]:
        g = rng.random((cells, int(cells * w / h) + 1), dtype=np.float32)
        layer = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        field += np.asarray(layer, dtype=np.float32) / 255.0 * amp
    field /= field.max()

    levels = 22
    a = (field * levels) % 1.0
    # línea donde la fase cruza 0 (banda fina); anchura constante vía gradiente
    gy, gx = np.gradient(field * levels)
    grad = np.hypot(gx, gy) + 1e-6
    dist = np.minimum(a, 1.0 - a) / grad          # distancia en píxeles a la isolínea
    line = np.clip(1.6 - dist, 0.0, 1.0)          # antialias ~3px

    idx = (field * levels).astype(int)
    major = (idx % 5 == 0)

    alpha = (line * 255).astype(np.uint8)
    rgb = np.zeros((h, w, 4), dtype=np.uint8)
    rgb[..., 0] = np.where(major, 255, 128)
    rgb[..., 1] = np.where(major, 255, 128)
    rgb[..., 2] = np.where(major, 255, 128)
    rgb[..., 3] = np.where(major, alpha, (alpha * 0.78).astype(np.uint8))

    img = Image.fromarray(rgb, "RGBA")

    # máscara circular con anillo exterior
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    R = int(w * 0.44)
    cx, cy = w // 2, int(h * 0.40)
    md.ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    img.putalpha(Image.composite(img.getchannel("A"), Image.new("L", (w, h), 0), mask))

    d = ImageDraw.Draw(img)
    ring_w = int(w * 0.006)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 255, 255, 255), width=ring_w)

    # marca de posición (aspa) en un "pico"
    px, py = int(cx + R * 0.28), int(cy - R * 0.30)
    s = int(w * 0.018)
    for sgn in (1, -1):
        d.line([px - s, py - sgn * s, px + s, py + sgn * s], fill=(255, 255, 255, 255),
               width=int(w * 0.005))

    f_big = font(FONT_BOLD, int(w * 0.050))
    f_sm = font(FONT_MONO, int(w * 0.021))
    ty = cy + R + int(h * 0.045)
    tracked_text(d, (w / 2, ty), "TOPOGRAFÍA", f_big, (255, 255, 255, 255), 0.40)
    tracked_text(d, (w / 2, ty + int(w * 0.062)), "DEL BARRIO A LA CIMA — SRH",
                 f_sm, (255, 255, 255, 235), 0.35)
    return img


# ----------------------------------------------------------------------------
# 4. VITRAL — zapatillas altas (Voronoi vidriera)
# ----------------------------------------------------------------------------
def vitral(size=2250, seed=23, n_seeds=150):
    rng = np.random.default_rng(seed)
    pts = rng.random((n_seeds, 2), dtype=np.float32) * size
    palette = np.array([
        (20, 65, 143),    # cobalto
        (13, 106, 90),    # esmeralda
        (146, 27, 48),    # rubí
        (216, 158, 42),   # ámbar
        (76, 42, 122),    # violeta
        (22, 122, 138),   # teal
        (238, 232, 218),  # pane claro
        (20, 65, 143),    # cobalto (peso extra)
        (13, 106, 90),
    ], dtype=np.float32)
    cell_color = palette[rng.integers(0, len(palette), n_seeds)]
    cell_color *= rng.uniform(0.82, 1.12, (n_seeds, 1)).astype(np.float32)

    out = np.zeros((size, size, 3), dtype=np.uint8)
    xs = np.arange(size, dtype=np.float32)
    chunk = 150
    for y0 in range(0, size, chunk):
        y1 = min(size, y0 + chunk)
        yy = np.arange(y0, y1, dtype=np.float32)[:, None, None]
        xx = xs[None, :, None]
        dx = xx - pts[None, None, :, 0]
        dy = yy - pts[None, None, :, 1]
        d2 = dx * dx + dy * dy
        order = np.argsort(d2, axis=2)[:, :, :2]
        i1 = order[..., 0]
        d1 = np.take_along_axis(d2, order[..., 0:1], 2)[..., 0]
        dsec = np.take_along_axis(d2, order[..., 1:2], 2)[..., 0]
        edge = (np.sqrt(dsec) - np.sqrt(d1)) < 7.0          # emplomado
        shade = 0.80 + 0.45 * np.exp(-np.sqrt(d1) / (size * 0.09))
        col = cell_color[i1] * shade[..., None]
        col = np.clip(col, 0, 255)
        col[edge] = (24, 22, 20)
        out[y0:y1] = col.astype(np.uint8)

    img = Image.fromarray(out, "RGB").filter(ImageFilter.GaussianBlur(0.6))
    return img


# ----------------------------------------------------------------------------
# 5. MOSAICO — slip-on (azulejo cobalto)
# ----------------------------------------------------------------------------
def mosaico(size=2325, tiles=5):
    COBALT = (20, 62, 138)
    AZURE = (128, 165, 214)
    BONE = (246, 243, 236)
    t = size // tiles
    w = t * SS
    tile_a = Image.new("RGB", (w, w), BONE)
    d = ImageDraw.Draw(tile_a)
    c = w / 2

    def star(draw, cx, cy, r_out, r_in, points, fill, rot=0.0):
        pts = []
        for i in range(points * 2):
            ang = rot + math.pi * i / points
            r = r_out if i % 2 == 0 else r_in
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        draw.polygon(pts, fill=fill)

    # tile A: estrella de 8 puntas
    d.rectangle([0, 0, w - 1, w - 1], outline=COBALT, width=int(w * 0.012))
    star(d, c, c, w * 0.44, w * 0.19, 8, COBALT, rot=math.pi / 8)
    star(d, c, c, w * 0.20, w * 0.088, 8, BONE, rot=math.pi / 8)
    d.ellipse([c - w * 0.052, c - w * 0.052, c + w * 0.052, c + w * 0.052], fill=AZURE)
    for corner in [(0, 0), (w, 0), (0, w), (w, w)]:
        d.ellipse([corner[0] - w * 0.14, corner[1] - w * 0.14,
                   corner[0] + w * 0.14, corner[1] + w * 0.14], fill=AZURE)
        d.ellipse([corner[0] - w * 0.085, corner[1] - w * 0.085,
                   corner[0] + w * 0.085, corner[1] + w * 0.085], fill=COBALT)

    # tile B: aspa morisca
    tile_b = Image.new("RGB", (w, w), COBALT)
    db = ImageDraw.Draw(tile_b)
    db.rectangle([0, 0, w - 1, w - 1], outline=BONE, width=int(w * 0.012))
    petal = w * 0.46
    for ang in range(4):
        a = math.pi / 2 * ang
        px, py = c + petal * 0.52 * math.cos(a), c + petal * 0.52 * math.sin(a)
        db.ellipse([px - petal * 0.34, py - petal * 0.34,
                    px + petal * 0.34, py + petal * 0.34], fill=BONE)
    star(db, c, c, w * 0.30, w * 0.13, 4, AZURE, rot=math.pi / 4)
    db.ellipse([c - w * 0.07, c - w * 0.07, c + w * 0.07, c + w * 0.07], fill=COBALT)

    tile_a = tile_a.resize((t, t), Image.LANCZOS)
    tile_b = tile_b.resize((t, t), Image.LANCZOS)
    img = Image.new("RGB", (size, size), BONE)
    for iy in range(tiles):
        for ix in range(tiles):
            img.paste(tile_a if (ix + iy) % 2 == 0 else tile_b, (ix * t, iy * t))
    return img


# ----------------------------------------------------------------------------
# 6. DOMINÓ — calcetines
# ----------------------------------------------------------------------------
def domino(W=1400, H=2400, seed=99):
    rng = random.Random(seed)
    CREAM = (239, 231, 214)
    INK = (24, 22, 20)
    w, h = W * SS, H * SS
    img = Image.new("RGB", (w, h), CREAM)

    tw, th = int(w * 0.30), int(w * 0.15)  # ficha horizontal 2:1

    def piece(vals, rot):
        tile = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        r = th * 0.18
        td.rounded_rectangle([0, 0, tw - 1, th - 1], radius=r, fill=INK)
        td.line([tw / 2, th * 0.12, tw / 2, th * 0.88], fill=CREAM, width=max(2, int(th * 0.045)))
        pip_r = th * 0.075
        offs = {
            0: [], 1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)],
            4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
            5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
            6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)],
        }
        for half, v in enumerate(vals):
            cx = tw * 0.25 if half == 0 else tw * 0.75
            cy = th * 0.5
            sp = th * 0.24
            for ox, oy in offs[v]:
                td.ellipse([cx + ox * sp - pip_r, cy + oy * sp - pip_r,
                            cx + ox * sp + pip_r, cy + oy * sp + pip_r], fill=CREAM)
        return tile.rotate(rot, expand=True, resample=Image.BICUBIC)

    ys = int(th * 1.55)
    xs = int(tw * 1.25)
    row = 0
    for y in range(-th, h + th, ys):
        offset = (row % 2) * xs // 2
        for x in range(-tw, w + tw, xs):
            vals = (rng.randint(0, 6), rng.randint(0, 6))
            rot = rng.uniform(-16, 16)
            p = piece(vals, rot)
            img.paste(p, (x + offset, y), p)
        row += 1
    return img.resize((W, H), Image.LANCZOS)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    jobs = [
        ("onda_optica.png", onda_optica),
        ("oro_roto.png", oro_roto),
        ("topografia.png", topografia),
        ("vitral.png", vitral),
        ("mosaico.png", mosaico),
        ("domino.png", domino),
    ]
    for name, fn in jobs:
        img = fn()
        img.save(f"{out}/{name}")
        print("saved", name, img.size)
