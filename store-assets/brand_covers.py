#!/usr/bin/env python3
# Brand covers — portadas de marca 1600×1600 para las colecciones core de SRHOOD.
# Mismo sistema visual que brand-cover-bandanas / brand-cover-capsula-barroco:
# fondo tonal con wordmark repetido, marco fino de oro, icono dorado, título serif
# en crema y pie "STREET ROYALTY HOOD — MMXXVI".
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "covers")
os.makedirs(OUT, exist_ok=True)

S = 1600
CREMA  = (242, 234, 217)
ARENA  = (216, 198, 160)
ORO    = (201, 164, 76)
ORO_HI = (232, 202, 122)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def F(path, size): return ImageFont.truetype(path, size)

PALETAS = {
    "burdeos": ((96, 32, 44), (58, 18, 26)),
    "navy":    ((32, 42, 70), (17, 23, 40)),
    "negro":   ((30, 30, 34), (12, 12, 14)),
    "oliva":   ((86, 90, 64), (52, 55, 38)),
}

def vgrad(size, top, bottom):
    w, h = size
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((w, h))

def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def grain(img):
    noise = Image.effect_noise(img.size, 10).convert("L")
    return Image.blend(img.convert("RGB"), Image.merge("RGB", (noise, noise, noise)), 0.04)

def text_tracked(draw, xy, text, font, fill, tracking=0, anchor_center=True):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if anchor_center: x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking

def crown_pts(cx, cy, w, h):
    l = cx - w / 2; r = cx + w / 2; b = cy + h / 2; t = cy - h / 2
    dipy = b - h * 0.42
    pts = [(l, b),
           (l, t + h * 0.30), (l + w * 0.185, dipy),
           (cx - w * 0.155, t + h * 0.12), (cx, dipy - h * 0.02),
           (cx + w * 0.155, t + h * 0.12), (r - w * 0.185, dipy),
           (r, t + h * 0.30), (r, b)]
    band = (l, b + h * 0.06, r, b + h * 0.16)
    return pts, band

# ---------------------------------------------------------------- iconos (oro, caja centrada en cx,cy de lado d)
LW = 14  # grosor de línea base

def i_crown(img, d, cx, cy, s):
    pts, band = crown_pts(cx, cy, s * 0.92, s * 0.44)
    d.polygon(pts, fill=ORO)
    d.rectangle(band, fill=ORO)
    for px_, py_ in [(cx - s * 0.46 + s * 0.02, cy - s * 0.16),
                     (cx, cy - s * 0.25), (cx + s * 0.46 - s * 0.02, cy - s * 0.16)]:
        d.ellipse([px_ - 11, py_ - 11, px_ + 11, py_ + 11], fill=ORO_HI)

def i_hanger(img, d, cx, cy, s):
    d.arc([cx - s * 0.07, cy - s * 0.42, cx + s * 0.07, cy - s * 0.28], 270, 180, fill=ORO, width=LW)
    d.line([cx, cy - s * 0.28, cx, cy - s * 0.16], fill=ORO, width=LW)
    d.line([cx, cy - s * 0.16, cx - s * 0.46, cy +
s * 0.16], fill=ORO, width=LW)
    d.line([cx, cy - s * 0.16, cx + s * 0.46, cy + s * 0.16], fill=ORO, width=LW)
    d.line([cx - s * 0.46, cy + s * 0.16, cx + s * 0.46, cy + s * 0.16], fill=ORO, width=LW)

def i_tee(img, d, cx, cy, s):
    w = s * 0.56; h = s * 0.72; sl = s * 0.22
    pts = [(cx - w / 2, cy - h / 2), (cx - w / 2 - sl, cy - h / 2 + sl * 0.9),
           (cx - w / 2 - sl * 0.6, cy - h / 2 + sl * 1.6), (cx - w / 2 + sl * 0.28, cy - h / 2 + sl),
           (cx - w / 2 + sl * 0.28, cy + h / 2), (cx + w / 2 - sl * 0.28, cy + h / 2),
           (cx + w / 2 - sl * 0.28, cy - h / 2 + sl), (cx + w / 2 + sl * 0.6, cy - h / 2 + sl * 1.6),
           (cx + w / 2 + sl, cy - h / 2 + sl * 0.9), (cx + w / 2, cy - h / 2)]
    d.line(pts + [pts[0]], fill=ORO, width=LW, joint="curve")
    d.arc([cx - w * 0.22, cy - h / 2 - w * 0.13, cx + w * 0.22, cy - h / 2 + w * 0.13], 0, 180, fill=ORO, width=LW)

def i_hoodie(img, d, cx, cy, s):
    w = s * 0.60; h = s * 0.70
    # cuerpo: hombros → laterales → bajo
    d.line([(cx - w * 0.34, cy - h * 0.30), (cx - w / 2, cy - h * 0.18), (cx - w / 2, cy + h / 2),
            (cx + w / 2, cy + h / 2), (cx + w / 2, cy - h * 0.18), (cx + w * 0.34, cy - h * 0.30)],
           fill=ORO, width=LW, joint="curve")
    # capucha: arco superior entre hombros + escote en V
    d.arc([cx - w * 0.34, cy - h * 0.52, cx + w * 0.34, cy - h * 0.06], 180, 360, fill=ORO, width=LW)
    d.line([(cx - w * 0.34, cy - h * 0.29), (cx, cy - h * 0.10), (cx + w * 0.34, cy - h * 0.29)],
           fill=ORO, width=LW, joint="curve")
    # cordones + bolsillo canguro
    d.line([cx - w * 0.05, cy - h * 0.08, cx - w * 0.05, cy + h * 0.10], fill=ORO, width=9)
    d.line([cx + w * 0.05, cy - h * 0.08, cx + w * 0.05, cy + h * 0.10], fill=ORO, width=9)
    d.line([(cx - w * 0.22, cy + h / 2), (cx - w * 0.16, cy + h * 0.26), (cx + w * 0.16, cy + h * 0.26),
            (cx + w * 0.22, cy + h / 2)], fill=ORO, width=10, joint="curve")

def i_pants(img, d, cx, cy, s):
    w = s * 0.5; h = s * 0.76
    d.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + s * 0.1], outline=ORO, width=12)
    d.line([(cx - w / 2, cy - h / 2 + s * 0.1), (cx - w / 2 + s * 0.02, cy + h / 2), (cx - w * 0.08, cy + h / 2),
            (cx, cy - h * 0.05), (cx + w * 0.08, cy + h / 2), (cx + w / 2 - s * 0.02, cy + h / 2),
            (cx + w / 2, cy - h / 2 + s * 0.1)], fill=ORO, width=LW, joint="curve")
    d.line([cx, cy - h / 2 + s * 0.04, cx, cy - h / 2 + s * 0.1], fill=ORO, width=10)

def i_jacket(img, d, cx, cy, s):
    w = s * 0.6; h = s * 0.7
    d.line([(cx - w * 0.16, cy - h / 2), (cx - w / 2, cy - h * 0.34), (cx - w / 2, cy + h / 2),
            (cx + w / 2, cy + h / 2), (cx + w / 2, cy - h * 0.34), (cx + w * 0.16, cy - h / 2)],
           fill=ORO, width=LW, joint="curve")
    d.line([(cx - w * 0.16, cy - h / 2), (cx, cy - h * 0.2), (cx + w * 0.16, cy - h / 2)], fill=ORO, width=LW, joint="curve")
    d.line([cx, cy - h * 0.2, cx, cy + h / 2], fill=ORO, width=10)
    d.line([(cx - w * 0.16, cy - h / 2), (cx - w * 0.3, cy - h * 0.06)], fill=ORO, width=10)
    d.line([(cx + w * 0.16, cy - h / 2), (cx + w * 0.3, cy - h * 0.06)], fill=ORO, width=10)

def i_sneaker(img, d, cx, cy, s):
    w = s * 0.86; h = s * 0.5
    x0, y1 = cx - w / 2, cy + h / 2
    d.line([(x0, y1 - s * 0.13), (x0, y1 - s * 0.38), (x0 + w * 0.30, y1 - s * 0.38),
            (x0 + w * 0.62, y1 - s * 0.16), (x0 + w, y1 - s * 0.13)], fill=ORO, width=LW, joint="curve")
    d.rounded_rectangle([x0, y1 - s * 0.13, x0 + w, y1], radius=s * 0.05, outline=ORO, width=LW)
    for k in range(3):
        d.line([(x0 + w * (0.13 + 0.065 * k), y1 - s * (0.38 - 0.0 * k)),
                (x0 + w * (0.23 + 0.065 * k), y1 - s * (0.25 - 0.0 * k))], fill=ORO, width=9)

def i_cap(img, d, cx, cy, s):
    w = s * 0.62
    d.pieslice([cx - w / 2, cy - w * 0.42, cx + w / 2, cy + w * 0.42], 180, 360, outline=ORO, width=LW)
    d.line([cx, cy - w * 0.42, cx, cy], fill=ORO, width=9)
    d.line([cx - w * 0.25, cy - w * 0.36, cx - w * 0.08, cy - w * 0.02], fill=ORO, width=9)
    d.line([cx + w * 0.25, cy - w * 0.36, cx + w * 0.08, cy - w * 0.02], fill=ORO, width=9)
    d.rounded_rectangle([cx - w * 0.5, cy - 7, cx + w * 0.78, cy + w * 0.1], radius=w * 0.05, outline=ORO, width=LW)
    d.ellipse([cx - 10, cy - w * 0.42 - 10, cx + 10, cy - w * 0.42 + 10], fill=ORO_HI)

def i_backpack(img, d, cx, cy, s):
    w = s * 0.54; h = s * 0.68
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=s * 0.1, outline=ORO, width=LW)
    d.arc([cx - w * 0.3, cy - h * 0.72, cx + w * 0.3, cy - h * 0.3], 180, 360, fill=ORO, width=LW)
    d.rounded_rectangle([cx - w * 0.3, cy + h * 0.05, cx + w * 0.3, cy + h / 2 - s * 0.04], radius=s * 0.04, outline=ORO, width=10)
    d.line([cx - w * 0.5, cy - h * 0.14, cx + w * 0.5, cy - h * 0.14], fill=ORO, width=10)

def i_glasses(img, d, cx, cy, s):
    r = s * 0.19
    for sx in (-1, 1):
        d.ellipse([cx + sx * s * 0.24 - r, cy - r, cx + sx * s * 0.24 + r, cy + r], outline=ORO, width=LW)
    d.arc([cx - s * 0.07, cy - s * 0.1, cx + s * 0.07, cy + s * 0.04], 180, 360, fill=ORO, width=12)
    d.line([cx - s * 0.24 - r, cy - s * 0.02, cx - s * 0.46, cy - s * 0.1], fill=ORO, width=12)
    d.line([cx + s * 0.24 + r, cy - s * 0.02, cx + s * 0.46, cy - s * 0.1], fill=ORO, width=12)

def i_spark(img, d, cx, cy, s):
    r = s * 0.46
    pts = []
    for k in range(8):
        a = math.pi / 4 * k - math.pi / 2
        rr = r if k % 2 == 0 else r * 0.24
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=ORO)
    d.ellipse([cx + r * 0.5 - 12, cy - r * 0.72 - 12, cx + r * 0.5 + 12, cy - r * 0.72 + 12], fill=ORO_HI)

def i_diamond(img, d, cx, cy, s):
    w = s * 0.78; h = s * 0.62; ty = cy - h * 0.5 + h * 0.3
    top = [(cx - w / 2, ty), (cx - w * 0.24, cy - h / 2), (cx + w * 0.24, cy - h / 2), (cx + w / 2, ty)]
    d.line(top + [(cx, cy + h / 2), top[0]], fill=ORO, width=LW, joint="curve")
    d.line([top[0], (cx - w * 0.16, ty), (cx - w * 0.24, cy - h / 2)], fill=ORO, width=9)
    d.line([top[3], (cx + w * 0.16, ty), (cx + w * 0.24, cy - h / 2)], fill=ORO, width=9)
    d.line([(cx - w / 2, ty), (cx + w / 2, ty)], fill=ORO, width=9)
    d.line([(cx - w * 0.16, ty), (cx, cy + h / 2), (cx + w * 0.16, ty)], fill=ORO, width=9)

def i_laurel(img, d, cx, cy, s):
    # dos ramas de laurel: hojas elípticas colocadas sobre un arco, de abajo hacia los lados
    r = s * 0.44
    for sx in (-1, 1):
        for k in range(6):
            theta = math.radians(18 + k * 24)          # desde la vertical inferior
            lx = cx + sx * r * math.sin(theta)
            ly = cy + r * math.cos(theta)
            leaf = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
            ld = ImageDraw.Draw(leaf)
            ld.ellipse([46, 16, 74, 104], fill=ORO)
            leaf = leaf.rotate(sx * (10 + k * 24), resample=Image.BICUBIC)
            img.paste(leaf, (int(lx - 60), int(ly - 60)), leaf)
    pts, band = crown_pts(cx, cy - s * 0.06, s * 0.34, s * 0.18)
    d.polygon(pts, fill=ORO_HI)
    d.rectangle(band, fill=ORO_HI)

def i_capsule(img, d, cx, cy, s):
    w = s * 0.4; h = s * 0.85
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    cap = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cap)
    cd.rounded_rectangle(box, radius=w / 2, outline=ORO, width=LW)
    cd.line([cx - w / 2 + LW, cy, cx + w / 2 - LW, cy], fill=ORO, width=10)
    cap = cap.rotate(32, resample=Image.BICUBIC, center=(cx, cy))
    img.paste(cap, (0, 0), cap)
    for ox, oy in [(-s * 0.42, -s * 0.3), (s * 0.42, s * 0.28), (s * 0.4, -s * 0.36)]:
        d.ellipse([cx + ox - 8, cy + oy - 8, cx + ox + 8, cy + oy + 8], fill=ORO_HI)

def i_tag(img, d, cx, cy, s):
    tag = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    w = s * 0.62; h = s * 0.5
    pts = [(cx - w * 0.5, cy - h * 0.5), (cx + w * 0.18, cy - h * 0.5), (cx + w * 0.5, cy),
           (cx + w * 0.18, cy + h * 0.5), (cx - w * 0.5, cy + h * 0.5)]
    td.line(pts + [pts[0]], fill=ORO, width=LW, joint="curve")
    td.ellipse([cx + w * 0.12 - 14, cy - 14, cx + w * 0.12 + 14, cy + 14], outline=ORO, width=10)
    f = F(SANS_B, int(s * 0.3))
    td.text((cx - w * 0.14, cy), "40", font=f, fill=ORO, anchor="mm")
    tag = tag.rotate(18, resample=Image.BICUBIC, center=(cx, cy))
    img.paste(tag, (0, 0), tag)

ICONS = {
    "crown": i_crown, "hanger": i_hanger, "tee": i_tee, "hoodie": i_hoodie,
    "pants": i_pants, "jacket": i_jacket, "sneaker": i_sneaker, "cap": i_cap,
    "backpack": i_backpack, "glasses": i_glasses, "spark": i_spark,
    "diamond": i_diamond, "laurel": i_laurel, "capsule": i_capsule, "tag": i_tag,
}

# ---------------------------------------------------------------- plantilla
def cover(title, subtitle, paleta, icon):
    top, bottom = PALETAS[paleta]
    img = vgrad((S, S), top, bottom)
    draw = ImageDraw.Draw(img)

    # wordmark tonal repetido (zona superior)
    tone = mix(mix(top, bottom, 0.4), CREMA, 0.10)
    fw = F(SANS_B, 130)
    for i in range(6):
        y = 90 + i * 150
        x_off = -(i % 3) * 260
        text_tracked(draw, (S / 2 + x_off, y), "SRHOOD · SRHOOD · SRHOOD", fw, tone, tracking=10)

    # velo inferior para legibilidad
    veil = vgrad((S, S), (0, 0, 0), bottom)
    m_ = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m_).rectangle([0, S * 0.52, S, S], fill=140)
    m_ = m_.filter(ImageFilter.GaussianBlur(60))
    img.paste(veil, (0, 0), m_)
    draw = ImageDraw.Draw(img)

    # marco doble con diamantes en esquinas
    m = 78
    draw.rectangle([m, m, S - m, S - m], outline=ORO, width=3)
    draw.rectangle([m + 14, m + 14, S - m - 14, S - m - 14], outline=mix(ORO, bottom, 0.45), width=2)
    for cxx in (m, S - m):
        for cyy in (m, S - m):
            r = 9
            draw.polygon([(cxx, cyy - r), (cxx + r, cyy), (cxx, cyy + r), (cxx - r, cyy)], fill=ORO_HI)

    # icono
    ICONS[icon](img, draw, S / 2, S * 0.35, 430)

    # regla + título + subtítulo
    draw.rectangle([S * 0.22, S * 0.585, S * 0.78, S * 0.589], fill=ORO)
    size = 150
    f_t = F(SERIF_B, size)
    while draw.textlength(title, font=f_t) > S * 0.84:
        size -= 6
        f_t = F(SERIF_B, size)
    draw.text((S / 2, S * 0.685), title, font=f_t, fill=CREMA, anchor="mm")
    text_tracked(draw, (S / 2, S * 0.775), subtitle, F(SANS, 34), ORO_HI, tracking=14)

    # pie
    text_tracked(draw, (S / 2, S * 0.905), "STREET ROYALTY HOOD — MMXXVI", F(SANS, 30), ARENA, tracking=12)
    return grain(img)

COVERS = [
    # (handle, título, subtítulo, paleta, icono)
    ("ropa-streetwear", "ROPA STREETWEAR", "DEL ASFALTO AL TRONO", "negro", "hanger"),
    ("camisetas", "CAMISETAS", "ALGODÓN CON CORONA", "navy", "tee"),
    ("sudaderas-hoodies", "SUDADERAS & HOODIES", "CAPUCHA Y CORONA", "burdeos", "hoodie"),
    ("pantalones-joggers", "PANTALONES & JOGGERS", "COMODIDAD REAL", "oliva", "pants"),
    ("chaquetas-abrigos", "CHAQUETAS & ABRIGOS", "ARMADURA URBANA", "negro", "jacket"),
    ("calzado-sneakers", "CALZADO & SNEAKERS", "PISADA REAL", "navy", "sneaker"),
    ("gorras-gorros", "GORRAS & GORROS", "LA CORONA DE DIARIO", "burdeos", "cap"),
    ("bolsas-mochilas", "BOLSAS & MOCHILAS", "CARGA CON ESTILO", "oliva", "backpack"),
    ("accesorios-streetwear", "ACCESORIOS", "LOS DETALLES CORONAN", "negro", "glasses"),
    ("novedades", "NOVEDADES", "LO ÚLTIMO DEL HOOD", "burdeos", "spark"),
    ("bestsellers", "ESENCIALES SRHOOD", "LOS IMPRESCINDIBLES", "negro", "diamond"),
    ("royalty-classics", "ROYALTY CLASSICS", "FONDO DE ARMARIO REAL", "navy", "laurel"),
    ("capsulas-srhood-series-limitadas", "CÁPSULAS SRHOOD", "SERIES LIMITADAS · NINGUNA SE REPITE", "burdeos", "capsule"),
    ("menos-de-40-entry-royalty", "MENOS DE 40 €", "ENTRY ROYALTY", "oliva", "tag"),
    ("street-royalty-hombre", "HOMBRE", "ÉL LLEVA LA CORONA", "navy", "crown"),
    ("street-royalty-mujer", "MUJER", "ELLA LLEVA LA CORONA", "burdeos", "crown"),
]

if __name__ == "__main__":
    for handle, title, sub, pal, icon in COVERS:
        img = cover(title, sub, pal, icon)
        img.save(f"{OUT}/brand-cover-{handle}.jpg", quality=90)
        print("done", handle)
