# Run 2026-07-18 — Cápsula Malaquita — Piedra Real

Tienda: Street Royalty Hood (srhood.com) · Printful store 18383330 (Shopify)

## Qué se hizo
Nueva cápsula de 6 productos con patrón **inédito** (malaquita procedural: bandas
concéntricas de esmeralda con warp fBm, estriaciones finas y vetas de oro que siguen
los contornos). Generador: `store-assets/malaquita.py` (numpy + PIL). Ficheros de
impresión subidos al CDN de Shopify vía stagedUploadsCreate + fileCreate; mockups
reales con el Mockup Generator de Printful.

Productos (Shopify product id · SKU · precio EUR · catálogo Printful):
1. Camiseta Malaquita Real — Negro (15843133227392 · SRH-MAL01 · 27,95/29,95 · Bella 3001, var 4016-4020)
2. Sudadera Malaquita Estrato — Verde Botella (15843133260160 · SRH-MAL02 · 44,95/46,95 · Gildan 18000, var 18763-18767)
3. Hoodie Premium Sello de Malaquita — Negro (15843133325696 · SRH-MAL03 · 49,95/51,95 · CH M2580, var 10779-10783)
4. Zapatillas Altas Malaquita Hombre — Negro/Esmeralda (15843133391232 · SRH-MAL04 · 74,95 · prod 513, var 17450-17466)
5. Zapatillas Deportivas Malaquita Mujer — Esmeralda (15843133456768 · SRH-MAL05 · 59,95 · prod 658, var 16385-16399)
6. Calcetines Malaquita — Verde Bosque (15843133489536 · SRH-MAL06 · 14,95 · prod 186, var 7290-7292)

Sincronización Printful: 50/50 variantes synced (sync products 447363895-447364388),
ficheros por placement (DTG `default`; altas: shoe_quarters/tongue L+R; deportivas:
shoe_left/right; calcetines: `default`) + opción embroidery_type=flat en prendas DTG.

Colecciones:
- Nueva smart "Cápsula Malaquita — Piedra Real" (tag `malaquita-real`,
  gid://shopify/Collection/701966745984), 6 productos, imagen de portada.
- Tag añadido al ruleset de "Cápsulas SRHOOD — Series Limitadas" (701957603712; ahora 34 tags).
- Entrada automática por reglas existentes en: Ropa Streetwear, Camisetas, Sudaderas &
  Hoodies, Calzado & Sneakers, Zapatillas Altas/Deportivas, Calzado Hombre/Mujer,
  Novedades, Completa el Look. Sin añadidos manuales para no sobrecargar.

## Detalles técnicos (para futuros runs)
- API v1 Printful, tiendas de plataforma: listar `/sync/products`, modificar
  **`PUT /sync/variant/{id}`** (SINGULAR; `/sync/variants/{id}` devuelve el error
  engañoso "Missing required parameters: external_ids"). `@external_id` tampoco
  funciona en ese endpoint: usar el id numérico del sync variant.
- Flujo completo: diseño → CDN Shopify → mockup generator (`position` es obligatorio;
  usar dims de `/mockup-generator/printfiles/{product_id}`) → create-product en
  Shopify (MCP) → esperar import de Printful (~1 min) → PUT sync/variant por talla.
- Rate limit Printful: ~1 req/s con ráfagas cortas; reintentar 429 tras ~35 s.

## Patrones ya usados (no repetir)
brocado, forja, tartán, eslabón/cadena, camo, escaque/damero/ajedrez, laurel, baraja,
frecuencia, kintsugi, plumaje, guilloché, neón, vidriera, celeste/astros, trazo/splatter,
estática/glitch, moiré, vía/asfalto, salpicadura, nube, suminagashi, cianotipo,
terrazo/terrazzo, greca, pinstripe, blueprint, topografía/contorno, retícula, órbita,
serpentina, azulejo/trencadís/mosaico, cuerda seca, panal, pantera, bogolán, ikat, lis,
paisley/cachemir/boteh, déco (zigurat/escama/abanico/rayos), espiga, celosía, seigaiha,
bargello, asanoha, damasco, meandro, jardín nocturno, isométrica, pata de gallo (gorra),
onda óptica, **malaquita (este run)**.
Libres aún: nácar/madreperla, ópalo, aurora boreal, trenzado/cesta, batik, shibori,
mármol clásico, granito, obsidiana, ámbar, filigrana, acanto en voluta, toile de jouy,
vichy, croco.
