#!/usr/bin/env python3
"""Cápsula "Neón Real" — generador de print files para SRHOOD (run 2026-07-18).

Estética: letreros de neón nocturnos. Cada pieza es una composición distinta
(letrero corona, badge circular, wordmark, all-over pared, pulso, zigzag).
Render con supersampling ×2 y glow multicapa (blur gaussiano en 3 radios +
núcleo caliente) para que el tubo parezca real y aguante impresión DTG/sublimación.

Salida (dimensiones = mismas que la cápsula Vidriera anterior):
  neon_tee.png    2400×3000  transparente (camiseta negra, DTG)
  neon_hoodie.png 2250×2250  transparente (hoodie negro, DTG)
  neon_sweat.png  2400×3000  transparente (sudadera negra, DTG)
  neon_sq.png     2400×2400  opaco (zapatillas altas, sublimación AOP)
  neon_ath.png    2000×3400  opaco (deportivas mujer, sublimación AOP)
  neon_socks.png  2000×2000  opaco (calcetines sublimados)
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 2  # supersampling
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

MAGENTA = (255, 45, 149)
CYAN = (35, 230, 255)
AMBER = (255, 191, 63)
LILA = (178, 102, 255)
NIGHT = (10, 11, 20, 255)

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, int(size))


def hot_core(color):
    """Color del núcleo del tubo: el color mezclado con blanco cálido."""
    return tuple(int(c * 0.35 + 255 * 0.65) for c in color)


def glow_composite(base, mask, color, width):
    """Compone sobre `base` un neón a partir de `mask` (L, blanco = tubo)."""
    layers = [
        (width * 7.0, 0.32),   # halo ancho
        (width * 3.2, 0.55),   # halo medio
        (width * 1.3, 0.85),   # borde brillante
    ]
    for radius, alpha in layers:
        blur = mask.filter(ImageFilter.GaussianBlur(radius))
        tint = Image.new("RGBA", base.size, color + (0,))
        tint.putalpha(blur.point(lambda p, a=alpha: int(p * a)))
        base.alpha_composite(tint)
    core_mask = mask.filter(ImageFilter.GaussianBlur(width * 0.22))
    core = Image.new("RGBA", base.size, hot_core(color) + (0,))
    core.putalpha(core_mask)
    base.alpha_composite(core)
    return base


class Neon:
    """Acumula trazos por color sobre máscaras y los compone con glow."""

    def __init__(self, size):
        self.size = size
        self.masks = {}

    def _mask(self, color, width):
        key = (color, round(width, 1))
        if key not in self.masks:
            self.masks[key] = Image.new("L", self.size, 0)
        return ImageDraw.Draw(self.masks[key]), self.masks[key]

    def line(self, pts, color, width, gap=0.0):
        d, _ = self._mask(color, width)
        if gap <= 0:
            d.line(pts, fill=255, width=int(width), joint="curve")
            for p in (pts[0], pts[-1]):
                d.ellipse([p[0] - width / 2, p[1] - width / 2,
                           p[0] + width / 2, p[1] + width / 2], fill=255)
            return
        # segmentos con huecos (uniones de tubo real)
        for a, b in zip(pts[:-1], pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < gap * 2.5:
                continue
            ux, uy = dx / ln, dy / ln
            a2 = (a[0] + ux * gap, a[1] + uy * gap)
            b2 = (b[0] - ux * gap, b[1] - uy * gap)
            d.line([a2, b2], fill=255, width=int(width))
            for p in (a2, b2):
                d.ellipse([p[0] - width / 2, p[1] - width / 2,
                           p[0] + width / 2, p[1] + width / 2], fill=255)

    def arc(self, bbox, start, end, color, width):
        d, _ = self._mask(color, width)
        d.arc(bbox, start, end, fill=255, width=int(width))

    def ellipse_outline(self, bbox, color, width):
        d, _ = self._mask(color, width)
        d.ellipse(bbox, outline=255, width=int(width))

    def dot(self, xy, r, color):
        d, _ = self._mask(color, max(2, r))
        d.ellipse([xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r], fill=255)

    def text(self, xy, s, fnt, color, width, anchor="mm", spacing_px=0):
        d, _ = self._mask(color, width)
        if spacing_px <= 0:
            d.text(xy, s, font=fnt, fill=0, stroke_width=int(width), stroke_fill=255,
                   anchor=anchor)
            return
        # tracking manual
        total = sum(d.textlength(ch, font=fnt) + spacing_px for ch in s) - spacing_px
        x = xy[0] - total / 2 if anchor[0] == "m" else xy[0]
        for ch in s:
            d.text((x, xy[1]), ch, font=fnt, fill=0, stroke_width=int(width),
                   stroke_fill=255, anchor="l" + anchor[1])
            x += d.textlength(ch, font=fnt) + spacing_px

    def arc_text(self, center, radius, s, fnt, color, width, a0, a1, flip=False):
        """Texto siguiendo un arco (grados; 0 = derecha, sentido horario)."""
        d, _ = self._mask(color, width)
        n = len(s)
        for i, ch in enumerate(s):
            t = i / max(1, n - 1)
            ang = math.radians(a0 + (a1 - a0) * t)
            x = center[0] + radius * math.cos(ang)
            y = center[1] + radius * math.sin(ang)
            rot = -math.degrees(ang) - 90 if not flip else -math.degrees(ang) + 90
            size = fnt.size * 3
            tile = Image.new("L", (size, size), 0)
            td = ImageDraw.Draw(tile)
            td.text((size / 2, size / 2), ch, font=fnt, fill=0,
                    stroke_width=int(width), stroke_fill=255, anchor="mm")
            tile = tile.rotate(rot, resample=Image.BICUBIC, expand=False)
            _, mask_img = self._mask(color, width)
            mask_img.paste(tile, (int(x - size / 2), int(y - size / 2)),
                           tile)

    def render(self, base):
        for (color, width), mask in self.masks.items():
            glow_composite(base, mask, color, width)
        return base


def crown_path(cx, cy, w, h):
    """Corona de 3 puntas estilo tubo: base + zigzag + gemas."""
    left, right = cx - w / 2, cx + w / 2
    base_y, top_y = cy + h / 2, cy - h / 2
    mid1 = cx - w / 4
    mid2 = cx + w / 4
    outline = [
        (left, base_y), (left, base_y - h * 0.18),
        (left, top_y + h * 0.30), (mid1, base_y - h * 0.42),
        (cx, top_y), (mid2, base_y - h * 0.42),
        (right, top_y + h * 0.30), (right, base_y - h * 0.18),
        (right, base_y), (left, base_y),
    ]
    return outline


def vignette(img, strength=0.55):
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([-w * 0.35, -h * 0.35, w * 1.35, h * 1.35], fill=int(255 * strength))
    m = m.filter(ImageFilter.GaussianBlur(min(w, h) * 0.18))
    dark = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    out = Image.composite(img, dark, m.point(lambda p: 255 - (255 - p)))
    return Image.blend(dark.convert("RGBA"), img, 1.0)  # vignette sutil via overlay


def night_bg(size, grid=False, grid_step=260, grid_alpha=16):
    img = Image.new("RGBA", size, NIGHT)
    d = ImageDraw.Draw(img)
    # degradado vertical muy sutil (más azul arriba)
    w, h = size
    top = (13, 15, 30)
    for y in range(0, h, 4):
        t = y / h
        c = tuple(int(top[i] * (1 - t) + NIGHT[i] * t) for i in range(3))
        d.rectangle([0, y, w, y + 4], fill=c + (255,))
    if grid:
        gc = (60, 70, 110, grid_alpha)
        for x in range(0, w + grid_step, grid_step):
            d.line([(x, 0), (x, h)], fill=gc, width=3 * SS)
        for y in range(0, h + grid_step, grid_step):
            d.line([(0, y), (w, y)], fill=gc, width=3 * SS)
    return img


def sparkle(neon, x, y, r, color, width):
    neon.line([(x - r, y), (x + r, y)], color, width)
    neon.line([(x, y - r), (x, y + r)], color, width)
    neon.line([(x - r * 0.5, y - r * 0.5), (x + r * 0.5, y + r * 0.5)], color, width * 0.7)
    neon.line([(x - r * 0.5, y + r * 0.5), (x + r * 0.5, y - r * 0.5)], color, width * 0.7)


# ----------------------------------------------------------------------------
def make_tee():
    """Camiseta: letrero 'corona + STREET ROYALTY' sobre transparencia."""
    W, H = 2400 * SS, 3000 * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    n = Neon((W, H))
    cx = W / 2
    # corona principal en magenta
    cw, ch = W * 0.52, H * 0.22
    cy = H * 0.30
    n.line(crown_path(cx, cy, cw, ch), MAGENTA, 26 * SS, gap=20 * SS)
    # gemas: puntos amber sobre las puntas
    for px, py in [(cx - cw / 2, cy - ch * 0.20), (cx, cy - ch / 2), (cx + cw / 2, cy - ch * 0.20)]:
        n.dot((px, py - 60 * SS), 16 * SS, AMBER)
    # wordmark cian
    f1 = font(F_BOLD, 150 * SS)
    n.text((cx, H * 0.52), "STREET", f1, CYAN, 9 * SS, spacing_px=70 * SS)
    n.text((cx, H * 0.60), "ROYALTY", f1, CYAN, 9 * SS, spacing_px=70 * SS)
    # subrayado con rabo
    y_u = H * 0.655
    n.line([(cx - W * 0.26, y_u), (cx + W * 0.20, y_u), (cx + W * 0.24, y_u - 40 * SS)],
           MAGENTA, 14 * SS)
    # tagline
    f2 = font(F_BOLD, 54 * SS)
    n.text((cx, H * 0.72), "LA CORONA NUNCA DUERME", f2, AMBER, 4 * SS, spacing_px=26 * SS)
    # chispas
    sparkle(n, cx - W * 0.34, H * 0.24, 40 * SS, CYAN, 8 * SS)
    sparkle(n, cx + W * 0.36, H * 0.35, 30 * SS, MAGENTA, 7 * SS)
    n.render(img)
    return img.resize((2400, 3000), Image.LANCZOS)


def make_hoodie():
    """Hoodie: badge circular 'OPEN 24/7' con corona ámbar."""
    W, H = 2250 * SS, 2250 * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    n = Neon((W, H))
    cx, cy = W / 2, H / 2
    R = W * 0.40
    n.ellipse_outline([cx - R, cy - R, cx + R, cy + R], CYAN, 16 * SS)
    R2 = R * 0.86
    n.ellipse_outline([cx - R2, cy - R2, cx + R2, cy + R2], CYAN, 7 * SS)
    # corona central ámbar
    cw, ch = W * 0.36, H * 0.17
    n.line(crown_path(cx, cy + H * 0.01, cw, ch), AMBER, 22 * SS, gap=16 * SS)
    # texto en arco
    f_arc = font(F_BOLD, 92 * SS)
    n.arc_text((cx, cy), R * 0.70, "STREET ROYALTY", f_arc, MAGENTA, 6 * SS, -168, -12)
    n.arc_text((cx, cy), R * 0.70, "OPEN 24/7", f_arc, MAGENTA, 6 * SS, 152, 28, flip=True)
    # separadores
    for ang in (-190, 10):
        a = math.radians(ang)
        n.dot((cx + R * 0.70 * math.cos(a), cy + R * 0.70 * math.sin(a)), 14 * SS, AMBER)
    n.render(img)
    return img.resize((2250, 2250), Image.LANCZOS)


def make_sweat():
    """Sudadera: wordmark apilado STAY/ROYAL con eco doble."""
    W, H = 2400 * SS, 3000 * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    n = Neon((W, H))
    cx = W / 2
    f_big = font(F_BOLD, 330 * SS)
    # eco desplazado (lila, fino) detrás
    off = 22 * SS
    n.text((cx + off, H * 0.335 + off), "STAY", f_big, LILA, 5 * SS, spacing_px=40 * SS)
    n.text((cx + off, H * 0.50 + off), "ROYAL", f_big, LILA, 5 * SS, spacing_px=40 * SS)
    # principal
    n.text((cx, H * 0.335), "STAY", f_big, CYAN, 11 * SS, spacing_px=40 * SS)
    n.text((cx, H * 0.50), "ROYAL", f_big, MAGENTA, 11 * SS, spacing_px=40 * SS)
    # mini corona ámbar arriba a la derecha del STAY
    n.line(crown_path(cx + W * 0.30, H * 0.245, W * 0.11, H * 0.045), AMBER, 10 * SS)
    # base: línea + texto pequeño
    y_u = H * 0.585
    n.line([(cx - W * 0.28, y_u), (cx + W * 0.28, y_u)], AMBER, 8 * SS)
    f2 = font(F_BOLD, 50 * SS)
    n.text((cx, H * 0.635), "NEÓN REAL · SRHOOD", f2, CYAN, 4 * SS, spacing_px=24 * SS)
    n.render(img)
    return img.resize((2400, 3000), Image.LANCZOS)


def motif_crown(n, x, y, s, color, w):
    n.line(crown_path(x, y, s, s * 0.55), color, w, gap=max(4 * SS, s * 0.05))


def motif_bolt(n, x, y, s, color, w):
    pts = [(x + s * 0.15, y - s * 0.5), (x - s * 0.2, y + s * 0.05),
           (x + s * 0.02, y + s * 0.05), (x - s * 0.15, y + s * 0.5)]
    n.line(pts, color, w)


def motif_srh(n, x, y, s, color, w):
    f = font(F_BOLD, s * 0.62)
    n.text((x, y), "SRH", f, color, w, spacing_px=s * 0.06)


def motif_star(n, x, y, s, color, w):
    sparkle_r = s * 0.4
    n.line([(x - sparkle_r, y), (x + sparkle_r, y)], color, w)
    n.line([(x, y - sparkle_r), (x, y + sparkle_r)], color, w)


def make_hightop():
    """Zapatillas altas: pared nocturna con letreros mini colgados en diagonal."""
    W, H = 2400 * SS, 2400 * SS
    img = night_bg((W, H), grid=True, grid_step=int(200 * SS), grid_alpha=22)
    n = Neon((W, H))
    motifs = [
        (motif_crown, MAGENTA, 13 * SS), (motif_bolt, CYAN, 12 * SS),
        (motif_srh, AMBER, 5 * SS), (motif_star, LILA, 8 * SS),
    ]
    random.seed(47)
    step = 400 * SS
    k = 0
    for row, y in enumerate(range(int(step * 0.5), H + step, step)):
        for col, x in enumerate(range(int(step * 0.5), W + step, step)):
            fn, color, w = motifs[k % len(motifs)]
            k += 1
            jx = x + (step * 0.5 if row % 2 else 0) + random.randint(-30, 30) * SS
            jy = y + random.randint(-30, 30) * SS
            s = step * (0.42 + random.random() * 0.12)
            fn(n, jx % (W + step * 0.2), jy, s, color, w)
    n.render(img)
    return img.resize((2400, 2400), Image.LANCZOS).convert("RGB")


def make_athletic():
    """Deportivas mujer: pulso neón (EKG) horizontal sobre noche."""
    W, H = 2000 * SS, 3400 * SS
    img = night_bg((W, H))
    n = Neon((W, H))
    random.seed(11)

    def pulse(y0, color, width, amp, period):
        pts, x = [], -50 * SS
        while x < W + 50 * SS:
            pts.append((x, y0))
            x += period * (0.7 + random.random() * 0.6)
            # pico tipo latido
            p = period * 0.5
            pts += [(x, y0), (x + p * 0.12, y0 - amp * 0.35), (x + p * 0.28, y0 + amp),
                    (x + p * 0.45, y0 - amp * 1.35), (x + p * 0.62, y0 + amp * 0.25),
                    (x + p * 0.75, y0)]
            x += p
        n.line(pts, color, width)

    lanes = int(3400 / 300)
    for i in range(lanes):
        y = H * (0.06 + 0.088 * i)
        if i % 3 == 1:
            pulse(y, MAGENTA, 12 * SS, 90 * SS, 700 * SS)
        elif i % 3 == 2:
            pulse(y, AMBER, 9 * SS, 60 * SS, 900 * SS)
        else:
            pulse(y, CYAN, 12 * SS, 80 * SS, 800 * SS)
    # polvo de estrellas
    for _ in range(90):
        x, y = random.random() * W, random.random() * H
        n.dot((x, y), random.choice([4, 5, 7]) * SS, random.choice([CYAN, MAGENTA, AMBER]))
    n.render(img)
    return img.resize((2000, 3400), Image.LANCZOS).convert("RGB")


def make_socks():
    """Calcetines: zigzag vertical neón + coronas mini."""
    W, H = 2000 * SS, 2000 * SS
    img = night_bg((W, H))
    n = Neon((W, H))
    step_x = 250 * SS
    amp = 90 * SS
    colors = [CYAN, MAGENTA, AMBER]
    for i, x0 in enumerate(range(int(step_x * 0.6), W + step_x, step_x)):
        color = colors[i % 3]
        pts, y = [], -40 * SS
        left = True
        while y < H + 40 * SS:
            pts.append((x0 + (amp if left else -amp) / 2, y))
            left = not left
            y += 160 * SS
        n.line(pts, color, 11 * SS)
    random.seed(7)
    for _ in range(14):
        x, y = random.random() * W, random.random() * H
        motif_crown(n, x, y, 90 * SS, random.choice(colors), 7 * SS)
    n.render(img)
    return img.resize((2000, 2000), Image.LANCZOS).convert("RGB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    jobs = [
        ("neon_tee.png", make_tee), ("neon_hoodie.png", make_hoodie),
        ("neon_sweat.png", make_sweat), ("neon_sq.png", make_hightop),
        ("neon_ath.png", make_athletic), ("neon_socks.png", make_socks),
    ]
    for name, fn in jobs:
        path = os.path.join(OUT, name)
        fn().save(path)
        print("ok", name)
