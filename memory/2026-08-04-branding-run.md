# Run 2026-08-04 — Branding: coherencia de mensaje + tema listo para publicar

Tienda: Street Royalty Hood (srhood.com) · Tarea programada: "Mejora el branding de nuestra tienda"

## Diagnóstico

El branding visual/copy base ya estaba fuerte (runs anteriores). Los problemas reales
eran de **coherencia de promesa** entre superficies, verificados contra la
configuración real de la tienda:

- **Verdad operativa** (verificada por API):
  - Descuento automático "Envío gratis en todos los pedidos" ACTIVO (mín. 0,01 €,
    todos los países, sin tope) → el envío ES gratis siempre.
  - "15% Bienvenida Royalty" automático ACTIVO. El código **BIENVENIDA15 está
    CADUCADO** (también SRH10, BIENVENIDA10, ROYALTY15).
  - Tarifas base: gratis ≥39 €; 4,95/6,95/9,95 € por debajo — pero el descuento
    automático las anula.
- **Contradicciones encontradas**: FAQ decía "gratis desde 39 €" y recomendaba el
  código caducado BIENVENIDA15; "Envíos y Devoluciones" decía 39 €; "Sobre SRHOOD"
  decía "gratis a partir de 50 €"; 7 colecciones y 46 productos decían "≥50 €";
  Guía de Tallas usaba info@srhood.com (el resto de la tienda usa srhood@srhood.com);
  21 productos con "info@srhood.com" en la nota de seguridad de producto.

## Acciones realizadas (efecto inmediato en la tienda)

1. **Páginas** (pageUpdate): FAQ (envío gratis sin mínimo + 15% automático sin código),
   Envíos y Devoluciones (envío gratis sin mínimo), Sobre SRHOOD (promesa alineada),
   Guía de Tallas (email unificado a srhood@srhood.com).
2. **Colecciones** (collectionUpdate, desc y/o SEO): Novedades, Pantalones & Joggers,
   Gorras & Gorros, Calzado Hombre, Calzado Mujer, Verano Royal — Baño & Playa,
   Bandanas (también typo "marquetearía"→"marquetería"). Todas dicen ya
   "envío gratis en todos los pedidos".
3. **Productos**: barrido de los 600 activos (subagente). 67 con claims caducados
   (46 con "≥50 €"/"desde 50 €"/"a partir de 50 €", 21 con info@srhood.com)
   corregidos vía productUpdate. Ningún producto mencionaba códigos caducados.

## Tema (requiere 1 clic del admin)

Escritura sobre el tema publicado está bloqueada por política. Se preparó el borrador
**"SRHood v6 — branding fixes"** (id 196743561600), sincronizado byte a byte con el
tema live (v5) salvo tres arreglos:

- **sections/footer-group.json**: eliminados los enlaces sociales placeholder
  (facebook.com/, instagram.com/, youtube.com/, tiktok.com/, x.com/ sin cuenta —
  los iconos llevaban a portadas genéricas). Cuando existan perfiles reales,
  añadir las URLs en el editor de tema.
- **sections/header-group.json**: divisor de la barra de anuncios #ff6b40 → #F7572D
  (el acento de marca).
- **config/settings_data.json**: chat de Shopify Inbox de azul #0066ff → naranja de
  marca #F7572D con texto blanco.

**Pendiente del admin**: Sales channels → Themes → publicar el borrador v6.

## Pendientes que siguen requiriendo admin (heredados + nuevos)

- CRÍTICO (heredado): idioma principal a Español (Configuración → Idiomas); 68% del
  tráfico es España y aterriza en /en/.
- Contradicción legal a decidir: la home promete "Devoluciones 14 días — derecho de
  desistimiento (UE)" pero FAQ/política dicen "sin devoluciones por cambio de opinión"
  (solo defectos). En POD de diseño estándar el desistimiento UE probablemente aplica —
  conviene revisar con asesoría y alinear home + políticas.
- Crear perfiles sociales reales (o dejar los iconos fuera, como queda en v6).
- Logo inverso del tema es un JPG (srhood-logo-final.jpg, sin transparencia);
  hoy no se usa (cabecera transparente desactivada), pero convendría un PNG blanco.
