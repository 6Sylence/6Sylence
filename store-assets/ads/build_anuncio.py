#!/usr/bin/env python3
"""
Heráldica Mineral — SRHOOD · anuncio de categoría para Instagram.

Un anuncio no es una publicación, y la diferencia manda en la retícula:

  · **El botón se dibuja encima.** En Historias, «Comprar» ocupa la franja inferior
    de la pantalla. El pie del feed vive en y≈1270 de 1350, que en 9:16 caería
    justo debajo del botón: aquí el pie sube a y≈1500 y de 1620 abajo no se pone
    nada. Arriba pasa lo mismo con el nombre de la cuenta, así que el contenido
    empieza en 300.
  · **Se ve sin contexto y sin sonido**, entre historias de amigos. El titular
    tiene que funcionar solo, y el precio va en la plancha a propósito: quien pulsa
    después de leer 24,95 € ya ha aceptado el precio, y ese clic vale lo que cuesta.
  · **Solo se afirma lo comprobable.** El pie dice «producción bajo demanda en
    Europa», que es literalmente lo que declaran las fichas de producto, y no de
    dónde sale el paquete: eso depende del taller que asigne el fabricante y no
    está verificado. Ninguna mención de envío gratis, por la decisión del 31/07.
  · **Es de categoría, no de producto.** Tres piezas —gorro, bucket y gorra— en vez
    de una: el anuncio vende la sección entera y el clic aterriza en la colección.

Se generan los dos formatos que pide el administrador de anuncios: 9:16 para
Historias y Reels, y 4:5 para el feed. Misma composición, distinta caja.
"""
import json, os, argparse
from PIL import ImageDraw
import srhood_stories as S
from srhood_stories import *   # noqa
import catalogo as C

# Las tres piezas: un tono oscuro, uno claro y uno cálido. Con las tres claras el
# grupo se empasta contra el campo, y con las tres oscuras hace falta tanto halo
# que se come el grabado.
#
# `lmin`/`smax` sobreescriben el umbral que eligió el QA automático. Hace falta en la
# gorra caqui: su mockup lleva una sombra proyectada que **no es neutra** —recoge el
# caqui y sube a saturación 0,13—, así que ningún umbral de luminancia la trata como
# fondo y quedaba pegada bajo la visera como una franja gris. A lmin=100 desaparece.
#
# El QA no lo elige solo porque su métrica de fuga compara contra una segmentación
# conservadora que **incluye la sombra**, y por eso lee «quitar la sombra» como
# «perder producto» (0,16, por encima del corte). En un lote de cien eso es la
# decisión prudente; en un anuncio de tres piezas escogidas a mano, se mira y se fija.
PIEZAS = [
    dict(handle="street-royalty-bucket-hat-corona-srh-negro-y-navy", escala=0.84, dx=-288, dy=40),
    dict(handle="street-royalty-gorro-corona-srh-blanco-y-gris-jaspeado", escala=0.90, dx=0, dy=6),
    dict(handle="street-royalty-gorra-sello-club-caqui", escala=0.84, dx=288, dy=46,
         lmin=100),
]

TITULAR = "LO PRIMERO QUE SE VE"
LINEA = "GORROS · BUCKETS · GORRAS"
SUB = "BORDADO EN RELIEVE · TALLA ÚNICA"
PRECIO = "24,95"

# (ancho, alto, cy_vitrina, radio, y_titular, y_linea, y_sub, y_precio, y_pie, display)
FORMATOS = {
    "story": dict(w=1080, h=1920, cy=860, r=372, display=118, y_cab=300,
                  y_tit=1252, y_lin=1330, y_sub=1364, y_pre=1432, y_pie=1524),
    "feed":  dict(w=1080, h=1350, cy=600, r=332, display=104, y_cab=140,
                  y_tit=1000, y_lin=1086, y_sub=1116, y_pre=1176, y_pie=1268),
}


def cargar(qa_path):
    qa = {c["handle"]: c for c in json.load(open(qa_path))}
    falta = [p["handle"] for p in PIEZAS if p["handle"] not in qa]
    if falta:
        raise SystemExit("✗ No están en el QA: " + ", ".join(falta))
    return qa


def anuncio(fmt, qa, acento=(120, 92, 40)):
    F_ = FORMATOS[fmt]
    W, H, CY, R = F_["w"], F_["h"], F_["cy"], F_["r"]
    S.set_canvas(W, H)
    S.MARGIN = 60
    cx = W // 2

    img = field((16, 19, 19), (6, 7, 9),
                glow=(cx, CY - 20, int(R * 1.55), acento, 0.40)).convert("RGBA")
    img.alpha_composite(tint(guilloche_mask((W, H), cx, CY, [
        dict(a=7, b=1.031, h=1.00, turns=54, steps=16000, R=int(R * 0.93), lw=0.78, rot=17)
    ]), ORO, 0.55))
    img.alpha_composite(tint(ring_mask((W, H), cx, CY, [(R, 1.0, 255)]), ORO, 0.44))
    img.alpha_composite(tint(ring_mask((W, H), cx, CY, [(R - 8, 1.0, 255)]), ORO, 0.17))

    # las laterales primero, para que la central quede por encima en el solape
    orden = sorted(PIEZAS, key=lambda p: -abs(p["dx"]))
    base = int(R * 1.02)
    for p in orden:
        q = qa[p["handle"]]["qa"]
        sp = cutout(qa[p["handle"]]["file"],
                    lmin=p.get("lmin", q["lmin"]),
                    smax=p.get("smax", q.get("smax", 0.08)))
        ancho = int(base * p["escala"] * (W / 1080))
        place(img, sp, cx + int(p["dx"] * W / 1080), CY + p["dy"],
              target_w=ancho, halo=(42, 0.40, acento), shadow=(34, 0.44, 24))

    d = ImageDraw.Draw(img)
    # En Historias, Instagram pinta el avatar y el nombre de la cuenta sobre los
    # primeros ~250 px: la cabecera del feed caería justo debajo y quedaría medio
    # tapada, así que en 9:16 baja a 300.
    yc = F_["y_cab"]
    img.alpha_composite(tint(crown_mask((W, H), cx, yc, 46, 29, lw=1.5), ORO_HI, 0.95))
    track(d, (cx, yc + 42), "STREET ROYALTY HOOD", F(JURA_L, 20), CREMA_DIM + (255,), 10, "ct")
    rule(d, yc + 82, 100, ORO, 105)

    f, tr = fit_display(d, TITULAR, ITALIANA, F_["display"], 8, max_w=W - 180)
    track(d, (cx, F_["y_tit"]), TITULAR, f, CREMA + (255,), tr, "cm")
    rule(d, F_["y_lin"] - 32, 250, ORO, 80)
    track(d, (cx, F_["y_lin"]), LINEA, F(GEIST, 16), ORO_HI + (232,), 4.0, "cm")
    track(d, (cx, F_["y_sub"]), SUB, F(GEIST, 14), CREMA_MUTE + (255,), 3.6, "cm")

    track(d, (cx, F_["y_pre"] - 34), "DESDE", F(JURA_M, 16), CREMA_MUTE + (230,), 6, "cm")
    price_tag(d, cx, F_["y_pre"], PRECIO, size=58)

    rule(d, F_["y_pie"] - 32, 360, ORO, 62)
    track(d, (cx, F_["y_pie"]), "SRHOOD.COM", F(BIGSH_B, 42), CREMA + (255,), 11, "cm")
    track(d, (cx, F_["y_pie"] + 32), "PRODUCCIÓN BAJO DEMANDA EN EUROPA",
          F(GEIST, 14), ORO_HI + (215,), 3.4, "cm")

    registration(d)
    return grain(img, seed=451)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--qa", required=True)
    ap.add_argument("--salida", default="out/anuncios")
    a = ap.parse_args()
    asegurar_fuentes()
    qa = cargar(a.qa)
    os.makedirs(a.salida, exist_ok=True)
    for fmt in FORMATOS:
        ruta = os.path.join(a.salida, f"srhood-anuncio-gorros-{fmt}.jpg")
        anuncio(fmt, qa).convert("RGB").save(ruta, "JPEG", quality=94, subsampling=0)
        print("→", ruta)
