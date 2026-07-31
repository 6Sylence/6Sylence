#!/usr/bin/env python3
"""
Heráldica Mineral — SRHOOD · lote de 10 publicaciones de feed (1080×1350, 4:5).

Mismo sistema que las Stories: roseta de guilloché trazada por acumulación,
recorte de producto por inundación sobre máscara de neutralidad, retícula fija.
Cambia el formato y el acento cromático de cada cápsula; la corona, el oro y la
tipografía no se mueven — es lo que cose la cuadrícula del perfil.
"""
from PIL import Image, ImageDraw
import srhood_stories as S
from srhood_stories import *   # noqa

S.set_canvas(1080, 1350)
S.MARGIN = 60
W, H, MARGIN = 1080, 1350, 60
asegurar_fuentes()

# acentos por cápsula: solo el halo cambia, el grabado sigue siendo oro
NOGAL     = (108, 66, 34)
TERRACOTA = (124, 56, 34)
BOTELLA   = (20, 74, 48)
ORO_GLOW  = (120, 92, 40)

CUT = {"brocado_shoe": 64, "forja_shoe": 64, "marq_shoe": 64,
       "malaquita_hoodie": 100, "cifra_hoodie": 100, "laurel_hoodie": 100,
       "kintsugi_hoodie": 100, "brocado_bucket": 100, "meandro_bandana": 100}

# (archivo, alto|ancho objetivo, modo)  ·  los zapatos se miden por ancho
FORMA = {"brocado_shoe": ("w", 620), "forja_shoe": ("w", 620), "marq_shoe": ("w", 620),
         "malaquita_hoodie": ("h", 596), "cifra_hoodie": ("h", 596),
         "laurel_hoodie": ("h", 596), "kintsugi_hoodie": ("h", 596),
         "brocado_bucket": ("w", 500), "meandro_bandana": ("w", 486)}

DISPLAY = 104
CY = 600                     # centro de la vitrina
R_OUT, R_ROSE = 332, 308   # el anillo cierra por encima del titular, sin cruzarlo


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


def vitrina(img, acento, rose_a, rose_b, rot=0):
    """Halo + roseta + doble anillo. La misma familia de curvas en cada plancha."""
    img.alpha_composite(tint(guilloche_mask((W, H), 540, CY, [
        dict(a=rose_a, b=rose_b, h=1.00, turns=54, steps=16000, R=R_ROSE, lw=0.78, rot=rot)
    ]), ORO, 0.55))
    img.alpha_composite(tint(ring_mask((W, H), 540, CY, [(R_OUT, 1.0, 255)]), ORO, 0.44))
    img.alpha_composite(tint(ring_mask((W, H), 540, CY, [(R_OUT - 8, 1.0, 255)]), ORO, 0.17))


def plancha(p):
    img = field((16, 19, 19), (6, 7, 9),
                glow=(540, CY - 15, 500, p["acento"], p.get("glow", 0.38))).convert("RGBA")
    vitrina(img, p["acento"], p.get("a", 5), p.get("b", 1.041), p.get("rot", 0))

    if p.get("src"):
        modo, val = FORMA[p["src"]]
        sp = cutout(f"{PROD}/{p['src']}.jpg", lmin=CUT[p["src"]])
        kw = {"target_w": val} if modo == "w" else {"target_h": val}
        place(img, sp, 540, CY + p.get("dy", 20), halo=(46, p.get("halo", 0.46), p["acento"]),
              shadow=(36, 0.46, 26), **kw)
    else:
        img.alpha_composite(tint(crown_mask((W, H), 540, CY - 10, 208, 130, filled=True),
                                 ORO_HI, 0.97))

    d = ImageDraw.Draw(img)
    cabecera(img, d)

    f, tr = fit_display(d, p["titulo"], ITALIANA, DISPLAY, 8, max_w=880)
    track(d, (540, 1000), p["titulo"], f, CREMA + (255,), tr, "cm")
    rule(d, 1054, 250, ORO, 80)
    track(d, (540, 1086), p["linea"], F(GEIST, 16), ORO_HI + (232,), 4.0, "cm")
    track(d, (540, 1116), p["sub"], F(GEIST, 14), CREMA_MUTE + (255,), 3.6, "cm")

    if p.get("precio"):
        price_tag(d, 540, 1176, p["precio"], size=58)
    else:
        track(d, (540, 1176), "S E   L L E V A", F(JURA_M, 22), ORO_HI + (240,), 8, "cm")

    pie(img, d, p.get("pie", "SERIES LIMITADAS · HECHO BAJO DEMANDA"))
    aparato(img, d, p["ref"])
    return grain(img, seed=p["seed"])


POSTS = [
    dict(n=1, src="brocado_shoe", titulo="SEDA REAL", precio="74,95", acento=ESM_HI,
         linea="CÁPSULA BROCADO · ORO SOBRE ESMERALDA", sub="ZAPATILLA ALTA · UNISEX",
         ref="REF. SR—BRC / F. I", seed=5),
    dict(n=2, src="malaquita_hoodie", titulo="PIEDRA REAL", precio="49,95", acento=ESM_HI,
         linea="CÁPSULA MALAQUITA · ESMERALDA Y ORO", sub="SUDADERA CAPUCHA PREMIUM",
         ref="REF. SR—MLQ / F. II", seed=13, a=7, b=1.017, rot=11),
    dict(n=3, src="cifra_hoodie", titulo="CIFRA REAL", precio="49,95", acento=ORO_GLOW,
         linea="EL MONOGRAMA DE LA CASA · CORONADO", sub="SUDADERA CAPUCHA PREMIUM",
         ref="REF. SR—CFR / F. III", seed=21, a=9, b=1.023, rot=23, glow=0.34, halo=0.58),
    dict(n=4, src="forja_shoe", titulo="HIERRO Y ORO", precio="74,95", acento=ORO_GLOW,
         linea="CÁPSULA FORJA · CELOSÍA DE HERRERÍA", sub="ZAPATILLA ALTA · UNISEX",
         ref="REF. SR—FRJ / F. IV", seed=34, a=4, b=1.052, rot=7, glow=0.32),
    dict(n=5, src="laurel_hoodie", titulo="VICTORIA REAL", precio="49,95", acento=BOTELLA,
         linea="CÁPSULA LAUREL · LA CORONA LAUREADA", sub="SUDADERA CAPUCHA PREMIUM",
         ref="REF. SR—LRL / F. V", seed=47, a=6, b=1.031, rot=17),
    dict(n=6, src="kintsugi_hoodie", titulo="ORO EN LA GRIETA", precio="49,95",
         acento=ORO_GLOW, linea="CÁPSULA KINTSUGI · LA LUNA ROTA",
         sub="SUDADERA CAPUCHA PREMIUM", ref="REF. SR—KTS / F. VI", seed=58,
         a=11, b=1.013, rot=29, glow=0.34, halo=0.54),
    dict(n=7, src="marq_shoe", titulo="INTARSIA REAL", precio="74,95", acento=NOGAL,
         linea="CÁPSULA MARQUETERÍA · MADERAS NOBLES", sub="ZAPATILLA ALTA · UNISEX",
         ref="REF. SR—MRQ / F. VII", seed=66, a=5, b=1.037, rot=13, glow=0.40),
    dict(n=8, src="brocado_bucket", titulo="DOS CARAS", precio="34,95", acento=ESM_HI,
         linea="BUCKET REVERSIBLE · BROCADO Y MARFIL", sub="ESTAMPADO INTEGRAL · UNISEX",
         ref="REF. SR—BKT / F. VIII", seed=72, a=3, b=1.063, rot=31),
    dict(n=9, src="meandro_bandana", titulo="EL REMATE", precio="19,95", acento=TERRACOTA,
         linea="CÁPSULA MEANDRO · LABERINTO REAL", sub="BANDANA · CUELLO, MUÑECA O CABEZA",
         ref="REF. SR—MDR / F. IX", seed=88, a=8, b=1.019, rot=5, glow=0.34),
    dict(n=10, src=None, titulo="LA CORONA", precio=None, acento=ESM_HI,
         linea="NO SE PIDE", sub="STREET ROYALTY HOOD · MADRID · MMXXVI",
         ref="REF. SR—SLL / F. X", seed=99, a=6, b=1.031, glow=0.30,
         pie="BIENVENIDA15 · 15% EN TU PRIMERA COMPRA"),
]


if __name__ == "__main__":
    for p in POSTS:
        ruta = f"{OUT}/srhood-feed-{p['n']:02d}.png"
        plancha(p).save(ruta)
        print("→", ruta)
