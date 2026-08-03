#!/usr/bin/env python3
"""
Construye las fichas de la cápsula de estampado integral.

## De dónde sale cada dato

Nada aquí está inventado, y eso importa porque una ficha de ropa que miente en la
composición o en las tallas genera devoluciones:

  · **Composición y medidas de la prenda** → descripción del producto de catálogo de
    Printful (`/v2/catalog-products/{id}`), traducida.
  · **Guía de tallas** → `/v2/catalog-products/{id}/sizes?unit=cm`. Ojo: unas son
    medidas **del cuerpo** (`measure_yourself`) y otras **de la prenda**
    (`product_measure`). Decir «pecho 100 cm» significa cosas distintas en cada caso,
    así que el encabezado de la tabla cambia según el tipo.
  · **Coste unitario** → `/orders/estimate-costs` con dirección real de Murcia, talla
    M, `stitch_color: black`. Va al campo `inventoryItem.cost` para que el margen se
    vea en los informes de Shopify sin tener que recalcularlo a mano.
  · **SKU** → `PF` + el `catalog_variant_id` de Printful, que es el patrón que usan
    las fichas de la tienda que sí se fabrican (el pedido #1001 se sirvió con
    `PF4011`).

## El argumento de venta, que es uno solo

La tienda ya vende estas mismas cápsulas estampadas en un rectángulo en el pecho. Lo
que justifica el precio de éstas es que **el patrón cubre la prenda entera**. Todo lo
demás de la ficha es soporte de ese argumento.

## Uso

    python3 crear_aop.py --plan                 # tabla resumen
    python3 crear_aop.py --salida aop.json      # entradas para productSet
"""
import argparse, json, os

AQUI = os.path.dirname(os.path.abspath(__file__))

CAPSULAS = {
    "brocado": dict(
        nombre="Brocado", sub="Seda Real", tag="brocado-real", color="Negro y oro",
        intro="El damasco que vestía a las casas reales, llevado a la calle. Retícula "
              "ojival a media caída, palmeta de hojas acantadas y una corona en cada "
              "cruce, en oro sobre negro."),
    "malaquita": dict(
        nombre="Malaquita", sub="Piedra Real", tag="malaquita-real", color="Verde mineral",
        intro="La malaquita crece en capas alrededor de un núcleo, y donde se encuentran "
              "dos crecimientos aparece una sutura. Este estampado se dibuja igual: "
              "bandas concéntricas de verde mineral que nunca caen dos veces igual."),
    "meandro": dict(
        nombre="Meandro", sub="Laberinto Real", tag="meandro-real", color="Negro y oro",
        intro="La greca griega, el motivo que lleva tres mil años sin pasar de moda. "
              "Espirales cuadradas encadenadas por un raíl continuo, oro sobre negro, "
              "sin principio ni final."),
    "camo": dict(
        nombre="Camo", sub="Camuflaje Coronado", tag="camo-real", color="Verde y arena",
        intro="Camuflaje en la paleta de la casa: negro, oliva, esmeralda y arena. Y si "
              "miras de cerca, hay coronas escondidas entre las manchas."),
    # ── Segunda tanda. Se eligieron por color, no por motivo: la primera son dos
    # oros sobre negro, un verde y un camuflaje, así que en la cuadrícula de
    # colección se leían como una sola familia oscura. Estas cuatro abren la
    # paleta —burdeos, cobalto sobre crema, oro sobre negro y tinta sobre hueso—
    # y traen el primer estampado claro del catálogo.
    "tartan": dict(
        nombre="Tartán", sub="Herencia Real", tag="tartan-real", color="Burdeos y oro",
        intro="El tartán es un apellido tejido: cada casa tenía el suyo y las bandas se "
              "contaban como se cuenta un linaje. Este es el de la nuestra —burdeos de "
              "fondo, bandas negras, filetes en crema y oro— con la sarga diagonal "
              "marcada, como en la lana de verdad."),
    "azulejo": dict(
        nombre="Azulejo", sub="Cerámica Real", tag="azulejo-real", color="Cobalto y crema",
        intro="Cobalto sobre crema, el azul que llegó a Andalucía desde Persia y se quedó "
              "en los zócalos de los patios. Octagrama, rosetón en cada vértice y una "
              "corona en el centro de cada baldosa. Es el primer estampado claro de la "
              "casa: el único que se lleva de día sin pedir permiso."),
    "eslabon": dict(
        nombre="Eslabón", sub="Cadena Real", tag="eslabon-real", color="Negro y oro",
        intro="La cadena de oro es el emblema más honesto del streetwear: se lleva a la "
              "vista y dice exactamente lo que quiere decir. Aquí deja de ser un accesorio "
              "y pasa a ser el tejido —eslabones ovalados entrelazados, con su bisel y su "
              "brillo, cubriendo la prenda entera."),
    "suminagashi": dict(
        # Ojo: la colección de esta cápsula filtra por `suminagashi` a secas, no por
        # `suminagashi-real`. Las cuatro colecciones ya existían con seis productos
        # cada una, así que estas piezas entran solas en la cápsula que les toca —
        # pero solo si la etiqueta coincide exactamente con la regla.
        nombre="Suminagashi", sub="Tinta al Agua", tag="suminagashi",
        color="Hueso y tinta",
        intro="Suminagashi es «tinta flotante»: se deja caer una gota en agua quieta y se "
              "recoge en papel la figura que el agua le da. Nunca sale dos veces igual. "
              "Tinta sobre hueso, línea finísima, sin un solo color más. Lo más callado "
              "que ha hecho la casa, y por eso lo más difícil de ignorar."),
    # ── Tercera tanda: las dos primeras cápsulas dibujadas con jerarquía de tres
    # escalas y trazo de grosor variable. Y las dos primeras que salen en **dos
    # colorways**, que es como trabaja de verdad una marca de moda: el mismo
    # dibujo cambiado de paleta multiplica la colección sin repetir el trabajo.
    "barroco": dict(
        nombre="Barroco", sub="Cartela Real", tag="barroco-real", color="Negro y oro",
        intro="Una cartela de damasco entera: el cuerpo ojival de la granada con sus "
              "escamas, dos hojas de acanto dentadas envolviéndolo y la corona en la "
              "cima. Está dibujado a tres escalas —la cartela, la palmeta de relleno y "
              "una trama diagonal de fondo que solo se ve de cerca— para que la prenda "
              "funcione igual a un metro que en la mano."),
    "barroco-vino": dict(
        nombre="Barroco Vino", sub="Cartela Real", tag="barroco-real",
        color="Burdeos y oro",
        intro="La misma cartela de damasco, en burdeos profundo con el oro encima y las "
              "coronas en crema. El negro es el uniforme de la casa; el vino es para "
              "cuando el uniforme se queda corto."),
    "piton": dict(
        nombre="Pitón", sub="Piel Real", tag="piton-real", color="Oro y oliva",
        intro="Escamas que se solapan como tejas, cada una con su canto de luz, y encima "
              "las manchas de silla que dibuja la piel de un pitón. Dos escalas en una: "
              "de cerca se cuentan las escamas, de lejos se leen las manchas."),
    "piton-hueso": dict(
        nombre="Pitón Hueso", sub="Piel Real", tag="piton-real", color="Hueso y topo",
        intro="La misma piel, decolorada. Escama sobre escama en hueso y topo, sin una "
              "gota de color. Es la versión que se lleva de día y con vaquero claro."),
}

PRENDAS = {
    "388": dict(
        prenda="Hoodie", tipo="Hoodie", precio="84.95", coste="44.94",
        ficha="{c}-388-2362x2362.jpg",
        specs=["96% poliéster reciclado y 4% elastano · 308 g/m²",
               "Tacto algodón por fuera, forro polar cepillado por dentro",
               "Capucha de doble capa, estampada por las dos caras",
               "Corte unisex relajado",
               "Cortado y cosido a mano después de imprimir"]),
    "320": dict(
        prenda="Sudadera", tipo="Sudadera", precio="74.95", coste="36.94",
        ficha="{c}-320-1983x2598.jpg",
        specs=["96% poliéster reciclado y 4% elastano · 308 g/m²",
               "Tacto algodón por fuera, forro polar cepillado por dentro",
               "Corte unisex regular",
               "Cortada y cosida a mano después de imprimir"]),
    "618": dict(
        prenda="Pantalón", tipo="Jogger", precio="69.95", coste="33.74",
        ficha="{c}-618-3307x3189.jpg",
        specs=["100% poliéster · 75 g/m², ligero y resistente al agua",
               "Forrado con malla",
               "Cintura y tobillos elásticos, con cordón",
               "Bolsillos con cremallera",
               "Corte relajado"]),
    "744": dict(
        prenda="Bandolera", tipo="Riñonera", precio="44.95", coste="24.58",
        ficha="{c}-744-886x591.jpg",
        specs=["100% poliéster · 305 g/m², resistente al agua",
               "14,5 × 19,5 × 5 cm · 1,4 litros",
               "Bolsillo interior y exterior",
               "Correa ajustable de 88 a 160,7 cm",
               "Cremallera de doble carro"]),
    "200": dict(
        prenda="Crop Top", tipo="Camiseta", precio="39.95", coste="20.57",
        ficha="{c}-200-2421x1240.jpg",
        specs=["75% poliéster reciclado y 25% elastano · 225 g/m²",
               "Elasticidad en cuatro direcciones",
               "Ajuste ceñido",
               "Cortado y cosido a mano después de imprimir"]),
}

CDN = "https://cdn.shopify.com/s/files/1/1003/6874/4832/files/"


def tabla(pid, tallas):
    """Tabla de tallas. El encabezado distingue medida de cuerpo de medida de prenda:
    decir «pecho 100 cm» no significa lo mismo en un caso que en el otro."""
    t = tallas[pid]
    if not t["filas"]:
        return ""
    cols = [c for c in t["cols"] if any(c in f for f in t["filas"].values())]
    cuerpo = t["tipo"] == "measure_yourself"
    titulo = "Guía de tallas — medidas del cuerpo (cm)" if cuerpo else \
             "Guía de tallas — medidas de la prenda (cm)"
    ES = {"Chest": "Pecho", "Waist": "Cintura", "Hips": "Cadera",
          "Waistband": "Cintura", "Inseam": "Tiro interior",
          "A": "Ancho", "B": "Alto", "C": "Fondo"}
    th = "".join(f"<th>{ES.get(c, c)}</th>" for c in cols)
    filas = ""
    for talla, med in t["filas"].items():
        tds = "".join(f'<td>{float(med[c]):.0f}</td>' for c in cols if c in med)
        filas += f"<tr><td>{talla}</td>{tds}</tr>"
    nota = ("Entre dos tallas, elige la mayor para un fit holgado."
            if cuerpo else "Medidas tomadas en plano; pueden variar hasta 5 cm.")
    return (f"<h3>{titulo}</h3><table><tr><th>Talla</th>{th}</tr>{filas}</table>"
            f"<p><em>{nota}</em></p>")


def ficha(clave, pid, tallas):
    cap, pr = CAPSULAS[clave], PRENDAS[pid]
    titulo = f'{pr["prenda"]} Integral {cap["nombre"]} — {cap["sub"]}'
    specs = "".join(f"<li>{s}</li>" for s in pr["specs"])
    desc = (
        f'<p>{cap["intro"]}</p>'
        f'<p><strong>Estampado integral:</strong> el patrón cubre la prenda entera '
        f'—delantero, espalda y mangas— y sigue en las costuras. No es un rectángulo '
        f'impreso en el pecho: la pieza se corta ya estampada y se cose después.</p>'
        f'<ul>{specs}</ul>'
        f'<p>Producción bajo demanda. Cuando una cápsula cierra, no vuelve. '
        f'Envío gratis a toda España.</p>'
        + tabla(pid, tallas))
    seo_d = (f'{titulo}. Estampado integral que cubre la prenda entera, no un estampado '
             f'en el pecho. Producción bajo demanda, envío gratis. SRHOOD.')[:320]
    return dict(
        clave=f"{clave}-{pid}", titulo=titulo, tipo=pr["tipo"], precio=pr["precio"],
        coste=pr["coste"], descripcion=desc,
        seo_titulo=f'{titulo} | SRHOOD'[:70], seo_desc=seo_d,
        fichero=CDN + pr["ficha"].format(c=clave),
        tags=sorted({cap["tag"], "estampado-integral", "SRHOOD", "streetwear",
                     "unisex", pr["prenda"].lower(), cap["nombre"].lower()}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tallas", default="tallas-aop.json")
    ap.add_argument("--variantes", default="variantes-aop.json")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--salida")
    a = ap.parse_args()

    tallas = json.load(open(a.tallas))
    variantes = json.load(open(a.variantes))

    fichas = []
    for pid in PRENDAS:
        for clave in CAPSULAS:
            f = ficha(clave, pid, tallas)
            f["variantes"] = [{"talla": v["talla"], "sku": v["sku"]}
                              for v in variantes[pid]]
            fichas.append(f)

    if a.plan:
        print(f'{"producto":46s} {"PVP":>7s} {"coste":>7s} {"margen":>7s} {"var":>4s}')
        for f in fichas:
            m = float(f["precio"]) - float(f["coste"])
            print(f'{f["titulo"][:46]:46s} {f["precio"]:>7s} {f["coste"]:>7s} '
                  f'{m:7.2f} {len(f["variantes"]):4d}')
        print(f'\n{len(fichas)} fichas · '
              f'{sum(len(f["variantes"]) for f in fichas)} variantes')

    if a.salida:
        json.dump(fichas, open(a.salida, "w"), ensure_ascii=False, indent=1)
        print("→", a.salida)
