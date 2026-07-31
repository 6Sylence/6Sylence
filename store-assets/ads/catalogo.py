#!/usr/bin/env python3
"""
Catálogo y control de calidad del recorte.

El catálogo se lee del escaparate público (`/products.json`), no de la Admin API:
son los mismos productos que ve un cliente, no hace falta credencial, y así el
selector de lotes funciona sin token.

La parte que importa es `qa()`. El recorte de producto de `srhood_stories.cutout`
inunda el fondo desde el borde sobre una máscara de neutralidad, así que **se come
las piezas claras**: una zapatilla blanca sobre fondo blanco no tiene frontera que
detenga la inundación. En vez de descubrirlo mirando 100 planchas, se mide antes:

  area   — fracción del encuadre que sobrevive. Muy poca = la pieza se disolvió;
           demasiada = no se recortó el fondo.
  frag   — trozos sueltos de tamaño relevante. Un mockup limpio da 1 (o 2 en un par
           de zapatillas separadas).
  cohes  — qué parte del recorte es la pieza principal. Bajo = quedó confeti.

Se prueban umbrales de luminancia crecientes y se queda el primero que pasa; si
ninguno pasa, el producto no entra en el lote. Es más barato descartar que retocar.
"""
import json, os, urllib.request
import numpy as np
from PIL import Image
from scipy import ndimage

TIENDA = "https://srhood.com"
AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(AQUI, "src2")

# tipos que son streetwear de verdad; fuera baño, mascotas, hogar y escritorio
TIPOS = {"ZAPATILLAS", "Zapatillas", "Hoodie", "Cropped Hoodie", "Sudadera",
         "Sudadera Cremallera", "Camiseta", "Camiseta Manga Larga",
         "Camiseta de Tirantes", "Polo", "Jogger", "Pantalón", "Shorts", "Chaqueta",
         "Cortavientos", "Bucket Hat", "Gorra", "Gorro", "Bandana", "Calcetines",
         "Riñonera", "Mochila", "Bolsa"}


def catalogo(cache=None):
    """Todos los productos publicados, paginando /products.json."""
    if cache and os.path.exists(cache):
        return json.load(open(cache))
    todos, pag = [], 1
    while True:
        u = f"{TIENDA}/products.json?limit=250&page={pag}"
        lote = json.load(urllib.request.urlopen(u)).get("products", [])
        if not lote:
            break
        todos += lote
        pag += 1
    if cache:
        json.dump(todos, open(cache, "w"), ensure_ascii=False)
    return todos


def capsulas(productos):
    """Las cápsulas se marcan con etiqueta: `*-real` o un nombre propio."""
    sueltas = {"frecuencia", "nube-imperial", "salpicadura-atelier", "corona-boreal",
               "suminagashi", "intarsia"}
    todas = {t for p in productos for t in p["tags"]}
    return {t for t in todas if t.endswith("-real") or t in sueltas}


def descargar(productos, hilos=16):
    """Baja la imagen principal de cada producto a src2/ (ignorado por git)."""
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(SRC, exist_ok=True)

    def una(p):
        destino = os.path.join(SRC, p["handle"] + ".jpg")
        if os.path.exists(destino) or not p["images"]:
            return
        src = p["images"][0]["src"].split("?")[0]
        if src.startswith("//"):
            src = "https:" + src
        try:
            urllib.request.urlretrieve(src, destino)
        except Exception as e:
            print("  ✗", p["handle"], e)

    with ThreadPoolExecutor(hilos) as ex:
        list(ex.map(una, productos))


def mascara(arr, lmin=100, smax=0.08):
    """La misma inundación que hace `cutout`, devuelta como máscara booleana."""
    L = arr.max(axis=2)
    sat = (L - arr.min(axis=2)) / np.maximum(L, 1.0)
    lab, _ = ndimage.label((L > lmin) & (sat < smax))
    borde = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
    borde.discard(0)
    fondo = np.isin(lab, list(borde)) if borde else np.zeros(L.shape, bool)
    return ndimage.binary_erosion(~fondo, iterations=1, border_value=0)


def _mayor(m):
    lab, n = ndimage.label(m)
    if n == 0:
        return m
    tam = ndimage.sum(m, lab, range(1, n + 1))
    return lab == (int(tam.argmax()) + 1)


def qa(path, lmin=100, smax=0.08):
    """Simula el recorte y mide si la pieza sobrevive. Ver docstring del módulo.

    Dos medidas hacen el trabajo, y cada una atrapa un fallo distinto:

    `relleno` — cuánto de su caja envolvente ocupa la pieza principal. Una zapatilla
    entera llena el 65-85%; cuando la inundación entra por un estampado blanco y
    negro y deja confeti, cae al 35%. Así cayeron las Moiré, que pasaban `area`,
    `frag` y `cohes` y salían destrozadas en la plancha.

    `fuga` — cuánto se ha comido la inundación, comparando contra una segmentación
    ultraconservadora (solo blanco casi puro, que no puede morder la prenda). Es la
    que atrapa el fallo silencioso: en una sudadera gris jaspeada la inundación entra
    por la capucha y sale por el borde, así que no deja huecos cerrados ni baja el
    relleno —el mordisco viene del perímetro— y la plancha sale con medio hombro
    ausente. Sanas: 0,00-0,06. Rotas: 0,10 para arriba. El corte va en 0,08, que deja
    fuera alguna sana rara —una gorra deshilachada da 0,107— pero ninguna rota dentro:
    con 172 candidatas, perder tres buenas es mejor negocio que publicar una rota.
    """
    arr = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    solido = mascara(arr, lmin, smax)
    l2, n = ndimage.label(solido)
    if n == 0:
        return dict(area=0.0, frag=99, cohes=0.0, relleno=0.0, lum=0.0, fuga=1.0,
                    lmin=lmin, smax=smax, ok=False)
    tam = ndimage.sum(solido, l2, range(1, n + 1))
    may = l2 == (int(tam.argmax()) + 1)
    ys, xs = np.where(may)
    bbox = (ys.max() - ys.min() + 1) * (xs.max() - xs.min() + 1)
    total = max(float(solido.sum()), 1.0)
    area = total / solido.size
    frag = int((tam > float(tam.max()) * 0.04).sum())
    cohes = float(tam.max()) / total
    relleno = float(may.sum()) / max(bbox, 1)
    lum = float(arr.max(axis=2)[may].mean())

    ref = _mayor(mascara(arr, 246, 0.03))
    # si el mockup no tiene fondo blanco (foto de estudio con pared gris, por
    # ejemplo), la referencia no vale y la comparación se omite en vez de mentir
    fuga = 0.0 if ref.sum() > 0.9 * ref.size or ref.sum() < 0.02 * ref.size \
        else max(0.0, 1 - float(may.sum()) / float(ref.sum()))

    return dict(area=round(area, 4), frag=frag, cohes=round(cohes, 3),
                relleno=round(relleno, 3), lum=round(lum, 1), fuga=round(fuga, 4),
                lmin=lmin, smax=smax,
                ok=bool(0.06 < area < 0.72 and frag <= 3 and cohes > 0.55
                        and relleno > 0.45 and fuga < 0.08))


# Escalera de umbrales, de permisivo a conservador. El último escalón —solo blanco
# casi puro— es el que rescata las piezas claras: un gorro blanco sobre fondo blanco
# se disuelve con cualquier umbral bajo, pero contra 246/0.03 sobrevive entero.
# Va el último y no el primero a propósito: en una prenda oscura ese umbral se traga
# también la sombra del mockup, porque el gris de la sombra ya no cuenta como fondo.
ESCALERA = ((100, 0.08), (130, 0.08), (160, 0.08), (200, 0.08), (246, 0.03))


def qa_escalado(path, escalones=ESCALERA):
    """Primer escalón que sobrevive; si ninguno, devuelve el último intento fallido."""
    r = None
    for lm, sm in escalones:
        r = qa(path, lmin=lm, smax=sm)
        if r["ok"]:
            return r
    return r
