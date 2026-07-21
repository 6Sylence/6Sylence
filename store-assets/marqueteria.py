#!/usr/bin/env python3
# Cápsula Marquetería — Intarsia Real (SRHOOD)
# Genera: emblema de marquetería (para prendas negras, DTG frontal) + tile AOP sin costura.
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

# --- paleta madera + latón ---
EBANO    = (26, 20, 16)
NOGAL    = (107, 74, 47)
NOGAL_D  = (74, 50, 30)
ARCE     = (201, 166, 107)
ARCE_HI  = (224, 196, 146)
ROSEWOOD = (122, 59, 46)
ROSE_HI  = (150, 78, 60)
LATON    = (201, 164, 76)
LATON_HI = (233, 205, 128)
CREMA    = (240, 231, 210)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def F(p, s): return ImageFont.truetype(p, s)

def lerp(a, b, t): return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def wood_wedge(draw, pts, base, hi, grain_dir, seed):
    """Rellena un polígono con veta de madera direccional."""
    rnd = random.Random(seed)
    draw.polygon(pts, fill=base)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    # líneas de veta
    n = 26
    for i in range(n):
        t = i / n
        col = lerp(base, hi, 0.25 + 0.5*abs(math.sin(t*math.pi*2 + rnd.random())))
        if grain_dir == 'v':
            x = x0 + (x1-x0)*t + rnd.uniform(-4, 4)
            draw.line([(x, y0-6), (x+rnd.uniform(-6,6), y1+6)], fill=col, width=1)
        else:
            y = y0 + (y1-y0)*t + rnd.uniform(-4, 4)
            draw.line([(x0-6, y), (x1+6, y+rnd.uniform(-6,6))], fill=col, width=1)

def poly_clip(img_layer, mask_pts):
    m = Image.new("L", img_layer.size, 0)
    ImageDraw.Draw(m).polygon(mask_pts, fill=255)
    img_layer.putalpha(ImageChops.multiply(img_layer.split()[3], m))
    return img_layer

def star_medallion(size=1300, points=8):
    """Rosetón de marquetería: estrella de compás en cuñas de madera con filetes de latón."""
    S = size
    R = S*4  # supersample
    img = Image.new("RGBA", (R, R), (0,0,0,0))
    d = ImageDraw.Draw(img)
    cx = cy = R/2
    rout = R*0.475
    rin  = R*0.185
    woods = [(NOGAL,NOGAL_D,'v'), (ARCE,ARCE_HI,'h'), (ROSEWOOD,ROSE_HI,'v'), (NOGAL_D,NOGAL,'h')]
    # anillo exterior de latón
    d.ellipse([cx-rout-R*0.028, cy-rout-R*0.028, cx+rout+R*0.028, cy+rout+R*0.028], fill=LATON_HI)
    d.ellipse([cx-rout-R*0.014, cy-rout-R*0.014, cx+rout+R*0.014, cy+rout+R*0.014], fill=LATON)
    # cuñas de la estrella (2*points)
    seg = 2*points
    tip_r = rout
    val_r = rout*0.60
    for k in range(seg):
        a0 = (k/seg)*2*math.pi - math.pi/2
        a1 = ((k+1)/seg)*2*math.pi - math.pi/2
        amid = (a0+a1)/2
        r_edge = tip_r if k % 2 == 0 else tip_r*0.9
        tip = (cx + r_edge*math.cos(amid), cy + r_edge*math.sin(amid))
        p0  = (cx + val_r*math.cos(a0), cy + val_r*math.sin(a0))
        p1  = (cx + val_r*math.cos(a1), cy + val_r*math.sin(a1))
        w = woods[k % len(woods)]
        wood_wedge(d, [p0, tip, p1], w[0], w[1], w[2], seed=k*7+3)
        # filete de latón en los bordes de la cuña
        d.line([p0, tip], fill=LATON, width=max(2,int(R*0.0045)))
        d.line([tip, p1], fill=LATON, width=max(2,int(R*0.0045)))
    # anillo interior de latón
    d.ellipse([cx-val_r*1.02, cy-val_r*1.02, cx+val_r*1.02, cy+val_r*1.02], outline=LATON_HI, width=int(R*0.012))
    d.ellipse([cx-rin*1.28, cy-rin*1.28, cx+rin*1.28, cy+rin*1.28], fill=LATON)
    d.ellipse([cx-rin*1.20, cy-rin*1.20, cx+rin*1.20, cy+rin*1.20], fill=EBANO)
    # centro: pequeña estrella de rombos arce/nogal
    for k in range(points):
        a0 = (k/points)*2*math.pi - math.pi/2
        a1 = ((k+0.5)/points)*2*math.pi - math.pi/2
        a2 = ((k+1)/points)*2*math.pi - math.pi/2
        mid = (cx + rin*0.5*math.cos(a1), cy + rin*0.5*math.sin(a1))
        pa = (cx + rin*math.cos(a0), cy + rin*math.sin(a0))
        pc = (cx + rin*math.cos(a2), cy + rin*math.sin(a2))
        d.polygon([(cx,cy), pa, mid], fill=ARCE if k%2 else ARCE_HI)
        d.polygon([(cx,cy), mid, pc], fill=NOGAL if k%2 else NOGAL_D)
    d.ellipse([cx-R*0.03, cy-R*0.03, cx+R*0.03, cy+R*0.03], fill=LATON_HI)
    return img.resize((S, S), Image.LANCZOS)

def crown(w, h, col=LATON_HI, col2=LATON):
    S = 4
    img = Image.new("RGBA", (w*S, h*S), (0,0,0,0))
    d = ImageDraw.Draw(img)
    W, H = w*S, h*S
    pts = [(0,H), (0,H*0.32), (W*0.2,H*0.60), (W*0.32,H*0.14), (W*0.5,H*0.5),
           (W*0.68,H*0.14), (W*0.8,H*0.60), (W,H*0.32), (W,H)]
    d.polygon(pts, fill=col)
    d.rectangle([0, H*0.86, W, H], fill=col2)
    for px in (W*0.06, W*0.5, W*0.94):
        r = W*0.05
        d.ellipse([px-r, H*0.14-r, px+r, H*0.14+r], fill=col)
    return img.resize((w, h), Image.LANCZOS)

def text_tracked(draw, xy, text, font, fill, tracking, center=True):
    x, y = xy
    ws = [draw.textlength(c, font=font) for c in text]
    tot = sum(ws) + tracking*(len(text)-1)
    if center: x -= tot/2
    for c, cw in zip(text, ws):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking
    return tot

# ---------------- EMBLEMA (prendas negras, front DTG 1800x2400) ----------------
def emblem():
    W, H = 1800, 2400
    img = Image.new("RGBA", (W, H), (0,0,0,0))
    med = star_medallion(1180, points=8)
    mx, my = (W-med.width)//2, 470
    img.alpha_composite(med, (mx, my))
    d = ImageDraw.Draw(img)
    cr = crown(300, 190)
    img.alpha_composite(cr, ((W-cr.width)//2, my-150))
    # banner wordmark
    f1 = F(SERIF_B, 132)
    text_tracked(d, (W/2, my+med.height+40), "MARQUETERÍA", f1, CREMA, 14)
    f2 = F(SANS_B, 60)
    text_tracked(d, (W/2, my+med.height+205), "STREET ROYALTY · INTARSIA REAL", f2, LATON_HI, 16)
    # filetes decorativos
    d.line([(W*0.2, my+med.height+185), (W*0.8, my+med.height+185)], fill=LATON, width=4)
    return img

# ---------------- TILE AOP sin costura (marquetería parquet) ----------------
def aop_tile(size=2400):
    S = size
    R = S  # tile base
    img = Image.new("RGBA", (R, R), EBANO+(255,))
    d = ImageDraw.Draw(img)
    # parquet de rombos (cubos isométricos) en tres maderas -> efecto 3D
    step = R/6
    woods = [(ARCE,ARCE_HI,'h'), (NOGAL,NOGAL_D,'v'), (ROSEWOOD,ROSE_HI,'v')]
    h = step
    w = step*math.sqrt(3)/2
    rows = int(R/ h)+3
    cols = int(R/ w)+3
    for r in range(-1, rows):
        for c in range(-1, cols):
            cx = c*w
            cy = r*h + (h/2 if c%2 else 0)
            top = (cx, cy-h/2); bot=(cx, cy+h/2)
            left=(cx-w, cy); right=(cx+w, cy)
            # tres rombos que forman un cubo
            wood_wedge(d, [top,(cx,cy),right,(cx+w,cy-h/2)] if False else [top,right,(cx,cy),left], woods[0][0],woods[0][1],'h', seed=r*31+c)
    # rehacer con cubos limpios
    img = Image.new("RGBA", (R, R), EBANO+(255,))
    d = ImageDraw.Draw(img)
    a = step
    dx = a*math.sqrt(3)/2
    for r in range(-2, int(R/(a*1.5))+3):
        for c in range(-2, int(R/(2*dx))+3):
            ox = c*2*dx + (dx if r%2 else 0)
            oy = r*1.5*a
            cxp, cyp = ox, oy
            topv=(cxp, cyp-a)
            tl=(cxp-dx, cyp-a/2); tr=(cxp+dx, cyp-a/2)
            bl=(cxp-dx, cyp+a/2); br=(cxp+dx, cyp+a/2)
            botv=(cxp, cyp+a)
            # cara superior (rombo) arce, izquierda nogal, derecha rosewood -> cubo
            wood_wedge(d, [topv,tr,cxp and (cxp,cyp) or (cxp,cyp),tl], ARCE, ARCE_HI, 'h', seed=r*17+c*3)
            d.polygon([topv,tr,(cxp,cyp),tl], outline=LATON, width=2)
            wood_wedge(d, [tl,(cxp,cyp),botv,bl], NOGAL, NOGAL_D, 'v', seed=r*17+c*3+1)
            d.polygon([tl,(cxp,cyp),botv,bl], outline=LATON, width=2)
            wood_wedge(d, [(cxp,cyp),tr,br,botv], ROSEWOOD, ROSE_HI, 'v', seed=r*17+c*3+2)
            d.polygon([(cxp,cyp),tr,br,botv], outline=LATON, width=2)
    return img

# ---------------- EMBLEMA cuadrado (hoodie front DTG 1800x1800) ----------------
def emblem_square():
    W, H = 1800, 1800
    img = Image.new("RGBA", (W, H), (0,0,0,0))
    med = star_medallion(1150, points=8)
    my = 300
    img.alpha_composite(med, ((W-med.width)//2, my))
    d = ImageDraw.Draw(img)
    cr = crown(290, 185)
    img.alpha_composite(cr, ((W-cr.width)//2, my-150))
    f1 = F(SERIF_B, 116)
    text_tracked(d, (W/2, my+med.height+28), "MARQUETERÍA", f1, CREMA, 12)
    f2 = F(SANS_B, 52)
    text_tracked(d, (W/2, my+med.height+168), "STREET ROYALTY · INTARSIA REAL", f2, LATON_HI, 14)
    d.line([(W*0.22, my+med.height+152), (W*0.78, my+med.height+152)], fill=LATON, width=4)
    return img

if __name__ == "__main__":
    e = emblem(); e.save(f"{OUT}/marqueteria-emblem.png")
    print("emblem", e.size)
    es = emblem_square(); es.save(f"{OUT}/marqueteria-emblem-sq.png")
    print("emblem_sq", es.size)
    t = aop_tile(4125); t.convert("RGB").save(f"{OUT}/marqueteria-aop.jpg", quality=90)
    print("aop", t.size)
