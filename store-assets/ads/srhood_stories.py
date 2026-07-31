#!/usr/bin/env python3
"""
Heráldica Mineral — SRHOOD Instagram Stories
Plancha 1080x1920. Guilloché trazado por acumulación, no por filtro.
"""
import math, os
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.join(BASE, "src")
OUT = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PROD, exist_ok=True)

# Originales en el CDN de Shopify: la plancha se reconstruye desde cero sin
# depender de ningún fichero temporal.
FUENTES = {
    "brocado_shoe": "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"
                    "mens-high-top-canvas-shoes-black-left-front-6a5be18bcf0a0.jpg?v=1784406613",
    "malaquita_hoodie": "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"
                        "unisex-premium-pullover-hoodie-black-front-6a5befe6b75f9.jpg?v=1784410271",
    "cifra_hoodie": "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"
                    "cifra-real-hoodie-black-front.jpg?v=1784600531",
    "forja_shoe": "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"
                  "mens-high-top-canvas-shoes-black-left-front-6a5bd7af4e719.jpg?v=1784404140",
    "kintsugi_shoe": "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"
                     "mens-high-top-canvas-shoes-black-left-6a5b72560960d.jpg?v=1784378076",
    "vidriera_shoe": "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"
                     "mens-high-top-canvas-shoes-white-left-front-6a5b10e5a5efd.jpg?v=1784353140",
    "laurel_hoodie": "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"
                     "unisex-premium-pullover-hoodie-black-front-6a5b9ef2db9ad.jpg?v=1784389433",
    "brocado_bucket": "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"
                      "all-over-print-reversible-bucket-hat-white-front-outside-6a5be1b5b31e0.jpg?v=1784406640",
    "meandro_bandana": "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"
                       "all-over-print-bandana-white-m-front-6a5bfdb5ed1ee.jpg?v=1784413780",
    "kintsugi_hoodie": "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"
                       "unisex-premium-pullover-hoodie-black-front-6a5b7252be077.jpg?v=1784378061",
    "marq_shoe": "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"
                 "mens-high-top-canvas-shoes-black-left-front-6a5ec02fd4bf6.jpg?v=1784594770",
}


def set_canvas(w, h):
    """Cambia el lienzo del sistema. Las funciones leen W/H del módulo."""
    global W, H
    W, H = w, h


def asegurar_fuentes():
    import urllib.request
    for nombre, url in FUENTES.items():
        destino = os.path.join(PROD, f"{nombre}.jpg")
        if not os.path.exists(destino):
            urllib.request.urlretrieve(url, destino)
            print("descargado", nombre)

W, H = 1080, 1920
SS = 3                      # supersample factor for all vector work
MARGIN = 66
SAFE_TOP, SAFE_BOT = 268, 1652

# ── paleta mineral ────────────────────────────────────────────────────────────
NEGRO      = (9, 10, 12)
NEGRO_WARM = (18, 21, 20)
ESMERALDA  = (11, 46, 37)
ESM_HI     = (24, 92, 71)
ORO        = (168, 133, 63)
ORO_HI     = (228, 197, 124)
CREMA      = (240, 233, 218)
CREMA_DIM  = (138, 133, 122)
CREMA_MUTE = (92, 89, 82)

FDIR = "/root/.claude/skills/canvas-design/canvas-fonts"
ITALIANA = f"{FDIR}/Italiana-Regular.ttf"
GLOOCK   = f"{FDIR}/Gloock-Regular.ttf"
JURA_L   = f"{FDIR}/Jura-Light.ttf"
JURA_M   = f"{FDIR}/Jura-Medium.ttf"
GEIST    = f"{FDIR}/GeistMono-Regular.ttf"
GEIST_B  = f"{FDIR}/GeistMono-Bold.ttf"
BIGSH_B  = f"{FDIR}/BigShoulders-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


# ── tipografía: espaciado manual, letra a letra ───────────────────────────────
def track_width(draw, text, font, tracking):
    if not text:
        return 0
    return sum(draw.textlength(c, font=font) for c in text) + tracking * (len(text) - 1)


def track(draw, xy, text, font, fill, tracking=0, anchor="lt"):
    """Dibuja texto con tracking. anchor: l/c/r + t/m/b"""
    x, y = xy
    total = track_width(draw, text, font, tracking)
    ha, va = anchor[0], anchor[1]
    if ha == "c":
        x -= total / 2
    elif ha == "r":
        x -= total
    asc, desc = font.getmetrics()
    if va == "m":
        y -= asc / 2
    elif va == "b":
        y -= asc
    for c in text:
        draw.text((x, y), c, font=font, fill=fill)
        x += draw.textlength(c, font=font) + tracking
    return total


# ── guilloché: acumulación paciente de una misma curva ────────────────────────
def epitrochoid(a, b, h, turns, steps):
    pts = []
    k = (a + b) / b
    for i in range(steps + 1):
        t = turns * 2 * math.pi * i / steps
        x = (a + b) * math.cos(t) - h * math.cos(k * t)
        y = (a + b) * math.sin(t) - h * math.sin(k * t)
        pts.append((x, y))
    return pts


def fit(pts, R):
    m = max(math.hypot(x, y) for x, y in pts) or 1.0
    s = R / m
    return [(x * s, y * s) for x, y in pts]


def guilloche_mask(size, cx, cy, specs):
    """Devuelve máscara L en resolución nativa; se traza a SSx y se reduce."""
    w, h = size
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    for sp in specs:
        pts = fit(epitrochoid(sp["a"], sp["b"], sp["h"], sp["turns"], sp["steps"]), sp["R"])
        rot = math.radians(sp.get("rot", 0))
        cs, sn = math.cos(rot), math.sin(rot)
        scr = [((x * cs - y * sn + cx) * SS, (x * sn + y * cs + cy) * SS) for x, y in pts]
        d.line(scr, fill=sp.get("v", 255), width=max(1, int(sp.get("lw", 1) * SS)), joint="curve")
    return m.resize((w, h), Image.LANCZOS)


def ring_mask(size, cx, cy, radii):
    w, h = size
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    for r, lw, v in radii:
        d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS],
                  outline=v, width=max(1, int(lw * SS)))
    return m.resize((w, h), Image.LANCZOS)


def tint(mask, color, opacity=1.0):
    """Convierte máscara L en capa RGBA del color dado."""
    layer = Image.new("RGBA", mask.size, color + (0,))
    a = mask.point(lambda v: int(v * opacity))
    layer.putalpha(a)
    return layer


# ── fondo ─────────────────────────────────────────────────────────────────────
def field(top, bottom, glow=None):
    col = Image.new("RGB", (1, H))
    px = col.load()
    for y in range(H):
        t = y / (H - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    img = col.resize((W, H), Image.LANCZOS)
    if glow:
        gx, gy, gr, gcol, gop = glow
        g = Image.new("L", (W // 4, H // 4), 0)
        gd = ImageDraw.Draw(g)
        gd.ellipse([(gx - gr) / 4, (gy - gr) / 4, (gx + gr) / 4, (gy + gr) / 4], fill=255)
        g = g.filter(ImageFilter.GaussianBlur(gr / 9)).resize((W, H), Image.LANCZOS)
        img = Image.alpha_composite(img.convert("RGBA"), tint(g, gcol, gop)).convert("RGB")
    return img


def grain(img, opacity=0.030, seed=5):
    rng = np.random.default_rng(seed)
    n = rng.normal(128, 46, (H, W)).clip(0, 255).astype(np.uint8)
    noise = Image.merge("RGB", (Image.fromarray(n),) * 3)
    return Image.blend(img.convert("RGB"), noise, opacity)


# ── recorte de producto ───────────────────────────────────────────────────────
def cutout(path, lmin=100, smax=0.08, erode=1, feather=0.8):
    """Recorte sobre fondo blanco, calidad de retoque.

    El mockup trae fondo puro (255) y una sombra proyectada que se degrada desde
    ~250 hasta ~110 al pegarse a la pieza. Ningún umbral de luminancia la separa
    del producto sin morderlo. Pero la sombra es GRIS NEUTRO y el producto no:
    o es muy oscuro (suela, felpa negra) o es cromático (verde, oro). Así que la
    inundación corre sobre la máscara «claro Y desaturado», entrando desde el
    marco: se traga fondo y sombra entera, y se detiene en la pieza.

    Al ser por conectividad, los blancos interiores (vivos, costuras, tipografía
    crema) quedan protegidos: están encerrados por píxeles que no son máscara y
    la inundación nunca los alcanza.
    """
    im = Image.open(path).convert("RGB")
    arr = np.asarray(im).astype(np.float32)
    L = arr.max(axis=2)
    sat = (L - arr.min(axis=2)) / np.maximum(L, 1.0)

    lab, _ = ndimage.label((L > lmin) & (sat < smax))
    border = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
    border.discard(0)
    in_bg = np.isin(lab, list(border)) if border else np.zeros(L.shape, bool)

    solid = ~in_bg
    if erode:
        solid = ndimage.binary_erosion(solid, iterations=erode, border_value=0)
    a = Image.fromarray((solid * 255).astype(np.uint8))
    if feather:
        a = a.filter(ImageFilter.GaussianBlur(feather))
    out = im.convert("RGBA")
    out.putalpha(a)
    return out.crop(out.getbbox())


DISPLAY_MAX_W = 872          # ancho máximo del titular: deja ~104 px de aire por lado


def fit_display(draw, text, path, size, tracking, max_w=DISPLAY_MAX_W):
    """Reduce el cuerpo hasta que el titular respire dentro de la caja.

    La retícula manda sobre el capricho: ningún titular toca el margen.
    """
    s = size
    while s > 10:
        f = F(path, s)
        if track_width(draw, text, f, tracking * s / size) <= max_w:
            return f, tracking * s / size
        s -= 1
    return F(path, s), tracking


def price_tag(draw, cx, y, amount, size=74, color=CREMA, tracking=3):
    """Cifra en Italiana + € en Jura (Italiana no trae el glifo del euro)."""
    fn, fe = F(ITALIANA, size), F(JURA_L, int(size * 0.50))
    wn = track_width(draw, amount, fn, tracking)
    we = draw.textlength("€", font=fe)
    gap = size * 0.20
    x = cx - (wn + gap + we) / 2
    asc, _ = fn.getmetrics()
    track(draw, (x, y - asc / 2), amount, fn, color + (255,), tracking, "lt")
    ea, _ = fe.getmetrics()
    draw.text((x + wn + gap, y - ea / 2 - size * 0.045), "€", font=fe, fill=color + (232,))


def place(canvas, sprite, cx, cy, target_w=None, target_h=None, shadow=None, halo=None):
    sw, sh = sprite.size
    if target_w:
        s = target_w / sw
    elif target_h:
        s = target_h / sh
    else:
        s = 1.0
    nw, nh = max(1, int(sw * s)), max(1, int(sh * s))
    sp = sprite.resize((nw, nh), Image.LANCZOS)
    x, y = int(cx - nw / 2), int(cy - nh / 2)
    if halo:
        # contraluz: sobre campo oscuro, una pieza negra necesita que el fondo
        # ceda un halo a su alrededor para que la silueta exista.
        blur, op, col = halo
        pad = int(blur * 3)
        m = Image.new("L", (nw + pad * 2, nh + pad * 2), 0)
        m.paste(sp.split()[3], (pad, pad))
        m = m.filter(ImageFilter.GaussianBlur(blur))
        canvas.alpha_composite(tint(m, col, op), (x - pad, y - pad))
    if shadow:
        blur, op, dy = shadow
        sh_l = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        m = sp.split()[3].filter(ImageFilter.GaussianBlur(blur))
        black = Image.new("RGBA", (nw, nh), (0, 0, 0, 255))
        black.putalpha(m.point(lambda v: int(v * op)))
        sh_l.paste(black, (x, y + dy), black)
        canvas.alpha_composite(sh_l)
    canvas.alpha_composite(sp, (x, y))
    return (x, y, x + nw, y + nh)


# ── marcas de registro / retícula de imprenta ─────────────────────────────────
def registration(draw, color=ORO, v=70):
    c = color + (v,)
    m, t = MARGIN, 26
    for (x, y, dx, dy) in [(m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)]:
        draw.line([x, y, x + dx * t, y], fill=c, width=1)
        draw.line([x, y, x, y + dy * t], fill=c, width=1)


def edge_ticks(draw, ys, color=ORO, v=52):
    for y in ys:
        draw.line([MARGIN - 14, y, MARGIN - 4, y], fill=color + (v,), width=1)
        draw.line([W - MARGIN + 4, y, W - MARGIN + 14, y], fill=color + (v,), width=1)


def rule(draw, y, half, color=ORO, v=90, lw=1):
    draw.line([W / 2 - half, y, W / 2 + half, y], fill=color + (v,), width=lw)


def vlabel(canvas, xy, text, font, fill, tracking, side="l"):
    """Etiqueta vertical rotada, al margen."""
    tmp = Image.new("RGBA", (900, 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    tw = track(d, (0, 20), text, font, fill, tracking)
    tmp = tmp.crop((0, 0, int(tw) + 4, 60))
    tmp = tmp.rotate(90 if side == "l" else -90, expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(tmp, (int(xy[0]), int(xy[1])))


# ── corona: marca de la casa, trazada ────────────────────────────────────────
def crown_mask(size, cx, cy, w, h, lw=2.0, filled=False):
    m = Image.new("L", (size[0] * SS, size[1] * SS), 0)
    d = ImageDraw.Draw(m)
    l, r = cx - w / 2, cx + w / 2
    b, t = cy + h / 2, cy - h / 2
    dip = b - h * 0.44
    pts = [(l, b), (l, t + h * 0.30), (l + w * 0.185, dip),
           (cx - w * 0.155, t + h * 0.10), (cx, dip - h * 0.03),
           (cx + w * 0.155, t + h * 0.10), (r - w * 0.185, dip),
           (r, t + h * 0.30), (r, b)]
    sp = [(x * SS, y * SS) for x, y in pts]
    band = [l * SS, (b + h * 0.10) * SS, r * SS, (b + h * 0.26) * SS]
    if filled:
        d.polygon(sp, fill=255)
        d.rectangle(band, fill=255)
    else:
        d.line(sp + [sp[0]], fill=255, width=max(1, int(lw * SS)), joint="curve")
        d.rectangle(band, outline=255, width=max(1, int(lw * SS)))
    for px, py in [(l + w * 0.185, dip), (cx, dip - h * 0.03), (r - w * 0.185, dip)]:
        rr = max(2.0, w * 0.030)
        d.ellipse([(px - rr) * SS, (py - rr) * SS, (px + rr) * SS, (py + rr) * SS], fill=255)
    return m.resize(size, Image.LANCZOS)
