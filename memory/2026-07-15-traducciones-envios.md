# Run 2026-07-15 — Traducciones EN + verificación de envíos

Tienda: Street Royalty Hood (srhood.com) · idioma principal ya = Español; EN secundario.

## Prioridad 1 — Traducciones al inglés (vía translationsRegister)
Traducidos a EN (title + body_html + product_type + meta_description) los **21 productos
más visibles**:
- **9 láminas Royal Ink** (Nº01–Nº09): p.ej. "Royal Ink Print Nº01 — Halftone Crown", etc.
- **12 productos de la colección de portada** (Home page): Bucket Hat, Jogger Wordmark,
  Camiseta Royalty Blackletter, Tote Sello Circular, Sudadera Crest, Gorra Corona,
  Camiseta Stay Royal, Hoodie Arco College, Hoodie Corona, Camiseta Wordmark,
  Zapatillas Altas Crown, Chanclas Crown.
Verificado: el producto 15827935265152 muestra "Wordmark T-Shirt — Black" en /en/. ✅

### Pendiente de traducción (backlog para próximos runs)
- Quedan ~438 productos activos SIN traducción EN (muestran español como fallback en /en/).
- Prioridad sugerida: los 2 swimwear de portada (Board Shorts / Bikini Crown Monogram,
  IDs 15825172234624 y 15825169351040 — tienen tabla de tallas larga), luego el resto
  de colecciones por tráfico. Flujo: translatableResourcesByIds (para digests) →
  translationsRegister con locale "en". Batch de ~6 por request funciona bien.

## Prioridad 2 — Envío gratis: VERIFICADO ✅
- Todos los perfiles (general + 4 de Printful) tienen tarifa **0,0 en todas las zonas
  SIN umbral**. El envío es gratis SIEMPRE, no solo >50€.
- La promesa de las fichas se cumple (y sobra). Inconsistencia menor de copy:
  unas dicen "a partir de 50€", las meta dicen "en todos los pedidos".
  RECOMENDACIÓN: unificar a "Envío gratis en todos los pedidos" (mensaje más fuerte)
  — mejora de conversión, no urgente. No se reescribieron las 459 fichas.

## Prioridad 3 y siguientes (para próximos runs, en orden)
1. Terminar traducciones EN del catálogo activo por lotes.
2. Generar mockups reales por diseño para los ~410 borradores swimwear "drop-julio"
   (IDs 15827xxx) con imagen placeholder, y activarlos.
3. Unificar copy de envío gratis.
4. Revisar el 91% de tráfico "direct" que no convierte (¿bots/ads mal etiquetadas?).
5. Seguir añadiendo producto de diseño original (nuevas series).
