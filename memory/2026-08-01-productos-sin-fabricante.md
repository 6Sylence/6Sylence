# 208 fichas a la venta sin nadie que las fabrique

Encontrado el 01/08/2026, y encontrado **porque Álvaro insistió**. Yo había concluido
que no se podían crear productos sin pasar por Printful; él dijo «hemos trabajado así
siempre». Tenía razón, y al ir a demostrarlo apareció esto.

## La comprobación que hice mal

Para ver si algún producto de la tienda había nacido fuera de Printful, crucé los IDs de
Shopify contra los `external_id` de los sync-products de Printful:

    Shopify 1303 · Printful 1303 · huérfanos 0

Y concluí que todo venía de Printful. **La prueba no valía nada.** Al crear un producto
de prueba en Shopify, Printful lo listó como sync-product **al instante**, con su
`external_id` puesto. Printful refleja el catálogo entero de la tienda, esté vinculado o
no. Tener registro en Printful no prueba absolutamente nada.

La bandera que sí sirve es **`catalog_variant_id` de la sync-variant**. Si es `null`, la
variante está `unsynced`: existe la ficha, se puede comprar, y no hay fabricante detrás.
`is_ignored` a nivel de producto es un buen primer filtro, pero hay que bajar a la
variante para confirmarlo — de 12 muestreados, 11 estaban rotos y 1 estaba bien.

    1303 productos · 582 sincronizados · 721 sin vincular
    De los 588 publicados: 208 sin vincular

## Lo que eso significa

Un cliente entra, paga 89,95 € por un bomber, y no hay nadie fabricándolo. No es un
riesgo teórico: son 208 fichas activas, con precio y botón de comprar.

**Y 131 de ellas son productos que estamos anunciando** en Instagram y Facebook. De los
287 publicados en redes, casi la mitad lleva tráfico a una ficha que no puede servir.
Cápsulas enteras: Marquetería, Meandro, Camo, Cifra. Y toda la línea Essential —bombers,
cortavientos, zapatillas, bañadores, bikinis—.

El único pedido real de la tienda (#1001, Camiseta Crown, servido) **sí estaba
vinculado**. El patrón se sostiene: lo vinculado se fabrica, lo demás no se fabricaría.

## La API sí lo puede arreglar — me equivoqué dos veces seguidas

Primero escribí que no se podía vincular por API. **También era falso.** Probé veinte
combinaciones alrededor de `/v2/sync-products` y `/v2/sync-variants`, todas fallan, y la
más reveladora es:

    PUT /v2/sync-variants/{id}?syncProductId=…&syncVariantId=…
    409 · "Cannot update the design of a sync variant with no catalog_variant_id"

Ese endpoint existe y responde, pero lee el `catalog_variant_id` del registro y no del
cuerpo: cambia el **diseño** de una variante ya vinculada, no crea el vínculo.

**Lo que sí funciona está en la v1**, en una familia de rutas que no había tocado:

    PUT /sync/variant/{sync_variant_id}
    PUT /sync/variant/@{external_id}          ← acepta el id de variante de Shopify

con `variant_id` (el de catálogo), `retail_price`, `is_ignored: false`, `files` y
`options`. Devuelve `synced: true` y el producto queda fabricable. Implementado en
`store-assets/ads/vincular_aop.py`.

**El error de método, que es el mismo dos veces:** generalicé de un endpoint a una API
entera. Que `/store/products` conteste «solo para tiendas de plataforma Manual Order»
dice algo sobre **crear** productos, no sobre **vincularlos** — son operaciones
distintas y viven en rutas distintas. Igual que antes di por buena una comprobación que
habría dado el mismo resultado aunque mi creencia fuese falsa.

**Consecuencia para los 208:** son arreglables por API, no hace falta el Creador de
productos. Álvaro dijo el 01/08 que los productos están bien y que no los toque, así que
**no se ha tocado ninguno**; queda anotado que la vía existe si algún día se quiere.

## Qué hacer, por orden de dinero protegido

1. **Los 208**: vincularlos en Printful → Sync products, o pasarlos a borrador mientras
   tanto. Pasarlos a borrador es un comando y es reversible.
2. **Parar los 131 anuncios** de productos que no pueden servir.
3. **Solo entonces** añadir los de estampado integral, bien vinculados de origen.

## La lección, que es la que vale para la próxima

Cuando una comprobación confirma lo que yo ya creía, hay que preguntarse qué mediría si
la creencia fuera falsa. La mía —«¿existe en Printful?»— habría dado el mismo resultado
en los dos mundos. Y cuando el dueño de la tienda contradice un dato mío sobre su propia
tienda, la respuesta correcta no es enseñarle la prueba otra vez: es dudar de la prueba.
