# Run 2026-07-18 (noche) — Cápsula Brocado — Seda Real

Tienda: Street Royalty Hood (srhood.com) · Printful store 18383330 (shopify)

## Nueva cápsula: Brocado — Seda Real (tag `brocado-real`)
Patrón nuevo: brocado/damasco barroco (retícula ogee + medallón coronado con
palmeta, volutas de acanto y rosetas), paleta esmeralda + oro + marfil.
Generador: `store-assets/damasco_real.py` (tiles seamless con paste envolvente,
curvas Catmull-Rom, supersampling 2×). Print files en Shopify CDN (`dam01..dam06`).

IMPORTANTE — la cápsula se llamó primero "Damasco" y se renombró a **"Brocado"**
en el mismo run: la Cápsula Telar (17-jul) ya tenía una "Camiseta Damasco Real —
Negro" (SRH-TL01, emblema dorado línea-art). Antes de nombrar una cápsula,
buscar SIEMPRE el nombre en productos existentes (search_products por título).

Productos (6, sincronizados variante a variante; sync product IDs):
- Camiseta Brocado Real — Negro (Bella 3001, 27,95/29,95 €) — SRH-DAM01 · 447336496
- Sudadera Brocado Real — Verde Botella (Gildan 18000 Forest, 44,95/46,95 €) — SRH-DAM02 · 447336619
- Hoodie Premium Seda Real — Negro (M2580, 49,95/51,95 €) — SRH-DAM03 · 447336690
- Zapatillas Altas Brocado Hombre — Negro/Esmeralda (17 tallas US, 74,95 €) — SRH-DAM04 · 447336937
- Zapatillas Slip-On Brocado Mujer — Marfil/Esmeralda (15 tallas US, 59,95 €) — SRH-DAM05 · 447337011
- Bucket Hat Brocado Reversible — Esmeralda/Marfil (S/M, L/XL, 34,95 €) — SRH-DAM06 · 447337074

Colección smart nueva: "Cápsula Brocado — Seda Real" (TAG brocado-real,
gid://shopify/Collection/701964452224, handle capsula-damasco-seda-real).
El tag también se añadió al ruleset de "Cápsulas SRHOOD — Series Limitadas"
(al hacerlo se añadió también forja-real, que faltaba).

## Incidencia detectada (de un run anterior de hoy, ~16:30)
Las cápsulas **Camo Real** (6 productos) y **Escaque — Jaque Real** (6 productos)
quedaron en DRAFT en Shopify y con **synced: 0 en Printful**: aquel run murió a
mitad del flujo y sus print files no están en el CDN de Shopify (probablemente
usó URLs temporales de staged upload, que caducan a las 24 h). Sin print files
no se pueden sincronizar para fulfillment.
- Acción tomada: se dejaron en DRAFT (invisibles para clientes). NO activarlas
  hasta regenerar sus diseños y sincronizarlas, o borrarlas.

## Convenciones del flujo (para próximos runs)
1. Diseños PIL → PNG/JPG en `store-assets/designs/`.
2. stagedUploadsCreate + POST multipart + fileCreate → usar SIEMPRE la URL final
   de cdn.shopify.com (nunca la resourceUrl temporal).
3. Mockups: POST /mockup-generator/create-task/{product_id} — requiere `position`
   completo ({area_width, area_height, width, height, top:0, left:0} del
   printfile); rate limit duro ≈2/min → backoff 60 s entre tareas.
4. Producto Shopify en DRAFT (MCP create-product) con mockups, tipo, tags, SKUs.
   El MCP update-product NO cambia tags: usar graphql tagsAdd/tagsRemove.
5. Printful importa solo el producto (~1 min); sincronizar cada variante con
   **PUT /sync/variant/{sync_variant_id}** (SINGULAR — la ruta plural
   /sync/variants/{id} devuelve "Missing required parameters: external_ids")
   con body {variant_id: <catálogo>, files: [...]}. GET también singular.
6. Al buscar el sync product por nombre puede haber colisiones de nombre con
   productos viejos: fijar los IDs devueltos por la importación comparando
   external_id con el GID del producto Shopify recién creado.
7. Activar productos + colección smart por TAG + añadir tag al ruleset de
   "Cápsulas SRHOOD" (update-collection REEMPLAZA todas las reglas: reenviar
   la lista completa, hoy 33 tags).

Variant IDs de catálogo usados: tee Bella 3001 negro 4016-4020 · Gildan 18000
forest 18763-18767 · M2580 negro 10779-10783 · High Top hombre (513) 17450-17466 ·
Slip-On mujer (575) 14721-14735 · Bucket reversible (654) 16360-16361.
