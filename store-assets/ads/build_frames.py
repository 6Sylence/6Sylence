#!/usr/bin/env python3
"""
Heráldica Mineral — SRHOOD · secuencia de tres planchas para Instagram Stories.

Retícula común a las tres: cabecera 300/352/396, pie 1576/1612/1648. Todo el
contenido crítico vive entre y=268 y y=1652 (zonas seguras de Stories).
"""
from PIL import Image, ImageDraw, ImageFilter
from srhood_stories import *   # noqa

asegurar_fuentes()

CUT = {"brocado_shoe": 64, "malaquita_hoodie": 100, "cifra_hoodie": 100}


def sujeto(name):
    return cutout(f"{PROD}/{name}.jpg", lmin=CUT[name])


# ── elementos comunes del sistema ─────────────────────────────────────────────
def cabecera(img, d):
    img.alpha_composite(tint(crown_mask((W, H), 540, 300, 54, 34, lw=1.7), ORO_HI, 0.95))
    track(d, (540, 352), "STREET ROYALTY HOOD", F(JURA_L, 23), CREMA_DIM + (255,), 11.5, "ct")
    rule(d, 396, 118, ORO, 105)


def pie(img, d, sub="SERIES LIMITADAS · HECHO BAJO DEMANDA"):
    rule(d, 1576, 420, ORO, 62)
    track(d, (540, 1612), "SRHOOD.COM", F(BIGSH_B, 52), CREMA + (255,), 13, "cm")
    track(d, (540, 1648), sub, F(GEIST, 17), ORO_HI + (215,), 4.0, "cm")


def aparato(img, d, ref, ejes):
    """Marcas de registro, referencias al margen: la plancha se declara plancha."""
    registration(d)
    edge_ticks(d, ejes)
    vlabel(img, (MARGIN - 30, 700), ref, F(GEIST, 15), CREMA_MUTE + (190,), 3.0, "l")
    vlabel(img, (W - MARGIN + 12, 736), "40.4168° N — 3.7038° W", F(GEIST, 15),
           CREMA_MUTE + (190,), 3.0, "r")


DISPLAY = 134                # cuerpo único del titular en toda la serie


def bloque_texto(d, display, linea_oro, linea_gris, precio):
    f, tr = fit_display(d, display, ITALIANA, DISPLAY, 9)
    track(d, (540, 1296), display, f, CREMA + (255,), tr, "cm")
    rule(d, 1374, 300, ORO, 80)
    track(d, (540, 1408), linea_oro, F(GEIST, 19), ORO_HI + (232,), 4.6, "cm")
    track(d, (540, 1444), linea_gris, F(GEIST, 17), CREMA_MUTE + (255,), 4.2, "cm")
    price_tag(d, 540, 1508, precio, size=76)


# ═══════════════════════════════════════════════ PLANCHA I — SEDA REAL ════════
def plancha_1():
    img = field((16, 19, 19), (6, 7, 9), glow=(540, 850, 560, ESM_HI, 0.40)).convert("RGBA")
    CX, CY = 540, 862

    img.alpha_composite(tint(guilloche_mask((W, H), CX, CY, [
        dict(a=5, b=1.041, h=1.00, turns=58, steps=17000, R=398, lw=0.8)]), ORO, 0.58))
    img.alpha_composite(tint(guilloche_mask((W, H), CX, CY, [
        dict(a=7, b=1.017, h=0.92, turns=40, steps=12000, R=292, lw=0.7, rot=11)]), ORO_HI, 0.34))
    img.alpha_composite(tint(guilloche_mask((W, H), CX, CY, [
        dict(a=3, b=1.063, h=1.04, turns=30, steps=9000, R=466, lw=0.65, rot=23)]), ORO, 0.20))

    img.alpha_composite(tint(ring_mask((W, H), CX, CY, [(466, 1.0, 255)]), ORO, 0.46))
    img.alpha_composite(tint(ring_mask((W, H), CX, CY, [(458, 1.0, 255)]), ORO, 0.18))
    img.alpha_composite(tint(ring_mask((W, H), CX, CY, [(192, 1.0, 255)]), ORO_HI, 0.24))

    place(img, sujeto("brocado_shoe"), CX, CY + 30, target_w=706,
          halo=(44, 0.34, ESM_HI), shadow=(36, 0.50, 30))

    d = ImageDraw.Draw(img)
    cabecera(img, d)
    bloque_texto(d, "SEDA REAL",
                 "CÁPSULA BROCADO · ORO SOBRE ESMERALDA",
                 "ZAPATILLA ALTA · SERIE LIMITADA", "74,95")
    pie(img, d)
    aparato(img, d, "REF. SR—BRC / PL. I", [CY - 466, CY, CY + 466])
    return grain(img, seed=5)


# ══════════════════════════════════════════ PLANCHA II — PIEDRA REAL ══════════
def plancha_2():
    img = field((15, 19, 18), (6, 7, 9), glow=(540, 790, 470, ESM_HI, 0.40)).convert("RGBA")
    CX = 540
    EM = 748                                   # centro del medallón sobre el pecho

    # roseta ceñida al medallón: lo enmarca como un sello, sin invadir cabecera
    img.alpha_composite(tint(guilloche_mask((W, H), CX, EM, [
        dict(a=5, b=1.037, h=1.00, turns=56, steps=16000, R=318, lw=0.8, rot=7)]), ORO, 0.54))
    img.alpha_composite(tint(ring_mask((W, H), CX, EM, [(346, 1.0, 255)]), ORO, 0.44))
    img.alpha_composite(tint(ring_mask((W, H), CX, EM, [(338, 1.0, 255)]), ORO, 0.17))

    place(img, sujeto("malaquita_hoodie"), CX, 860, target_h=660,
          halo=(46, 0.50, ESM_HI), shadow=(38, 0.42, 24))

    d = ImageDraw.Draw(img)
    cabecera(img, d)
    bloque_texto(d, "PIEDRA REAL",
                 "CÁPSULA MALAQUITA · ESMERALDA Y ORO",
                 "SUDADERA CAPUCHA PREMIUM · UNISEX", "49,95")
    pie(img, d)
    aparato(img, d, "REF. SR—MLQ / PL. II", [EM - 346, EM, EM + 346])
    return grain(img, seed=13)


# ═══════════════════════════════════════════ PLANCHA III — EL SELLO ═══════════
def plancha_3():
    img = field((14, 17, 17), (6, 7, 9), glow=(540, 716, 520, ESM_HI, 0.30)).convert("RGBA")
    CX, CY = 540, 716

    # una sola familia de curvas: el sello respira, no se empasta
    img.alpha_composite(tint(guilloche_mask((W, H), CX, CY, [
        dict(a=6, b=1.031, h=0.98, turns=34, steps=11000, R=306, lw=0.8)]), ORO, 0.52))
    img.alpha_composite(tint(ring_mask((W, H), CX, CY, [(330, 1.0, 255)]), ORO, 0.46))
    img.alpha_composite(tint(ring_mask((W, H), CX, CY, [(322, 1.0, 255)]), ORO, 0.18))

    # la corona, maciza: el sello de la casa
    img.alpha_composite(tint(crown_mask((W, H), CX, CY - 20, 212, 132, filled=True), ORO_HI, 0.97))

    d = ImageDraw.Draw(img)
    cabecera(img, d)

    # declaración
    for ln, yy in [("LA CORONA", 1152), ("NO SE PIDE", 1268)]:
        f, tr = fit_display(d, ln, ITALIANA, DISPLAY, 8)
        track(d, (540, yy), ln, f, CREMA + (255,), tr, "cm")
    rule(d, 1346, 176, ORO, 95)
    track(d, (540, 1384), "S E   L L E V A", F(JURA_M, 26), ORO_HI + (240,), 9, "cm")

    # cédula de condiciones
    x0, x1, y0, y1 = 176, 904, 1436, 1540
    d.rectangle([x0, y0, x1, y1], outline=ORO + (78,), width=1)
    for cx_, cy_ in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
        d.ellipse([cx_ - 2, cy_ - 2, cx_ + 2, cy_ + 2], fill=ORO_HI + (200,))
    d.line([540, y0 + 16, 540, y1 - 16], fill=ORO + (52,), width=1)
    track(d, (358, 1472), "BIENVENIDA15", F(BIGSH_B, 40), CREMA + (255,), 5, "cm")
    track(d, (358, 1508), "15% EN TU PRIMERA COMPRA", F(GEIST, 15), CREMA_MUTE + (255,), 3.4, "cm")
    track(d, (722, 1472), "SERIES LIMITADAS", F(BIGSH_B, 40), CREMA + (255,), 5, "cm")
    track(d, (722, 1508), "HECHO BAJO DEMANDA", F(GEIST, 15), CREMA_MUTE + (255,), 3.4, "cm")

    pie(img, d)
    aparato(img, d, "REF. SR—SLL / PL. III", [CY - 330, CY, CY + 330])
    return grain(img, seed=29)


if __name__ == "__main__":
    for i, fn in enumerate([plancha_1, plancha_2, plancha_3], 1):
        p = f"{OUT}/srhood-story-{i:02d}.png"
        fn().save(p)
        print("→", p)
