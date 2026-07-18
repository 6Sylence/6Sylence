# -*- coding: utf-8 -*-
"""
Mockups de ajuste para la sincronización con Printful:
- Bucket Hat Suminagashi (la gorra dad-hat no existe como producto imprimible
  en Printful; el producto pasa a bucket reversible AOP, como el de Paisley).
- Manga larga en blanco (Bella+Canvas 3501 no se fabrica en crema).
"""
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from suminagashi_capsule import (BG, FONT_B, OUT, S, canvas, drop_shadow,
                                 draw_tee, seal_stamp, suminagashi)


def draw_bucket(pattern, path):
    base = canvas().convert("RGBA")
    mask = Image.new("L", (S, S), 0)
    dm = ImageDraw.Draw(mask)
    # copa
    dm.polygon([(560, 480), (1040, 480), (1120, 830), (480, 830)], fill=255)
    dm.pieslice([560, 400, 1040, 640], 180, 360, fill=255)
    # ala acampanada
    dm.polygon([(480, 820), (1120, 820), (1330, 1080), (270, 1080)], fill=255)
    dm.ellipse([270, 1010, 1330, 1150], fill=255)
    drop_shadow(base, mask, dy=24)
    hat = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    hat.paste(pattern.resize((S, S)), (0, 0), mask)
    d = ImageDraw.Draw(hat)
    sew = (0, 0, 0, 70)
    d.line([(480, 828), (1120, 828)], fill=sew, width=6)      # unión copa/ala
    d.arc([560, 400, 1040, 640], 180, 360, fill=sew, width=5)
    d.line([(640, 500), (600, 826)], fill=sew, width=4)
    d.line([(960, 500), (1000, 826)], fill=sew, width=4)
    d.arc([270, 990, 1330, 1130], 10, 170, fill=sew, width=6)  # borde del ala
    d.arc([320, 940, 1280, 1080], 10, 170, fill=(0, 0, 0, 45), width=4)
    st = seal_stamp(64)
    hat.alpha_composite(st, (770, 700))
    base.alpha_composite(hat)
    base.convert("RGB").save(path, quality=92)


if __name__ == "__main__":
    random.seed(20260718)
    pat_cap = suminagashi(1400, 1400, seed=83, n_centers=8, rings=(12, 20), ss=1)
    draw_bucket(pat_cap, f"{OUT}/sum-bucket.jpg")
    pat_ls = suminagashi(1000, 1250, seed=23, n_centers=5, ss=1)
    draw_tee(pat_ls, (250, 250, 248), f"{OUT}/sum-longsleeve-white.jpg",
             long_sleeve=True)
    print("ok")
