# Lotes de publicación — cómo se hacen y dónde vamos

El lote 1 (10 planchas) se escribió a mano, pieza por pieza, en una tabla dentro de
`build_feed.py`. Funciona para diez y no funciona para cien. Esta tubería deriva del
catálogo todo lo que se puede medir y deja escrito a mano solo lo que hay que decidir.

## Dónde vamos

| Lote | Piezas | Estado | Canales |
|---|---|---|---|
| 1 | 10 | publicado 31/07/2026 | Instagram |
| 2 | 100 | ver `lotes/estado-lote-02.json` | Instagram + Facebook |
| 3 | — | sin generar | — |

**La memoria entre lotes es `lotes/publicados.json`.** Guarda el handle de todo lo que
ya ha salido; `seleccionar.py` lo lee y nunca vuelve a elegirlo. Mientras ese fichero
esté en el repositorio, el lote siguiente arranca donde terminó el anterior sin que
nadie tenga que acordarse de nada.

Quedan unas 200 piezas aptas en el catálogo, así que dan para dos lotes más de 100.

## Generar el lote siguiente

```bash
cd store-assets/ads
python3 - <<'PY'          # catálogo + control de calidad del recorte
import json, catalogo as C
ps = [p for p in C.catalogo(cache="/tmp/catalogo.json") if p["product_type"] in C.TIPOS]
C.descargar(ps)
json.dump([dict(handle=p["handle"], titulo=p["title"], tipo=p["product_type"],
                precio=p["variants"][0]["price"], tags=p["tags"],
                caps=[t for t in p["tags"] if t in C.capsulas(ps)],
                file=f"{C.SRC}/{p['handle']}.jpg",
                qa=C.qa_escalado(f"{C.SRC}/{p['handle']}.jpg"))
           for p in ps], open("/tmp/qa.json", "w"), ensure_ascii=False)
PY
python3 seleccionar.py --qa /tmp/qa.json --n 100 --salida lotes/lote-03.json
python3 build_lote.py --lote lotes/lote-03.json --salida out/lote03
```

Las imágenes no se guardan en el repositorio: son ~28 MB por lote y el render es
determinista —las semillas salen del índice, no del reloj—, así que el manifiesto más
el script las reproducen idénticas en tres minutos.

## Publicar

```bash
export POSTIZ_API_KEY='...'
python3 postiz_publish.py --list                       # ids de los canales
python3 postiz_publish.py --lote lotes/lote-03.json --imagenes out/lote03 \
    --canal <ig>,<fb>                                  # simulacro
python3 postiz_publish.py --lote lotes/lote-03.json --imagenes out/lote03 \
    --canal <ig>,<fb> --confirmar                      # publica
```

Relanzar el mismo comando es seguro: el fichero de estado sabe qué salió y por qué
canal, así que continúa en vez de duplicar.

## Las tres decisiones que costaron

**El recorte se come lo claro.** `cutout` inunda el fondo desde el borde sobre una
máscara de neutralidad: una zapatilla blanca sobre fondo blanco no tiene frontera que
detenga la inundación. La métrica que lo detecta es `relleno` —cuánto de su caja
envolvente ocupa la pieza principal—: una zapatilla entera llena el 65-85%, y cuando
la inundación entra por un estampado blanco y negro y deja confeti cae al 35%. Las
Moiré pasaban `area`, `frag` y `cohes` y salían destrozadas; con `relleno > 0.45`
caen donde deben. De 486 prendas del catálogo, 298 aguantan el recorte.

**El halo tiene que contrastar, no acompañar.** El acento se mide del color dominante
de la propia foto, pero su *luminancia* va al revés que la de la pieza: pieza oscura
→ halo claro, pieza clara → halo oscuro. Antes de esa regla, las Essential verde
oliva se disolvían dentro de su propio halo oliva.

**Escalar por un solo lado saca la pieza de la vitrina.** Un mockup cenital de
deportivas es casi cuadrado; ajustado por ancho se salía del anillo y chocaba con el
titular. Ahora cada pieza se encaja por los dos lados de su caja.

## Reglas de contenido que cumplen los 100

- Ningún reclamo de envío. El umbral de 39 € no se anuncia (decisión de 31/07).
- Precio real de la variante.
- `BIENVENIDA15` solo como 15% de primera compra.
- El cuerpo del pie sale de la descripción real del producto: nada inventado.
- Texto alternativo en todas. **Postiz no lo transmite**: hay que pegarlo en la app
  (`···` → Editar → Editar texto alternativo). Está en el campo `alt` del manifiesto.

## El tope de Instagram

Meta rechaza la publicación 51 de las últimas 24 horas por cuenta. No es evitable:
un lote de 100 tarda dos días en entrar entero en Instagram. Facebook no tiene ese
tope duro. El publicador lleva la cuenta en ventana móvil sobre el fichero de estado
y para al llegar, en vez de estrellarse contra el límite.
