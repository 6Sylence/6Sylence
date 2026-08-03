#!/usr/bin/env python3
"""
Selector de lote: escoge las N piezas siguientes que aún no se han publicado.

Tres cosas que hace y conviene entender:

1. **No repite.** `lotes/publicados.json` guarda el handle de todo lo que ya salió.
   Ese fichero es la memoria entre lotes: mientras exista, el lote 3 arranca donde
   terminó el 2 sin que nadie tenga que acordarse.

2. **Descarta lo que el recorte no aguanta** (ver `catalogo.qa`). Una zapatilla
   blanca sobre fondo blanco no se puede recortar por inundación, así que no entra.

3. **Reparte.** Sin cuotas, el ranking se llena de sudaderas: hay 59 aptas y son las
   que mejor puntúan. Se limita por cápsula y por tipo, y luego se intercala calzado
   / prenda / accesorio para que la cuadrícula del perfil no salga a bloques.

El acento cromático de cada plancha **se mide de la propia foto** (color dominante
saturado de la pieza), no se elige a mano: con 100 planchas, a mano se pierde la
coherencia a la tercera.
"""
import json, os, argparse
import numpy as np
from PIL import Image
import catalogo as C

AQUI = os.path.dirname(os.path.abspath(__file__))
LOTES = os.path.join(AQUI, "lotes")
PUBLICADOS = os.path.join(LOTES, "publicados.json")

PESO_TIPO = {
    "ZAPATILLAS": 30, "Zapatillas": 30, "Hoodie": 28, "Cropped Hoodie": 20,
    "Sudadera Cremallera": 24, "Sudadera": 22, "Chaqueta": 22, "Cortavientos": 22,
    "Bucket Hat": 18, "Camiseta": 16, "Jogger": 16, "Camiseta Manga Larga": 14,
    "Gorra": 14, "Bandana": 14, "Gorro": 12, "Shorts": 10, "Pantalón": 10,
    "Riñonera": 10, "Mochila": 10, "Bolsa": 9, "Calcetines": 8, "Polo": 8,
    "Camiseta de Tirantes": 8,
}

# familias para intercalar la cuadrícula
FAMILIA = {"ZAPATILLAS": "calzado", "Zapatillas": "calzado",
           "Hoodie": "prenda", "Cropped Hoodie": "prenda", "Sudadera": "prenda",
           "Sudadera Cremallera": "prenda", "Chaqueta": "prenda",
           "Cortavientos": "prenda", "Camiseta": "prenda",
           "Camiseta Manga Larga": "prenda", "Camiseta de Tirantes": "prenda",
           "Polo": "prenda", "Jogger": "prenda", "Pantalón": "prenda",
           "Shorts": "prenda"}


def acento(path, lmin=100):
    """Color del halo que va detrás de la pieza.

    El **tono** se toma de la propia foto: los píxeles saturados de la pieza,
    promediados con peso de saturación. Así una cápsula esmeralda arrastra un halo
    verde y una de nogal uno cálido, sin decidir nada a mano.

    La **luminancia** va al revés que la pieza, y ese es el truco. Una zapatilla
    oliva sobre un halo oliva de la misma claridad desaparece dentro de él —pasó
    con las Essential verde cuartel—, así que:

        pieza oscura  → halo claro  (la silueta se recorta contra la luz)
        pieza clara   → halo oscuro (la pieza se recorta contra la sombra)

    El tono se conserva en los dos casos; solo cambia de qué lado del producto
    está el contraste.
    """
    arr = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    m = C.mascara(arr, lmin)
    if m.sum() < 200:
        return (108, 84, 38)
    px = arr[m]
    mx, mn = px.max(axis=1), px.min(axis=1)
    sat = (mx - mn) / np.maximum(mx, 1.0)
    objetivo = 118 if float(mx.mean()) < 85 else 48
    vivos = sat > 0.18
    if vivos.sum() < 60:                   # pieza acromática (negro, blanco, gris)
        base = np.array([108.0, 84.0, 38.0])   # oro apagado, el neutro de la casa
    else:
        base = np.average(px[vivos], axis=0, weights=sat[vivos])
    c = base / max(base.max(), 1.0) * objetivo
    return tuple(int(v) for v in c)


def publicados():
    if os.path.exists(PUBLICADOS):
        return set(json.load(open(PUBLICADOS)))
    return set()


def puntuar(p):
    q = p["qa"]
    s = PESO_TIPO.get(p["tipo"], 8) + q["cohes"] * 20
    if p["caps"]:
        s += 40
    for t in ("premium", "oversized", "garment-dyed", "all-over-print", "novedades"):
        if t in p["tags"]:
            s += 5
    return s


def intercalar(elegidos):
    """Reparte las familias por toda la tira, no solo al principio.

    Un turno fijo (prenda, calzado, prenda, accesorio) agota la cola corta enseguida
    y deja las últimas veinte planchas siendo todo zapatillas. En vez de eso, a cada
    pieza se le da una posición ideal repartida en [0,1) dentro de su familia y se
    ordena por ella: cada familia queda estirada de punta a punta, en proporción a
    cuántas piezas tiene.
    """
    colas = {}
    for p in elegidos:
        colas.setdefault(FAMILIA.get(p["tipo"], "accesorio"), []).append(p)
    marcados = []
    for i, (fam, cola) in enumerate(sorted(colas.items())):
        for j, p in enumerate(cola):
            # el desfase por familia evita que dos familias caigan siempre juntas
            marcados.append(((j + 0.5) / len(cola) + i * 0.017, p))
    marcados.sort(key=lambda x: x[0])
    return [p for _, p in marcados]


def seleccionar(qa_items, n=100, max_cap=4, max_tipo=22):
    ya = publicados()
    pool = [p for p in qa_items if p["qa"]["ok"] and p["handle"] not in ya]
    pool.sort(key=puntuar, reverse=True)
    por_cap, por_tipo, elegidos = {}, {}, []
    for p in pool:
        if len(elegidos) >= n:
            break
        cap = p["caps"][0] if p["caps"] else "—"
        if por_cap.get(cap, 0) >= max_cap or por_tipo.get(p["tipo"], 0) >= max_tipo:
            continue
        por_cap[cap] = por_cap.get(cap, 0) + 1
        por_tipo[p["tipo"]] = por_tipo.get(p["tipo"], 0) + 1
        elegidos.append(p)
    # segunda pasada: si las cuotas dejaron hueco, se rellena con lo mejor que quede
    if len(elegidos) < n:
        resto = [p for p in pool if p not in elegidos]
        elegidos += resto[:n - len(elegidos)]
    return intercalar(elegidos)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--qa", required=True, help="json con el QA del catálogo")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()

    items = json.load(open(a.qa))
    sel = seleccionar(items, a.n)
    for i, p in enumerate(sel, 1):
        p["n"] = i
        p["acento"] = acento(p["file"], p["qa"]["lmin"])
    os.makedirs(os.path.dirname(a.salida) or ".", exist_ok=True)
    json.dump(sel, open(a.salida, "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(f"{len(sel)} piezas → {a.salida}")
    print("tipos:", Counter(p["tipo"] for p in sel).most_common())
    print("cápsulas:", len({p["caps"][0] for p in sel if p["caps"]}))
