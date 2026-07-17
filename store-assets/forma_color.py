#!/usr/bin/env python3
"""Cápsula Forma & Color — Geometría Moderna (run 2026-07-17).

Genera los print files de la cápsula (6 productos Printful):
  - serpentina_tee.png      3600x4800  DTG front (Bella 3001, blanco)
  - portico_crew.png        3600x4800  DTG front (sweatshirt navy)
  - composicion_hoodie.png  3600x4800  DTG front (hoodie negro)
  - reticula_quarters.png   2250x2250  hi-top canvas quarters
  - reticula_tongue.png     2250x2250  hi-top tongue
  - orbita_athletic.png     1950x3300  women's athletic shoes
  - confeti_socks.png       1400x2400  sublimated socks

Todo se dibuja a 2x y se reduce con LANCZOS para antialiasing.
"""
import math
import random
import sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

CREAM = (242, 233, 218, 255)
PAPER = (246, 241, 230, 255)
INK = (26, 26, 28, 255)
NAVY = (31, 58, 95, 255)
TERRA = (193, 80, 46, 255)
MUSTARD = (217, 164, 65, 255)
SKY = (128, 162, 194, 255)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def canvas(w, h, bg=(0, 0, 0, 0)):
    img = Image.new("RGBA", (w * 2, h * 2), bg)
    return img, ImageDraw.Draw(img)


def save(img, name, w, h):
    img = img.resize((w, h), Image.LANCZOS)
    img.save(f"{OUT}/{name}")
    print("wrote", name, img.size)


def spaced_text(draw, xy, text, size, fill, tracking=0.18, anchor="mm"):
    font = ImageFont.truetype(FONT, size)
    widths = [draw.textlength(c, font=font) for c in text]
    gap = size * tracking
    total = sum(widths) + gap * (len(text) - 1)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill, anchor="lm")
        x += cw + gap


def crown(draw, cx, cy, w, fill):
    """Corona geométrica: tres triángulos sobre una barra."""
    h = w * 0.55
    bar = w * 0.14
    base = cy + h / 2
    draw.rectangle([cx - w / 2, base - bar, cx + w / 2, base], fill=fill)
    for i, peak in enumerate((0.30, 0.46, 0.30)):
        x0 = cx - w / 2 + i * w / 3
        x1 = x0 + w / 3
        draw.polygon([(x0, base - bar), (x1, base - bar),
                      ((x0 + x1) / 2, base - bar - h * peak * 1.6)], fill=fill)


# ---------------------------------------------------------------- 1. Camiseta
def tee():
    W, H = 3600, 4800
    img, d = canvas(W, H)
    rnd = random.Random(20260717)
    cols, rows, tile = 5, 5, 1200  # 2x
    ox = (W * 2 - cols * tile) / 2
    oy = 700
    palette = [NAVY, TERRA, MUSTARD, INK]
    stroke = 170
    for r in range(rows):
        for c in range(cols):
            x, y = ox + c * tile, oy + r * tile
            color = palette[(r * 2 + c + rnd.randint(0, 1)) % 4]
            flip = rnd.random() < 0.5
            # dos cuartos de círculo por celda (patrón de serpentinas)
            if flip:
                d.arc([x - tile / 2, y - tile / 2, x + tile / 2, y + tile / 2],
                      0, 90, fill=color, width=stroke)
                d.arc([x + tile / 2, y + tile / 2, x + tile * 1.5, y + tile * 1.5],
                      180, 270, fill=color, width=stroke)
            else:
                d.arc([x + tile / 2, y - tile / 2, x + tile * 1.5, y + tile / 2],
                      90, 180, fill=color, width=stroke)
                d.arc([x - tile / 2, y + tile / 2, x + tile / 2, y + tile * 1.5],
                      270, 360, fill=color, width=stroke)
            if rnd.random() < 0.18:
                d.ellipse([x + tile / 2 - 60, y + tile / 2 - 60,
                           x + tile / 2 + 60, y + tile / 2 + 60], fill=INK)
    # marco fino
    m = 40
    d.rectangle([ox - m, oy - m, ox + cols * tile + m, oy + rows * tile + m],
                outline=INK, width=14)
    y = oy + rows * tile + 340
    spaced_text(d, (W, y), "STREET ROYALTY", 190, INK, 0.42)
    spaced_text(d, (W, y + 260), "FORMA & COLOR · MMXXVI", 96, TERRA, 0.34)
    save(img, "serpentina_tee.png", W, H)


# ---------------------------------------------------------------- 2. Sudadera
def crew():
    W, H = 3600, 4800
    img, d = canvas(W, H)
    rnd = random.Random(71)
    cols, rows = 4, 4
    cw, ch = 1400, 1560  # celda 2x
    aw, ah = 1040, 1300  # arco 2x
    ox = (W * 2 - cols * cw) / 2 + (cw - aw) / 2
    oy = 620
    palette = [CREAM, MUSTARD, TERRA, SKY]
    for r in range(rows):
        for c in range(cols):
            x = ox + c * cw
            y = oy + r * ch
            color = palette[(c + r * 3) % 4]
            filled = (c + r) % 2 == 0
            box = [x, y, x + aw, y + aw]
            if filled:
                d.pieslice(box, 180, 360, fill=color)
                d.rectangle([x, y + aw / 2, x + aw, y + ah], fill=color)
                d.ellipse([x + aw / 2 - 70, y + aw / 2 - 210,
                           x + aw / 2 + 70, y + aw / 2 - 70],
                          fill=NAVY if color != NAVY else CREAM)
            else:
                d.arc(box, 180, 360, fill=color, width=120)
                d.rectangle([x, y + aw / 2, x + 120, y + ah], fill=color)
                d.rectangle([x + aw - 120, y + aw / 2, x + aw, y + ah], fill=color)
                d.rectangle([x + 240, y + ah - 120, x + aw - 240, y + ah],
                            fill=color)
    y = oy + rows * ch + 240
    spaced_text(d, (W, y), "STREET ROYALTY", 190, CREAM, 0.42)
    spaced_text(d, (W, y + 260), "PÓRTICO REAL", 96, MUSTARD, 0.5)
    save(img, "portico_crew.png", W, H)


# ------------------------------------------------------------------ 3. Hoodie
def hoodie():
    W, H = 3600, 4800
    img, d = canvas(W, H)
    cx, cy = W, 2600
    # composición abstracta: anillo, semicírculo, triángulo, barras
    d.ellipse([cx - 1500, cy - 1500, cx + 1500, cy + 1500],
              outline=MUSTARD, width=150)
    d.pieslice([cx - 1050, cy - 450, cx + 1050, cy + 1650], 180, 360,
               fill=TERRA)
    d.polygon([(cx - 1250, cy + 1250), (cx + 350, cy - 1350),
               (cx + 1550, cy + 550)], outline=CREAM, width=90)
    d.rectangle([cx - 1800, cy + 900, cx + 1800, cy + 1020], fill=SKY)
    d.rectangle([cx - 1400, cy + 1160, cx + 1000, cy + 1240], fill=CREAM)
    d.ellipse([cx + 780, cy - 1180, cx + 1180, cy - 780], fill=SKY)
    d.ellipse([cx - 1300, cy - 900, cx - 1100, cy - 700], fill=CREAM)
    crown(d, cx, cy - 2100, 720, CREAM)
    spaced_text(d, (W, cy + 1900), "STREET ROYALTY", 190, CREAM, 0.42)
    spaced_text(d, (W, cy + 2160), "COMPOSICIÓN Nº1", 96, MUSTARD, 0.4)
    save(img, "composicion_hoodie.png", W, H)


# ------------------------------------------------------- 4. Zapatillas altas
def hitop():
    W = 2250
    img, d = canvas(W, W, PAPER)
    rnd = random.Random(4513)
    n, tile = 9, W * 2 // 9
    for r in range(n):
        for c in range(n):
            x, y = c * tile, r * tile
            roll = rnd.random()
            color = rnd.choice([INK, INK, INK, MUSTARD, TERRA, NAVY])
            if roll < 0.30:  # cuarto de círculo
                corner = rnd.randint(0, 3)
                box = {0: [x - tile, y - tile, x + tile, y + tile],
                       1: [x, y - tile, x + 2 * tile, y + tile],
                       2: [x, y, x + 2 * tile, y + 2 * tile],
                       3: [x - tile, y, x + tile, y + 2 * tile]}[corner]
                start = {0: 0, 1: 90, 2: 180, 3: 270}[corner]
                d.pieslice(box, start, start + 90, fill=color)
            elif roll < 0.48:  # triángulo medio-cuadrado
                pts = [[(x, y), (x + tile, y), (x, y + tile)],
                       [(x + tile, y), (x + tile, y + tile), (x, y)],
                       [(x + tile, y + tile), (x, y + tile), (x + tile, y)],
                       [(x, y + tile), (x, y), (x + tile, y + tile)]]
                d.polygon(pts[rnd.randint(0, 3)], fill=color)
            elif roll < 0.60:  # anillo
                pad = tile * 0.16
                d.ellipse([x + pad, y + pad, x + tile - pad, y + tile - pad],
                          outline=color, width=int(tile * 0.13))
            elif roll < 0.70:  # punto
                pad = tile * 0.3
                d.ellipse([x + pad, y + pad, x + tile - pad, y + tile - pad],
                          fill=color)
            # resto: celda vacía (respira)
    save(img, "reticula_quarters.png", W, W)


def tongue():
    W = 2250
    img, d = canvas(W, W, INK)
    crown(d, W, W - 340, 980, MUSTARD)
    spaced_text(d, (W, W + 560), "SR", 460, CREAM, 0.30)
    d.rectangle([W - 560, W + 950, W + 560, W + 990], fill=MUSTARD)
    save(img, "reticula_tongue.png", W, W)


# --------------------------------------------------- 5. Deportivas (órbitas)
def athletic():
    W, H = 1950, 3300
    img, d = canvas(W, H, PAPER)
    rnd = random.Random(658)
    centers = [(500, 700, 7), (3100, 1900, 9), (900, 4600, 8),
               (3350, 5600, 6), (2000, 3300, 5)]
    palette = [NAVY, TERRA, MUSTARD]
    for cx, cy, rings in centers:
        for i in range(rings):
            radius = 260 + i * 240
            color = palette[i % 3]
            d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                      outline=color, width=22)
            if rnd.random() < 0.6:  # planeta sobre la órbita
                a = rnd.uniform(0, 2 * math.pi)
                px, py = cx + radius * math.cos(a), cy + radius * math.sin(a)
                pr = rnd.choice([36, 52, 68])
                d.ellipse([px - pr, py - pr, px + pr, py + pr],
                          fill=palette[(i + 1) % 3])
    for _ in range(26):  # pequeñas cruces
        x, y = rnd.uniform(80, W * 2 - 80), rnd.uniform(80, H * 2 - 80)
        s = rnd.choice([26, 36])
        d.rectangle([x - s, y - 8, x + s, y + 8], fill=INK)
        d.rectangle([x - 8, y - s, x + 8, y + s], fill=INK)
    save(img, "orbita_athletic.png", W, H)


# ----------------------------------------------------------- 6. Calcetines
def socks():
    W, H = 1400, 2400
    img, d = canvas(W, H, CREAM)
    rnd = random.Random(186)
    palette = [NAVY, TERRA, MUSTARD, INK]
    cols, rows = 7, 12
    cw, ch = W * 2 / cols, H * 2 / rows
    for r in range(rows):
        for c in range(cols):
            cx = c * cw + cw / 2 + rnd.uniform(-30, 30)
            cy = r * ch + ch / 2 + rnd.uniform(-30, 30)
            color = palette[rnd.randint(0, 3)]
            kind = rnd.randint(0, 3)
            s = rnd.uniform(60, 105)
            if kind == 0:  # triángulo rotado
                a0 = rnd.uniform(0, 2 * math.pi)
                pts = [(cx + s * math.cos(a0 + k * 2.0944),
                        cy + s * math.sin(a0 + k * 2.0944)) for k in range(3)]
                d.polygon(pts, fill=color)
            elif kind == 1:  # cuarto de círculo
                start = rnd.choice([0, 90, 180, 270])
                d.pieslice([cx - s, cy - s, cx + s, cy + s],
                           start, start + 90, fill=color)
            elif kind == 2:  # punto / anillo
                if rnd.random() < 0.5:
                    d.ellipse([cx - s * 0.6, cy - s * 0.6,
                               cx + s * 0.6, cy + s * 0.6], fill=color)
                else:
                    d.ellipse([cx - s * 0.7, cy - s * 0.7,
                               cx + s * 0.7, cy + s * 0.7],
                              outline=color, width=26)
            else:  # barra rotada
                bar = Image.new("RGBA", (int(s * 2.4), int(s * 0.7)), color)
                bar = bar.rotate(rnd.uniform(0, 180), expand=True)
                img.alpha_composite(bar, (int(cx - bar.width / 2),
                                          int(cy - bar.height / 2)))
    save(img, "confeti_socks.png", W, H)


if __name__ == "__main__":
    tee()
    crew()
    hoodie()
    hitop()
    tongue()
    athletic()
    socks()
