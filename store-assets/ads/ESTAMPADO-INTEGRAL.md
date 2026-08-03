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
`/v2/product-templates` (se leen, no se crean).

> **Corrección importante (01/08, más tarde).** De aquí saqué la conclusión de que un
> producto creado en Shopify «no se fabricaría nunca», y **era falsa**. No se puede
> *crear* el producto por API, pero sí se puede **crear en Shopify y vincularlo después**,
> y el vínculo también es automatizable: está en la v1, en
> `PUT /sync/variant/{id}`. Los 20 productos se crearon con `productSet` y se
> vincularon con `vincular_aop.py`, sin pisar el Creador de productos.
>
> El error de método fue generalizar de un endpoint a una API entera: que
> `/store/products` conteste «solo para tiendas Manual Order» dice algo sobre **crear**
> productos, no sobre **vincularlos**, que es otra operación y vive en otra ruta.

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

---

## Actualización: los 20 productos están creados y publicados

Creados con `productSet` de la Admin API y publicados en los seis canales (Tienda
online, Shop, Google & YouTube, TikTok, Facebook & Instagram, Instagram Shop-AI). El
catálogo pasó de **588 a 608** productos publicados.

| Prenda | Cápsulas | PVP | Tallas |
|---|---|---|---|
| Hoodie Integral | Brocado, Malaquita, Meandro, Camo | 84,95 € | XS–3XL |
| Sudadera Integral | las cuatro | 74,95 € | XS–3XL |
| Pantalón Integral | las cuatro | 69,95 € | XS–3XL |
| Bandolera Integral | las cuatro | 44,95 € | única |
| Crop Top Integral | las cuatro | 39,95 € | XS–XL |

108 variantes en total. Cada una lleva su **SKU `PF` + `catalog_variant_id`** —el mismo
patrón que las fichas que ya se fabrican— y el **coste real de Printful** en
`inventoryItem.cost`, para que el margen salga solo en los informes de Shopify.

### Vinculados en Printful, también por API

Nacieron en Printful como `is_ignored: true` y `catalog_variant_id: null`, que es el
estado normal de un producto creado desde Shopify. **Ya no**: `vincular_aop.py` los
conecta con `PUT /sync/variant/{id}`, poniendo la variante de catálogo, el precio, la
opción `stitch_color` y el fichero de impresión en **todas** las colocaciones de cada
prenda.

El `variant_id` de catálogo no hay que buscarlo en ninguna tabla: está en el SKU. Las
fichas se crearon con `PF` + `catalog_variant_id` precisamente por esto, así que
`variant_id = int(sku[2:])` y no hay nada que mantener sincronizado a mano.

La API no puede dar ese paso: `PUT /v2/sync-variants` responde
`409 · Cannot update the design of a sync variant with no catalog_variant_id` —edita el
diseño de una variante ya conectada, no crea la conexión—. Comprobadas doce
combinaciones de ruta, método y carga.

### Un defecto que se cazó mirando, no midiendo

La primera tanda de bandoleras salió con **los laterales blancos**: había cubierto
`front`, `back` y `pocket`, pero no `details` ni `inside_pocket`, y esas dos son las
caras laterales de la bolsa. Ninguna comprobación automática lo habría dicho —la tarea
de mockup se completó sin error—. Regeneradas con las cinco colocaciones.

---

## Segunda tanda: cuatro cápsulas más (03/08)

Veinte fichas nuevas, 108 variantes. Las cuatro primeras cápsulas eran **dos oros
sobre negro, un verde y un camuflaje**: en la cuadrícula de colección se leían como
una sola familia oscura. Estas cuatro se eligieron por **color**, no por motivo.

| Cápsula | Paleta | Qué aporta |
|---|---|---|
| **Tartán — Herencia Real** | Burdeos, negro, crema, oro | El primer burdeos integral. Sett propio, con sarga diagonal |
| **Azulejo — Cerámica Real** | Cobalto sobre crema | **El primer estampado claro del catálogo.** Se lleva de día |
| **Eslabón — Cadena Real** | Oro sobre negro | La cadena deja de ser accesorio y pasa a ser el tejido |
| **Suminagashi — Tinta al Agua** | Tinta sobre hueso | Monocromo, línea finísima. Lo más callado de la casa |

Las cuatro **ya existían como cápsulas de la casa**, con su colección automática y
seis productos cada una. No hubo que crear ninguna colección: las fichas entran
solas por etiqueta. Con un matiz que costó encontrar — la regla de Suminagashi
filtra por `suminagashi` **a secas**, no por `suminagashi-real` como las otras tres.

### La costura: la métrica anterior se equivocaba en los dos sentidos

`comprobar()` comparaba el salto de la costura contra la media de todo el azulejo.
Esa referencia miente:

- **Falso positivo.** El suminagashi daba 2,82 y **no tenía nada roto**: es un
  patrón disperso —tinta fina sobre papel liso—, así que la media interior es
  minúscula y cualquier línea que pase por el borde dispara el ratio.
- **Falso negativo, que es el grave.** El azulejo daba 1,66, dentro del umbral,
  **teniendo una discontinuidad saturada de 175 sobre 255 en 90 filas**. La media
  global estaba inflada por los filetes de cobalto del interior de la baldosa y
  tapaba el salto.

La referencia correcta es **local**: los cuatro saltos inmediatamente a cada lado de
la costura. Una discontinuidad real destaca sobre su propia vecindad; el contenido
que casualmente cae en el borde, no. Con esa medida el azulejo roto marcaba **990**
y el suminagashi sano **1,31**.

El defecto del azulejo era este: el rosetón de la esquina se dibujaba como un
**cuarto** de círculo dentro de un lienzo anclado en el vértice. `pegar_envuelto`
**no puede envolver lo que nunca se dibujó** —los otros tres cuartos no existían—,
así que el borde izquierdo llevaba arco de cobalto y el derecho crema plana. Se
arregla dibujando el rosetón entero y pegándolo centrado en el vértice.

### Y el suminagashi tenía otro defecto, este solo visible mirando

Recortar la onda por umbral da líneas cuyo grosor depende de lo deprisa que suba la
fase: donde el campo se aplana la cresta se ensancha y la tinta se emborrona en
manchas que parecen suciedad de impresión. Se corrige dividiendo la distancia
angular a la cresta por el **módulo del gradiente**, que la convierte en distancia
en píxeles y deja el trazo del mismo grosor en todo el azulejo. El gradiente se
calcula con `np.roll` —exactamente periódico—; `np.gradient` no lo es y rompería la
costura que acabamos de arreglar.

Primer intento con 1,6 px: a 150 dpi son 0,27 mm y sobre tela se leía como papel en
blanco. Subido a 3,4 px (0,58 mm), el trazo de un pincel fino.

### Mockups, ahora automatizados

`mockups_aop.py` genera las 20 tandas de fotos con `source: catalog`, o sea **antes
de que la ficha exista en Shopify**. Eso permite crear el producto con sus fotos ya
puestas en vez de crearlo desnudo. Los estilos van elegidos a mano, uno por uno, y
la bandolera lleva el **plano de estudio como principal** a propósito: su estilo
«Lifestyle Front» fotografía al modelo de espaldas y la primera imagen de la ficha
no enseñaba el estampado.

### Precios y márgenes

Los mismos de la primera tanda, porque la base es la misma: hoodie 84,95 €,
sudadera 74,95 €, pantalón 69,95 €, bandolera 44,95 €, crop top 39,95 €. Siguen
siendo los mejores márgenes del catálogo, de +19,38 € a +40,01 €.

### Estado final de la segunda tanda

**216/216 variantes vinculadas y 376 ficheros de impresión en `ok`**, con las
colocaciones completas en las cinco prendas. El catálogo de estampado integral pasa
de 20 a **40 productos**: ocho cápsulas × cinco bases.

---

## Tercera tanda: dos cápsulas dibujadas de otra manera (03/08)

Veinte fichas más. El catálogo integral pasa de 40 a **60 productos**: doce cápsulas
× cinco bases.

Lo que cambia aquí no es el motivo, es **cómo está dibujado**. Las ocho primeras
cápsulas compartían dos limitaciones de oficio:

1. **Una sola escala.** Un patrón que repite el mismo motivo por toda la tela se
   convierte en color plano a un metro de distancia. Un estampado de firma tiene
   jerarquía: motivo dominante, relleno secundario y fondo con textura.
2. **Trazo de grosor constante.** Una línea de ancho fijo se lee como cable. El
   dibujo a mano engorda donde el pincel apoya y adelgaza donde levanta.

| Cápsula | Colorways | Qué prueba |
|---|---|---|
| **Barroco — Cartela Real** | oro sobre negro · oro sobre burdeos | Tres escalas: cartela, palmeta de relleno y trama diagonal de fondo. Todo con trazo de grosor variable |
| **Pitón — Piel Real** | oro y oliva · hueso y topo | Dos escalas y volumen real: escamas que se solapan como tejas, con canto de luz |

**Y estrena los colorways**, que es como trabaja de verdad una marca: el mismo
dibujo cambiado de paleta multiplica la colección sin repetir el trabajo de diseño.

### Tres errores de dibujo que costó ver

- **La espina de pescado.** El primer barroco dibujaba las hojas con trazo cónico
  —ancho al principio, punta al final—. Eso es un tallo, no una hoja: una hoja es
  panzuda. Con `trazo_perfilado()`, que describe el grosor punto a punto, y el
  perfil `sin(πt)^0,62`, la lámina aparece. Y hacen falta **dientes**: una lámina
  lisa de ese tamaño se lee como un plátano.
- **El plástico de burbujas.** Las escamas del pitón salían redondas y con un
  brillo en el centro. Agrandarlas dentro de su propia celda no solapa nada: las
  **recorta**, y la costura subió de 9,6 a 11,45. Un solape de verdad exige evaluar
  tres celdas candidatas —la propia y las filas de arriba y abajo— y quedarse con la
  que toca. Con eso desaparece el canto duro de cada fila y la costura baja a 0,80.
- **Los colorways son un riesgo de fabricación.** «barroco» es prefijo de
  «barroco-vino», y `clasificar()` buscaba subcadenas: todos los Barroco Vino se
  habrían fabricado con el fichero del Barroco negro, **sin ningún error visible**.
  Ahora se normaliza el separador y se prueba de clave más larga a más corta.

### Una observación honesta sobre el pitón

A escala de prenda entera —hoodie, sudadera, pantalón— las manchas de silla se leen
más como **camuflaje escamado** que como piel de serpiente, y la tienda ya tiene una
cápsula Camo. En bandolera y crop top sí se lee como pitón, porque el panel es
pequeño y cae dentro de una sola mancha. Se corrige agrandando el repetido solo para
esta cápsula; queda anotado, no hecho.

### Estado final de la tercera tanda

**324/324 variantes vinculadas y 376 ficheros nuevos en `ok`**, colocaciones
completas. El catálogo de estampado integral queda en **60 productos**: doce cápsulas
× cinco bases, 324 variantes fabricables.

Se comprobó además, **sobre los datos vivos de Printful**, qué fichero recibió de
verdad cada cápsula: `barroco → barroco`, `barroco-vino → barroco-vino`,
`piton → piton`, `piton-hueso → piton-hueso`, 94 ficheros cada una. Con colorways no
basta la prueba unitaria del clasificador: hay que mirar qué se mandó a fabricar.
