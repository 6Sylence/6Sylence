# Lote de 10 publicaciones — Instagram feed

Creatividades: `out/srhood-feed-01..10.png` — **1080 × 1350 (4:5)**, el formato que más
superficie ocupa en el feed. Mismo sistema visual que las Stories (Heráldica Mineral):
guilloché de oro trazado por acumulación, corona en cabecera, Italiana para el titular y
monoespaciada para la ficha técnica. Lo único que cambia entre planchas es el **acento
cromático** de cada cápsula — es lo que da ritmo a la cuadrícula sin romper la marca.

> **Nada de envío gratis en los textos.** El umbral de 39 € no se anuncia, así que ninguna
> publicación lo menciona ni promete envío gratuito. El gancho es `BIENVENIDA15`.

---

## 1 · SEDA REAL — Zapatilla alta Brocado (74,95 €)

> La seda que vestía palacios, ahora vulcanizada para el asfalto.
>
> Cápsula Brocado: medallones de oro sobre verde noche, de borde a borde. Serie limitada,
> hecha bajo demanda — cuando la cápsula cierra, no vuelve.
>
> 🔗 Link en bio · Código BIENVENIDA15 en tu primera compra

## 2 · PIEDRA REAL — Sudadera Malaquita (49,95 €)

> La malaquita fue piedra de reyes antes de ser nuestra.
>
> Medallón esmeralda con doble anillo de oro y la corona al centro. Felpa premium de gramaje
> alto, corte unisex.
>
> La corona es mineral. 🔗 Link en bio

## 3 · CIFRA REAL — Sudadera Cifra (49,95 €)

> Una cifra es el monograma de la realeza. Esta es la nuestra.
>
> La «SR» coronada y ceñida en laurel, en crema sobre negro absoluto. Sin ruido: presencia.
>
> Cápsula Nº01 de la línea Cifra Real. 🔗 Link en bio

## 4 · HIERRO Y ORO — Zapatilla alta Forja (74,95 €)

> Herrería española convertida en sneaker.
>
> Celosía de volutas de hierro pulido con rosetas y remaches en oro, de puntera a talón.
> La puerta del reino, en tus pies.
>
> 🔗 Link en bio · BIENVENIDA15

## 5 · VICTORIA REAL — Sudadera Laurel (49,95 €)

> El laurel no se compra: se gana. Nosotros solo lo bordamos.
>
> Corona laureada al pecho sobre felpa premium. Cápsula Laurel — Victoria Real.
>
> 🔗 Link en bio

## 6 · ORO EN LA GRIETA — Sudadera Kintsugi (49,95 €)

> El kintsugi japonés repara la cerámica rota con oro. No esconde la grieta: la corona.
>
> Luna partida y vetas doradas sobre negro. La pieza más nuestra de toda la casa.
>
> Lo roto también reina. 🔗 Link en bio

## 7 · INTARSIA REAL — Zapatilla alta Marquetería (74,95 €)

> Parquet de palacio, para la calle.
>
> Taracea isométrica en nogal, arce y palo rosa con filetes de latón. Cápsula Marquetería —
> Intarsia Real, serie limitada.
>
> 🔗 Link en bio

## 8 · DOS CARAS — Bucket Hat Brocado reversible (34,95 €)

> Dos sombreros, un solo linaje.
>
> Brocado de oro sobre esmeralda por fuera; rosetas doradas sobre marfil por dentro. Le das
> la vuelta y cambias de fit.
>
> 🔗 Link en bio

## 9 · EL REMATE — Bandana Meandro (19,95 €)

> Lo que separa un fit de un fit terminado.
>
> Greca griega en terracota, laberinto central y coronas en las esquinas. Al cuello, en la
> muñeca o en el bolsillo trasero.
>
> 🔗 Link en bio

## 10 · LA CORONA NO SE PIDE

> Se lleva.
>
> No hacemos ropa al azar: trabajamos por cápsulas. Cada una nace de una idea —una piedra,
> una seda, una forja— reinterpretada para la calle. Cuando una cierra, no vuelve.
>
> Primera compra: **BIENVENIDA15**, 15% de descuento. 🔗 Link en bio

---

## Hashtags (ponlos en el primer comentario, no en el pie)

Mezcla siempre 3 niveles: nicho, medio y marca. Evita los de millones de posts: te entierran.

**Base fija (marca + nicho)**
```
#srhood #streetroyalty #streetwearespaña #modaurbanaespaña #streetwearmadrid
#edicionlimitada #hechobajodemanda #ropaurbana
```

**Rotatorios por tipo de pieza**
- Zapatillas → `#zapatillasaltas #sneakerheadspain #customsneakers #calzadostreetwear`
- Sudaderas → `#sudaderas #hoodiestyle #outfitdeldia #modahombre #modamujer`
- Accesorios → `#bucketthat #bandana #accesoriosurbanos #completaellook`
- Marca/statement → `#streetstyle #urbanfashion #diseñoespañol #marcaespañola`

Máximo 15-20 en total. Repetir el mismo bloque en todos los posts penaliza el alcance.

## Orden de publicación sugerido

La cuadrícula se llena de derecha a izquierda y de abajo a arriba, así que **publica en este
orden** para que las tres primeras filas queden equilibradas de color:

```
1 · SEDA REAL        (verde)      →  fila 1
5 · VICTORIA REAL    (verde)
4 · HIERRO Y ORO     (oro)
─────────────────────────────────────────
2 · PIEDRA REAL      (verde)      →  fila 2
7 · INTARSIA REAL    (nogal)
3 · CIFRA REAL       (oro)
─────────────────────────────────────────
9 · EL REMATE        (terracota)  →  fila 3
6 · ORO EN LA GRIETA (oro)
8 · DOS CARAS        (verde)
─────────────────────────────────────────
10 · LA CORONA                    →  cierre / fijado arriba
```

Fija el nº 10 como publicación destacada: es el que explica la marca a quien llega nuevo.

**Cadencia**: 3 por semana (L-X-V). Diez publicaciones cubren tres semanas y algo. No las
sueltes todas de golpe — la cuadrícula se construye, no se vuelca.

## Reutilización

Cada plancha de feed funciona también como Story recortando a 1080×1920 con el producto
centrado, pero es mejor usar las tres Stories dedicadas (`srhood-story-01..03.png`), que ya
respetan las zonas seguras de la interfaz.

Para regenerar todo: `python3 build_feed.py` (descarga los originales del CDN y reconstruye
las diez planchas en unos 12 segundos). Cambiar precio, titular o producto es editar la
tabla `POSTS` al final del script.
