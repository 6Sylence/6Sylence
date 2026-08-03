# Run 2026-08-03 — Branding: portadas de colección unificadas

Tienda: Street Royalty Hood (srhood.com) · Tarea programada "Mejora el branding".

## Contexto detectado
- El sistema visual de marca (negro #0c0c0e + oro #c9a44c, corona, marco deco doble,
  serif crema, sello circular) ya estaba establecido por la corrida del 2-ago en
  las portadas `brand-cover-home.jpg`, `brand-cover-verano-royal.jpg` y
  `brand-cover-nomada-real.jpg`.
- 12 colecciones de navegación seguían usando fotos crudas de mockup de producto
  como portada, y las portadas antiguas por categoría (`camisetas.png`, etc., 10-jul)
  son escenas neón generadas por IA que chocan con la identidad actual.
- Las descripciones HTML de colecciones están bien (el "texto aplastado" que se ve
  en el campo `description` plano es solo el stripping de HTML — no tocar).

## Acciones realizadas
1. Nuevo script `store-assets/brand_covers.py` (PIL): 3 plantillas del sistema
   (rays / seal / band) que generan portadas cuadradas 1600×1600 en el estilo de casa.
2. Generadas y subidas 12 portadas (stagedUploadsCreate + fileCreate, con alt en
   español) y asignadas a sus colecciones vía collectionUpdate:
   - Novedades, Royalty Classics, Street Royalty Hombre, Street Royalty Mujer (rays)
   - Esenciales SRHOOD, Completa el Look, Deporte & Gym (navy), Eco & Orgánico (oliva) (seal)
   - Menos de 40 €, Nuevos Colores (burdeos), All-Over Print, Drop Julio 2026 (navy) (band)
   CDN: https://cdn.shopify.com/s/files/1/1003/6874/4832/files/brand-cover-<handle>.jpg
3. NOTA técnica: `collectionUpdate` con `image.src` reemplaza el CONTENIDO de la
   imagen manteniendo el path/nombre de archivo antiguo en la URL (solo sube el
   cache-buster `v=`). No es un fallo: verificado descargando las URLs — las
   portadas nuevas (1600×1600) están en vivo. No re-lanzar mutaciones por ver el
   nombre antiguo en la URL.

## Corrida 2 (mismo día, a petición del usuario)
- Añadidas 19 portadas más a `brand_covers.py` (tanda 2) y aplicadas: Ropa
  Streetwear, Accesorios, Calzado & Sneakers, Oversized Club, Crown Capsule,
  Camisetas, Sudaderas & Hoodies, Pantalones & Joggers, Chaquetas (navy),
  Gorras & Gorros, Bolsas & Mochilas, Bañadores (navy), Bikinis (navy),
  Zapatillas Altas / Bajas & Slip-On / Deportivas, Slides & Chanclas (navy),
  Calzado Hombre, Calzado Mujer (arena). Con esto, TODAS las portadas neón
  antiguas y fotos crudas de categoría quedan sustituidas; las cápsulas siguen
  con foto de producto (decisión consciente: muestran el patrón).
- Flujo simplificado verificado: stagedUploadsCreate con httpMethod PUT (una sola
  URL firmada por archivo, curl -X PUT) es mucho más manejable que POST multipart.
- collectionUpdate admite varios updates con alias en una mutación (lotes de 5-7;
  19 de golpe dio error temporal del Admin API).

## Pendiente / siguientes corridas
- Sigue pendiente (requiere admin): idioma principal a Español; la meta descripción
  de la tienda sigue en inglés (no editable por API).
