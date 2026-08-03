# Bases de estampado integral sin explotar

Printful tiene **103 productos cut-sew** en catálogo. SRHOOD usa **cinco**. Este
fichero deja hechos los deberes para las cuatro siguientes: variantes, colocaciones,
medidas de impresión, estilos de mockup y **coste real consultado**, para que montar
la tanda sea ejecutar el mismo guion de siempre y no volver a investigar.

## Las cuatro elegidas y por qué

| Base | Qué es | Por qué esta |
|---|---|---|
| **390** | Bomber Jacket | La prenda de más valor percibido del streetwear. Es la que sostiene un PVP de tres cifras |
| **659** | Button Shirt | **La camisa es *la* prenda del estampado integral.** Es donde un damasco o un pitón se leen enteros, sin capucha ni bolsillo cortando el dibujo |
| **644** | Sports Jersey | Cinco estilos de mockup con modelo, los que más de todo el catálogo |
| **654** | Reversible Bucket Hat | Accesorio de tendencia, y **reversible**: admite un patrón por fuera y otro por dentro, o sea dos cápsulas en una pieza |

## Coste real y precio propuesto

Consultado a `/orders/estimate-costs` con dirección de Murcia, talla media,
`stitch_color: black`. **Coste = `subtotal` + `shipping`, sin IVA** — comprobado
contra el hoodie 388, que da 38,95 + 5,99 = 44,94 € y coincide con la ficha.

| Base | Coste | PVP | Margen | Múltiplo |
|---|---|---|---|---|
| 390 Bomber | 52,44 € | 99,95 € | +47,51 € | 1,91 |
| 659 Camisa | 38,31 € | 74,95 € | +36,64 € | 1,96 |
| 644 Jersey | 31,24 € | 59,95 € | +28,71 € | 1,92 |
| 654 Bucket hat | 26,03 € | 49,95 € | +23,92 € | 1,92 |

El múltiplo de referencia es el del hoodie integral: 84,95 / 44,94 = **1,89**.

## Lo que cambia respecto a las cinco bases actuales

**Las colocaciones ya no miden todas lo mismo.** En hoodie, sudadera, pantalón,
bandolera y crop top un único fichero servía para todos los paneles. Aquí no:

| Base | Colocaciones | Medidas de impresión |
|---|---|---|
| 390 | front, back, sleeve_left, sleeve_right, details | 31×36 cm los cuatro primeros · **details 53×18** |
| 659 | front, back, details, sleeve_left, sleeve_right, inside_yoke | 38×50 los tres primeros · **mangas y canesú 38×20** |
| 644 | front, back, sleeve_left, sleeve_right | 33×45 · **mangas 33×15** |
| 654 | outside_front, outside_back, inside_front, inside_back | 18×21 los cuatro |

O sea que 390, 659 y 644 necesitan **dos ficheros por cápsula**, no uno.
`patrones_aop.py --generar` ya lo resuelve solo: agrupa por medida y escribe un
fichero por grupo. Lo que hay que ampliar es `PRENDAS` en `crear_aop.py` y en
`vincular_aop.py`, que hoy asumen un sufijo único por prenda.

## Variantes de catálogo

| Base | Tallas | Ids |
|---|---|---|
| 390 | XS–3XL (7) | 10877 XS · 10878 S · 10879 M · 10880 L · 10881 XL · 10882 2XL · 10883 3XL |
| 659 | 2XS–6XL (11) | 17117 2XS · 17119 S · 16400 M · 17120 L · 17121 XL · 17122 2XL · 17123 3XL · 17124 4XL · 17125 5XL · 17126 6XL |
| 644 | 2XS–6XL (11) | 16258 2XS · 16260 S · 16261 M · 16262 L · 16263 XL · 16264 2XL · 16265 3XL · 16266 4XL · 16267 5XL · 16268 6XL |
| 654 | XS, S/M, L/XL (3) | 19255 XS · 16360 S/M · 16361 L/XL |

## Estilos de mockup verificados

    390 → 3023 (Lifestyle 1/Front), 3024 (Back), 20443 (Women's Lifestyle)
    659 → 4993 (Men's Lifestyle/Front), 4991 (Women's Lifestyle/Front)
    644 → 4724, 4731, 4732, 4733 (cuatro Lifestyle de hombre), 4727 (mujer)
    654 → 4883 (Men's Lifestyle/Front Outside), 4889 (Front Inside)

## Lo que queda del catálogo

Otros candidatos con foto de modelo, por si se quiere seguir: **279** mochila,
**507** biker shorts, **189** leggings, **604** wide-leg pants, **717** zip hoodie,
**801** track jacket. La lista completa de las 103 sale con:

    GET /v2/catalog-products?limit=100&offset=…   → filtrar techniques por cut-sew
