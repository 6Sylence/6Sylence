"""Los doce personajes, dibujados por código.

Un solo constructor paramétrico en lugar de doce dibujos sueltos: así los doce
parecen del mismo mundo, que es lo que convierte una colección de premios en
una colección. Cambiar una proporción los cambia a todos a la vez.

Cada animal se dibuja en dos modos:

- **color**: el premio que el niño ve en la app.
- **contorno**: el mismo dibujo sin relleno, que es la lámina para colorear.
  Reutilizar la figura es lo que hace que colorear al personaje se sienta como
  colorear *a su* personaje.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from PIL import ImageDraw

from palette import INK, LINE, WHITE, tint


# Un animal no ocupa solo su círculo: las antenas, el chorro, las púas y el
# caparazón sobresalen. Este es el alto real que ocupa cualquiera de los doce,
# en múltiplos del radio y hacia cada lado. Quien coloque un animal tiene que
# reservar `r * VERTICAL_EXTENT` arriba y abajo, o le cortará la cabeza.
VERTICAL_EXTENT = 1.5


@dataclass(frozen=True)
class Animal:
    fur: tuple[int, int, int]
    muzzle: tuple[int, int, int] = (245, 236, 224)
    ears: str = "round"  # round | pointed | tufted | long | none
    eyes: str = "dot"  # dot | disc
    nose: str = "dot"  # dot | triangle | beak | none
    extra: str = ""  # mask | spikes | shell | spout | antennae | crest | none
    cheeks: bool = True
    whiskers: bool = False
    ear_ratio: float = 0.42


ANIMALS: dict[str, Animal] = {
    "nutria": Animal(fur=(146, 110, 84), ears="round", nose="dot", whiskers=True, ear_ratio=0.34),
    "camaleon": Animal(fur=(126, 168, 74), ears="none", eyes="disc", extra="crest", nose="dot"),
    "loro": Animal(fur=(214, 86, 74), ears="none", nose="beak", extra="crest", muzzle=(250, 214, 120)),
    "mapache": Animal(fur=(150, 152, 160), ears="pointed", extra="mask", nose="triangle"),
    "oso": Animal(fur=(166, 124, 88), ears="round", nose="triangle", ear_ratio=0.46),
    "hormiga": Animal(fur=(104, 76, 62), ears="none", extra="antennae", nose="dot", cheeks=False),
    "rana": Animal(fur=(94, 176, 118), ears="none", eyes="disc", nose="dot", muzzle=(214, 240, 220)),
    "buho": Animal(fur=(152, 122, 94), ears="tufted", eyes="disc", nose="beak", muzzle=(248, 226, 176)),
    "erizo": Animal(fur=(176, 148, 124), ears="round", extra="spikes", nose="triangle", ear_ratio=0.28),
    "tortuga": Animal(fur=(108, 158, 92), ears="none", extra="shell", nose="dot"),
    "zorro": Animal(fur=(230, 128, 72), ears="pointed", nose="triangle", ear_ratio=0.5),
    "ballena": Animal(fur=(80, 152, 188), ears="none", extra="spout", nose="none", muzzle=(214, 236, 246)),
}


class Pen:
    """Pincel que sabe si está dibujando a color o solo el contorno."""

    def __init__(self, draw: ImageDraw.ImageDraw, outline_only: bool, width: int):
        self.draw = draw
        self.outline_only = outline_only
        self.width = max(2, width)

    def _fill(self, color):
        return WHITE if self.outline_only else color

    def ellipse(self, box, color, stroke: bool = True):
        self.draw.ellipse(
            box, fill=self._fill(color), outline=LINE if stroke else None, width=self.width
        )

    def polygon(self, points, color, stroke: bool = True):
        self.draw.polygon(points, fill=self._fill(color), outline=LINE if stroke else None)
        if stroke and self.width > 1:
            self.draw.line(list(points) + [points[0]], fill=LINE, width=self.width, joint="curve")

    def solid_ellipse(self, box, color):
        """Detalle que se dibuja igual en ambos modos, como una pupila."""
        self.draw.ellipse(box, fill=color)

    def line(self, points, color=LINE, width: int | None = None):
        self.draw.line(points, fill=color, width=width or self.width, joint="curve")

    def arc(self, box, start, end, color=LINE, width: int | None = None):
        self.draw.arc(box, start, end, fill=color, width=width or self.width)


def draw_animal(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    r: float,
    name: str,
    outline_only: bool = False,
) -> None:
    """Dibuja la cara de un animal centrada en (cx, cy) con radio r."""
    animal = ANIMALS[name]
    pen = Pen(draw, outline_only, width=max(3, int(r * 0.035)))

    _draw_behind(pen, animal, cx, cy, r)
    _draw_ears(pen, animal, cx, cy, r)
    pen.ellipse([cx - r, cy - r, cx + r, cy + r], animal.fur)
    _draw_mask(pen, animal, cx, cy, r)
    _draw_eyes(pen, animal, cx, cy, r)
    _draw_snout(pen, animal, cx, cy, r)
    _draw_front(pen, animal, cx, cy, r)


# ==================== Piezas ====================


def _draw_behind(pen: Pen, animal: Animal, cx: float, cy: float, r: float) -> None:
    if animal.extra == "spikes":
        for i in range(11):
            angle = math.radians(190 + i * 16)
            base = r * 0.94
            tip = r * 1.34
            spread = math.radians(7)
            pen.polygon(
                [
                    (cx + base * math.cos(angle - spread), cy + base * math.sin(angle - spread)),
                    (cx + tip * math.cos(angle), cy + tip * math.sin(angle)),
                    (cx + base * math.cos(angle + spread), cy + base * math.sin(angle + spread)),
                ],
                (94, 74, 60),
            )
    elif animal.extra == "shell":
        pen.ellipse(
            [cx - r * 1.15, cy + r * 0.12, cx + r * 1.15, cy + r * VERTICAL_EXTENT], (196, 148, 86)
        )
        for i in range(3):
            offset = r * (0.44 - i * 0.36)
            pen.arc(
                [cx - r * 0.72 - offset, cy + r * 0.28, cx + r * 0.72 + offset, cy + r * 1.3],
                200,
                340,
            )
    elif animal.extra == "spout":
        # Chorro en abanico. Tres gotas pequeñas en fila se leían como tres
        # puntos sueltos; separarlas en altura y ángulo hace evidente que
        # salen de la ballena.
        pen.line([(cx, cy - r * 0.98), (cx, cy - r * 1.16)], width=max(4, int(r * 0.07)))
        for dx, dy, scale in ((-0.42, 1.24, 0.18), (0.0, 1.28, 0.22), (0.42, 1.24, 0.18)):
            pen.ellipse(
                [
                    cx + r * dx - r * scale,
                    cy - r * (dy + scale),
                    cx + r * dx + r * scale,
                    cy - r * (dy - scale),
                ],
                (170, 214, 236),
            )


def _draw_ears(pen: Pen, animal: Animal, cx: float, cy: float, r: float) -> None:
    if animal.ears == "none":
        return
    er = r * animal.ear_ratio
    inner = tint(animal.fur, 0.45)

    for side in (-1, 1):
        ex = cx + side * r * 0.72
        ey = cy - r * 0.66
        if animal.ears == "round":
            pen.ellipse([ex - er, ey - er, ex + er, ey + er], animal.fur)
            pen.ellipse(
                [ex - er * 0.5, ey - er * 0.5, ex + er * 0.5, ey + er * 0.5], inner, stroke=False
            )
        elif animal.ears == "pointed":
            pen.polygon(
                [
                    (ex - er * 0.85, ey + er * 0.75),
                    (ex + side * er * 0.25, ey - er * 1.5),
                    (ex + er * 0.85, ey + er * 0.75),
                ],
                animal.fur,
            )
        elif animal.ears == "tufted":
            pen.polygon(
                [
                    (ex - er * 0.7, ey + er * 0.5),
                    (ex + side * er * 0.5, ey - er * 1.25),
                    (ex + er * 0.7, ey + er * 0.4),
                ],
                animal.fur,
            )


def _draw_mask(pen: Pen, animal: Animal, cx: float, cy: float, r: float) -> None:
    if animal.extra != "mask":
        return
    # Antifaz del mapache: recortado contra la cabeza para que no se salga.
    band = [cx - r * 0.98, cy - r * 0.34, cx + r * 0.98, cy + r * 0.26]
    pen.draw.pieslice(band, 0, 360, fill=None if pen.outline_only else (78, 74, 78))
    pen.arc(band, 0, 360)


def _draw_eyes(pen: Pen, animal: Animal, cx: float, cy: float, r: float) -> None:
    ey = cy - r * 0.12
    dx = r * 0.38

    if animal.eyes == "disc":
        disc = r * 0.34
        for side in (-1, 1):
            pen.ellipse(
                [cx + side * dx - disc, ey - disc, cx + side * dx + disc, ey + disc],
                (252, 250, 246),
            )
            pupil = disc * 0.46
            pen.solid_ellipse(
                [cx + side * dx - pupil, ey - pupil, cx + side * dx + pupil, ey + pupil], INK
            )
    else:
        pupil = r * 0.13
        for side in (-1, 1):
            pen.solid_ellipse(
                [cx + side * dx - pupil, ey - pupil, cx + side * dx + pupil, ey + pupil], INK
            )
            shine = pupil * 0.36
            pen.solid_ellipse(
                [
                    cx + side * dx - shine + pupil * 0.34,
                    ey - shine - pupil * 0.3,
                    cx + side * dx + shine + pupil * 0.34,
                    ey + shine - pupil * 0.3,
                ],
                WHITE,
            )

    if animal.cheeks and not pen.outline_only:
        for side in (-1, 1):
            blush = r * 0.16
            pen.draw.ellipse(
                [
                    cx + side * r * 0.66 - blush,
                    cy + r * 0.22 - blush * 0.7,
                    cx + side * r * 0.66 + blush,
                    cy + r * 0.22 + blush * 0.7,
                ],
                fill=(244, 168, 158),
            )


def _draw_snout(pen: Pen, animal: Animal, cx: float, cy: float, r: float) -> None:
    if animal.nose == "beak":
        pen.polygon(
            [
                (cx - r * 0.2, cy + r * 0.18),
                (cx + r * 0.2, cy + r * 0.18),
                (cx, cy + r * 0.62),
            ],
            animal.muzzle,
        )
        return

    if animal.nose == "none":
        # La ballena no tiene hocico: una sonrisa ancha basta.
        pen.arc([cx - r * 0.62, cy + r * 0.02, cx + r * 0.62, cy + r * 0.78], 20, 160)
        return

    muzzle = [cx - r * 0.44, cy + r * 0.18, cx + r * 0.44, cy + r * 0.74]
    pen.ellipse(muzzle, animal.muzzle)

    if animal.nose == "triangle":
        pen.polygon(
            [
                (cx - r * 0.15, cy + r * 0.3),
                (cx + r * 0.15, cy + r * 0.3),
                (cx, cy + r * 0.48),
            ],
            INK,
        )
    else:
        pen.solid_ellipse(
            [cx - r * 0.11, cy + r * 0.29, cx + r * 0.11, cy + r * 0.45], INK
        )

    pen.arc([cx - r * 0.3, cy + r * 0.36, cx + r * 0.3, cy + r * 0.72], 30, 150)

    if animal.whiskers:
        for side in (-1, 1):
            for i, dy in enumerate((-0.04, 0.06, 0.16)):
                pen.line(
                    [
                        (cx + side * r * 0.4, cy + r * (0.4 + dy)),
                        (cx + side * r * 0.95, cy + r * (0.32 + dy * 1.6)),
                    ],
                    width=max(2, int(r * 0.02)),
                )


def _draw_front(pen: Pen, animal: Animal, cx: float, cy: float, r: float) -> None:
    if animal.extra == "crest":
        for i, (dx, height) in enumerate([(-0.3, 0.28), (0.0, 0.42), (0.3, 0.28)]):
            pen.polygon(
                [
                    (cx + r * (dx - 0.16), cy - r * 0.92),
                    (cx + r * dx, cy - r * (0.92 + height)),
                    (cx + r * (dx + 0.16), cy - r * 0.92),
                ],
                tint(animal.fur, 0.25),
            )
    elif animal.extra == "antennae":
        for side in (-1, 1):
            start = (cx + side * r * 0.3, cy - r * 0.86)
            end = (cx + side * r * 0.66, cy - r * 1.32)
            pen.line([start, end], width=max(3, int(r * 0.05)))
            bulb = r * 0.14
            pen.ellipse([end[0] - bulb, end[1] - bulb, end[0] + bulb, end[1] + bulb], animal.fur)


def draw_prop(
    draw: ImageDraw.ImageDraw, kind: str, cx: float, cy: float, r: float, color=None
) -> None:
    """Icono suelto.

    Sin `color` sale en contorno, que es lo que necesitan las láminas de
    colorear y recortar. Con `color`, sale relleno para decorar las páginas
    del cuento.
    """
    pen = Pen(draw, outline_only=color is None, width=max(3, int(r * 0.14)))
    WHITE_OR = color or WHITE
    if kind == "hoja":
        pen.polygon(
            [(cx, cy - r), (cx + r * 0.8, cy), (cx, cy + r), (cx - r * 0.8, cy)], WHITE_OR
        )
        pen.line([(cx, cy - r * 0.8), (cx, cy + r * 0.8)])
    elif kind == "estrella":
        points = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            radius = r if i % 2 == 0 else r * 0.45
            points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        pen.polygon(points, WHITE_OR)
    elif kind == "gota":
        pen.polygon(
            [(cx, cy - r), (cx + r * 0.62, cy + r * 0.32), (cx - r * 0.62, cy + r * 0.32)], WHITE_OR
        )
        pen.ellipse([cx - r * 0.62, cy - r * 0.3, cx + r * 0.62, cy + r * 0.92], WHITE_OR)
    elif kind == "circulo":
        pen.ellipse([cx - r, cy - r, cx + r, cy + r], WHITE_OR)
    elif kind == "cuadrado":
        pen.draw.rounded_rectangle(
            [cx - r * 0.85, cy - r * 0.85, cx + r * 0.85, cy + r * 0.85],
            radius=int(r * 0.2),
            fill=WHITE_OR,
            outline=LINE,
            width=pen.width,
        )
    elif kind == "triangulo":
        pen.polygon(
            [(cx, cy - r), (cx + r * 0.9, cy + r * 0.7), (cx - r * 0.9, cy + r * 0.7)], WHITE_OR
        )
    elif kind == "corazon":
        # Curva paramétrica en vez de dos círculos y un triángulo: montando
        # figuras, los contornos interiores se cruzaban y el corazón se leía
        # como una letra B.
        points = []
        for i in range(73):
            t = 2 * math.pi * i / 72
            hx = 16 * math.sin(t) ** 3
            hy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            points.append((cx + hx * r / 17, cy - hy * r / 17))
        pen.polygon(points, WHITE_OR)


PROP_KINDS = ["hoja", "estrella", "gota", "circulo", "cuadrado", "triangulo", "corazon"]
