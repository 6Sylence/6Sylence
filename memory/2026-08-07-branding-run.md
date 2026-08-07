# Run 2026-08-07 — Branding: pulido SEO + contenido editorial

Tienda: Street Royalty Hood (srhood.com) · Shopify Basic · EUR

## Estado detectado
- Las 71 colecciones tienen descripción, SEO y portada de marca (brand-cover-*) de runs
  anteriores (3–6 ago). Páginas de confianza y blog activos. Catálogo activo: 650 productos,
  todos con SEO title/description consistentes ("… | SRHOOD").
- Sin naming antiguo en activos: los 3 títulos con "SRHOOD" en activo son diseños wordmark
  legítimos, no restos del formato "SRHOOD | ...". (Quedan 76 drafts con naming antiguo,
  sin cambios — decisión pendiente del run 2026-07-15.)
- Huecos encontrados: SEO de "Bandanas" sin tildes, colección "Home page" sin SEO, y las
  cápsulas de agosto (Barroco, Pitón) sin artículo de blog (último post: 30 jul).

## Acciones realizadas
1. Bandanas (gid://shopify/Collection/702673551744): restauradas tildes en la meta
   description ("cápsula", "producción", "envío", "España").
   Nota técnica: `collectionUpdate` con `seo.description` solo BORRA el seo.title —
   hay que reenviar ambos campos siempre.
2. Home page (gid://shopify/Collection/700570239360): añadido SEO
   title "Street Royalty Hood — Streetwear con Corona | SRHOOD" + meta description.
3. Nuevo artículo publicado en el blog News:
   "Estampado integral: llegan las cápsulas Barroco y Pitón"
   (gid://shopify/Article/1005766934912, handle estampado-integral-llegan-las-capsulas-barroco-y-piton).
   Presenta las 2 cápsulas integrales de agosto con sus 2 colorways, guía de estilo
   ("cómo llevar un integral") y enlaces internos a las colecciones. Imagen destacada:
   portada de marca de Barroco ya en CDN.

## Recomendaciones pendientes (requieren admin)
- Sigue pendiente lo crítico del run 2026-07-15: idioma principal a Español
  (Configuración → Idiomas) — el tráfico es 68% España y aterriza en /en/.
- Decidir el destino de los ~650 drafts (activar por lotes o borrar duplicados).
- El campo shop.brand (logo/colores/eslogan para canales) no está disponible vía esta
  API MCP; revisar branding global en Admin → Configuración → Marca.
