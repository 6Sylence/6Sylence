#!/usr/bin/env python3
"""Genera los mockups de Printful para una tanda de cápsulas de estampado integral.

Se puede pedir el mockup **antes** de que exista la ficha en Shopify y antes de
vincular nada: `source: catalog` solo necesita el producto de catálogo, la
variante, las colocaciones y la URL del fichero de impresión, que ya está en el
CDN de la tienda. Eso permite crear el producto en Shopify con sus fotos ya
puestas, en vez de crearlo desnudo y rellenarlo después.

## Los estilos están elegidos a mano, y hay una razón por cada uno

Printful ofrece entre 24 y 358 estilos por producto. Casi todos son planos de
estudio sobre fondo blanco, que no venden. Los que van aquí son los verificados
uno a uno mirando la foto:

| Base | Estilos | Por qué |
|---|---|---|
| 388 hoodie | 20176, 20606 | Lifestyle 2 de hombre y de mujer, foto editorial |
| 320 sudadera | 18435, 18453 | Lifestyle 2 y 3, las dos con modelo y escenario |
| 618 pantalón | 21582, 4179 | Lifestyle 2 y Lifestyle; el pantalón necesita cuerpo entero |
| 744 bandolera | 21376, 22045 | **El plano va primero, y es deliberado** |
| 200 crop top | 20450, 15000 | Lifestyle 2 de mujer, y el On Model de frente |

**La bandolera fue una trampa.** Su estilo «Men's Lifestyle/Front» —que por el
nombre parece el frontal— fotografía al modelo **de espaldas**, con la bolsa
cruzada a la espalda, así que la primera imagen de la ficha no enseñaba el
estampado. Por eso la principal es el plano de estudio 21376 y el lifestyle va
detrás. Ninguna comprobación automática lo habría dicho: la tarea de mockup
termina «completed» igual.

## Uso

    python3 mockups_aop.py --capsulas tartan,azulejo --salida urls.json
"""
import argparse, json, os, sys, time
import urllib.request, urllib.error

CLAVE = os.environ.get("PRINTFUL_API_KEY", "")
TIENDA = os.environ.get("PRINTFUL_STORE_ID", "18383330")
CDN = "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"

# base → variante de catálogo con la que se renderiza, estilos, colocaciones y
# nombre del fichero de impresión
BASES = {
    "388": dict(variante=10871, estilos=[20176, 20606], fichero="{c}-388-2362x2362.jpg",
                placas=["front", "back", "sleeve_left", "sleeve_right", "hood", "pocket"]),
    "320": dict(variante=9732, estilos=[18435, 18453], fichero="{c}-320-1983x2598.jpg",
                placas=["front", "back", "sleeve_left", "sleeve_right"]),
    "618": dict(variante=15744, estilos=[21582, 4179], fichero="{c}-618-3307x3189.jpg",
                placas=["front", "back"]),
    "744": dict(variante=19256, estilos=[21376, 22045], fichero="{c}-744-886x591.jpg",
                placas=["front", "back", "pocket", "details", "inside_pocket"]),
    "200": dict(variante=7814, estilos=[20450, 15000], fichero="{c}-200-2421x1240.jpg",
                placas=["default"]),
}


def api(metodo, ruta, cuerpo=None, reintentos=6):
    for intento in range(reintentos):
        datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
        req = urllib.request.Request(
            "https://api.printful.com" + ruta, data=datos, method=metodo,
            # sin X-PF-Store-Id la API de mockups contesta 400, aunque la ruta
            # sea de catálogo y no dependa de la tienda
            headers={"Authorization": "Bearer " + CLAVE, "X-PF-Store-Id": TIENDA,
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            cuerpo_err = e.read().decode()[:300]
            if e.code in (429, 500, 502, 503) and intento < reintentos - 1:
                time.sleep(8 * (intento + 1))
                continue
            raise RuntimeError(f"HTTP {e.code} {metodo} {ruta}: {cuerpo_err}")
        except (urllib.error.URLError, OSError):
            if intento < reintentos - 1:
                time.sleep(5 * (intento + 1))
                continue
            raise


def lanzar(capsulas):
    tareas = {}
    for pid, cfg in BASES.items():
        for c in capsulas:
            url = CDN + cfg["fichero"].format(c=c)
            cuerpo = {"format": "jpg", "products": [{
                "source": "catalog", "catalog_product_id": int(pid),
                "catalog_variant_ids": [cfg["variante"]],
                "mockup_style_ids": cfg["estilos"],
                # obligatoria en cut-sew: sin ella no sale ni el mockup ni el pedido
                "product_options": [{"name": "stitch_color", "value": "black"}],
                "placements": [{"placement": p, "technique": "cut-sew",
                                "layers": [{"type": "file", "url": url}]}
                               for p in cfg["placas"]]}]}
            r = api("POST", "/v2/mockup-tasks", cuerpo)
            tareas[f"{c}-{pid}"] = r["data"][0]["id"]
            print(f"  lanzada {c}-{pid} → tarea {r['data'][0]['id']}", flush=True)
            time.sleep(1.5)
    return tareas


def recoger(tareas, vueltas=60, espera=15):
    """Devuelve {clave: [(estilo, url), …]} **en el orden pedido en `estilos`**.

    Printful no respeta el orden en que se piden los estilos, y eso importa: la
    primera imagen es la que se ve en la cuadrícula de colección. Una vez salió
    un crop top con el estilo equivocado de portada por dar por bueno el orden
    de la respuesta."""
    fuera = {}
    for _ in range(vueltas):
        time.sleep(espera)
        pendientes = 0
        for k, tid in tareas.items():
            if k in fuera:
                continue
            d = api("GET", f"/v2/mockup-tasks?id={tid}")["data"][0]
            if d["status"] == "pending":
                pendientes += 1
                continue
            urls = [(m["style_id"], m["mockup_url"])
                    for cv in d.get("catalog_variant_mockups", [])
                    for m in cv.get("mockups", [])]
            orden = BASES[k.rsplit("-", 1)[1]]["estilos"]
            urls.sort(key=lambda t: orden.index(t[0]) if t[0] in orden else 99)
            fuera[k] = urls
            print(f"  {k}: {d['status']} · {len(urls)} imágenes", flush=True)
        if not pendientes:
            break
    return fuera


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--capsulas", required=True, help="separadas por comas")
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()
    if not CLAVE:
        sys.exit("✗ Falta PRINTFUL_API_KEY en el entorno.")

    caps = a.capsulas.split(",")
    print(f"{len(caps) * len(BASES)} tareas de mockup")
    tareas = lanzar(caps)
    fuera = recoger(tareas)
    json.dump(fuera, open(a.salida, "w"), indent=1)
    faltan = [k for k in tareas if k not in fuera or not fuera[k]]
    print(f"\n{len(fuera)}/{len(tareas)} tareas con imágenes → {a.salida}")
    if faltan:
        print("✗ sin imágenes:", faltan)
        sys.exit(1)
