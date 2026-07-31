#!/usr/bin/env python3
"""
Heráldica Mineral — SRHOOD · generador de lotes de feed (1080×1350, 4:5).

`build_feed.py` llevaba las diez planchas del lote 1 escritas a mano en una tabla.
A cien piezas eso deja de funcionar, así que aquí todo lo que se puede medir se
mide y solo se escribe lo que hay que decidir:

  · el **acento** sale del color dominante de la propia foto (`seleccionar.acento`);
  · el **recorte** usa el umbral que el QA del catálogo encontró para esa foto;
  · el **tamaño** en la vitrina depende del corte de la prenda, no del tipo de
    Shopify — unas slip-on no ocupan lo mismo que unas altas;
  · la **roseta** de guilloché varía con el índice, para que cien planchas no
    lleven el mismo grabado detrás.

Lo que no cambia nunca: la corona, el oro, la retícula y la tipografía. Es lo que
hace que la cuadrícula del perfil se lea como una sola casa.
"""
import json, os, argparse
from PIL import ImageDraw
import srhood_stories as S
from srhood_stories import *   # noqa
import textos as T

S.set_canvas(1080, 1350)
S.MARGIN = 60
W, H, MARGIN = 1080, 1350, 60

DISPLAY = 104
CY = 600
R_OUT, R_ROSE = 332, 308

# Caja máxima (ancho, alto) por corte de prenda. Se encaja por el lado que primero
# toque, nunca por uno solo: un mockup cenital de deportivas es casi cuadrado, y
# escalarlo solo por ancho lo saca de la vitrina y lo estampa contra el titular.
CAJA_PRENDA = [
    ("Zapatillas altas", (620, 600)), ("Zapatillas slip-on", (610, 580)),
    ("Zapatillas deportivas", (600, 600)), ("Zapatillas", (610, 590)),
    ("Sudadera corta", (560, 540)), ("Sudadera", (600, 596)),
    ("Camiseta de tirantes", (560, 556)), ("Camiseta", (580, 566)),
    ("Gorro bucket", (500, 470)), ("Gorro", (470, 440)), ("Gorra", (480, 450)),
    ("Bandana", (486, 486)), ("Riñonera", (540, 470)), ("Mochila", (500, 566)),
    ("Chaqueta", (600, 596)), ("Cortavientos", (600, 596)),
    ("Pantalón jogger", (520, 606)), ("Pantalón corto", (520, 540)),
    ("Pantalón", (520, 606)), ("Calcetines", (540, 540)), ("Polo", (580, 566)),
    ("Bolsa", (520, 560)),
]

# abreviatura de tres letras para la referencia impresa en el margen
SIGLA = {"meandro-real": "MDR", "intarsia": "MRQ", "brocado-real": "BRC",
         "malaquita-real": "MLQ", "forja-real": "FRJ", "eslabon-real": "ESL",
         "camo-real": "CMO", "baraja-real": "BRJ", "plumaje-real": "PLM",
         "guilloche-real": "GLL", "neon-real": "NEO", "vidriera-real": "VDR",
         "corona-boreal": "CRB", "frecuencia": "FRC", "tartan-real": "TRT",
         "kintsugi-real": "KTS", "nube-imperial": "NUB", "suminagashi": "SMG",
         "azulejo-real": "AZL", "nomada-real": "NMD", "telar-real": "TLR",
         "paisley-real": "PSL", "laurel-real": "LRL", "relieve-real": "RLV",
         "cifra-real": "CFR"}

ROMANOS = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def romano(n):
    """Números de lámina en romano. Más allá de X no compensa: se abrevia."""
    if n <= 10:
        return ROMANOS[n]
    d, u = divmod(n, 10)
    dec = ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC", "C"][d]
    return dec + ROMANOS[u]


def caja(nombre_prenda):
    for clave, val in CAJA_PRENDA:
        if nombre_prenda.lower().startswith(clave.lower()):
            return val
    return (580, 580)


def encajar(sprite, nombre_prenda):
    """Ancho final para que la pieza quepa entera en su caja, sin deformarla."""
    aw, ah = caja(nombre_prenda)
    sw, sh = sprite.size
    escala = min(aw / sw, ah / sh)
    return max(1, int(sw * escala))


def cabecera(img, d):
    img.alpha_composite(tint(crown_mask((W, H), 540, 140, 46, 29, lw=1.5), ORO_HI, 0.95))
    track(d, (540, 182), "STREET ROYALTY HOOD", F(JURA_L, 20), CREMA_DIM + (255,), 10, "ct")
    rule(d, 222, 100, ORO, 105)


def pie(img, d, sub="SERIES LIMITADAS · HECHO BAJO DEMANDA"):
    rule(d, 1236, 360, ORO, 62)
    track(d, (540, 1268), "SRHOOD.COM", F(BIGSH_B, 42), CREMA + (255,), 11, "cm")
    track(d, (540, 1300), sub, F(GEIST, 14), ORO_HI + (215,), 3.4, "cm")


def aparato(img, d, ref):
    registration(d)
    edge_ticks(d, [CY - R_OUT, CY, CY + R_OUT])
    vlabel(img, (MARGIN - 28, 470), ref, F(GEIST, 13), CREMA_MUTE + (185,), 2.6, "l")
    vlabel(img, (W - MARGIN + 12, 500), "40.4168° N — 3.7038° W", F(GEIST, 13),
           CREMA_MUTE + (185,), 2.6, "r")


def vitrina(img, rose_a, rose_b, rot):
    img.alpha_composite(tint(guilloche_mask((W, H), 540, CY, [
        dict(a=rose_a, b=rose_b, h=1.00, turns=54, steps=16000, R=R_ROSE, lw=0.78, rot=rot)
    ]), ORO, 0.55))
    img.alpha_composite(tint(ring_mask((W, H), 540, CY, [(R_OUT, 1.0, 255)]), ORO, 0.44))
    img.alpha_composite(tint(ring_mask((W, H), 540, CY, [(R_OUT - 8, 1.0, 255)]), ORO, 0.17))


def roseta(i):
    """Parámetros de la roseta derivados del índice: cien grabados distintos y
    reproducibles. Los pasos son primos entre sí para que no se repita el ciclo."""
    a = 3 + (i * 7) % 9
    b = 1.011 + ((i * 13) % 27) * 0.002
    return a, round(b, 4), (i * 37) % 360


def plancha(p):
    acento = tuple(p["acento"])
    img = field((16, 19, 19), (6, 7, 9),
                glow=(540, CY - 15, 500, acento, 0.38)).convert("RGBA")
    a, b, rot = roseta(p["n"])
    vitrina(img, a, b, rot)

    sp = cutout(p["file"], lmin=p["qa"]["lmin"])
    place(img, sp, 540, CY + 20, target_w=encajar(sp, p["prenda"]),
          halo=(46, 0.46, acento), shadow=(36, 0.46, 26))

    d = ImageDraw.Draw(img)
    cabecera(img, d)

    f, tr = fit_display(d, p["display"], ITALIANA, DISPLAY, 8, max_w=880)
    track(d, (540, 1000), p["display"], f, CREMA + (255,), tr, "cm")
    rule(d, 1054, 250, ORO, 80)
    track(d, (540, 1086), p["linea"], F(GEIST, 16), ORO_HI + (232,), 4.0, "cm")
    track(d, (540, 1116), p["sub"], F(GEIST, 14), CREMA_MUTE + (255,), 3.6, "cm")
    price_tag(d, 540, 1176, p["precio_txt"], size=58)

    pie(img, d)
    aparato(img, d, p["ref"])
    return grain(img, seed=(p["n"] * 17) % 997)


def preparar(lote, catalogo):
    """Rellena cada entrada con lo que necesita la plancha y el publicador."""
    cat = {q["handle"]: q for q in catalogo}
    for i, p in enumerate(lote):
        prod = cat[p["handle"]]
        cap = p["caps"][0] if p["caps"] else "—"
        c = T.CAPSULAS.get(cap, T.BASE)
        p["cap"] = cap
        p["prenda"] = T.prenda(prod, p["tipo"])
        p["display"] = T.titular(p["handle"], p["titulo"])
        p["linea"] = c["linea"]
        genero = ("MUJER" if "mujer" in prod["title"].lower() else
                  "HOMBRE" if "hombre" in prod["title"].lower() else "UNISEX")
        p["sub"] = f'{p["prenda"].upper()} · {genero}'
        p["precio_txt"] = f'{float(p["precio"]):.2f}'.replace(".", ",")
        p["ref"] = f'REF. SR—{SIGLA.get(cap, "RYC")} / F. {romano(p["n"])}'
        p["pie"] = T.pie(prod, cap, i)
        p["hashtags"] = T.hashtags(p["tipo"], cap, i, p["titulo"])
        p["alt"] = T.alt(prod, p["tipo"], cap, p["display"])
        p["imagen"] = f'srhood-l02-{p["n"]:03d}.jpg'
    return lote


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", default="lotes/lote-02.json")
    ap.add_argument("--catalogo", help="json cacheado; si falta, se baja de la tienda")
    ap.add_argument("--salida", default="out/lote02")
    ap.add_argument("--solo", type=int, help="renderiza solo la plancha n (prueba)")
    ap.add_argument("--desde", type=int, default=1)
    a = ap.parse_args()

    asegurar_fuentes()
    import catalogo as C
    cat = json.load(open(a.catalogo)) if a.catalogo else C.catalogo()
    lote = preparar(json.load(open(a.lote)), cat)
    json.dump(lote, open(a.lote, "w"), ensure_ascii=False, indent=1)

    os.makedirs(a.salida, exist_ok=True)
    for p in lote:
        if a.solo and p["n"] != a.solo:
            continue
        if p["n"] < a.desde:
            continue
        ruta = os.path.join(a.salida, p["imagen"])
        plancha(p).convert("RGB").save(ruta, "JPEG", quality=92, subsampling=0)
        print(f'  [{p["n"]:03d}] {p["display"]:22s} → {ruta}')
