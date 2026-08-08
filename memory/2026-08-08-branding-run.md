# Run 2026-08-08 — Branding: portadas de marca para las 32 cápsulas

Tienda: Street Royalty Hood (srhood.com) · Tarea programada: "Mejora el branding de nuestra tienda"

## Estado detectado
- Las colecciones principales (Ropa, Calzado, Camisetas, Hombre/Mujer, drops, etc.) ya
  tenían portadas de marca uniformes (`brand-cover-*.jpg`: lienzo negro, marco dorado,
  icono line-art, tipografía serif crema) de runs anteriores.
- 32 colecciones de cápsulas y líneas seguían usando fotos de mockup POD crudas
  (`unisex-premium-pullover-hoodie-*.jpg`, `mens-high-top-canvas-shoes-*.jpg`, previews
  PNG) como portada → rejilla de colecciones incoherente, la mayor fuga de branding
  visible que quedaba.

## Acciones realizadas
1. Nuevo generador `store-assets/capsule_covers.py` (PIL, 1600×1600): reproduce el
   sistema visual de las portadas existentes (fondo negro con patrón SRHOOD, marco
   dorado con diamantes, regla dorada, título serif, subtítulo y pie tracked) con un
   icono line-art dorado único por cápsula (media luna, telar, boteh, rosetón,
   guilloché, kintsugi, meandro, etc.).
2. Generadas y subidas las 32 portadas vía `stagedUploadsCreate` + `fileCreate`
   (MediaImage 70050192851328 … 70050193867136, todas READY).
3. Asignada cada portada a su colección con alt text descriptivo
   ("Portada de la Cápsula X — … de Street Royalty Hood"). Colecciones actualizadas:
   Serie Nocturna, Telar, Déco, Pañuelo, Azulejo, Forma & Color, Cianotipo,
   Suminagashi, Relieve, Nube Imperial, Salpicadura, Línea Vía, Línea Moiré,
   Línea Estática, Línea Trazo, Observatorio, Vidriera, Neón, Guilloché, Plumaje,
   Kintsugi, Frecuencia, Baraja, Laurel, Camo Real, Eslabón, Tartán, Forja, Brocado,
   Malaquita, Meandro y Marquetería.
4. Verificado en CDN: Shopify reemplaza el contenido conservando el nombre de archivo
   antiguo con nuevo parámetro `?v=` — el contenido servido ya es la portada de marca
   (comprobado descargando Serie Nocturna y Tartán).

## Resultado
Las ~50 colecciones publicadas de la tienda comparten ahora el mismo sistema visual de
portada. Con esto, la rejilla de colecciones, los enlaces compartidos (og:image de
colección) y la navegación por cápsulas quedan 100% con imagen de marca.

## Pendiente / ideas para próximos runs
- El campo `shop.brand` (logo/colores/eslogan a nivel de tienda) no existe en esta
  versión del Admin API — logo y favicon siguen siendo cosa del tema (admin).
- Los iconos de cápsula podrían reutilizarse como badges en fichas de producto o en
  el blog de drops.
