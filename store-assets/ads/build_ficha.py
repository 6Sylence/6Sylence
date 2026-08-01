#!/usr/bin/env python3
"""
Heráldica Mineral — SRHOOD · imágenes de ficha de producto.

Dos capas, y la separación entre ellas no es estética sino obligatoria.

## Por qué la principal va limpia

La tienda publica en Google & YouTube, TikTok, Facebook & Instagram e Instagram
Shop. Los cuatro toman la **primera imagen** del producto para su catálogo, y tanto
la política de imágenes de Google Merchant Center como la de catálogos de Meta
prohíben en ella texto promocional, marcos, bordes y marcas de agua. Poner ahí la
plancha del anuncio —con su precio, su anillo de oro y su SRHOOD.COM— haría que los
artículos se rechazaran en las cuatro superficies a la vez, incluida la que alimenta
los anuncios de catálogo.

Y hay una razón de marca por encima de la técnica: **el overlay sobre foto de
producto es el lenguaje del descuento**. SHEIN y AliExpress decoran la foto; Aesop,
Byredo, Carhartt WIP, Stüssy y Arc'teryx la dejan desnuda y ponen la marca en lo que
se repite —encuadre, fondo, escala, sombra, tipografía de la página—. La coherencia
es lo que se lee como caro. El marco dorado, en la ficha, se leería como barato.

  · **Imagen 1 — `principal`**: producto recortado sobre hueso cálido, mismo margen,
    misma escala relativa por tipo de prenda, misma sombra de contacto. Sin una sola
    letra. Es apta para feed y es la que unifica la cuadrícula de colección.
  · **Imagen 2 — `editorial`**: la plancha Heráldica Mineral, que vive en la galería
    de la ficha y da la firma visual. Nunca toca el feed.

## Y por qué la editorial de ficha NO lleva precio

La del anuncio sí lo lleva, a propósito: cualifica el clic. La de la ficha no, porque
una imagen con el precio grabado se queda obsoleta en cuanto cambia la tarifa y pasa
a ser un precio anunciado que no coincide con el del carrito. Ya hemos limpiado esa
clase de desajuste en 61 fichas; no vamos a fabricarlo otra vez en las imágenes.
"""
import json, os, argparse
from PIL import Image, ImageDraw, ImageFilter
import srhood_stories as S
from srhood_stories import *   # noqa
import textos as T

LADO = 2048          # Shopify sirve hasta 2048 con zoom; cuadrado unifica la rejilla
HUESO = (243, 240, 234)
HUESO_BORDE = (228, 223, 214)

# Fracción del lado que ocupa la pieza, por corte de prenda. Fija por tipo para que
# en la cuadrícula de colección una gorra no salga del tamaño de una sudadera: es
# justo esa disparidad la que hace que un catálogo parezca improvisado.
OCUPACION = [
    ("Zapatillas", 0.78), ("Sudadera", 0.74), ("Camiseta", 0.72), ("Chaqueta", 0.74),
    ("Cortavientos", 0.74), ("Pantalón", 0.70), ("Bandana", 0.68), ("Gorro bucket", 0.60),
    ("Gorro", 0.56), ("Gorra", 0.60), ("Mochila", 0.66), ("Riñonera", 0.62),
    ("Bolsa", 0.66), ("Calcetines", 0.62), ("Polo", 0.72),
]


def ocupacion(prenda):
    for clave, v in OCUPACION:
        if prenda.lower().startswith(clave.lower()):
            return v
    return 0.70


def principal(p):
    """Imagen 1: apta para feed. Fondo hueso, sombra de contacto, cero texto."""
    img = Image.new("RGB", (LADO, LADO), HUESO)
    # viñeta muy leve: da profundidad sin que se lea como fondo de estudio barato
    v = Image.new("L", (LADO, LADO), 0)
    ImageDraw.Draw(v).ellipse([-LADO * 0.25, -LADO * 0.25, LADO * 1.25, LADO * 1.25], fill=255)
    img = Image.composite(img, Image.new("RGB", (LADO, LADO), HUESO_BORDE),
                          v.filter(ImageFilter.GaussianBlur(LADO * 0.10)))
    img = img.convert("RGBA")

    sp = cutout(p["file"], lmin=p["qa"]["lmin"], smax=p["qa"].get("smax", 0.08))
    caja = int(LADO * ocupacion(p["prenda"]))
    esc = min(caja / sp.width, caja / sp.height)
    nw, nh = int(sp.width * esc), int(sp.height * esc)
    sp = sp.resize((nw, nh), Image.LANCZOS)
    x, y = (LADO - nw) // 2, (LADO - nh) // 2

    # sombra de contacto: elipse difuminada bajo la pieza, no un duplicado desplazado.
    # El duplicado delata el recorte; la elipse se lee como apoyo sobre superficie.
    som = Image.new("L", (LADO, LADO), 0)
    ancho = int(nw * 0.72)
    ImageDraw.Draw(som).ellipse(
        [(LADO - ancho) // 2, y + nh - int(nh * 0.06),
         (LADO + ancho) // 2, y + nh + int(nh * 0.055)], fill=92)
    som = som.filter(ImageFilter.GaussianBlur(LADO * 0.018))
    img.alpha_composite(tint(som, (86, 80, 70), 1.0))
    img.alpha_composite(sp, (x, y))
    return img.convert("RGB")


def editorial(p):
    """Imagen 2: la plancha de la casa. Sin precio — ver el docstring del módulo."""
    S.set_canvas(LADO, LADO)
    S.MARGIN = int(LADO * 0.055)
    cx = cy = LADO // 2
    R = int(LADO * 0.315)
    acento = tuple(p["acento"])

    img = field((16, 19, 19), (6, 7, 9),
                glow=(cx, cy - int(LADO * 0.03), int(R * 1.5), acento, 0.38)).convert("RGBA")
    img.alpha_composite(tint(guilloche_mask((LADO, LADO), cx, cy, [
        dict(a=5 + (p["n"] * 7) % 9, b=1.011 + ((p["n"] * 13) % 27) * 0.002, h=1.0,
             turns=54, steps=16000, R=int(R * 0.94), lw=0.78, rot=(p["n"] * 37) % 360)
    ]), ORO, 0.55))
    img.alpha_composite(tint(ring_mask((LADO, LADO), cx, cy, [(R, 1.0, 255)]), ORO, 0.44))
    img.alpha_composite(tint(ring_mask((LADO, LADO), cx, cy, [(R - 14, 1.0, 255)]), ORO, 0.17))

    sp = cutout(p["file"], lmin=p["qa"]["lmin"], smax=p["qa"].get("smax", 0.08))
    caja = int(LADO * ocupacion(p["prenda"]) * 0.92)
    esc = min(caja / sp.width, caja / sp.height)
    place(img, sp, cx, cy - int(LADO * 0.015), target_w=int(sp.width * esc),
          halo=(int(LADO * 0.042), 0.44, acento), shadow=(int(LADO * 0.032), 0.44, 44))

    d = ImageDraw.Draw(img)
    img.alpha_composite(tint(crown_mask((LADO, LADO), cx, int(LADO * 0.088),
                                        int(LADO * 0.042), int(LADO * 0.027), lw=1.5),
                             ORO_HI, 0.95))
    track(d, (cx, int(LADO * 0.118)), "STREET ROYALTY HOOD", F(JURA_L, int(LADO * 0.0135)),
          CREMA_DIM + (255,), 10, "ct")

    f, tr = fit_display(d, p["display"], ITALIANA, int(LADO * 0.070), 8,
                        max_w=int(LADO * 0.82))
    track(d, (cx, int(LADO * 0.828)), p["display"], f, CREMA + (255,), tr, "cm")
    rule(d, int(LADO * 0.868), int(LADO * 0.17), ORO, 80)
    track(d, (cx, int(LADO * 0.893)), p["linea"], F(GEIST, int(LADO * 0.0105)),
          ORO_HI + (232,), 4.0, "cm")
    track(d, (cx, int(LADO * 0.917)), p["sub"], F(GEIST, int(LADO * 0.0092)),
          CREMA_MUTE + (255,), 3.6, "cm")
    registration(d)
    return grain(img, seed=(p["n"] * 17) % 997).convert("RGB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", required=True, help="manifiesto ya preparado por build_lote")
    ap.add_argument("--salida", default="out/fichas")
    ap.add_argument("--solo", type=int)
    ap.add_argument("--limite", type=int)
    a = ap.parse_args()
    asegurar_fuentes()
    os.makedirs(a.salida, exist_ok=True)
    lote = json.load(open(a.lote))
    if a.solo:
        lote = [p for p in lote if p["n"] == a.solo]
    if a.limite:
        lote = lote[:a.limite]
    for p in lote:
        base = f'{a.salida}/{p["handle"][:60]}'
        principal(p).save(f"{base}-1-principal.jpg", "JPEG", quality=92, subsampling=0)
        editorial(p).save(f"{base}-2-editorial.jpg", "JPEG", quality=92, subsampling=0)
        print(f'  {p["display"][:26]:28s} → {base}-{{1,2}}-*.jpg')
