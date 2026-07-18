#!/usr/bin/env python3
# Cápsula Meandro — Laberinto Real · SRHOOD
# 6 original Greek-key / meander designs (terracotta amphora palette) for the
# Street Royalty Hood POD pipeline (Printful mockups + Shopify).
import math, os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

NEGRO     = (22, 18, 15, 255)
CREMA     = (238, 227, 203, 255)
TERRACOTA = (193, 94, 57, 255)
TERRA_OSC = (146, 64, 39, 255)
OCRE      = (215, 158, 85, 255)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def F(path, size): return ImageFont.truetype(path, size)

def text_tracked(draw, xy, text, font, fill, tracking=0, center=True):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if center: x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking

# ---------------------------------------------------------------- meander fret
def fret_strip(cells, cell, color, stroke=None, bg=None):
    """Classic running Greek key: hooks hanging between two rails.
    Returns an RGBA image of size (cells*cell, cell)."""
    c = cell
    s = stroke if stroke else max(3, c // 7)
    img = Image.new("RGBA", (cells * c, c), bg if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    h = c
    for i in range(cells):
        x = i * c
        # single-stroke hook spiral per cell, standing on the bottom rail
        p = [(x + c,        h - s // 2),
             (x + s // 2,   h - s // 2),
             (x + s // 2,   s // 2),
             (x + c * 0.72, s // 2),
             (x + c * 0.72, h * 0.60),
             (x + c * 0.30, h * 0.60),
             (x + c * 0.30, h * 0.30),
             (x + c * 0.52, h * 0.30)]
        d.line(p, fill=color, width=s, joint="curve")
    return img

def fret_frame(size, cell, color, stroke=None, inset=0):
    """Square frame made of four fret strips (rotated), returns RGBA size×size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    n = max(1, (size - 2 * inset - 2 * cell) // cell)
    run = n * cell
    strip = fret_strip(n, cell, color, stroke)
    off = (size - run) // 2
    img.paste(strip, (off, inset), strip)                                   # top
    img.paste(strip.rotate(180), (off, size - inset - cell), strip.rotate(180))  # bottom
    img.paste(strip.rotate(-90, expand=True), (inset, off), strip.rotate(-90, expand=True))  # left
    img.paste(strip.rotate(90, expand=True), (size - inset - cell, off), strip.rotate(90, expand=True))  # right
    # corner squares
    d = ImageDraw.Draw(img)
    s = stroke if stroke else max(3, cell // 7)
    for cx, cy in ((inset, inset), (size - inset - cell, inset),
                   (inset, size - inset - cell), (size - inset - cell, size - inset - cell)):
        d.rectangle([cx + cell * 0.22, cy + cell * 0.22, cx + cell * 0.78, cy + cell * 0.78],
                    outline=color, width=s)
        d.rectangle([cx + cell * 0.42, cy + cell * 0.42, cx + cell * 0.58, cy + cell * 0.58],
                    fill=color)
    return img

# ------------------------------------------------------------------ labyrinth
def labyrinth_disc(diam, ring_color, disc_color=None, rings=6, stroke=None):
    """Stylised circular labyrinth: concentric arcs with alternating gates."""
    img = Image.new("RGBA", (diam, diam), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if disc_color:
        d.ellipse([0, 0, diam - 1, diam - 1], fill=disc_color)
    s = stroke if stroke else max(4, diam // 60)
    cx = cy = diam / 2
    gap = 26  # degrees of gate opening
    step = (diam * 0.46 - diam * 0.10) / rings
    for k in range(rings):
        r = diam * 0.46 - k * step
        a0 = 90 if k % 2 == 0 else 270   # gate alternates top/bottom
        d.arc([cx - r, cy - r, cx + r, cy + r],
              start=a0 + gap / 2, end=a0 + 360 - gap / 2, fill=ring_color, width=s)
        # radial gate walls connecting to the next ring inwards
        if k < rings - 1:
            r2 = r - step
            for sign in (-1, 1):
                ang = math.radians(a0 + sign * gap / 2)
                d.line([(cx + r * math.cos(ang), cy + r * math.sin(ang)),
                        (cx + r2 * math.cos(ang), cy + r2 * math.sin(ang))],
                       fill=ring_color, width=s)
    return img

def crown(w, color):
    """Simple SRHOOD 3-point crown, returns RGBA (w, ~0.72w)."""
    h = int(w * 0.72)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    b = h * 0.78
    pts = [(0, b), (0, h * 0.30), (w * 0.185, h * 0.55),
           (w * 0.345, h * 0.10), (w * 0.5, h * 0.50),
           (w * 0.655, h * 0.10), (w * 0.815, h * 0.55),
           (w, h * 0.30), (w, b)]
    d.polygon(pts, fill=color)
    d.rectangle([0, b + h * 0.05, w, b + h * 0.16], fill=color)
    return img

# =====================================================================
# 01 · Camiseta — "Medallón del Laberinto"  (1800×2400, transparent)
# =====================================================================
def mea01():
    W, H = 1800, 2400
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    side = 1500
    ox = (W - side) // 2
    oy = 240
    frame = fret_frame(side, 125, CREMA)
    img.paste(frame, (ox, oy), frame)
    inner = fret_frame(side - 470, 78, TERRACOTA, stroke=14)
    img.paste(inner, (ox + 235, oy + 235), inner)
    lab = labyrinth_disc(620, CREMA, rings=6, stroke=16)
    img.paste(lab, ((W - 620) // 2, oy + (side - 620) // 2), lab)
    cw = 240
    cr = crown(cw, TERRACOTA)
    img.paste(cr, ((W - cw) // 2, oy + (side - int(cw * 0.72)) // 2 - 10), cr)
    y = oy + side + 120
    text_tracked(d, (W / 2, y), "MEANDRO REAL", F(SERIF_B, 128), CREMA, tracking=26)
    text_tracked(d, (W / 2, y + 190), "SRHOOD · LABERINTO · MMXXVI",
                 F(SERIF, 54), TERRACOTA, tracking=16)
    img.save(f"{OUT}/mea01_camiseta.png")

# =====================================================================
# 02 · Sudadera (Sand) — "Friso de Ánfora"  (1800×2400, transparent)
# Print = black band + knocked-out cream fret + terracotta rails
# =====================================================================
def mea02():
    W, H = 1800, 2400
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    band_h = 560
    by = 520
    # black frieze band
    d.rectangle([60, by, W - 60, by + band_h], fill=NEGRO)
    # cream fret riding the band
    strip = fret_strip(10, 160, CREMA, stroke=26)
    img.paste(strip, ((W - 1600) // 2, by + (band_h - 160) // 2), strip)
    # terracotta rails
    for yy in (by - 46, by + band_h + 18):
        d.rectangle([60, yy, W - 60, yy + 28], fill=TERRACOTA)
    for yy in (by - 74, by + band_h + 60):
        d.rectangle([60, yy, W - 60, yy + 10], fill=TERRA_OSC)
    # crown above
    cr = crown(190, NEGRO)
    img.paste(cr, ((W - 190) // 2, by - 74 - 210), cr)
    # caption below
    y = by + band_h + 150
    text_tracked(d, (W / 2, y), "SRHOOD", F(SERIF_B, 150), NEGRO, tracking=60)
    text_tracked(d, (W / 2, y + 220), "CERÁMICA DE LA CALLE · MMXXVI",
                 F(SERIF, 52), TERRA_OSC, tracking=14)
    img.save(f"{OUT}/mea02_sudadera.png")

# =====================================================================
# 03 · Hoodie Premium — "Emblema del Laberinto"  (1800×1800, transparent)
# =====================================================================
def mea03():
    W = 1800
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    frame = fret_frame(W - 200, 110, CREMA)
    img.paste(frame, (100, 100), frame)
    # inner thin rule
    d.rectangle([345, 345, W - 345, W - 345], outline=TERRACOTA, width=12)
    cw = 470
    cr = crown(cw, OCRE)
    img.paste(cr, ((W - cw) // 2, 480), cr)
    text_tracked(d, (W / 2, 910), "STREET ROYALTY", F(SERIF_B, 88), CREMA, tracking=14)
    text_tracked(d, (W / 2, 1050), "LABERINTO REAL", F(SERIF, 58), TERRACOTA, tracking=26)
    # small fret divider
    strip = fret_strip(5, 72, TERRACOTA, stroke=12)
    img.paste(strip, ((W - 360) // 2, 1190), strip)
    text_tracked(d, (W / 2, 1300), "MMXXVI", F(SERIF, 46), CREMA, tracking=34)
    img.save(f"{OUT}/mea03_hoodie.png")

# =====================================================================
# 04 · Zapatillas Altas Hombre — diagonal fret bands  (2250×2250, opaque)
# =====================================================================
def mea04():
    S = 2250
    big = int(S * 1.6)
    base = Image.new("RGBA", (big, big), NEGRO)
    y = 0
    i = 0
    while y < big:
        if i % 2 == 0:
            cell = 300
            strip = fret_strip(big // cell + 2, cell, CREMA, stroke=44)
            base.paste(strip, (0, y), strip)
            y += cell + 70
        else:
            d = ImageDraw.Draw(base)
            d.rectangle([0, y, big, y + 16], fill=TERRACOTA)
            d.rectangle([0, y + 44, big, y + 60], fill=TERRA_OSC)
            y += 130
        i += 1
    rot = base.rotate(45, resample=Image.BICUBIC, expand=False)
    x0 = (big - S) // 2
    img = rot.crop((x0, x0, x0 + S, x0 + S)).convert("RGB")
    img.save(f"{OUT}/mea04_altas.png")

# =====================================================================
# 05 · Slip-On Mujer — allover fret grid on cream  (2325×2325, opaque)
# =====================================================================
def mea05():
    S = 2325
    img = Image.new("RGBA", (S, S), CREMA)
    d = ImageDraw.Draw(img)
    cell = 186
    row_h = cell + 96
    y = 20
    row = 0
    while y < S:
        strip = fret_strip(S // cell + 2, cell, TERRACOTA, stroke=22)
        if row % 2 == 1:
            strip = strip.rotate(180)
            xoff = -cell // 2
        else:
            xoff = 0
        img.paste(strip, (xoff, y), strip)
        # ocre pinstripe + black micro squares between rows
        yy = y + cell + 40
        if yy + 12 < S:
            d.rectangle([0, yy, S, yy + 8], fill=OCRE)
            for x in range(cell // 2, S, cell):
                d.rectangle([x - 11, yy - 11, x + 11, yy + 19], fill=NEGRO)
        y += row_h
        row += 1
    img.convert("RGB").save(f"{OUT}/mea05_slipon.png")

# =====================================================================
# 06 · Bandana — classical square layout  (4125×4125, opaque)
# =====================================================================
def mea06():
    S = 4125
    img = Image.new("RGBA", (S, S), TERRACOTA)
    d = ImageDraw.Draw(img)
    # outer cream fret border
    frame = fret_frame(S - 260, 240, CREMA, stroke=38)
    img.paste(frame, (130, 130), frame)
    # second black thin fret frame
    frame2 = fret_frame(S - 1180, 150, NEGRO, stroke=24)
    img.paste(frame2, (590, 590), frame2)
    # thin cream rule
    d.rectangle([880, 880, S - 880, S - 880], outline=CREMA, width=16)
    # center: black disc + cream labyrinth
    disc = 1520
    lab = labyrinth_disc(disc, CREMA, disc_color=NEGRO, rings=7, stroke=30)
    img.paste(lab, ((S - disc) // 2, (S - disc) // 2), lab)
    cw = 480
    cr = crown(cw, TERRACOTA)
    img.paste(cr, ((S - cw) // 2, (S - int(cw * 0.72)) // 2 - 20), cr)
    # corner crowns (inside second frame corners)
    ccr = crown(300, NEGRO)
    for cx, cy in ((1050, 1050), (S - 1350, 1050), (1050, S - 1270), (S - 1350, S - 1270)):
        img.paste(ccr, (cx, cy), ccr)
    # side wordmarks
    f = F(SERIF_B, 100)
    for ang, pos in ((0, (S / 2, 940)), (180, (S / 2, S - 1070))):
        txt = Image.new("RGBA", (2800, 160), (0, 0, 0, 0))
        td = ImageDraw.Draw(txt)
        text_tracked(td, (1400, 10), "SRHOOD · MEANDRO REAL", f, CREMA, tracking=28)
        txt = txt.rotate(ang, expand=True)
        img.paste(txt, (int(pos[0] - txt.width / 2), int(pos[1])), txt)
    img.convert("RGB").save(f"{OUT}/mea06_bandana.png")

if __name__ == "__main__":
    for fn in (mea01, mea02, mea03, mea04, mea05, mea06):
        fn()
        print("ok", fn.__name__)
