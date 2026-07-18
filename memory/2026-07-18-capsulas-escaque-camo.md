# Run 2026-07-18 — Drop: Cápsula Escaque + Cápsula Camo Real

Tienda: Street Royalty Hood (srhood.com) · Shopify · EUR

## Contexto
Ya existían 27 cápsulas temáticas (Royal Ink, Nocturna, Telar, Déco, Paisley, Nómada,
Azulejo, Forma & Color, Cianotipo, Suminagashi, Relieve, Nube, Salpicadura, Vía, Moiré,
Glitch, Trazo, Observatorio, Vidriera, Neón, Guilloché, Plumaje, Kintsugi, Frecuencia,
Baraja, Laurel, Street Lab). Los dos temas nuevos NO repiten ningún patrón anterior:
- **Escaque** (ajedrez: tablero deformado ébano/marfil + piezas + oro) — tag `escaque-real`
- **Camo Real** (camuflaje de lujo bosque/medianoche con coronas doradas ocultas) — tag `camo-real`

## Flujo técnico (igual que runs anteriores + mockups Printful)
1. Diseños procedurales con PIL/numpy: `store-assets/capsules_escaque_camo.py`
   (14 archivos en `store-assets/designs/`, DTG frontales 1800×2400 RGBA y covers AOP).
2. Los PNG se sirven por raw.githubusercontent.com (repo público) — no hizo falta CDN.
3. Mockups reales con la **Printful Mockup Generator API** (store id 18383330, tipo shopify).
   OJO: la API de Printful NO permite crear productos sync en tiendas tipo Shopify
   (endpoint /store/products devuelve 400) → los productos se crean directo en Shopify
   con los mockups de Printful, como en todos los runs anteriores. Para que Printful
   los fulfille hay que vincularlos/sincronizarlos desde el dashboard de Printful.
4. Script de mockups (task por producto, con position por placement): scratchpad del run.
5. Productos creados vía MCP Shopify con inventario 9999 (inventorySetQuantities, 100 variantes).

## Productos creados (12, todos ACTIVE, vendor SRHOOD)
Cápsula Escaque (SKU SRH-ESC01..06):
- Camiseta Escaque Real — Negro (15842487796096) 27,95 €
- Sudadera Escaque Defiende la Corona — Gris Jaspeado (15842488058240) 42,95 €
- Hoodie Premium Rey de Marfil — Negro (15842488385920) 49,95 €
- Zapatillas Altas Escaque Hombre — Negro (15842488746368) 74,95 € (17 tallas, lengüeta propia)
- Zapatillas Deportivas Escaque Mujer — Marfil (15842489074048) 74,95 €
- Calcetines Escaque — Negro (15842489172352) 14,95 €

Cápsula Camo Real (SKU SRH-CMR01..06):
- Camiseta Camo Real — Verde Militar (15842489434496) 27,95 €
- Sudadera Cremallera Camo Nunca Se Rinde — Negro (15842489598336) 47,95 € (print en espalda)
- Hoodie Premium Camo Real — Navy (15842489794944) 49,95 €
- Zapatillas Altas Camo Hombre — Blanco (15842490220928) 74,95 € (lengüeta camo)
- Zapatillas Slip-On Camo Mujer — Salvia (15842490483072) 59,95 €
- Bandana Camo Real — Verde (15842490712448) 19,95 €

Tipos/tags siguen la convención de la tienda → entran solos en Ropa Streetwear, Camisetas,
Sudaderas & Hoodies, Calzado & Sneakers, Zapatillas Altas/Deportivas/Slip-On, Calzado
Hombre/Mujer, Novedades, Completa el Look y All-Over Print.

## Colecciones nuevas
- Cápsula Escaque — Jaque Real (701957538176, tag escaque-real)
- Cápsula Camo Real — La Corona se Camufla (701957570944, tag camo-real)
- **Cápsulas SRHOOD — Series Limitadas** (701957603712): hub smart con OR de los 29 tags
  de cápsula (174 productos). Añadir aquí el tag de cada cápsula futura.

## Notas para el próximo run
- No repetir: ajedrez/tablero ni camuflaje (ni ninguno de los 29 temas listados arriba).
  Ideas libres aún: terrazzo, ola japonesa/seigaiha, mosaico romano, ikat, caligrafía
  gótica, constelaciones zodiacales (distinto de carta estelar), vitral art nouveau…
- Precios de referencia: tee 27,95 (+2 en 2XL) / sudadera 42,95 / zip 47,95 / hoodie
  premium 49,95 / altas y deportivas 74,95 / slip-on 59,95 / calcetines 14,95 / bandana 19,95.
- Los mockups de Printful (URLs tmp de S3) caducan ~72 h: Shopify ya copió las imágenes.
- Pendiente de admin (sigue igual que el 15-07): idioma principal a español, verificar
  envío gratis ≥50 €, decidir qué hacer con los ~650 drafts antiguos.
