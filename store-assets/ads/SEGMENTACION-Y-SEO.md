# Campaña «Heráldica Mineral» — segmentación, copy y SEO

Tienda: **srhood.com** · España · EUR · idioma único ES
Creatividades: `out/srhood-story-01|02|03.png` — 1080 × 1920, zonas seguras respetadas.

---

## 0. Contexto que condiciona la campaña

El cuello de botella de SRHOOD **no es la conversión, es el tráfico**: 188 sesiones en 14 días,
1 pedido en 30 días. La ficha, el catálogo y las páginas de confianza ya están bien. Por eso
esta campaña es de **adquisición en frío**, no de retargeting — el pixel apenas tiene volumen
para alimentar audiencias similares todavía.

Consecuencia práctica: **empieza por Advantage+ / segmentación amplia**, no por intereses
estrechos. Con menos de 50 conversiones semanales, el algoritmo aprende mejor con audiencia
abierta que con capas de intereses que reducen el pool y disparan el CPM.

---

## 1. Estructura de campaña (Meta — Instagram Stories)

| Nivel | Ajuste |
|---|---|
| Objetivo | Ventas → Conversiones (`Purchase`). Si en 7 días no hay ≥15 compras, baja a `AddToCart` |
| Presupuesto | CBO, 15-25 €/día para empezar. No toques nada 4 días (fase de aprendizaje) |
| Ubicación | **Manual**: Stories + Reels de Instagram. Desactiva Audience Network |
| Optimización | Máximo número de conversiones, sin límite de puja al principio |
| Atribución | 7 días clic / 1 día visita |

### Conjuntos de anuncios

**A · Amplio España** ← el que debe ganar
- Geo: España. Excluye Ceuta y Melilla (fricción logística).
- Edad 18-40, todos los géneros. Sin intereses.
- Advantage+ audience activado.

**B · Afinidad streetwear** (control, mismo presupuesto)
- Geo: España, 18-40.
- Intereses: streetwear · Hypebeast · sneakers · Nike SB · Carhartt WIP · Stüssy ·
  New Era · JD Sports · Foot Locker · cultura hip-hop · skateboarding.
- Comportamiento: *compradores online frecuentes*.

**C · Retargeting** (activar solo al superar ~1.000 visitas/mes)
- Visitantes 30 días + `AddToCart` 14 días sin compra + engagement IG 365 días.
- Excluye compradores 90 días.
- Aquí sí va la plancha III (oferta), con frecuencia limitada a 2/semana.

### Reparto de creatividades

| Plancha | Conjunto | Función |
|---|---|---|
| **I — Seda Real** (zapatilla, 74,95 €) | A y B | Gancho. Es la pieza más llamativa: es la que debe abrir |
| **II — Piedra Real** (sudadera, 49,95 €) | A y B | Precio de entrada más bajo, mayor volumen de conversión |
| **III — El Sello** (oferta) | C | Cierre: envío gratis + 15% |

Sube las tres al mismo conjunto y deja que Meta reparta. No hagas A/B manual con este volumen.

---

## 2. Copy de los anuncios

**Texto principal (variante 1 — producto)**
> La seda que vestía palacios, ahora en clave sneaker.
> Cápsula Brocado: oro sobre esmeralda, serie limitada, hecha bajo demanda.
> Envío gratis en todos los pedidos y 15% de bienvenida automático.

**Texto principal (variante 2 — marca)**
> No hacemos ropa al azar. Trabajamos por cápsulas: cada pieza nace de una misma idea
> —una piedra, una seda, una forja— reinterpretada para la calle.
> La corona no se pide. Se lleva.

**Texto principal (variante 3 — oferta, para retargeting)**
> Envío gratis en todos los pedidos. 15% de bienvenida aplicado solo. Series limitadas:
> cuando una cápsula cierra, no vuelve.

**Titulares** (máx. 40 car.)
- `Cápsula Brocado — Seda Real`
- `Streetwear con corona. Envío gratis`
- `Series limitadas · Hechas en Europa`

**Descripción**: `Envío gratis · 15% de bienvenida · Devoluciones fáciles`
**CTA**: `Comprar` (no «Más información»: penaliza la intención de compra)

---

## 3. Destinos y UTM

| Plancha | Destino |
|---|---|
| I | `srhood.com/collections/capsula-damasco-seda-real` |
| II | `srhood.com/collections/capsula-malaquita-piedra-real` |
| III | `srhood.com/collections/capsulas-srhood-series-limitadas` |

Manda a **colección, no a producto**: con tráfico frío, la colección deja elegir talla,
color y pieza hermana, y sube el valor medio del pedido.

```
?utm_source=instagram&utm_medium=paid_social&utm_campaign=heraldica_mineral
&utm_content=plancha_01_seda_real
```

---

## 4. SEO — palabras clave por página

Trabajadas en español, que es el 100% del idioma de la tienda tras el saneamiento de locales.

**Cabeza (alto volumen, alta competencia)** — para colección y home
`streetwear españa` · `ropa urbana hombre` · `sudaderas streetwear` ·
`zapatillas altas lona` · `marca streetwear española`

**Media cola (el objetivo realista a 3-6 meses)**
`zapatillas altas estampadas hombre` · `sudadera capucha estampado exclusivo` ·
`streetwear edición limitada españa` · `zapatillas lona verde esmeralda` ·
`ropa urbana diseño original`

**Larga cola (donde se gana antes)** — para ficha de producto y blog
`zapatillas altas brocado verde y oro` · `sudadera malaquita esmeralda unisex` ·
`cápsula streetwear serie limitada española` · `regalo streetwear original hombre` ·
`streetwear hecho bajo demanda españa`

### Acciones concretas

1. **Meta títulos** de las colecciones de cápsula — hoy heredan el título sin más.
   Patrón: `Cápsula Brocado — Seda Real | Streetwear Edición Limitada · SRHOOD`
2. **Texto de colección**: 120-200 palabras únicas por cápsula. Google no indexa bien una
   colección que solo es una rejilla de productos. Es la palanca SEO con mejor relación
   esfuerzo/resultado que le queda a la tienda.
3. **Blog**: ya existe `/blogs/news/capsulas-srhood-drops-limitados` con enlaces internos a
   7 cápsulas. Manténlo a 2 artículos/mes atacando larga cola.
4. **Datos estructurados**: verifica que el tema emite `Product` con `price`,
   `availability` y `aggregateRating`. Sin esto no hay resultados enriquecidos.
5. **Google Merchant Center**: el feed ya está completo (los 612 productos activos se
   publicaron en el canal Google & YouTube). Confirma que la cuenta está verificada y
   reclamada, o el feed no sirve de nada.

---

## 5. Hashtags para la publicación orgánica

No afectan al anuncio pagado; sirven para la story orgánica y el Reel.

```
#streetwear #streetwearespaña #ropaurbana #sneakers #zapatillasaltas
#modaurbana #streetstyle #edicionlimitada #hechoenespaña #srhood
#streetroyalty #outfitdeldia #sudaderas #dropnuevo #modahombre
```

---

## 6. Qué vigilar y cuándo cortar

| Métrica | Sano | Actúa si |
|---|---|---|
| CTR (salida) | > 0,8% | < 0,5% a los 3 días → cambia creatividad, no puja |
| CPM España | 4-9 € | > 15 € → audiencia demasiado estrecha, abre |
| Coste por AddToCart | < 3 € | > 6 € → el problema está en la landing |
| ROAS | > 1,8 | < 1,0 tras 7 días y 50+ clics → pausa el conjunto |
| Frecuencia | < 2,0 | > 2,5 → rota creatividad |

**Antes de gastar un euro**: comprueba que el Pixel dispara `Purchase` de verdad
(Events Manager → Probar eventos, con una compra real). Con 1 pedido en 30 días, un pixel
mal configurado se detecta tarde y arruina toda la fase de aprendizaje.

---

## 7. Aviso de márgenes

Envío gratis universal + 15% automático sobre producción bajo demanda (Printful)
comprime el margen. En un pedido de 49,95 € con perfil de envío Printful de pago
(6,99-16,99 USD), el margen puede quedar en negativo. **Antes de escalar presupuesto**,
recalcula el margen real por pieza: la campaña puede «funcionar» en ROAS aparente y aun
así perder dinero.
