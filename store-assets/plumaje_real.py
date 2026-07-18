#!/usr/bin/env python3
# Plumaje Real — Ojo del Pavo Real. Cápsula SRHOOD: pluma de pavo real dibujada
# barba a barba (rachis curvo, ojo iridiscente en anillos orgánicos, flecos de oro).
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

# ----- paleta joya
NOCHE   = (9, 14, 28)      # fondo nocturno
NAVY    = (17, 27, 52)
ZAFIRO  = (33, 66, 148)
ZAF_HI  = (72, 116, 198)
TEAL    = (14, 116, 118)
TEAL_HI = (32, 158, 152)
ESMER   = (22, 148, 100)
ESM_HI  = (66, 200, 138)
ORO     = (206, 166, 82)
ORO_HI  = (238, 206, 128)
BRONCE  = (150, 112, 54)
CREMA   = (243, 235, 216)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def F(p, s): return ImageFont.truetype(p, s)

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def ramp(t, stops):
    """t in [0,1] over list of colors -> smooth multi-stop gradient"""
    n = len(stops) - 1
    x = min(max(t, 0.0), 0.9999) * n
    i = int(x)
    return lerp(stops[i], stops[i + 1], x - i)

# ---------------------------------------------------------------- una pluma
def feather(h, seed=1, bright=1.0, wisp=1.0):
    """Renderiza una pluma vertical (base abajo, ojo arriba) en RGBA, 2x supersample."""
    rnd = random.Random(seed)
    S = 2
    Wf, Hf = int(h * 0.62) * S, h * S
    img = Image.new("RGBA", (Wf, Hf), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def B(c):  # aclara según 'bright'
        return tuple(min(255, int(v * bright)) for v in c)

    sway = rnd.uniform(-1, 1) * 0.06
    def rachis(t):  # t=0 base, 1 punta
        x = Wf / 2 + math.sin(t * math.pi) * sway * Wf + math.sin(t * 9 + seed) * Wf * 0.004
        y = Hf * (0.985 - t * 0.95)
        return x, y

    eye_t = 0.76
    ex, ey = rachis(eye_t)
    eye_r = Wf * 0.30

    barbs = ramp(0, [NAVY, TEAL, ESMER])  # placeholder
    grad = [B(NAVY), B(ZAFIRO), B(TEAL), B(ESMER), B(ESM_HI)]
    n_steps = 230
    for i in range(n_steps):
        t = 0.03 + 0.90 * i / n_steps
        bx, by = rachis(t)
        # envolvente de longitud: amplia en el centro, corta en base y punta
        env = math.sin(min(t / 0.85, 1.0) * math.pi) ** 0.7
        Lmax = Wf * 0.46 * env * wisp
        if Lmax < 3: continue
        col = ramp(t * 0.92 + rnd.uniform(-0.03, 0.03), grad)
        for side in (-1, 1):
            L = Lmax * rnd.uniform(0.55, 1.0)
            up = rnd.uniform(0.22, 0.42)          # curvatura hacia arriba
            pts = []
            for k in range(7):
                s = k / 6
                px = bx + side * L * s
                py = by - L * up * (s ** 1.6) + math.sin(s * 6 + i) * S * 1.2
                pts.append((px, py))
            wdt = max(1, int(S * (1.6 - t)))
            c = col if rnd.random() > 0.12 else B(TEAL_HI)
            d.line(pts, fill=c + (200,), width=wdt)
    # flecos dorados alrededor del disco del ojo
    for a in range(0, 360, 4):
        if 60 < a < 120: continue                  # hueco inferior (entra el raquis)
        rad = math.radians(a)
        r0 = eye_r * rnd.uniform(0.98, 1.04)
        r1 = r0 + eye_r * rnd.uniform(0.10, 0.30)
        x0, y0 = ex + math.cos(rad) * r0, ey + math.sin(rad) * r0
        x1, y1 = ex + math.cos(rad) * r1, ey + math.sin(rad) * r1
        d.line([x0, y0, x1, y1], fill=B(ORO) + (210,), width=S)

    # ---- ojo: anillos orgánicos
    def organic(cx, cy, r, squash=1.16, wob=0.05, ph=0.0):
        pts = []
        for a in range(0, 360, 3):
            rad = math.radians(a)
            rr = r * (1 + wob * math.sin(3 * rad + ph) + wob * 0.5 * math.sin(7 * rad + ph * 2))
            # muesca inferior donde entra el raquis
            gap = math.exp(-((a - 90) / 26) ** 2)
            rr *= (1 - 0.28 * gap)
            pts.append((cx + math.cos(rad) * rr, cy + math.sin(rad) * rr * squash))
        return pts
    ph = rnd.uniform(0, 6)
    d.polygon(organic(ex, ey, eye_r * 1.00, ph=ph),        fill=B(ORO))
    d.polygon(organic(ex, ey, eye_r * 0.93, ph=ph + .4),   fill=B(BRONCE))
    d.polygon(organic(ex, ey, eye_r * 0.84, ph=ph + .8),   fill=B(ESMER))
    d.polygon(organic(ex, ey, eye_r * 0.66, ph=ph + 1.2),  fill=B(TEAL))
    d.polygon(organic(ex, ey, eye_r * 0.47, ph=ph + 1.6),  fill=B(ZAFIRO))
    core = organic(ex, ey - eye_r * 0.06, eye_r * 0.30, squash=1.30, wob=0.04, ph=ph)
    d.polygon(core, fill=(8, 12, 26))
    # brillo del núcleo
    d.ellipse([ex - eye_r * 0.10, ey - eye_r * 0.26,
               ex + eye_r * 0.02, ey - eye_r * 0.12], fill=B(ZAF_HI))
    # raquis (tronco) — de la base hasta el ojo
    spine = [rachis(t) for t in [x / 40 for x in range(0, int(eye_t * 40) + 1)]]
    d.line(spine, fill=B((222, 192, 118)) + (255,), width=3 * S)
    d.line(spine, fill=B(ORO_HI) + (255,), width=S)
    # penacho corto sobre el ojo
    for a in range(-64, 65, 7):
        rad = math.radians(a - 90)
        r0, r1 = eye_r * 1.02, eye_r * rnd.uniform(1.22, 1.5)
        x0, y0 = ex + math.cos(rad) * r0, ey + math.sin(rad) * r0 * 1.16
        x1, y1 = ex + math.cos(rad) * r1, ey + math.sin(rad) * r1 * 1.16
        d.line([x0, y0, x1, y1], fill=ramp(abs(a) / 70, [B(ESM_HI), B(TEAL)]) + (220,), width=S)
    return img.resize((Wf // S, Hf // S), Image.LANCZOS)

# ---------------------------------------------------------------- fondos
def night(size, speck=420, seed=5, base=NOCHE, low=None):
    W_, H_ = size
    low = low or tuple(max(0, c - 6) for c in base)
    top = tuple(min(255, c + 8) for c in base)
    img = Image.new("RGB", (1, H_))
    px = img.load()
    for y in range(H_):
        t = y / (H_ - 1)
        px[0, y] = lerp(top, low, t)
    img = img.resize((W_, H_))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(speck):
        x, y = rnd.randrange(W_), rnd.randrange(H_)
        r = rnd.choice([1, 1, 1, 2])
        c = rnd.choice([BRONCE, ORO, (60, 70, 100)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=lerp(c, base, rnd.uniform(0.3, 0.7)))
    return img

def grain(img, seed=7):
    noise = Image.effect_noise(img.size, 12).convert("L")
    return Image.blend(img.convert("RGB"), Image.merge("RGB", (noise,) * 3), 0.035)

def scatter_feathers(canvas, cell_w, cell_h, fh, seeds, seed=3, jitter=0.12, rot=10):
    """patrón media-caída (half-drop) de plumas superpuestas, filas de abajo arriba"""
    W_, H_ = canvas.size
    rnd = random.Random(seed)
    variants = [feather(fh, seed=s) for s in seeds]
    rows = []
    y = H_ + cell_h
    row_i = 0
    while y > -fh:
        rows.append((y, row_i)); y -= cell_h; row_i += 1
    for y, row_i in rows:                      # de abajo hacia arriba: solape tipo escama
        x0 = -cell_w if row_i % 2 else -cell_w // 2
        x = x0
        while x < W_ + cell_w:
            f = variants[rnd.randrange(len(variants))]
            ang = rnd.uniform(-rot, rot)
            fr = f.rotate(ang, expand=True, resample=Image.BICUBIC)
            px = int(x + rnd.uniform(-jitter, jitter) * cell_w - fr.width / 2)
            py = int(y - fr.height + rnd.uniform(-jitter, jitter) * cell_h)
            canvas.paste(fr, (px, py), fr)
            x += cell_w
    return canvas

# ---------------------------------------------------------------- 1. camiseta (frente, PNG transparente)
def tee():
    W_, H_ = 2400, 3200
    img = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    f = feather(2350, seed=11, bright=1.18, wisp=1.0)
    img.alpha_composite(f, ((W_ - f.width) // 2, 60))
    d = ImageDraw.Draw(img)
    # anillo fino dorado detrás del lockup
    d.rectangle([W_ * 0.20, 2560, W_ * 0.80, 2564], fill=ORO + (255,))
    f1 = F(SERIF_B, 128); f2 = F(SANS, 54)
    t1 = "PLUMAJE REAL"
    x = W_ / 2 - d.textlength(t1, font=f1) / 2 - 6 * (len(t1) - 1) / 2
    for ch in t1:
        d.text((x, 2620), ch, font=f1, fill=ORO_HI + (255,))
        x += d.textlength(ch, font=f1) + 6
    t2 = "STREET ROYALTY HOOD · MMXXVI"
    x = W_ / 2 - d.textlength(t2, font=f2) / 2 - 10 * (len(t2) - 1) / 2
    for ch in t2:
        d.text((x, 2790), ch, font=f2, fill=CREMA + (235,))
        x += d.textlength(ch, font=f2) + 10
    return img

# ---------------------------------------------------------------- 2. hoodie (frente, PNG transparente)
def hoodie():
    W_ = H_ = 1800
    img = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    cx, base_y = W_ / 2, H_ * 0.80
    # abanico de 5 plumas
    for ang, hh, s in [(-44, 1150, 21), (-22, 1300, 22), (0, 1400, 23), (22, 1300, 24), (44, 1150, 25)]:
        f = feather(hh, seed=s, bright=1.15, wisp=0.9)
        fr = f.rotate(-ang, expand=True, resample=Image.BICUBIC)
        # ancla: girar en torno a la base de la pluma
        rad = math.radians(ang)
        tipx = cx + math.sin(rad) * hh * 0.52
        tipy = base_y - math.cos(rad) * hh * 0.52
        img.alpha_composite(fr, (int(tipx - fr.width / 2), int(tipy - fr.height / 2)))
    d = ImageDraw.Draw(img)
    # corona en la base
    cw, chh = 300, 190
    cy = base_y + 10
    l, r = cx - cw / 2, cx + cw / 2
    pts = [(l, cy), (l, cy - chh * 0.62),
           (l + cw * 0.185, cy - chh * 0.28), (cx - cw * 0.155, cy - chh * 0.88),
           (cx, cy - chh * 0.34), (cx + cw * 0.155, cy - chh * 0.88),
           (r - cw * 0.185, cy - chh * 0.28), (r, cy - chh * 0.62), (r, cy)]
    d.polygon(pts, fill=ORO + (255,))
    d.rectangle([l, cy + 14, r, cy + 40], fill=ORO + (255,))
    for gx in (l, cx, r):
        d.ellipse([gx - 12, cy - chh * 0.95 - 12, gx + 12, cy - chh * 0.95 + 12], fill=ORO_HI + (255,))
    f2 = F(SANS_B, 56)
    t2 = "SRHOOD"
    x = cx - d.textlength(t2, font=f2) / 2 - 22 * 2.5
    for ch in t2:
        d.text((x, cy + 74), ch, font=f2, fill=CREMA + (240,))
        x += d.textlength(ch, font=f2) + 22
    return img

# ---------------------------------------------------------------- 3. high-tops hombre (AOP)
def hitops():
    img = night((2400, 2400), speck=700, seed=31)
    img = scatter_feathers(img.convert("RGB"), 560, 620, 780, seeds=[41, 42, 43, 44], seed=32, rot=14)
    return grain(img, 33)

# ---------------------------------------------------------------- 4. athletic mujer (AOP, más denso)
def athletic():
    img = night((1950, 3300), speck=800, seed=51)
    img = scatter_feathers(img.convert("RGB"), 430, 500, 620, seeds=[61, 62, 63], seed=52, rot=12)
    return grain(img, 53)

# ---------------------------------------------------------------- 5. calcetines (sublimación)
def socks():
    W_, H_ = 1400, 2400
    img = night((W_, H_), speck=260, seed=71)
    d = ImageDraw.Draw(img)
    # columnas de mini-ojos en media caída + rombos de oro
    f = feather(360, seed=72, bright=1.05, wisp=0.75)
    stepx, stepy = 340, 420
    rnd = random.Random(73)
    for row in range(-1, H_ // stepy + 2):
        off = stepx // 2 if row % 2 else 0
        for col in range(-1, W_ // stepx + 2):
            x = col * stepx + off; y = H_ - row * stepy
            fr = f.rotate(rnd.uniform(-8, 8), expand=True, resample=Image.BICUBIC)
            img.paste(fr, (int(x - fr.width / 2), int(y - fr.height)), fr)
    for row in range(0, H_ // stepy + 2):
        off = 0 if row % 2 else stepx // 2
        for col in range(0, W_ // stepx + 2):
            x = col * stepx + off - stepx // 2; y = H_ - row * stepy - stepy // 2
            s = 16
            d.polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)], outline=ORO, width=3)
    return grain(img, 74)

# ---------------------------------------------------------------- 6. bandana (AOP 4125×4125)
def bandana():
    W_ = H_ = 4125
    img = night((W_, H_), speck=1600, seed=91)
    d = ImageDraw.Draw(img)
    cx = cy = W_ / 2
    # marco doble + fila de mini-rombos
    for m, wd, c in [(150, 12, ORO), (205, 5, BRONCE), (330, 5, BRONCE)]:
        d.rectangle([m, m, W_ - m, H_ - m], outline=c, width=wd)
    rnd = random.Random(92)
    s = 26
    for k in range(240, W_ - 240, 88):     # rombos del marco
        for x, y in [(k, 268), (k, H_ - 268), (268, k), (W_ - 268, k)]:
            d.polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)], outline=ORO, width=4)
    # corona central
    def crown(cx_, cy_, cw, chh, col, hi):
        l, r = cx_ - cw / 2, cx_ + cw / 2
        pts = [(l, cy_), (l, cy_ - chh * 0.62),
               (l + cw * 0.185, cy_ - chh * 0.28), (cx_ - cw * 0.155, cy_ - chh * 0.88),
               (cx_, cy_ - chh * 0.34), (cx_ + cw * 0.155, cy_ - chh * 0.88),
               (r - cw * 0.185, cy_ - chh * 0.28), (r, cy_ - chh * 0.62), (r, cy_)]
        d.polygon(pts, fill=col)
        d.rectangle([l, cy_ + chh * 0.07, r, cy_ + chh * 0.20], fill=col)
        for gx in (l, cx_, r):
            rr = cw * 0.045
            d.ellipse([gx - rr, cy_ - chh * 0.95 - rr, gx + rr, cy_ - chh * 0.95 + rr], fill=hi)
    # rueda de 12 plumas
    fbig = feather(1050, seed=93, bright=1.05)
    for k in range(12):
        ang = k * 30
        fr = fbig.rotate(-ang + 180, expand=True, resample=Image.BICUBIC)
        rad = math.radians(ang - 90)
        px = cx + math.cos(rad) * 1000 - fr.width / 2
        py = cy + math.sin(rad) * 1000 - fr.height / 2
        img.paste(fr, (int(px), int(py)), fr)
    # medallón central
    for rr, c, wd in [(560, ORO, 10), (515, BRONCE, 5)]:
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=c, width=wd)
    d.ellipse([cx - 470, cy - 470, cx + 470, cy + 470], fill=lerp(NOCHE, NAVY, 0.5))
    crown(cx, cy + 110, 480, 330, ORO, ORO_HI)
    f2 = F(SANS_B, 92)
    t = "STREET ROYALTY HOOD"
    # texto circular en el medallón
    Rt = 380
    total = sum(d.textlength(c, font=f2) + 26 for c in t) - 26
    a0 = -math.pi / 2 - total / (2 * Rt)
    a = a0
    for ch in t:
        wch = d.textlength(ch, font=f2)
        am = a + (wch / 2) / Rt
        x = cx + math.cos(am) * Rt; y = cy + math.sin(am) * Rt
        chimg = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        cd = ImageDraw.Draw(chimg)
        cd.text((100, 100), ch, font=f2, fill=CREMA + (255,), anchor="mm")
        chimg = chimg.rotate(-math.degrees(am) - 90, resample=Image.BICUBIC, center=(100, 100))
        img.paste(chimg, (int(x - 100), int(y - 100)), chimg)
        a += (wch + 26) / Rt
    # plumas de esquina
    fsm = feather(620, seed=94, bright=1.0, wisp=0.8)
    for (ex, ey, ang) in [(560, 560, 135), (W_ - 560, 560, -135), (560, H_ - 560, 45), (W_ - 560, H_ - 560, -45)]:
        fr = fsm.rotate(ang, expand=True, resample=Image.BICUBIC)
        img.paste(fr, (int(ex - fr.width / 2), int(ey - fr.height / 2)), fr)
    return grain(img, 95)

if __name__ == "__main__":
    jobs = {
        "plu_tee_print":      (tee, "PNG"),
        "plu_hoodie_print":   (hoodie, "PNG"),
        "plu_hitops_print":   (hitops, "PNG"),
        "plu_athletic_print": (athletic, "PNG"),
        "plu_socks_print":    (socks, "PNG"),
        "plu_bandana_print":  (bandana, "PNG"),
    }
    for name, (fn, fmt) in jobs.items():
        im = fn()
        im.save(f"{OUT}/{name}.png")
        print("done", name, im.size)
