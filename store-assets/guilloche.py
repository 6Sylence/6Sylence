# Cápsula "Guilloché — Grabado Real" · SRHOOD
# Motor espirográfico de grabado de seguridad (estilo billete/pasaporte):
# rosetones hypotrochoides, cintas onduladas entrelazadas y ráfagas radiales,
# supermuestreado x2 para línea fina limpia. Salida: 6 archivos de impresión.
import math, os
from PIL import Image, ImageDraw, ImageFont

OUT = os.environ.get("GUI_OUT", "/tmp/claude-0/-home-user-6Sylence/17042625-32b4-5f73-a57d-c7b023d4ae8d/scratchpad/designs")
os.makedirs(OUT, exist_ok=True)

EMERALD = (14, 93, 69, 255)
DEEP    = (9, 58, 44, 255)
COPPER  = (186, 116, 48, 255)
IVORY   = (242, 237, 223, 255)
PAPER   = (243, 239, 228, 255)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

SS = 2  # supersample


def canvas(w, h, bg=(0, 0, 0, 0)):
    img = Image.new("RGBA", (w * SS, h * SS), bg)
    return img, ImageDraw.Draw(img)


def save(img, name, w, h):
    img = img.resize((w, h), Image.LANCZOS)
    img.save(os.path.join(OUT, name))
    print("saved", name, img.size)


def poly(draw, pts, color, width):
    draw.line(pts, fill=color, width=width, joint="curve")


def ring_band(draw, cx, cy, r0, amp, lobes, curves, color, width=2, steps=1200, twist=1.0):
    """Banda guilloché clásica: familia de curvas r(t)=r0+amp*sin(lobes*t+fase)."""
    for i in range(curves):
        ph = 2 * math.pi * i / curves
        pts = []
        for s in range(steps + 1):
            t = 2 * math.pi * s / steps
            r = r0 + amp * math.sin(lobes * t + ph * twist)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        poly(draw, pts, color, width)


def hypo_rosette(draw, cx, cy, radius_px, kR, kr, dfrac, color, width=2, steps_per_turn=900):
    """Rosetón hypotrochoide (espirógrafo) escalado a radius_px.
    kR/kr enteros definen los lóbulos; dfrac es d relativo al rodillo."""
    g = math.gcd(kR, kr)
    turns = kr // g
    rr = kr / kR
    d = dfrac * rr
    # radio máximo del trocoide unitario para escalar exacto
    rmax = (1 - rr) + d
    n = steps_per_turn * turns
    pts = []
    for s in range(n + 1):
        t = 2 * math.pi * turns * s / n
        x = (1 - rr) * math.cos(t) + d * math.cos((1 - rr) / rr * t)
        y = (1 - rr) * math.sin(t) - d * math.sin((1 - rr) / rr * t)
        pts.append((cx + x / rmax * radius_px, cy + y / rmax * radius_px))
    poly(draw, pts, color, width)


def radial_burst(draw, cx, cy, r1, r2, n, color, width=2, skip=1):
    for i in range(0, n, skip):
        a = 2 * math.pi * i / n
        draw.line([(cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
                   (cx + r2 * math.cos(a), cy + r2 * math.sin(a))], fill=color, width=width)


def dashed_ring(draw, cx, cy, r, n, color, width, frac=0.55):
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = a0 + 2 * math.pi * frac / n
        pts = [(cx + r * math.cos(a0 + (a1 - a0) * s / 8), cy + r * math.sin(a0 + (a1 - a0) * s / 8)) for s in range(9)]
        poly(draw, pts, color, width)


def circle(draw, cx, cy, r, color, width):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)


def wave_band(draw, x0, x1, y, amp, wl, curves, color, width=2, steps=900, envelope=None):
    """Cinta horizontal de ondas entrelazadas (dos familias en contrafase)."""
    for fam in (1, -1):
        for i in range(curves):
            ph = 2 * math.pi * i / curves
            pts = []
            for s in range(steps + 1):
                x = x0 + (x1 - x0) * s / steps
                e = envelope(x) if envelope else 1.0
                pts.append((x, y + fam * amp * e * math.sin(2 * math.pi * (x - x0) / wl + ph)))
            poly(draw, pts, color, width)


def crown(draw, cx, cy, w, color, width, layers=4):
    """Corona grabada: silueta en trazos concéntricos."""
    h = w * 0.72
    for k in range(layers):
        f = 1 - 0.09 * k
        W, H = w * f, h * f
        base_y = cy + H * 0.5
        pts = [(cx - W * 0.5, base_y - H * 0.28),
               (cx - W * 0.5, cy - H * 0.18),
               (cx - W * 0.28, base_y - H * 0.42),
               (cx - W * 0.17, cy - H * 0.5),
               (cx, base_y - H * 0.48),
               (cx + W * 0.17, cy - H * 0.5),
               (cx + W * 0.28, base_y - H * 0.42),
               (cx + W * 0.5, cy - H * 0.18),
               (cx + W * 0.5, base_y - H * 0.28),
               (cx - W * 0.5, base_y - H * 0.28)]
        poly(draw, pts, color, width)
        draw.line([(cx - W * 0.5, base_y - H * 0.2), (cx + W * 0.5, base_y - H * 0.2)], fill=color, width=width)
        draw.line([(cx - W * 0.5, base_y), (cx + W * 0.5, base_y)], fill=color, width=width)
    for dx in (-0.5, -0.17, 0.17, 0.5):
        circle(draw, cx + dx * w, cy - h * (0.5 if abs(dx) < 0.3 else 0.18) - w * 0.045, w * 0.045, color, width)


def spaced_text(draw, cx, y, text, font, color, spacing):
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=font, fill=color)
        x += w + spacing


def arc_text(img, cx, cy, r, text, font, color, a0, a1, bottom=False):
    """Texto sobre arco. Para arcos inferiores (bottom=True) los glifos se
    voltean hacia fuera para leerse de izquierda a derecha."""
    n = len(text)
    for i, ch in enumerate(text):
        a = math.radians(a0 + (a1 - a0) * (i / max(n - 1, 1)))
        tile = Image.new("RGBA", (220 * SS, 220 * SS), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        tw = td.textlength(ch, font=font)
        td.text(((220 * SS - tw) / 2, (140 * SS if bottom else 60 * SS)), ch, font=font, fill=color)
        deg = (-math.degrees(a) + 90) if bottom else (-math.degrees(a) - 90)
        tile = tile.rotate(deg, resample=Image.BICUBIC, expand=False)
        x = cx + r * math.cos(a) - 110 * SS
        y = cy + r * math.sin(a) - 110 * SS
        img.alpha_composite(tile, (int(x), int(y)))


def corner_rosette(draw, cx, cy, R, color, width):
    hypo_rosette(draw, cx, cy, R * 0.92, 7, 3, 0.85, color, width)
    circle(draw, cx, cy, R * 1.06, color, width)


# ----------------------------------------------------------------------------
# 1 · CAMISETA (blanca) — "Gran Rosetón" 2400x3200, fondo transparente
# ----------------------------------------------------------------------------
def tee():
    W, H = 2400, 3200
    img, d = canvas(W, H)
    cx, cy = W * SS // 2, int(H * SS * 0.44)
    u = W * SS / 2400.0

    # marco de billete con esquinas
    m, m2 = int(70 * u), int(96 * u)
    d.rectangle([m, m, W * SS - m, H * SS - m], outline=EMERALD, width=int(3 * u))
    d.rectangle([m2, m2, W * SS - m2, H * SS - m2], outline=EMERALD, width=int(1.6 * u))
    for gx in (int(230 * u), W * SS - int(230 * u)):
        for gy in (int(230 * u), H * SS - int(230 * u)):
            corner_rosette(d, gx, gy, int(84 * u), COPPER, int(2.4 * u))

    # gran rosetón central: tres bandas + hypotrochoides
    ring_band(d, cx, cy, int(760 * u), int(66 * u), 36, 14, EMERALD, int(2.6 * u))
    ring_band(d, cx, cy, int(620 * u), int(52 * u), 24, 12, EMERALD, int(2.6 * u), twist=-1)
    hypo_rosette(d, cx, cy, int(540 * u), 24, 11, 0.8, DEEP, int(2 * u))
    hypo_rosette(d, cx, cy, int(430 * u), 18, 7, 0.75, COPPER, int(1.8 * u))
    ring_band(d, cx, cy, int(300 * u), int(30 * u), 18, 9, EMERALD, int(2.4 * u))
    dashed_ring(d, cx, cy, int(852 * u), 120, EMERALD, int(2.2 * u))
    circle(d, cx, cy, int(886 * u), EMERALD, int(3 * u))
    circle(d, cx, cy, int(196 * u), DEEP, int(3 * u))
    radial_burst(d, cx, cy, int(206 * u), int(262 * u), 160, EMERALD, int(1.8 * u))
    crown(d, cx, cy - int(6 * u), int(212 * u), DEEP, int(4 * u))

    f_arc = ImageFont.truetype(SERIF_B, int(74 * SS * u / SS))
    arc_text(img, cx, cy, int(960 * u), "STREET ROYALTY", f_arc, DEEP, -152, -28)
    arc_text(img, cx, cy, int(960 * u), "GRABADO REAL", f_arc, DEEP, 152, 28, bottom=True)

    d = ImageDraw.Draw(img)
    f_big = ImageFont.truetype(SERIF_B, int(150 * u))
    f_sm = ImageFont.truetype(SERIF, int(54 * u))
    spaced_text(d, cx, int(H * SS * 0.795), "SRHOOD", f_big, EMERALD, int(46 * u))
    spaced_text(d, cx, int(H * SS * 0.86), "SERIE GUILLOCHÉ · MMXXVI", f_sm, COPPER, int(14 * u))
    wave_band(d, int(330 * u), W * SS - int(330 * u), int(H * SS * 0.925), int(26 * u), int(300 * u), 5, EMERALD, int(2 * u))
    save(img, "gui_tee_print.png", W, H)


# ----------------------------------------------------------------------------
# 2 · SUDADERA (negra) — "Cinta Grabada" 2400x3200, transparente, tinta marfil
# ----------------------------------------------------------------------------
def sweat():
    W, H = 2400, 3200
    img, d = canvas(W, H)
    u = W * SS / 2400.0
    cx = W * SS // 2

    f_big = ImageFont.truetype(SERIF_B, int(240 * u))
    f_sm = ImageFont.truetype(SERIF, int(58 * u))
    spaced_text(d, cx, int(120 * u), "SRHOOD", f_big, IVORY, int(60 * u))
    spaced_text(d, cx, int(430 * u), "— LA CORONA SE GRABA, NO SE IMPRIME —", f_sm, COPPER, int(10 * u))

    # cinta central: tres bandas de ondas entrelazadas con envolvente
    y0 = int(1250 * u)
    env = lambda x: 0.55 + 0.45 * math.sin(math.pi * (x - 300 * u) / (W * SS - 600 * u))
    wave_band(d, int(180 * u), W * SS - int(180 * u), y0 - int(330 * u), int(120 * u), int(560 * u), 9, IVORY, int(2.6 * u), envelope=env)
    wave_band(d, int(180 * u), W * SS - int(180 * u), y0, int(160 * u), int(430 * u), 12, IVORY, int(2.6 * u), envelope=env)
    wave_band(d, int(180 * u), W * SS - int(180 * u), y0 + int(330 * u), int(120 * u), int(560 * u), 9, COPPER, int(2.4 * u), envelope=env)
    for yy in (y0 - int(560 * u), y0 + int(560 * u)):
        d.line([(int(180 * u), yy), (W * SS - int(180 * u), yy)], fill=IVORY, width=int(3 * u))
        d.line([(int(180 * u), yy + (int(24 * u) if yy > y0 else -int(24 * u))), (W * SS - int(180 * u), yy + (int(24 * u) if yy > y0 else -int(24 * u)))], fill=IVORY, width=int(1.6 * u))

    # medallón pequeño sobre la cinta
    mcx, mcy = cx, y0
    circle(d, mcx, mcy, int(300 * u), IVORY, int(4 * u))
    d.ellipse([mcx - int(292 * u), mcy - int(292 * u), mcx + int(292 * u), mcy + int(292 * u)], fill=(12, 12, 12, 255))
    ring_band(d, mcx, mcy, int(238 * u), int(26 * u), 20, 8, IVORY, int(2.2 * u))
    hypo_rosette(d, mcx, mcy, int(200 * u), 12, 5, 0.7, COPPER, int(1.8 * u))
    crown(d, mcx, mcy, int(130 * u), IVORY, int(3.4 * u), layers=3)
    dashed_ring(d, mcx, mcy, int(272 * u), 72, COPPER, int(2 * u))

    f_num = ImageFont.truetype(SERIF_B, int(96 * u))
    spaced_text(d, cx, int(2050 * u), "SERIE GUILLOCHÉ", f_num, IVORY, int(26 * u))
    spaced_text(d, cx, int(2200 * u), "STREET ROYALTY · MMXXVI", ImageFont.truetype(SERIF, int(52 * u)), COPPER, int(12 * u))
    save(img, "gui_sweat_print.png", W, H)


# ----------------------------------------------------------------------------
# 3 · HOODIE PREMIUM (negro) — "Sello Real" 2250x2250, transparente
# ----------------------------------------------------------------------------
def hoodie():
    W, H = 2250, 2250
    img, d = canvas(W, H)
    u = W * SS / 2250.0
    cx, cy = W * SS // 2, int(H * SS * 0.46)

    # ráfaga radial de fondo
    radial_burst(d, cx, cy, int(560 * u), int(1020 * u), 240, (242, 237, 223, 150), int(1.6 * u), skip=2)
    circle(d, cx, cy, int(1020 * u), IVORY, int(3 * u))
    circle(d, cx, cy, int(548 * u), IVORY, int(3.4 * u))

    # sello central
    ring_band(d, cx, cy, int(460 * u), int(44 * u), 30, 11, IVORY, int(2.6 * u))
    hypo_rosette(d, cx, cy, int(390 * u), 20, 9, 0.78, COPPER, int(2 * u))
    ring_band(d, cx, cy, int(210 * u), int(22 * u), 14, 7, IVORY, int(2.2 * u))
    circle(d, cx, cy, int(140 * u), IVORY, int(3 * u))
    crown(d, cx, cy - int(4 * u), int(150 * u), IVORY, int(3.6 * u), layers=3)
    dashed_ring(d, cx, cy, int(512 * u), 96, COPPER, int(2.2 * u))

    f_arc = ImageFont.truetype(SERIF_B, int(64 * u))
    arc_text(img, cx, cy, int(600 * u), "STREET ROYALTY HOOD", f_arc, IVORY, -160, -20)
    arc_text(img, cx, cy, int(600 * u), "GRABADO REAL", f_arc, IVORY, 160, 20, bottom=True)
    d = ImageDraw.Draw(img)
    spaced_text(d, cx, int(H * SS * 0.885), "EST. MMXXVI", ImageFont.truetype(SERIF, int(50 * u)), COPPER, int(16 * u))
    save(img, "gui_hoodie_print.png", W, H)


# ----------------------------------------------------------------------------
# 4 · ZAPATILLAS ALTAS (513) — retícula tejida 2400x2400, fondo marfil opaco
# ----------------------------------------------------------------------------
def hitops():
    W, H = 2400, 2400
    img, d = canvas(W, H, PAPER)
    u = W * SS / 2400.0
    # retícula de seguridad: dos familias de ondas horizontales finas + rosetones dispersos
    wl, amp, gap = int(340 * u), int(44 * u), int(84 * u)
    y = -amp
    row = 0
    while y < H * SS + amp:
        for fam in (1, -1):
            pts = []
            for s in range(0, W * SS + 20, 12):
                pts.append((s, y + fam * amp * math.sin(2 * math.pi * s / wl + row * 0.9)))
            poly(d, pts, EMERALD if fam == 1 else DEEP, int(2.2 * u))
        y += gap
        row += 1
    # hilos verticales sutiles
    x = 0
    while x < W * SS:
        pts = [(x + int(20 * u) * math.sin(2 * math.pi * yy / (500 * u)), yy) for yy in range(0, H * SS + 20, 16)]
        poly(d, pts, (14, 93, 69, 70), int(1.6 * u))
        x += int(200 * u)
    # rosetones cobre en cuadrícula suelta
    for i in range(3):
        for j in range(3):
            rx = int((400 + i * 800) * u), int((400 + j * 800) * u)
            corner_rosette(d, rx[0], rx[1], int(96 * u), COPPER, int(2.2 * u))
    save(img, "gui_hitops_print.png", W, H)


# ----------------------------------------------------------------------------
# 5 · DEPORTIVAS MUJER (658) — corriente vertical 1950x3300, marfil opaco
# ----------------------------------------------------------------------------
def athletic():
    W, H = 1950, 3300
    img, d = canvas(W, H, PAPER)
    u = W * SS / 1950.0
    # trenza vertical de guilloché: tres columnas de husos entrelazados
    for ci, colx in enumerate((0.22, 0.5, 0.78)):
        cx = int(W * SS * colx)
        amp = int((250 if ci == 1 else 170) * u)
        wl = int((1100 if ci == 1 else 800) * u)
        col_a = EMERALD if ci == 1 else DEEP
        for fam in (1, -1):
            for i in range(8):
                ph = 2 * math.pi * i / 8
                pts = []
                for s in range(0, H * SS + 20, 14):
                    x = cx + fam * amp * math.sin(2 * math.pi * s / wl + ph)
                    pts.append((x, s))
                poly(d, pts, col_a, int(2.2 * u))
    # hilos horizontales sutiles de fondo
    for yy in range(0, H * SS, int(150 * u)):
        d.line([(0, yy), (W * SS, yy)], fill=(14, 93, 69, 45), width=int(1.4 * u))
    # rosetones cobre en los cruces de la columna central
    for k in range(3):
        cy = int((550 + k * 1100) * u)
        corner_rosette(d, W * SS // 2, cy, int(130 * u), COPPER, int(2.4 * u))
    save(img, "gui_athletic_print.png", W, H)


# ----------------------------------------------------------------------------
# 6 · RIÑONERA (350) — 2850x1050, esmeralda profundo opaco, grabado marfil
# ----------------------------------------------------------------------------
def fanny():
    W, H = 2850, 1050
    img, d = canvas(W, H, (9, 58, 44, 255))
    u = H * SS / 1050.0
    # banda central de ondas marfil + filas de rosetones
    wave_band(d, 0, W * SS, H * SS // 2, int(150 * u), int(520 * u), 10, IVORY, int(2.4 * u))
    wave_band(d, 0, W * SS, H * SS // 2, int(220 * u), int(760 * u), 6, COPPER, int(2 * u))
    for k in range(5):
        cx = int((285 + k * 570) * W * SS / 2850.0 / 1)
        corner_rosette(d, cx, H * SS // 2, int(120 * u), IVORY, int(2.4 * u))
    # cenefas superior e inferior
    for yy, sign in ((int(90 * u), 1), (H * SS - int(90 * u), -1)):
        d.line([(0, yy), (W * SS, yy)], fill=IVORY, width=int(3 * u))
        pts = [(x, yy + sign * int(28 * u) * abs(math.sin(2 * math.pi * x / (170 * u)))) for x in range(0, W * SS + 10, 10)]
        poly(d, pts, COPPER, int(2 * u))
    f = ImageFont.truetype(SERIF_B, int(66 * u))
    spaced_text(d, W * SS // 2, H * SS - int(230 * u), "STREET ROYALTY · SERIE GUILLOCHÉ", f, IVORY, int(14 * u))
    save(img, "gui_fanny_print.png", W, H)


if __name__ == "__main__":
    tee(); sweat(); hoodie(); hitops(); athletic(); fanny()
