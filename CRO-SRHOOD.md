# CRO SRHOOD — Mejoras de conversión sobre el tema activo

Trabajo realizado sobre una copia versionada del tema publicado **"SRHood Street Royalty"** (base Horizon). Cada cambio de tema es un commit revisable en este repo; **nada se ha subido al tema en vivo**. Los únicos cambios ya efectivos en la tienda son los de Admin listados en §3 (todos reversibles con un clic).

---

## 1. Cómo aplicar los cambios del tema

Los archivos están en `shopify-theme/` con la estructura estándar. La API bloquea escrituras al tema publicado desde esta sesión, así que se aplica con Shopify CLI:

```bash
cd shopify-theme
shopify theme push --store srhood.myshopify.com --only \
  layout/theme.liquid \
  templates/product.json templates/collection.json templates/cart.json \
  templates/index.json templates/404.json templates/list-collections.json \
  templates/page.contact.json \
  sections/footer-group.json sections/header-group.json \
  sections/main-cart.liquid sections/product-information.liquid \
  sections/newsletter-popup.liquid sections/product-reviews.liquid \
  snippets/cart-drawer.liquid snippets/card-gallery.liquid snippets/meta-tags.liquid \
  snippets/free-shipping-bar.liquid snippets/cart-cross-sell.liquid \
  snippets/product-custom-badges.liquid snippets/product-rating-jsonld.liquid \
  snippets/breadcrumbs-jsonld.liquid \
  blocks/footer-copyright.liquid blocks/trust-badges.liquid \
  blocks/product-description-tabs.liquid \
  config/settings_schema.json config/settings_data.json \
  locales/es.json locales/en.default.json
```

Recomendado: probar primero contra un **duplicado del tema** (Admin → Temas → Duplicar) usando `--theme <id>` y publicar cuando esté validado.

⚠️ `config/settings_data.json` y los `templates/*.json` pisan la configuración del editor: si se retocó el tema en el editor después del 13-jul-2026, re-descargar y re-aplicar los diffs.

---

## 2. Resumen por tarea

### T1 · Prueba social (crítico)
**Problema:** Judge.me estaba instalado como app embed pero el tema no pintaba ni una estrella.
**Cambios:** bloque nativo `review` (estrellas + recuento desde los metafields `reviews.rating` que Judge.me sincroniza) bajo el título de la ficha, en las tarjetas de colección y en recomendaciones; nueva sección **Reseñas** en la ficha con el widget de Judge.me (`jdgm-review-widget`); JSON-LD `AggregateRating` opcional (`snippets/product-rating-jsonld.liquid`, desactivado por defecto porque Judge.me ya emite rich snippets — activar solo uno de los dos).
**Probar:** abrir una ficha → sección "Reseñas" visible; dejar una reseña de prueba en Judge.me → estrellas aparecen en tarjetas y ficha (los metafields tardan unos minutos en sincronizar).
**Pendiente (app):** en Judge.me activar el email post-compra automático para generar reseñas (ajuste de la app, no del tema).

### T2 · Ficha de producto (crítico)
- **Guía de tallas:** enlace "📏 Guía de tallas" junto al selector, abre modal con la página `/pages/guia-de-tallas` (ya existía y no estaba enlazada). Además cada producto conserva su tabla de medidas propia dentro del acordeón.
- **Urgencia honesta:** bloque de confianza `trust-badges` bajo el CTA: "Hecho bajo demanda — producción 2–4 días", envío 3–5 días/gratis +50 €, devolución 30 días, pago seguro. Sin contadores falsos.
- **Descripción en acordeón:** `product-description-tabs` divide automáticamente la descripción por sus `<h3>` (Características / Guía de Lavado / Guía de tallas) + fila fija "Envío y devoluciones". Fallback: si un producto no tiene `<h3>`, se muestra íntegra.
- **CTA:** "Agregar al carrito" sigue siendo el botón primario y el primero; G Pay queda debajo con las garantías inmediatamente después. Sticky add-to-cart ya estaba activo.
- **Galería:** el zoom ya estaba activo. Añadir más ángulos/lifestyle es tarea de contenido: en Printful generar mockups adicionales (modelo, espalda, detalle) y subirlos a los productos top primero. Con 2 fotos por producto la galería seguirá corta.

### T3 · Oferta unificada (crítico)
**Problema real (auditado):** 6 descuentos activos solapados — SRH10, BIENVENIDA10 y BIENVENIDO10 (tres 10% de bienvenida), ROYALTY15 (código 15% con 2+), un **15% automático sobre todo pedido**, un BXGY automático y envío gratis ≥50 €; y el banner decía "+49€" y la home "envío a toda España gratis".
**Oferta final (una historia en todo el funnel):**
1. **−10% primera compra con SRH10** (banner, pop-up, footer)
2. **Envío gratis ≥50 €** (banner + barra de progreso en carrito)
3. **Completa tu look: 2º artículo −15% automático** (BXGY, banner + cross-sell del carrito)

Barra "Te faltan X € para el envío gratis" en drawer y página de carrito (Liquid puro, se actualiza con cada cambio del carrito, umbral configurable en Ajustes del tema → Carrito).

### T4 · Carrito
- Tilde corregida: "Tu carrito **está** vacío" (`locales/es.json`).
- Cross-sell "Completa tu look" en el drawer: hasta 3 complementos de la colección `completa-el-look`, añadir directo (1 clic) si el producto tiene una sola variante.
- El campo de cupón ya estaba activo (`show_add_discount_code`) y "Pagar" ya era el CTA primario — verificado, sin cambios.

### T5 · Navegación
- El mega-menú de escritorio **ya funcionaba** (verificado en el HTML servido: los 10 submenús se renderizan con hover CSS); el hueco era móvil → drawer ahora con **acordeón de subcategorías** y separadores.
- Ítem de menú **"Sale" → "Menos de 40 €"** (aplicado en Admin; la colección ya se llamaba "Menos de 40 € — Entry Royalty", el rótulo era lo engañoso).
- **Colecciones (propuesta, NO aplicada — decisión de negocio):**
  - `Novedades` tiene 803/1051 productos porque todo el catálogo lleva el tag `novedades`. Propuesta: reservar ese tag al último drop (retirarlo en cada drop anterior) o usar la colección del drop vigente como "Novedades".
  - `Accesorios` (219) mezcla vestir con hogar/escritorio. Propuesta: quitar de sus reglas los tipos `Taza, MUG, Alfombrilla, Posavasos, Toalla, Cuaderno, Imán, Chapa, Pegatinas, Botella, Vaso, SUBLIMATION` (ya viven en Setup & Escritorio / Decoración / Regalos) y dejar solo accesorios de vestir + bolsas + fundas.
  - `Hombre` (643) y `Mujer` (682) se solapan casi al 100% porque ambas incluyen tag `unisex` — normal en POD, pero conviene curar los drops con tags `hombre`/`mujer` reales.

### T6 · Footer y contenido
- Reparado el copyright roto (`</span>` mutilado que imprimía "Street Royalty Hood**span>**") en `blocks/footer-copyright.liquid`.
- Footer completo de 4 columnas: newsletter traducido (incentivo 10% SRH10) + **iconos de pago** (`shop.enabled_payment_types`) · Comprar · Ayuda · Legal. Menús `footer-ayuda` y `footer-legal` creados en Admin.
- **Páginas creadas (en borrador, hay que publicarlas):** `/pages/faq` y `/pages/envios-y-devoluciones`. "Sobre SRHOOD", "Guía de Tallas" y "Contacto" ya existían.
- ⚠️ Las redes sociales del footer apuntan a URLs genéricas (`facebook.com/`, `instagram.com/`…). Poner los perfiles reales o quitar los iconos (Editor → Footer → Social links).

### T7 · Idioma
Traducidos todos los textos de sección en inglés: "Shop now", "View all", "Cart", "You may also like", "Continue shopping", "Page not found", "Collections", "Discover something new", "Submit", "Join our email list" y el párrafo de marca de la home. "Elegir"/"Agregar" son correctos (Elegir = abrir selector de talla; Agregar = añadir directo).
⚠️ Pendiente de datos (no tema): la opción de producto se llama **"Size"** en inglés en todo el catálogo → renombrar a "Talla" vía API (bulk `productOptionUpdate`); puedo ejecutarlo con aprobación.

### T8 · Pop-up de captación
Nueva sección `newsletter-popup`: dialog nativo accesible, retardo 8 s + exit-intent, formulario de clientes de Shopify (tags `newsletter,popup` → compatible con Shopify Email/Klaviyo), no reaparece en 15 días tras cerrarlo ni nunca tras suscribirse, y tras el alta muestra el código **SRH10**. Configurable en el editor (grupo Footer).

### T9 · Rendimiento, SEO, accesibilidad (auditoría)
Hallazgos sobre el sitio en vivo:
- **Meta description ausente en home y fichas** → corregido en tema con cadena de fallbacks (SEO manual → descripción truncada a 160 → tienda). Recomendado además: rellenar la de la home en Online Store → Preferencias.
- **BreadcrumbList JSON-LD** no existía → añadido (producto y colección). Product/Offer ya lo emitía el tema; OG/Twitter cards correctos.
- HTML de la home muy pesado (~677 KB): principal causa, cantidad de secciones y el mega-menú con productos destacados. Palanca rápida: menos productos destacados por submenú o `menu_style: collection_images`.
- Scripts: los duplicados detectados son módulos ES (el navegador los deduplica); el chat de Shopify Inbox y el widget de Google cargan async — el widget de Google (esquina inferior izquierda) es prescindible y tapa contenido en móvil: valorar desactivarlo (Admin → Apps → Google & YouTube).
- La lentitud/timeout reportada en fichas no se reprodujo vía HTTP (respuestas <1 s); recomiendo un pase de Lighthouse desde vuestra red (el sandbox de esta sesión bloquea el navegador). El sticky-ATC es un módulo de 14 KB con `fetchpriority=low` — descartado como causa.
- Accesibilidad: 1 imagen sin alt en la home (revisar en el editor); imágenes con lazy-load correcto; los diálogos (drawer, pop-up, guía de tallas) usan `<dialog>` nativo con foco atrapado y cierre con ESC; la barra de envío gratis usa `role=status`/`progressbar`. El contraste blanco/naranja sobre negro cumple AA en textos grandes; evitar naranja #F7572D para texto pequeño sobre negro (ratio ~4.0).

### T10 · Listados
- Quick-add activado también en **móvil** ("Agregar" directo con 1 variante; "Elegir" abre modal con selector de talla sin salir del listado).
- Estrellas de reseña en tarjetas de colección y recomendaciones.
- Badges **"Nuevo"** (creado <30 días, configurable) y **"Bestseller"** (pertenencia a la colección manual `bestsellers`), en la esquina opuesta a Oferta/Agotado.
- Filtros por talla/color/tipo: se gestionan con la app gratuita **Shopify Search & Discovery** (Admin → Apps → Search & Discovery → Filtros → añadir "Size", "Color", "Tipo de producto"). El tema ya tiene el bloque de filtros horizontal activo.

---

## 3. Cambios YA aplicados en Admin (reversibles)

| Cambio | Rollback |
|---|---|
| Desactivado descuento automático "15% Bienvenida Royalty" | Descuentos → activar |
| Desactivados códigos BIENVENIDO10, BIENVENIDA10, ROYALTY15 | Descuentos → activar |
| Ítem de menú "Sale" → "Menos de 40 €" | Navegación → Main menu → renombrar |
| Menús nuevos `footer-ayuda` y `footer-legal` | Navegación → eliminar |
| Páginas `faq` y `envios-y-devoluciones` **en borrador** | Páginas → eliminar |

Quedan activos: **SRH10** (10%), **envío gratis ≥50 €**, **BXGY "Completa el Look"**.

## 4. Pendiente de tu aprobación

1. **Limpieza de descripciones (173 productos activos):** prometen "15% de descuento automático" que ya no existe. Dry-run completado — 173/173 limpiezas seguras, solo se elimina esa cláusula (la de envío gratis ≥50 €, que es verdadera, se conserva). Artefactos en `shopify-admin/`: `desc_diff_resumen.csv` (qué se elimina en cada producto), `desc_cleaned_FINAL.jsonl` (HTML final propuesto), `desc_originals_FINAL.jsonl` (backup para rollback). **Di "aplica la limpieza de descripciones" y ejecuto las 173 mutaciones** (o hazlo tú importando el JSONL).
2. **Publicar** las páginas FAQ y Envíos y Devoluciones (borradores listos).
3. Renombrar opción "Size" → "Talla" en catálogo (bulk, con aprobación).
4. Reglas de colecciones (propuestas en T5).

## 5. Tres experimentos A/B iniciales

| # | Hipótesis | Variantes | Métrica primaria | Guardrail |
|---|---|---|---|---|
| 1 | El bloque de confianza + guía de tallas junto al CTA reduce la incertidumbre de talla, principal freno en moda POD | A: ficha actual · B: ficha nueva (trust-badges + guía de tallas + acordeón) | Tasa añadir-al-carrito de la ficha | Tasa de devolución por talla |
| 2 | Una sola oferta clara convierte más que múltiples ofertas contradictorias | A: banner multi-oferta antiguo · B: banner unificado (SRH10 + envío 50 €) | Conversión de sesión a compra | Margen bruto/pedido (AOV con descuento) |
| 3 | La barra de envío gratis + cross-sell del drawer sube el ticket | A: drawer sin barra ni cross-sell · B: drawer completo | AOV y % pedidos ≥50 € | Tasa de abandono de carrito |

Ejecución: apps tipo *Shoplift* o *Intelligems* para split por plantilla de tema (los dos temas: actual vs. mejorado), 2–4 semanas o ~1.000 sesiones/variante mínimo por test, un test cada vez.

## 6. Estructura del repo

- `shopify-theme/` — tema (línea base = 2 primeros commits; cada tarea = 1 commit con su diff)
- `shopify-admin/` — artefactos de la limpieza de descripciones (dry-run)
- `CRO-SRHOOD.md` — este informe
