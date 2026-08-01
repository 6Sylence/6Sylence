# Qué añadir de Printful, y por qué el titular no son los tatuajes

Revisado el catálogo completo de Printful (295 productos base), cruzado con lo que la
tienda ya vende, y **generado y mirado uno a uno** los mockups de los finalistas. Ese
último paso no es opcional: la API no dice si un modelo lleva tatuajes ni si la foto es
de estudio o de calle, solo el nombre de la categoría, y el nombre engaña.

## Primero, la respuesta a la pregunta que hiciste

**No hay más modelos tatuados que los que ya teníamos.** Amplié la verificación a nueve
estilos nuevos y ninguno los lleva:

| Producto base | Estilo | Qué se ve de verdad |
|---|---|---|
| 463 Denim Hat | Men's Lifestyle 2 | Chico de estudio, brazos fuera de plano. Sin tatuajes |
| 327 Vintage Cap | Flat / Women's Lifestyle | Bodegón de escritorio con planta y libreta, y chica de estudio |
| 320 Sudadera AOP | Men's Lifestyle 2 / 3 / 4 | Tres modelos, ninguno tatuado |
| 388 Hoodie AOP | Men's / Women's Lifestyle 2 | Sin tatuajes |
| 744 Bandolera AOP | Men's Lifestyle 2 | Sin tatuajes |
| 200 Crop Top AOP | Women's Lifestyle 2 / On Model | Sin tatuajes |
| 618 Track Pants AOP | Men's Lifestyle 2 / 3 | Sin tatuajes |

Sigue en pie lo de `mockups_modelo.py`: **modelo tatuado solo en camiseta (754, 758) y
gorra (15130, 15099)**. Si quieres tatuajes en el resto del catálogo, no salen de
Printful — salen de fotografía propia o de IA, que es la conversación de
`IA-PRUEBA-Y-ESCENARIOS.md`.

## Segundo, lo que sí encontré, que vale más

**La tienda no vende ni una sola prenda de estampado integral.** Y las 25 cápsulas
—brocado, malaquita, tartán, meandro, camo, paisley, suminagashi— son *patrones*: cosas
diseñadas para cubrir una superficie entera. Ahora mismo cada una vive comprimida en un
rectángulo en el pecho de una sudadera lisa. Es como imprimir un papel pintado en un
sello.

Printful tiene el producto y **la fotografía es de otra liga**: pared de ladrillo,
nave industrial, estudio con foco a la vista. Nada que ver con los planos y fantasmas
que usa hoy la tienda.

| Añadir | Base | Por qué |
|---|---|---|
| **Sudadera estampado integral** | 320 | El producto que la marca lleva pidiendo desde el primer día. Tres estilos de modelo, todos editoriales |
| **Hoodie estampado integral** | 388 | Igual, y es reciclado — argumento de venta que la tienda no usa |
| **Track pants integral** | 618 | Cierra el chándal completo con la 320. Un *drop* de conjunto vende más que dos piezas sueltas |
| **Bandolera integral** | 744 | El accesorio con el que se completa el look, y en pieza pequeña el patrón se lee entero |
| **Crop top integral** | 200 | Única entrada real a público femenino con el mismo lenguaje |

Aviso técnico, que descubrí a golpes: estos cinco son `cut-sew` y **exigen la opción
`stitch_color`** en la llamada de mockup (`product_options` como **lista**, no como
objeto: `[{"name": "stitch_color", "value": "black"}]`). Sin eso devuelven 400 y no dicen
por qué de forma útil.

## Tercero, un producto que yo NO añadiría

**Las gorras bordadas de la lista corta (327 Vintage Cap, 463 Denim Hat, 92, 140, 265).**
Generé el bordado con un motivo real de la casa y el resultado está en
`contactos-aop.jpg`: el guilloché se convierte en un borrón rojo dentro de un recuadro
blanco. El bordado tiene una resolución de puntada que la línea fina de estas cápsulas
no aguanta. Es exactamente el mismo modo de fallo que documentamos para el try-on por IA.

Si quieres más tocados, que sean por **sublimación o impresión**, no bordado.

## Cómo comprobarlo tú

Los mockups generados están en el scratchpad de la sesión: `contactos-aop.jpg` (los ocho
de estampado integral y bordado) y `contactos-618.jpg` (el pantalón). Amplía el bordado
de la gorra al 100% y se ve el problema sin que haga falta que te lo cuente.
