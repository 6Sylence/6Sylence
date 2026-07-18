#!/usr/bin/env python3
"""Cápsula "Vidriera Real" — Street Royalty Hood.

Genera los archivos de impresión de la cápsula de vidriera gótica:
rosetón de 12 pétalos, tríptico de lancetas y celosías de diamante
en tonos joya con emplomado. Salida en ./out-vidriera/.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 2  # supersampling
random.seed(20260718)

FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
GLOOCK = f"{FONT_DIR}/Gloock-Regular.ttf"

LEAD = (24, 22, 27, 255)
SOLDER = (74, 70, 80, 255)          # brillo del emplomado
GOLDLINE = (198, 162, 92, 255)

RUBY = (146, 24, 50)
SAPPHIRE = (26, 62, 138)
DEEPSAPH = (18, 40, 96)
EMERALD = (16, 96, 74)
AMBER = (218, 158, 58)
VIOLET = (92, 44, 118)
IVORY = (236, 226, 202)
GOLD = (232, 190, 96)
CHARCOAL = (30, 28, 34)

JEWELS = [RUBY, SAPPHIRE, EMERALD, VIOLET]


def jitter(c, lo=0.86, hi=1.14):
    f = random.uniform(lo, hi)
    return tuple(min(255, max(0, int(v * f))) for v in c[:3]) + ((c[3],) if len(c) > 3 else (255,))


def polar(cx, cy, r, a):
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def glass_texture(img, light=(0.5, 0.35), strength=0.55, mask_alpha=True):
    """Luz radial + grano + vetas diagonales sobre la imagen (respeta alfa)."""
    w, h = img.size
    lx, ly = int(w * light[0]), int(h * light[1])
    rad = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(rad)
    maxr = math.hypot(max(lx, w - lx), max(ly, h - ly))
    for i in range(24, 0, -1):
        r = maxr * i / 24
        dr.ellipse([lx - r, ly - r, lx + r, ly + r], fill=int(70 * strength * (1 - i / 24)))
    light_layer = Image.new("RGBA", (w, h), (255, 250, 235, 0))
    light_layer.putalpha(rad)

    noise = Image.effect_noise((w, h), 26).convert("L")
    grain = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    grain.putalpha(noise.point(lambda p: int(p * 0.10)))

    streaks = Image.new("L", (w * 2, h * 2), 0)
    ds = ImageDraw.Draw(streaks)
    for _ in range(int(60 * strength)):
        x = random.randint(-w, 2 * w)
        ww = random.randint(6 * SS, 40 * SS)
        ds.line([(x, 0), (x + h, 2 * h)], fill=random.randint(8, 22), width=ww)
    streaks = streaks.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(3 * SS))
    veil = Image.new("RGBA", (w, h), (255, 252, 240, 0))
    veil.putalpha(streaks)

    alpha = img.getchannel("A") if mask_alpha else None
    for layer in (light_layer, veil, grain):
        if alpha is not None:
            la = layer.getchannel("A")
            layer.putalpha(Image.composite(la, Image.new("L", (w, h), 0), alpha.point(lambda p: 255 if p > 10 else 0)))
        img.alpha_composite(layer)
    return img


def lead_poly(d, pts, width, gold=False):
    d.line(pts + [pts[0]], fill=LEAD, width=width, joint="curve")
    inner = max(SS, width // 4)
    d.line(pts + [pts[0]], fill=GOLDLINE if gold else SOLDER, width=inner, joint="curve")


def petal(cx, cy, a0, a1, r_in, r_out, bulge=0.55):
    """Pétalo gótico apuntado entre dos radios."""
    ac = (a0 + a1) / 2
    w = (a1 - a0) / 2
    pts = []
    pts.append(polar(cx, cy, r_in, a0 + w * 0.12))
    pts.append(polar(cx, cy, (r_in + r_out) / 2, a0 + w * (1 - bulge) * 0.5))
    pts.append(polar(cx, cy, r_out * 0.97, ac - w * 0.30))
    pts.append(polar(cx, cy, r_out, ac))                      # punta
    pts.append(polar(cx, cy, r_out * 0.97, ac + w * 0.30))
    pts.append(polar(cx, cy, (r_in + r_out) / 2, a1 - w * (1 - bulge) * 0.5))
    pts.append(polar(cx, cy, r_in, a1 - w * 0.12))
    pts.append(polar(cx, cy, r_in * 1.02, ac))
    return pts


def crown(d, cx, cy, w, color=LEAD):
    h = w * 0.72
    x0, y0 = cx - w / 2, cy + h * 0.28
    band = h * 0.22
    pts = [
        (x0, y0), (x0, y0 - h * 0.52),
        (cx - w * 0.25, y0 - h * 0.18), (cx, y0 - h * 0.62),
        (cx + w * 0.25, y0 - h * 0.18), (x0 + w, y0 - h * 0.52),
        (x0 + w, y0),
    ]
    d.polygon(pts, fill=color)
    d.rectangle([x0, y0, x0 + w, y0 + band], fill=color)
    r = w * 0.055
    for px, py in [(x0, y0 - h * 0.52), (cx, y0 - h * 0.62), (x0 + w, y0 - h * 0.52)]:
        d.ellipse([px - r, py - r, px + r, py + r], fill=color)


def rose_window(size, lead_w=None):
    """Rosetón de 12 pétalos, medallón ámbar con corona."""
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = S / 2
    R = S * 0.492
    lw = lead_w or max(4 * SS, int(S * 0.008))
    N = 12

    # banda exterior segmentada
    for i in range(48):
        a0 = 2 * math.pi * i / 48
        a1 = 2 * math.pi * (i + 1) / 48
        pts = [polar(cx, cy, R, a) for a in (a0, a1)] + [polar(cx, cy, R * 0.935, a) for a in (a1, a0)]
        col = jitter(GOLD, 0.9, 1.08) if i % 2 == 0 else jitter(DEEPSAPH)
        d.polygon(pts, fill=col)

    # anillo C: 12 lancetas
    for i in range(N):
        a0 = 2 * math.pi * i / N
        a1 = 2 * math.pi * (i + 1) / N
        col = jitter(JEWELS[i % 4])
        pts = petal(cx, cy, a0, a1, R * 0.655, R * 0.915, bulge=0.7)
        d.polygon(pts, fill=col)
        lead_poly(d, pts, lw)
        # gota dorada entre puntas
        ga = a1
        gx, gy = polar(cx, cy, R * 0.90, ga)
        gr = R * 0.028
        d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=jitter(GOLD))
        d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=LEAD, width=max(SS, lw // 2))

    # anillo B: 24 paneles alternos
    for i in range(24):
        a0 = 2 * math.pi * i / 24
        a1 = 2 * math.pi * (i + 1) / 24
        col = jitter(IVORY, 0.93, 1.05) if i % 2 == 0 else jitter(EMERALD if (i // 2) % 2 else SAPPHIRE)
        steps = 6
        outer = [polar(cx, cy, R * 0.63, a0 + (a1 - a0) * t / steps) for t in range(steps + 1)]
        inner = [polar(cx, cy, R * 0.475, a1 - (a1 - a0) * t / steps) for t in range(steps + 1)]
        d.polygon(outer + inner, fill=col)
        lead_poly(d, outer + inner, max(SS * 2, lw * 2 // 3))

    # anillo A: 12 pétalos grandes
    for i in range(N):
        a0 = 2 * math.pi * i / N + math.pi / N
        a1 = a0 + 2 * math.pi / N
        col = jitter(JEWELS[(i + 1) % 4])
        pts = petal(cx, cy, a0, a1, R * 0.20, R * 0.445, bulge=0.5)
        d.polygon(pts, fill=col)
        lead_poly(d, pts, lw)

    # círculos de plomo en los límites
    for rr, wf in [(R, 1.6), (R * 0.935, 1.0), (R * 0.655, 1.2), (R * 0.475, 1.0), (R * 0.20, 1.2)]:
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=LEAD, width=int(lw * wf))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=SOLDER, width=max(SS, lw // 3))

    # medallón central ámbar con corona
    rm = R * 0.185
    d.ellipse([cx - rm, cy - rm, cx + rm, cy + rm], fill=jitter(AMBER, 0.98, 1.06))
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        d.line([polar(cx, cy, rm * 0.55, a), polar(cx, cy, rm, a)], fill=LEAD, width=max(SS, lw // 2))
    d.ellipse([cx - rm, cy - rm, cx + rm, cy + rm], outline=LEAD, width=lw)
    d.ellipse([cx - rm * 0.55, cy - rm * 0.55, cx + rm * 0.55, cy + rm * 0.55],
              fill=jitter(GOLD, 1.0, 1.1), outline=LEAD, width=max(SS, lw // 2))
    crown(d, cx, cy + rm * 0.02, rm * 0.62)

    img = glass_texture(img, light=(0.42, 0.30))
    return img.resize((size, size), Image.LANCZOS)


def lancet(d, x0, y0, x1, y1, lw, palette, head_rose=True):
    """Ventana de lanceta con arco apuntado, dos luces y óculo."""
    w = x1 - x0
    apex = (x0 + w / 2, y0)
    spring = y0 + w * 0.62          # arranque del arco
    # contorno: arco apuntado por dos arcos de circunferencia aproximados
    steps = 26
    left_arc = []
    right_arc = []
    for t in range(steps + 1):
        tt = t / steps
        # curva bezier-ish del arco gótico
        lx = x0 + (w / 2) * tt
        ly = spring - (spring - y0) * (tt ** 1.7)
        left_arc.append((lx, ly))
        right_arc.append((x1 - (w / 2) * tt, ly))
    outline = [(x0, y1), (x0, spring)] + left_arc + right_arc[::-1] + [(x1, spring), (x1, y1)]

    # fondo de paneles en rombos
    d.polygon(outline, fill=jitter(DEEPSAPH))
    cell = w / 5
    yy = y0
    row = 0
    while yy < y1 + cell:
        xx = x0 - cell
        while xx < x1 + cell:
            pts = [(xx + cell / 2, yy), (xx + cell, yy + cell / 2), (xx + cell / 2, yy + cell), (xx, yy + cell / 2)]
            r = random.random()
            if r < 0.14: col = jitter(RUBY)
            elif r < 0.24: col = jitter(EMERALD)
            elif r < 0.32: col = jitter(AMBER)
            elif r < 0.38: col = jitter(IVORY, 0.92, 1.04)
            else: col = jitter(palette)
            d.polygon(pts, fill=col)
            d.line(pts + [pts[0]], fill=LEAD, width=max(SS, lw // 2))
            xx += cell
        yy += cell
        row += 1

    # recorte exterior: repintar fuera del contorno con transparencia usando máscara
    # (se hace fuera, con máscara de lanceta)
    # óculo en la cabeza, dentro del arco
    if head_rose:
        ocx, ocy, orr = x0 + w / 2, spring - w * 0.02, w * 0.155
        d.ellipse([ocx - orr, ocy - orr, ocx + orr, ocy + orr], fill=jitter(AMBER))
        for k in range(6):
            a = 2 * math.pi * k / 6
            tri = [polar(ocx, ocy, orr * 0.92, a - 0.35), polar(ocx, ocy, orr * 0.92, a + 0.35), (ocx, ocy)]
            if k % 2 == 0:
                d.polygon(tri, fill=jitter(RUBY))
            d.line(tri + [tri[0]], fill=LEAD, width=max(SS, lw // 2))
        d.ellipse([ocx - orr, ocy - orr, ocx + orr, ocy + orr], outline=LEAD, width=lw)
        crown(d, ocx, ocy, orr * 0.7, color=GOLDLINE)

    # mainel central y travesaños
    d.line([(x0 + w / 2, spring + w * 0.1), (x0 + w / 2, y1)], fill=LEAD, width=lw)
    d.line([(x0, spring), (x1, spring)], fill=LEAD, width=lw)
    d.line(outline + [outline[0]], fill=LEAD, width=int(lw * 1.5), joint="curve")
    d.line(outline + [outline[0]], fill=SOLDER, width=max(SS, lw // 3), joint="curve")
    return outline


def triptych(wpx, hpx):
    S = (wpx * SS, hpx * SS)
    img = Image.new("RGBA", S, (0, 0, 0, 0))
    lw = max(4 * SS, int(S[0] * 0.006))
    W, H = S
    # máscaras por lanceta para transparencia limpia
    windows = [
        (W * 0.055, H * 0.16, W * 0.315, H * 0.97, SAPPHIRE, False),
        (W * 0.355, H * 0.02, W * 0.645, H * 0.97, SAPPHIRE, True),
        (W * 0.685, H * 0.16, W * 0.945, H * 0.97, SAPPHIRE, False),
    ]
    for x0, y0, x1, y1, pal, rose in windows:
        layer = Image.new("RGBA", S, (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        outline = lancet(dl, x0, y0, x1, y1, lw, pal, head_rose=rose)
        mask = Image.new("L", S, 0)
        ImageDraw.Draw(mask).polygon(outline, fill=255)
        mask = mask.filter(ImageFilter.MaxFilter(3))
        layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", S, 0), mask))
        img.alpha_composite(layer)
    img = glass_texture(img, light=(0.5, 0.22))
    return img.resize((wpx, hpx), Image.LANCZOS)


def lattice(wpx, hpx, cell_px, medallions=6, bg=CHARCOAL, small=False):
    """Celosía de rombos joya con emplomado y filo dorado, a sangre."""
    S = (wpx * SS, hpx * SS)
    img = Image.new("RGBA", S, bg + (255,))
    d = ImageDraw.Draw(img)
    cell = cell_px * SS
    lw = max(3 * SS, int(cell * 0.055))
    W, H = S
    yy = -cell
    while yy < H + cell:
        xx = -cell
        while xx < W + cell:
            pts = [(xx + cell / 2, yy), (xx + cell, yy + cell / 2), (xx + cell / 2, yy + cell), (xx, yy + cell / 2)]
            r = random.random()
            if r < 0.10: col = jitter(RUBY)
            elif r < 0.19: col = jitter(EMERALD)
            elif r < 0.26: col = jitter(AMBER, 0.9, 1.05)
            elif r < 0.33: col = jitter(VIOLET)
            elif r < 0.48: col = jitter(SAPPHIRE)
            else: col = jitter(DEEPSAPH, 0.82, 1.12)
            d.polygon(pts, fill=col)
            d.line(pts + [pts[0]], fill=LEAD, width=lw, joint="curve")
            d.line(pts + [pts[0]], fill=GOLDLINE, width=max(SS, lw // 3), joint="curve")
            xx += cell
        yy += cell

    # medallones-rosetón dispersos, sin solaparse
    placed = []
    attempts = 0
    while len(placed) < medallions and attempts < 400:
        attempts += 1
        mx = random.uniform(cell * 1.2, W - cell * 1.2)
        my = random.uniform(cell * 1.2, H - cell * 1.2)
        mr = cell * (0.62 if small else 0.85)
        if any(math.hypot(mx - px, my - py) < (mr + pr) * 2.6 for px, py, pr in placed):
            continue
        placed.append((mx, my, mr))
    for mx, my, mr in placed:
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=jitter(AMBER))
        for k in range(8):
            a = 2 * math.pi * k / 8
            tri = [polar(mx, my, mr * 0.9, a - 0.3), polar(mx, my, mr * 0.9, a + 0.3), (mx, my)]
            if k % 2 == 0:
                d.polygon(tri, fill=jitter(RUBY if k % 4 == 0 else EMERALD))
            d.line(tri + [tri[0]], fill=LEAD, width=max(SS, lw // 2))
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=LEAD, width=lw)
        d.ellipse([mx - mr * 0.35, my - mr * 0.35, mx + mr * 0.35, my + mr * 0.35],
                  fill=jitter(GOLD), outline=LEAD, width=max(SS, lw // 2))

    img = glass_texture(img, light=(0.5, 0.18), strength=0.7, mask_alpha=False)
    return img.resize((wpx, hpx), Image.LANCZOS)


def wordmark(draw, cx, y, text, px, fill=GOLD, tracking=0.32):
    font = ImageFont.truetype(GLOOCK, px)
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * px * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking * px


def compose_garment(art, wpx, hpx, art_w, art_y, brand=True, sub="VIDRIERA REAL · MMXXVI"):
    img = Image.new("RGBA", (wpx * SS, hpx * SS), (0, 0, 0, 0))
    a = art.resize((art_w * SS, int(art.height * art_w / art.width) * SS), Image.LANCZOS)
    img.alpha_composite(a, ((wpx - art_w) // 2 * SS, art_y * SS))
    if brand:
        d = ImageDraw.Draw(img)
        by = art_y * SS + a.height + int(hpx * SS * 0.035)
        wordmark(d, wpx * SS / 2, by, "STREET ROYALTY", int(wpx * SS * 0.040))
        wordmark(d, wpx * SS / 2, by + int(wpx * SS * 0.062), sub, int(wpx * SS * 0.020),
                 fill=(200, 190, 170, 235), tracking=0.5)
    return img.resize((wpx, hpx), Image.LANCZOS)


if __name__ == "__main__":
    import os
    out = os.environ.get("OUT_DIR", "./out-vidriera")
    os.makedirs(out, exist_ok=True)

    rose = rose_window(2000)
    tri = triptych(1900, 2100)

    # 1) Camiseta — rosetón + wordmark (2400x3000)
    compose_garment(rose, 2400, 3000, 2050, 260).save(f"{out}/vid_tee_print.png")
    print("tee ok")

    # 2) Sudadera granate — tríptico (2400x3000)
    compose_garment(tri, 2400, 3000, 2080, 140, sub="LUX REGIA · MMXXVI").save(f"{out}/vid_sweat_print.png")
    print("sweat ok")

    # 3) Hoodie premium — rosetón grande, marca compacta (2250x2250)
    compose_garment(rose, 2250, 2250, 1850, 60, sub="VIDRIERA REAL").save(f"{out}/vid_hoodie_print.png")
    print("hoodie ok")

    # 4) Zapatillas altas hombre — celosía media (2400x2400)
    lattice(2400, 2400, 300, medallions=7).save(f"{out}/vid_sq.png")
    print("hightop ok")

    # 5) Zapatillas deportivas mujer — celosía vertical (2000x3400)
    lattice(2000, 3400, 260, medallions=8).save(f"{out}/vid_ath.png")
    print("athletic ok")

    # 6) Calcetines — celosía fina (2000x2000)
    lattice(2000, 2000, 170, medallions=5, small=True).save(f"{out}/vid_socks.png")
    print("socks ok")
