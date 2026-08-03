# Sistema visual de la tienda — imágenes de ficha

## La decisión de partida

Aplicar la plancha del anuncio como **imagen principal** de cada producto era la idea
obvia y es la equivocada, por dos motivos independientes que apuntan al mismo sitio.

**El técnico.** La tienda publica en Google & YouTube, TikTok, Facebook & Instagram e
Instagram Shop. Los cuatro toman la primera imagen del producto para su catálogo, y
las políticas de Google Merchant Center y de catálogos de Meta prohíben en esa imagen
texto promocional, marcos, bordes y marcas de agua. La plancha lleva las cuatro cosas:
precio, anillo, SRHOOD.COM y marcas de registro. Ponerla ahí haría que los artículos
se rechazaran en las cuatro superficies a la vez — incluida la que alimentaría los
anuncios de catálogo que hemos especificado.

**El de marca, que pesa más.** Mira quién decora la foto de producto y quién no:

| Marca | Imagen principal | Dónde ponen la marca |
|---|---|---|
| Aesop | Frasco sobre fondo liso, sin una letra | Tipografía y espacio en blanco de la página |
| Byredo | Producto centrado, fondo neutro constante | Repetición milimétrica del encuadre |
| Carhartt WIP | Prenda plana o fantasma sobre gris claro | Etiqueta cosida, lookbook aparte |
| Stüssy | Prenda sobre blanco, misma escala siempre | Editorial en secundarias y en campaña |
| Arc'teryx | Producto sobre blanco, tres cuartos fijo | Nomenclatura y ficha técnica |
| Nike | Producto sobre plano de color, sin overlay | Lifestyle en secundarias |
| **SHEIN, AliExpress, Temu** | **Collage con precio, flechas y sellos** | — |

La conclusión no es de gusto: **el overlay sobre foto de producto es el lenguaje del
descuento**. Las marcas caras dejan la foto desnuda y ponen la identidad en lo que se
repite —fondo, margen, escala, sombra, tipografía—. La coherencia es lo que se lee
como caro; el marco dorado sobre la ficha se leería como barato, que es exactamente lo
contrario de lo que busca esta marca.

## Las dos capas

**Imagen 1 · `principal` — apta para feed**
Producto recortado sobre hueso cálido (243,240,234) con viñeta muy leve, mismo margen,
**misma escala relativa por tipo de prenda**, y una sombra de contacto elíptica bajo la
pieza. Cero texto. 2048×2048.

La escala fija por tipo es lo que más trabaja: sin ella, en la cuadrícula de colección
una gorra sale del tamaño de una sudadera y el catálogo parece montado a trozos. Es el
detalle que separa una tienda cuidada de una improvisada, y no se nota hasta que está.

La sombra es una elipse difuminada, no un duplicado desplazado del producto. El
duplicado delata el recorte; la elipse se lee como apoyo sobre una superficie.

**Imagen 2 · `editorial` — la firma de la casa**
La plancha Heráldica Mineral en cuadrado: campo oscuro, roseta de guilloché, doble
anillo de oro, corona, titular en Italiana y línea de cápsula. Vive en la galería de la
ficha, donde ningún feed la mira.

**Sin precio, a diferencia de la del anuncio.** En el anuncio el precio cualifica el
clic y compensa; en la ficha, una imagen con el precio grabado se queda obsoleta en
cuanto cambia la tarifa y pasa a ser un precio anunciado que no coincide con el del
carrito. Ya hemos limpiado 61 fichas de esa clase de desajuste: no vamos a fabricarlo
de nuevo, y menos en un sitio donde corregirlo obliga a regenerar imágenes.

## Generar

```bash
python3 build_ficha.py --lote lotes/lote-03.json --salida out/fichas
```

Toma cualquier manifiesto ya preparado por `build_lote.py` —de ahí saca el recorte
calibrado, el acento cromático, el titular y la línea— y escribe dos JPEG por producto.

## Alcance real

De 588 productos publicados, **399 aguantan el recorte** con la escalera de umbrales
actual. Los otros 189 son piezas claras o de estampado blanco y negro que la
inundación destroza; para esas la imagen de Printful se queda como está hasta que
haya un recorte mejor.

A ~2 s por producto, las 399 son unos 15 minutos de render. Subirlas a Shopify va en
lotes de `productCreateMedia`, que solo mandan la URL y por tanto son baratas.

**Orden de despliegue recomendado:** primero las de las colecciones que reciben
tráfico (Gorras & Gorros, Completa el Look, las cápsulas activas), verificar cómo
queda la cuadrícula de colección de verdad, y solo entonces el resto. Cambiar 399
fichas de golpe sin mirar una rejilla real es como se estropean los catálogos.
