# Run 2026-07-16 (2ª sesión) — Cápsula Heritage: ampliar categorías flojas de ropa/calzado

Petición del usuario: ampliar las categorías de ropa y calzado con pocos productos,
con productos nuevos y únicos, sin repetir diseños.

## Diagnóstico (productos ACTIVOS por tipo)
Bien surtidas: Camiseta 64, Bañador 41, Jogger 40, Bikini 39, Hoodie 34, ZAPATILLAS 34.
Flojas → ampliadas hoy: Leggings 0→1, ZAPATOS 0→1, Calcetines 1→2, Cropped Hoodie 2→3,
Polo 3→4, Camiseta de Tirantes 4→5, Camiseta Manga Larga 6→7.
(Otras aún a 0: Camisa, Jersey, Top Deportivo, Boxers — POD limitado, quedan para otro drop.)

## Productos creados (todos ACTIVE, publicados en los 5 canales, con SKU y SEO)
1. Polo Piqué Tipping — Navy · 34,95 € · gid://shopify/Product/15839768019328
2. Camiseta Manga Larga Coordenadas — Negro · 32,95 € · 15839768084864
3. Camiseta de Tirantes Spine — Negro · 24,95 € · 15839768150400 (2 imágenes: espalda+frontal)
4. Cropped Hoodie Láurea — Crema · 44,95 € · 15839768248704
5. Leggings Pinstripe SRH — Negro · 39,95 € · 15839768281472
6. Calcetines Crew Crown Stripe — Blanco (Pack 2) · 12,95 € · 15839768314240
7. Zapatillas Slip-On Micro-Corona — Negro · 59,95 € · 15839768412544 (tipo ZAPATOS,
   estrena la subcategoría de calzado vacía; entró además en "Zapatillas Bajas & Slip-On")

Prints nuevos no usados antes: tipping heráldico, coordenadas Madrid + manga vertical,
spine ROYALTY en espalda, láurea burdeos, pinstripe monograma SRH, crown-stripe de
calcetín, patrón all-over micro-corona.

## Técnica
- `store-assets/capsula_heritage.py`: renderizador flat-lay de prendas (PIL+numpy):
  fondo estudio con degradado, sombra proyectada, sombreado de tejido (gradiente +
  ruido + sombra interior de borde), costuras discontinuas, canalé, y prints
  compuestos. 8 imágenes 1600×1600.
- Los tipos de producto se eligieron EXACTOS a las reglas de las smart collections
  (Polo, Camiseta Manga Larga, Camiseta de Tirantes, Cropped Hoodie, Leggings,
  Calcetines, ZAPATOS) → clasificación automática correcta.
- Tags de género (unisex/mujer/hombre) para las colecciones Mujer/Hombre.
- Recordatorio: productos creados por API NO se publican solos → publishablePublish
  a las 5 publicaciones (IDs en memory/2026-07-16-store-run.md).

## Pendiente / nota
- Estos 7 productos tampoco están conectados a Printful (fulfillment manual si hay
  pedido). Las imágenes son ilustración editorial de catálogo, no fotografía.
- Categorías aún a 0 si se quiere seguir ampliando: Camisa, Jersey, Top Deportivo, Boxers.
