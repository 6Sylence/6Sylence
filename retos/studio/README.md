# Studio — generador de premios

Genera por código los premios de las 12 semanas: el personaje, el cuento, la lámina
imprimible y el diploma de hito.

El contenido es el coste recurrente de este producto, no los servidores: son 52 semanas
al año de material nuevo. Por eso se genera con un sistema y no a mano, igual que
`store-assets/royal_ink.py` en la raíz del repositorio.

## Uso

```bash
cd retos/studio
pip install -r requirements.txt

python generate.py                  # las 12 semanas, todo
python generate.py --week 3         # solo la semana 3
python generate.py --only sheets    # solo las láminas
python generate.py --contact        # además, la hoja de control
```

La salida va a `retos/assets/`, **fuera del control de versiones**: son archivos
derivados y se regeneran en segundos. Lo que se versiona es el generador.

## Qué produce

| Archivo | Formato | Qué es |
|---|---|---|
| `assets/wNN/personaje.png` | PNG 1200×1200 | La tarjeta del personaje. Es el premio que se ve en la app. |
| `assets/wNN/historia.pdf` | PDF, 4 páginas | Portada y tres páginas de cuento. |
| `assets/wNN/imprimible.pdf` | PDF A4, 300 ppp | La lámina que la familia imprime en casa. |
| `assets/hitos/diploma-sNN.pdf` | PDF A4 | Solo semanas 4, 8 y 12. |

Las rutas replican el `asset_key` que sirve la API: `w03/personaje` → `assets/w03/personaje.png`.

## De dónde sale cada cosa

Los **títulos** se leen de `retos/backend/app/content/weeks.py`, que es la única fuente de
verdad. El nombre del premio que muestra la app y el que sale impreso no pueden
desincronizarse porque son el mismo dato.

El **texto de los cuentos** y la especificación de cada lámina viven en `scripts.py`. No
están en el backend a propósito: la API solo necesita saber que el cuento existe y cómo se
llama, no su contenido.

## Los cinco tipos de lámina

| Tipo | Qué hace el niño |
|---|---|
| `colorear` | Colorea al personaje de la semana, en contorno |
| `buscar` | Encuentra y colorea solo unas formas concretas entre muchas |
| `trazos` | Repasa cuatro caminos punteados: onda, zigzag, bucles y montañas |
| `recortar` | Recorta cuatro piezas por su línea discontinua |
| `dibujar` | Dibuja libre dentro de un marco, con renglones para que el adulto escriba |

## Cómo se dibujan los personajes

Un solo constructor paramétrico (`fauna.py`) en lugar de doce dibujos sueltos: así los doce
parecen del mismo mundo, que es lo que convierte una colección de premios en una colección.
Cada animal es una combinación de orejas, ojos, hocico y un extra (antifaz, púas, caparazón,
chorro, antenas, cresta).

Cada uno se dibuja en dos modos con la misma función: **a color** para el premio de la app y
**en contorno** para la lámina de colorear. Reutilizar la figura es lo que hace que colorear
al personaje se sienta como colorear *a su* personaje.

## Antes de publicar

- **Sustituir la tipografía.** DejaVu está en cualquier máquina Linux y sirve para generar y
  revisar, pero no es una fuente infantil. Hay que poner una redondeada con licencia
  comercial en `studio/fonts/` como `bold.ttf` y `regular.ttf`; `palette.py` las coge sola.
- **Revisar cada lámina impresa en papel.** Lo que se ve bien en pantalla puede salir con la
  línea demasiado fina en una impresora doméstica.
- **Nada de personajes con licencia.** Todo lo que hay aquí es original y generado. Que siga
  así: un parecido con un personaje conocido es la vía rápida al cierre de la cuenta.
