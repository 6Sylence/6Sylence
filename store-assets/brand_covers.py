#!/usr/bin/env python3
# Brand covers — portadas de colección unificadas para Street Royalty Hood.
# Estilo de la casa: fondo oscuro degradado, doble marco dorado con diamantes,
# icono line-art dorado, título serif crema, subtítulo tracked oro, watermark SRHOOD.
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "covers")
os.makedirs(OUT, exist_ok=True)

S = 1600  # lado del cuadrado

NEGRO_T = (16, 16, 20); NEGRO_B = (8, 8, 10)
NAVY_T  = (26, 32, 52); NAVY_B  = (10, 13, 22)
OLIVA_T = (34, 38, 26); OLIVA_B = (14, 16, 11)
BURD_T  = (96, 30, 42); BURD_B  = (44, 13, 19)
CREMA   = (242, 234, 217)
ORO     = (201, 164, 76)
ORO_HI  = (232, 202, 122)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def F(path, size): return ImageFont.truetype(path, int(size))

def vgrad(size, top, bottom):
    w, h = size
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((w, h))

def grain(img):
    noise = Image.effect_noise(img.size, 10).convert("L")
    return Image.blend(img.convert("RGB"), Image.merge("RGB", (noise, noise, noise)), 0.045)

def text_tracked(draw, xy, text, font, fill, tracking=0, anchor_center=False):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if anchor_center: x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking
    return total

def watermark(img, top_color):
    """Filas de 'SRHOOD ·' en gran tamaño, apenas visibles sobre el fondo."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = F(SANS_B, 150)
    tone = tuple(min(255, c + 26) for c in top_color) + (46,)
    y = 90
    row = 0
    while y < S * 0.62:
        txt = "SRHOOD · " * 6
        d.text((-160 - (row % 3) * 210, y), txt, font=f, fill=tone)
        y += 210
        row += 1
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def frame(draw):
    m = 68
    draw.rectangle([m, m, S - m, S - m], outline=ORO, width=3)
    draw.rectangle([m + 16, m + 16, S - m - 16, S - m - 16], outline=(150, 118, 56), width=1)
    for cx in (m, S - m):
        for cy in (m, S - m):
            r = 11
            draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=ORO)

def fit_title(draw, text, max_w, start=150, minimum=84):
    size = start
    while size > minimum:
        f = F(SERIF_B, size)
        if draw.textlength(text, font=f) <= max_w:
            return [(text, f)]
        size -= 6
    # dos líneas: partir por el espacio más centrado
    words = text.split(" ")
    best, best_d = None, 1e9
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        d = abs(len(a) - len(b))
        if d < best_d: best, best_d = (a, b), d
    size = start
    while size > 64:
        f = F(SERIF_B, size)
        if all(draw.textlength(t, font=f) <= max_w for t in best):
            return [(best[0], f), (best[1], f)]
        size -= 6
    return [(best[0], F(SERIF_B, 64)), (best[1], F(SERIF_B, 64))]

# ----------------------------------------------------------------- iconos
# Cada icono dibuja line-art dorado centrado en (cx, cy) dentro de un radio s.
LW = 14  # grosor de línea estándar

def _crown(d, cx, cy, w, h, width=LW, fill=None):
    l, r, t, b = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    dip = b - h * 0.40
    pts = [(l, b), (l, t + h * 0.30), (l + w * 0.19, dip), (cx - w * 0.16, t + h * 0.10),
           (cx, dip - h * 0.04), (cx + w * 0.16, t + h * 0.10), (r - w * 0.19, dip),
           (r, t + h * 0.30), (r, b)]
    if fill:
        d.polygon(pts, fill=fill)
        d.rectangle([l, b + h * 0.08, r, b + h * 0.20], fill=fill)
    else:
        d.line(pts + [pts[0]], fill=ORO, width=width, joint="curve")
        d.rectangle([l, b + h * 0.08, r, b + h * 0.20], outline=ORO, width=width)

def _circle(d, cx, cy, r, width=LW, color=ORO):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)

def i_hanger(d, cx, cy, s):
    hook_r = s * 0.22
    d.arc([cx - hook_r, cy - s*0.95, cx + hook_r, cy - s*0.95 + hook_r*2], 270, 90 + 360, fill=ORO, width=12)
    d.arc([cx - hook_r, cy - s*0.95, cx + hook_r, cy - s*0.95 + hook_r*2], 0, 270, fill=ORO, width=12)
    top = cy - s * 0.95 + hook_r * 2
    d.line([(cx, top), (cx - s*0.95, cy + s*0.45), (cx + s*0.95, cy + s*0.45), (cx, top)],
           fill=ORO, width=LW, joint="curve")
    _crown(d, cx, cy + s*0.12, s*0.42, s*0.26, width=9)

def i_star(d, cx, cy, s):
    R, r = s * 0.95, s * 0.42
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rad = R if k % 2 == 0 else r
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    d.line(pts + [pts[0]], fill=ORO, width=LW, joint="curve")

def i_bolt(d, cx, cy, s):
    pts = [(cx + s*0.10, cy - s*0.95), (cx - s*0.42, cy + s*0.12), (cx - s*0.02, cy + s*0.12),
           (cx - s*0.10, cy + s*0.95), (cx + s*0.42, cy - s*0.15), (cx + s*0.02, cy - s*0.15)]
    d.line(pts + [pts[0]], fill=ORO, width=LW, joint="curve")

def i_venus(d, cx, cy, s):
    _circle(d, cx, cy - s * 0.30, s * 0.52)
    d.line([(cx, cy + 0.22 * s), (cx, cy + s * 0.95)], fill=ORO, width=LW)
    d.line([(cx - s * 0.30, cy + s * 0.60), (cx + s * 0.30, cy + s * 0.60)], fill=ORO, width=LW)

def i_mars(d, cx, cy, s):
    _circle(d, cx - s * 0.22, cy + s * 0.22, s * 0.52)
    d.line([(cx + s * 0.16, cy - s * 0.16), (cx + s * 0.80, cy - s * 0.80)], fill=ORO, width=LW)
    d.line([(cx + s * 0.80, cy - s * 0.80), (cx + s * 0.80, cy - s * 0.38)], fill=ORO, width=LW)
    d.line([(cx + s * 0.80, cy - s * 0.80), (cx + s * 0.38, cy - s * 0.80)], fill=ORO, width=LW)

def i_seal(d, cx, cy, s):
    _circle(d, cx, cy, s * 0.95, width=12)
    _circle(d, cx, cy, s * 0.80, width=6)
    _crown(d, cx, cy - s * 0.02, s * 0.85, s * 0.5, width=LW)
    for sgn in (-1, 1):
        d.line([(cx + sgn * s * 0.18, cy + s * 0.48), (cx + sgn * s * 0.42, cy + s * 0.48)], fill=ORO, width=8)
    d.ellipse([cx - 7, cy + s * 0.48 - 7, cx + 7, cy + s * 0.48 + 7], fill=ORO)

def i_tote(d, cx, cy, s):
    d.rectangle([cx - s*0.7, cy - s*0.3, cx + s*0.7, cy + s*0.85], outline=ORO, width=LW)
    d.arc([cx - s*0.45, cy - s*0.95, cx + s*0.45, cy + s*0.05], 180, 360, fill=ORO, width=LW)
    _crown(d, cx, cy + s*0.26, s*0.5, s*0.3, width=9)

def i_dumbbell(d, cx, cy, s):
    d.line([(cx - s*0.5, cy), (cx + s*0.5, cy)], fill=ORO, width=LW)
    for sgn in (-1, 1):
        d.rectangle([cx + sgn*s*0.75 - s*0.14, cy - s*0.55, cx + sgn*s*0.75 + s*0.14, cy + s*0.55], outline=ORO, width=LW)
        d.rectangle([cx + sgn*s*0.5 - s*0.10, cy - s*0.38, cx + sgn*s*0.5 + s*0.10, cy + s*0.38], outline=ORO, width=12)

def i_leaf(d, cx, cy, s):
    left  = [(cx, cy + s*0.9), (cx - s*0.75, cy + s*0.15), (cx - s*0.35, cy - s*0.75), (cx, cy - s*0.9)]
    right = [(cx, cy - s*0.9), (cx + s*0.35, cy - s*0.75), (cx + s*0.75, cy + s*0.15), (cx, cy + s*0.9)]
    d.line(left, fill=ORO, width=LW, joint="curve")
    d.line(right, fill=ORO, width=LW, joint="curve")
    d.line([(cx, cy + s*0.9), (cx, cy - s*0.55)], fill=ORO, width=10)
    for k in range(3):
        y = cy + s*0.45 - k * s*0.42
        d.line([(cx, y), (cx - s*0.30, y - s*0.18)], fill=ORO, width=8)
        d.line([(cx, y - s*0.14), (cx + s*0.30, y - s*0.32)], fill=ORO, width=8)

def i_tag(d, cx, cy, s):
    pts = [(cx - s*0.85, cy), (cx - s*0.15, cy - s*0.7), (cx + s*0.85, cy - s*0.7),
           (cx + s*0.85, cy + s*0.7), (cx - s*0.15, cy + s*0.7)]
    d.line(pts + [pts[0]], fill=ORO, width=LW, joint="curve")
    _circle(d, cx - s*0.42, cy, s*0.12, width=10)
    f = F(SANS_B, s * 0.55)
    d.text((cx + s*0.18, cy), "40", font=f, fill=ORO, anchor="mm")

def i_pattern(d, cx, cy, s):
    for gy in range(3):
        for gx in range(3):
            x = cx + (gx - 1) * s * 0.66
            y = cy + (gy - 1) * s * 0.66
            r = s * 0.24
            d.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], outline=ORO, width=10)

def i_drop(d, cx, cy, s):
    d.arc([cx - s*0.6, cy - s*0.25, cx + s*0.6, cy + s*0.95], 0, 180, fill=ORO, width=LW)
    d.line([(cx - s*0.6, cy + s*0.35), (cx, cy - s*0.95)], fill=ORO, width=LW)
    d.line([(cx + s*0.6, cy + s*0.35), (cx, cy - s*0.95)], fill=ORO, width=LW)
    _circle(d, cx + s*0.14, cy + s*0.30, s*0.11, width=8)

def i_cap(d, cx, cy, s):
    # copa de la gorra
    d.arc([cx - s*0.75, cy - s*0.70, cx + s*0.55, cy + s*0.60], 180, 360, fill=ORO, width=LW)
    d.line([(cx - s*0.75, cy - s*0.05), (cx + s*0.55, cy - s*0.05)], fill=ORO, width=LW)
    d.line([(cx - s*0.10, cy - s*0.70), (cx - s*0.10, cy - s*0.05)], fill=ORO, width=8)
    # visera hacia la derecha
    d.line([(cx + s*0.55, cy - s*0.05), (cx + s*1.05, cy + s*0.10)], fill=ORO, width=LW)
    d.arc([cx + s*0.15, cy - s*0.05, cx + s*1.05, cy + s*0.55], 0, 75, fill=ORO, width=LW)
    # botón
    d.ellipse([cx - s*0.15, cy - s*0.78, cx - s*0.05, cy - s*0.68], fill=ORO)

def i_sun(d, cx, cy, s):
    _circle(d, cx, cy, s * 0.45)
    for k in range(12):
        a = k * math.pi / 6
        x1, y1 = cx + s*0.62 * math.cos(a), cy + s*0.62 * math.sin(a)
        x2, y2 = cx + s*0.92 * math.cos(a), cy + s*0.92 * math.sin(a)
        d.line([(x1, y1), (x2, y2)], fill=ORO, width=11)

def i_gem(d, cx, cy, s):
    top, mid = cy - s*0.55, cy - s*0.15
    pts = [(cx - s*0.85, mid), (cx - s*0.45, top), (cx + s*0.45, top), (cx + s*0.85, mid), (cx, cy + s*0.8)]
    d.line(pts + [pts[0]], fill=ORO, width=LW, joint="curve")
    d.line([(cx - s*0.85, mid), (cx + s*0.85, mid)], fill=ORO, width=10)
    for px in (-0.38, 0, 0.38):
        d.line([(cx + px * s, mid), (cx, cy + s*0.8)], fill=ORO, width=8)
    d.line([(cx - s*0.38, mid), (cx - s*0.45, top)], fill=ORO, width=8)
    d.line([(cx + s*0.38, mid), (cx + s*0.45, top)], fill=ORO, width=8)

def _sneaker(d, cx, cy, s, high=False, laces=3):
    b = cy + s * 0.55
    d.line([(cx - s*0.95, b), (cx + s*0.95, b)], fill=ORO, width=LW)                       # suela base
    d.line([(cx - s*0.95, b - s*0.22), (cx + s*0.95, b - s*0.22)], fill=ORO, width=10)    # línea suela
    d.line([(cx - s*0.95, b), (cx - s*0.95, b - s*0.22)], fill=ORO, width=10)
    d.line([(cx + s*0.95, b), (cx + s*0.95, b - s*0.22)], fill=ORO, width=10)
    topy = b - (s * 1.35 if high else s * 0.95)
    d.line([(cx - s*0.95, b - s*0.22), (cx - s*0.80, topy), (cx - s*0.25, topy),
            (cx + s*0.45, b - s*0.55), (cx + s*0.95, b - s*0.40)], fill=ORO, width=LW, joint="curve")
    for k in range(laces):
        y = topy + s*0.18 + k * s*0.22
        d.line([(cx - s*0.62, y), (cx - s*0.30 + k * s*0.12, y + s*0.10)], fill=ORO, width=9)

def i_hitop(d, cx, cy, s):  _sneaker(d, cx, cy, s, high=True, laces=4)
def i_lowtop(d, cx, cy, s): _sneaker(d, cx, cy, s, high=False, laces=2)

def i_runner(d, cx, cy, s):
    _sneaker(d, cx, cy, s, high=False, laces=2)
    for k in range(3):
        y = cy - s*0.05 + k * s*0.2
        d.line([(cx - s*1.45, y), (cx - s*1.12, y)], fill=ORO, width=9)

def i_slide(d, cx, cy, s):
    b = cy + s * 0.45
    # suela con grosor
    d.line([(cx - s*0.95, b), (cx + s*0.95, b)], fill=ORO, width=LW)
    d.line([(cx - s*0.88, b + s*0.18), (cx + s*0.88, b + s*0.18)], fill=ORO, width=10)
    d.line([(cx - s*0.95, b), (cx - s*0.88, b + s*0.18)], fill=ORO, width=10)
    d.line([(cx + s*0.95, b), (cx + s*0.88, b + s*0.18)], fill=ORO, width=10)
    # banda
    d.arc([cx - s*0.62, b - s*1.00, cx + s*0.55, b + s*0.30], 195, 345, fill=ORO, width=LW)
    _crown(d, cx - s*0.04, b - s*0.70, s*0.34, s*0.2, width=8)

def i_shoe_mars(d, cx, cy, s):
    _sneaker(d, cx, cy + s*0.2, s * 0.85, high=False, laces=2)
    i_mars(d, cx + s*0.45, cy - s*0.72, s * 0.34)

def i_shoe_venus(d, cx, cy, s):
    _sneaker(d, cx, cy + s*0.2, s * 0.85, high=False, laces=2)
    i_venus(d, cx + s*0.62, cy - s*0.75, s * 0.34)

def i_flask(d, cx, cy, s):
    d.line([(cx - s*0.22, cy - s*0.9), (cx - s*0.22, cy - s*0.25), (cx - s*0.75, cy + s*0.75)],
           fill=ORO, width=LW, joint="curve")
    d.line([(cx + s*0.22, cy - s*0.9), (cx + s*0.22, cy - s*0.25), (cx + s*0.75, cy + s*0.75)],
           fill=ORO, width=LW, joint="curve")
    d.line([(cx - s*0.75, cy + s*0.75), (cx + s*0.75, cy + s*0.75)], fill=ORO, width=LW)
    d.line([(cx - s*0.32, cy - s*0.9), (cx + s*0.32, cy - s*0.9)], fill=ORO, width=LW)
    d.line([(cx - s*0.52, cy + s*0.32), (cx + s*0.52, cy + s*0.32)], fill=ORO, width=10)
    _circle(d, cx - s*0.12, cy + s*0.02, s*0.07, width=7)
    _circle(d, cx + s*0.18, cy - s*0.28, s*0.05, width=6)

# ----------------------------------------------------------------- plantilla
def cover(title, subtitle, icon, colorway):
    top, bottom = colorway
    img = vgrad((S, S), top, bottom)
    img = watermark(img, top)
    draw = ImageDraw.Draw(img)
    frame(draw)
    icon(draw, S / 2, S * 0.30, 200)
    # regla + título
    draw.rectangle([S * 0.22, S * 0.545, S * 0.78, S * 0.549], fill=ORO)
    lines = fit_title(draw, title, S * 0.76)
    y = S * 0.645 if len(lines) == 1 else S * 0.615
    for text, f in lines:
        draw.text((S / 2, y), text, font=f, fill=CREMA, anchor="mm")
        y += f.size * 1.12
    text_tracked(draw, (S / 2, y + 24), subtitle, F(SANS, 42), ORO_HI, tracking=18, anchor_center=True)
    text_tracked(draw, (S / 2, S * 0.895), "STREET ROYALTY HOOD — MMXXVI", F(SANS, 30), ORO, tracking=10, anchor_center=True)
    return grain(img)

COVERS = [
    # (archivo, título, subtítulo, icono, colorway)
    ("ropa-streetwear",        "ROPA STREETWEAR",       "EL ARMARIO COMPLETO",        i_hanger,    (NAVY_T, NAVY_B)),
    ("esenciales-srhood",      "ESENCIALES",            "LOS QUE NUNCA FALLAN",       i_star,      (NEGRO_T, NEGRO_B)),
    ("novedades",              "NOVEDADES",             "EL DROP VIGENTE",            i_bolt,      (NEGRO_T, NEGRO_B)),
    ("street-royalty-mujer",   "MUJER",                 "SELECCIÓN PARA ELLA",        i_venus,     (NAVY_T, NAVY_B)),
    ("street-royalty-hombre",  "HOMBRE",                "SELECCIÓN PARA ÉL",          i_mars,      (NAVY_T, NAVY_B)),
    ("royalty-classics",       "ROYALTY CLASSICS",      "LA COLECCIÓN INSIGNIA",      i_seal,    (NEGRO_T, NEGRO_B)),
    ("bolsas-mochilas",        "BOLSAS & MOCHILAS",     "CARGA CON ESTILO",           i_tote,      (NAVY_T, NAVY_B)),
    ("deporte-gym-royalty",    "DEPORTE & GYM",         "DEL GYM A LA CALLE",         i_dumbbell,  (NAVY_T, NAVY_B)),
    ("eco-organico",           "ECO & ORGÁNICO",        "MENOS HUELLA, MISMA ACTITUD",i_leaf,      (OLIVA_T, OLIVA_B)),
    ("menos-de-40",            "MENOS DE 40 €",         "ENTRY ROYALTY",              i_tag,       (NEGRO_T, NEGRO_B)),
    ("all-over-print",         "ALL-OVER PRINT",        "EDICIONES ÚNICAS",           i_pattern,   (NEGRO_T, NEGRO_B)),
    ("nuevos-colores",         "NUEVOS COLORES",        "EL COLOR ES ACTITUD",        i_drop,      (BURD_T, BURD_B)),
    ("completa-el-look",       "COMPLETA EL LOOK",      "DE LA CABEZA A LOS PIES",    i_cap,       (NAVY_T, NAVY_B)),
    ("drop-julio-2026",        "DROP JULIO 2026",       "VERANO ROYALTY",             i_sun,       (NEGRO_T, NEGRO_B)),
    ("capsulas-srhood",        "CÁPSULAS SRHOOD",       "SERIES LIMITADAS",           i_gem,       (NEGRO_T, NEGRO_B)),
    ("zapatillas-altas",       "ZAPATILLAS ALTAS",      "CAÑA ALTA CLÁSICA",          i_hitop,     (NAVY_T, NAVY_B)),
    ("zapatillas-bajas",       "BAJAS & SLIP-ON",       "SILUETAS LIMPIAS",           i_lowtop,    (NAVY_T, NAVY_B)),
    ("zapatillas-deportivas",  "DEPORTIVAS",            "LIGERAS Y TRANSPIRABLES",    i_runner,    (NAVY_T, NAVY_B)),
    ("slides-chanclas",        "SLIDES & CHANCLAS",     "VERANO A PIE DE CALLE",      i_slide,     (NAVY_T, NAVY_B)),
    ("calzado-hombre",         "CALZADO HOMBRE",        "PISA FUERTE",                i_shoe_mars, (NAVY_T, NAVY_B)),
    ("calzado-mujer",          "CALZADO MUJER",         "PISA FUERTE",                i_shoe_venus,(NAVY_T, NAVY_B)),
    ("street-lab",             "STREET LAB",            "SERIE GRÁFICA",              i_flask,     (NEGRO_T, NEGRO_B)),
]

if __name__ == "__main__":
    for name, title, sub, icon, cw in COVERS:
        cover(title, sub, icon, cw).save(f"{OUT}/brand-cover-{name}.jpg", quality=90)
        print("done", name)
