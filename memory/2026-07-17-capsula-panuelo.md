# Run 2026-07-17 (4º del día) — Drop "Cápsula Pañuelo — Paisley Real"

Tienda: Street Royalty Hood (srhood.com) · Shopify + Printful · EUR

## Qué se hizo

Nueva cápsula de 6 productos (ropa + calzado + complemento, nicho general streetwear),
creada vía Printful (mockups del Mockup Generator + sync de variantes con print files)
y publicada en Shopify. Patrón inédito: **paisley/bandana** (boteh cachemir a bezier
ajustado a mano), primera cápsula que abandona el negro: paleta crema `#f3ecd8`,
verde bosque `#1d3a29`, verde militar y óxido `#b85c2e`.

### Productos (ACTIVE, vendor SRHOOD, tag cápsula `paisley-real`)
| SKU | Producto | Base Printful | Precio | GID |
|---|---|---|---|---|
| SRH-PY01 | Camiseta Bandana Real — Crema | Bella+Canvas 3001 Soft Cream (71) | 27,95 € | 15840506773888 |
| SRH-PY02 | Camiseta Manga Larga Boteh — Verde Militar | Bella 3501 Military Green (356) | 32,95 € | 15840507101568 |
| SRH-PY03 | Hoodie Cremallera Cachemir Corona — Verde Bosque | Gildan 18600 Forest Green (692) | 54,95 € | 15840507330944 |
| SRH-PY04 | Zapatillas Altas Paisley Real Hombre — Verde Bosque | Men's High Top Canvas Black (513) | 74,95 € | 15840507462016 |
| SRH-PY05 | Zapatillas Deportivas Cachemir Mujer — Crema | Women's Athletic White (658) | 69,95 € | 15840507625856 |
| SRH-PY06 | Bucket Hat Reversible Paisley — Crema/Verde | AOP Reversible Bucket Hat (654) | 34,95 € | 15840507724160 |

Mix de tipos NUEVO respecto a las cápsulas anteriores (todas repetían camiseta +
sudadera + hoodie + 2 zapatillas + calcetines): manga larga, hoodie con cremallera,
deportivas de mujer y bucket hat reversible no se habían usado en ninguna cápsula.

### Colección / menú
- Smart collection **"Cápsula Pañuelo — Paisley Real"** (tag `paisley-real`,
  gid://shopify/Collection/701892657536, CREATED_DESC, imagen: espalda del hoodie).
- Añadida como subenlace 1º en **Novedades** y **Colecciones** del menú principal
  (menuUpdate: los ítems COLLECTION requieren `resourceId`, con solo `url` falla
  con "collection no encontrado").
- Hoodie cremallera + deportivas mujer añadidos a la colección manual "Home page" (ahora 27).

### Printful
- Diseños: `store-assets/paisley_real.py` (PIL, supersampling 2×, boteh paisley por
  beziers con contorno interior por offset de normales). 9 print files.
- Print files subidos al CDN de Shopify (stagedUploadsCreate + curl POST + fileCreate).
- Mockups: Mockup Generator con `X-PF-Store-Id: 18449429` (store nativo; el de
  Shopify 18383330 rechaza /store/products pero /sync/* sí funciona con él).
  **Límite 2 create-task/min** (429 con Retry-After). El placement `front` del zip
  hoodie devuelve como mockup principal la vista trasera; las frontales reales van
  en `extra` ("Front").
  Los placements de calzado/bucket requieren `position` aunque sean fill_mode=cover.
- Sync: variantes vinculadas vía `PUT /sync/variant/{id}` (store 18383330) con
  `variant_id` de catálogo + files por placement (49 variantes, ver pf_sync.log del run).

## Patrones YA usados (no repetir en próximos drops)
- Royal Ink/pósters: halftone corona, wordmark, crest, circuito, sello, señal,
  ocaso, topografía, carta estelar, marea.
- Street Lab: onda óptica (op-art), kintsugi/oro roto, topografía, vitral, mosaico
  azulejo, dominó.
- Serie Nocturna: constelación, suminagashi, terrazzo, isométrico, jardín nocturno,
  meandro griego. (negro+oro)
- Cápsula Telar: damasco, asanoha, bargello, seigaiha, celosía, espiga. (negro/navy/burdeos)
- Cápsula Déco: rayos/sunburst, guilloché, abanico, plumaje pavo real, escama, zigurat.
  (navy/burdeos/crema/oro)
- **Cápsula Pañuelo (este run): paisley/bandana — botehs, medallón bandana, cascada,
  banda pecho, all-over semicaído. (crema/verde militar/verde bosque/óxido)**

Ideas libres para el siguiente: liquid marble mármol veteado, cuerda/nudos marineros,
gingham/vichy, tie-dye shibori, espirales/olas Hokusai, granito/terrazo claro, tartán
(¡ojo: hubo "Tartán Real" en rex-drop!), pata de gallo, cebra/animal print abstracto.

## Estado pendiente heredado (no tocado en este run)
- Idioma principal de la tienda sigue en inglés (requiere admin).
- 600+ drafts antiguos "SRHOOD | ..." sin depurar.
- PRs #2–#8 de runs anteriores siguen abiertos (draft) sin mergear.
