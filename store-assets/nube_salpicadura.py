#!/usr/bin/env python3
"""Cápsulas 'Nube Imperial' y 'Salpicadura Atelier' — Street Royalty Hood.

Genera los archivos de impresión (DTG transparentes + tiles all-over seamless)
para Printful. Run 2026-07-18.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = os.environ.get("NS_OUT", "/tmp/ns_out")
os.makedirs(OUT, exist_ok=True)

# Paleta
NAVY_BG = (16, 28, 51, 255)        # fondo navy profundo
GOLD = (201, 162, 39, 255)
GOLD_LIGHT = (228, 197, 107, 255)
IVORY = (243, 237, 224, 255)
INK = (30, 44, 73, 255)            # tinta navy sobre marfil
BURDEOS = (110, 20, 35, 255)
S_NAVY = (27, 42, 74, 255)
S_ORO = (185, 146, 41, 255)
S_NEGRO = (24, 22, 24, 255)
WHITE = (255, 255, 255, 255)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# ----------------------------------------------------------------------------
# NUBE IMPERIAL — nube auspiciosa (xiangyun/ruyi) dibujada con arcos gruesos
# ----------------------------------------------------------------------------

def _spiral_curl(draw, cx, cy, r, w, color, turns=1.55, start_deg=210):
    """Espiral de Arquímedes trazada con segmentos, remate en punto."""
    steps = max(int(90 * turns), 40)
    pts = []
    for i in range(steps + 1):
        t = i / steps
        ang = math.radians(start_deg) + t * turns * 2 * math.pi
        rad = r * (0.18 + 0.82 * t)
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    lw = max(int(w), 2)
    draw.line(pts, fill=color, width=lw, joint="curve")
    x0, y0 = pts[0]
    draw.ellipse([x0 - lw * 0.9, y0 - lw * 0.9, x0 + lw * 0.9, y0 + lw * 0.9], fill=color)


def cloud_motif(size, color, accent=None, rng=None):
    """Nube auspiciosa: rizo central grande, dos rizos laterales y cola."""
    rng = rng or random.Random(0)
    S = int(size)
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = max(S // 34, 3)
    cx, cy = S * 0.5, S * 0.44
    r_main = S * 0.185
    # rizo central
    _spiral_curl(d, cx, cy, r_main, w, color, turns=1.65, start_deg=250)
    # rizos laterales, más bajos y pequeños
    for sgn in (-1, 1):
        _spiral_curl(
            d, cx + sgn * S * 0.235, cy + S * 0.075, r_main * 0.62, w * 0.85, color,
            turns=1.35, start_deg=270 - sgn * 40,
        )
    # contorno inferior que une los rizos (arco ancho)
    d.arc([cx - S * 0.335, cy - S * 0.10, cx + S * 0.335, cy + S * 0.26],
          start=15, end=165, fill=color, width=int(w * 1.05))
    # cola: dos trazos horizontales escalonados con remate
    for i, (dx, dy, ln) in enumerate([(0.08, 0.33, 0.30), (0.02, 0.40, 0.20)]):
        y = cy + S * dy
        x0 = cx - S * ln
        x1 = cx + S * (ln * 0.55) - i * S * 0.06
        d.line([(x0, y), (x1, y)], fill=color, width=int(w * 0.9))
        d.ellipse([x1 - w, y - w, x1 + w, y + w], fill=color)
        # gancho al final de la cola
        d.arc([x0 - S * 0.05, y - S * 0.05, x0 + S * 0.05, y + S * 0.05],
              start=90, end=270, fill=color, width=int(w * 0.9))
    if accent:
        # perla interior del rizo central
        d.ellipse([cx - w * 1.4, cy - w * 1.4, cx + w * 1.4, cy + w * 1.4], fill=accent)
    return img


def dot_diamond(size, color):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size * 0.09
    for dx, dy in [(0, -0.3), (0, 0.3), (-0.3, 0), (0.3, 0)]:
        x, y = size * 0.5 + dx * size, size * 0.5 + dy * size
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)
    return img


def paste_wrapped(canvas, tile, x, y):
    """Pega con wraparound toroidal para tiles seamless."""
    W, H = canvas.size
    w, h = tile.size
    for ox in (-W, 0, W):
        for oy in (-H, 0, H):
            px, py = int(x + ox), int(y + oy)
            if px < W and py < H and px + w > 0 and py + h > 0:
                canvas.alpha_composite(tile, (px, py))


def cloud_field(W, H, bg, main_color, accent_color, seed, density=1.0, minor_color=None):
    """Patrón all-over seamless de nubes en rejilla diagonal con jitter."""
    rng = random.Random(seed)
    canvas = Image.new("RGBA", (W, H), bg)
    cell = int(430 / density)
    cols = max(round(W / cell), 1)
    rows = max(round(H / (cell * 0.85)), 1)
    cw, ch = W / cols, H / rows
    for j in range(rows):
        for i in range(cols):
            x = (i + 0.5) * cw + (cw * 0.5 if j % 2 else 0)
            y = (j + 0.5) * ch
            x += rng.uniform(-cw * 0.12, cw * 0.12)
            y += rng.uniform(-ch * 0.10, ch * 0.10)
            big = (i + 2 * j) % 3 != 1
            s = cw * (rng.uniform(0.88, 1.02) if big else rng.uniform(0.52, 0.62))
            col = main_color
            if minor_color and rng.random() < 0.18:
                col = minor_color
            m = cloud_motif(s, col, accent=accent_color if big and rng.random() < 0.6 else None,
                            rng=rng)
            m = m.rotate(rng.uniform(-8, 8), expand=True, resample=Image.BICUBIC)
            paste_wrapped(canvas, m, x - m.size[0] / 2, y - m.size[1] / 2)
            if not big and rng.random() < 0.7:
                dd = dot_diamond(int(cw * 0.16), accent_color or main_color)
                paste_wrapped(canvas, dd, x + cw * 0.42 - dd.size[0] / 2,
                              y - ch * 0.38 - dd.size[1] / 2)
    return canvas


def crown(width, color, lw=None):
    """Corona SRH: tres puntas con perlas, trazada en línea."""
    W = int(width)
    H = int(width * 0.72)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = lw or max(W // 26, 3)
    bx0, bx1 = W * 0.10, W * 0.90
    by = H * 0.80
    top = H * 0.18
    mid = H * 0.40
    pts = [
        (bx0, by), (bx0, mid), (W * 0.32, H * 0.58), (W * 0.5, top),
        (W * 0.68, H * 0.58), (bx1, mid), (bx1, by), (bx0, by),
    ]
    d.line(pts, fill=color, width=lw, joint="curve")
    r = lw * 1.15
    for x, y in [(bx0, mid), (W * 0.5, top), (bx1, mid)]:
        d.ellipse([x - r, y - r * 3.0, x + r, y - r], fill=color)
    d.line([(bx0, by + lw * 2.0), (bx1, by + lw * 2.0)], fill=color, width=lw)
    return img


def spaced_text(text, font_size, color, spacing=0.32):
    f = ImageFont.truetype(FONT_BOLD, font_size)
    widths = [f.getbbox(ch)[2] for ch in text]
    gap = int(font_size * spacing)
    W = sum(widths) + gap * (len(text) - 1) + 8
    H = int(font_size * 1.5)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 4
    for ch, w in zip(text, widths):
        d.text((x, H * 0.12), ch, font=f, fill=color)
        x += w + gap
    return img.crop(img.getbbox())


def center_paste(canvas, img, cx, cy):
    canvas.alpha_composite(img, (int(cx - img.size[0] / 2), int(cy - img.size[1] / 2)))


def nube_dtg(W, H, name):
    """Composición DTG (fondo transparente) para camiseta/hoodie navy."""
    rng = random.Random(hash(name) & 0xFFFF)
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx = W / 2
    # emblema: corona sobre banco de nubes
    cw_ = W * 0.30
    center_paste(art, crown(cw_, GOLD), cx, H * 0.155)
    band_y = H * 0.36
    specs = [
        (cx - W * 0.26, band_y + H * 0.028, W * 0.30, GOLD, GOLD_LIGHT),
        (cx + W * 0.255, band_y + H * 0.020, W * 0.27, GOLD, None),
        (cx, band_y - H * 0.045, W * 0.40, GOLD, GOLD_LIGHT),
        (cx - W * 0.395, band_y - H * 0.052, W * 0.185, IVORY, None),
        (cx + W * 0.385, band_y - H * 0.062, W * 0.16, IVORY, None),
    ]
    for x, y, s, col, acc in specs:
        m = cloud_motif(s, col, accent=acc, rng=rng)
        center_paste(art, m, x, y)
    # texto
    t1 = spaced_text("NUBE IMPERIAL", int(W * 0.052), GOLD_LIGHT, 0.42)
    center_paste(art, t1, cx, H * 0.545)
    t2 = spaced_text("STREET ROYALTY · SRH", int(W * 0.024), IVORY, 0.34)
    center_paste(art, t2, cx, H * 0.585)
    # nubes menores flotando abajo, asimétricas
    for x, y, s in [(cx - W * 0.24, H * 0.68, W * 0.14),
                    (cx + W * 0.19, H * 0.735, W * 0.185),
                    (cx - W * 0.04, H * 0.815, W * 0.115)]:
        m = cloud_motif(s, GOLD, rng=rng)
        center_paste(art, m, x, y)
    dd = dot_diamond(int(W * 0.05), GOLD_LIGHT)
    center_paste(art, dd, cx + W * 0.30, H * 0.66)
    center_paste(art, dd, cx - W * 0.31, H * 0.79)
    return art


# ----------------------------------------------------------------------------
# SALPICADURA ATELIER — splatter de pintura con física simple
# ----------------------------------------------------------------------------

def _blob(d, x, y, r, color, rng):
    steps = 26
    pts = []
    wob = [rng.uniform(0.72, 1.28) for _ in range(steps)]
    for i in range(steps):
        ang = i / steps * 2 * math.pi
        k = (wob[i] + wob[(i + 1) % steps]) / 2
        pts.append((x + r * k * math.cos(ang), y + r * k * math.sin(ang)))
    d.polygon(pts, fill=color)


def splat(layer, x, y, size, color, rng, streak_p=0.45):
    d = ImageDraw.Draw(layer)
    _blob(d, x, y, size, color, rng)
    # satélites
    for _ in range(rng.randint(4, 9)):
        ang = rng.uniform(0, 2 * math.pi)
        dist = size * rng.uniform(1.3, 3.2)
        r = size * rng.uniform(0.08, 0.28)
        _blob(d, x + dist * math.cos(ang), y + dist * math.sin(ang), r, color, rng)
    # chorretón direccional
    if rng.random() < streak_p:
        ang = rng.uniform(0, 2 * math.pi)
        L = size * rng.uniform(3.0, 7.0)
        n = 14
        for i in range(n):
            t = i / n
            r = size * (0.42 * (1 - t) + 0.06)
            px = x + L * t * math.cos(ang)
            py = y + L * t * math.sin(ang)
            d.ellipse([px - r, py - r, px + r, py + r], fill=color)
        r = size * 0.16
        px, py = x + L * math.cos(ang), y + L * math.sin(ang)
        d.ellipse([px - r, py - r, px + r, py + r], fill=color)


def mist(layer, W, H, n, color, rng, rmax=5):
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.uniform(1.2, rmax)
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)


def splatter_field(W, H, bg, seed, scale=1.0, density=1.0, seamless=False):
    """Campo all-over de salpicaduras en la paleta de la casa."""
    rng = random.Random(seed)
    canvas = Image.new("RGBA", (W, H), bg)
    order = [(S_ORO, 0.9), (S_NAVY, 1.0), (BURDEOS, 1.0), (S_NEGRO, 0.25)]
    for color, mult in order:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        n = int(10 * density * mult * (W * H) / (2600 * 2600))
        for _ in range(max(n, 2)):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            s = scale * rng.uniform(18, 68)
            if seamless:
                tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                splat(tmp, x, y, s, color, rng)
                for ox in (-W, 0, W):
                    for oy in (-H, 0, H):
                        if ox or oy:
                            layer.alpha_composite(tmp, (ox, oy))
                layer.alpha_composite(tmp, (0, 0))
            else:
                splat(layer, x, y, s, color, rng)
        mist(layer, W, H, int(160 * density * mult * (W * H) / (2600 * 2600)),
             color, rng, rmax=4 * scale)
        canvas.alpha_composite(layer)
    return canvas


def crown_solid(width):
    """Silueta sólida de corona (máscara para espacio negativo)."""
    W = int(width)
    H = int(width * 0.72)
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    bx0, bx1 = W * 0.08, W * 0.92
    by0, by1 = H * 0.62, H * 0.86
    pts = [(bx0, by0), (bx0, H * 0.30), (W * 0.33, H * 0.52), (W * 0.5, H * 0.10),
           (W * 0.67, H * 0.52), (bx1, H * 0.30), (bx1, by0)]
    d.polygon(pts, fill=255)
    d.rectangle([bx0, by0, bx1, by1], fill=255)
    r = W * 0.045
    for x, y in [(bx0, H * 0.30), (W * 0.5, H * 0.10), (bx1, H * 0.30)]:
        d.ellipse([x - r, y - r * 2.6, x + r, y - r * 0.6], fill=255)
    return img


def salpicadura_dtg(W, H, name, band="diag"):
    """Composición DTG: splatter con corona en espacio negativo."""
    rng = random.Random(hash(name) & 0xFFFF)
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cy = W / 2, H * 0.34
    # campo de splatter concentrado alrededor de la corona (para que el
    # recorte en negativo se lea con fuerza)
    field = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    n_big = 52
    for i in range(n_big):
        t = i / n_big
        if band == "diag":
            bx = cx + rng.gauss(0, W * 0.20)
            by = cy + rng.gauss(0, H * 0.085) - (bx - cx) * 0.22
        else:  # vertical
            bx = cx + rng.gauss(0, W * 0.14)
            by = H * (0.12 + 0.50 * t) + rng.uniform(-H * 0.03, H * 0.03)
        color = [S_ORO, S_NAVY, BURDEOS, BURDEOS, S_NAVY][i % 5]
        splat(field, bx, by, rng.uniform(16, 50), color, rng, streak_p=0.5)
    # bruma con caída radial alrededor de la corona
    d_m = ImageDraw.Draw(field)
    for col in (BURDEOS, S_NAVY, S_ORO):
        for _ in range(260):
            ang = rng.uniform(0, 2 * math.pi)
            rad = abs(rng.gauss(0, 0.55))
            x = cx + math.cos(ang) * rad * W * 0.42
            y = cy + math.sin(ang) * rad * H * 0.16
            r = rng.uniform(1.2, 4)
            d_m.ellipse([x - r, y - r, x + r, y + r], fill=col)
    # espacio negativo: recorta la corona del campo
    cm = crown_solid(W * 0.34)
    mask = Image.new("L", (W, H), 255)
    mask.paste(Image.new("L", cm.size, 0), (int(cx - cm.size[0] / 2), int(cy - cm.size[1] / 2)),
               cm)
    field.putalpha(Image.composite(field.getchannel("A"), Image.new("L", (W, H), 0), mask))
    art.alpha_composite(field)
    # contorno fino de la corona para afirmar la silueta
    ol = crown(W * 0.34, S_NEGRO, lw=max(int(W * 0.006), 3))
    center_paste(art, ol, cx, cy + W * 0.34 * 0.72 * 0.5 - ol.size[1] / 2 + 2)
    t1 = spaced_text("SALPICADURA ATELIER", int(W * 0.040), S_NEGRO, 0.34)
    center_paste(art, t1, cx, H * 0.60)
    t2 = spaced_text("STREET ROYALTY · HECHO A MANO DIGITAL", int(W * 0.019), BURDEOS, 0.28)
    center_paste(art, t2, cx, H * 0.638)
    return art


# ----------------------------------------------------------------------------
# Render de todos los archivos
# ----------------------------------------------------------------------------

def save(img, name, mode="RGBA"):
    p = os.path.join(OUT, name)
    if mode == "RGB":
        img = img.convert("RGB")
    img.save(p)
    print("wrote", p, img.size)


if __name__ == "__main__":
    # --- Nube Imperial ---
    save(nube_dtg(2400, 3000, "nube-tee"), "nube_tee_print.png")
    save(nube_dtg(2400, 2250, "nube-hoodie"), "nube_hoodie_print.png")
    save(cloud_field(2600, 2600, NAVY_BG, GOLD, GOLD_LIGHT, seed=71, density=1.0,
                     minor_color=IVORY), "nube_hitop_tile.png", "RGB")
    save(cloud_field(2600, 2600, IVORY, INK, GOLD, seed=75, density=0.92),
         "nube_slipon_tile.png", "RGB")
    save(cloud_field(2000, 2000, NAVY_BG, GOLD, GOLD_LIGHT, seed=18, density=1.35),
         "nube_socks_print.png", "RGB")
    save(cloud_field(2600, 2600, NAVY_BG, GOLD, GOLD_LIGHT, seed=65, density=1.15,
                     minor_color=IVORY), "nube_bucket_out.png", "RGB")
    save(cloud_field(1200, 1200, IVORY, INK, None, seed=66, density=1.1),
         "nube_bucket_in.png", "RGB")

    # --- Salpicadura Atelier ---
    save(salpicadura_dtg(2400, 3000, "salp-tee", band="diag"), "salp_tee_print.png")
    save(salpicadura_dtg(2400, 3000, "salp-sweat", band="diag"), "salp_sweat_print.png")
    save(salpicadura_dtg(2400, 3000, "salp-ls", band="vert"), "salp_ls_print.png")
    save(splatter_field(4500, 4500, WHITE, seed=31, scale=1.6, density=1.1, seamless=True),
         "salp_lona_tile.png", "RGB")
    save(splatter_field(3900, 6600, WHITE, seed=32, scale=1.5, density=1.2, seamless=True),
         "salp_deportivas_print.png", "RGB")
    save(splatter_field(3300, 3900, WHITE, seed=33, scale=1.4, density=1.15, seamless=True),
         "salp_chanclas_print.png", "RGB")
