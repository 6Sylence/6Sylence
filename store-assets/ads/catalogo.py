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


def qa(path, lmin=100, smax=0.08):
    """Simula el recorte y mide si la pieza sobrevive. Ver docstring del módulo.

    `relleno` es lo que de verdad separa un recorte bueno de uno roto: cuánto de su
    caja envolvente ocupa la pieza principal. Una zapatilla entera llena el 65-85%;
    cuando la inundación entra por un estampado blanco y negro y deja confeti, cae
    al 35% aunque `cohes` y `frag` sigan pareciendo razonables. Ese fue exactamente
    el caso de las Moiré, que pasaban el filtro y salían destrozadas en la plancha.
    """
    arr = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    solido = mascara(arr, lmin, smax)
    l2, n = ndimage.label(solido)
    if n == 0:
        return dict(area=0.0, frag=99, cohes=0.0, relleno=0.0, lum=0.0, lmin=lmin, ok=False)
    tam = ndimage.sum(solido, l2, range(1, n + 1))
    mayor_id = int(tam.argmax()) + 1
    may = l2 == mayor_id
    ys, xs = np.where(may)
    bbox = (ys.max() - ys.min() + 1) * (xs.max() - xs.min() + 1)
    total = max(float(solido.sum()), 1.0)
    area = total / solido.size
    frag = int((tam > float(tam.max()) * 0.04).sum())
    cohes = float(tam.max()) / total
    relleno = float(may.sum()) / max(bbox, 1)
    lum = float(arr.max(axis=2)[may].mean())
    return dict(area=round(area, 4), frag=frag, cohes=round(cohes, 3),
                relleno=round(relleno, 3), lum=round(lum, 1), lmin=lmin,
                ok=bool(0.06 < area < 0.72 and frag <= 3 and cohes > 0.55
                        and relleno > 0.45))


def qa_escalado(path, umbrales=(100, 130, 160, 200)):
    """Primer umbral que sobrevive; si ninguno, devuelve el último intento fallido."""
    r = None
    for lm in umbrales:
        r = qa(path, lmin=lm)
        if r["ok"]:
            return r
    return r
