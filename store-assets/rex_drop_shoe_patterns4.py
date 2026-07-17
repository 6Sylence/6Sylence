# -*- coding: utf-8 -*-
# SRHOOD — calzado drop 4: greca, terrazo, blueprint, pinstripe, wordmark chanclas
import math, os, random
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

def meander(d, x0, y0, s, color, lw, flip=False):
    u = s / 8.0
    pts = [(1,7),(1,1),(7,1),(7,7),(3,7),(3,3),(5,3),(5,5)]
    if flip: pts = [(px, 8-py) for px, py in pts]
    d.line([(x0+px*u, y0+py*u) for px, py in pts], fill=color, width=lw, joint="curve")

# 1) Greca Real — high top 2250 (x2). Meandro griego oro sobre negro + coronas
S = 4500
img = Image.new("RGBA", (S, S), NEGRO)
d = ImageDraw.Draw(img)
tile = 560
for r in range(-1, S // tile + 2):
    for c in range(-1, S // tile + 2):
        meander(d, c * tile, r * tile, tile, ORO, 22, flip=(r % 2 == 1))
# banda de coronas cada 2 filas
for r in range(0, S // tile + 1, 2):
    for c in range(0, S // tile + 1):
        crown(d, c * tile + tile*0.5, r * tile + tile*0.5, 150, (201,162,75,150), 9)
img.convert("RGB").save(f"{OUT}/pattern-greca.png")
print("ok greca")

# 2) Terrazo Real — slip-on 2325 (x2). Terrazo speckle sobre crema + coronas oro ocasionales
S = 4650
img = Image.new("RGBA", (S, S), CREMA)
d = ImageDraw.Draw(img)
rnd = random.Random(21)
cols = [BURDEOS, NAVY, OLIVA, (201,162,75,255), (60,60,66,255)]
for _ in range(900):
    cx, cy = rnd.randint(0, S), rnd.randint(0, S)
    r = rnd.randint(22, 70)
    col = rnd.choice(cols)
    k = rnd.randint(3, 6)
    pts = []
    for i in range(k):
        a = 2*math.pi*i/k + rnd.random()
        rr = r * (0.6 + rnd.random()*0.7)
        pts.append((cx+rr*math.cos(a), cy+rr*math.sin(a)))
    d.polygon(pts, fill=col)
for _ in range(30):
    crown(d, rnd.randint(150, S-150), rnd.randint(150, S-150), 150, (201,162,75,230), 10)
img.convert("RGB").save(f"{OUT}/pattern-terrazo.png")
print("ok terrazo")

# 3) Blueprint Real — athletic 1950x3300 (x2). Plano técnico corona en navy
W, H = 3900, 6600
img = Image.new("RGBA", (W, H), NAVY)
d = ImageDraw.Draw(img)
grid = 150
for x in range(0, W, grid):
    d.line([(x,0),(x,H)], fill=(255,255,255,26), width=2)
for y in range(0, H, grid):
    d.line([(0,y),(W,y)], fill=(255,255,255,26), width=2)
def blueprint_crown(cx, cy, s, col):
    crown(d, cx, cy, s, col, 12)
    # círculos de construcción y ejes
    for rad in (s*0.7, s*0.42):
        d.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], outline=(255,255,255,90), width=3)
    d.line([(cx-s*0.9, cy),(cx+s*0.9, cy)], fill=(255,255,255,70), width=2)
    d.line([(cx, cy-s*0.9),(cx, cy+s*0.9)], fill=(255,255,255,70), width=2)
for r in range(4):
    for c in range(2):
        blueprint_crown(500 + c*1900, 500 + r*1650, 460, ORO)
# cotas técnicas
f = ImageFont.truetype(FB, 90)
for r in range(4):
    d.text((150, 500 + r*1650 - 620), "SRH · REX · 2026", font=f, fill=(255,255,255,120))
img.convert("RGB").save(f"{OUT}/pattern-blueprint.png")
print("ok blueprint")

# 4) Pinstripe Royal — lace-up 2250 (x2). Rayas finas navy + micro-coronas
S = 4500
img = Image.new("RGBA", (S, S), NAVY)
d = ImageDraw.Draw(img)
for x in range(0, S, 150):
    d.line([(x,0),(x,S)], fill=(233,226,208,235), width=10)
for r in range(0, S, 300):
    for c in range(75, S, 300):
        crown(d, c, r+150, 90, (201,162,75,235), 7)
img.convert("RGB").save(f"{OUT}/pattern-pinstripe.png")
print("ok pinstripe")

# 5) Wordmark chanclas — flip flops 1650x1950 (x2). Navy + wordmark oro + corona central
W, H = 3300, 3900
img = Image.new("RGBA", (W, H), NAVY)
d = ImageDraw.Draw(img)
f = ImageFont.truetype(FB, 130)
txt = "STREET ROYALTY HOOD  ·  "
row = Image.new("RGBA", (W*2, 200), (0,0,0,0))
dr = ImageDraw.Draw(row)
x = 0
while x < row.size[0]:
    dr.text((x, 34), txt, font=f, fill=ORO); x += int(dr.textlength(txt, font=f))
for i, yy in enumerate(range(-100, H, 260)):
    off = -(i*150) % int(dr.textlength(txt, font=f))
    img.alpha_composite(row, (-off, yy))
# corona grande centrada (cubierta parcialmente por la tira pero refuerza)
crown(d, W//2, int(H*0.30), 820, ORO, 60)
img.convert("RGB").save(f"{OUT}/pattern-wordmark-flipflops.png")
print("ok wordmark-ff")

sheet = Image.new("RGB", (1500, 1000), (245,245,245))
names = ["pattern-greca.png","pattern-terrazo.png","pattern-blueprint.png","pattern-pinstripe.png","pattern-wordmark-flipflops.png"]
for i, n2 in enumerate(names):
    sheet.paste(Image.open(f"{OUT}/{n2}").resize((500,500)), ((i%3)*500,(i//3)*500))
sheet.save(f"{OUT}/_patterns4.jpg", quality=85)
print("done")
