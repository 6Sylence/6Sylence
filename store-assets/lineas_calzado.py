# -*- coding: utf-8 -*-
"""
Líneas de calzado SRHOOD (subfamilias estilo Nike):
- Vía: asfalto + señalización vial (doble amarilla, trazos blancos).
- Moiré: interferencia óptica de dos rejillas radiales B/N.
- Estática: glitch/scanline sobre fondo oscuro con acentos RGB.
Archivos de impresión all-over para el Mockup Generator y la Sync API.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "print")
os.makedirs(OUT, exist_ok=True)


def _noise_img(w, h, base, sigma, seed):
    rng = np.random.default_rng(seed)
    arr = np.tile(np.array(base, dtype=np.int16), (h, w, 1))
    arr = arr + rng.normal(0, sigma, (h, w, 1)).astype(np.int16)
    return np.clip(arr, 0, 255)


def via(w, h, seed):
    """Asfalto con grano + doble línea amarilla diagonal + trazos blancos."""
    rng = np.random.default_rng(seed)
    arr = _noise_img(w, h, (40, 40, 43), 7, seed)
    # árido: motas claras y oscuras dispersas
    n_specks = w * h // 900
    xs = rng.integers(0, w, n_specks)
    ys = rng.integers(0, h, n_specks)
    vals = rng.integers(-26, 34, n_specks)
    for dx in (0, 1):
        for dy in (0, 1):
            arr[np.clip(ys + dy, 0, h - 1), np.clip(xs + dx, 0, w - 1)] += \
                vals[:, None] // (1 + dx + dy)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    diag = math.hypot(w, h)
    ang = math.radians(28)
    ca, sa = math.cos(ang), math.sin(ang)
    cx, cy = w * 0.52, h * 0.5

    def line_at(offset, width, color, dash=None):
        # línea sobre el eje diagonal desplazada `offset` en la normal
        nx, ny = -sa, ca
        x0 = cx + nx * offset - ca * diag
        y0 = cy + ny * offset - sa * diag
        step = 90 if dash else int(diag * 2)
        gap = dash or 0
        t = 0
        while t < diag * 2:
            x1 = x0 + ca * t
            y1 = y0 + sa * t
            seg = min(step, diag * 2 - t)
            d.line([(x1, y1), (x1 + ca * seg, y1 + sa * seg)], fill=color,
                   width=width)
            t += seg + gap

    amarillo = (208, 168, 32)
    blanco = (222, 222, 218)
    line_at(-w * 0.055, int(w * 0.028), amarillo)
    line_at(+w * 0.010, int(w * 0.028), amarillo)
    line_at(+w * 0.30, int(w * 0.020), blanco, dash=130)
    line_at(-w * 0.34, int(w * 0.020), blanco, dash=130)
    # desgaste: erosiona la pintura con ruido
    wear = np.asarray(img).astype(np.int16)
    mask = np.random.default_rng(seed + 1).random((h, w)) < 0.16
    grano = _noise_img(w, h, (44, 44, 47), 9, seed + 2)
    wear[mask] = grano[mask]
    img = Image.fromarray(np.clip(wear, 0, 255).astype(np.uint8))
    return img.filter(ImageFilter.GaussianBlur(0.6))


def moire(w, h, seed, period=46):
    """Interferencia de dos rejillas de anillos concéntricos."""
    rng = random.Random(seed)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    k = 2 * math.pi / period
    c1 = (w * rng.uniform(0.30, 0.42), h * rng.uniform(0.34, 0.5))
    c2 = (w * rng.uniform(0.58, 0.72), h * rng.uniform(0.5, 0.66))
    r1 = np.hypot(xs - c1[0], ys - c1[1])
    r2 = np.hypot(xs - c2[0], ys - c2[1])
    f = np.sin(k * r1) + np.sin(k * r2)
    ink = f > 0
    img = np.empty((h, w, 3), dtype=np.uint8)
    img[ink] = (26, 26, 29)
    img[~ink] = (244, 242, 236)
    out = Image.fromarray(img).filter(ImageFilter.GaussianBlur(1.2))
    noise = np.random.default_rng(seed).normal(0, 4, (h, w, 1)).repeat(3, 2)
    arr = np.clip(np.asarray(out).astype(np.int16) + noise.astype(np.int16), 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def estatica(w, h, seed):
    """Estática de pantalla: scanlines, bandas glitch y aberración RGB."""
    rng = np.random.default_rng(seed)
    base = _noise_img(w, h, (20, 20, 24), 6, seed).astype(np.int16)
    # scanlines horizontales
    scan = (np.arange(h) % 8 < 3)[:, None, None]
    base = base + scan * 10
    # parches de nieve (static)
    for _ in range(6):
        y0 = rng.integers(0, h - h // 8)
        x0 = rng.integers(0, w - w // 5)
        hh = rng.integers(h // 30, h // 9)
        ww = rng.integers(w // 8, w // 3)
        patch = rng.integers(0, 2, (hh, ww, 1)) * rng.integers(90, 200)
        base[y0:y0 + hh, x0:x0 + ww] = patch.repeat(3, 2)
    # bandas glitch desplazadas con separación RGB
    for _ in range(14):
        y0 = int(rng.integers(0, h - 40))
        hh = int(rng.integers(8, 60))
        shift = int(rng.integers(-w // 10, w // 10))
        band = np.roll(base[y0:y0 + hh], shift, axis=1)
        base[y0:y0 + hh] = band
        off = int(rng.integers(6, 22))
        base[y0:y0 + hh, :, 0] = np.roll(band[:, :, 0], off, axis=1)
        base[y0:y0 + hh, :, 2] = np.roll(band[:, :, 2], -off, axis=1)
    # líneas de sincronía en verde fósforo y magenta
    for _ in range(5):
        y0 = int(rng.integers(0, h - 4))
        col = (57, 255, 120) if rng.random() < 0.6 else (255, 64, 180)
        base[y0:y0 + 3] = np.array(col, dtype=np.int16)
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    return img.filter(ImageFilter.GaussianBlur(0.5))


if __name__ == "__main__":
    print("vía…")
    via(2400, 2400, seed=7).save(f"{OUT}/via_sq.png")
    via(2000, 3400, seed=11).save(f"{OUT}/via_ath.png")
    print("moiré…")
    moire(2400, 2400, seed=17).save(f"{OUT}/moire_sq.png")
    print("estática…")
    estatica(2400, 2400, seed=23).save(f"{OUT}/est_sq.png")
    estatica(2000, 3400, seed=29).save(f"{OUT}/est_ath.png")
    # slip-on moiré con centros propios para no clonar la lona
    moire(2400, 2400, seed=31, period=54).save(f"{OUT}/moire_sq2.png")
    print("ok:", sorted(os.listdir(OUT)))
