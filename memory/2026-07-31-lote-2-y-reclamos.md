# Lote 2 (100 publicaciones) y promesas caducadas en las fichas

## Lo que hay que mirar primero

**176 productos anunciaban en su descripción dos cosas que la tienda ya no cumple.**
Apareció al leer las fichas para escribir los pies del lote 2:

| Promesa en la ficha | Realidad desde el 31/07 |
|---|---|
| «Envío gratis … 50 €» (12 redacciones distintas) | El umbral es **39 €** y se decidió **no anunciarlo** |
| «15% de descuento automático en el carrito» | Es `BIENVENIDA15`, **código de primera compra**, no automático |

La pasada del 31/07 corrigió las meta descripciones y dejó el `body_html` intacto, así
que el error sobrevivió donde más se lee: la propia página de producto. El cliente ve
una promesa, llega al checkout y no está — que es la peor forma de perder un carrito,
además del problema de publicidad engañosa.

**Estado: 61 corregidos, 115 pendientes.** El corrector es
`store-assets/ads/corregir_reclamos.py`, verificado sobre los 176 (cero reclamos
supervivientes en el simulacro). No se aplicó entero porque el único camino de
escritura disponible es la MCP de Shopify, y mandar 176 descripciones por ahí consume
un contexto enorme. **Con un token de Admin en el entorno se termina en segundos:**

```bash
SHOPIFY_TOKEN=shpat_... SHOPIFY_TIENDA=srhood.myshopify.com \
    python3 store-assets/ads/corregir_reclamos.py --aplicar
```

Antes de escribir se comprobó que el `body_html` de `/products.json` es **byte a byte
idéntico** al `descriptionHtml` de Admin, sobre varios productos de distinta longitud;
si no lo fuera, el corrector borraría texto bueno.

La tercera promesa, «devoluciones en 30 días», estaba en 8 fichas y **ya está
corregida** (0 supervivientes). El plazo real es de **14 días naturales** —derecho de
desistimiento de la UE, con el porte de vuelta a cargo del cliente—, tal como dice la
Política de Reembolso. Se quitó la frase en vez de cambiar 30 por 14: la ficha de
producto no es el sitio para repetir condiciones, y añadir plazos sueltos es
exactamente lo que produjo este lío. Si algún día interesa como argumento de venta,
que se ponga a propósito y con el matiz de quién paga la devolución.

**Pendiente de decisión (no tocado):** la Política de Envío y los Términos del
Servicio dicen «Envío Gratuito en Todos los Pedidos — sin mínimo de compra». Eso
contradice el umbral de 39 € que está configurado y activo:

| Zona | Desde 39 € | Por debajo de 39 € |
|---|---|---|
| España | gratis | 4,95 € |
| UE | gratis | 6,95 € |
| Internacional | gratis | 9,95 € |

Esto es más grave que las descripciones: la página de condiciones es la que vincula.
Texto propuesto, a la espera del visto bueno:

> **Gastos de envío**
> El envío es gratuito en pedidos a partir de 39 €. En pedidos inferiores se aplica un
> cargo de envío que se muestra en el carrito antes de finalizar la compra.

## Lote 2

100 publicaciones a Instagram y Facebook, mismo sistema Heráldica Mineral que el
lote 1. Ver `store-assets/ads/LOTES.md` para la tubería y cómo generar el lote 3.

- **Selección:** 486 prendas del catálogo → 298 aguantan el recorte → 100 elegidas con
  cuota por cápsula y por tipo, de 25 cápsulas distintas.
- **No repite:** `lotes/publicados.json` guarda los handles publicados y
  `seleccionar.py` los excluye. Quedan ~200 aptas, o sea dos lotes más.
- **Progreso de envío:** `lotes/estado-lote-02.json`. Relanzar el mismo comando
  continúa donde se quedó; no duplica.
- **Instagram para a las 50/24 h** — límite de Meta, no nuestro. El lote entero tarda
  dos días en entrar en Instagram; Facebook no tiene ese tope.

### Tres cosas que costaron y conviene no volver a descubrir

1. **El recorte se come lo claro.** La métrica que lo detecta es `relleno` (cuánto de
   su caja envolvente ocupa la pieza): una zapatilla entera llena el 65-85%, y cuando
   la inundación entra por un estampado blanco y negro y deja confeti cae al 35%. Las
   Moiré pasaban los filtros anteriores y salían destrozadas.
2. **El halo tiene que contrastar con la pieza, no acompañarla.** El tono se mide de la
   foto pero la luminancia va al revés: pieza oscura → halo claro, pieza clara → halo
   oscuro. Antes, las Essential verde oliva se disolvían dentro de su halo oliva.
3. **Encajar por un solo lado saca la pieza de la vitrina.** Un mockup cenital de
   deportivas es casi cuadrado y, ajustado por ancho, chocaba con el titular.

### Textos

Los pies salen de la descripción real de cada producto, así que no hay nada inventado.
Escrito a mano: los ganchos de las 25 cápsulas y los titulares que colisionaban (cinco
planchas decían ESSENTIAL). Verificado sobre las 100: ningún reclamo de envío.

**El texto alternativo sigue sin poder enviarse por Postiz** y hay que pegarlo a mano
en la app. Está en el campo `alt` del manifiesto.

## Clave de Postiz

Sigue pendiente de rotar: se transmitió en claro en la conversación del 31/07. Vive
solo en `$SCRATCHPAD/.postiz_key` (600), fuera del repositorio.
