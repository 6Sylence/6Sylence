# Run 2026-07-18 — Drop "Kintsugi Real" (Printful + Shopify)

Tienda: Street Royalty Hood (srhood.com) · Printful store 18383330 (Shopify) · EUR

## Contexto
Tarea programada: seguir añadiendo productos POD (creados en Printful) a las ramas de
ropa / calzado / accesorios sin repetir patrones. Series ya usadas detectadas en las
~300 sync products más recientes: Plumaje Real, Guilloché, Neón, Vidriera, Celeste/
Astrolabio, Trazo/Salpicadura, Estática, Moiré, Vía, Nube Imperial, Suminagashi,
Cianotipo, Camuflaje, Terrazo, Greca, Pinstripe, Blueprint, Damero, Topográfico,
Órbita, Retícula, Trencadís/Azulejo/Mosaico, Pantera, Bogolán, Ikat, Paisley/Cachemir,
Panal, Confeti, Cuerda Seca, Composición, Serpentina, Nube, Bandana…

## Patrón nuevo elegido: KINTSUGI (no usado antes)
Porcelana craquelada + fracturas reparadas con vetas de oro (motor generativo propio en
`store-assets/kintsugi.py`: grietas ramificadas con taper, sombra/perfil de tinta, oro
con shimmer, polvo dorado, craquelure fino, corona/luna de porcelana).

## Productos creados (6, SKU SRH-KIN01..06) — flujo completo
1. Shopify `productSet` (ACTIVE, tallas/precios/SKU/tags como drops previos).
2. Prints subidos a Shopify Files (stagedUploadsCreate + fileCreate).
3. Printful importa los productos → PUT /sync/variant/{id} con variant_id de catálogo
   + files por placement (60/60 variantes synced, reintentos con backoff por 429).
4. Mockups vía /mockup-generator (requiere `position`) → productCreateMedia.

| Producto | Shopify ID | PF sync | Catálogo PF | Precio |
|---|---|---|---|---|
| Camiseta Kintsugi Real — Negro | 15842113028480 | 447127607 | 71 (Bella 3001) 4016-20 | 27,95/29,95 |
| Camiseta ML Kintsugi Fractura — Blanco | 15842115125632 | 447127727 | 356 (Bella 3501) 10142-46 | 32,95 |
| Hoodie Premium Kintsugi Luna Rota — Negro | 15842117517696 | 447127866 | 380 (M2580) 10779-83 | 49,95/52,95 |
| Zapatillas Altas Kintsugi Hombre — Porcelana | 15842118566272 | 447128001 | 513, 17450-66 (quarters+tongue L/R) | 74,95 |
| Zapatillas Slip-On Kintsugi Mujer — Tinta | 15842119451008 | 447128119 | 575, 14721-35 (shoe L/R) | 59,95 |
| Calcetines Kintsugi — Tinta | 15842120073600 | 447128216 | 186, 7290-92 | 14,95 |

## Colecciones
- Nueva smart "Kintsugi Real — Porcelana & Oro" (tag `kintsugi-real`,
  gid://shopify/Collection/701949149568, 6 productos, imagen = mockup high tops).
- Entradas automáticas por tipo/tag: Ropa Streetwear 552→555, Calzado & Sneakers
  349→351, Accesorios 242→243, Novedades +6, Mujer/Hombre por tags.
- Camiseta + Zapatillas Altas añadidas a "Home page" (portada, 45 productos).

## Notas técnicas (para próximos runs)
- La tienda Printful es tipo `shopify`: NO sirve POST /store/products (solo Manual/API);
  el alta se hace creando el producto en Shopify y configurando después los sync
  variants (PUT /sync/variant/{id}). Header `X-PF-Store-Id: 18383330`.
- Rate limit Printful: ráfaga corta y ventana de 60 s → backoff leyendo "after N seconds".
- Mockup generator exige `position` {area_width,area_height,width,height,top,left};
  áreas: tee/ls front 1800×2400, hoodie front 1800×1800, hitops 2250², slipon 2325²,
  calcetines 700×1200.
- Print files servidos desde Shopify CDN funcionan como `url` de Printful.

## Pendiente / ideas futuras (sin repetir)
- Patrones aún libres: Art Déco rayos, cadena/eslabones, sashiko/seigaiha, tormenta
  eléctrica, lacre/sellos de cera, caligrafía pincel, mapa nocturno de metro.
- Sigue pendiente de admin: idioma principal a Español, tarifa envío gratis ≥50 €.
