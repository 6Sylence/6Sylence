"""Primitivas de dibujo compartidas."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from palette import DPI, FONT_BOLD, FONT_REGULAR

_font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = str(FONT_BOLD if bold else FONT_REGULAR)
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def page(size: tuple[int, int], color) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", size, color)
    return image, ImageDraw.Draw(image)


# ==================== Texto ====================


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words, current = paragraph.split(), ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if draw.textlength(candidate, font=fnt) <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def text_block(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt,
    fill,
    max_width: int,
    leading: float = 1.35,
    align: str = "left",
) -> int:
    """Escribe texto ajustado al ancho. Devuelve la altura ocupada."""
    x, y = xy
    line_height = int(fnt.size * leading)
    for line in wrap(draw, text, fnt, max_width):
        offset = 0
        if align == "center":
            offset = int((max_width - draw.textlength(line, font=fnt)) / 2)
        elif align == "right":
            offset = int(max_width - draw.textlength(line, font=fnt))
        draw.text((x + offset, y), line, font=fnt, fill=fill)
        y += line_height
    return y - xy[1]


# ==================== Formas ====================


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill=None, outline=None, width: int = 1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def dashed_rect(draw: ImageDraw.ImageDraw, box, dash: int, gap: int, fill, width: int = 4):
    """Borde discontinuo. Es la señal universal de 'corta por aquí'."""
    x0, y0, x1, y1 = box
    for x in range(int(x0), int(x1), dash + gap):
        draw.line([(x, y0), (min(x + dash, x1), y0)], fill=fill, width=width)
        draw.line([(x, y1), (min(x + dash, x1), y1)], fill=fill, width=width)
    for y in range(int(y0), int(y1), dash + gap):
        draw.line([(x0, y), (x0, min(y + dash, y1))], fill=fill, width=width)
        draw.line([(x1, y), (x1, min(y + dash, y1))], fill=fill, width=width)


def dotted_path(draw: ImageDraw.ImageDraw, points, fill, radius: int = 5, step: int = 26):
    """Camino de puntos para repasar con lápiz.

    Puntos separados, no línea discontinua: a los 3 años se persigue un punto,
    no se sigue una raya.
    """
    accumulated = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        segment = math.hypot(x1 - x0, y1 - y0)
        distance = accumulated
        while distance < segment:
            t = distance / segment
            cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=fill)
            distance += step
        accumulated = distance - segment


def wave_points(x0: int, x1: int, y: int, amplitude: int, periods: float, samples: int = 160):
    return [
        (x0 + (x1 - x0) * i / samples, y + amplitude * math.sin(2 * math.pi * periods * i / samples))
        for i in range(samples + 1)
    ]


def zigzag_points(x0: int, x1: int, y: int, amplitude: int, steps: int = 8):
    points = []
    for i in range(steps + 1):
        points.append((x0 + (x1 - x0) * i / steps, y + (amplitude if i % 2 else -amplitude)))
    return points


def loop_points(x0: int, x1: int, y: int, amplitude: int, loops: int = 5, samples: int = 260):
    """Bucles encadenados: el trazo previo a aprender a escribir.

    Es una cicloide alargada. La clave es que el radio del círculo que rueda
    sea mayor que su avance por vuelta; si no, sale una onda y no un bucle,
    que es un ejercicio distinto y mucho más fácil.
    """
    advance = (x1 - x0) / loops
    radius = advance * 0.62
    raw = []
    for i in range(samples + 1):
        angle = 2 * math.pi * loops * i / samples
        raw.append(
            (advance * angle / (2 * math.pi) - radius * math.sin(angle), y - amplitude * math.cos(angle))
        )

    # Los bucles se salen por los lados: la cicloide retrocede en cada vuelta.
    # Se reescala en horizontal para que el trazo empiece y acabe justo donde
    # están la salida y la meta.
    xs = [p[0] for p in raw]
    lo, hi = min(xs), max(xs)
    scale = (x1 - x0) / (hi - lo)
    return [(x0 + (px - lo) * scale, py) for px, py in raw]


def hill_points(x0: int, x1: int, y: int, amplitude: int, hills: int = 5, samples: int = 200):
    """Montañas: medias circunferencias seguidas, todas hacia arriba.

    Distinto ejercicio que la onda: aquí el lápiz sube, baja y **se levanta**
    del recorrido en cada valle.
    """
    points = []
    for i in range(samples + 1):
        t = i / samples
        phase = (t * hills) % 1.0
        points.append((x0 + (x1 - x0) * t, y - amplitude * math.sin(math.pi * phase)))
    return points


def confetti(draw: ImageDraw.ImageDraw, box, colors, seed: int, count: int = 60, size: int = 14):
    """Motas de color de fondo. Alegran sin competir con el dibujo principal."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(count):
        cx, cy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(size * 0.4, size)
        color = rnd.choice(colors)
        if rnd.random() < 0.5:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
        else:
            draw.rounded_rectangle([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], radius=int(r / 2), fill=color)


# ==================== Salida ====================


def save_png(image: Image.Image, path: Path, palette: int | None = None) -> Path:
    """Guarda un PNG. Con `palette` reduce a N colores.

    Estos dibujos son planos: 128 colores no cambian nada a la vista y
    recortan el archivo a una fracción. Solo se usa donde el peso importa
    (la hoja de control va al repositorio); los premios se guardan a color
    completo.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if palette:
        image = image.quantize(colors=palette, method=Image.MEDIANCUT)
    image.save(path, "PNG", optimize=True)
    return path


def save_pdf(images: list[Image.Image], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    first, rest = images[0].convert("RGB"), [i.convert("RGB") for i in images[1:]]
    first.save(path, "PDF", resolution=DPI, save_all=True, append_images=rest)
    return path
