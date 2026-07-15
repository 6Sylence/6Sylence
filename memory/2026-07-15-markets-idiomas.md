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

## PENDIENTE — solo admin (imposible por API, limitación de Shopify)
- **Idioma principal de la tienda → Español**: Configuración → Idiomas →
  Español → "Convertir en idioma predeterminado". Doc oficial: *"You can't change the
  primary locale using the GraphQL Admin API."* Es el último paso para que las URLs
  canónicas dejen de ser `/en/` y el español sea el idioma base real.
- Verificar en incógnito desde España que srhood.com carga en español en la raíz
  (propagación CDN puede tardar minutos).
