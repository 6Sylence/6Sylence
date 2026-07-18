# Run 2026-07-18 — Drop "Plumaje Real — Ojo del Pavo Real"

Tienda: Street Royalty Hood (srhood.com) · Printful store 18383330 (shopify)

## Concepto
Pluma de pavo real dibujada barba a barba (raquis de oro, ojo iridiscente en anillos
orgánicos zafiro/teal/esmeralda con halo dorado) sobre fondo de noche. Motivo NO usado
en ninguna cápsula anterior (revisadas las ~30 series existentes: guilloché, neón,
vidriera, celeste, suminagashi, cianotipo, paisley, azulejo, ikat, bogolán, pantera,
panal, moiré, terrazo, greca, damero, topografía, déco, telar, etc.).

## Productos creados (6 · Shopify ACTIVE + Printful synced)
Cápsula de 6 piezas para no sobrecargar (mismo tamaño que las cápsulas previas):
1. Camiseta Plumaje Real — Negro · Bella+Canvas 3001 · 27,95/29,95 € · SRH-PLU01
   (gid 15841941619072)
2. Hoodie Premium Abanico Real — Negro · CH M2580 · 49,95/52,95 € · SRH-PLU02
   (gid 15841941946752) — abanico de 5 plumas sobre corona oro
3. Zapatillas Altas Plumaje Hombre — Noche · base NEGRA (novedad) · 74,95 € ·
   SRH-PLU03 (gid 15841942372736) · AOP 4 placements
4. Zapatillas Deportivas Plumaje Mujer — Noche · 74,95 € · SRH-PLU04
   (gid 15841943028096)
5. Bandana Plumaje Real — Noche · catálogo Printful 630 — TIPO NUEVO, primera bandana
   de la tienda · mandala 12 plumas + medallón corona · 19,95 € · SRH-PLU05
   (gid 15841943454080)
6. Calcetines Plumaje — Noche · 14,95 € · SRH-PLU06 (gid 15841943716224)

## Flujo técnico (reproducible)
1. Diseños PIL: `store-assets/plumaje_real.py` → 6 PNG (tee 2400×3200 RGBA,
   hoodie 1800×1800 RGBA, hitops 2400×2400, athletic 1950×3300, socks 1400×2400,
   bandana 4125×4125).
2. Subida a Shopify Files vía stagedUploadsCreate + fileCreate → cdn.shopify.com/…/plu_*.png
3. Mockups: Printful mockup-generator (create-task con `position` obligatorio =
   área completa del printfile; OJO rate limit 429 → espaciar).
4. Productos Shopify vía MCP (opción "Talla", vendor SRHOOD, tipos Camiseta/Hoodie/
   ZAPATILLAS/Bandana/Calcetines, tag cápsula `plumaje-real` + novedades etc.).
5. Printful importa automáticamente (~1-2 min) → PUT /sync/variant/{id} con
   variant_id de catálogo + files por placement (tee/hoodie/socks `default`;
   hitops shoe_quarters_l/r + shoe_tongue_l/r; athletic shoe_left/right;
   bandana front+default).

## Colecciones
- Nueva smart collection "Cápsula Plumaje — Ojo del Pavo Real"
  (gid://shopify/Collection/701946888576, tag plumaje-real, CREATED_DESC).
- Entradas automáticas por tipo/tag: Ropa Streetwear, Calzado & Sneakers, Camisetas,
  Sudaderas & Hoodies, Zapatillas Altas/Deportivas, Calzado Hombre/Mujer, Accesorios,
  Completa el Look, Novedades, All-Over Print.
- Añadidos Hoodie + Zapatillas Altas a "Home page" (portada).

## Estado final de sincronización
48/48 variantes synced en Printful (verificado): tee 5/5, hoodie 5/5, altas 17/17,
deportivas 15/15, bandana 3/3, calcetines 3/3.
- Gotcha 1: el placement `front` NO se acepta en PUT /sync/variant para la bandana
  (630) — usar `type: default`.
- Gotcha 2: la importación automática Shopify→Printful tarda 1-5 min y no es
  simultánea (el hoodie tardó ~10 min más que el resto).

## Aviso anti-repetición (para próximos runs)
"Zapatillas Altas Plumaje Real Hombre — Negro" (SRH-DC04, cápsula Déco) ya usaba
ojos de pavo real EN CLAVE GEOMÉTRICA déco (círculos planos + rayos). Verificado
visualmente: patrón distinto al de esta cápsula (pluma naturalista dibujada).
Con esta cápsula el motivo pavo real queda AGOTADO — no volver a usarlo.

## Notas / pendientes
- Sigue pendiente de sesiones previas: ~20 productos del lote 10-jul (Greca, Terrazo,
  Blueprint, Pinstripe, Damero, Camuflaje, Corona Scatter, Wordmark…) figuran en
  Printful con synced 0 — no se han tocado hoy.
- Recomendación de la auditoría 15-jul sin resolver: idioma principal de la tienda
  sigue en inglés (requiere admin).
