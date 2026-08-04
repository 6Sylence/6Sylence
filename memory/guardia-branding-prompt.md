# Guardia de branding SRHOOD — prompt para tarea programada

Para hacerla permanente: crear una tarea programada diaria (en el mismo sitio
donde se configuró "Mejora el branding de nuestra tienda") con este prompt.
También está montada como cron de sesión (07:04) pero caduca con la sesión.

---

Guardia de branding SRHOOD (srhood.com, Shopify MCP). Corrida incremental y
silenciosa: NO notificar si no hay nada que arreglar.

1. Lee memory/2026-08-03-branding-run.md del repo para las convenciones y
   trampas conocidas (el input `seo` de collectionUpdate/productUpdate
   REEMPLAZA el objeto completo — enviar siempre title+description; staged
   uploads con httpMethod PUT; collectionUpdate con image.src reemplaza el
   contenido manteniendo el nombre de archivo; bulkOperationRunMutation está
   bloqueado — usar mutaciones con ~25 aliases; collections(first:50) pagina —
   ordenar por ID desc).
2. Colecciones: query collections(first:30, sortKey:ID, reverse:true) con
   seo{title,description}, image{url} y description. Para cada una SIN
   seo.title o SIN seo.description: escribir SEO en voz de casa (título
   "Nombre | SRHOOD" ≤60 chars; descripción ≤155 chars destilada de su propia
   description). Para cada una SIN image: generar portada con
   store-assets/brand_covers.py (añadir entrada al dict COVERS con la variante
   band y paleta acorde), subir por staged PUT + fileCreate con alt en español
   y aplicar con collectionUpdate image.src.
3. Productos: bulk export (bulkOperationRunQuery, query "status:active") de
   id,title,seo. Para los que no tengan seo.title: generar con la regla de
   store-assets/build_seo.py ("Nombre — Color | SRHOOD" ≤60; conservar
   descripción existente o generar la genérica) y aplicar en lotes de 25
   productUpdate aliased. Detectar también títulos de producto con prefijos
   antiguos "SRHOOD | " o "Street Royalty | " y renombrarlos quitando el
   prefijo (title es campo de nivel superior, no toca seo).
4. Verificar por muestreo lo aplicado, actualizar la nota de memoria del día
   en memory/, commit y push a la rama claude/elegant-cerf-eqj9fb.
5. Notificar (PushNotification) SOLO si se arregló algo o si la corrida no
   pudo ejecutarse, con el resumen de qué se cerró.
