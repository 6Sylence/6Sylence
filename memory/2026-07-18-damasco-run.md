# Run 2026-07-18 (noche) — Cápsula Damasco — Seda Real

Tienda: Street Royalty Hood (srhood.com) · Printful store 18383330 (shopify)

## Nueva cápsula: Damasco — Seda Real (tag `damasco-real`)
Patrón nuevo no usado por ninguna de las 32 cápsulas previas: damasco barroco
(retícula ogee + medallón coronado con palmeta, volutas de acanto y rosetas),
paleta esmeralda + oro + marfil. Generador: `store-assets/damasco_real.py`
(tiles seamless con paste envolvente, medallones simétricos Catmull-Rom,
supersampling 2×). Print files en Shopify CDN (`dam01..dam06`).

Productos (6, ACTIVE, sincronizados en Printful variante a variante):
- Camiseta Damasco Real — Negro (Bella 3001, 27,95/29,95 €) — SRH-DAM01
- Sudadera Damasco Real — Verde Botella (Gildan 18000 Forest, 44,95/46,95 €) — SRH-DAM02
- Hoodie Premium Seda Real — Negro (Cotton Heritage M2580, 49,95/51,95 €) — SRH-DAM03
- Zapatillas Altas Damasco Hombre — Negro/Esmeralda (17 tallas US, 74,95 €) — SRH-DAM04
- Zapatillas Slip-On Damasco Mujer — Marfil/Esmeralda (15 tallas US, 59,95 €) — SRH-DAM05
- Bucket Hat Damasco Reversible — Esmeralda/Marfil (S/M, L/XL, 34,95 €) — SRH-DAM06

Colección smart nueva: "Cápsula Damasco — Seda Real" (TAG damasco-real).
El tag también se añadió al ruleset de "Cápsulas SRHOOD — Series Limitadas".

## Incidencia detectada (de un run anterior de hoy, ~16:30)
Las cápsulas **Camo Real** (6 productos) y **Escaque — Jaque Real** (6 productos)
quedaron en DRAFT en Shopify y con **synced: 0 en Printful**: aquel run murió a
mitad del flujo y sus print files no están en el CDN de Shopify (probablemente
usó URLs de staged upload, que caducan a las 24 h). Sin print files no se pueden
sincronizar para fulfillment.
- Acción tomada: se dejaron en DRAFT (invisibles para clientes). NO activarlas
  hasta regenerar sus diseños y sincronizarlas, o borrarlas.
- Lección para próximos runs: subir SIEMPRE los print files vía
  stagedUploadsCreate + fileCreate y usar la URL final de cdn.shopify.com
  (no la resourceUrl temporal) tanto para mockups como para el sync.

## Convenciones del flujo (para próximos runs)
1. Diseños PIL → PNG/JPG en `store-assets/designs/`.
2. stagedUploadsCreate + POST multipart + fileCreate → URL cdn.shopify.com.
3. Mockups: POST /mockup-generator/create-task/{product_id} (requiere `position`
   completo; rate limit duro ≈2/min — usar backoff 62 s), luego GET task.
4. Producto Shopify en DRAFT (MCP create-product) con mockups, tipo, tags, SKUs.
5. Printful importa solo el producto (~1 min); PUT /sync/variants/{id} con
   variant_id de catálogo + files (URL CDN) por cada variante.
6. Activar producto + colección smart por TAG + añadir tag al ruleset de
   "Cápsulas SRHOOD" (update-collection REEMPLAZA todas las reglas: reenviar
   la lista completa).

Variant IDs de catálogo usados: tee Bella 3001 negro 4016-4020 · Gildan 18000
forest 18763-18767 · M2580 negro 10779-10783 · High Top hombre 17450-17466 ·
Slip-On mujer 14721-14735 · Bucket reversible 16360-16361.
