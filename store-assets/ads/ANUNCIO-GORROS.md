# Anuncio de categoría — Tocados

Creatividades: `out/anuncios/srhood-anuncio-gorros-story.jpg` (1080×1920) y
`srhood-anuncio-gorros-feed.jpg` (1080×1350). Se regeneran con:

```bash
python3 build_anuncio.py --qa /tmp/qa.json
```

## Configuración

| | |
|---|---|
| **Objetivo** | Ventas, optimizando a **AddToCart** en frío (a Compra no sale de aprendizaje con un pedido de histórico) |
| **Llamada a la acción** | **Comprar** |
| **Destino** | `https://srhood.com/collections/gorras-gorros` — la colección, no la portada |
| **Ubicaciones** | Historias, Reels y Feed. El 9:16 y el 4:5 cubren las tres |
| **Público** | España peninsular + Baleares, 20-34, todos los géneros (ver el desglose de intereses que ya está definido) |

**Por qué el precio va en la imagen:** quien pulsa después de leer 24,95 € ya ha
aceptado el precio. Eso filtra el clic antes de pagarlo, y con un píxel sin datos
importa más la calidad del evento que el volumen.

## Texto principal — tres versiones para probar

Lo único visible antes del «…más» son los primeros ~125 caracteres. En las tres,
el gancho cabe entero ahí.

**A · Producto**
```
Lo primero que se ve de ti a diez metros.

Gorros de punto, buckets y gorras con la corona bordada en relieve. Talla única,
bordado denso que no se despega al tercer lavado.

Cada pieza se fabrica cuando la pides.
```

**B · Objeción**
```
Un bordado que se despega al tercer lavado no era un bordado.

El nuestro va en relieve, hilo sobre hilo, sobre punto acrílico grueso o lona de
algodón. Talla única con vuelta ajustable.

Gorros, buckets y gorras desde 24,95 €.
```

**C · Marca**
```
La corona no se pide. Se lleva — y se lleva en la cabeza.

Gorro, bucket o gorra: tres formas de rematar el mismo fit. Bordado en relieve,
talla única, producción bajo demanda en Europa.
```

## Titular (máx. 40 car.)

- `Gorros, buckets y gorras · desde 24,95 €` — el que yo pondría primero
- `La corona, bordada en relieve`
- `Talla única. Bordado que aguanta.`

## Descripción (máx. 30 car.)

`Producción bajo demanda` — a menudo Meta ni la muestra; no metas nada que
importe aquí.

## Texto alternativo

```
Tres tocados de SRHOOD sobre fondo oscuro con un grabado circular dorado: un
gorro bucket negro con la corona SRH bordada, un gorro de punto blanco con la
corona bordada en el vuelto, y una gorra caqui con el sello circular Hood Royalty
Club. Streetwear español, producción bajo demanda.
```

## Lo que este anuncio NO dice, y por qué

- **Nada de envío.** El umbral de 39 € no se anuncia (decisión del 31/07), y
  además el pie de la creatividad no promete de dónde sale el paquete: Printful
  asigna taller y eso no está verificado. Solo se afirma «producción bajo demanda
  en Europa», que es literalmente lo que declaran las fichas.
- **Nada de `BIENVENIDA15`.** Un gorro de 24,95 € con el 15% queda en 21,21 €, o
  sea 17,53 € netos de IVA. Con el coste de fabricación de un gorro bordado ahí no
  queda margen que defender. El código tiene su sitio en el retargeting de carrito
  abandonado, no en el anuncio de entrada.

## El problema que este anuncio crea, y cómo taparlo

Un anuncio que entra por 24,95 € trae **cestas de un solo artículo por debajo de
39 €**, que es exactamente donde la tienda pierde dinero: el envío del primer
artículo se lo come entero. El único pedido de la historia de la tienda fue eso
mismo — 21,21 €, una camiseta suelta.

Dos formas de taparlo, y conviene hacer las dos:

1. **El destino es la colección, no el producto.** Con 100 referencias delante, la
   probabilidad de segunda pieza sube mucho respecto a una ficha suelta.
2. **Cross-sell en la ficha.** «Completa el Look» ya existe como colección de 213
   productos; que aparezca en la ficha de los tocados es lo que convierte 26,95 €
   en 54 € y cruza el umbral sin tener que anunciarlo.

Si al mes el ticket medio sigue por debajo de 39 €, el problema no es el anuncio:
es que el catálogo de entrada es demasiado barato para el coste de envío, y eso se
arregla en el precio o en el umbral, no en la creatividad.
