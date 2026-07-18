# Run 2026-07-18 — Drop "Cápsula Meandro — Laberinto Real"

Tienda: Street Royalty Hood (srhood.com) · Shopify · EUR · Printful store_id 18383330

## Contexto
Rutina diaria de cápsulas. Antes de crear nada se auditó el catálogo completo para no
repetir patrón: ya existen ~35 cápsulas (royal-ink, street-lab, serie-nocturna, telar,
época dorada, paisley, nómada, azulejo, forma-color, cianotipo, suminagashi, relieve,
nube-imperial, salpicadura, líneas vía/moiré/estática/trazo, corona-boreal, vidriera,
neón, guilloché, plumaje, kintsugi, frecuencia, baraja, laurel, escaque, camo, eslabón,
tartán, forja, brocado, malaquita). Motivo elegido: **greca griega / meandro + laberinto**
en paleta de ánfora (negro #16120F, crema #EEE3CB, terracota #C15E39, ocre #D79E55) —
inédito en la tienda, tanto en motivo como en paleta.

## Pipeline técnico (el que funciona)
1. La API v1 de Printful NO permite crear sync products en tiendas de plataforma Shopify
   (`/store/products` → 400). El camino operativo: **catálogo + mockup generator** de
   Printful y creación del producto vía Shopify Admin.
2. Diseños generados con PIL → `store-assets/meandro_real.py` (6 printfiles a medida).
3. Subida a Shopify Files (stagedUploadsCreate + fileCreate) → URLs públicas CDN.
4. Mockups: `POST /mockup-generator/create-task/{catalog_id}?store_id=18383330` con
   `option_groups` (Flat / Men's / Lifestyle) y polling del task. IDs de catálogo:
   camiseta Bella 3001 = 71, hoodie premium M2580 = 380, sudadera Gildan 18000 = 145,
   altas hombre = 513, slip-on mujer = 575, bandana AOP = 630.
5. Producto en Shopify con mockups como imágenes (se copian a CDN), ACTIVE, vendor
   SRHOOD, opción "Talla", inventario sin rastrear (no bloquea compra, correcto en POD).

## Productos creados (6, tag `meandro-real`)
| SKU | Producto | GID | Precio |
|---|---|---|---|
| SRH-MEA01 | Camiseta Meandro Real — Negro (S–2XL) | 15843221963136 | 27,95/29,95 € |
| SRH-MEA02 | Sudadera Friso de Ánfora — Arena (S–2XL) | 15843222028672 | 44,95/46,95 € |
| SRH-MEA03 | Hoodie Premium Laberinto Real — Negro (S–2XL) | 15843222061440 | 49,95/51,95 € |
| SRH-MEA04 | Zapatillas Altas Meandro Hombre — Negro/Crema (US 5–13) | 15843222159744 | 74,95 € |
| SRH-MEA05 | Zapatillas Slip-On Meandro Mujer — Crema/Terracota (US 5–12) | 15843222356352 | 59,95 € |
| SRH-MEA06 | Bandana Meandro Real — Terracota (S/M/L) | 15843222421888 | 19,95 € |

Cada pieza lleva una composición distinta (medallón, friso, emblema, diagonal all-over,
grid pequeño all-over, bandana clásica) — sin repetir composición dentro de la cápsula.

## Colecciones
- Nueva smart collection **"Cápsula Meandro — Laberinto Real"**
  (gid://shopify/Collection/701967270272, tag meandro-real, 6 productos, imagen = altas).
- Añadida la regla `meandro-real` al agregador **"Cápsulas SRHOOD — Series Limitadas"**
  (701957603712, ahora 35 cápsulas / 210 productos).
- Entrada automática por tipo/tag en: Ropa Streetwear, Camisetas, Sudaderas & Hoodies,
  Calzado & Sneakers, Zapatillas Altas, Zapatillas Bajas & Slip-On, Calzado Hombre,
  Calzado Mujer, Street Royalty Hombre/Mujer, Novedades, Accesorios Streetwear,
  Completa el Look (bandana) y Menos de 40 € (camiseta/bandana).
  No se sobrecargó ninguna colección manual (Home page intacta).

## Notas para el próximo run
- Temas ya usados: ver lista de arriba + meandro-real. Buscar motivo nuevo
  (ideas libres aún: panal/hexágonos, seigaiha, terrazo, mosaico romano, sello lacre,
  cuerda/nudos náuticos, mármol veteado…* comprobar tags igualmente).
- Paletas recientes: negro+oro (muchas), esmeralda, burdeos, navy, terracota (esta).
- La bandana (630) sólo existe en blanco: el color visible sale del printfile (cover).
- Sudadera en color "Sand" (Gildan 18000) funcionó bien para paletas cálidas.
