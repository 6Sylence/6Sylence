#!/usr/bin/env python3
"""Forma & Color — cápsula Bauhaus SRHOOD (drop FC, 2026-07-17).

Regenera los 7 archivos de impresión Printful de los 6 productos del drop
(la camiseta, sudadera, hoodie, zapatilla alta [quarters+tongue], deportiva
y calcetín), fieles a los mockups publicados en la tienda.

Salida en OUT (por defecto ./out):
  fc_tee_front.png        3600x4800 RGBA  (Bella 3001 blanco, DTG frontal)
  fc_sudadera_front.png   3600x4800 RGBA  (Gildan 18000 navy, DTG frontal)
  fc_hoodie_front.png     3600x4800 RGBA  (hoodie premium negro, DTG frontal)
  fc_hitop_quarters.png   2250x2250 RGB   (AOP laterales zapatilla alta)
  fc_hitop_tongue.png     2250x2250 RGB   (AOP lengüeta zapatilla alta)
  fc_athletic_shoes.png   4096x4096 RGB   (AOP deportiva mujer)
  fc_socks.png            1400x2400 RGB   (calcetín sublimado)
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

OUT = os.environ.get("OUT", "out")
os.makedirs(OUT, exist_ok=True)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Paleta Bauhaus de la cápsula
CREAM = (242, 234, 218)
PAPER = (250, 248, 243)
TERRA = (194, 91, 51)
MUSTARD = (217, 154, 43)
GOLD = (206, 145, 38)
NAVY = (30, 42, 68)
INK = (17, 17, 17)
CELESTE = (127, 168, 217)
DEEPBLUE = (36, 72, 107)


def F(size):
    return ImageFont.truetype(SANS_B, size)


def text_tracked(draw, xy, text, font, fill, tracking=0):
    """Texto centrado en xy con tracking extra entre caracteres."""
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy[0] - total / 2
    for c, w in zip(text, widths):
        draw.text((x, xy[1]), c, font=font, fill=fill, anchor="lm")
        x += w + tracking


def quarter_ring(draw, cx, cy, r_out, r_in, quadrant, fill):
    """Cuarto de anillo. quadrant: 0=NE 1=SE 2=SW 3=NW (sentido horario)."""
    start = {0: 270, 1: 0, 2: 90, 3: 180}[quadrant]
    draw.pieslice([cx - r_out, cy - r_out, cx + r_out, cy + r_out],
                  start, start + 90, fill=fill)
    draw.pieslice([cx - r_in, cy - r_in, cx + r_in, cy + r_in],
                  start - 1, start + 91, fill=(0, 0, 0, 0))


def ring(draw, cx, cy, r_out, width, fill):
    draw.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out], fill=fill)
    r_in = r_out - width
    draw.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=(0, 0, 0, 0))


def _paste_shape(base, shape):
    base.alpha_composite(shape)


# ---------------------------------------------------------------- camiseta
def tee():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = random.Random(41)

    # Panel enmarcado
    P = 2900
    px, py = (W - P) // 2, 520
    d.rectangle([px, py, px + P, py + P], fill=(255, 255, 255, 255),
                outline=INK, width=10)

    # Retícula 6x6 de serpentinas: teselas Truchet (cuartos de anillo anclados
    # a esquinas opuestas, que encadenan en tuberías sinuosas)
    n = 6
    margin = 150
    cell = (P - 2 * margin) / n
    thick = cell * 0.30
    colors = [TERRA, INK, NAVY, MUSTARD, TERRA, NAVY, INK, TERRA]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def corner_arc(cd, corner_x, corner_y, color):
        quad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        qd = ImageDraw.Draw(quad)
        r_out = cell / 2 + thick / 2
        r_in = cell / 2 - thick / 2
        qd.ellipse([corner_x - r_out, corner_y - r_out,
                    corner_x + r_out, corner_y + r_out], fill=color)
        qd.ellipse([corner_x - r_in, corner_y - r_in,
                    corner_x + r_in, corner_y + r_in], fill=(0, 0, 0, 0))
        return quad

    for row in range(n):
        for col in range(n):
            x = px + margin + col * cell
            y = py + margin + row * cell
            cx, cy = x + cell / 2, y + cell / 2
            roll = rng.random()
            cell_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            if roll < 0.72:
                # tesela Truchet: dos arcos en esquinas opuestas
                flip = rng.random() < 0.5
                corners = [(x, y), (x + cell, y + cell)] if flip else \
                          [(x + cell, y), (x, y + cell)]
                for (qx, qy) in corners:
                    c = colors[rng.randrange(len(colors))] + (255,)
                    _paste_shape(cell_img, corner_arc(None, qx, qy, c))
            elif roll < 0.84:
                # anillo completo
                c = colors[rng.randrange(len(colors))] + (255,)
                ring_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ring(ImageDraw.Draw(ring_img), cx, cy, cell * 0.40, thick * 0.85, c)
                _paste_shape(cell_img, ring_img)
            elif roll < 0.93:
                # punto
                cd = ImageDraw.Draw(cell_img)
                cd.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=INK + (255,))
            # recorta la tesela a su celda antes de componer
            mask = Image.new("L", (W, H), 0)
            ImageDraw.Draw(mask).rectangle([x, y, x + cell, y + cell], fill=255)
            clipped = Image.composite(cell_img.split()[3], Image.new("L", (W, H), 0), mask)
            layer.paste(cell_img, (0, 0), clipped)
    # recorta la capa al interior del panel y compón
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rectangle(
        [px + 12, py + 12, px + P - 12, py + P - 12], fill=255)
    img.paste(layer, (0, 0), Image.composite(layer.split()[3], Image.new("L", (W, H), 0), mask))

    # Rótulos
    text_tracked(d, (W / 2, py + P + 210), "STREET ROYALTY", F(150), INK + (255,), tracking=64)
    text_tracked(d, (W / 2, py + P + 390), "FORMA & COLOR · MMXXVI", F(76), TERRA + (255,), tracking=30)
    img.save(f"{OUT}/fc_tee_front.png")


# ---------------------------------------------------------------- sudadera
def sudadera():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Pórtico 4x4: arcos macizos (crema/terracota, con punto navy) alternados
    # con arcos de línea (mostaza/celeste, con clave-barra)
    aw, ah = 560, 740        # tamaño de arco
    gap = 150
    n = 4
    total_w = n * aw + (n - 1) * gap
    x0 = (W - total_w) / 2
    y0 = 760
    row_gap = 210
    solid_colors = [CREAM, TERRA]
    line_colors = [MUSTARD, CELESTE]
    for row in range(4):
        for col in range(4):
            x = x0 + col * (aw + gap)
            y = y0 + row * (ah + row_gap)
            solid = (row + col) % 2 == 0
            idx = ((row * 4 + col) // 2) % 2
            if solid:
                c = solid_colors[(row + col // 2) % 2] + (255,)
                # arco macizo: rectángulo + media elipse superior
                r = aw / 2
                d.pieslice([x, y, x + aw, y + 2 * r], 180, 360, fill=c)
                d.rectangle([x, y + r, x + aw, y + ah], fill=c)
                d.ellipse([x + aw / 2 - 30, y + 190, x + aw / 2 + 30, y + 250],
                          fill=NAVY + (255,))
            else:
                c = line_colors[idx] + (255,)
                s = 60  # grosor de línea
                r = aw / 2
                # contorno del arco
                d.arc([x, y, x + aw, y + 2 * r], 180, 360, fill=c, width=s)
                d.rectangle([x, y + r, x + s, y + ah - 160], fill=c)
                d.rectangle([x + aw - s, y + r, x + aw, y + ah - 160], fill=c)
                # clave: barra inferior centrada
                d.rectangle([x + aw / 2 - 130, y + ah - 60, x + aw / 2 + 130, y + ah],
                            fill=c)
    ybase = y0 + 4 * ah + 3 * row_gap + 300
    text_tracked(d, (W / 2, ybase), "STREET ROYALTY", F(130), CREAM + (255,), tracking=58)
    text_tracked(d, (W / 2, ybase + 165), "PORTICO REAL", F(64), MUSTARD + (255,), tracking=46)
    img.save(f"{OUT}/fc_sudadera_front.png")


# ------------------------------------------------------------------ hoodie
def hoodie():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 1750

    # corona geométrica (tres triángulos) arriba
    ty = cy - 1250
    for i, dx in enumerate([-190, 0, 190]):
        hgt = 150 if i == 1 else 120
        d.polygon([(cx + dx - 85, ty), (cx + dx + 85, ty), (cx + dx, ty - hgt)],
                  fill=CREAM + (255,))

    # semicírculo terracota (apoyado en la barra)
    r_s = 620
    d.pieslice([cx - r_s, cy - r_s + 240, cx + r_s, cy + r_s + 240], 180, 360,
               fill=TERRA + (255,))
    # barra celeste horizontal
    d.rectangle([cx - 1050, cy + 215, cx + 1050, cy + 300], fill=CELESTE + (255,))
    # anillo de oro
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ring(ImageDraw.Draw(layer), cx, cy, 900, 80, GOLD + (255,))
    _paste_shape(img, layer)
    # triángulo en trazo crema, ligeramente rotado
    tri = [(cx - 40, cy - 780), (cx + 660, cy + 285), (cx - 700, cy + 210)]
    d.line(tri + [tri[0]], fill=CREAM + (255,), width=42, joint="curve")
    # puntos en los vértices
    for (vx, vy) in tri:
        d.ellipse([vx - 34, vy - 34, vx + 34, vy + 34], fill=PAPER + (255,))
    # disco celeste sobre el anillo, arriba a la derecha
    ax = cx + 900 * math.cos(math.radians(-55))
    ay = cy + 900 * math.sin(math.radians(-55))
    d.ellipse([ax - 95, ay - 95, ax + 95, ay + 95], fill=CELESTE + (255,))

    ybase = cy + 1150
    text_tracked(d, (W / 2, ybase), "STREET ROYALTY", F(130), CREAM + (255,), tracking=58)
    text_tracked(d, (W / 2, ybase + 165), "COMPOSICION Nº1", F(64), GOLD + (255,), tracking=46)
    img.save(f"{OUT}/fc_hoodie_front.png")


# ----------------------------------------------------------- zapatilla alta
def _reticula(size, n, seed):
    """Tile AOP: retícula de celdas donde cada una elige su forma."""
    img = Image.new("RGBA", (size, size), CREAM + (255,))
    rng = random.Random(seed)
    cell = size / n
    palette = [INK, MUSTARD, TERRA, NAVY, DEEPBLUE]
    for row in range(n):
        for col in range(n):
            x, y = col * cell, row * cell
            cx, cy = x + cell / 2, y + cell / 2
            c = palette[rng.randrange(len(palette))] + (255,)
            roll = rng.random()
            cell_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            cd = ImageDraw.Draw(cell_img)
            if roll < 0.42:
                # cuarto de círculo macizo anclado a una esquina
                corner = rng.randrange(4)
                box = {0: [x - cell, y - cell, x + cell, y + cell],
                       1: [x, y - cell, x + 2 * cell, y + cell],
                       2: [x, y, x + 2 * cell, y + 2 * cell],
                       3: [x - cell, y, x + cell, y + 2 * cell]}[corner]
                start = {0: 0, 1: 90, 2: 180, 3: 270}[corner]
                cd.pieslice(box, start, start + 90, fill=c)
            elif roll < 0.58:
                # medio círculo apoyado en un lado
                side = rng.randrange(4)
                if side == 0:
                    cd.pieslice([x, y - cell, x + cell, y + cell], 0, 180, fill=c)
                elif side == 1:
                    cd.pieslice([x, y, x + cell, y + 2 * cell], 180, 360, fill=c)
                elif side == 2:
                    cd.pieslice([x - cell, y, x + cell, y + cell], 270, 90, fill=c)
                else:
                    cd.pieslice([x, y, x + 2 * cell, y + cell], 90, 270, fill=c)
            elif roll < 0.72:
                # anillo
                r = cell * 0.36
                cd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
                r2 = r - cell * 0.13
                cd.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=CREAM + (255,))
            elif roll < 0.82:
                # triángulo
                pts = [(x + 14, y + cell - 14), (x + cell - 14, y + cell - 14),
                       (x + cell / 2, y + 14)]
                rot = rng.randrange(4)
                for _ in range(rot):
                    pts = [(y2 - y + x, cell - (x2 - x) + y - (cell - (x2 - x)) * 0 + (x2 - x) * 0)
                           for (x2, y2) in pts]  # placeholder, se sobreescribe abajo
                # rotación simple alrededor del centro de celda
                ang = math.radians(90 * rng.randrange(4))
                pts = [(cx + (px - cx) * math.cos(ang) - (py - cy) * math.sin(ang),
                        cy + (px - cx) * math.sin(ang) + (py - cy) * math.cos(ang))
                       for (px, py) in [(x + 14, y + cell - 14),
                                        (x + cell - 14, y + cell - 14),
                                        (x + cell / 2, y + 14)]]
                cd.polygon(pts, fill=c)
            elif roll < 0.92:
                # punto
                r = cell * 0.16
                cd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
            # ~8%: celda vacía
            # recorta al interior de la celda para las formas ancladas
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).rectangle([x, y, x + cell, y + cell], fill=255)
            img.paste(cell_img, (0, 0),
                      Image.composite(cell_img.split()[3], Image.new("L", (size, size), 0), mask))
    return img.convert("RGB")


def hitop():
    _reticula(2250, 6, seed=7).save(f"{OUT}/fc_hitop_quarters.png")
    _reticula(2250, 8, seed=23).save(f"{OUT}/fc_hitop_tongue.png")


# ------------------------------------------------------------- deportivas
def athletic():
    S = 4096
    img = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(img)
    rng = random.Random(11)
    palette = [NAVY, TERRA, MUSTARD, DEEPBLUE, INK]
    # órbitas: grandes arcos finos que barren el lienzo
    for i in range(16):
        c = palette[i % len(palette)]
        r = rng.uniform(S * 0.35, S * 1.1)
        cx = rng.uniform(-S * 0.4, S * 1.4)
        cy = rng.uniform(-S * 0.5, S * 1.5)
        w = rng.randint(16, 26)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=w)
    # planetas: puntos navy/terracota
    for _ in range(26):
        r = rng.uniform(18, 44)
        x, y = rng.uniform(0, S), rng.uniform(0, S)
        d.ellipse([x - r, y - r, x + r, y + r],
                  fill=palette[rng.randrange(2)])
    # cruces de carta estelar
    for _ in range(34):
        x, y = rng.uniform(0, S), rng.uniform(0, S)
        a = rng.uniform(28, 46)
        w = 10
        d.rectangle([x - a, y - w, x + a, y + w], fill=INK)
        d.rectangle([x - w, y - a, x + w, y + a], fill=INK)
    img.save(f"{OUT}/fc_athletic_shoes.png")


# --------------------------------------------------------------- calcetines
def socks():
    W, H = 1400, 2400
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    rng = random.Random(5)
    palette = [NAVY, TERRA, MUSTARD, INK, DEEPBLUE]
    step = 118
    for gy in range(0, H + step, step):
        for gx in range(0, W + step, step):
            if rng.random() < 0.22:
                continue
            x = gx + rng.uniform(-30, 30)
            y = gy + rng.uniform(-30, 30)
            c = palette[rng.randrange(len(palette))]
            kind = rng.random()
            ang = rng.uniform(0, 360)
            if kind < 0.38:
                # triángulo pequeño
                s = rng.uniform(24, 40)
                pts = []
                for k in range(3):
                    a = math.radians(ang + k * 120)
                    pts.append((x + s * math.cos(a), y + s * math.sin(a)))
                d.polygon(pts, fill=c)
            elif kind < 0.58:
                # barra rotada
                ln, wd = rng.uniform(34, 52), 11
                a = math.radians(ang)
                dx, dy = math.cos(a), math.sin(a)
                px, py = -dy * wd, dx * wd
                d.polygon([(x - dx * ln - px, y - dy * ln - py),
                           (x + dx * ln - px, y + dy * ln - py),
                           (x + dx * ln + px, y + dy * ln + py),
                           (x - dx * ln + px, y - dy * ln + py)], fill=c)
            elif kind < 0.78:
                # anillo pequeño
                r = rng.uniform(18, 28)
                d.ellipse([x - r, y - r, x + r, y + r], outline=c, width=9)
            else:
                # punto
                r = rng.uniform(11, 18)
                d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    img.save(f"{OUT}/fc_socks.png")


if __name__ == "__main__":
    tee()
    sudadera()
    hoodie()
    hitop()
    athletic()
    socks()
    print("OK ->", OUT)
