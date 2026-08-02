# Run 2026-08-02 — Mejora de branding

Tienda: Street Royalty Hood (srhood.com) · Shopify Basic · EUR
Tarea programada: "Mejora el branding de nuestra tienda."

## Estado detectado
- La identidad verbal está muy asentada: ~60 colecciones con descripciones en
  español, voz de marca consistente (corona, "Stay Royal", quiet-streetwear).
  El HTML de las descripciones está bien estructurado (lo que parecía texto
  amazacotado era solo el campo `description` en texto plano).
- Huecos encontrados:
  - 4 colecciones SIN imagen de portada: Home page (frontpage), Verano Royal —
    Baño & Playa, Nómada Real — Patrones del Mundo, Bandanas.
  - Home page (frontpage) sin descripción.
  - 2 productos ACTIVE con naming antiguo "SRHOOD | ..." (el resto del naming
    antiguo sigue en DRAFT, sin cambios).
- El campo `Shop.brand` no existe en la versión del Admin API del MCP → el
  logo/eslogan a nivel de tienda solo se puede tocar desde el admin.

## Acciones realizadas
1. Nuevo script `store-assets/brand_covers.py` (PIL): 4 portadas de colección
   1600×1600 con la identidad de la casa (corona 5 puntas, oro/crema sobre
   negro/navy/burdeos, DejaVu serif+sans con tracking):
   - brand-cover-home.jpg — emblema art déco (corona dorada + rayos + marco).
   - brand-cover-verano-royal.jpg — sol coronado sobre olas, navy+oro.
   - brand-cover-nomada-real.jpg — 6 bandas de patrones del mundo + medallón.
   - brand-cover-bandanas.jpg — diseño tipo bandana burdeos con botehs.
2. Subidas vía stagedUploadsCreate + fileCreate y asignadas como imagen de
   colección (con alt text) a:
   - Home page (700570239360) — además se añadió descripción de marca.
   - Verano Royal — Baño & Playa (701745365376)
   - Nómada Real — Patrones del Mundo (701897769344)
   - Bandanas (702673551744)
3. Naming unificado en los 2 últimos productos activos con formato antiguo:
   - 15822994440576 → "Biker Shorts All-Over Mujer — Street Royalty"
   - 15822996046208 → "Shorts All-Over Unisex — Street Royalty"

## Pendiente / requiere admin
- Logo, colores de marca y eslogan a nivel Shop (Configuración → Marca) no son
  accesibles por API; los covers generados sirven como base del kit de marca.
- Sigue pendiente del run anterior: idioma principal a Español, revisar tarifa
  de envío gratis ≥50 €, y triaje de los 653 drafts.
