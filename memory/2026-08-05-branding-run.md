# Run 2026-08-05 — Branding: portadas de marca para colecciones core

Tienda: Street Royalty Hood (srhood.com) · Tarea programada: "Mejora el branding de nuestra tienda"

## Estado detectado
- Las 51 colecciones tienen descripción, SEO e imagen — pero solo las 3 más recientes
  (Bandanas, Cápsula Barroco, Cápsula Pitón) usaban portadas de marca dedicadas
  (`brand-cover-*.jpg`, 1600×1600, sistema burdeos/oro/crema con corona y pie
  "STREET ROYALTY HOOD — MMXXVI"). Las ~48 restantes usaban fotos planas de mockup
  de producto como portada → inconsistencia visual en la navegación principal.

## Acciones realizadas
1. Nuevo script `store-assets/brand_covers.py` (PIL): sistema de portadas de marca
   1600×1600 con plantilla común (degradado tonal por paleta, wordmark SRHOOD
   repetido tono sobre tono, marco doble de oro con diamantes, icono dorado por
   categoría, título serif crema, subtítulo tracked y pie MMXXVI). 4 paletas
   (burdeos/navy/negro/oliva) y 15 iconos de línea (percha, camiseta, hoodie,
   pantalón, chaqueta, sneaker, gorra, mochila, gafas, destello, diamante, laurel,
   cápsula, etiqueta 40, corona).
2. Generadas y subidas 16 portadas (stagedUploadsCreate → POST → collectionUpdate;
   9 necesitaron la ruta fileCreate → CDN → collectionUpdate porque el fetch directo
   del staged upload no aplicó el cambio de imagen) para las colecciones core:
   Ropa Streetwear, Camisetas, Sudaderas & Hoodies, Pantalones & Joggers,
   Chaquetas & Abrigos, Calzado & Sneakers, Gorras & Gorros, Bolsas & Mochilas,
   Accesorios, Novedades, Esenciales SRHOOD, Royalty Classics, Cápsulas SRHOOD,
   Menos de 40 €, Street Royalty Hombre y Street Royalty Mujer.
3. Todas las portadas llevan alt text de marca: "«Título» — portada de marca
   Street Royalty Hood" (coherente con las cápsulas de runs anteriores).

## Verificación
- Las 16 colecciones sirven la nueva portada. Ojo: en 9 de ellas Shopify conserva
  la RUTA del archivo anterior (p. ej. `unisex-heavy-blend-hoodie-...jpg`) pero el
  contenido servido ya es la portada nueva (el parámetro `?v=` rompe la caché);
  descargada la URL de Novedades y comprobado píxel a píxel que es la portada.
  En las otras 7 la URL pasó a `collections/brand-cover-<handle>.jpg`.
- Alt text verificado en las 16 vía GraphQL.

## Pendiente / notas para el próximo run
- Las ~32 cápsulas restantes siguen con foto de mockup como portada; se pueden
  migrar al sistema `brand_covers.py` añadiendo entradas a `COVERS` (o mantener
  el criterio de que las cápsulas muestren producto y solo las core lleven portada
  de marca — decidir).
- Sigue pendiente de admin: idioma principal a Español, verificar tarifa de envío
  gratis ≥50 €, y el tráfico "direct" de baja calidad (ver run 2026-07-15).
