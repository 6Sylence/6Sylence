# -*- coding: utf-8 -*-
# SRHOOD — calzado drop 3: 2ª tanda de colorways, motivos nuevos
import math, os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__)) + "/prints"
os.makedirs(OUT, exist_ok=True)
ORO = (201, 162, 75, 255)
CREMA = (242, 234, 216, 255)
BURDEOS = (107, 34, 49, 255)
NAVY = (30, 42, 68, 255)
NEGRO = (20, 21, 26, 255)
OLIVA = (90, 95, 69, 255)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def crown(d, cx, cy, w, color, lw):
    h = w * 0.52
    pts = [(cx - w/2, cy + h/2), (cx - w/2, cy - h*0.1), (cx - w*0.25, cy + h*0.05),
           (cx, cy - h/2), (cx + w*0.25, cy + h*0.05), (cx + w/2, cy - h*0.1),
           (cx + w/2, cy + h/2), (cx - w/2, cy + h/2)]
    d.line(pts, fill=color, width=lw, joint="curve")
    for i in range(6):
        x = cx - w/2 + (i + 0.5) * w / 6
        y = cy + h/2 + h*0.22
        r = max(2, w * 0.035)
        d.ellipse([x-r, y-r, x+r, y+r], fill=color)

# 1) Damero Real — slip-on 2325 (x2). Checkerboard negro/burdeos + micro-coronas oro
S = 4650
img = Image.new("RGBA", (S, S), NEGRO)
d = ImageDraw.Draw(img)
n = 10
cell = S / n
for r in range(n + 1):
    for c in range(n + 1):
        if (r + c) % 2 == 0:
            x0, y0 = c * cell, r * cell
            d.rectangle([x0, y0, x0 + cell, y0 + cell], fill=BURDEOS)
            crown(d, x0 + cell/2, y0 + cell/2, cell * 0.4, ORO, 10)
img.convert("RGB").save(f"{OUT}/pattern-damero.png")
print("ok damero")

# 2) Camuflaje Corona — high top 2250 (x2). Camo crema/oliva/navy/burdeos + coronas oro
S = 4500
img = Image.new("RGBA", (S, S), CREMA)
d = ImageDraw.Draw(img)
import random
rnd = random.Random(7)
def blob(cx, cy, rad, col):
    pts = []
    steps = 14
    for i in range(steps):
        a = 2 * math.pi * i / steps
        rr = rad * (0.68 + rnd.random() * 0.5)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col)
for col in (OLIVA, NAVY, BURDEOS):
    for _ in range(26):
        blob(rnd.randint(0, S), rnd.randint(0, S), rnd.randint(300, 560), col)
for _ in range(40):
    crown(d, rnd.randint(200, S-200), rnd.randint(200, S-200), 150, (201, 162, 75, 210), 9)
img.convert("RGB").save(f"{OUT}/pattern-camo.png")
print("ok camo")

# 3) Circuito GP — athletic 1950x3300 (x2). Varias bandas de bandera a cuadros + pinlines oro + coronas
W, H = 3900, 6600
img = Image.new("RGBA", (W, H), NEGRO)
sq = 150
band = 300
# rejilla a cuadros grande para recortar en bandas
grid = Image.new("RGBA", (int(W*1.8), int(H*1.8)), (0, 0, 0, 0))
dg = ImageDraw.Draw(grid)
for yy in range(0, grid.size[1], sq):
    for xx in range(0, grid.size[0], sq):
        if ((xx // sq) + (yy // sq)) % 2 == 0:
            dg.rectangle([xx, yy, xx + sq, yy + sq], fill=CREMA)
# tres bandas diagonales a distintas alturas
for cy in (int(H*0.22), int(H*0.55), int(H*0.88)):
    mask = Image.new("L", grid.size, 0)
    dm = ImageDraw.Draw(mask)
    yc = grid.size[1] // 2
    dm.rectangle([0, yc - band, grid.size[0], yc + band], fill=255)
    strip = grid.copy()
    strip.putalpha(Image.composite(strip.split()[3], Image.new("L", strip.size, 0), mask))
    strip = strip.rotate(20, resample=Image.BICUBIC, expand=False)
    img.alpha_composite(strip, (int((W - strip.size[0]) / 2), cy - grid.size[1]//2))
d = ImageDraw.Draw(img)
# pinlines oro que acompañan cada banda
for cy in (int(H*0.22), int(H*0.55), int(H*0.88)):
    for off in (-band-50, band+50):
        dyy = int(math.tan(math.radians(20)) * (W/2 + 200))
        d.line([(-200, cy + off + dyy), (W+200, cy + off - dyy)], fill=ORO, width=28)
# coronas oro dispersas entre bandas
for i in range(12):
    crown(d, 380 + (i % 3) * 1450, 340 + (i // 3) * 1620, 190, ORO, 13)
img.convert("RGB").save(f"{OUT}/pattern-circuito.png")
print("ok circuito")

# 4) Wordmark Repeat — lace-up 2250 (x2). Base navy, "STREET ROYALTY HOOD" oro en filas diagonales
S = 4500
img = Image.new("RGBA", (S, S), NAVY)
d = ImageDraw.Draw(img)
f = ImageFont.truetype(FB, 150)
txt = "STREET ROYALTY HOOD  ·  "
row = Image.new("RGBA", (S * 2, 240), (0, 0, 0, 0))
dr = ImageDraw.Draw(row)
x = 0
while x < row.size[0]:
    dr.text((x, 40), txt, font=f, fill=ORO)
    x += int(dr.textlength(txt, font=f))
for i, yy in enumerate(range(-200, S, 300)):
    off = -(i * 180) % int(dr.textlength(txt, font=f))
    img.alpha_composite(row, (-off, yy))
img.convert("RGB").save(f"{OUT}/pattern-wordmark-shoes.png")
print("ok wordmark")

# 5) Corona Scatter — slides 1650 (x2). Base burdeos, coronas oro/crema dispersas
S = 3300
img = Image.new("RGBA", (S, S), BURDEOS)
d = ImageDraw.Draw(img)
rnd2 = random.Random(11)
placed = []
for _ in range(60):
    for _try in range(20):
        cx, cy = rnd2.randint(120, S-120), rnd2.randint(120, S-120)
        w = rnd2.choice([170, 220, 270, 330])
        if all((cx-px)**2 + (cy-py)**2 > (w*0.72)**2 for px, py, pw in placed):
            placed.append((cx, cy, w))
            col = ORO if rnd2.random() < 0.7 else CREMA
            crown(d, cx, cy, w, col, max(9, int(w*0.05)))
            break
img.convert("RGB").save(f"{OUT}/pattern-scatter.png")
print("ok scatter")

sheet = Image.new("RGB", (1500, 1000), (245, 245, 245))
names = ["pattern-damero.png", "pattern-camo.png", "pattern-circuito.png",
         "pattern-wordmark-shoes.png", "pattern-scatter.png"]
for i, n2 in enumerate(names):
    sheet.paste(Image.open(f"{OUT}/{n2}").resize((500, 500)), ((i % 3) * 500, (i // 3) * 500))
sheet.save(f"{OUT}/_patterns3.jpg", quality=85)
print("done")
