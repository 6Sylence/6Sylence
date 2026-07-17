# Run 2026-07-17 — Drop "Cápsula Déco — Época Dorada"

Tienda: Street Royalty Hood (srhood.com) · Printful store 18383330 (Shopify)

## Cápsula nueva (6 productos, tag `epoca-dorada`, SKU SRH-DC01…DC06)

Tema: Art Déco años 20 — paleta navy / burdeos / crema / oro (rompe con el
total-black de las cápsulas Telar, Nocturna y Street Lab). Patrones NO usados
antes: sol naciente déco, guilloché, abanico de láminas, plumaje de pavo real
geométrico, escama/concha con radios, zigurat escalonado.

| Producto | Shopify ID | Catálogo Printful | Precio |
|---|---|---|---|
| Camiseta Rayos Déco — Natural | 15840216416640 | Bella 3001 Natural (71) | 27,95 € |
| Sudadera Guilloché Real — Burdeos | 15840216547712 | Gildan 18000 Maroon (145) | 42,95 € |
| Hoodie Abanico Déco — Navy | 15840216711552 | CH M2580 Navy Blazer (380) | 49,95 € |
| Zapatillas Altas Plumaje Real Hombre — Negro | 15840216940928 | High Top Black (513) | 74,95 € |
| Zapatillas Slip-On Escama Déco Mujer — Crema | 15840217530752 | Slip On White (575) | 59,95 € |
| Calcetines Zigurat Déco — Navy | 15840218087808 | Sublimated Socks (186) | 14,95 € |

## Flujo técnico usado (documentado para futuros runs)

1. Diseños generados con `store-assets/epoca_dorada.py` (PIL, supersampling 2×):
   frontales 3600×4800 transparentes; patrones seamless 4500² (altas, 4
   placements shoe_quarters_*/shoe_tongue_*), 4650² (slip-on, shoe_left/right)
   y 1400×2400 (calcetines).
2. Subida a Shopify Files: `stagedUploadsCreate` → POST multipart → `fileCreate`.
3. Productos creados con MCP create-product (opción "Talla", tallas/SKU/precios
   idénticos al patrón de cápsulas previas; tags de color + novedades +
   hombre/mujer/unisex + calzado/all-over-print/completa-el-look según tipo).
4. Printful importa el producto Shopify solo (~1 min). Luego
   `PUT /sync/variant/{id}` con `variant_id` de catálogo + files por placement.
   ¡OJO rate limit 429!: máx ~2 req/s no basta — usar pausas de 2,5 s y backoff
   de 65 s; la primera pasada sin backoff falló en 40 variantes.
5. Mockups: el mockup-generator API falla sin campo `position` (error MG-4).
   NO hace falta: al sincronizar variantes, Printful genera solo un archivo
   `type: preview` por variante (files.cdn.printful.com/..._preview.png).
   Basta coger ese `preview_url` del primer sync variant y pasarlo a
   update-product / update-collection (Shopify lo copia a su CDN). Nota: el
   CDN de Printful devuelve 403 a urllib sin User-Agent; curl -A Mozilla ok.

## Colección / navegación

- Nueva colección smart "Cápsula Déco — Época Dorada"
  (gid://shopify/Collection/701873488256, tag `epoca-dorada`, CREATED_DESC).
- Añadida al menú principal como submenú en "Novedades" (1ª posición) y en
  "Colecciones" (1ª posición) vía `menuUpdate` (hay que reenviar el árbol
  completo de items con sus resourceId).
- Hoodie Abanico + Slip-On Escama añadidos a la colección manual "Home page".
- Los productos entran solos por reglas en: Ropa Streetwear, Camisetas,
  Sudaderas & Hoodies, Calzado & Sneakers, Zapatillas Altas, Zapatillas Bajas &
  Slip-On, Calzado Hombre/Mujer, Novedades, All-Over Print, Completa el Look,
  Menos de 40 € y Hombre/Mujer.

## Patrones ya usados (no repetir en próximos drops)

Telar: Damasco, Asanoha, Bargello, Seigaiha, Celosía, Espiga ·
Nocturna: Corona Boreal, Marea, Terrazzo, Isométrica, Jardín Nocturno, Meandro ·
Street Lab: Onda Óptica, Topografía, Oro Roto, Mosaico, Vitral, Dominó ·
Otros: Tartán, Dinastía, Cadena, Rex, Estandarte, Micro-Corona, Rombo, Llave,
Paisley (bandana), Coordenadas, Blackletter, León Heráldico ·
**Época Dorada: Rayos/Sol Déco, Guilloché, Abanico, Plumaje Pavo Real, Escama,
Zigurat.**

Ideas libres para el siguiente: ikat, azulejo portugués, panal/hexágonos,
constelaciones, mármol veteado, ondas moiré, cachemira (en prenda), ajedrez
distorsionado, laberinto.
