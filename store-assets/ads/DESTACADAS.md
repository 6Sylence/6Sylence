# Portadas de historias destacadas

Archivos: `out/srhood-destacada-01..10-*.png` — **1080 × 1920**, que es el formato que
Instagram acepta como portada.

**Por qué en vertical si el resultado es un círculo:** Instagram recorta el círculo inscrito
en el cuadrado central de la imagen. Todo el dibujo vive dentro de un radio de 440 px desde
el centro, así que nada se corta por muy justo que recorte la app, y el fondo va a sangre
para que el filo del círculo salga limpio y sin borde blanco.

Los glifos están **trazados con la misma línea de oro** que el guilloché de las planchas —
no son iconos importados de una librería, y por eso el conjunto pega con el feed.

## El set

| Archivo | Glifo | Nombre a escribir en Instagram |
|---|---|---|
| `01-capsulas` | corona maciza | **Cápsulas** |
| `02-novedades` | estrella de ocho puntas | **Novedades** |
| `03-looks` | greca / meandro | **Looks** |
| `04-tallas` | regla graduada | **Tallas** |
| `05-envios` | paquete | **Envíos** |
| `06-devoluciones` | flecha circular | **Devoluciones** |
| `07-faq` | interrogación en Italiana | **FAQ** |
| `08-la-casa` | monograma SR | **La Casa** |
| `09-contacto` | sobre | **Contacto** |
| `10-codigo` | etiqueta | **BIENVENIDA15** |

El nombre que escribas debajo va en **minúsculas o versalitas cortas** (máx. 10-12
caracteres, o Instagram lo corta con puntos suspensivos). El icono lleva el peso; el texto
solo desambigua.

## Cómo se ponen

1. Crea la destacada (o edítala): **Editar destacada → Editar portada**.
2. Icono de la foto → elige el PNG de la galería.
3. **No lo muevas ni hagas zoom**: ya viene centrado. Si lo tocas, se descoloca el anillo.
4. Escribe el nombre y guarda.

Si la destacada aún no existe, necesitas al menos una historia dentro para poder crearla —
sube cualquiera, créala, y luego cambia la portada.

## Orden recomendado

Instagram muestra las destacadas de izquierda a derecha por orden de última actualización,
así que para fijar el orden hay que **actualizarlas en orden inverso** (la que quieras
primera, la última que tocas).

Orden objetivo, de más comercial a más informativo:

```
Cápsulas · Novedades · Looks · BIENVENIDA15 · Tallas · Envíos · Devoluciones · FAQ · Contacto · La Casa
```

Las cuatro primeras son las que ve alguien que llega de un anuncio; las demás resuelven las
dudas que frenan la compra (talla, plazos, devoluciones), que en una tienda de producción
bajo demanda es justo donde se pierde la venta.

## Contenido sugerido de cada destacada

- **Cápsulas** — una historia por cápsula activa: la plancha del feed + un primer plano del
  estampado. Es tu catálogo navegable.
- **Novedades** — el último drop, con sticker de enlace al producto.
- **Looks** — combinaciones completas (hoodie + zapatilla + accesorio de la misma cápsula).
  Empuja el ticket medio, que es lo que más falta le hace a la tienda.
- **BIENVENIDA15** — cómo se aplica el código, con captura del checkout.
- **Tallas** — la tabla de medidas en plano, cápsula a cápsula.
- **Envíos** — plazos reales (producción 2-4 días + envío 3-5) y los gastos, tal como están
  en la página de Envíos. Sin promesas de gratuidad.
- **Devoluciones** — qué cubrimos (defecto, daño, error) y qué no (cambio de opinión, por
  ser producción bajo demanda). Explicarlo bien evita reclamaciones.
- **FAQ** — las preguntas de la página FAQ, una por historia.
- **Contacto** — srhood@srhood.com y tiempo de respuesta.
- **La Casa** — el manifiesto: qué es una cápsula, por qué bajo demanda, qué significa la
  corona.

## Regenerar

```
python3 build_highlights.py
```

Los glifos están en funciones `g_*()` al principio del script. Añadir uno nuevo es escribir
la función y una línea en la tabla `PORTADAS` con su acento cromático.
