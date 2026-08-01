# Estampado integral — la cápsula que faltaba

Veinte ficheros de impresión listos, cuatro cápsulas × cinco prendas, verificados sobre
el producto real de Printful. Lo que falta para venderlos son unos minutos de clics que
la API no me deja dar; están explicados abajo, uno a uno.

## Lo que no se pudo hacer y por qué

**Printful no permite crear productos por API en una tienda conectada a Shopify.** No es
un permiso que falte ni un token: el endpoint lo dice literalmente.

    POST /store/products  →  400
    "This API endpoint applies only to Printful stores based on the
     Manual Order / API platform."

Lo comprobé también en `/v2/sync-products` (404 en la tienda de Shopify, y sí funciona
en la tienda nativa 18449429 — que no sincroniza con srhood.com, así que no sirve) y en
`/v2/product-templates` (se leen, no se crean). El producto tiene que nacer en el
Creador de productos de Printful, que es quien lo empuja a Shopify con sus variantes,
sus tallas y su vínculo de fabricación. Un producto creado a mano en Shopify **no se
fabricaría**: entraría el pedido y no habría nada al otro lado.

Así que el trabajo se ha hecho hasta el último paso automatizable, y ese último paso
está descrito para que lleve tres minutos por prenda.

## Y el estampado tampoco se podía recuperar

Los ficheros originales de las cápsulas no se pueden descargar. Printful devuelve el
campo `url` de cada capa **vacío** por las tres vías —`sync-variants`,
`product-templates` y la API v1— y la biblioteca de ficheros ya no existe (`/files` →
HTTP 410). No es un fallo: es cómo trata Printful a las tiendas de plataforma.

Por eso el estampado está **vuelto a dibujar** en `patrones_aop.py`, con la paleta de la
casa y la misma geometría que las planchas. No es una copia del original: es el mismo
motivo llevado a un formato que el original no tenía.

## Las cuatro cápsulas

| Cápsula | Qué es | Por qué esta |
|---|---|---|
| **Brocado — Seda Real** | Damasco: retícula ojival a media caída, palmeta acantada y corona | Es el motivo más «casa real» del catálogo y el que más gana al cubrir la prenda entera |
| **Malaquita — Piedra Real** | Bandas concéntricas alrededor de varios núcleos, como crece la piedra | Verde mineral: el único color fuerte de la marca que no es oro |
| **Meandro — Laberinto Real** | Greca griega encadenada, oro sobre negro | Geometría pura. Es el que más se lee de lejos, y el que mejor funciona en pantalón |
| **Camo — Camuflaje Coronado** | Camuflaje de cuatro tonos de la paleta, con coronas escondidas | Streetwear literal. El camuflaje **ya es** un estampado integral; tenerlo en pecho era el desperdicio más claro |

Las tres primeras las verifiqué sobre el hoodie real (`out/aop/SRHOOD-estampado-integral.jpg`).
El repetido de 16 cm da unas tres repeticiones de ancho de pecho, que era exactamente el
objetivo: se lee como diseño, no como fondo.

## Precios propuestos

Coste real consultado a Printful con envío a Murcia, talla M, `stitch_color: black`:

| Prenda | Base | Coste (con envío) | PVP | Margen |
|---|---|---|---|---|
| Sudadera integral | 320 | 36,94 € | **74,95 €** | +38,01 € |
| Hoodie integral | 388 | 44,94 € | **84,95 €** | +40,01 € |
| Pantalón integral | 618 | 33,74 € | **69,95 €** | +36,21 € |
| Bandolera integral | 744 | 24,58 € | **44,95 €** | +20,37 € |
| Crop top integral | 200 | 20,57 € | **39,95 €** | +19,38 € |

Son los márgenes más altos del catálogo: el hoodie premium actual deja +22,41 €, este
deja +40,01 €. El estampado integral cuesta bastante más de fabricar, pero admite un PVP
que la prenda lisa no admite, porque **no se compara con una sudadera estampada, se
compara con una prenda de firma**.

Dos avisos honestos:

- **Las tallas grandes cuestan más.** Una 3XL sube unos 8 €. A PVP plano el hoodie 3XL
  deja +37,41 € en vez de +40,01 €. Sigue siendo el mejor margen de la tienda, pero si
  algún día se venden muchas tallas grandes, conviene revisarlo.
- **Sudadera y pantalón forman conjunto.** 74,95 + 69,95 = 144,90 €. Ahí es donde tiene
  sentido un descuento de conjunto, no en la pieza suelta.

## Los ficheros

Están en `out/aop/`, veinte JPEG a 150 dpi y calidad 95 sin submuestreo de croma. El
nombre lo dice todo: `capsula-productoPrintful-anchoxalto.jpg`.

Dentro de una prenda **todas las colocaciones miden lo mismo** —el frontal, la espalda,
las dos mangas, la capucha y el bolsillo de un hoodie son 40 × 40 cm—, así que el mismo
fichero vale para las seis y solo hay que subirlo una vez. `indice.json` dice qué
colocaciones cubre cada uno.

Y ya están además en el CDN de la tienda, por si el Creador de productos acepta URL:

    https://cdn.shopify.com/s/files/1/1003/6874/4832/files/brocado-388-2362x2362.jpg
    https://cdn.shopify.com/s/files/1/1003/6874/4832/files/malaquita-388-2362x2362.jpg
    https://cdn.shopify.com/s/files/1/1003/6874/4832/files/meandro-388-2362x2362.jpg
    https://cdn.shopify.com/s/files/1/1003/6874/4832/files/camo-388-2362x2362.jpg

## Los tres minutos por prenda

1. Printful → **Product Maker** → busca el producto por su número de catálogo
   (320 sudadera, 388 hoodie, 618 pantalón, 744 bandolera, 200 crop top).
2. Elige **la tienda SRHOOD** (la de Shopify, no la nativa).
3. En cada colocación —frontal, espalda, mangas, capucha, bolsillo— sube el **mismo**
   fichero de esa cápsula y encájalo a sangre, cubriendo todo el panel.
4. Opción **`stitch_color`: black** en las cuatro cápsulas. Es obligatoria; si no la
   pones, ni el mockup ni el pedido salen.
5. Estilos de mockup: marca **Men's Lifestyle 2** y **Men's Lifestyle** — son los dos que
   verifiqué, con modelo real y foto editorial.
6. Precio: el de la tabla de arriba.
7. Título y colección: `Hoodie Integral Brocado — Seda Real`, y a la colección de su
   cápsula más «Novedades».

Empezaría por **el hoodie de Brocado**. Es el que mejor sale en la foto, el de mayor
margen, y el que mejor explica de un vistazo qué es esta marca.

## Si algún día se quiere ampliar

`patrones_aop.py` genera cualquier cápsula sobre cualquier producto: se añade la función
del motivo a `CAPSULAS`, se mete el producto en `spec-aop.json` y se vuelve a lanzar.
Quedan 21 cápsulas del catálogo sin llevar a estampado integral.

`comprobar()` mide si el mosaico cierra antes de escribir nada. Es la única prueba que
de verdad importa aquí: un patrón que no cierra deja una costura recta cada 16 cm y se
ve a un metro de distancia.
