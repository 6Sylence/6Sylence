#!/usr/bin/env python3
# Brand Covers — portadas de colección Street Royalty Hood (sistema negro + oro)
# Tres variantes de plantilla (rays / seal / band) sobre la misma identidad:
# corona SRH, marco deco doble, serif crema, tracking oro, grano sutil.
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "covers")
os.makedirs(OUT, exist_ok=True)

S = 1600  # square covers
NEGRO   = (12, 12, 14)
NEGRO_2 = (18, 18, 22)
CREMA   = (242, 234, 217)
ARENA   = (216, 198, 160)
ORO     = (201, 164, 76)
ORO_HI  = (232, 202, 122)
ORO_LO  = (150, 118, 56)
NAVY    = (23, 31, 51)
NAVY_HI = (34, 45, 74)
OLIVA   = (74, 78, 55)
OLIVA_HI= (104, 110, 78)
BURDEOS = (74, 22, 32)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def F(path, size): return ImageFont.truetype(path, size)

def grain(img):
    noise = Image.effect_noise(img.size, 10).convert("L")
    return Image.blend(img.convert("RGB"), Image.merge("RGB", (noise, noise, noise)), 0.045)

def vgrad(size, top, bottom):
    w, h = size
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((w, h))

def crown_path(cx, cy, w, h):
    l = cx - w / 2; r = cx + w / 2; b = cy + h / 2; t = cy - h / 2
    dipy = b - h * 0.42
    pts = [(l, b),
           (l, t + h * 0.30), (l + w * 0.185, dipy),
           (cx - w * 0.155, t + h * 0.12), (cx, dipy - h * 0.02),
           (cx + w * 0.155, t + h * 0.12), (r - w * 0.185, dipy),
           (r, t + h * 0.30), (r, b)]
    band = (l, b + h * 0.06, r, b + h * 0.16)
    return pts, band

def text_tracked(draw, xy, text, font, fill, tracking=0, anchor_center=False):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if anchor_center: x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking
    return total

def fit_serif(draw, text, max_w, start=150, minimum=70):
    size = start
    while size > minimum:
        f = F(SERIF_B, size)
        if draw.textlength(text, font=f) <= max_w: return f
        size -= 4
    return F(SERIF_B, minimum)

def circular_text(img, center, radius, text, font, fill, start_deg=-90, clockwise=True):
    cx, cy = center
    tmp = ImageDraw.Draw(img)
    arcs = []
    for c in text:
        w = max(tmp.textlength(c, font=font), font.size * 0.28)
        arcs.append(w / radius)
    total = sum(arcs)
    a = math.radians(start_deg) - (total / 2 if clockwise else -total / 2)
    for c, arc in zip(text, arcs):
        a_mid = a + (arc / 2 if clockwise else -arc / 2)
        x = cx + radius * math.cos(a_mid)
        y = cy + radius * math.sin(a_mid)
        size = int(font.size * 3)
        ch = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        cd = ImageDraw.Draw(ch)
        cd.text((size / 2, size / 2), c, font=font, fill=fill, anchor="mm")
        deg = math.degrees(a_mid) + (90 if clockwise else -90)
        ch = ch.rotate(-deg, resample=Image.BICUBIC, center=(size / 2, size / 2))
        img.paste(ch, (int(x - size / 2), int(y - size / 2)), ch)
        a += arc if clockwise else -arc

def frame(draw, accent, accent_lo):
    m = 64
    draw.rectangle([m, m, S - m, S - m], outline=accent, width=4)
    draw.rectangle([m + 16, m + 16, S - m - 16, S - m - 16], outline=accent_lo, width=2)
    for cxx in (m + 16, S - m - 16):
        for cyy in (m + 16, S - m - 16):
            draw.ellipse([cxx - 6, cyy - 6, cxx + 6, cyy + 6], fill=accent)

def footer_line(draw, accent):
    text_tracked(draw, (S / 2, S - 160), "STREET ROYALTY HOOD — MMXXVI", F(SANS, 26),
                 tuple(int(c * 0.72) for c in accent), tracking=9, anchor_center=True)

# ---------------------------------------------------------------- variante A: rays
def cover_rays(title, subtitle, bg=(NEGRO_2, NEGRO), accent=ORO, accent_hi=ORO_HI):
    img = vgrad((S, S), *bg)
    draw = ImageDraw.Draw(img)
    accent_lo = tuple(int(c * 0.72) for c in accent)
    cx, cy = S / 2, S * 0.40
    for i in range(-10, 11):
        a = math.radians(90 + i * 8.2)
        x2 = cx + math.cos(a) * S * 0.85
        y2 = cy - abs(math.sin(a)) * S * 0.85
        draw.line([cx, cy - 30, x2, y2], fill=(accent if i % 2 == 0 else accent_lo),
                  width=3 if i % 2 == 0 else 1)
    for rr, wd in [(S * 0.315, 4), (S * 0.345, 2), (S * 0.395, 1)]:
        draw.arc([cx - rr, cy - rr - 30, cx + rr, cy + rr - 30], 180, 360, fill=accent, width=wd)
    pts, band = crown_path(cx, cy - S * 0.045, S * 0.34, S * 0.155)
    draw.polygon(pts, fill=accent)
    draw.rectangle(band, fill=accent)
    for px_, py_ in [(cx - S * 0.17, cy - S * 0.045 - S * 0.155 * 0.20),
                     (cx, cy - S * 0.045 - S * 0.155 * 0.44),
                     (cx + S * 0.17, cy - S * 0.045 - S * 0.155 * 0.20)]:
        draw.ellipse([px_ - 10, py_ - 10, px_ + 10, py_ + 10], fill=accent_hi)
    for ww, yy in [(0.46, 0.505), (0.36, 0.525), (0.26, 0.545)]:
        draw.rectangle([cx - S * ww / 2, S * yy, cx + S * ww / 2, S * yy + 6], fill=accent)
    frame(draw, accent, accent_lo)
    f_big = fit_serif(draw, title, S * 0.78)
    draw.text((S / 2, S * 0.685), title, font=f_big, fill=CREMA, anchor="mm")
    text_tracked(draw, (S / 2, S * 0.775), subtitle, F(SANS, 34), accent_hi, tracking=13, anchor_center=True)
    footer_line(draw, accent)
    return grain(img)

# ---------------------------------------------------------------- variante B: seal
def cover_seal(title, subtitle, ring_text, bg=(NEGRO_2, NEGRO), accent=ORO, accent_hi=ORO_HI):
    img = vgrad((S, S), *bg)
    draw = ImageDraw.Draw(img)
    accent_lo = tuple(int(c * 0.72) for c in accent)
    cx, cy = S / 2, S * 0.40
    R = S * 0.27
    for rr, wd in [(R, 5), (R * 0.87, 2)]:
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=accent, width=wd)
    circular_text(img, (cx, cy), R * 0.94, ring_text, F(SANS_B, 40), accent_hi)
    pts, band = crown_path(cx, cy + S * 0.004, S * 0.21, S * 0.10)
    draw.line(pts + [pts[0]], fill=CREMA, width=7, joint="curve")
    draw.rectangle(band, outline=CREMA, width=7)
    for px_, py_ in [(cx - S * 0.105, cy - S * 0.044 + S * 0.024),
                     (cx, cy - S * 0.044),
                     (cx + S * 0.105, cy - S * 0.044 + S * 0.024)]:
        draw.ellipse([px_ - 8, py_ - 8, px_ + 8, py_ + 8], outline=CREMA, width=5)
    frame(draw, accent, accent_lo)
    f_big = fit_serif(draw, title, S * 0.78)
    draw.text((S / 2, S * 0.735), title, font=f_big, fill=CREMA, anchor="mm")
    text_tracked(draw, (S / 2, S * 0.82), subtitle, F(SANS, 34), accent_hi, tracking=13, anchor_center=True)
    footer_line(draw, accent)
    return grain(img)

# ---------------------------------------------------------------- variante C: band
def cover_band(title, subtitle, bg=(NEGRO_2, NEGRO), accent=ORO, accent_hi=ORO_HI, band_word="SRHOOD"):
    img = vgrad((S, S), *bg)
    draw = ImageDraw.Draw(img)
    accent_lo = tuple(int(c * 0.72) for c in accent)
    faint = tuple(int(bg[0][i] + (accent[i] - bg[0][i]) * 0.16) for i in range(3))
    f_band = F(SANS_B, 108)
    rows = 9
    y0 = S * 0.06
    dy = (S * 0.52) / rows
    for i in range(rows):
        y = y0 + i * dy
        x_off = -80 + (i % 3) * 46
        text_tracked(draw, (S / 2 + x_off, y), f"{band_word} · {band_word} · {band_word}",
                     f_band, faint, tracking=4, anchor_center=True)
    # central gold crown over the band
    cx, cy = S / 2, S * 0.36
    pts, band = crown_path(cx, cy, S * 0.26, S * 0.12)
    draw.polygon(pts, fill=accent)
    draw.rectangle(band, fill=accent)
    for px_, py_ in [(cx - S * 0.13, cy - S * 0.024),
                     (cx, cy - S * 0.053),
                     (cx + S * 0.13, cy - S * 0.024)]:
        draw.ellipse([px_ - 9, py_ - 9, px_ + 9, py_ + 9], fill=accent_hi)
    frame(draw, accent, accent_lo)
    draw.rectangle([S * 0.22, S * 0.60, S * 0.78, S * 0.604], fill=accent)
    f_big = fit_serif(draw, title, S * 0.78)
    draw.text((S / 2, S * 0.685), title, font=f_big, fill=CREMA, anchor="mm")
    text_tracked(draw, (S / 2, S * 0.775), subtitle, F(SANS, 34), accent_hi, tracking=13, anchor_center=True)
    footer_line(draw, accent)
    return grain(img)

COVERS = {
    # handle -> (builder, kwargs)
    "novedades":            (cover_rays, dict(title="NOVEDADES", subtitle="EL DROP VIGENTE")),
    "royalty-classics":     (cover_rays, dict(title="ROYALTY CLASSICS", subtitle="LA COLECCIÓN INSIGNIA")),
    "street-royalty-hombre":(cover_rays, dict(title="HOMBRE", subtitle="SELECCIÓN STREET ROYALTY")),
    "street-royalty-mujer": (cover_rays, dict(title="MUJER", subtitle="SELECCIÓN STREET ROYALTY",
                                              accent=ARENA, accent_hi=CREMA)),
    "bestsellers":          (cover_seal, dict(title="ESENCIALES", subtitle="LOS QUE NUNCA FALLAN",
                                              ring_text="ESENCIALES SRHOOD · EST. MMXXVI · ")),
    "completa-el-look":     (cover_seal, dict(title="COMPLETA EL LOOK", subtitle="DE LA CABEZA A LOS PIES",
                                              ring_text="COMPLETA EL LOOK · SRHOOD · ")),
    "deporte-gym-royalty":  (cover_seal, dict(title="DEPORTE & GYM", subtitle="DEL GYM A LA CALLE",
                                              bg=(NAVY_HI, NAVY),
                                              ring_text="DEPORTE & GYM ROYALTY · SRHOOD · ")),
    "eco-organico":         (cover_seal, dict(title="ECO & ORGÁNICO", subtitle="MENOS HUELLA, MISMA ESTÉTICA",
                                              bg=(OLIVA_HI, OLIVA), accent=CREMA, accent_hi=CREMA,
                                              ring_text="ECO & ORGÁNICO · SRHOOD · ")),
    "menos-de-40-entry-royalty": (cover_band, dict(title="MENOS DE 40 €", subtitle="ENTRY ROYALTY")),
    "nuevos-colores":       (cover_band, dict(title="NUEVOS COLORES", subtitle="EL COLOR TAMBIÉN ES ACTITUD",
                                              accent=BURDEOS and (122, 41, 55), accent_hi=(196, 120, 130))),
    "all-over-print-ediciones-unicas": (cover_band, dict(title="ALL-OVER PRINT", subtitle="EDICIONES ÚNICAS")),
    "drop-julio-2026-verano-royalty":  (cover_band, dict(title="VERANO ROYALTY", subtitle="DROP JULIO · MMXXVI",
                                              bg=(NAVY_HI, NAVY))),
    # ---- tanda 2 (2026-08-03, corrida 2): categorías con portada neón antigua o foto cruda
    "ropa-streetwear":      (cover_rays, dict(title="ROPA STREETWEAR", subtitle="EL ARMARIO COMPLETO")),
    "crown-capsule-street-royalty": (cover_rays, dict(title="CROWN CAPSULE", subtitle="LA CIMA DEL STREETWEAR")),
    "calzado-sneakers":     (cover_rays, dict(title="CALZADO", subtitle="SILUETAS LIMPIAS")),
    "accesorios-streetwear":(cover_seal, dict(title="ACCESORIOS", subtitle="EL DETALLE QUE FIRMA EL LOOK",
                                              ring_text="ACCESORIOS SRHOOD · EST. MMXXVI · ")),
    "gorras-gorros":        (cover_seal, dict(title="GORRAS & GORROS", subtitle="BORDADO DIRECTO",
                                              ring_text="GORRAS & GORROS · SRHOOD · ")),
    "bolsas-mochilas":      (cover_seal, dict(title="BOLSAS & MOCHILAS", subtitle="PARA EL DÍA A DÍA URBANO",
                                              ring_text="BOLSAS & MOCHILAS · SRHOOD · ")),
    "oversized-club":       (cover_seal, dict(title="OVERSIZED CLUB", subtitle="EL CORTE QUE DOMINA",
                                              ring_text="OVERSIZED CLUB · SRHOOD · ")),
    "chaquetas-abrigos":    (cover_seal, dict(title="CHAQUETAS", subtitle="SIN TEMPORADA",
                                              bg=(NAVY_HI, NAVY),
                                              ring_text="CHAQUETAS & ABRIGOS · SRHOOD · ")),
    "calzado-hombre":       (cover_seal, dict(title="CALZADO HOMBRE", subtitle="PISA FUERTE",
                                              ring_text="CALZADO HOMBRE · SRHOOD · ")),
    "calzado-mujer":        (cover_seal, dict(title="CALZADO MUJER", subtitle="COMBINA CON TODO",
                                              accent=ARENA, accent_hi=CREMA,
                                              ring_text="CALZADO MUJER · SRHOOD · ")),
    "camisetas":            (cover_band, dict(title="CAMISETAS", subtitle="LA BASE DE TODO LOOK")),
    "sudaderas-hoodies":    (cover_band, dict(title="SUDADERAS & HOODIES", subtitle="GRAMAJE ALTO, ACABADO PREMIUM")),
    "pantalones-joggers":   (cover_band, dict(title="PANTALONES & JOGGERS", subtitle="FELPA FRANCESA PREMIUM")),
    "bikinis-verano-royalty":(cover_band, dict(title="BIKINIS", subtitle="VERANO ROYALTY",
                                              bg=(NAVY_HI, NAVY))),
    "banadores-hombre-verano-royalty": (cover_band, dict(title="BAÑADORES", subtitle="VERANO ROYALTY · HOMBRE",
                                              bg=(NAVY_HI, NAVY))),
    "zapatillas-altas":     (cover_band, dict(title="ZAPATILLAS ALTAS", subtitle="CAÑA ALTA CLÁSICA")),
    "zapatillas-bajas-slip-on": (cover_band, dict(title="BAJAS & SLIP-ON", subtitle="ZAPATILLAS STREET ROYALTY")),
    "zapatillas-deportivas":(cover_band, dict(title="DEPORTIVAS", subtitle="PARA ENTRENAR O PARA LA CALLE")),
    "slides-chanclas":      (cover_band, dict(title="SLIDES & CHANCLAS", subtitle="VERANO ROYALTY",
                                              bg=(NAVY_HI, NAVY))),
}

if __name__ == "__main__":
    for handle, (fn, kw) in COVERS.items():
        img = fn(**kw)
        path = f"{OUT}/brand-cover-{handle}.jpg"
        img.save(path, quality=90)
        print("done", path)
