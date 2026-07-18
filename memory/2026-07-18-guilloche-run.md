# Run 2026-07-18 — Cápsula "Guilloché — Grabado Real"

Tienda: Street Royalty Hood (srhood.com) · Shopify + Printful (store 18383330)

## Concepto
Grabado de seguridad de billete clásico (guilloché): rosetones hipotrocoides,
cintas de ondas entrelazadas, ráfagas radiales y cenefas — generado
matemáticamente con `store-assets/guilloche.py` (PIL, supermuestreo ×2).
Paleta: esmeralda #0E5D45 / verde profundo #093A2C / marfil #F2EDDF / cobre #BA7430.
Patrón NO usado por ninguna cápsula previa (nocturna, suminagashi, cianotipo,
moiré, glitch, vidriera, neón, azulejo, telar, déco, paisley, topografía, etc.).

## Productos creados (6 · ACTIVE · tag `guilloche-real`)
| SKU | Producto | Shopify ID | Printful sync | Catálogo PF |
|---|---|---|---|---|
| SRH-GUI01 | Camiseta Gran Rosetón — Blanco (27,95–29,95 €) | 15841883488640 | 447082110 | 71 Bella 3001 White |
| SRH-GUI02 | Sudadera Cinta Grabada — Negro (39,95–42,95 €) | 15841883554176 | 447082204 | 145 Gildan 18000 Black |
| SRH-GUI03 | Hoodie Premium Sello Real — Negro (49,95–52,95 €) | 15841883586944 | 447082317 | 380 CH M2580 Black |
| SRH-GUI04 | Zapatillas Altas Hombre — Marfil/Esmeralda (74,95 €) | 15841883652480 | 447082482 | 513 High Top Canvas |
| SRH-GUI05 | Deportivas Mujer — Marfil/Esmeralda (79,95 €) | 15841883783552 | 447082613 | 658 Women's Athletic |
| SRH-GUI06 | Riñonera — Esmeralda (32,95 €) | 15841883816320 | 447082753 | 350 AOP Fanny Pack |

Colección smart: "Cápsula Guilloché — Grabado Real"
(gid://shopify/Collection/701944398208, regla TAG=guilloche-real, 6 productos).
Entradas automáticas por tipo/tag: Ropa Streetwear, Camisetas, Sudaderas & Hoodies,
Calzado & Sneakers, Zapatillas Altas/Deportivas, Calzado Hombre/Mujer, Novedades,
Completa el Look (riñonera), Hombre/Mujer (tag unisex).

## Pipeline técnico (documentado para futuros runs)
1. Diseños PIL → PNG (front 2400×3200 fit, hoodie 2250×2250, altas 2400×2400
   cover, deportivas 1950×3300 cover, riñonera 2850×1050 cover front/top/back).
2. Subida a Shopify CDN: `stagedUploadsCreate` (httpMethod PUT es lo más simple:
   un solo `curl -X PUT --data-binary`) → `fileCreate` → poll `nodes(ids:)` hasta
   fileStatus READY para obtener URL cdn.shopify.com/.../files/….
3. Mockups: POST `/mockup-generator/create-task/{catalog_id}` (requiere
   `position` completo: area_width/height + width/height + top/left) → poll
   `/mockup-generator/task?task_key=`. Los printfiles por producto salen de
   `/mockup-generator/printfiles/{id}` (requiere header X-PF-Store-Id).
4. Productos Shopify vía MCP create-product (imágenes = URLs temporales de
   mockup; Shopify las copia a su CDN). Tags/tipos según sistema de colecciones.
5. Printful importa el producto Shopify en <1 min como sync product
   (unsynced, is_ignored=true). GET `/sync/products/@{shopify_product_id}`.
6. **CLAVE**: vincular variantes con `PUT /sync/variant/{sync_variant_id}`
   (SINGULAR — la ruta plural `/sync/variants/{id}` es un endpoint bulk
   read-only que exige `?external_ids=` y NO aplica cambios; devuelve 200
   engañoso). Body: `{"variant_id": <catalog_variant_id>, "is_ignored": false,
   "files": [{"type": "default|shoe_left|…", "url": <print png>, "position": …}]}`.
   Con eso la variante pasa a synced=true al instante. Ojo: en prendas DTG el
   type es `default`, pero en cut&sew tipo riñonera es `front`/`top`/`back`
   (`default` da "placements are not available"). Rate limit agresivo: ~1 req/s
   con backoff en 429.
7. Colección smart por tag vía MCP create-collection.

Variant IDs de catálogo usados (referencia rápida):
- Bella 3001 White S–2XL: 4011–4015 · Gildan 18000 Black: 5434–5438
- CH M2580 Black: 10779–10783 · High Tops 513: 12903–12916, 12918–12920
- Athletic 658: 16385–16399 · Fanny 350: 9986 (S/M), 9987 (M/L)

## Notas
- La API v1 `/store/products` está bloqueada para tiendas Shopify; la tienda
  "native" 18449429 está vacía y no se usa.
- Los archivos de impresión y mockups quedan en el CDN de Shopify (gui_*.png).
- Precios alineados con cápsulas previas (tee 27,95 / hoodie 49,95+3 en 2XL /
  altas 74,95 / deportivas 79,95).
