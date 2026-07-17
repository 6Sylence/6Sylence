# -*- coding: utf-8 -*-
# SRHOOD — patrones all-over para calzado Printful (fill_mode cover)
import math, os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__)) + "/prints"
os.makedirs(OUT, exist_ok=True)
ORO = (201, 162, 75, 255)
CREMA = (242, 234, 216, 255)
BURDEOS = (107, 34, 49, 255)
NAVY = (30, 42, 68, 255)
NEGRO = (20, 21, 26, 255)
CRUDO = (233, 226, 208, 255)
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

def lion_mini(d, cx, cy, r, main, accent):
    pts = []
    for i in range(20):
        a = math.pi*2*i/20 - math.pi/2
        rr = r if i % 2 == 0 else r*0.74
        pts.append((cx + rr*math.cos(a), cy + rr*math.sin(a)))
    d.polygon(pts, fill=main)
    d.ellipse([cx-r*0.56, cy-r*0.56, cx+r*0.56, cy+r*0.56], outline=accent, width=max(3, int(r*0.07)))
    for sx in (-1, 1):
        d.ellipse([cx+sx*r*0.24-r*0.09, cy-r*0.22-r*0.09, cx+sx*r*0.24+r*0.09, cy-r*0.22+r*0.09], fill=accent)
    d.polygon([(cx-r*0.13, cy+r*0.08), (cx+r*0.13, cy+r*0.08), (cx, cy+r*0.28)], fill=accent)

# 1) Rex — high tops negras (2250 spec -> 4500)
S = 4500
img = Image.new("RGBA", (S, S), NEGRO)
d = ImageDraw.Draw(img)
step = 750
for row in range(-1, S//step + 2):
    for col in range(-1, S//step + 2):
        x = col*step + (step//2 if row % 2 else 0)
        y = row*step
        if (row + col) % 2 == 0:
            lion_mini(d, x, y, 190, ORO, NEGRO)
        else:
            crown(d, x, y, 220, CREMA, 16)
img.convert("RGB").save(f"{OUT}/pattern-rex.png")
img.save(f"{OUT}/pattern-rex-rgba.png")
print("ok rex")

# 2) Cadena — slip-on crudo (2325 spec -> 4650)
S = 4650
img = Image.new("RGBA", (S, S), CRUDO)
d = ImageDraw.Draw(img)
lw, a, b = 46, 300, 190   # eslabón: semiejes
stepx = int(a*1.62)
for row in range(-1, S//(b*3) + 3):
    y = row * b*3
    off = stepx//2 if row % 2 else 0
    for i in range(-1, S//stepx + 2):
        x = i*stepx + off
        col = ORO if i % 2 == 0 else NAVY
        d.ellipse([x-a, y-b, x+a, y+b], outline=col, width=lw)
    ym = y + int(b*1.5)
    for i in range(-1, S//stepx + 2):
        x = i*stepx + stepx//2 + off
        crown(d, x, ym, 130, (166, 124, 66, 255), 10)
img.convert("RGB").save(f"{OUT}/pattern-cadena.png")
print("ok cadena")

# 3) Estandarte — slides negras (1650 spec -> 3300)
S = 3300
img = Image.new("RGBA", (S, S), BURDEOS)
d = ImageDraw.Draw(img)
for pad, col, w in ((150, ORO, 14), (210, CREMA, 8)):
    d.rectangle([pad, pad, S-pad, S-pad], outline=col, width=w)
crown(d, S//2, S//2 - 260, 1050, ORO, 80)
f = ImageFont.truetype(FB, 430)
d.text((S//2, S//2 + 560), "SRH", font=f, fill=CREMA, anchor="mm")
d.line([(S//2-520, S//2+900), (S//2+520, S//2+900)], fill=ORO, width=22)
f2 = ImageFont.truetype(FB, 120)
d.text((S//2, S//2 + 1080), "STREET ROYALTY HOOD", font=f2, fill=ORO, anchor="mm")
for xx in range(400, S-300, 420):
    for yy in (420, S-430):
        d.ellipse([xx-16, yy-16, xx+16, yy+16], fill=ORO)
img.convert("RGB").save(f"{OUT}/pattern-estandarte-slides.png")
print("ok slides")

# hoja de revisión
sheet = Image.new("RGB", (1500, 500), (245,245,245))
for i, n in enumerate(["pattern-rex.png", "pattern-cadena.png", "pattern-estandarte-slides.png"]):
    sheet.paste(Image.open(f"{OUT}/{n}").resize((500, 500)), (i*500, 0))
sheet.save(f"{OUT}/_patterns.jpg", quality=85)
print("done")
