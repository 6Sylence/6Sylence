# -*- coding: utf-8 -*-
# SRHOOD — archivos de impresión DTG 3600x4800 (12"x16" @300dpi), PNG transparente
import math, os
from PIL import Image, ImageDraw, ImageFont

W, H = 3600, 4800
OUT = os.path.dirname(os.path.abspath(__file__)) + "/prints"
os.makedirs(OUT, exist_ok=True)

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
        r = w * 0.035
        d.ellipse([x-r, y-r, x+r, y+r], fill=color)

def arc_text(d, text, cx, cy, radius, font, color, a0, a1, flip=False):
    n = len(text)
    for i, ch in enumerate(text):
        a = math.radians(a0 + (a1 - a0) * (i + 0.5) / n)
        x = cx + radius * math.cos(a)
        y = cy + radius * math.sin(a)
        rot = math.degrees(a) + (90 if not flip else -90)
        img = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
        dd = ImageDraw.Draw(img)
        dd.text((150, 150), ch, font=font, fill=color, anchor="mm")
        img = img.rotate(-rot, resample=Image.BICUBIC, center=(150, 150))
        base.alpha_composite(img, (int(x-150), int(y-150)))

def leon(main, accent, fname):
    global base
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    cx, cy = W//2, 2350
    R1, R2 = 1050, 780
    pts = []
    for i in range(28):
        a = math.pi*2*i/28 - math.pi/2
        r = R1 if i % 2 == 0 else R2
        pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    d.polygon(pts, fill=main)
    d.ellipse([cx-640, cy-640, cx+640, cy+640], outline=accent, width=36)
    d.ellipse([cx-590, cy-590, cx+590, cy+590], fill=main)
    for sx in (-1, 1):  # orejas
        d.ellipse([cx+sx*590-130, cy-760, cx+sx*590+130, cy-500], fill=main, outline=accent, width=24)
    for sx in (-1, 1):  # ojos
        d.ellipse([cx+sx*260-110, cy-260, cx+sx*260+110, cy-60], fill=accent)
        d.ellipse([cx+sx*260-45, cy-200, cx+sx*260+45, cy-110], fill=main)
    d.polygon([(cx-140, cy+90), (cx+140, cy+90), (cx, cy+280)], fill=accent)  # hocico
    d.line([(cx, cy+280), (cx, cy+420)], fill=accent, width=30)
    d.arc([cx-200, cy+300, cx, cy+520], 0, 100, fill=accent, width=30)
    d.arc([cx, cy+300, cx+200, cy+520], 80, 180, fill=accent, width=30)
    for sx in (-1, 1):
        for dy in (-40, 40, 120):
            d.line([(cx+sx*220, cy+300+dy), (cx+sx*520, cy+250+dy)], fill=accent, width=22)
    crown(d, cx, cy - 1420, 640, accent, 52)
    f = ImageFont.truetype(FB, 190)
    d.text((cx, cy + 1450), "R E X   D E L   B A R R I O", font=f, fill=main, anchor="mm")
    d.line([(cx-900, cy+1600), (cx+900, cy+1600)], fill=accent, width=16)
    f2 = ImageFont.truetype(FB, 110)
    d.text((cx, cy + 1750), "S T R E E T   R O Y A L T Y   H O O D", font=f2, fill=main, anchor="mm")
    base.save(f"{OUT}/{fname}")
    print("ok", fname)

def estandarte(fname):
    global base
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    cx = W//2
    bw, bh, by = 1700, 2600, 1000
    pts = [(cx-bw/2, by), (cx+bw/2, by), (cx+bw/2, by+bh), (cx, by+bh-420), (cx-bw/2, by+bh)]
    d.polygon(pts, fill=BURDEOS)
    d.polygon(pts, outline=ORO, width=44)
    inner = [(cx-bw/2+90, by+90), (cx+bw/2-90, by+90), (cx+bw/2-90, by+bh-160),
             (cx, by+bh-540), (cx-bw/2+90, by+bh-160)]
    d.polygon(inner, outline=CREMA, width=18)
    d.line([(cx-bw/2-160, by-70), (cx+bw/2+160, by-70)], fill=ORO, width=70)
    for sx in (-1, 1):
        d.ellipse([cx+sx*(bw/2+160)-70, by-140, cx+sx*(bw/2+160)+70, by], fill=ORO)
        d.line([(cx+sx*(bw/2-40), by-70), (cx+sx*(bw/2+40), by+140)], fill=ORO, width=26)
    crown(d, cx, by+700, 760, ORO, 60)
    f = ImageFont.truetype(FB, 420)
    d.text((cx, by+1400), "SRH", font=f, fill=CREMA, anchor="mm")
    d.line([(cx-420, by+1700), (cx+420, by+1700)], fill=ORO, width=24)
    f2 = ImageFont.truetype(FB, 120)
    d.text((cx, by+1880), "EST. MMXXVI", font=f2, fill=ORO, anchor="mm")
    f3 = ImageFont.truetype(FB, 150)
    d.text((cx, by+2900), "S T R E E T   R O Y A L T Y   H O O D", font=f3, fill=CREMA, anchor="mm")
    base.save(f"{OUT}/{fname}")
    print("ok", fname)

def cadena(fname):
    global base
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    cx, cy = W//2, 2400
    f = ImageFont.truetype(FB, 200)
    arc_text(d, "STREET ROYALTY", cx, cy, 1250, f, NAVY, 195, 345)
    arc_text(d, "HOOD · MMXXVI", cx, cy, 1250, f, NAVY, 150, 30, flip=True)
    # tres eslabones entrelazados
    for i, sx in enumerate((-1, 0, 1)):
        col = ORO if i % 2 == 0 else NAVY
        d.ellipse([cx+sx*560-420, cy-300, cx+sx*560+420, cy+300], outline=col, width=90)
    crown(d, cx, cy - 780, 520, ORO, 46)
    f2 = ImageFont.truetype(FB, 108)
    d.text((cx, cy + 560), "LOS ESLABONES NO SE ROMPEN", font=f2, fill=NAVY, anchor="mm")
    base.save(f"{OUT}/{fname}")
    print("ok", fname)

leon(ORO, CREMA, "print-leon-black.png")       # para prendas negras
leon(BURDEOS, ORO, "print-leon-white.png")     # para prendas blancas
estandarte("print-estandarte.png")             # hoodie negro
cadena("print-cadena.png")                     # sudadera sport grey

# previews sobre fondo para revisión
for f, bg in [("print-leon-black.png", (25,25,28)), ("print-leon-white.png", (245,245,242)),
              ("print-estandarte.png", (25,25,28)), ("print-cadena.png", (200,200,198))]:
    im = Image.open(f"{OUT}/{f}")
    prev = Image.new("RGB", (900, 1200), bg)
    prev.paste(im.resize((900, 1200)), (0, 0), im.resize((900, 1200)))
    prev.save(f"{OUT}/prev-{f.replace('.png','.jpg')}", quality=85)
sheet = Image.new("RGB", (1800, 2400), (240,240,240))
for i, f in enumerate(["prev-print-leon-black.jpg","prev-print-leon-white.jpg","prev-print-estandarte.jpg","prev-print-cadena.jpg"]):
    sheet.paste(Image.open(f"{OUT}/{f}").resize((900,1200)), ((i%2)*900, (i//2)*1200))
sheet.save(f"{OUT}/_contact.jpg", quality=85)
print("done")
