#!/usr/bin/env python3
"""
Patrones de estampado integral para SRHOOD.

## Por qué existe este fichero

La tienda tiene 25 cápsulas que son **patrones** —brocado, malaquita, meandro,
camuflaje— y las vende todas comprimidas en un rectángulo en el pecho de una prenda
lisa. Printful tiene el producto de estampado integral; lo que no había era el
fichero de impresión.

Y no se podía recuperar: para una tienda conectada a Shopify, Printful devuelve el
campo `url` de cada capa **vacío** en las tres vías (`sync-variants`, `product-templates`
y la API v1), y la biblioteca de ficheros ya no existe (`/files` → 410). Así que el
estampado hay que volver a dibujarlo. Esto lo dibuja.

## La única regla técnica que importa: el mosaico tiene que cerrar

Un estampado integral se imprime sobre paneles grandes —el frontal de un hoodie son
40 × 40 cm— y el motivo se repite dentro de cada panel. Si el azulejo no cierra por
los cuatro lados, aparece una costura recta cada 16 cm y la prenda se ve barata.

Aquí eso está garantizado por construcción, no por retoque:

  · **Los campos de ruido** se construyen sumando senos y cosenos de frecuencia
    **entera** sobre el toro. Una función así vale exactamente lo mismo en x y en
    x + n, sin excepción y sin costura que disimular.
  · **Las distancias** (malaquita, camuflaje) se miden en el toro: la distancia entre
    dos puntos nunca es mayor que medio azulejo, porque se sale por un borde y se
    entra por el contrario.
  · **Los motivos dibujados** (brocado, meandro) se pegan nueve veces, en las ocho
    posiciones desplazadas además de la propia. Lo que se sale por la derecha entra
    por la izquierda ya dibujado, no cortado.

`comprobar()` verifica las tres cosas midiendo el salto entre el borde derecho y el
izquierdo y comparándolo con el salto interior típico. Si el patrón no cerrara, el
borde tendría un salto mucho mayor que el interior; se exige que no lo tenga.

## Escala

El repetido es de **16 cm**. No es un capricho: por debajo de ~12 cm el patrón se lee
como textura de tela barata y por encima de ~22 cm una talla S recorta el motivo por
la mitad. Dieciséis centímetros dan tres repeticiones a lo ancho de un pecho adulto,
que es la densidad a la que estos motivos se leen como diseño y no como fondo.

## Uso

    python3 patrones_aop.py --muestras            # una lámina por cápsula, para mirar
    python3 patrones_aop.py --generar --salida out/aop
"""
import argparse, json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Paleta de la casa, la misma de las planchas (srhood_stories).
NEGRO      = (9, 10, 12)
NEGRO_WARM = (18, 21, 20)
ESMERALDA  = (11, 46, 37)
ESM_HI     = (24, 92, 71)
ORO        = (168, 133, 63)
ORO_HI     = (228, 197, 124)
CREMA      = (240, 233, 218)
BURDEOS    = (74, 22, 32)
OLIVA      = (74, 78, 55)
ARENA      = (176, 158, 124)
COBALTO    = (26, 54, 118)
HUESO      = (241, 237, 228)
TINTA      = (30, 34, 44)

DPI = 150
REPETIDO_CM = 16.0
SS = 3          # supermuestreo para el trazo; se reduce con LANCZOS al final


def px(cm, dpi=DPI):
    return int(round(cm / 2.54 * dpi))


# ─────────────────────────────────────────────────────────── campos periódicos

def ruido(n, octavas=(2, 4, 8, 16), semilla=0, terminos=3):
    """Campo escalar exactamente periódico en n.

    Cada término es sin(fx·x + fy·y + φ) con fx, fy **enteros** y x, y medidos en
    vueltas completas de 2π sobre el azulejo. Eso hace que el valor en x coincida
    con el valor en x+n por identidad trigonométrica, no por aproximación."""
    rng = np.random.default_rng(semilla)
    ejes = np.arange(n) / n * 2 * math.pi
    y, x = np.meshgrid(ejes, ejes, indexing="ij")
    out = np.zeros((n, n), np.float64)
    for f in octavas:
        for _ in range(terminos):
            fx, fy = int(rng.integers(-f, f + 1)), int(rng.integers(-f, f + 1))
            if fx == 0 and fy == 0:
                fx = f
            out += np.sin(fx * x + fy * y + rng.uniform(0, 2 * math.pi)) / f
    return out / np.abs(out).max()


def dist_toro(n, cx, cy):
    """Distancia al punto (cx, cy) medida sobre el toro, en píxeles."""
    e = np.arange(n)
    dx = np.minimum(np.abs(e - cx), n - np.abs(e - cx))
    dy = np.minimum(np.abs(e - cy), n - np.abs(e - cy))
    return np.hypot(dx[None, :], dy[:, None])


def mediana_periodica(arr, lado):
    """Filtro de mediana que respeta el toro.

    Un filtro de vecindad mira fuera del borde, y PIL rellena repitiendo el píxel
    del extremo: eso rompe la periodicidad justo donde más se nota. Se filtra sobre
    tres copias y se recorta la del centro, que sí ha visto los vecinos correctos."""
    n = arr.shape[0]
    tri = np.tile(arr, (3, 3))
    out = Image.fromarray(tri).filter(ImageFilter.MedianFilter(lado))
    return np.asarray(out, np.float64)[n:2 * n, n:2 * n]


def rampa(v, paradas):
    """Mapea v∈[0,1] sobre una lista [(t, (r,g,b)), …] ordenada por t."""
    v = np.clip(v, 0, 1)
    ts = np.array([t for t, _ in paradas])
    cs = np.array([c for _, c in paradas], np.float64)
    idx = np.clip(np.searchsorted(ts, v) - 1, 0, len(ts) - 2)
    t0, t1 = ts[idx], ts[idx + 1]
    f = ((v - t0) / np.maximum(t1 - t0, 1e-9))[..., None]
    return (cs[idx] * (1 - f) + cs[idx + 1] * f).astype(np.uint8)


def pegar_envuelto(base, motivo, x, y):
    """Pega el motivo en las nueve posiciones del toro.

    Es lo que hace que un dibujo cruce el borde en vez de cortarse en él: la parte
    que se sale por la derecha ya está pintada entrando por la izquierda."""
    n = base.size[0]
    for dx in (-n, 0, n):
        for dy in (-n, 0, n):
            base.paste(motivo, (int(x + dx), int(y + dy)), motivo)


# ────────────────────────────────────────────────────────────────── cápsulas

def malaquita(n, semilla=11):
    """Bandas concéntricas de malaquita alrededor de varios núcleos.

    La piedra real se forma en capas alrededor de puntos de nucleación, así que el
    patrón correcto no es una onda: es la distancia al núcleo **más cercano**,
    ondulada. Al tomar el mínimo sobre varios núcleos aparecen solas las suturas
    donde se encuentran dos crecimientos, que es lo que hace que se lea como piedra
    y no como papel pintado."""
    rng = np.random.default_rng(semilla)
    d = np.full((n, n), 1e9)
    for _ in range(7):
        cx, cy = rng.integers(0, n, 2)
        d = np.minimum(d, dist_toro(n, cx, cy) * rng.uniform(0.75, 1.35))
    turb = ruido(n, (2, 4, 8), semilla + 1) * n * 0.055
    fase = (d + turb) / (n / 9.0) * 2 * math.pi
    v = 0.5 + 0.5 * np.sin(fase)
    v = np.clip((v - 0.5) * 1.9 + 0.5, 0, 1)                  # bandas más marcadas
    v = v * (0.88 + 0.12 * (0.5 + 0.5 * ruido(n, (24, 48), semilla + 2)))  # estría fina
    # Paleta apagada un punto respecto a la primera versión: en la cuadrícula de
    # colección, junto al oro del brocado y al camuflaje, el verde brillante se leía
    # casi neón y rompía la familia. La piedra real tampoco brilla así: lo que la
    # hace cara es la profundidad, no la saturación. Se bajan sobre todo los dos
    # topes altos, que son los que dan el efecto menta.
    arr = rampa(v, [(0.0, (4, 16, 13)), (0.30, (8, 33, 26)), (0.55, (14, 56, 43)),
                    (0.78, (28, 88, 67)), (0.93, (68, 128, 104)), (1.0, (132, 170, 150))])
    return Image.fromarray(arr, "RGB")


def camo(n, semilla=5):
    """Camuflaje de cuatro tonos con coronas escondidas.

    Las manchas salen de cortar un campo de ruido por cuantiles, no por umbrales
    fijos: así el reparto de los cuatro tonos es el mismo aunque cambie la semilla,
    que es lo que mantiene el camuflaje reconocible de una talla a otra."""
    f = ruido(n, (2, 3, 5, 9), semilla, terminos=4)
    f = mediana_periodica(((f + 1) * 127.5).astype(np.uint8), 9)
    qs = np.quantile(f, [0.34, 0.63, 0.86])
    capas = [NEGRO_WARM, OLIVA, ESMERALDA, ARENA]
    arr = np.zeros((n, n, 3), np.uint8)
    idx = np.digitize(f, qs)
    for i, c in enumerate(capas):
        arr[idx == i] = c
    base = Image.fromarray(arr, "RGB").convert("RGBA")
    rng = np.random.default_rng(semilla + 3)
    for _ in range(9):                                        # coronas dispersas
        lado = int(n * 0.075)
        m = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
        corona(ImageDraw.Draw(m), lado * 0.5, lado * 0.55, lado * 0.7, lado * 0.5,
               ORO + (150,))
        m = m.rotate(rng.uniform(0, 360), resample=Image.BICUBIC)
        pegar_envuelto(base, m, rng.integers(0, n), rng.integers(0, n))
    return base.convert("RGB")


def meandro(n, semilla=0, celdas=4):
    """Greca griega: espirales cuadradas encadenadas por un raíl.

    El motivo se traza sobre una retícula de 6×6 pasos por celda, así que el grosor
    del trazo y el hueco entre vueltas son el mismo número y la greca no se empasta
    al reducir. Cierra por construcción: el raíl entra y sale por el mismo alto."""
    N = n * SS
    img = Image.new("RGBA", (N, N), NEGRO + (255,))
    d = ImageDraw.Draw(img)
    c = N / celdas
    paso, gr = c / 6.0, max(2, int(c / 15))
    for fila in range(celdas):
        for col in range(celdas):
            ox, oy = col * c, fila * c
            inv = (fila + col) % 2
            pts = [(0.5, 5.5), (5.5, 5.5), (5.5, 0.5), (1.5, 0.5),
                   (1.5, 4.5), (4.5, 4.5), (4.5, 1.5), (2.5, 1.5), (2.5, 3.5)]
            if inv:
                pts = [(6 - a, b) for a, b in pts]
            camino = [(ox + a * paso, oy + b * paso) for a, b in pts]
            d.line(camino, fill=ORO, width=gr, joint="curve")
        y = fila * c + 5.5 * paso                              # raíl continuo
        d.line([(0, y), (N, y)], fill=ORO_HI, width=max(1, gr // 2))
    return img.convert("RGB").resize((n, n), Image.LANCZOS)


def epitrocoide(a, b, h, vueltas=1, pasos=2200):
    t = np.linspace(0, 2 * math.pi * vueltas, pasos)
    k = (a + b) / b
    return np.stack([(a + b) * np.cos(t) - h * np.cos(k * t),
                     (a + b) * np.sin(t) - h * np.sin(k * t)], 1)


def corona(d, cx, cy, w, h, color):
    l, r, b, t = cx - w / 2, cx + w / 2, cy + h / 2, cy - h / 2
    dip = b - h * 0.42
    d.polygon([(l, b), (l, t + h * 0.30), (l + w * 0.185, dip),
               (cx - w * 0.155, t + h * 0.12), (cx, dip - h * 0.02),
               (cx + w * 0.155, t + h * 0.12), (r - w * 0.185, dip),
               (r, t + h * 0.30), (r, b)], fill=color)


def palmeta(lado, petalos=8):
    """Palmeta de damasco: hojas acantadas en abanico, roseta al centro, corona arriba.

    La primera versión metía aquí una epitrocoide de la casa y quedaba un borrón:
    a 200 px una curva de espirógrafo tiene las vueltas más juntas que el grosor del
    trazo, así que se empasta y deja de leerse como grabado. Un damasco no se dibuja
    con una curva continua sino con **hojas separadas**, que es lo que aguanta la
    reducción y lo que hace que el motivo se reconozca desde lejos."""
    m = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(m)
    c = lado / 2
    gr = max(1, int(lado / 110))

    for i in range(petalos):                                    # hojas en abanico
        ang = math.pi * (i + 0.5) / petalos - math.pi / 2
        largo = c * (0.92 if i % 2 else 0.74)
        for signo in (1, -1):
            pts = []
            for k in range(46):
                t = k / 45
                r = largo * math.sin(math.pi * t) ** 0.62       # panza de la hoja
                desv = signo * r * 0.30 * math.sin(math.pi * t)
                rr = largo * t
                pts.append((c + rr * math.cos(ang) - desv * math.sin(ang),
                            c + rr * math.sin(ang) + desv * math.cos(ang)))
            d.line(pts, fill=ORO + (225,), width=gr, joint="curve")
        d.line([(c, c), (c + largo * math.cos(ang), c + largo * math.sin(ang))],
               fill=ORO + (120,), width=max(1, gr // 2))

    for k, rr in enumerate((0.30, 0.20, 0.11)):                 # roseta central
        d.ellipse([c - c * rr, c - c * rr, c + c * rr, c + c * rr],
                  outline=(ORO_HI if k % 2 else ORO) + (235,), width=gr)
    cl = lado * 0.20
    corona(d, c, c * 0.16, cl, cl * 0.68, ORO_HI + (235,))
    return m


def brocado(n, semilla=3):
    """Damasco en retícula ogival a media caída, con roseta de guilloché dentro.

    La media caída —columnas alternas desplazadas medio alto— es lo que distingue un
    damasco de una cuadrícula de sellos: rompe las filas horizontales que el ojo
    engancha enseguida. Para que el azulejo siga cerrando, tiene que contener un
    número **par** de columnas; con dos, el desplazamiento de la segunda vuelve a
    coincidir al saltar el borde."""
    N = n * SS
    img = Image.new("RGBA", (N, N), NEGRO_WARM + (255,))
    cols, filas = 2, 2
    cw, ch = N / cols, N / filas
    rng = np.random.default_rng(semilla)

    def ogiva(lado, color):
        """Marco ojival: dos arcos que se besan arriba y abajo."""
        m = Image.new("RGBA", (int(lado), int(lado * 1.35)), (0, 0, 0, 0))
        dd = ImageDraw.Draw(m)
        w, h = m.size
        gr = max(2, int(w / 26))
        for signo in (1, -1):
            pts = []
            for i in range(80):
                t = i / 79
                # S alargada: seno para la panza, coseno para el estrechamiento
                x = w / 2 + signo * (w / 2 - gr) * math.sin(math.pi * t) ** 0.85
                y = gr + (h - 2 * gr) * t
                pts.append((x, y))
            dd.line(pts, fill=color, width=gr, joint="curve")
        return m

    for col in range(cols):
        for fila in range(filas + 1):
            cx = (col + 0.5) * cw
            cy = (fila + 0.5) * ch - (ch / 2 if col % 2 else 0)
            marco = ogiva(cw * 0.92, ORO + (210,))
            pegar_envuelto(img, marco, cx - marco.size[0] / 2, cy - marco.size[1] / 2)

            lado = int(cw * 0.62)                               # palmeta interior
            pal = palmeta(lado, 7 + (col + fila) % 3)
            pegar_envuelto(img, pal, cx - lado / 2, cy - lado / 2)

            cl = int(cw * 0.16)                                 # corona en la unión
            m = Image.new("RGBA", (cl, cl), (0, 0, 0, 0))
            corona(ImageDraw.Draw(m), cl / 2, cl / 2, cl * 0.9, cl * 0.62, ORO + (235,))
            pegar_envuelto(img, m, cx - cl / 2, cy - ch / 2 - cl / 2)
    return img.convert("RGB").resize((n, n), Image.LANCZOS)


def tartan(n, semilla=0):
    """Tartán en el sett de la casa: burdeos de fondo, bandas negras, filetes en
    crema y oro.

    Un tartán es dos sistemas de bandas idénticos —uno vertical, uno horizontal—
    entrelazados por una sarga diagonal. Las bandas se definen como **fracciones del
    azulejo**, así que cierran por construcción. La sarga no puede ser el clásico
    `((x+y)//t) % 2` porque su periodo tendría que dividir al lado y 945 es impar:
    se usa `sin(2πk(x+y)/n) > 0`, que es exactamente periódico para cualquier k
    entero y da la misma diagonal."""
    # sett simétrico como fracciones acumuladas del lado: (hasta, color)
    SETT = [(0.30, BURDEOS), (0.34, NEGRO), (0.36, BURDEOS), (0.37, ORO),
            (0.39, BURDEOS), (0.43, NEGRO), (0.445, CREMA), (0.48, NEGRO),
            (0.78, BURDEOS), (0.80, NEGRO), (0.815, CREMA), (0.83, NEGRO),
            (0.845, ORO), (1.0, BURDEOS)]
    eje = np.arange(n) / n
    banda = np.zeros((n, 3), np.float64)
    prev = 0.0
    for hasta, color in SETT:
        m = (eje >= prev) & (eje < hasta)
        banda[m] = color
        prev = hasta
    cx = banda[None, :, :].repeat(n, 0)          # sistema vertical
    cy = banda[:, None, :].repeat(n, 1)          # sistema horizontal
    y, x = np.mgrid[0:n, 0:n]
    sarga = np.sin(2 * math.pi * 67 * (x + y) / n) > 0
    arr = np.where(sarga[..., None], cx, cy)
    # el hilo se insinúa con una trama fina, también periódica
    hilo = 0.94 + 0.06 * np.sin(2 * math.pi * 189 * x / n) * np.sin(2 * math.pi * 189 * y / n)
    return Image.fromarray(np.clip(arr * hilo[..., None], 0, 255).astype(np.uint8), "RGB")


def azulejo(n, semilla=0, celdas=3):
    """Azulejería andaluza: octagrama cobalto sobre crema, celda a celda.

    Cada celda dibuja su motivo entero dentro de sus límites y el rosetón de la
    esquina se pega **entero y centrado** en el vértice, así que el mosaico cierra
    igual que cierra un zócalo real: porque la unidad es la baldosa.

    Aquí estuvo el único defecto de costura de esta tanda, y es una trampa que
    conviene recordar: el rosetón se dibujaba como un cuarto de círculo dentro de
    un lienzo anclado en el vértice, y `pegar_envuelto` **no puede envolver lo que
    nunca se dibujó** — los otros tres cuartos no existían, así que el borde
    izquierdo llevaba arco de cobalto y el derecho crema plana, un salto de 175
    sobre 255 en 90 filas. La costura solo cierra si el motivo del vértice está
    completo antes de pegarlo."""
    N = n * SS
    img = Image.new("RGBA", (N, N), CREMA + (255,))
    d = ImageDraw.Draw(img)
    c = N / celdas
    gr = max(2, int(c / 42))
    for f in range(celdas):
        for col in range(celdas):
            ox, oy = col * c, f * c
            cx, cy = ox + c / 2, oy + c / 2
            # doble filete perimetral
            for m_ in (0.03, 0.055):
                d.rectangle([ox + c * m_, oy + c * m_, ox + c * (1 - m_), oy + c * (1 - m_)],
                            outline=COBALTO, width=gr)
            # octagrama: dos cuadrados girados 45°
            for ang0 in (0, math.pi / 4):
                r = c * 0.30
                pts = [(cx + r * math.cos(ang0 + i * math.pi / 2) * 1.15,
                        cy + r * math.sin(ang0 + i * math.pi / 2) * 1.15) for i in range(4)]
                d.polygon(pts, outline=COBALTO, width=gr)
            d.ellipse([cx - c * 0.10, cy - c * 0.10, cx + c * 0.10, cy + c * 0.10],
                      outline=COBALTO, width=gr)
            corona(d, cx, cy + c * 0.01, c * 0.11, c * 0.075, ORO + (255,))
            # rosetón entero centrado en el vértice, pegado envuelto
            r = c * 0.13
            lado = int(r * 2.2)
            ros = Image.new("RGBA", (lado * 2, lado * 2), (0, 0, 0, 0))
            dr = ImageDraw.Draw(ros)
            m = lado                                   # centro del lienzo
            for rr in (1.00, 0.68, 0.36):
                dr.ellipse([m - r * rr, m - r * rr, m + r * rr, m + r * rr],
                           outline=COBALTO, width=gr)
            for k in range(8):                         # ocho pétalos radiales
                ang = k * math.pi / 4
                dr.line([m + r * 0.36 * math.cos(ang), m + r * 0.36 * math.sin(ang),
                         m + r * 1.00 * math.cos(ang), m + r * 1.00 * math.sin(ang)],
                        fill=COBALTO, width=gr)
            dr.ellipse([m - r * 0.14, m - r * 0.14, m + r * 0.14, m + r * 0.14],
                       fill=ORO + (255,))
            pegar_envuelto(img, ros, ox - m, oy - m)
    return img.convert("RGB").resize((n, n), Image.LANCZOS)


def eslabon(n, semilla=0, filas=5):
    """Cadena Real: filas de eslabones de oro entrelazados sobre negro.

    Cada eslabón es un anillo ovalado con bisel —dos elipses concéntricas—.
    El entrelazado se dibuja por capas: primero los pares, luego los impares
    encima, y al final se repinta un arco corto del par sobre el impar para que
    la cadena alterne por-encima/por-debajo como una cadena de verdad."""
    N = n * SS
    img = Image.new("RGBA", (N, N), NEGRO + (255,))
    ancho, alto = N / 3.2, N / 6.4                 # eslabón horizontal
    paso = ancho * 0.72                            # solape entre eslabones
    gr = int(alto * 0.16)

    def anillo(color, borde):
        st = Image.new("RGBA", (int(ancho), int(alto)), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.ellipse([gr // 2, gr // 2, ancho - gr // 2, alto - gr // 2],
                   outline=color, width=gr)
        if borde:                                   # canto oscuro que separa capas
            sd.ellipse([0, 0, ancho, alto], outline=NEGRO + (255,), width=max(2, gr // 4))
            sd.ellipse([gr, gr, ancho - gr, alto - gr], outline=NEGRO + (255,),
                       width=max(2, gr // 4))
        return st

    par, impar = anillo(ORO + (255,), True), anillo(ORO_HI + (255,), True)
    # nº de eslabones por fila: entero para que la fila cierre en el toro
    por_fila = max(4, round(N / paso))
    paso_real = N / por_fila
    for f in range(filas):
        cy = (f + 0.5) * N / filas - alto / 2
        desfase = (f % 2) * paso_real / 2
        for k in range(por_fila):
            x = k * paso_real + desfase
            pegar_envuelto(img, par if k % 2 == 0 else impar, x, cy)
        # repaso de arcos para el entrelazado: un tramo del par vuelve encima
        for k in range(0, por_fila, 2):
            x = k * paso_real + desfase
            arco = par.crop((0, 0, int(ancho * 0.22), int(alto)))
            pegar_envuelto(img, arco, x, cy)
    return img.convert("RGB").resize((n, n), Image.LANCZOS)


def suminagashi(n, semilla=21):
    """Tinta al agua: anillos finos de tinta sobre papel hueso.

    La misma mecánica que la malaquita —distancia en el toro más turbulencia—
    pero invertida y afinada: pocos núcleos, mucha turbulencia y solo la cresta
    de la onda se entinta, que es como queda el suminagashi de verdad cuando la
    gota se expande y el agua la deforma.

    El trazo se mide **en píxeles, no en fase**. Recortar la onda por umbral da
    líneas cuyo grosor depende de lo deprisa que suba la fase ahí: donde el campo
    se aplana la cresta se ensancha y la tinta se emborrona en manchas que parecen
    suciedad de impresión. Dividiendo por el módulo del gradiente se convierte la
    distancia angular a la cresta en distancia real, y la línea sale del mismo
    grosor en todo el azulejo. El gradiente se calcula con `np.roll`, que es
    exactamente periódico; `np.gradient` no lo es y rompería la costura."""
    rng = np.random.default_rng(semilla)
    d = np.full((n, n), 1e9)
    for _ in range(5):
        cx, cy = rng.integers(0, n, 2)
        d = np.minimum(d, dist_toro(n, cx, cy) * rng.uniform(0.8, 1.25))
    turb = ruido(n, (2, 3, 5, 9), semilla + 1, terminos=4) * n * 0.11
    fase = (d + turb) / (n / 13.0) * 2 * math.pi
    dif = lambda eje: (np.roll(fase, -1, eje) - np.roll(fase, 1, eje)) / 2
    grad = np.hypot(dif(1), dif(0))
    # distancia angular con signo a la cresta más cercana, llevada a píxeles
    r = np.abs((fase - math.pi / 2 + math.pi) % (2 * math.pi) - math.pi)
    # 3,4 px a 150 dpi son 0,58 mm: el trazo de un pincel fino. Con 1,6 px la
    # línea medía 0,27 mm y sobre tela se leía como papel en blanco.
    ancho = 3.4 * (0.75 + 0.5 * (0.5 + 0.5 * ruido(n, (3, 7), semilla + 2)))
    tinta = np.clip(1.0 - (r / np.maximum(grad, 1e-6)) / ancho, 0, 1)
    papel = np.array(HUESO, np.float64)[None, None, :] * \
        (0.97 + 0.03 * (0.5 + 0.5 * ruido(n, (2, 5), semilla + 3)))[..., None]
    arr = papel * (1 - tinta[..., None]) + np.array(TINTA, np.float64) * tinta[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


CAPSULAS = {
    "malaquita": dict(fn=malaquita, nombre="Malaquita — Piedra Real", sigla="MLQ"),
    "brocado":   dict(fn=brocado,   nombre="Brocado — Seda Real",     sigla="BRC"),
    "meandro":   dict(fn=meandro,   nombre="Meandro — Laberinto Real", sigla="MDR"),
    "camo":      dict(fn=camo,      nombre="Camo — Camuflaje Coronado", sigla="CMO"),
    "tartan":     dict(fn=tartan,     nombre="Tartán — Herencia Real",   sigla="TRT"),
    "azulejo":    dict(fn=azulejo,    nombre="Azulejo — Cerámica Real",  sigla="AZL"),
    "eslabon":    dict(fn=eslabon,    nombre="Eslabón — Cadena Real",    sigla="ESL"),
    "suminagashi": dict(fn=suminagashi, nombre="Suminagashi — Tinta al Agua", sigla="SMG"),
}


# ────────────────────────────────────────────────────────────── comprobación

def comprobar(tile):
    """¿Cierra el mosaico? Compara el salto de la costura con el de sus vecinos.

    La versión anterior comparaba contra la media de **todo** el azulejo, y esa
    referencia engaña en los dos sentidos:

    - **Falso positivo.** En un patrón disperso —tinta fina sobre papel liso— la
      media interior es minúscula, así que cualquier línea que pase por el borde
      dispara el ratio. El suminagashi daba 2.82 y no tenía nada roto: tenía una
      línea de tinta en x=0, que se ve como una línea, no como una costura.
    - **Falso negativo.** El azulejo daba 1.66 —dentro del umbral— teniendo una
      discontinuidad saturada de 175 sobre 255. La media global estaba inflada
      por los filetes de cobalto del interior de cada baldosa y tapaba el salto.

    La referencia correcta es **local**: los cuatro saltos inmediatamente a cada
    lado de la costura. Una discontinuidad real destaca sobre su propia vecindad;
    el contenido que casualmente cae en el borde, no. Con esto el azulejo roto
    marcaba 990 y el suminagashi sano 1.31.

    Devuelve (ok, ratio_x, ratio_y); 1.0 es perfecto."""
    a = np.asarray(tile, np.float64)

    def eje(u):
        b = a if u == 0 else a.transpose(1, 0, 2)
        salto = lambda i, j: np.abs(b[:, i] - b[:, j]).mean()
        costura = salto(-1, 0)
        # Un salto invisible es correcto aunque su vecindad sea exactamente plana,
        # que es el caso del brocado y el meandro: 0 sobre 0 no es un defecto.
        if costura < 0.5:
            return 0.0
        vecinos = np.mean([salto(-2, -1), salto(-3, -2), salto(0, 1), salto(1, 2)])
        return costura / max(vecinos, 1e-9)

    rx, ry = eje(0), eje(1)
    return (rx < 2.0 and ry < 2.0), round(rx, 2), round(ry, 2)


def panel(tile, ancho_px, alto_px, repetido_px):
    """Repite el azulejo hasta cubrir el panel del producto."""
    t = tile.resize((repetido_px, repetido_px), Image.LANCZOS)
    out = Image.new("RGB", (ancho_px, alto_px))
    for y in range(0, alto_px, repetido_px):
        for x in range(0, ancho_px, repetido_px):
            out.paste(t, (x, y))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--muestras", action="store_true")
    ap.add_argument("--generar", action="store_true")
    ap.add_argument("--spec", default="spec-aop.json")
    ap.add_argument("--salida", default="out/aop")
    ap.add_argument("--solo", help="solo estas cápsulas, separadas por comas")
    a = ap.parse_args()

    n = px(REPETIDO_CM)
    quiero = set(a.solo.split(",")) if a.solo else set(CAPSULAS)
    tiles = {}
    for clave, cfg in CAPSULAS.items():
        if clave not in quiero:
            continue
        t = cfg["fn"](n)
        ok, rx, ry = comprobar(t)
        print(f'{clave:10s} {n}×{n}px  costura x{rx} y{ry}  {"✓" if ok else "✗ NO CIERRA"}')
        tiles[clave] = t

    if a.muestras:
        os.makedirs(a.salida, exist_ok=True)
        for clave, t in tiles.items():
            # 2×2 azulejos: si hubiera costura, aquí se vería como una cruz
            m = Image.new("RGB", (n * 2, n * 2))
            for i in range(2):
                for j in range(2):
                    m.paste(t, (i * n, j * n))
            m.resize((900, 900), Image.LANCZOS).save(f"{a.salida}/muestra-{clave}.jpg",
                                                     quality=92)
        print("→ muestras en", a.salida)

    if a.generar:
        spec = json.load(open(a.spec))
        os.makedirs(a.salida, exist_ok=True)
        indice = []
        for pid, s in spec.items():
            # Dentro de un producto casi todas las colocaciones miden lo mismo —el
            # frontal, la espalda y las mangas de un hoodie son 40×40 cm—, así que
            # un solo fichero sirve para todas y se sube una vez, no seis.
            medidas = {}
            for pl, info in s["placements"].items():
                if not pl.startswith("label"):
                    medidas.setdefault(tuple(info["px"]) + (info["dpi"],), []).append(pl)
            for clave, t in tiles.items():
                for (w, h, dpi), pls in medidas.items():
                    f = f'{a.salida}/{clave}-{pid}-{w}x{h}.jpg'
                    panel(t, w, h, px(REPETIDO_CM, dpi)).save(f, quality=95, subsampling=0)
                    indice.append(dict(capsula=clave, producto=int(pid),
                                       nombre=s["nombre"], colocaciones=pls,
                                       px=[w, h], fichero=os.path.basename(f),
                                       mb=round(os.path.getsize(f) / 1e6, 2)))
        json.dump(indice, open(f"{a.salida}/indice.json", "w"), ensure_ascii=False, indent=1)
        print(f"{len(indice)} ficheros de impresión · "
              f"{sum(i['mb'] for i in indice):.0f} MB en {a.salida}")
