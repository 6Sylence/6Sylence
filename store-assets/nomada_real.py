#!/usr/bin/env python3
"""Drop "Nómada Real" — Street Royalty Hood (SRHOOD).

Genera los 6 print files del drop. Patrones inéditos en la tienda:
  01 Lis Nómada    — emblema flor de lis / semé heráldico  (camiseta burdeos, DTG frontal)
  02 Ikat Imperial — banda ikat con desplazamiento de urdimbre (sudadera navy, DTG frontal)
  03 Camo Corona   — camuflaje contenido en silueta de corona (hoodie verde militar, DTG frontal)
  04 Bogolán Real  — mudcloth de símbolos a mano (zapatillas altas hombre, base blanca)
  05 Pantera Real  — rosetas de leopardo con coronas ocultas (deportivas mujer, base blanca)
  06 Panal Real    — panal de oro sobre verde bosque (calcetines sublimados)

DTG: 3600x4800 (12"x16" @300dpi), fondo transparente.
Calzado/calcetines: teselas densas envolventes (wrap-safe) 4096x4096 / 2400x3600.
Determinista (seed fija). Salida: store-assets/out/*.png
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

CREMA = (242, 232, 213, 255)
ORO = (201, 162, 39, 255)
ORO_CLARO = (232, 200, 92, 255)
TERRACOTA = (176, 96, 58, 255)
TINTA = (36, 29, 20, 255)


def font(size, bold=True):
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def tracked_text(draw, cx, y, text, f, fill, tracking=0.35):
    """Texto centrado con letterspacing proporcional al cuerpo."""
    sizes = [draw.textlength(ch, font=f) for ch in text]
    sp = f.size * tracking
    total = sum(sizes) + sp * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, sizes):
        draw.text((x, y), ch, font=f, fill=fill)
        x += w + sp


def arc_text(img, cx, cy, radius, text, f, fill, a0, a1, flip=False):
    """Texto sobre un arco. Arco superior: a0→a1 pasando por 270°, glifos hacia fuera.
    Arco inferior (flip): a0→a1 pasando por 90°, glifos hacia el centro."""
    n = len(text)
    for i, ch in enumerate(text):
        t = i / max(n - 1, 1)
        deg = a0 + (a1 - a0) * t
        ang = math.radians(deg)
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        glyph = Image.new("RGBA", (f.size * 2, f.size * 2), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glyph)
        gd.text((f.size, f.size), ch, font=f, fill=fill, anchor="mm")
        rot_ccw = (270 - deg) if not flip else (90 - deg)
        glyph = glyph.rotate(rot_ccw, resample=Image.BICUBIC, center=(f.size, f.size))
        img.alpha_composite(glyph, (int(x - f.size), int(y - f.size)))


def crown_poly(cx, cy, w, h):
    """Corona de tres puntas con base — glifo de la casa."""
    x0, y0 = cx - w / 2, cy - h / 2
    pts = [
        (x0, y0 + h * 0.30),
        (x0 + w * 0.18, y0 + h * 0.62),
        (x0 + w * 0.32, y0 + h * 0.18),
        (x0 + w * 0.50, y0 + h * 0.55),
        (x0 + w * 0.68, y0 + h * 0.18),
        (x0 + w * 0.82, y0 + h * 0.62),
        (x0 + w, y0 + h * 0.30),
        (x0 + w * 0.90, y0 + h * 0.86),
        (x0 + w * 0.10, y0 + h * 0.86),
    ]
    return pts


def draw_crown(draw, cx, cy, w, h, fill):
    draw.polygon(crown_poly(cx, cy, w, h), fill=fill)
    draw.rectangle([cx - w * 0.40, cy + h * 0.40, cx + w * 0.40, cy + h * 0.50], fill=fill)


def grain(img, amount=14, coverage=0.05, seed=7):
    """Erosión sutil tipo tinta gastada sobre los píxeles opacos."""
    rnd = random.Random(seed)
    w, h = img.size
    holes = Image.new("L", (w, h), 0)
    hd = ImageDraw.Draw(holes)
    n = int(w * h * coverage / 90)
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.uniform(1.2, 4.5)
        hd.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(60, amount * 10))
    holes = holes.filter(ImageFilter.GaussianBlur(1.1))
    a = img.getchannel("A")
    from PIL import ImageChops
    img.putalpha(ImageChops.subtract(a, holes))
    return img


# ---------------------------------------------------------------- 01 · LIS NÓMADA
def lis_petal(draw, cx, cy, w, h, fill):
    """Pétalo central: hoja apuntada con base acampanada (dos beziers espejadas)."""
    def bez(p0, p1, p2, n=60):
        return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
                 (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])
                for t in (i / n for i in range(n + 1))]
    top = (cx, cy - h / 2)
    left = bez(top, (cx - w * 0.62, cy - h * 0.05), (cx - w * 0.16, cy + h / 2))
    right = bez((cx + w * 0.16, cy + h / 2), (cx + w * 0.62, cy - h * 0.05), top)
    draw.polygon(left + [(cx, cy + h / 2)] + right, fill=fill)


def lis_scroll(img, cx, cy, r, thickness, fill, flip=False):
    """Voluta lateral: arco grueso que se enrosca hacia dentro-abajo, con remate en gota."""
    s = int(r * 2.8 + thickness * 2)
    layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = s / 2
    box = [c - r, c - r, c + r, c + r]
    # arco: nace arriba-dentro y cae hacia fuera-abajo
    d.arc(box, 150, 40, fill=fill, width=int(thickness))
    # remate inferior en gota
    ex = c + r * math.cos(math.radians(40)) - thickness * 0.45
    ey = c + r * math.sin(math.radians(40))
    d.ellipse([ex - thickness * 0.62, ey - thickness * 0.62,
               ex + thickness * 0.62, ey + thickness * 0.62], fill=fill)
    if flip:
        layer = layer.transpose(Image.FLIP_LEFT_RIGHT)
    img.alpha_composite(layer, (int(cx - s / 2), int(cy - s / 2)))


def draw_lis(img, cx, cy, scale, fill, gold):
    d = ImageDraw.Draw(img)
    w, h = 620 * scale, 900 * scale
    # pétalo central
    lis_petal(d, cx, cy - h * 0.10, w * 0.52, h * 0.82, fill)
    # volutas laterales curvándose hacia fuera
    lis_scroll(img, cx - w * 0.44, cy - h * 0.06, 150 * scale, 92 * scale, fill, flip=True)
    lis_scroll(img, cx + w * 0.44, cy - h * 0.06, 150 * scale, 92 * scale, fill, flip=False)
    d = ImageDraw.Draw(img)
    # banda
    bw, bh = w * 0.96, 92 * scale
    band_y = cy + h * 0.20
    d.rounded_rectangle([cx - bw / 2, band_y, cx + bw / 2, band_y + bh],
                        radius=bh / 2, fill=gold)
    # pie: trío de pétalos colgando de la banda
    foot_y = band_y + bh + h * 0.13
    lis_petal(d, cx, foot_y, w * 0.22, h * 0.30, fill)
    for k in (-1, 1):
        pet = Image.new("RGBA", (int(w * 0.5), int(h * 0.4)), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pet)
        lis_petal(pd, w * 0.25, h * 0.17, w * 0.18, h * 0.27, fill)
        pet = pet.rotate(-24 * k, resample=Image.BICUBIC)
        img.alpha_composite(pet, (int(cx + k * w * 0.30 - w * 0.25), int(foot_y - h * 0.18)))


def design_lis():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 2350
    # semé de lis: siembra heráldica tenue al fondo, recortada al rombo
    seme = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for row in range(9):
        for col in range(7):
            sx = 500 + col * 440 + (220 if row % 2 else 0)
            sy = 700 + row * 400
            mini = Image.new("RGBA", (300, 340), (0, 0, 0, 0))
            draw_lis(mini, 150, 150, 0.16, ORO[:3] + (92,), ORO[:3] + (92,))
            seme.alpha_composite(mini, (int(sx) - 150, int(sy) - 150))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.polygon([(cx, 620), (W - 480, cy), (cx, 4080), (480, cy)], fill=255)
    img.paste(seme, (0, 0), Image.composite(seme.getchannel("A"), Image.new("L", (W, H), 0), mask))
    # marco doble en rombo con lis en los vértices
    for inset, width in ((0, 16), (70, 7)):
        md2 = [(cx, 620 + inset * 1.5), (W - 480 - inset * 1.5, cy),
               (cx, 4080 - inset * 1.5), (480 + inset * 1.5, cy)]
        d.line(md2 + [md2[0]], fill=ORO, width=width, joint="curve")
    for vx, vy in [(cx, 620), (W - 480, cy), (cx, 4080), (480, cy)]:
        mini = Image.new("RGBA", (400, 460), (0, 0, 0, 0))
        draw_lis(mini, 200, 200, 0.22, ORO, ORO_CLARO)
        img.alpha_composite(mini, (int(vx) - 200, int(vy) - 210))
    # lis central grande
    draw_lis(img, cx, cy, 1.9, CREMA, ORO)
    d = ImageDraw.Draw(img)
    draw_crown(d, cx, cy - 1180, 340, 220, ORO)
    arc_text(img, cx, cy + 150, 1560, "STREET ROYALTY", font(150), CREMA, 218, 322)
    arc_text(img, cx, cy - 210, 1560, "· NÓMADA REAL ·", font(122), ORO_CLARO, 118, 62, flip=True)
    tracked_text(d, cx, 4290, "MMXXVI", font(96), ORO, 0.9)
    return grain(img, seed=11)


# ---------------------------------------------------------------- 02 · IKAT IMPERIAL
def ikat_displace(layer, seed=3, max_shift=26, band=6):
    """Desplaza columnas verticalmente (ruido suave + jitter) → sangrado de urdimbre."""
    rnd = random.Random(seed)
    w, h = layer.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shift, target = 0.0, 0.0
    for x in range(0, w, band):
        if rnd.random() < 0.25:
            target = rnd.uniform(-max_shift, max_shift)
        shift += (target - shift) * 0.4 + rnd.uniform(-4, 4)
        col = layer.crop((x, 0, min(x + band, w), h))
        out.paste(col, (x, int(shift)))
    return out


def design_ikat():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    panel_w, panel_h = 3140, 2540
    px0, py0 = (W - panel_w) / 2, 900
    crisp = Image.new("RGBA", (panel_w, panel_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(crisp)
    cx = panel_w / 2

    def diamond(dx, cy, w, h, fill, hollow=None):
        pts = [(dx, cy - h / 2), (dx + w / 2, cy), (dx, cy + h / 2), (dx - w / 2, cy)]
        d.polygon(pts, fill=fill)
        if hollow:
            pts2 = [(dx, cy - h * 0.28), (dx + w * 0.28, cy), (dx, cy + h * 0.28), (dx - w * 0.28, cy)]
            d.polygon(pts2, fill=hollow)

    rows = [
        (240, 90, CREMA), (400, 240, ORO), (740, 560, CREMA),
        (1270, 760, ORO), (1800, 560, CREMA), (2140, 240, ORO), (2300, 90, CREMA),
    ]
    for cy, hh, col in rows:
        n = 5 if hh > 400 else 8
        step = panel_w / n
        for i in range(n + 1):
            dx = i * step + (step / 2 if hh <= 400 else 0)
            hollow = (0, 0, 0, 0) if hh > 500 else None
            diamond(dx, cy, step * (0.94 if hh > 400 else 0.7), hh, col, hollow)
        if hh > 500:
            for i in range(n + 1):
                diamond(i * step + step / 2 if hh <= 400 else i * step, cy,
                        step * 0.36, hh * 0.36, TERRACOTA)
    # líneas finas separadoras
    for y in (330, 560, 1080, 1470, 1990, 2220):
        d.line([(0, y), (panel_w, y)], fill=ORO_CLARO[:3] + (170,), width=8)
    crisp = ikat_displace(crisp, seed=5, max_shift=30, band=7)
    # segunda pasada leve en sentido contrario para plumeado más rico
    crisp = ikat_displace(crisp.transpose(Image.FLIP_LEFT_RIGHT), seed=9, max_shift=14, band=5)
    crisp = crisp.transpose(Image.FLIP_LEFT_RIGHT)
    img.alpha_composite(crisp, (int(px0), int(py0)))
    d = ImageDraw.Draw(img)
    # corona en el rombo central
    draw_crown(d, W / 2, py0 + 1270, 300, 200, TINTA[:3] + (235,))
    tracked_text(d, W / 2, py0 + panel_h + 140, "IKAT IMPERIAL", font(140), CREMA, 0.5)
    tracked_text(d, W / 2, py0 + panel_h + 350, "STREET ROYALTY · HECHO PARA REINAR", font(74), ORO_CLARO, 0.42)
    return grain(img, seed=21, coverage=0.03)


# ---------------------------------------------------------------- 03 · CAMO CORONA
def camo_layer(w, h, seed, palette):
    """Camuflaje por metaballs de paseo aleatorio, tono a tono."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, h), palette[0])
    for color, blobs, rmin, rmax in [
        (palette[1], 46, 90, 220), (palette[2], 34, 70, 190), (palette[3], 26, 50, 150),
    ]:
        layer = Image.new("L", (w, h), 0)
        ld = ImageDraw.Draw(layer)
        for _ in range(blobs):
            x, y = rnd.uniform(0, w), rnd.uniform(0, h)
            for _ in range(rnd.randint(6, 14)):
                r = rnd.uniform(rmin, rmax)
                ld.ellipse([x - r, y - r, x + r, y + r], fill=255)
                ang = rnd.uniform(0, 2 * math.pi)
                x += math.cos(ang) * r * 0.8
                y += math.sin(ang) * r * 0.8
        layer = layer.filter(ImageFilter.GaussianBlur(18)).point(lambda v: 255 if v > 110 else 0)
        img.paste(Image.new("RGBA", (w, h), color), (0, 0), layer)
    return img


def design_camo():
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cw, ch = 3000, 2050
    cx, cy = W / 2, 1750
    palette = [(31, 38, 26, 255), (18, 16, 12, 255), (94, 88, 58, 255), (214, 199, 165, 255)]
    camo = camo_layer(cw, int(ch * 1.15), seed=13, palette=palette)
    mask = Image.new("L", (cw, int(ch * 1.15)), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(crown_poly(cw / 2, ch * 0.48, cw * 0.94, ch * 0.92), fill=255)
    md.rectangle([cw * 0.08, ch * 0.86, cw * 0.92, ch * 0.97], fill=255)
    cut = Image.new("RGBA", camo.size, (0, 0, 0, 0))
    cut.paste(camo, (0, 0), mask)
    img.alpha_composite(cut, (int(cx - cw / 2), int(cy - ch * 0.52)))
    d = ImageDraw.Draw(img)
    # contorno crema desplazado (sello serigráfico)
    outline = [(x + 26, y + 30) for x, y in crown_poly(cx, cy - ch * 0.04, cw * 0.94, ch * 0.92)]
    d.line(outline + [outline[0]], fill=CREMA, width=18, joint="curve")
    tracked_text(d, cx, cy + ch * 0.62, "CAMO CORONA", font(160), CREMA, 0.42)
    tracked_text(d, cx, cy + ch * 0.62 + 250, "STREET ROYALTY HOOD", font(84), (214, 199, 165, 255), 0.5)
    tracked_text(d, cx, cy + ch * 0.62 + 420, "MANDA EN SILENCIO", font(66), ORO_CLARO, 0.62)
    return grain(img, seed=31, coverage=0.04)


# ---------------------------------------------------------------- 04 · BOGOLÁN REAL
def hand_line(draw, pts, fill, width, seed):
    """Polilínea con temblor de mano y grosor variable."""
    rnd = random.Random(seed)
    jpts = [(x + rnd.uniform(-4, 4), y + rnd.uniform(-4, 4)) for x, y in pts]
    for (x0, y0), (x1, y1) in zip(jpts, jpts[1:]):
        w = max(2, int(width + rnd.uniform(-width * 0.25, width * 0.25)))
        draw.line([(x0, y0), (x1, y1)], fill=fill, width=w)
        draw.ellipse([x1 - w / 2, y1 - w / 2, x1 + w / 2, y1 + w / 2], fill=fill)


def design_bogolan():
    S = 4096
    BONE = (233, 223, 201, 255)
    INK = (36, 29, 20, 255)
    RUST = (138, 75, 45, 255)
    img = Image.new("RGBA", (S, S), BONE)
    d = ImageDraw.Draw(img)
    rnd = random.Random(41)
    # moteado de tela teñida a mano
    for _ in range(2600):
        x, y = rnd.uniform(0, S), rnd.uniform(0, S)
        r = rnd.uniform(2, 9)
        tone = rnd.choice([(221, 209, 183, 90), (243, 235, 218, 80)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=tone)
    rows = 11
    rh = S / rows
    kinds = ["zigzag", "diamonds", "bars", "crosses", "dots", "crowns",
             "waves", "diamonds", "zigzag", "crosses", "bars"]
    for r, kind in enumerate(kinds):
        y0 = r * rh
        yc = y0 + rh / 2
        ink = RUST if r in (3, 7) else INK
        seed = 100 + r
        # separadores de banda
        hand_line(d, [(x, y0 + 6) for x in range(0, S + 1, 64)], INK, 10, seed * 3)
        if kind == "zigzag":
            for off, wdt in ((0, 16), (rh * 0.30, 9)):
                pts = []
                for i in range(0, 33):
                    x = i * S / 32
                    pts.append((x, yc - rh * 0.26 + off if i % 2 == 0 else yc + rh * 0.26 - off * 0.4))
                hand_line(d, pts, ink, wdt, seed)
        elif kind == "diamonds":
            n = 10
            for i in range(n + 1):
                cx = (i % (n + 1)) * S / n
                pts = [(cx, yc - rh * 0.28), (cx + S / n * 0.36, yc), (cx, yc + rh * 0.28),
                       (cx - S / n * 0.36, yc), (cx, yc - rh * 0.28)]
                hand_line(d, pts, ink, 13, seed + i)
                rr = rh * 0.07
                d.ellipse([cx - rr, yc - rr, cx + rr, yc + rr], fill=ink)
        elif kind == "bars":
            for i in range(26):
                cx = i * S / 26 + S / 52
                for k in (-1, 0, 1):
                    hand_line(d, [(cx + k * 26, yc - rh * 0.30), (cx + k * 26, yc + rh * 0.30)],
                              ink, 12, seed + i * 3 + k)
        elif kind == "crosses":
            for i in range(13):
                cx = i * S / 13 + S / 26
                a = rh * 0.24
                hand_line(d, [(cx - a, yc - a), (cx + a, yc + a)], ink, 14, seed + i)
                hand_line(d, [(cx - a, yc + a), (cx + a, yc - a)], ink, 14, seed + i + 50)
        elif kind == "dots":
            for i in range(30):
                for j in (-1, 0, 1):
                    cx = i * S / 30 + S / 60 + (S / 60 if j == 0 else 0)
                    cyd = yc + j * rh * 0.24
                    rr = rh * 0.055 + rnd.uniform(-2, 2)
                    d.ellipse([cx - rr, cyd - rr, cx + rr, cyd + rr], fill=ink)
        elif kind == "crowns":
            for i in range(9):
                cx = i * S / 9 + S / 18
                pts = crown_poly(cx, yc - rh * 0.04, rh * 0.62, rh * 0.42)
                hand_line(d, pts + [pts[0]], ink, 13, seed + i)
                hand_line(d, [(cx - rh * 0.25, yc + rh * 0.30), (cx + rh * 0.25, yc + rh * 0.30)],
                          ink, 12, seed + i + 7)
        elif kind == "waves":
            for off in (0, rh * 0.26):
                pts = [(x, yc - rh * 0.13 + off + math.sin(x / S * math.pi * 10) * rh * 0.13)
                       for x in range(0, S + 1, 32)]
                hand_line(d, pts, ink, 12, seed + int(off))
    return img


# ---------------------------------------------------------------- 05 · PANTERA REAL
def design_pantera():
    S = 4096
    img = Image.new("RGBA", (S, S), (241, 231, 211, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(55)
    # veladura suave de fondo
    for _ in range(1600):
        x, y = rnd.uniform(0, S), rnd.uniform(0, S)
        r = rnd.uniform(3, 14)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(233, 220, 194, 70))
    # rosetas con muestreo por rejilla + jitter (sin solapes)
    cell = 390
    centers = []
    for gy in range(0, S, cell):
        for gx in range(0, S, cell):
            if rnd.random() < 0.82:
                centers.append((gx + rnd.uniform(90, cell - 90), gy + rnd.uniform(90, cell - 90)))
    CARAMELO = (201, 139, 63, 255)
    OSCURO = (46, 36, 24, 255)
    for i, (cx, cy) in enumerate(centers):
        for (px, py) in ((cx, cy), (cx - S, cy), (cx + S, cy), (cx, cy - S), (cx, cy + S)):
            rot = rnd.uniform(0, 360)
            rr = rnd.uniform(95, 150)
            # mancha interior caramelo, irregular
            blob = [(px + rr * 0.62 * math.cos(math.radians(a + rot)) * rnd.uniform(0.75, 1.15),
                     py + rr * 0.52 * math.sin(math.radians(a + rot)) * rnd.uniform(0.75, 1.15))
                    for a in range(0, 360, 30)]
            d.polygon(blob, fill=CARAMELO)
            # anillos rotos: 2-4 arcos gruesos
            n_arc = rnd.randint(2, 4)
            a0 = rnd.uniform(0, 360)
            for k in range(n_arc):
                start = a0 + k * (360 / n_arc) + rnd.uniform(0, 24)
                end = start + (360 / n_arc) * rnd.uniform(0.45, 0.75)
                box = [px - rr, py - rr * 0.86, px + rr, py + rr * 0.86]
                d.arc(box, start, end, fill=OSCURO, width=int(rr * 0.30))
            if i % 12 == 0 and px == cx and py == cy:
                draw_crown(d, px, py + 4, rr * 0.62, rr * 0.44, (201, 162, 39, 255))
    # motas sueltas y polvo de oro
    for _ in range(420):
        x, y = rnd.uniform(0, S), rnd.uniform(0, S)
        r = rnd.uniform(6, 20)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(46, 36, 24, 255))
    for _ in range(260):
        x, y = rnd.uniform(0, S), rnd.uniform(0, S)
        r = rnd.uniform(2.5, 7)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(201, 162, 39, 210))
    return img


# ---------------------------------------------------------------- 06 · PANAL REAL
def design_panal():
    W, H = 2400, 3600
    VERDE = (20, 53, 42, 255)
    VERDE_HONDO = (14, 40, 31, 255)
    img = Image.new("RGBA", (W, H), VERDE)
    rnd = random.Random(77)
    # viñeteado sutil por franjas (compuesto, no sobrescrito, para no perforar el alfa)
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for y in range(0, H, 24):
        t = abs(y - H / 2) / (H / 2)
        if t > 0.5:
            vd.rectangle([0, y, W, y + 24], fill=VERDE_HONDO[:3] + (int((t - 0.5) * 90),))
    img.alpha_composite(vig)
    d = ImageDraw.Draw(img)
    # rejilla hexagonal (pointy-top)
    R = 150
    dx = math.sqrt(3) * R
    dy = 1.5 * R
    cols = int(W / dx) + 2
    rows = int(H / dy) + 2

    def hexagon(cx, cy, r):
        return [(cx + r * math.cos(math.radians(60 * k - 30)),
                 cy + r * math.sin(math.radians(60 * k - 30))) for k in range(6)]

    filled = set()
    for row in range(rows):
        for col in range(cols):
            if rnd.random() < 0.075:
                filled.add((row, col))
    for row in range(rows):
        for col in range(cols):
            cx = col * dx + (dx / 2 if row % 2 else 0)
            cy = row * dy
            pts = hexagon(cx, cy, R - 8)
            if (row, col) in filled:
                d.polygon(pts, fill=ORO)
                draw_crown(d, cx, cy + 6, R * 0.78, R * 0.56, VERDE)
            elif rnd.random() < 0.06:
                d.polygon(hexagon(cx, cy, R * 0.30), fill=ORO_CLARO)
                d.polygon(pts, fill=None, outline=ORO, width=12)
            else:
                d.polygon(pts, fill=None, outline=ORO, width=12)
    return img


DESIGNS = {
    "lis_nomada_front.png": design_lis,
    "ikat_imperial_front.png": design_ikat,
    "camo_corona_front.png": design_camo,
    "bogolan_real_shoes.png": design_bogolan,
    "pantera_real_shoes.png": design_pantera,
    "panal_real_socks.png": design_panal,
}

if __name__ == "__main__":
    for name, fn in DESIGNS.items():
        print("→", name)
        im = fn()
        im.save(os.path.join(OUT, name))
        im.thumbnail((640, 640))
        im.save(os.path.join(OUT, "prev_" + name))
    print("OK:", OUT)
