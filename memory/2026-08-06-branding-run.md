# Run 2026-08-06 — Branding: portadas de colección unificadas + copy

Tienda: Street Royalty Hood (srhood.com) · Shopify Basic · EUR

## Qué se hizo

### 1. 22 portadas de marca nuevas (colecciones que usaban fotos de producto)
Generadas con `store-assets/brand_covers.py` (PIL, 1600×1600) en el estilo de la
casa ya establecido (marco doble dorado con diamantes, icono line-art oro, título
serif crema, subtítulo tracked, watermark SRHOOD, footer MMXXVI). Colorways:
navy (categorías), negro (marca/hub), oliva (Eco), burdeos (Nuevos Colores).

Aplicadas a: Ropa Streetwear, Esenciales SRHOOD, Novedades, Street Royalty
Mujer/Hombre, Royalty Classics, Bolsas & Mochilas, Deporte & Gym, Eco & Orgánico,
Menos de 40 €, All-Over Print, Nuevos Colores, Completa el Look, Drop Julio 2026,
Cápsulas SRHOOD (hub), Zapatillas Altas/Bajas/Deportivas, Slides & Chanclas,
Calzado Hombre/Mujer, Street Lab.

Con esto, TODAS las colecciones de navegación/categoría tienen portada de marca.
Las cápsulas pequeñas (6–11 productos) conservan foto de producto a propósito:
su foto ES el arte de la cápsula.

### 2. Copy roto arreglado (9 colecciones)
Descripciones con encabezados aplanados ("El Estilo que DominaGrande es mejor")
reescritas como HTML limpio (p + ul): Oversized Club, Crown Capsule,
Chaquetas & Abrigos, Pantalones & Joggers, Cianotipo, Bandanas, Barroco,
Pitón, Marquetería.

## Aprendizajes técnicos (importante para futuros runs)
- `Shop.brand` NO existe en esta versión de API.
- `collectionUpdate` con `image.src` es **ignorado silenciosamente si la
  colección ya tiene imagen** (solo aplica altText). Solución: primero
  `image: null` (limpia síncronamente), luego `image: {src, altText}`.
- Subir archivos: `fileCreate` acepta URLs externas (raw.githubusercontent del
  repo público funciona) → devuelve MediaImage; consultar `nodes(ids:)` hasta
  `fileStatus: READY` para obtener la URL CDN. Más simple que stagedUploads.
- No hay token de Shopify en el entorno (solo PRINTFUL_API_KEY y
  POSTIZ_API_KEY); todo va por MCP.

## Pendiente (requiere admin)
- Sigue pendiente del run anterior: idioma principal a Español, verificar
  tarifa envío gratis ≥50 €, decidir sobre 653 drafts.
- 4 cápsulas con foto de producto de baja calidad como portada (Déco usa un
  PNG "preview"): candidatas a portada propia en su lenguaje visual si se
  quiere rematar.
