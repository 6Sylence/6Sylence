#!/usr/bin/env python3
"""
Sube los precios para absorber el envío y poder ofrecer envío gratis de verdad.

## De dónde salen las cifras

No de una intuición: de lo que Printful cobra realmente por enviar cada familia a
España, consultado contra `/shipping/rates` con dirección real (Murcia, 30110), un
artículo por pedido. El pedido medio de esta tienda es de **un artículo**, así que lo
que hay que absorber es la tarifa de primer artículo, no una media optimista.

    camiseta, gorra, gorro, bucket, bandana, calcetines, bolsa, riñonera, polo,
    chanclas, bañador, bikini ............................ 4,29 €  → +6 €
    hoodie, sudadera, sudadera con cremallera ............ 6,29 €  → +8 €
    jogger, pantalón, shorts, chaqueta, cortavientos ..... 5,99 €  → +8 €
    zapatillas .......................................... 8,99 €  → +11 €
    mochila ............................................ 11,49 €  → +14 €

La subida es el **menor euro entero que cubre el coste con el IVA incluido** (los
precios de la tienda llevan el 21% dentro, así que absorber 4,29 € de coste exige
subir 5,19 € de PVP). Se usa euro entero porque todos los precios acaban en ,95 y así
lo siguen haciendo sin tener que redondear a mano producto por producto.

## Lo que esto NO arregla

Sube el PVP de todas las unidades por el coste de **la primera**. En un pedido de dos
artículos se recauda de más —dos subidas de 6 € contra un envío real de 5,54 €—, y eso
es deliberado: convierte cada artículo extra en margen y es el incentivo correcto para
una tienda cuyo problema es el pedido de una sola pieza barata.

## Orden de ejecución, que importa

1. Subir precios (este script).
2. **Después** quitar el umbral de 39 € del perfil de envío.
3. **Después** corregir los textos de la tienda, que ya serán ciertos.

Al revés se regala el envío durante el rato que medie entre los pasos.

## Uso

    python3 reprecificar.py --plan                       # tabla, no toca nada
    python3 reprecificar.py --salida precios.json        # el mapa de cambios
    SHOPIFY_TOKEN=... SHOPIFY_TIENDA=srhood.myshopify.com \
        python3 reprecificar.py --aplicar
"""
import argparse, json, math, os, sys, urllib.request
from collections import Counter, defaultdict

TIENDA = "https://srhood.com"

# coste real de envío a España, 1 artículo, consultado a Printful
ENVIO = {
    "ZAPATILLAS": 8.99, "Zapatillas": 8.99, "Chanclas": 4.29,
    "Hoodie": 6.29, "Cropped Hoodie": 6.29, "Sudadera": 6.29,
    "Sudadera Cremallera": 6.29,
    "Camiseta": 4.29, "Camiseta Manga Larga": 4.29, "Camiseta de Tirantes": 4.29,
    "Polo": 4.29, "Jogger": 5.99, "Pantalón": 5.99, "Shorts": 5.99,
    "Chaqueta": 5.99, "Cortavientos": 5.99, "Gorra": 4.29, "Gorro": 4.29,
    "Bucket Hat": 4.29, "Bandana": 4.29, "Calcetines": 4.29, "Bolsa": 4.29,
    "Riñonera": 4.29, "Mochila": 11.49, "Bañador": 4.29, "Bikini": 4.29,
}
IVA = 1.21


def subida(coste):
    """Menor euro entero que cubre el coste una vez repercutido el IVA."""
    return math.ceil(coste * IVA)


def catalogo():
    todos, pag = [], 1
    while True:
        u = f"{TIENDA}/products.json?limit=250&page={pag}"
        lote = json.load(urllib.request.urlopen(u)).get("products", [])
        if not lote:
            return todos
        todos += lote
        pag += 1


def plan(productos):
    cambios, saltados = [], Counter()
    for p in productos:
        coste = ENVIO.get(p["product_type"])
        if coste is None:
            saltados[p["product_type"]] += 1
            continue
        s = subida(coste)
        for v in p["variants"]:
            viejo = float(v["price"])
            cambios.append({
                "producto": p["handle"], "tipo": p["product_type"],
                "variant_id": v["id"], "antes": round(viejo, 2),
                "despues": round(viejo + s, 2), "subida": s,
            })
    return cambios, saltados


def aplicar(cambios, tienda, token, tam=100):
    """productVariantUpdate por lotes con alias. Requiere token de Admin."""
    url = f"https://{tienda}/admin/api/2025-07/graphql.json"
    hechos = 0
    for i in range(0, len(cambios), tam):
        trozo = cambios[i:i + tam]
        campos = " ".join(
            f'v{j}: productVariantUpdate(input: {{id: $i{j}, price: $p{j}}}) '
            f'{{ userErrors {{ field message }} }}' for j in range(len(trozo)))
        firma = ", ".join(f"$i{j}: ID!, $p{j}: Money!" for j in range(len(trozo)))
        variables = {}
        for j, c in enumerate(trozo):
            variables[f"i{j}"] = f'gid://shopify/ProductVariant/{c["variant_id"]}'
            variables[f"p{j}"] = f'{c["despues"]:.2f}'
        cuerpo = json.dumps({"query": f"mutation({firma}) {{ {campos} }}",
                             "variables": variables}).encode()
        req = urllib.request.Request(url, data=cuerpo, method="POST", headers={
            "X-Shopify-Access-Token": token, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:
            res = json.load(r)
        errores = [e for v in (res.get("data") or {}).values()
                   for e in v.get("userErrors", [])]
        if errores or res.get("errors"):
            print("  ✗", (errores or res["errors"])[:2])
        else:
            hechos += len(trozo)
            print(f"  · {hechos}/{len(cambios)}")
    return hechos


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--salida")
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()

    prods = catalogo()
    cambios, saltados = plan(prods)
    print(f"{len(prods)} productos · {len(cambios)} variantes a reprecificar")
    if saltados:
        print("sin tarifa conocida (no se tocan):", dict(saltados))

    if a.plan:
        por_tipo = defaultdict(lambda: [0, 0])
        for c in cambios:
            por_tipo[c["tipo"]][0] += 1
            por_tipo[c["tipo"]][1] = c["subida"]
        for t, (n, s) in sorted(por_tipo.items(), key=lambda x: -x[1][0]):
            print(f"  {t:22s} {n:5d} variantes  +{s} €")

    if a.salida:
        json.dump(cambios, open(a.salida, "w"), ensure_ascii=False)
        print("→", a.salida, "(guarda este fichero: es el mapa para revertir)")

    if a.aplicar:
        token, tienda = os.environ.get("SHOPIFY_TOKEN"), os.environ.get("SHOPIFY_TIENDA")
        if not (token and tienda):
            sys.exit("✗ Faltan SHOPIFY_TOKEN y SHOPIFY_TIENDA.")
        print(f"\nAplicados: {aplicar(cambios, tienda, token)}")
