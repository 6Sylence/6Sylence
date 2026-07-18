# -*- coding: utf-8 -*-
"""
Archivos de impresión (print files) para sincronizar con Printful:
- Cápsula Suminagashi: mismos seeds que los mockups, a resolución de impresión.
- Cápsula Cianotipo: paneles botánicos para las 6 piezas (los 4 del run anterior
  no conservan su arte original; se regeneran en el mismo estilo de la serie).
Salida en store-assets/print/.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from suminagashi_capsule import (CHALK, PRUSSIA, cyanotype_panel, eucalyptus,
                                 fern, seal_stamp, suminagashi)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "print")
os.makedirs(OUT, exist_ok=True)


def with_seal(img, rel=0.15, margin=0.03):
    img = img.convert("RGBA")
    w, h = img.size
    s = int(w * rel)
    st = seal_stamp(s)
    img.alpha_composite(st, (w - s - int(w * margin), h - s - int(w * margin)))
    return img.convert("RGB")


def leaf_panel(w, h, seed):
    """Hojas de gran formato con nervadura (motivo 'Hoja' del hoodie cianotipo)."""
    rng = random.Random(seed)
    img = Image.new("RGB", (w, h), PRUSSIA)
    d = ImageDraw.Draw(img)
    for _ in range(3):
        cx = rng.uniform(0.25, 0.75) * w
        cy = rng.uniform(0.3, 0.75) * h
        L = rng.uniform(0.3, 0.42) * h
        ang = rng.uniform(-0.7, 0.7)
        ca, sa = math.cos(ang), math.sin(ang)
        n = 60
        pts_r, pts_l = [], []
        for i in range(n + 1):
            t = i / n
            wd = math.sin(math.pi * t) ** 0.8 * L * 0.34
            x0 = (t - 0.5) * L
            pts_r.append((cx + x0 * ca - wd * sa, cy + x0 * sa + wd * ca))
            pts_l.append((cx + x0 * ca + wd * sa, cy + x0 * sa - wd * ca))
        d.polygon(pts_r + pts_l[::-1], fill=CHALK)
        # nervadura central y laterales en azul (negativo)
        d.line([pts_r[0], pts_r[-1]], fill=PRUSSIA, width=max(3, w // 260))
        for i in range(6, n - 4, 6):
            t = i / n
            x0 = (t - 0.5) * L
            bx, by = cx + x0 * ca, cy + x0 * sa
            wd = math.sin(math.pi * t) ** 0.8 * L * 0.30
            for sgn in (1, -1):
                d.line([(bx, by),
                        (bx - sgn * wd * sa + L * 0.06 * ca,
                         by + sgn * wd * ca + L * 0.06 * sa)],
                       fill=PRUSSIA, width=max(2, w // 400))
    img = img.filter(ImageFilter.GaussianBlur(w / 1500))
    noise = np.random.default_rng(seed).normal(0, 6, (h, w, 1)).repeat(3, 2)
    arr = np.clip(np.asarray(img).astype(np.int16) + noise.astype(np.int16), 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def micro_herbario(w, h, seed):
    """Mini-helechos dispersos para calcetines de sublimación (full bleed)."""
    rng = random.Random(seed)
    img = Image.new("RGB", (w, h), PRUSSIA)
    d = ImageDraw.Draw(img)
    for _ in range(26):
        x = rng.uniform(0, w)
        y = rng.uniform(0.1, 1.05) * h
        fern(d, x, y, rng.uniform(0.10, 0.22) * h,
             rng.uniform(0.2, math.pi - 0.2), CHALK, width=max(2, w // 500),
             depth=1)
    img = img.filter(ImageFilter.GaussianBlur(w / 1800))
    noise = np.random.default_rng(seed).normal(0, 6, (h, w, 1)).repeat(3, 2)
    arr = np.clip(np.asarray(img).astype(np.int16) + noise.astype(np.int16), 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


if __name__ == "__main__":
    jobs = []

    # --- suminagashi (mismos seeds que los mockups publicados) ---
    print("suminagashi tee…")
    with_seal(suminagashi(2400, 3000, seed=11, ss=1)).save(
        f"{OUT}/sum_tee_print.png")
    print("suminagashi manga larga…")
    with_seal(suminagashi(2400, 3000, seed=23, n_centers=5, ss=1)).save(
        f"{OUT}/sum_ls_print.png")
    print("suminagashi hoodie…")
    with_seal(suminagashi(2400, 2250, seed=37, n_centers=6, ss=1)).save(
        f"{OUT}/sum_hoodie_print.png")
    print("suminagashi hitop…")
    suminagashi(2600, 2600, seed=52, n_centers=8, rings=(14, 22), ss=1).save(
        f"{OUT}/sum_hitop_print.png")
    print("suminagashi slipon…")
    suminagashi(2600, 2600, seed=67, n_centers=7, rings=(16, 24), ss=1).save(
        f"{OUT}/sum_slipon_print.png")
    print("suminagashi bucket…")
    suminagashi(2600, 2600, seed=83, n_centers=8, rings=(12, 20), ss=1).save(
        f"{OUT}/sum_bucket_out.png")
    Image.new("RGB", (1200, 1200), (24, 24, 27)).save(f"{OUT}/sum_bucket_in.png")

    # --- cianotipo ---
    print("cianotipo calzado…")
    cyanotype_panel(2600, 2600, seed=91, motif="fern").save(
        f"{OUT}/cia_hitop_print.png")
    cyanotype_panel(2600, 2600, seed=97, motif="eucalyptus").save(
        f"{OUT}/cia_slipon_print.png")
    print("cianotipo prendas…")
    with_seal(cyanotype_panel(2400, 3000, seed=113, motif="fern")).save(
        f"{OUT}/cia_tee_print.png")
    with_seal(cyanotype_panel(2400, 3000, seed=127, motif="eucalyptus")).save(
        f"{OUT}/cia_sweat_print.png")
    with_seal(leaf_panel(2400, 2250, seed=131)).save(f"{OUT}/cia_hoodie_print.png")
    micro_herbario(2000, 2000, seed=137).save(f"{OUT}/cia_socks_print.png")

    print("ok:", sorted(os.listdir(OUT)))
