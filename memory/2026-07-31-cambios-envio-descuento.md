# Cambios aplicados 2026-07-31 — envío mínimo 39 € y 15% solo primera compra

## 1. Envío

Antes: tarifa 0 € en todas las zonas **más** un descuento automático de envío gratis sin
mínimo. Resultado: envío gratis siempre, en todo el mundo.

Ahora, en el «Perfil general», cada zona tiene **dos tarifas condicionales** y Shopify muestra
solo la que corresponde al subtotal del carrito:

| Zona | ≥ 39 € | ≤ 38,99 € |
|---|---|---|
| España | `Envío estándar` — 0 € | `Gastos de envío — pedido inferior a 39 €` — **4,95 €** |
| UE | `Envío estándar internacional` — 0 € | `Gastos de envío — pedido inferior a 39 €` — **6,95 €** |
| Internacional | `Envío estándar` — 0 € | `Gastos de envío — pedido inferior a 39 €` — **9,95 €** |

El nombre de la tarifa es lo que ve el cliente en el carrito, así que el cargo se explica solo
sin necesidad de banners ni avisos de «te faltan X € para el envío gratis».

Descuento automático **«Envío gratis en todos los pedidos» → DESACTIVADO**. Era imprescindible:
un descuento de envío se aplica sobre la tarifa y habría anulado también el cargo de los
pedidos pequeños.

## 2. Descuento del 15%

Antes: `15% Bienvenida Royalty`, automático, sin mínimo, sin caducidad, para todos y siempre.

**Un descuento automático no puede limitarse por cliente.** El esquema de Shopify no expone
`appliesOncePerCustomer` en `DiscountAutomaticBasicInput`; solo permite acotar por segmento de
cliente, y un segmento no evalúa a un invitado sin identificar, así que la mayoría del tráfico
se quedaría sin verlo en el carrito. Por eso:

- `15% Bienvenida Royalty` (automático) → **DESACTIVADO**
- Nuevo código **`BIENVENIDA15`** — 15%, `appliesOncePerCustomer: true`, sin caducidad,
  compatible con descuentos de envío, incompatible con otros de pedido/producto.

`appliesOncePerCustomer` es el mecanismo nativo más cercano a «solo primera compra»: Shopify
lo vincula a la cuenta o al email del checkout. Limitación conocida: alguien que compre con
otro email puede reutilizarlo. La alternativa estricta (segmento «0 pedidos») rompe el
checkout de invitado y se descartó.

Sigue activo el BxGy `Completa el Look — 15% al llevar 2+ artículos`. Se deja a propósito:
ahora empuja hacia el umbral de 39 €.

## 3. Efecto en márgenes

Con el 15% ya no aplicándose por defecto, los cinco casos negativos del informe anterior
pasan a positivo. Los calcetines (14,95 €) siguen siendo el punto débil: en pedido suelto
dejaban −1,53 € incluso sin descuento, pero ahora el comprador paga 4,95 € de envío, así que
el pedido suelto queda en **+2,90 €**. Resuelto por la vía del envío, no por precio.

## 4. Copy corregido (obligado)

Con el cambio, todo lo que prometía «envío gratis en todos los pedidos» pasó a ser falso.
Corregido:

- **Página «Envíos y Devoluciones»** — sustituido «Envío GRATIS en todos los pedidos, sin
  importe mínimo» por el detalle real de tarifas. En la página de política hay obligación
  legal de indicar el coste (TRLGDCU art. 60), así que aquí sí se especifica.
- **FAQ** — corregida la respuesta «¿Cuánto cuesta el envío?» y añadido `BIENVENIDA15` en la
  pregunta de códigos de descuento.
- **Creativos de Stories** — el pie ya no dice «ENVÍO GRATIS EN TODOS LOS PEDIDOS» sino
  «SERIES LIMITADAS · HECHO BAJO DEMANDA», y la cédula de la plancha III promociona
  `BIENVENIDA15` en lugar del 15% automático.

### PENDIENTE — 497 fichas de producto

**497 de 588 productos activos siguen con el reclamo falso en su meta descripción SEO** (y 122
de ellos prometen además «15% de descuento automático»). Están preparados y verificados los
497 textos corregidos, que eliminan el reclamo y lo sustituyen por «Envío a toda España ·
Devoluciones fáciles» — sin mencionar el umbral, según lo pedido.

No se ha ejecutado porque `bulkOperationRunMutation` está bloqueada por la política del MCP y
hay que hacerlo en 10 lotes de `productUpdate`. Ficheros listos en el scratchpad
(`lote01..10.gql`). **Es lo primero que hay que lanzar**: mientras siga así, cada ficha anuncia
envío gratis incondicional, con riesgo de práctica comercial engañosa y de suspensión en
Google Merchant Center por discrepancia de gastos de envío.
