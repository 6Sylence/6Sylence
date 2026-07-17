# -*- coding: utf-8 -*-
# SRHOOD — Cápsula Atelier: generador de mockups 1600x1600
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = 1600
S = 2  # supersample
OUT = os.path.dirname(os.path.abspath(__file__)) + "/atelier"
os.makedirs(OUT, exist_ok=True)

# Paleta
NEGRO   = (20, 21, 26)
NAVY    = (30, 42, 68)
CREMA   = (242, 234, 216)
BURDEOS = (107, 34, 49)
ORO     = (201, 162, 75)
OLIVA   = (90, 95, 69)
PIEDRA  = (185, 178, 166)
CHOCO   = (74, 52, 42)
ANTRACITA = (58, 60, 66)
DENIM   = (96, 116, 146)
DENIM_CLARO = (128, 148, 176)
BEIGE   = (216, 204, 180)
GUM     = (188, 138, 92)
BLANCO  = (244, 242, 236)
CRUDO   = (233, 226, 208)

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def base_canvas():
    top = np.array([238, 236, 231], dtype=float)
    bot = np.array([222, 219, 212], dtype=float)
    g = np.linspace(0, 1, W)[:, None]
    arr = (top[None, None, :] * (1 - g[:, :, None]) + bot[None, None, :] * g[:, :, None])
    arr = np.repeat(arr, W // arr.shape[1] if arr.shape[1] != W else 1, axis=1)
    arr = np.tile(arr, (1, W, 1)) if arr.shape[1] == 1 else arr
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    return img

def darker(c, f=0.82):
    return tuple(int(v * f) for v in c[:3])

def lighter(c, f=1.12):
    return tuple(min(255, int(v * f)) for v in c[:3])

def P(pts):
    return [(x * S, y * S) for x, y in pts]

def stitch_line(d, p1, p2, color, dash=13, gap=9, width=3):
    x1, y1 = p1; x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0: return
    n = int(dist // (dash + gap)) + 1
    ux, uy = (x2 - x1) / dist, (y2 - y1) / dist
    t = 0
    for _ in range(n):
        a = (x1 + ux * t, y1 + uy * t)
        b = (x1 + ux * min(t + dash, dist), y1 + uy * min(t + dash, dist))
        d.line(P([a, b]), fill=color, width=width * S)
        t += dash + gap
        if t >= dist: break

def stitch_path(d, pts, color, **kw):
    for i in range(len(pts) - 1):
        stitch_line(d, pts[i], pts[i + 1], color, **kw)

def crown_mark(d, cx, cy, w, color, lw=None):
    # corona zigzag SRH con base punteada
    h = w * 0.52
    lw = lw or max(3, int(w * 0.085))
    pts = [(cx - w / 2, cy + h / 2), (cx - w / 2, cy - h * 0.1),
           (cx - w * 0.25, cy + h * 0.05), (cx, cy - h / 2),
           (cx + w * 0.25, cy + h * 0.05), (cx + w / 2, cy - h * 0.1),
           (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
    d.line(P(pts), fill=color, width=lw * S, joint="curve")
    n = 6
    for i in range(n):
        x = cx - w / 2 + (i + 0.5) * w / n
        y = cy + h / 2 + h * 0.22
        r = max(2, w * 0.035)
        d.ellipse(P([(x - r, y - r), (x + r, y + r)]), fill=color)

def new_layer():
    return Image.new("RGBA", (W * S, W * S), (0, 0, 0, 0))

def compose(draw_fn, title, subtitle, num, total, fname, pattern_hooks=None):
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    draw_fn(d, layer)
    layer = layer.resize((W, W), Image.LANCZOS)
    canvas = base_canvas()
    alpha = layer.split()[3]

    # sombra suave
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    shm = Image.new("L", (W, W), 0)
    shm.paste(alpha, (0, 26))
    shm = shm.filter(ImageFilter.GaussianBlur(30))
    sh.putalpha(shm.point(lambda v: int(v * 0.30)))
    black = Image.new("RGBA", (W, W), (24, 24, 30, 255))
    canvas = Image.alpha_composite(canvas, Image.composite(black, Image.new("RGBA", (W, W), (0, 0, 0, 0)), sh.split()[3]))

    canvas = Image.alpha_composite(canvas, layer)

    # sombreado vertical (volumen) recortado a la prenda
    grad = np.linspace(0, 1, W)[:, None]
    top_light = (np.clip(0.16 - grad * 0.32, 0, 1) * 255 * 0.45).astype(np.uint8)
    bot_dark = (np.clip(grad * 0.30 - 0.14, 0, 1) * 255 * 0.55).astype(np.uint8)
    am = np.array(alpha) / 255.0
    light_a = Image.fromarray((np.tile(top_light, (1, W)) * am).astype(np.uint8))
    dark_a = Image.fromarray((np.tile(bot_dark, (1, W)) * am).astype(np.uint8))
    wl = Image.new("RGBA", (W, W), (255, 255, 255, 255)); wl.putalpha(light_a)
    dl = Image.new("RGBA", (W, W), (10, 10, 14, 255)); dl.putalpha(dark_a)
    canvas = Image.alpha_composite(canvas, wl)
    canvas = Image.alpha_composite(canvas, dl)

    # textura de tejido (ruido fino)
    rng = np.random.default_rng(42 + num)
    noise = rng.normal(0, 1, (W, W))
    na = ((noise > 0.6).astype(float) * 26 * am).astype(np.uint8)
    nb = ((noise < -0.6).astype(float) * 22 * am).astype(np.uint8)
    nw = Image.new("RGBA", (W, W), (255, 255, 255, 255)); nw.putalpha(Image.fromarray(na))
    nd = Image.new("RGBA", (W, W), (0, 0, 0, 255)); nd.putalpha(Image.fromarray(nb))
    canvas = Image.alpha_composite(canvas, nw)
    canvas = Image.alpha_composite(canvas, nd)

    # pie de marca + sello de cápsula
    d2 = ImageDraw.Draw(canvas)
    fb = ImageFont.truetype(F_BOLD, 34)
    fr = ImageFont.truetype(F_REG, 30)
    fs = ImageFont.truetype(F_BOLD, 22)
    d2.text((72, 1468), "STREET ROYALTY HOOD", font=fb, fill=(70, 70, 74))
    d2.text((72, 1512), subtitle, font=fr, fill=(140, 138, 134))
    stamp = f"CÁPSULA ATELIER · Nº {num:02d}/{total:02d}"
    d2.text((72, 64), stamp, font=fs, fill=(158, 128, 66))
    d2.line([(72, 100), (72 + d2.textlength(stamp, font=fs), 100)], fill=(158, 128, 66, 120), width=1)

    out = canvas.convert("RGB")
    out.save(f"{OUT}/{fname}", "JPEG", quality=90, progressive=True)
    print("ok", fname)

# ---------- utilidades de prenda ----------

def part_mask(draw_fn):
    m = new_layer()
    dm = ImageDraw.Draw(m)
    draw_fn(dm)
    return m

def paste_pattern(layer, mask_layer, pattern_fn):
    pat = new_layer()
    dp = ImageDraw.Draw(pat)
    pattern_fn(dp)
    layer.paste(pat, (0, 0), Image.composite(pat.split()[3], Image.new("L", pat.size, 0), mask_layer.split()[3]))

# ============================================================
# 01 — Camisa Oxford "Firma" — Blanco
def camisa_oxford(d, layer):
    c = BLANCO; cd = darker(c, 0.90); line = (196, 192, 182)
    # mangas
    d.polygon(P([(505, 430), (330, 520), (255, 1000), (400, 1035), (505, 700)]), fill=cd)
    d.polygon(P([(1095, 430), (1270, 520), (1345, 1000), (1200, 1035), (1095, 700)]), fill=cd)
    # puños
    d.polygon(P([(255, 1000), (400, 1035), (388, 1105), (243, 1070)]), fill=c)
    d.polygon(P([(1345, 1000), (1200, 1035), (1212, 1105), (1357, 1070)]), fill=c)
    # cuerpo
    d.polygon(P([(505, 430), (660, 355), (800, 385), (940, 355), (1095, 430),
                 (1075, 1250), (525, 1250)]), fill=c)
    # placket
    d.rectangle(P([(778, 392), (822, 1250)]), fill=lighter(c, 1.03), outline=line, width=2 * S)
    for y in range(470, 1230, 108):
        d.ellipse(P([(794, y), (808, y + 14)]), fill=(210, 205, 194), outline=(170, 165, 154), width=1 * S)
    # cuello
    d.chord(P([(660, 338), (940, 442)]), 180, 360, fill=darker(c, 0.94), outline=line, width=2 * S)
    d.polygon(P([(660, 388), (800, 392), (700, 470), (640, 425)]), fill=c, outline=line, width=2 * S)
    d.polygon(P([(940, 388), (800, 392), (900, 470), (960, 425)]), fill=c, outline=line, width=2 * S)
    # bolsillo pecho izquierdo
    d.rectangle(P([(585, 560), (715, 700)]), outline=line, width=2 * S)
    stitch_path(d, [(585, 560), (585, 700), (715, 700), (715, 560)], (176, 172, 162))
    # costuras hombro/sisa
    stitch_line(d, (505, 440), (505, 700), (176, 172, 162))
    stitch_line(d, (1095, 440), (1095, 700), (176, 172, 162))
    # firma bordada en oro (pecho derecho) — trazo cursivo
    sig = [(870, 640), (900, 600), (925, 645), (945, 590), (965, 645), (990, 605),
           (1010, 640), (1035, 615)]
    d.line(P(sig), fill=ORO, width=6 * S, joint="curve")
    d.line(P([(862, 655), (1042, 655)]), fill=ORO, width=3 * S)
    d.ellipse(P([(1046, 608), (1058, 620)]), fill=ORO)

# ============================================================
# 02 — Sobrecamisa Franela "Tartán Real" — Burdeos
def sobrecamisa_tartan(d, layer):
    def silo(dm):
        dm.polygon(P([(470, 430), (300, 520), (235, 1010), (385, 1045), (470, 720)]), fill=(255, 0, 0, 255))
        dm.polygon(P([(1130, 430), (1300, 520), (1365, 1010), (1215, 1045), (1130, 720)]), fill=(255, 0, 0, 255))
        dm.polygon(P([(470, 430), (640, 350), (800, 382), (960, 350), (1130, 430), (1110, 1270), (490, 1270)]), fill=(255, 0, 0, 255))
    m = part_mask(silo)
    # base burdeos
    layer.paste(Image.new("RGBA", layer.size, BURDEOS + (255,)), (0, 0), m.split()[3])
    # tartán
    def tartan(dp):
        for x in range(180, 1460, 150):
            dp.rectangle(P([(x, 300), (x + 56, 1300)]), fill=NAVY + (120,))
            dp.line(P([(x + 100, 300), (x + 100, 1300)]), fill=ORO + (180,), width=3 * S)
        for y in range(330, 1300, 150):
            dp.rectangle(P([(180, y), (1420, y + 56)]), fill=NAVY + (110,))
            dp.line(P([(180, y + 100), (1420, y + 100)]), fill=ORO + (170,), width=3 * S)
    paste_pattern(layer, m, tartan)
    d = ImageDraw.Draw(layer)
    # cuello y placket
    d.polygon(P([(640, 350), (800, 388), (706, 468), (622, 415)]), fill=darker(BURDEOS, 0.75))
    d.polygon(P([(960, 350), (800, 388), (894, 468), (978, 415)]), fill=darker(BURDEOS, 0.75))
    d.rectangle(P([(776, 388), (824, 1270)]), fill=darker(BURDEOS, 0.8))
    for y in range(480, 1240, 120):
        d.ellipse(P([(792, y), (808, y + 16)]), fill=ORO)
    # bolsillos con solapa
    for bx in (560, 890):
        d.rectangle(P([(bx, 585), (bx + 150, 730)]), outline=CREMA + (170,), width=2 * S)
        d.polygon(P([(bx - 6, 585), (bx + 156, 585), (bx + 150, 640), (bx, 640)]), fill=darker(BURDEOS, 0.78))
        d.ellipse(P([(bx + 68, 616), (bx + 82, 630)]), fill=ORO)
    # puños
    d.polygon(P([(235, 1010), (385, 1045), (373, 1115), (223, 1080)]), fill=darker(BURDEOS, 0.78))
    d.polygon(P([(1365, 1010), (1215, 1045), (1227, 1115), (1377, 1080)]), fill=darker(BURDEOS, 0.78))
    stitch_line(d, (470, 440), (470, 720), CREMA)
    stitch_line(d, (1130, 440), (1130, 720), CREMA)

# ============================================================
# 03 — Jersey de Punto "Cetro" — Crema
def jersey_cetro(d, layer):
    c = CREMA; cd = darker(c, 0.92)
    # mangas
    d.polygon(P([(495, 460), (315, 560), (262, 1030), (405, 1062), (495, 740)]), fill=cd)
    d.polygon(P([(1105, 460), (1285, 560), (1338, 1030), (1195, 1062), (1105, 740)]), fill=cd)
    # cuerpo
    d.polygon(P([(495, 460), (665, 380), (935, 380), (1105, 460), (1085, 1210), (515, 1210)]), fill=c)
    # columnas de ochos (cable knit)
    for cx in (620, 730, 870, 980):
        y = 500
        while y < 1130:
            d.arc(P([(cx - 26, y), (cx + 26, y + 64)]), 300, 120, fill=darker(c, 0.82), width=7 * S)
            d.arc(P([(cx - 26, y + 32), (cx + 26, y + 96)]), 120, 300, fill=darker(c, 0.86), width=7 * S)
            y += 64
    # canalé: cuello, puños, bajo
    d.rectangle(P([(515, 1210), (1085, 1268)]), fill=cd)
    for x in range(520, 1085, 18):
        d.line(P([(x, 1212), (x, 1266)]), fill=darker(c, 0.8), width=2 * S)
    d.polygon(P([(665, 380), (800, 348), (935, 380), (915, 430), (800, 402), (685, 430)]), fill=cd)
    for i in range(0, 24):
        x1, y1 = 672 + i * 11, 385 - i * 0  # ribs cuello
    d.polygon(P([(262, 1030), (405, 1062), (394, 1128), (251, 1096)]), fill=cd)
    d.polygon(P([(1338, 1030), (1195, 1062), (1206, 1128), (1349, 1096)]), fill=cd)
    # cetro bordado (pecho izquierdo)
    d.line(P([(648, 648), (688, 788)]), fill=ORO, width=7 * S)
    d.ellipse(P([(633, 620), (665, 652)]), outline=ORO, width=5 * S)
    d.line(P([(681, 764), (705, 756)]), fill=ORO, width=5 * S)
    crown_mark(d, 649, 600, 44, ORO, lw=5)

# ============================================================
# 04 — Cárdigan "Ajedrez Real" — Negro
def cardigan_ajedrez(d, layer):
    c = NEGRO
    d.polygon(P([(500, 470), (330, 560), (270, 1040), (415, 1072), (500, 745)]), fill=lighter(c, 1.28))
    d.polygon(P([(1100, 470), (1270, 560), (1330, 1040), (1185, 1072), (1100, 745)]), fill=lighter(c, 1.28))
    # paneles frontales con V
    d.polygon(P([(500, 470), (680, 392), (795, 640), (795, 1235), (515, 1235)]), fill=c)
    d.polygon(P([(1100, 470), (920, 392), (805, 640), (805, 1235), (1085, 1235)]), fill=c)
    # tira de botones
    d.rectangle(P([(778, 640), (822, 1235)]), fill=lighter(c, 1.9))
    for y in range(700, 1200, 105):
        d.ellipse(P([(791, y), (809, y + 18)]), fill=ORO)
    # banda damero en bajo y puños
    def damero(x0, y0, x1, y1, n=2, s=36):
        cols = int((x1 - x0) / s) + 1
        for r in range(n):
            for cc in range(cols):
                if (r + cc) % 2 == 0:
                    d.rectangle(P([(x0 + cc * s, y0 + r * s), (min(x0 + (cc + 1) * s, x1), y0 + (r + 1) * s)]), fill=CREMA)
                else:
                    d.rectangle(P([(x0 + cc * s, y0 + r * s), (min(x0 + (cc + 1) * s, x1), y0 + (r + 1) * s)]), fill=darker(BURDEOS, 0.9))
    damero(515, 1163, 1085, 1235)
    damero(270, 1000, 415, 1072)
    damero(1185, 1000, 1330, 1072)
    # solapa/cuello chal
    d.polygon(P([(680, 392), (800, 640), (760, 700), (640, 470)]), fill=lighter(c, 2.2))
    d.polygon(P([(920, 392), (800, 640), (840, 700), (960, 470)]), fill=lighter(c, 2.2))
    # rey de ajedrez bordado (pecho derecho)
    kx, ky = 985, 585
    d.line(P([(kx, ky - 58), (kx, ky - 28)]), fill=ORO, width=5 * S)
    d.line(P([(kx - 14, ky - 44), (kx + 14, ky - 44)]), fill=ORO, width=5 * S)
    d.polygon(P([(kx - 20, ky - 26), (kx + 20, ky - 26), (kx + 12, ky + 8), (kx - 12, ky + 8)]), outline=ORO, width=4 * S)
    d.line(P([(kx - 16, ky + 16), (kx + 16, ky + 16)]), fill=ORO, width=4 * S)
    d.polygon(P([(kx - 22, ky + 24), (kx + 22, ky + 24), (kx + 28, ky + 40), (kx - 28, ky + 40)]), outline=ORO, width=4 * S)

# ============================================================
# 05 — Chaqueta Denim "Estandarte" — Azul Lavado (vista trasera)
def denim_estandarte(d, layer):
    c = DENIM
    # mangas
    d.polygon(P([(480, 450), (310, 540), (250, 1020), (398, 1052), (480, 730)]), fill=darker(c, 0.88))
    d.polygon(P([(1120, 450), (1290, 540), (1350, 1020), (1202, 1052), (1120, 730)]), fill=darker(c, 0.88))
    # cuerpo espalda
    d.polygon(P([(480, 450), (655, 372), (945, 372), (1120, 450), (1100, 1160), (500, 1160)]), fill=c)
    # lavado central (más claro)
    ml = part_mask(lambda dm: dm.polygon(P([(620, 430), (980, 430), (1020, 1150), (580, 1150)]), fill=(255, 0, 0, 90)))
    layer.paste(Image.new("RGBA", layer.size, DENIM_CLARO + (70,)), (0, 0), ml.split()[3])
    d = ImageDraw.Draw(layer)
    # cuello
    d.polygon(P([(655, 372), (800, 340), (945, 372), (915, 420), (800, 396), (685, 420)]), fill=darker(c, 0.8))
    # canesú y costuras
    d.line(P([(500, 520), (1100, 520)]), fill=darker(c, 0.7), width=4 * S)
    stitch_line(d, (500, 534), (1100, 534), (222, 176, 118))
    for x in (610, 990):
        d.line(P([(x, 534), (x, 1160)]), fill=darker(c, 0.7), width=4 * S)
        stitch_line(d, (x + 12, 540), (x + 12, 1155), (222, 176, 118))
    # cinturilla y puños
    d.rectangle(P([(500, 1160), (1100, 1225)]), fill=darker(c, 0.82))
    stitch_line(d, (505, 1192), (1095, 1192), (222, 176, 118))
    d.polygon(P([(250, 1020), (398, 1052), (388, 1118), (240, 1086)]), fill=darker(c, 0.78))
    d.polygon(P([(1350, 1020), (1202, 1052), (1212, 1118), (1360, 1086)]), fill=darker(c, 0.78))
    # parche estandarte (banner de cola de golondrina)
    bx, by, bw, bh = 800, 560, 300, 420
    pts = [(bx - bw/2, by), (bx + bw/2, by), (bx + bw/2, by + bh),
           (bx, by + bh - 70), (bx - bw/2, by + bh)]
    d.polygon(P(pts), fill=BURDEOS, outline=ORO, width=6 * S)
    stitch_path(d, pts + [pts[0]], CREMA, dash=10, gap=8)
    # barra superior y cordones
    d.line(P([(bx - bw/2 - 30, by - 10), (bx + bw/2 + 30, by - 10)]), fill=ORO, width=8 * S)
    d.ellipse(P([(bx - bw/2 - 42, by - 22), (bx - bw/2 - 18, by + 2)]), fill=ORO)
    d.ellipse(P([(bx + bw/2 + 18, by - 22), (bx + bw/2 + 42, by + 2)]), fill=ORO)
    crown_mark(d, bx, by + 130, 130, ORO, lw=9)
    fb = ImageFont.truetype(F_BOLD, 64 * S)
    d.text((bx * S, (by + 250) * S), "SRH", font=fb, fill=CREMA, anchor="mm")
    d.line(P([(bx - 70, by + 305), (bx + 70, by + 305)]), fill=ORO, width=4 * S)

# ============================================================
# 06 — Camiseta "León Heráldico" — Piedra
def tee_leon(d, layer):
    c = PIEDRA
    d.polygon(P([(520, 445), (355, 535), (300, 800), (445, 845), (520, 660)]), fill=darker(c, 0.9))
    d.polygon(P([(1080, 445), (1245, 535), (1300, 800), (1155, 845), (1080, 660)]), fill=darker(c, 0.9))
    d.polygon(P([(520, 445), (672, 372), (800, 400), (928, 372), (1080, 445), (1062, 1235), (538, 1235)]), fill=c)
    d.chord(P([(672, 340), (928, 452)]), 0, 180, fill=darker(c, 0.85))
    # print: cara de león heráldico (simétrica) en burdeos con corona oro
    cx, cy = 800, 760
    m = BURDEOS
    # melena — puntas zigzag radiales
    R1, R2 = 210, 150
    pts = []
    for i in range(24):
        a = math.pi * 2 * i / 24 - math.pi / 2
        r = R1 if i % 2 == 0 else R2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(P(pts), fill=m)
    # cara
    d.ellipse(P([(cx - 130, cy - 130), (cx + 130, cy + 130)]), fill=c)
    d.ellipse(P([(cx - 118, cy - 118), (cx + 118, cy + 118)]), fill=m)
    # orejas
    for sx in (-1, 1):
        d.ellipse(P([(cx + sx * 118 - 26, cy - 148), (cx + sx * 118 + 26, cy - 96)]), fill=m)
    # ojos
    for sx in (-1, 1):
        d.ellipse(P([(cx + sx * 52 - 20, cy - 48), (cx + sx * 52 + 20, cy - 12)]), fill=c)
        d.ellipse(P([(cx + sx * 52 - 8, cy - 36), (cx + sx * 52 + 8, cy - 20)]), fill=m)
    # hocico
    d.polygon(P([(cx - 26, cy + 18), (cx + 26, cy + 18), (cx, cy + 52)]), fill=ORO)
    d.line(P([(cx, cy + 52), (cx, cy + 78)]), fill=c, width=5 * S)
    d.arc(P([(cx - 36, cy + 56), (cx, cy + 96)]), 0, 100, fill=c, width=5 * S)
    d.arc(P([(cx, cy + 56), (cx + 36, cy + 96)]), 80, 180, fill=c, width=5 * S)
    # bigotes
    for sx in (-1, 1):
        for dy in (-6, 8, 22):
            d.line(P([(cx + sx * 40, cy + 52 + dy), (cx + sx * 96, cy + 44 + dy)]), fill=c, width=3 * S)
    # corona sobre la melena
    crown_mark(d, cx, cy - 258, 120, ORO, lw=9)
    # lema
    fb = ImageFont.truetype(F_BOLD, 30 * S)
    d.text((cx * S, (cy + 268) * S), "R E X   D E L   B A R R I O", font=fb, fill=darker(m, 0.9), anchor="mm")

# ============================================================
# 07 — Polo Rugby "Cadena" — Navy/Crema
def rugby_cadena(d, layer):
    def silo(dm):
        dm.polygon(P([(495, 445), (320, 535), (258, 1010), (402, 1044), (495, 725)]), fill=(255, 0, 0, 255))
        dm.polygon(P([(1105, 445), (1280, 535), (1342, 1010), (1198, 1044), (1105, 725)]), fill=(255, 0, 0, 255))
        dm.polygon(P([(495, 445), (665, 368), (935, 368), (1105, 445), (1085, 1240), (515, 1240)]), fill=(255, 0, 0, 255))
    m = part_mask(silo)
    layer.paste(Image.new("RGBA", layer.size, NAVY + (255,)), (0, 0), m.split()[3])
    def hoops(dp):
        for i, y in enumerate(range(380, 1300, 130)):
            if i % 2 == 1:
                dp.rectangle(P([(180, y), (1420, y + 65)]), fill=CREMA + (255,))
    paste_pattern(layer, m, hoops)
    d = ImageDraw.Draw(layer)
    # cuello blanco y placket
    d.polygon(P([(665, 368), (800, 400), (712, 486), (632, 428)]), fill=BLANCO)
    d.polygon(P([(935, 368), (800, 400), (888, 486), (968, 428)]), fill=BLANCO)
    d.rectangle(P([(779, 400), (821, 640)]), fill=BLANCO)
    for y in (450, 530, 610):
        d.ellipse(P([(793, y), (807, y + 14)]), fill=(210, 205, 194))
    # puños blancos
    d.polygon(P([(258, 1010), (402, 1044), (392, 1108), (248, 1074)]), fill=BLANCO)
    d.polygon(P([(1342, 1010), (1198, 1044), (1208, 1108), (1352, 1074)]), fill=BLANCO)
    # emblema cadena (pecho izquierdo) — 3 eslabones oro
    ex, ey = 645, 585
    for i in range(3):
        d.ellipse(P([(ex + i * 44 - 26, ey - 18), (ex + i * 44 + 26, ey + 18)]), outline=ORO, width=6 * S)

# ============================================================
# 08 — Pantalón Carpenter "Atelier" — Beige
def carpenter(d, layer):
    c = BEIGE
    hilo = (166, 124, 66)
    # cintura
    d.rectangle(P([(560, 360), (1040, 430)]), fill=darker(c, 0.9))
    d.ellipse(P([(792, 384), (816, 408)]), fill=ORO)
    # perneras
    d.polygon(P([(560, 430), (795, 430), (780, 1280), (545, 1280)]), fill=c)
    d.polygon(P([(805, 430), (1040, 430), (1055, 1280), (820, 1280)]), fill=c)
    # bragueta
    stitch_line(d, (800, 430), (800, 600), hilo)
    stitch_line(d, (778, 440), (772, 590), hilo)
    # bolsillos sesgados
    d.arc(P([(560, 400), (720, 560)]), 300, 60, fill=darker(c, 0.7), width=4 * S)
    d.arc(P([(880, 400), (1040, 560)]), 120, 240, fill=darker(c, 0.7), width=4 * S)
    stitch_line(d, (588, 452), (668, 540), hilo)
    stitch_line(d, (1012, 452), (932, 540), hilo)
    # panel doble rodilla
    for x0, x1 in ((572, 772), (828, 1028)):
        d.rectangle(P([(x0, 830), (x1, 1050)]), fill=darker(c, 0.94), outline=darker(c, 0.8), width=2 * S)
        stitch_path(d, [(x0 + 8, 838), (x1 - 8, 838)], hilo)
        stitch_path(d, [(x0 + 8, 1042), (x1 - 8, 1042)], hilo)
    # martillera (hammer loop) lado derecho
    d.arc(P([(1032, 620), (1108, 760)]), 270, 90, fill=darker(c, 0.75), width=10 * S)
    # bolsillo lateral herramienta
    d.rectangle(P([(590, 620), (740, 780)]), outline=darker(c, 0.75), width=3 * S)
    stitch_path(d, [(590, 620), (590, 780), (740, 780), (740, 620)], hilo)
    d.line(P([(665, 620), (665, 780)]), fill=darker(c, 0.8), width=2 * S)
    # etiqueta jacquard burdeos/oro en cintura
    d.rectangle(P([(880, 372), (980, 418)]), fill=BURDEOS)
    crown_mark(d, 930, 392, 40, ORO, lw=4)
    # bajos con costura
    stitch_line(d, (552, 1250), (778, 1250), hilo)
    stitch_line(d, (822, 1250), (1048, 1250), hilo)
    # costuras laterales
    stitch_line(d, (560, 440), (545, 1275), hilo, dash=16, gap=12)
    stitch_line(d, (1040, 440), (1055, 1275), hilo, dash=16, gap=12)

# ---------- calzado: helpers ----------
def sole_wave(d, x0, x1, ytop, h, color, n=9):
    pts = [(x0, ytop)]
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        pts.append((x, ytop + (6 if i % 2 == 0 else -6)))
    pts += [(x1, ytop + h), (x0, ytop + h)]
    d.polygon(P(pts), fill=color)

def lace_cross(d, x0, y0, n, dx, dy, color, w=7):
    for i in range(n):
        d.line(P([(x0 + i * dx, y0 + i * dy), (x0 + dx + i * dx, y0 + dy + i * dy - 26)]), fill=color, width=w * S)
        d.line(P([(x0 + dx + i * dx, y0 + i * dy), (x0 + i * dx, y0 + dy + i * dy - 26)]), fill=color, width=w * S)

# ============================================================
# 09 — Zapatillas Deportivas "Llave" — Blanco/Caramelo (runner perfil)
def runner_llave(d, layer):
    # suela gum ondulada
    sole_wave(d, 300, 1310, 1010, 95, GUM)
    d.rectangle(P([(300, 1085), (1310, 1105)]), fill=darker(GUM, 0.8))
    # entresuela blanca
    d.polygon(P([(295, 940), (1315, 940), (1310, 1015), (300, 1015)]), fill=BLANCO)
    # upper
    d.polygon(P([(320, 950), (355, 700), (520, 640), (660, 630), (700, 560), (960, 520),
                 (1140, 700), (1300, 850), (1305, 945)]), fill=(228, 224, 214),
              outline=(196, 192, 182), width=3 * S)
    # puntera mesh
    for yy in range(880, 945, 16):
        for xx in range(1120, 1290, 24):
            d.ellipse(P([(xx, yy), (xx + 7, yy + 7)]), fill=(205, 202, 195))
    # talonera navy
    d.polygon(P([(320, 950), (355, 700), (470, 660), (500, 950)]), fill=NAVY)
    # panel lateral + llave dorada
    kx, ky = 760, 830
    d.ellipse(P([(kx - 70, ky - 40), (kx - 6, ky + 24)]), outline=ORO, width=8 * S)
    d.line(P([(kx - 6, ky - 8), (kx + 150, ky - 8)]), fill=ORO, width=8 * S)
    d.line(P([(kx + 110, ky - 8), (kx + 110, ky + 26)]), fill=ORO, width=8 * S)
    d.line(P([(kx + 145, ky - 8), (kx + 145, ky + 34)]), fill=ORO, width=8 * S)
    # lengüeta + cordones
    d.polygon(P([(700, 560), (960, 520), (990, 585), (730, 630)]), fill=(238, 236, 230))
    lace_cross(d, 715, 590, 4, 62, 12, (215, 212, 205))
    # costuras
    stitch_path(d, [(520, 645), (660, 635), (700, 565)], (185, 182, 175))
    stitch_path(d, [(500, 945), (505, 690)], (150, 160, 185))
    crown_mark(d, 400, 800, 54, ORO, lw=5)

# ============================================================
# 10 — Zapatillas Altas "Guardia" — Negro/Gum (high-top perfil)
def hightop_guardia(d, layer):
    sole_wave(d, 310, 1300, 1030, 90, GUM)
    d.polygon(P([(305, 960), (1305, 960), (1300, 1035), (310, 1035)]), fill=BLANCO)
    # upper alto
    d.polygon(P([(330, 970), (350, 520), (560, 470), (700, 500), (740, 600), (980, 560),
                 (1150, 730), (1295, 870), (1300, 965)]), fill=NEGRO)
    # cuello tobillo acolchado (banda siguiendo el borde superior)
    d.line(P([(365, 545), (575, 495)]), fill=lighter(NEGRO, 2.0), width=44 * S)
    d.ellipse(P([(345, 523), (389, 567)]), fill=lighter(NEGRO, 2.0))
    d.ellipse(P([(553, 473), (597, 517)]), fill=lighter(NEGRO, 2.0))
    # banda "guardia" diagonal tricolor
    for i, col in enumerate((BURDEOS, ORO, NAVY)):
        d.line(P([(760 + i * 46, 960), (930 + i * 46, 600)]), fill=col, width=26 * S)
    # puntera
    d.chord(P([(1140, 830), (1310, 990)]), 180, 360, fill=(230, 228, 222))
    # ojales y cordones
    eyelets = [(600, 560 + i * 66) for i in range(6)]
    for ex, ey in eyelets:
        d.ellipse(P([(ex - 9, ey - 9), (ex + 9, ey + 9)]), fill=ORO)
    for i in range(5):
        d.line(P([(600, 560 + i * 66), (668, 594 + i * 66)]), fill=(226, 222, 214), width=9 * S)
        d.line(P([(668, 560 + i * 66 + 34), (600, 560 + (i + 1) * 66)]), fill=(210, 206, 198), width=9 * S)
    stitch_path(d, [(505, 950), (520, 600)], (120, 120, 126))
    crown_mark(d, 440, 760, 56, ORO, lw=5)

# ============================================================
# 11 — Zapatillas Lona "Rombo Real" — Crudo
def lona_rombo(d, layer):
    # foxing blanco
    d.rectangle(P([(310, 985), (1300, 1075)]), fill=BLANCO)
    d.line(P([(310, 1005), (1300, 1005)]), fill=(200, 60, 50), width=5 * S)
    d.rectangle(P([(310, 1075), (1300, 1100)]), fill=darker(BLANCO, 0.75))
    def silo(dm):
        dm.polygon(P([(330, 990), (360, 730), (560, 665), (700, 655), (745, 585), (985, 545),
                      (1150, 720), (1295, 865), (1298, 990)]), fill=(255, 0, 0, 255))
    m = part_mask(silo)
    layer.paste(Image.new("RGBA", layer.size, CRUDO + (255,)), (0, 0), m.split()[3])
    def rombos(dp):
        s = 56
        for yy in range(500, 1000, s):
            for xx in range(300, 1320, s):
                off = (yy // s) % 2 * (s // 2)
                cx0, cy0 = xx + off, yy
                pts = [(cx0, cy0 - 14), (cx0 + 14, cy0), (cx0, cy0 + 14), (cx0 - 14, cy0)]
                col = BURDEOS if ((xx + yy) // s) % 2 == 0 else NAVY
                dp.polygon(P(pts), outline=col + (200,), width=2 * S)
                dp.ellipse(P([(cx0 - 2, cy0 - 2), (cx0 + 2, cy0 + 2)]), fill=ORO + (230,))
    paste_pattern(layer, m, rombos)
    d = ImageDraw.Draw(layer)
    # puntera goma
    d.chord(P([(1130, 820), (1305, 995)]), 160, 360, fill=BLANCO)
    # talonera
    d.polygon(P([(330, 990), (360, 730), (470, 700), (492, 990)]), fill=darker(CRUDO, 0.85))
    d.rectangle(P([(370, 760), (462, 820)]), fill=BURDEOS)
    crown_mark(d, 416, 790, 50, CREMA, lw=4)
    # lengüeta + cordones planos
    d.polygon(P([(745, 585), (985, 545), (1010, 610), (775, 655)]), fill=darker(CRUDO, 0.92))
    lace_cross(d, 755, 615, 4, 58, 11, BLANCO, w=9)
    stitch_path(d, [(560, 670), (700, 660), (745, 590)], (170, 160, 140))

# ============================================================
# 12 — Slides Acolchados "Trono" — Chocolate
def slides_trono(d, layer):
    # plataforma
    d.polygon(P([(330, 1010), (1290, 1010), (1260, 1120), (360, 1120)]), fill=darker(CHOCO, 0.8))
    d.polygon(P([(330, 1010), (1290, 1010), (1300, 960), (320, 960)]), fill=CHOCO)
    # plantilla
    d.line(P([(340, 962), (1285, 962)]), fill=lighter(CHOCO, 1.4), width=6 * S)
    # tira acolchada: arco grueso sobre el empeine
    d.arc(P([(470, 680), (1160, 1240)]), 185, 355, fill=lighter(CHOCO, 1.3), width=110 * S)
    d.arc(P([(470, 680), (1160, 1240)]), 185, 355, fill=lighter(CHOCO, 1.55), width=18 * S)
    # costuras de acolchado (radiales)
    cx, cy = 815, 960
    for ang in (215, 250, 290, 325):
        a = math.radians(ang)
        r1, r2 = 218, 336
        d.line(P([(cx + r1 * math.cos(a), cy + r1 * math.sin(a) * 0.82),
                  (cx + r2 * math.cos(a), cy + r2 * math.sin(a) * 0.82)]),
               fill=darker(CHOCO, 0.72), width=7 * S)
    # corona grabada en la tira
    crown_mark(d, 815, 742, 88, ORO, lw=7)
    # textura suela
    for x in range(390, 1240, 60):
        d.line(P([(x, 1035), (x - 14, 1102)]), fill=darker(CHOCO, 0.65), width=5 * S)

# ============================================================
# 13 — Gorra "Pata de Gallo" — Negro/Blanco
def gorra_pdg(d, layer):
    def silo(dm):
        dm.pieslice(P([(430, 430), (1170, 1120)]), 180, 360, fill=(255, 0, 0, 255))
        dm.polygon(P([(430, 775), (1170, 775), (1170, 860), (430, 860)]), fill=(255, 0, 0, 255))
    m = part_mask(silo)
    layer.paste(Image.new("RGBA", layer.size, BLANCO + (255,)), (0, 0), m.split()[3])
    def hound(dp):
        s = 46
        for yy in range(380, 900, s):
            for xx in range(380, 1220, s):
                # tile pata de gallo simplificado
                dp.polygon(P([(xx, yy), (xx + s // 2, yy), (xx, yy + s // 2)]), fill=NEGRO + (255,))
                dp.polygon(P([(xx + s // 2, yy + s // 2), (xx + s, yy + s // 2), (xx + s, yy), (xx + s * 3 // 4, yy)]), fill=NEGRO + (255,))
                dp.polygon(P([(xx + s // 2, yy + s // 2), (xx + s // 2, yy + s), (xx, yy + s), (xx, yy + s * 3 // 4)]), fill=NEGRO + (255,))
    paste_pattern(layer, m, hound)
    d = ImageDraw.Draw(layer)
    # costuras de paneles
    d.arc(P([(430, 430), (1170, 1120)]), 180, 360, fill=(90, 90, 94), width=3 * S)
    d.arc(P([(620, 470), (980, 1120)]), 180, 360, fill=(90, 90, 94), width=3 * S)
    d.line(P([(800, 432), (800, 775)]), fill=(90, 90, 94), width=3 * S)
    # botón y ojal
    d.ellipse(P([(786, 420), (814, 448)]), fill=NEGRO)
    d.ellipse(P([(692, 560), (716, 584)]), fill=NEGRO, outline=(120, 120, 124), width=2 * S)
    # visera negra
    d.pieslice(P([(560, 640), (1330, 1010)]), 315, 90, fill=NEGRO)
    d.arc(P([(600, 660), (1290, 990)]), 320, 85, fill=lighter(NEGRO, 2.0), width=4 * S)
    # banda inferior
    d.rectangle(P([(430, 800), (1000, 860)]), fill=NEGRO)
    crown_mark(d, 620, 830, 56, ORO, lw=5)

# ============================================================
# 14 — Bandana "Paisley Real" — Burdeos
def bandana_paisley(d, layer):
    x0, y0, x1, y1 = 330, 380, 1270, 1240
    d.rectangle(P([(x0, y0), (x1, y1)]), fill=BURDEOS)
    # marcos
    for pad, col, wd in ((36, CREMA, 3), (58, ORO, 2), (74, CREMA, 2)):
        d.rectangle(P([(x0 + pad, y0 + pad), (x1 - pad, y1 - pad)]), outline=col, width=wd * S)
    def paisley(cx, cy, sc, rot):
        # lágrima paisley: círculo + cola curva
        r = 60 * sc
        d.ellipse(P([(cx - r, cy - r), (cx + r, cy + r)]), outline=CREMA, width=4 * S)
        d.ellipse(P([(cx - r * .55, cy - r * .55), (cx + r * .55, cy + r * .55)]), outline=ORO, width=3 * S)
        d.ellipse(P([(cx - r * .2, cy - r * .2), (cx + r * .2, cy + r * .2)]), fill=CREMA)
        a0 = rot
        d.arc(P([(cx - r * 1.7, cy - r * 1.7), (cx + r * 1.7, cy + r * 1.7)]), a0, a0 + 120, fill=CREMA, width=4 * S)
        ax = cx + r * 1.7 * math.cos(math.radians(a0 + 120)) / 2
    # esquinas
    for (cx, cy, rot) in ((x0 + 190, y0 + 190, 200), (x1 - 190, y0 + 190, 300),
                          (x0 + 190, y1 - 190, 100), (x1 - 190, y1 - 190, 0)):
        paisley(cx, cy, 1.0, rot)
    # centro: medallón corona
    d.ellipse(P([(716, 726), (884, 894)]), outline=ORO, width=4 * S)
    d.ellipse(P([(700, 710), (900, 910)]), outline=CREMA, width=3 * S)
    crown_mark(d, 800, 800, 90, CREMA, lw=7)
    # campo de puntos
    for yy in range(y0 + 120, y1 - 110, 64):
        for xx in range(x0 + 120, x1 - 110, 64):
            if abs(xx - 800) > 160 or abs(yy - 810) > 160:
                if (xx // 64 + yy // 64) % 2 == 0:
                    d.ellipse(P([(xx - 4, yy - 4), (xx + 4, yy + 4)]), fill=ORO)
    # pliegue: sombra diagonal sutil
    d.line(P([(x0, y0), (x1, y1)]), fill=darker(BURDEOS, 0.85), width=3 * S)

PRODUCTS = [
    (camisa_oxford,    "Camisa Oxford Firma — Blanco",           "camisa-oxford-firma.jpg"),
    (sobrecamisa_tartan, "Sobrecamisa Franela Tartán Real — Burdeos", "sobrecamisa-tartan-real.jpg"),
    (jersey_cetro,     "Jersey de Punto Cetro — Crema",          "jersey-cetro.jpg"),
    (cardigan_ajedrez, "Cárdigan Ajedrez Real — Negro",          "cardigan-ajedrez-real.jpg"),
    (denim_estandarte, "Chaqueta Denim Estandarte — Azul Lavado", "denim-estandarte.jpg"),
    (tee_leon,         "Camiseta León Heráldico — Piedra",       "camiseta-leon-heraldico.jpg"),
    (rugby_cadena,     "Polo Rugby Cadena — Navy/Crema",         "polo-rugby-cadena.jpg"),
    (carpenter,        "Pantalón Carpenter Atelier — Beige",     "pantalon-carpenter-atelier.jpg"),
    (runner_llave,     "Zapatillas Deportivas Llave — Blanco/Caramelo", "zapatillas-llave.jpg"),
    (hightop_guardia,  "Zapatillas Altas Guardia — Negro/Gum",   "zapatillas-altas-guardia.jpg"),
    (lona_rombo,       "Zapatillas Lona Rombo Real — Crudo",     "zapatillas-lona-rombo.jpg"),
    (slides_trono,     "Slides Acolchados Trono — Chocolate",    "slides-trono.jpg"),
    (gorra_pdg,        "Gorra Pata de Gallo — Negro/Blanco",     "gorra-pata-de-gallo.jpg"),
    (bandana_paisley,  "Bandana Paisley Real — Burdeos",         "bandana-paisley-real.jpg"),
]

if __name__ == "__main__":
    total = len(PRODUCTS)
    for i, (fn, subtitle, fname) in enumerate(PRODUCTS, 1):
        compose(fn, "STREET ROYALTY HOOD", subtitle, i, total, fname)
    # hoja de contacto para revisión
    cols, rows = 4, 4
    sheet = Image.new("RGB", (cols * 400, rows * 400), (240, 240, 240))
    for i, (_, _, fname) in enumerate(PRODUCTS):
        im = Image.open(f"{OUT}/{fname}").resize((400, 400))
        sheet.paste(im, ((i % cols) * 400, (i // cols) * 400))
    sheet.save(f"{OUT}/_contact.jpg", quality=85)
    print("done")
