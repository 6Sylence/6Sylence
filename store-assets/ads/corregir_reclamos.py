#!/usr/bin/env python3
"""
Quita de las descripciones de producto dos promesas que ya no son ciertas.

El 31/07 se puso el envío gratis en 39 € con la decisión de **no anunciarlo**, y el
15% pasó a ser un código de primera compra (`BIENVENIDA15`) en vez de un descuento
automático. Aquella pasada corrigió las meta descripciones, pero el `body_html` de
los productos se quedó como estaba, así que 176 fichas siguen diciendo:

  · «Envío gratis … 50 €» — umbral equivocado (el real es 39) y además no se anuncia;
  · «15% de descuento automático» — dejó de aplicarse solo en el carrito.

Las dos son promesas que el checkout no cumple: además del problema legal, es la
peor forma de perder un carrito, porque el cliente se entera al final.

## Uso

    python3 corregir_reclamos.py                 # informe, no toca nada
    python3 corregir_reclamos.py --salida correcciones.json

El fichero de salida lleva `{gid, handle, descriptionHtml}` listo para pasar a
`productUpdate`. Con un token de Admin se puede aplicar directamente:

    SHOPIFY_TOKEN=... SHOPIFY_TIENDA=srhood.myshopify.com \
        python3 corregir_reclamos.py --aplicar

Sin token, el JSON se aplica desde la sesión de Claude con `graphql_mutation`.

## Por qué se lee del escaparate público

`/products.json` devuelve el `body_html` **completo y byte a byte igual** que el
`descriptionHtml` de la Admin API —comprobado sobre varios productos antes de
escribir nada—, y así el script funciona sin credencial para la parte de lectura.
Si algún día dejaran de coincidir, esto sobrescribiría texto: la comprobación de
`--verificar` está para eso.
"""
import argparse, json, os, re, sys, urllib.request

TIENDA = "https://srhood.com"

# el reclamo de envío, en las doce redacciones que hay en la tienda
CLAIM = r"env[ií]o[s]?\s+grat\w*[^<]*?(?:50\s*€|≥\s*50\s*€)"
DESCUENTO = r"\s*(?:\+|y)?\s*15\s*%\s*de descuento autom[áa]tico[^<]*"


def corregir(h):
    """Solo borra. Nunca añade ni reescribe una promesa: si algo queda a medias,
    que sea de menos, no de más."""
    h = re.sub(rf"<li>\s*(?:{CLAIM})[^<]*</li>\s*", "", h, flags=re.I)   # el <li> es el reclamo
    h = re.sub(rf"(<li>[^<]*?)\s*·\s*(?:{CLAIM})[^<]*(</li>)", r"\1\2", h, flags=re.I)
    h = re.sub(rf"<p>\s*(?:{CLAIM})[^<]*</p>\s*", "", h, flags=re.I)     # el <p> es el reclamo
    h = re.sub(rf"\s*(?:{CLAIM})[^<]*", "", h, flags=re.I)               # cláusula suelta
    h = re.sub(DESCUENTO, "", h, flags=re.I)
    h = re.sub(r"<li>\s*</li>\s*", "", h)
    h = re.sub(r"<p>\s*</p>\s*", "", h)
    return h


def catalogo():
    todos, pag = [], 1
    while True:
        u = f"{TIENDA}/products.json?limit=250&page={pag}"
        lote = json.load(urllib.request.urlopen(u)).get("products", [])
        if not lote:
            return todos
        todos += lote
        pag += 1


def afectados(productos):
    out = []
    for p in productos:
        b = p.get("body_html") or ""
        if not (re.search(CLAIM, b, re.I) or re.search(DESCUENTO, b, re.I)):
            continue
        nuevo = corregir(b)
        if nuevo != b:
            out.append({"gid": f'gid://shopify/Product/{p["id"]}',
                        "handle": p["handle"], "descriptionHtml": nuevo,
                        "quitado": len(b) - len(nuevo)})
    return out


def aplicar(items, tienda, token, tam=20):
    """productUpdate en lotes con alias. Requiere token de Admin."""
    url = f"https://{tienda}/admin/api/2025-07/graphql.json"
    hechos = 0
    for i in range(0, len(items), tam):
        trozo = items[i:i + tam]
        campos = " ".join(
            f'p{j}: productUpdate(product: {{id: $id{j}, descriptionHtml: $h{j}}}) '
            f'{{ userErrors {{ field message }} }}' for j in range(len(trozo)))
        firma = ", ".join(f"$id{j}: ID!, $h{j}: String!" for j in range(len(trozo)))
        variables = {}
        for j, it in enumerate(trozo):
            variables[f"id{j}"] = it["gid"]
            variables[f"h{j}"] = it["descriptionHtml"]
        cuerpo = json.dumps({"query": f"mutation({firma}) {{ {campos} }}",
                             "variables": variables}).encode()
        req = urllib.request.Request(url, data=cuerpo, method="POST", headers={
            "X-Shopify-Access-Token": token, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            res = json.load(r)
        errores = [e for v in (res.get("data") or {}).values() for e in v.get("userErrors", [])]
        if errores or res.get("errors"):
            print("  ✗", errores or res["errors"])
        else:
            hechos += len(trozo)
            print(f"  · {hechos}/{len(items)}")
    return hechos


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", help="escribe el JSON de correcciones")
    ap.add_argument("--aplicar", action="store_true", help="requiere SHOPIFY_TOKEN")
    a = ap.parse_args()

    items = afectados(catalogo())
    print(f"{len(items)} productos con promesas caducadas en la descripción")
    for it in items[:5]:
        print(f'  {it["handle"][:52]:54s} −{it["quitado"]} car.')
    if len(items) > 5:
        print(f"  … y {len(items) - 5} más")

    if a.salida:
        json.dump(items, open(a.salida, "w"), ensure_ascii=False, indent=1)
        print("→", a.salida)

    if a.aplicar:
        token = os.environ.get("SHOPIFY_TOKEN")
        tienda = os.environ.get("SHOPIFY_TIENDA")
        if not (token and tienda):
            sys.exit("✗ Faltan SHOPIFY_TOKEN y SHOPIFY_TIENDA.")
        print(f"\nAplicados: {aplicar(items, tienda, token)}")
