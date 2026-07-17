# -*- coding: utf-8 -*-
# SRHOOD — patrones calzado drop 2: Dinastía (athletic), Tartán Real (lace-up), Corona (flip flops)
import math, os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__)) + "/prints"
ORO = (201, 162, 75, 255)
CREMA = (242, 234, 216, 255)
BURDEOS = (107, 34, 49, 255)
NAVY = (30, 42, 68, 255)
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
        d.ellipse([x-w*0.035, y-w*0.035, x+w*0.035, y+w*0.035], fill=color)

# 1) Dinastía — athletic 1950x3300 (x2)
W, H = 3900, 6600
img = Image.new("RGBA", (W, H), (240, 237, 230, 255))
d = ImageDraw.Draw(img)
# bandas diagonales dinámicas (45º): navy ancha + pinlines oro
step = 900
for i in range(-8, 16):
    x0 = i * step
    d.line([(x0, H), (x0 + H, 0)], fill=NAVY, width=150)
    d.line([(x0 + 260, H), (x0 + 260 + H, 0)], fill=ORO, width=44)
    d.line([(x0 + 380, H), (x0 + 380 + H, 0)], fill=(180, 175, 162, 255), width=18)
# coronas tonales dispersas sobre las bandas
for row in range(8):
    for col in range(5):
        x = col * 800 + (400 if row % 2 else 0)
        y = row * 880 + 300
        crown(d, x, y, 150, (255, 255, 255, 200), 12)
img.convert("RGB").save(f"{OUT}/pattern-dinastia.png")
print("ok dinastia")

# 2) Tartán Real — lace-up 2250 (x2)
S = 4500
img = Image.new("RGBA", (S, S), BURDEOS)
d = ImageDraw.Draw(img)
cell = 470
for x in range(0, S + cell, cell):
    d.rectangle([x, 0, x + 170, S], fill=(84, 27, 39, 255))
    d.line([(x + 300, 0), (x + 300, S)], fill=ORO, width=14)
    d.line([(x + 90, 0), (x + 90, S)], fill=(30, 42, 68, 140), width=54)
for y in range(0, S + cell, cell):
    d.rectangle([0, y, S, y + 170], fill=(84, 27, 39, 200))
    d.line([(0, y + 300), (S, y + 300)], fill=ORO, width=14)
    d.line([(0, y + 90), (S, y + 90)], fill=(30, 42, 68, 140), width=54)
img.convert("RGB").save(f"{OUT}/pattern-tartan-shoes.png")
print("ok tartan")

# 3) Corona — flip flops footbed 1650x1950 (x2)
W, H = 3300, 3900
img = Image.new("RGBA", (W, H), BURDEOS)
d = ImageDraw.Draw(img)
for pad, col, wd in ((140, ORO, 16), (210, CREMA, 8)):
    d.rectangle([pad, pad, W - pad, H - pad], outline=col, width=wd)
crown(d, W//2, int(H*0.30), 900, ORO, 70)
f = ImageFont.truetype(FB, 330)
d.text((W//2, int(H*0.52)), "SRH", font=f, fill=CREMA, anchor="mm")
f2 = ImageFont.truetype(FB, 120)
d.text((W//2, int(H*0.64)), "STREET ROYALTY HOOD", font=f2, fill=ORO, anchor="mm")
f3 = ImageFont.truetype(FB, 100)
d.text((W//2, int(H*0.78)), "REX DEL BARRIO · MMXXVI", font=f3, fill=CREMA, anchor="mm")
for yy in range(int(H*0.86), int(H*0.90), 40):
    for xx in range(500, W-400, 350):
        d.ellipse([xx-14, yy-14, xx+14, yy+14], fill=ORO)
img.convert("RGB").save(f"{OUT}/pattern-corona-flipflops.png")
print("ok flipflops")

sheet = Image.new("RGB", (1500, 500), (245, 245, 245))
for i, n in enumerate(["pattern-dinastia.png", "pattern-tartan-shoes.png", "pattern-corona-flipflops.png"]):
    sheet.paste(Image.open(f"{OUT}/{n}").resize((500, 500)), (i * 500, 0))
sheet.save(f"{OUT}/_patterns2.jpg", quality=85)
print("done")
