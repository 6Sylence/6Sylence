#!/usr/bin/env python3
"""
Regenera los mockups de la tienda con modelos, y con modelos tatuados donde los hay.

## Qué se encontró mirando, no leyendo

Printful ofrece ~118 estilos de mockup por producto, y la tienda usa **solo los
planos y fantasma**: de 588 productos publicados, ninguno tiene una foto con modelo.
Ese es el hallazgo grande, por encima de la cuestión de los tatuajes.

Sobre los tatuajes: la API **no dice** si un modelo lleva tatuajes, solo el nombre de
la categoría. Hubo que generar los estilos y mirarlos. El nombre engaña —«Men's
Lifestyle 2» tiene modelo tatuado en camiseta y en gorra, y no lo tiene en sudadera
con capucha—, así que esta tabla está verificada uno a uno y **no se debe ampliar por
analogía**: si se añade un tipo de prenda, hay que generar y mirar.

    camiseta (71)   754 Men's Lifestyle 2   antebrazos tatuados     ✔ verificado
                    758 Men's Lifestyle 3   antebrazos tatuados     ✔ verificado
    gorra (206)   15130 Men's Lifestyle 2   antebrazos tatuados     ✔ verificado
                  15099 Women's Lifestyle 2 tatuaje pequeño en mano ✔ verificado
    hoodie (380)  19955 Men's Lifestyle 2   SIN tatuajes            ✔ verificado
    sudadera (411), manga larga (356), bucket (654): no existen estilos Lifestyle 2/3

O sea: **hay modelo tatuado para camisetas y gorras, y no lo hay para el resto**.
Para las demás prendas lo que sí se puede hacer —y hace falta— es pasar de foto
plana a foto con modelo, aunque el modelo no vaya tatuado.
"""
import argparse, json, os, time
import urllib.request, urllib.error

CLAVE = os.environ.get("PRINTFUL_API_KEY", "")
TIENDA_PF = os.environ.get("PRINTFUL_STORE_ID", "18383330")
AQUI = os.path.dirname(os.path.abspath(__file__))

# Verificado a ojo, estilo por estilo. Ver el docstring: NO ampliar por analogía.
ESTILOS = {
    71:  dict(nombre="Camiseta B+C 3001", tecnica="dtg", placement="front",
              tatuado=[754, 758], relleno=[]),
    206: dict(nombre="Gorra bordada", tecnica="embroidery", placement="embroidery_front",
              tatuado=[15130, 15099], relleno=[]),
    380: dict(nombre="Hoodie", tecnica="dtg", placement="front",
              tatuado=[], relleno=[19955]),          # con modelo, sin tatuajes
}


def api(metodo, ruta, cuerpo=None, reintentos=3):
    for intento in range(reintentos):
        datos = json.dumps(cuerpo).encode() if cuerpo else None
        req = urllib.request.Request(
            "https://api.printful.com" + ruta, data=datos, method=metodo,
            headers={"Authorization": "Bearer " + CLAVE, "X-PF-Store-Id": TIENDA_PF,
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            cuerpo_err = e.read().decode()[:200]
            if e.code == 429 and intento < reintentos - 1:
                time.sleep(30 * (intento + 1))
                continue
            raise RuntimeError(f"HTTP {e.code} {metodo} {ruta}: {cuerpo_err}")
        except urllib.error.URLError:
            if intento < reintentos - 1:
                time.sleep(10)
                continue
            raise


def sync_products(limite=None):
    """Todos los productos sincronizados con su id de Shopify (external_id)."""
    todos, offset = [], 0
    while True:
        r = api("GET", f"/v2/sync-products?limit=100&offset={offset}")
        d = r.get("data", [])
        if not d:
            break
        todos += d
        offset += 100
        if limite and len(todos) >= limite:
            return todos[:limite]
    return todos


def esperar(tarea, espera=6, vueltas=50):
    for _ in range(vueltas):
        r = api("GET", f"/v2/mockup-tasks?id={tarea}")
        d = r["data"][0]
        if d["status"] != "pending":
            return d
        time.sleep(espera)
    return {"status": "timeout", "catalog_variant_mockups": []}


def generar(catalog_product_id, catalog_variant_id, url_diseno, estilos, cfg):
    """Lanza una tarea de mockup y devuelve {style_id: url}."""
    r = api("POST", "/v2/mockup-tasks", {"format": "jpg", "products": [{
        "source": "catalog",
        "catalog_product_id": catalog_product_id,
        "catalog_variant_ids": [catalog_variant_id],
        "mockup_style_ids": estilos,
        "placements": [{"placement": cfg["placement"], "technique": cfg["tecnica"],
                        "layers": [{"type": "file", "url": url_diseno}]}]}]})
    d = esperar(r["data"][0]["id"])
    out = {}
    for cv in d.get("catalog_variant_mockups", []):
        for mk in cv.get("mockups", []):
            out[mk["style_id"]] = mk["mockup_url"]
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--listar", action="store_true",
                    help="cuenta qué productos de la tienda pueden llevar modelo")
    ap.add_argument("--salida", default="lotes/mockups.json")
    ap.add_argument("--limite", type=int)
    a = ap.parse_args()
    if not CLAVE:
        raise SystemExit("✗ Falta PRINTFUL_API_KEY en el entorno.")

    prods = sync_products(a.limite)
    print(f"{len(prods)} productos sincronizados en Printful")

    if a.listar:
        from collections import Counter
        c = Counter()
        for p in prods:
            v = api("GET", f'/v2/sync-products/{p["id"]}/sync-variants?limit=1')["data"]
            if not v:
                continue
            cv = api("GET", f'/v2/catalog-variants/{v[0]["catalog_variant_id"]}')["data"]
            c[cv["catalog_product_id"]] += 1
        for pid, n in c.most_common():
            cfg = ESTILOS.get(pid)
            etiqueta = ("tatuado" if cfg and cfg["tatuado"] else
                        "modelo sin tatuajes" if cfg else "sin estilo verificado")
            print(f"  producto base {pid:5d}: {n:4d} artículos · {etiqueta}")
