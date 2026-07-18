# Run 2026-07-18 (19:15–20:05 UTC) — Reparación de sync + Cápsula Forja

Tienda: Street Royalty Hood (srhood.com) · Printful store 18383330 (Shopify) · EUR

## Hallazgo crítico al empezar
Los 4 drops de las ejecuciones anteriores de hoy (Escaque, Camo ~16:30; Eslabón, Tartán ~17:35)
quedaron **sin sincronizar en Printful** (`is_ignored=true`, 0/98+ variantes vinculadas):
productos ACTIVE en Shopify que Printful NO habría producido si alguien compraba.

**Método de reparación descubierto** (documentado aquí para futuros runs):
- El endpoint correcto es `PUT https://api.printful.com/sync/variant/{sync_variant_id}` — **SINGULAR** —
  con body `{"variant_id": <catalog_id>, "is_ignored": false, "files": [{"type": ..., "url": ...}]}`.
- `/sync/variants/...` (plural), `/store/variants` y la API v2 NO funcionan para tiendas Shopify.
- Rate limit efectivo: ~10 req/min (429 con retry-after 60 s). Espaciar ~6,5 s por llamada.
- El variant_id de catálogo se copia de un producto equivalente ya sincronizado (misma talla/color)
  o del catálogo (`GET /products/{pid}`).
- Placements: camiseta/sudadera/hoodie/tank/calcetines/chanclas `default`; zip-espalda `back`;
  altas `shoe_quarters_left/right + shoe_tongue_left/right`; deportivas/slip-on `shoe_left/right`;
  mochila `front/top/bottom/pocket`; riñonera `default/top/back`.

## Acciones realizadas
1. **Reparados Tartán + Eslabón (12 productos, 98/98 variantes)** — ahora `synced` y sin ignorar.
   Los archivos de impresión (trt01..06, esl01..06) estaban en Shopify Files.
2. **Escaque + Camo (12 productos) → DRAFT.** Sus archivos de impresión nunca se subieron a ningún
   sitio recuperable (el run que los creó murió antes); no se pueden sincronizar sin regenerar el
   diseño, y un diseño regenerado no coincidiría con los mockups que ve el cliente. Además Camo y
   Escaque rozan repetición de patrones previos (Camo Jul-17, Cadena). PENDIENTE: decidir si se
   regeneran (diseño + mockups nuevos + sync) o se eliminan.
3. **Nueva Cápsula Forja — Hierro y Oro** (patrón forja/rejas españolas, NO usado antes; verificado
   contra los 1.271 nombres de productos). 6 productos ACTIVE, tag `forja-real`, SKUs SRH-FRJ01..06:
   - Camiseta Forja Real — Negro (27,95/29,95 2XL) — 15842879308160
   - Camiseta de Tirantes Forja — Negro (24,95/26,95) — 15842880061824
   - Hoodie Premium Puerta del Reino — Negro (49,95/51,95) — 15842881110400
   - Zapatillas Altas Forja Hombre — Negro/Oro (74,95) — 15842882421120
   - Chanclas Forja — Negro/Oro (24,95) — 15842883338624
   - Riñonera Forja — Negro/Oro (32,95) — 15842884223360
   Diseños PIL (`store-assets/forja_designs.py`), prints en Shopify Files (frj01..frj06),
   mockups vía Printful mockup-generator (requiere `position` completo), sync vía PUT /sync/variant.
4. **Colecciones**: nueva smart "Cápsula Forja — Hierro y Oro" (tag forja-real,
   gid://shopify/Collection/701963174272, con imagen). Los 6 entran solos en Ropa/Calzado/
   Accesorios/Camisetas/Sudaderas/Zapatillas Altas/Slides & Chanclas/Bolsas/Novedades/Hombre/Mujer
   por tipo+tags. Camiseta y Zapatillas Altas añadidas a "Home page" (49 items).
5. **Menú principal actualizado sin sobrecargar**: submenú "Novedades" ahora rota a las 8 cápsulas
   más recientes (Forja, Relieve, Suminagashi, Cianotipo, Forma&Color, Azulejo, Nómada, Pañuelo) +
   Classics + Verano + Ver todo; submenú "Colecciones" ahora sí lista TODAS las cápsulas (faltaban
   las 5 más nuevas) con Forja arriba.

## Estado pendiente / para el próximo run
- Verificar al final del run el resultado de `forja_sync` (49 variantes nuevas): ver
  scratchpad/forja_sync_results.json del run — si algo falló, re-ejecutar PUT /sync/variant.
- Decidir Escaque/Camo (en DRAFT): regenerar diseños+mockups+sync, o borrar.
- Patrones YA usados (no repetir): tartán, eslabón/cadena, camo, escaque, laurel, baraja,
  frecuencia, kintsugi, plumaje, guilloché, neón, vidriera, celeste, trazo/salpicadura, azulejo,
  mosaico/trencadís, topografía/relieve/contorno, greca, ikat, damasco, terrazo, suminagashi,
  cianotipo, boteh/paisley, panal, pantera, escama, onda, marea, león heráldico, circuito, forja.
- El idioma principal de la tienda sigue en inglés (68% tráfico España) — requiere admin manual.
