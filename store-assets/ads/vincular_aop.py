#!/usr/bin/env python3
"""
Vincula en Printful los productos de estampado integral creados desde Shopify.

## El hallazgo que hace esto posible

Yo había concluido —y escrito— que vincular un producto por API era imposible. Era
falso, y el error estuvo en dónde busqué. La API v2 de Printful **no** tiene forma de
crear el vínculo:

    PUT /v2/sync-variants/{id}?syncProductId=…&syncVariantId=…
    409 · "Cannot update the design of a sync variant with no catalog_variant_id"

Ese endpoint lee el `catalog_variant_id` del registro, no del cuerpo: sirve para cambiar
el diseño de una variante **ya** vinculada. Probé veinte combinaciones de ruta, método y
carga alrededor de `/v2/sync-products` y `/v2/sync-variants`, y todas fallan.

Lo que sí funciona está en la **v1**, en una familia de rutas distinta que no había
tocado:

    PUT /sync/variant/{sync_variant_id}
    PUT /sync/variant/@{external_id}          ← también acepta el id de Shopify

con `variant_id` (el de catálogo de Printful), `retail_price`, `is_ignored: false`,
`files` y `options`. Devuelve `synced: true` y el producto queda fabricable.

**La lección de método:** que `/store/products` conteste «este endpoint solo aplica a
tiendas de plataforma Manual Order» no significa que *ninguna* ruta v1 sirva. Esa
respuesta era sobre **crear** productos; **vincular** es otra operación y vive en otro
sitio. Generalicé de un endpoint a una API entera.

## De dónde sale cada dato

El `variant_id` de catálogo **no hay que buscarlo**: está en el SKU. Las fichas se
crearon con `PF` + `catalog_variant_id` justamente por esto, siguiendo el patrón de los
productos que ya se fabricaban (el pedido #1001 se sirvió con `PF4011`). Así que
`variant_id = int(sku[2:])`, sin tablas que mantener y sin margen para desalinearse.

## Colocaciones

Cada prenda necesita el fichero en **todos** sus paneles, no solo en el frontal. Se
aprendió a golpes con la bandolera, que salió con los laterales blancos por no cubrir
`details` ni `inside_pocket`. Printful renombra `front` a `default` al guardarlo; el
resto conserva su nombre.

## Uso

    python3 vincular_aop.py --plan          # qué haría, sin tocar nada
    python3 vincular_aop.py --aplicar
    python3 vincular_aop.py --verificar     # cuántas quedan sincronizadas
"""
import argparse, json, os, re, sys, time
import urllib.request, urllib.error

CLAVE = os.environ.get("PRINTFUL_API_KEY", "")
TIENDA = os.environ.get("PRINTFUL_STORE_ID", "18383330")
CDN = "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"

# prenda → (id de catálogo, colocaciones a cubrir, sufijo del fichero, PVP)
PRENDAS = {
    "hoodie":    (388, ["front", "back", "sleeve_left", "sleeve_right", "hood", "pocket"],
                  "388-2362x2362", "84.95"),
    "sudadera":  (320, ["front", "back", "sleeve_left", "sleeve_right"],
                  "320-1983x2598", "74.95"),
    "pantalon":  (618, ["front", "back"], "618-3307x3189", "69.95"),
    "bandolera": (744, ["front", "back", "pocket", "details", "inside_pocket"],
                  "744-886x591", "44.95"),
    "crop":      (200, ["default"], "200-2421x1240", "39.95"),
}
CAPSULAS = ["brocado", "malaquita", "meandro", "camo"]


def api(metodo, ruta, cuerpo=None, reintentos=6):
    for intento in range(reintentos):
        datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
        req = urllib.request.Request(
            "https://api.printful.com" + ruta, data=datos, method=metodo,
            headers={"Authorization": "Bearer " + CLAVE, "X-PF-Store-Id": TIENDA,
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            cuerpo_err = e.read().decode()[:200]
            if e.code in (429, 500, 502, 503) and intento < reintentos - 1:
                time.sleep(8 * (intento + 1))
                continue
            raise RuntimeError(f"HTTP {e.code} {metodo} {ruta}: {cuerpo_err}")
        except (urllib.error.URLError, OSError):
            if intento < reintentos - 1:
                time.sleep(5 * (intento + 1))
                continue
            raise


def clasificar(nombre):
    """Del título de la ficha saca la prenda y la cápsula. Devuelve None si no es
    de estampado integral, para no tocar nunca un producto que no sea nuestro."""
    n = nombre.lower()
    if "integral" not in n:
        return None
    prenda = ("hoodie" if "hoodie" in n else "sudadera" if "sudadera" in n else
              "pantalon" if "pantal" in n else "bandolera" if "bandolera" in n else
              "crop" if "crop" in n else None)
    capsula = next((c for c in CAPSULAS if c in n), None)
    if not prenda or not capsula:
        return None
    return prenda, capsula


def pendientes():
    """Productos de estampado integral con alguna variante sin sincronizar."""
    fuera, offset = [], 0
    while True:
        r = api("GET", f"/sync/products?limit=100&offset={offset}")["result"]
        if not r:
            break
        for p in r:
            cl = clasificar(p["name"])
            if cl and p.get("synced", 0) < p.get("variants", 0):
                fuera.append((p["id"], p["name"], cl))
        offset += 100
    return fuera


def vincular(sp_id, prenda, capsula, seco=False):
    pid, colocaciones, sufijo, pvp = PRENDAS[prenda]
    url = f"{CDN}{capsula}-{sufijo}.jpg"
    detalle = api("GET", f"/sync/products/{sp_id}")["result"]
    hechas = 0
    for v in detalle["sync_variants"]:
        if v.get("synced") and v.get("variant_id"):
            continue
        sku = v.get("sku") or ""
        if not re.fullmatch(r"PF\d+", sku):
            print(f"    ✗ {v['name'][-12:]}: SKU inesperado {sku!r}, se salta")
            continue
        cuerpo = {
            "variant_id": int(sku[2:]),          # el SKU ya lleva el id de catálogo
            "retail_price": pvp,
            "is_ignored": False,
            "files": [{"type": c, "url": url} for c in colocaciones],
            "options": [{"id": "stitch_color", "value": "black"}],
        }
        if seco:
            print(f"    · {v['name'][-14:]:14s} → variante {cuerpo['variant_id']}")
            hechas += 1
            continue
        r = api("PUT", f"/sync/variant/{v['id']}", cuerpo)["result"]["sync_variant"]
        malos = [f["type"] for f in r.get("files", []) if f.get("status") != "ok"]
        print(f"    · {v['name'][-14:]:14s} synced={r.get('synced')} "
              f"ficheros={len(r.get('files', []))}" + (f" ✗ {malos}" if malos else ""))
        hechas += 1
        time.sleep(0.6)                          # el límite de Printful ronda 120/min
    return hechas


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--verificar", action="store_true")
    a = ap.parse_args()
    if not CLAVE:
        sys.exit("✗ Falta PRINTFUL_API_KEY en el entorno.")

    if a.verificar:
        tot = sinc = prods = 0
        offset = 0
        while True:
            r = api("GET", f"/sync/products?limit=100&offset={offset}")["result"]
            if not r:
                break
            for p in r:
                if clasificar(p["name"]):
                    prods += 1
                    tot += p.get("variants", 0)
                    sinc += p.get("synced", 0)
            offset += 100
        print(f"{prods} productos de estampado integral · {sinc}/{tot} variantes sincronizadas")
        sys.exit(0 if sinc == tot else 1)

    lista = pendientes()
    print(f"{len(lista)} productos con variantes pendientes")
    total = 0
    for sp_id, nombre, (prenda, capsula) in lista:
        print(f"  {nombre[:46]}")
        total += vincular(sp_id, prenda, capsula, seco=not a.aplicar)
    print(f"\n{'Se vincularían' if not a.aplicar else 'Vinculadas'}: {total} variantes")
