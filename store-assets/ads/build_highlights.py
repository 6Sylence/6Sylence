#!/usr/bin/env python3
"""
Heráldica Mineral — SRHOOD · portadas de historias destacadas.

Lienzo 1080×1920 (formato Story) porque es lo que Instagram acepta como portada,
pero solo se ve el CÍRCULO CENTRAL: el recorte visible es el círculo inscrito en
el cuadrado central, radio 540 px. Todo el dibujo vive dentro de r=440 para que
nada se corte, y el fondo va a sangre para que el borde del círculo sea limpio.

Los glifos se trazan, no se importan: misma línea de oro que el guilloché.
"""
import math
from PIL import Image, ImageDraw
import srhood_stories as S
from srhood_stories import *   # noqa

S.set_canvas(1080, 1920)
W, H = 1080, 1920
CX, CY = 540, 960
R_RING = 430
LW = 9.0                      # grosor de línea de los glifos, a escala de lienzo


def _mask():
    return Image.new("L", (W * SS, H * SS), 0)


def _fin(m):
    return m.resize((W, H), Image.LANCZOS)


def _d(m):
    return ImageDraw.Draw(m)


def _s(pts):
    return [(x * SS, y * SS) for x, y in pts]


def _centrar(m):
    """Recentra el glifo por su caja real: una espiral no tiene su centro donde se dibuja."""
    bb = m.getbbox()
    if not bb:
        return m
    recorte = m.crop(bb)
    base = Image.new("L", m.size, 0)
    base.paste(recorte, (int(CX - recorte.width / 2), int(CY - recorte.height / 2)))
    return base


# ── glifos ────────────────────────────────────────────────────────────────────
def g_corona():
    return crown_mask((W, H), CX, CY - 10, 300, 190, filled=True)


def g_estrella(r=170, rr=64, n=8):
    m = _mask(); d = _d(m); pts = []
    for i in range(n * 2):
        a = math.pi * i / n - math.pi / 2
        rad = r if i % 2 == 0 else rr
        pts.append((CX + rad * math.cos(a), CY + rad * math.sin(a)))
    d.polygon(_s(pts), fill=255)
    return _fin(m)


def g_greca(paso=44, vueltas=4):
    """Meandro cuadrado: la greca de la casa, trazada en espiral."""
    m = _mask(); d = _d(m)
    x, y = CX + paso * vueltas, CY + paso * vueltas
    pts = [(x, y)]
    largo = paso * vueltas * 2
    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    i = 0
    while largo > paso:
        dx, dy = dirs[i % 4]
        x += dx * largo; y += dy * largo
        pts.append((x, y))
        if i % 2 == 1:
            largo -= paso * 2
        i += 1
    d.line(_s(pts), fill=255, width=int(LW * SS), joint="curve")
    return _centrar(_fin(m))


def g_regla():
    m = _mask(); d = _d(m)
    w, h = 340, 130
    d.rectangle(_s([(CX - w / 2, CY - h / 2), (CX + w / 2, CY + h / 2)]),
                outline=255, width=int(LW * SS))
    for i in range(1, 7):
        x = CX - w / 2 + w * i / 7
        alto = h * (0.46 if i % 2 else 0.28)
        d.line(_s([(x, CY + h / 2), (x, CY + h / 2 - alto)]), fill=255, width=int(LW * 0.8 * SS))
    return _fin(m)


def g_caja():
    """Paquete: caja, costura de solapa y cinta corta. Sin la cruz completa,
    que a tamaño de círculo se lee como una ventana."""
    m = _mask(); d = _d(m)
    w, h = 300, 264
    y0, y1 = CY - h / 2, CY + h / 2
    seam = y0 + h * 0.32
    d.rectangle(_s([(CX - w / 2, y0), (CX + w / 2, y1)]), outline=255, width=int(LW * SS))
    d.line(_s([(CX - w / 2, seam), (CX + w / 2, seam)]), fill=255, width=int(LW * SS))
    d.line(_s([(CX, y0), (CX, seam)]), fill=255, width=int(LW * SS))
    return _fin(m)


def g_retorno():
    """Flecha circular: la punta se alinea con la tangente del arco, no se pega encima."""
    m = _mask(); d = _d(m)
    r, a0, a1 = 150, 300, 610          # el arco cierra casi el círculo
    d.arc(_s([(CX - r, CY - r), (CX + r, CY + r)]), a0, a1, fill=255, width=int(LW * SS))
    a = math.radians(a1)
    px, py = CX + r * math.cos(a), CY + r * math.sin(a)
    tx, ty = -math.sin(a), math.cos(a)          # tangente en sentido creciente
    nx, ny = math.cos(a), math.sin(a)           # normal
    L, Wd = 62, 34
    d.polygon(_s([(px + tx * L, py + ty * L),
                  (px - tx * 6 + nx * Wd, py - ty * 6 + ny * Wd),
                  (px - tx * 6 - nx * Wd, py - ty * 6 - ny * Wd)]), fill=255)
    return _fin(m)


def g_texto(txt, size, path=None, dy=0):
    m = _mask(); d = _d(m)
    f = F(path or ITALIANA, int(size * SS))
    d.text((CX * SS, (CY + dy) * SS), txt, font=f, fill=255, anchor="mm")
    return _fin(m)


def g_sobre():
    m = _mask(); d = _d(m)
    w, h = 330, 226
    x0, y0, x1, y1 = CX - w / 2, CY - h / 2, CX + w / 2, CY + h / 2
    d.rectangle(_s([(x0, y0), (x1, y1)]), outline=255, width=int(LW * SS))
    d.line(_s([(x0, y0), (CX, CY + h * 0.10), (x1, y0)]), fill=255,
           width=int(LW * SS), joint="curve")
    return _fin(m)


def g_etiqueta():
    m = _mask(); d = _d(m)
    w, h = 300, 300
    pts = [(CX - w / 2, CY - h * 0.18), (CX - w * 0.10, CY - h / 2),
           (CX + w / 2, CY - h / 2), (CX + w / 2, CY + h * 0.30),
           (CX - w * 0.10, CY + h * 0.30)]
    d.line(_s(pts + [pts[0]]), fill=255, width=int(LW * SS), joint="curve")
    hr = 26
    d.ellipse(_s([(CX + w * 0.16 - hr, CY - h * 0.30 - hr),
                  (CX + w * 0.16 + hr, CY - h * 0.30 + hr)]), outline=255, width=int(LW * SS))
    return _fin(m)


# ── plancha ───────────────────────────────────────────────────────────────────
def portada(glifo, acento, rose, seed, escala=1.0):
    img = field((15, 18, 18), (8, 9, 11),
                glow=(CX, CY, 620, acento, 0.42)).convert("RGBA")
    img.alpha_composite(tint(guilloche_mask((W, H), CX, CY, [
        dict(a=rose[0], b=rose[1], h=1.0, turns=46, steps=13000, R=396, lw=0.75,
             rot=rose[2])]), ORO, 0.42))
    img.alpha_composite(tint(ring_mask((W, H), CX, CY, [(R_RING, 1.2, 255)]), ORO, 0.52))
    img.alpha_composite(tint(ring_mask((W, H), CX, CY, [(R_RING - 10, 1.0, 255)]), ORO, 0.20))

    m = glifo()
    if escala != 1.0:                       # margen óptico para glifos anchos
        nw, nh = int(W * escala), int(H * escala)
        m = m.resize((nw, nh), Image.LANCZOS)
        base = Image.new("L", (W, H), 0)
        base.paste(m, (int((W - nw) / 2), int((H - nh) / 2)))
        m = base
    img.alpha_composite(tint(m, ORO_HI, 0.97))
    return grain(img, opacity=0.024, seed=seed)


PORTADAS = [
    ("01-capsulas",     g_corona,                              ESM_HI,        (5, 1.041, 0),  5,  1.0),
    ("02-novedades",    g_estrella,                            (120, 92, 40), (7, 1.017, 11), 12, 1.0),
    ("03-looks",        g_greca,                               (124, 56, 34), (4, 1.052, 23), 19, 1.0),
    ("04-tallas",       g_regla,                               ESM_HI,        (6, 1.031, 7),  26, 1.0),
    ("05-envios",       g_caja,                                (120, 92, 40), (9, 1.023, 17), 33, 1.0),
    ("06-devoluciones", g_retorno,                             (20, 74, 48),  (3, 1.063, 29), 40, 1.0),
    ("07-faq",          lambda: g_texto("?", 300, dy=6),       ESM_HI,        (8, 1.019, 5),  47, 1.0),
    ("08-la-casa",      lambda: g_texto("SR", 230, dy=4),      (108, 66, 34), (5, 1.037, 13), 54, 1.0),
    ("09-contacto",     g_sobre,                               ESM_HI,        (11, 1.013, 21), 61, 1.0),
    ("10-codigo",       g_etiqueta,                            (120, 92, 40), (6, 1.031, 33), 68, 1.0),
]


if __name__ == "__main__":
    for nombre, glifo, acento, rose, seed, esc in PORTADAS:
        ruta = f"{OUT}/srhood-destacada-{nombre}.png"
        portada(glifo, acento, rose, seed, esc).save(ruta)
        print("→", ruta)
