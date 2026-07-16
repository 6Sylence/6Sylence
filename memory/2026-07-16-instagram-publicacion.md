# Run 2026-07-16 — Todos los productos disponibles en Instagram (canal vinculado)

Tienda: Street Royalty Hood (srhood.com). Petición: que **todos** los productos de
Shopify estén disponibles automáticamente en la cuenta de Instagram vinculada.

## Diagnóstico
Paginando el catálogo activo con `publishedOnPublication` por publicación, detecté:
- **209 productos activos NO estaban en "Facebook & Instagram"**
  (`gid://shopify/Publication/341511569792`).
- **12 de ellos ni siquiera estaban en la Tienda online** — eran los pósters que yo
  mismo creé en runs anteriores (Royal Ink + Manifiesto); estaban ACTIVE pero sin
  publicar en NINGÚN canal → invisibles en el escaparate. Bug propio corregido aquí.

## Acción — publicación masiva ✅
Extraídos los 209 GIDs a gap_fb.txt. Generados 6 lotes de `publishablePublish`
(35 por lote, último 34) publicando cada producto en **6 canales**:
- Tienda online (340225393024)
- Facebook & Instagram (341511569792)
- Instagram Shop-AI (341089255808)
- Google & YouTube (341089419648)
- Shop (340225425792)
- TikTok (341487944064)
Los 6 lotes devolvieron `userErrors: []`.

## Verificación ✅
Muestreo a lo largo de los 6 lotes (posiciones 1, 50, 100, 150, 200, 209 + los pósters
antes invisibles): **todos `fb:true`**; los 12 pósters ahora también `online:true`.
Ejemplos: "Camiseta Wordmark — Negro", "Hoodie Arco College", "Bandana Mascotas Corona",
"Gorro Corona Lineart", "Slides Essential Navy", "Lámina Royal Ink Nº04",
"Póster Manifiesto Nº01", "Gorra Desgastada Vintage".

## Límite real para "automáticamente" (productos FUTUROS)
`publications { supportsFuturePublishing }` →
**Facebook & Instagram = false**. La Admin API NO permite activar el
auto-publicado de productos futuros para ese canal. Sólo Tienda online y
Google & YouTube soportan future publishing por API.
→ Para que los productos NUEVOS aparezcan solos en Instagram, el dueño debe activar
en el **canal Facebook & Instagram (o en Meta Commerce Manager)** la opción de
sincronizar/añadir automáticamente todo el catálogo. No es configurable por API.

## Segundo caveat (Meta)
Publicar en Shopify ≠ visible en Instagram al instante. Los productos aparecen en la
cuenta de IG sólo tras la **aprobación del catálogo por Meta** (revisión de Commerce
Manager, independiente de Shopify). Si el catálogo o la cuenta comercial no están
aprobados, nada se mostrará aunque estén publicados.

## Pendiente / próximos runs
- (Dueño) Activar auto-sync de futuros productos en el canal FB & IG / Commerce Manager.
- (Dueño) Verificar aprobación del catálogo en Meta Commerce Manager.
- Moda AI: cuando el dueño genere imágenes con modelo, hacer el swap en Shopify.
- Google Ads / PMax: bloqueado hasta reset de cuota adspirer (8 ago 2026).
