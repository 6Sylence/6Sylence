# Run 2026-07-15 — Configuración de Mercados e Idiomas (srhood.com)

Tienda: Street Royalty Hood (srhood.com) · Shopify Basic · EUR
Arquitectura de mercados: **Markets nueva** (mutaciones `marketUpdate` /
`webPresenceCreate|Update|Delete`; la vinculación mercado↔web presence se hace con
`MarketUpdateInput.webPresencesToAdd`, NO con un `marketId` en el web presence).

## Estado previo detectado
- srhood.com estaba servido por el web presence `gid://shopify/MarketWebPresence/74800398720`
  con `market: null` (no vinculado a ningún mercado). Ya tenía es por defecto (raíz) +
  de/fr/it/en en subcarpetas.
- Mercado **Spain** (`gid://shopify/Market/110875443584`, primario) sin web presence.
- Mercado **European Union** → streetroyaltyhood.com (es def + de/fr/it/en), 26 países UE.
- **Idioma principal de la tienda = Inglés (`en`)** ← sigue así.

## Acciones realizadas por API (ruta NO destructiva)
1. `marketUpdate(id: Spain, input:{ webPresencesToAdd:[74800398720] })`
   → srhood.com queda asignado al mercado Spain (sin borrar/recrear el web presence,
   evitando conflicto de dominio y caída del sitio).
2. `webPresenceUpdate(id: 74800398720, input:{ defaultLocale:"es", alternateLocales:["en"] })`
   → srhood.com sirve **es en la raíz** (`srhood.com/`) + **en** en `/en/`.
   Se quitaron de/fr/it de este dominio (permanecen en el dominio UE).

## Estado final
- Spain (primario): srhood.com · es (default) + en.
- European Union: streetroyaltyhood.com · es + de/fr/it/en (intacto; España NO duplicada).
- Internacional / United Kingdom: sin web presence (igual que antes).

## Idioma principal → Español (HECHO por el usuario en admin) + corrección
- El usuario cambió el idioma principal a **Español** desde el admin (único paso que
  no permite la API: *"You can't change the primary locale using the GraphQL Admin API."*).
- **Efecto secundario detectado y corregido**: ese cambio ELIMINÓ el inglés por completo
  (desapareció de shopLocales; srhood.com quedó solo es, sin /en/; la UE perdió en).
  Restaurado por API:
  1. `shopLocaleEnable(locale:"en")` → reactivado.
  2. `shopLocaleUpdate(locale:"en", {published:true})` → publicado.
  3. `webPresenceUpdate` srhood.com → alternateLocales ["en"] (vuelve /en/).
  4. `webPresenceUpdate` streetroyaltyhood.com → alternateLocales ["de","fr","it","en"].

## Estado FINAL verificado (2026-07-15)
- shopLocales: **es (primary)** + en/de/fr/it publicados.
- Spain (primario): srhood.com · es raíz + en (/en/).
- European Union: streetroyaltyhood.com · es raíz + de/fr/it/en.
- Internacional / United Kingdom: sin web presence.

## Pendiente / próximos runs
- El catálogo está en español; NO hay traducciones reales al inglés, así que /en/
  muestra español como fallback. Si se quiere inglés real: generar traducciones vía
  `translationsRegister` (candidato a próximo run).
- Verificar en incógnito desde España que srhood.com carga en español en la raíz
  (propagación CDN puede tardar minutos).
