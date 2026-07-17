# Run 2026-07-17 (14:12 UTC) — Rescate Cápsula Nómada + Cápsula Azulejo

Tienda: Street Royalty Hood (srhood.com) · Shopify Basic · EUR · Printful store_id 18383330

## Hallazgo crítico: cómo enlazar variantes Printful en tiendas Shopify
El endpoint documentado `PUT /sync/variants/{id}` NO funciona (error "Missing required
parameters: external_ids" — esa ruta es un endpoint bulk de solo lectura por
`?external_ids=`). El endpoint correcto es **singular**:

    PUT https://api.printful.com/sync/variant/{sync_variant_id}?store_id=18383330
    body: {"variant_id": <catalog_variant_id>, "is_ignored": false,
           "files": [{"type": "<placement>", "url": "<cdn.shopify print file>"}]}

- `GET /sync/variant/{id}` (singular) también funciona.
- Un producto importado de Shopify llega con `is_ignored: true` a nivel producto y
  variantes sin `variant_id`; al enlazar variantes con `is_ignored:false` el producto
  se activa y Printful empuja inventario 9999 a Shopify.
- Rate limit ~120 req/min COMPARTIDO: usar pausas de ~1,5 s y reintentos ante 429.
- Mockup generator: `POST /mockup-generator/create-task/{catalog_product_id}` exige
  `position` en cada file (area_width/area_height/width/height/top/left = dims del
  printfile, ver `/mockup-generator/printfiles/{pid}`). Placements: tee/sudadera/hoodie
  `front` 1800×2400; hi-top 513 `shoe_quarters_*`/`shoe_tongue_*` 2250×2250; slip-on
  mujer 575 `shoe_left/right` 2325×2325; calcetines 186 `default` 700×1200.

## Sesión paralela detectada
Al iniciar este run, el run de las ~13:20 seguía vivo reparando su "Cápsula Nómada —
Patrones del Mundo" (tag nomada-real). Reparto de trabajo real: este run enlazó las 50
variantes Printful de la Nómada (tras descubrir el endpoint) y el run paralelo añadió
mockups, activó productos y borró sus calcetines duplicados (v2/v3). Resultado: 6/6
Nómada ACTIVE y sincronizados. Lección: los runs se solapan — comprobar SIEMPRE el
estado vivo antes de crear/borrar, y preferir operaciones idempotentes.

## Cápsula nueva de este run: "Cápsula Azulejo — Cerámica Real" (tag azulejo-real)
Primera cápsula en azul cobalto/blanco/oro. Patrones cerámicos inéditos (no repiten
paisley/déco/telar/nocturna/tartán/bogolán/ikat/camo/lis/pantera/panal):
1. Camiseta Azulejo Real — Blanco (15840606650752, SRH-AZ01, 27,95 €) — panel 4×4 de
   azulejos rosetón/estrella-cruz con medallón corona, Bella 3001 White.
2. Sudadera Mosaico Real — Blanco (15840606683520, SRH-AZ02, 42,95 €) — franja de
   mosaico + cenefas, Gildan 18000 White.
3. Hoodie Estrella de Ocho — Azul Royal (15840606781824, SRH-AZ03, 49,95 €) — estrella
   zellige concéntrica con corona de oro, M2580 Team Royal.
4. Zapatillas Altas Azulejo Hombre — Blanco/Cobalto (15840606847360, SRH-AZ04, 74,95 €)
   — teselado en quarters + lengüeta medallón, producto 513, tallas 5–13.
5. Zapatillas Slip-On Trencadís Mujer — Blanco (15840606978432, SRH-AZ05, 59,95 €) —
   trencadís gaudiniano all-over, producto 575, tallas 5–12.
6. Calcetines Cuerda Seca — Cobalto (15840607109504, SRH-AZ06, 14,95 €) — mini
   estrellas de ocho, producto 186.

Print files en Shopify Files: azulejo_*.png (v=17842988xx). Generador:
`store-assets/azulejo_real.py` (PIL; azulejos renderizados por celda recortada para
evitar sangrado entre teselas).

Colección smart creada: "Cápsula Azulejo — Cerámica Real" por tag azulejo-real.
Los productos entran solos en Ropa Streetwear / Calzado & Sneakers / Camisetas /
Sudaderas & Hoodies / Zapatillas Altas / Zapatillas Bajas & Slip-On / Calzado
Hombre / Calzado Mujer / Novedades / Completa el Look por tipo+tags.

## Estado de cápsulas (para no repetir patrones ni prendas)
- Colores base ya usados: negro, navy, burdeos, verde bosque, verde militar, crema,
  arena, blanco, azul royal (nuevo), cobalto (nuevo).
- Familias de patrón usadas: paisley/boteh, art déco (abanico/guilloché/rayos/zigurat/
  escama/plumaje), telar (bargello/asanoha/seigaiha/damasco/celosía/espiga), nocturna
  (terrazzo/marea/boreal/jardín/isométrica/meandro), tartán/dinastía/cadena/estandarte,
  nómada (bogolán/ikat/camo/lis/pantera/panal), azulejo (rosetón/estrella-cruz/zellige/
  trencadís/cuerda seca/cenefa), royal ink (halftone/wordmark/crest/circuito/sello/glitch).
- Ideas libres para próximos runs: topográfico/contornos, op-art moiré, glitch textil,
  ondas ukiyo-e (distinto de seigaiha ya usado), mola/kuna, wax print africano,
  azteca/talavera mexicana, souvenir jacquard, cianotipo botánico.
