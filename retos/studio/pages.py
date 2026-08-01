"""Las cuatro piezas que se generan: personaje, cuento, lámina y diploma."""

from __future__ import annotations

import random
from dataclasses import dataclass

from PIL import Image

import canvas
from fauna import PROP_KINDS, VERTICAL_EXTENT, draw_animal, draw_prop
from palette import (
    A4,
    A4_MARGIN,
    BORDER,
    CARD,
    CREAM,
    INK,
    INK_SOFT,
    LINE,
    STORY_PAGE,
    WHITE,
    accent,
    tint,
)
from scripts import Script


@dataclass(frozen=True)
class Brief:
    """Todo lo que hace falta para generar los premios de una semana."""

    index: int
    theme: str
    subtitle: str
    character: str
    story_title: str
    sheet_title: str
    animal: str
    script: Script


# ==================== Personaje ====================


def character_card(brief: Brief) -> Image.Image:
    color = accent(brief.index)
    image, draw = canvas.page(CARD, CREAM)
    w, h = CARD

    canvas.confetti(
        draw,
        (0, 0, w, h),
        [tint(color, 0.62), tint(color, 0.78), (255, 235, 220)],
        seed=brief.index,
        count=70,
        size=22,
    )

    # Disco de color detrás del personaje: lo separa del confeti sin
    # necesidad de sombras. El radio del animal sale del hueco disponible
    # entre la cabecera y el nombre, contando lo que sobresale.
    center_y = 470
    radius = min(w * 0.24, (830 - 150) / 2 / VERTICAL_EXTENT)
    disc = int(radius * 1.42)
    draw.ellipse(
        [w // 2 - disc, center_y - disc, w // 2 + disc, center_y + disc], fill=tint(color, 0.55)
    )
    draw_animal(draw, w / 2, center_y, radius, brief.animal)

    small = canvas.font(34, bold=True)
    draw.text(
        (w / 2 - draw.textlength(f"SEMANA {brief.index}", font=small) / 2, 72),
        f"SEMANA {brief.index}",
        font=small,
        fill=color,
    )

    canvas.text_block(
        draw, (110, 830), brief.character, canvas.font(82, bold=True), INK, w - 220, align="center"
    )
    canvas.text_block(
        draw, (170, 970), brief.theme, canvas.font(40), INK_SOFT, w - 340, align="center"
    )
    return image


# ==================== Cuento ====================


def story_pages(brief: Brief) -> list[Image.Image]:
    return [_story_cover(brief)] + [
        _story_page(brief, number, text) for number, text in enumerate(brief.script.pages, start=1)
    ]


def _story_cover(brief: Brief) -> Image.Image:
    color = accent(brief.index)
    image, draw = canvas.page(STORY_PAGE, tint(color, 0.72))
    w, h = STORY_PAGE

    draw.rectangle([0, 0, w, 190], fill=color)
    label = canvas.font(36, bold=True)
    draw.text((90, 74), f"CUENTO · SEMANA {brief.index}", font=label, fill=WHITE)

    canvas.text_block(
        draw, (110, 300), brief.story_title, canvas.font(92, bold=True), INK, w - 220, leading=1.2
    )

    center_y = 1090
    radius = min(w * 0.22, (h - center_y - 120) / VERTICAL_EXTENT)
    disc = int(radius * 1.42)
    draw.ellipse(
        [w // 2 - disc, center_y - disc, w // 2 + disc, center_y + disc], fill=tint(color, 0.4)
    )
    draw_animal(draw, w / 2, center_y, radius, brief.animal)
    return image


# Cada página coloca al personaje en un sitio y a un tamaño distintos, y le
# pone compañía diferente. Tres páginas con la misma ilustración se leen como
# un producto descuidado, por muy bueno que sea el texto.
_STORY_STAGING = {
    1: {"x": 0.50, "r": 215, "props": [(0.16, 0.62, 60), (0.86, 0.34, 48)]},
    2: {"x": 0.36, "r": 178, "props": [(0.72, 0.42, 82), (0.86, 0.68, 54), (0.62, 0.74, 44)]},
    3: {"x": 0.62, "r": 222, "props": [(0.17, 0.38, 70), (0.24, 0.70, 46)]},
}


def _story_page(brief: Brief, number: int, text: str) -> Image.Image:
    color = accent(brief.index)
    image, draw = canvas.page(STORY_PAGE, WHITE)
    w, h = STORY_PAGE
    band = 760

    # Banda ilustrada arriba, texto abajo: el niño mira, el adulto lee.
    draw.rectangle([0, 0, w, band], fill=tint(color, 0.78))
    canvas.confetti(
        draw, (0, 0, w, band), [tint(color, 0.5), tint(color, 0.62)], seed=brief.index * 10 + number,
        count=34, size=20,
    )

    staging = _STORY_STAGING[number]
    for i, (px, py, pr) in enumerate(staging["props"]):
        draw_prop(
            draw,
            PROP_KINDS[(brief.index + number + i) % len(PROP_KINDS)],
            w * px,
            band * py,
            pr,
            color=tint(color, 0.35),
        )
    draw_animal(draw, w * staging["x"], band * 0.52, staging["r"], brief.animal)

    canvas.text_block(draw, (110, 880), text, canvas.font(60), INK, w - 220, leading=1.45)

    page_label = canvas.font(32, bold=True)
    draw.text((w - 110 - draw.textlength(str(number), font=page_label), h - 110), str(number),
              font=page_label, fill=INK_SOFT)
    return image


# ==================== Lámina imprimible ====================


def printable_sheet(brief: Brief) -> Image.Image:
    color = accent(brief.index)
    image, draw = canvas.page(A4, WHITE)
    w, h = A4
    left, right = A4_MARGIN, w - A4_MARGIN

    draw.rectangle([0, 0, w, 26], fill=color)

    label = canvas.font(44, bold=True)
    draw.text((left, 190), f"SEMANA {brief.index} · {brief.theme.upper()}", font=label, fill=color)
    canvas.text_block(
        draw, (left, 270), brief.sheet_title, canvas.font(104, bold=True), INK, right - left
    )

    canvas.rounded(draw, [left, 430, right, 560], radius=26, fill=tint(color, 0.85))
    canvas.text_block(
        draw, (left + 40, 468), brief.script.sheet.instruction, canvas.font(42), INK, right - left - 80
    )

    body = (left, 640, right, h - 340)
    renderer = {
        "colorear": _body_colorear,
        "buscar": _body_buscar,
        "trazos": _body_trazos,
        "recortar": _body_recortar,
        "dibujar": _body_dibujar,
    }[brief.script.sheet.kind]
    renderer(draw, brief, body)

    _sheet_footer(draw, brief, left, right, h)
    return image


def _sheet_footer(draw, brief: Brief, left: int, right: int, h: int) -> None:
    y = h - 250
    draw.line([(left, y), (right, y)], fill=BORDER, width=4)
    small = canvas.font(38)
    draw.text((left, y + 50), "Nombre:", font=small, fill=INK_SOFT)
    draw.line([(left + 200, y + 100), (left + 950, y + 100)], fill=BORDER, width=4)
    tag = f"Retos · semana {brief.index}"
    draw.text((right - draw.textlength(tag, font=small), y + 50), tag, font=small, fill=INK_SOFT)


def _body_colorear(draw, brief: Brief, box) -> None:
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2

    # Reparto fijo, no aleatorio: al azar los iconos se solapaban y quedaban
    # figuras imposibles de colorear.
    top_y, bottom_y = y0 + 150, y1 - 150
    for i, px in enumerate((0.18, 0.5, 0.82)):
        draw_prop(draw, PROP_KINDS[(brief.index + i) % len(PROP_KINDS)], x0 + (x1 - x0) * px, top_y, 95)
    for i, px in enumerate((0.3, 0.7)):
        draw_prop(
            draw, PROP_KINDS[(brief.index + i + 3) % len(PROP_KINDS)], x0 + (x1 - x0) * px, bottom_y, 95
        )

    # El personaje ocupa el hueco central entero: es lo que se colorea.
    inner_top, inner_bottom = top_y + 170, bottom_y - 170
    radius = min((x1 - x0) * 0.38, (inner_bottom - inner_top) / 2 / VERTICAL_EXTENT)
    draw_animal(draw, cx, (inner_top + inner_bottom) / 2, radius, brief.animal, outline_only=True)


def _body_buscar(draw, brief: Brief, box) -> None:
    x0, y0, x1, y1 = box
    cols, rows = 4, 5
    cell_w, cell_h = (x1 - x0) / cols, (y1 - y0) / rows
    rnd = random.Random(brief.index * 7)
    for row in range(rows):
        for col in range(cols):
            kind = rnd.choice(PROP_KINDS)
            draw_prop(
                draw,
                kind,
                x0 + cell_w * (col + 0.5),
                y0 + cell_h * (row + 0.5),
                min(cell_w, cell_h) * 0.32,
            )


def _body_trazos(draw, brief: Brief, box) -> None:
    x0, y0, x1, y1 = box
    rows = 4
    gap = (y1 - y0) / rows
    # Cuatro trazos distintos, de menos a más difícil: onda, zigzag, bucles y
    # montañas. Repetir el mismo cuatro veces no enseña nada nuevo.
    builders = [
        lambda y: canvas.wave_points(x0 + 160, x1 - 120, y, 70, 2.5),
        lambda y: canvas.zigzag_points(x0 + 160, x1 - 120, y, 70, 8),
        lambda y: canvas.loop_points(x0 + 160, x1 - 120, y, 85, 5),
        lambda y: canvas.hill_points(x0 + 160, x1 - 120, y + 40, 95, 5),
    ]
    for i, build in enumerate(builders):
        y = y0 + gap * (i + 0.5)
        points = build(y)
        # Punto de salida lleno y meta hueca: se ve de dónde a dónde sin leer.
        draw.ellipse([x0 + 70, y - 40, x0 + 150, y + 40], fill=accent(brief.index))
        canvas.dotted_path(draw, points, LINE, radius=7, step=34)
        draw.ellipse([x1 - 110, y - 40, x1 - 30, y + 40], outline=LINE, width=6)


def _body_recortar(draw, brief: Brief, box) -> None:
    x0, y0, x1, y1 = box
    cols, rows = 2, 2
    pad = 40
    cell_w, cell_h = (x1 - x0) / cols, (y1 - y0) / rows
    for row in range(rows):
        for col in range(cols):
            cell = (
                x0 + cell_w * col + pad,
                y0 + cell_h * row + pad,
                x0 + cell_w * (col + 1) - pad,
                y0 + cell_h * (row + 1) - pad,
            )
            canvas.dashed_rect(draw, cell, dash=26, gap=20, fill=LINE, width=5)
            cx, cy = (cell[0] + cell[2]) / 2, (cell[1] + cell[3]) / 2
            index = row * cols + col
            if index == 0:
                draw_animal(
                    draw, cx, cy, min(cell_w, cell_h) * 0.26 / VERTICAL_EXTENT * 1.2,
                    brief.animal, outline_only=True,
                )
            else:
                draw_prop(
                    draw,
                    PROP_KINDS[(brief.index + index) % len(PROP_KINDS)],
                    cx,
                    cy,
                    min(cell_w, cell_h) * 0.26,
                )


def _body_dibujar(draw, brief: Brief, box) -> None:
    x0, y0, x1, y1 = box
    frame_bottom = y1 - 320
    canvas.rounded(draw, [x0, y0, x1, frame_bottom], radius=40, outline=LINE, width=6)
    if brief.script.sheet.prompt:
        canvas.text_block(
            draw, (x0 + 60, y0 + 50), brief.script.sheet.prompt, canvas.font(56, bold=True),
            INK_SOFT, x1 - x0 - 120,
        )
    for i in range(3):
        y = frame_bottom + 110 + i * 100
        draw.line([(x0, y), (x1, y)], fill=BORDER, width=5)


# ==================== Diploma de hito ====================


def diploma(brief: Brief) -> Image.Image:
    color = accent(brief.index)
    image, draw = canvas.page(A4, CREAM)
    w, h = A4
    margin = A4_MARGIN

    canvas.rounded(draw, [margin, margin, w - margin, h - margin], radius=60, outline=color, width=18)
    canvas.rounded(
        draw,
        [margin + 40, margin + 40, w - margin - 40, h - margin - 40],
        radius=44,
        outline=tint(color, 0.5),
        width=6,
    )

    canvas.text_block(
        draw, (margin, 520), "DIPLOMA", canvas.font(150, bold=True), color, w - margin * 2,
        align="center",
    )
    canvas.text_block(
        draw,
        (margin + 120, 760),
        f"por completar la semana {brief.index}",
        canvas.font(58),
        INK_SOFT,
        w - (margin + 120) * 2,
        align="center",
    )

    draw.line([(margin + 300, 1180), (w - margin - 300, 1180)], fill=INK_SOFT, width=5)
    canvas.text_block(
        draw, (margin, 1210), "escribe aquí tu nombre", canvas.font(38), INK_SOFT,
        w - margin * 2, align="center",
    )

    center_y = 1880
    radius = min(360, (2480 - center_y) / VERTICAL_EXTENT)
    disc = int(radius * 1.42)
    draw.ellipse(
        [w // 2 - disc, center_y - disc, w // 2 + disc, center_y + disc], fill=tint(color, 0.62)
    )
    draw_animal(draw, w / 2, center_y, radius, brief.animal)

    canvas.text_block(
        draw,
        (margin + 200, 2560),
        "Tu premio de verdad viaja aparte. Pídelo con el código que\n"
        "aparece en la zona de adultos de la app.",
        canvas.font(44),
        INK,
        w - (margin + 200) * 2,
        align="center",
        leading=1.5,
    )

    draw.line([(margin + 500, 2860), (w - margin - 500, 2860)], fill=INK_SOFT, width=5)
    canvas.text_block(
        draw, (margin, 2890), "código", canvas.font(38), INK_SOFT, w - margin * 2, align="center"
    )
    return image


# ==================== Hoja de control ====================


def contact_sheet(sheets: list[tuple[int, str, Image.Image]]) -> Image.Image:
    """Las doce láminas en una sola imagen, para revisarlas de un vistazo."""
    cols, rows = 4, 3
    thumb_w = 460
    thumb_h = int(thumb_w * A4[1] / A4[0])
    pad, header, caption = 40, 150, 70

    width = cols * thumb_w + pad * (cols + 1)
    height = header + rows * (thumb_h + caption) + pad * (rows + 1)
    image, draw = canvas.page((width, height), CREAM)

    canvas.text_block(draw, (pad, 48), "Retos · las 12 láminas", canvas.font(56, bold=True), INK, width)

    for i, (index, title, sheet) in enumerate(sheets):
        col, row = i % cols, i // cols
        x = pad + col * (thumb_w + pad)
        y = header + pad + row * (thumb_h + caption + pad)
        thumb = sheet.resize((thumb_w, thumb_h), Image.LANCZOS)
        image.paste(thumb, (x, y))
        draw.rectangle([x, y, x + thumb_w, y + thumb_h], outline=BORDER, width=3)
        canvas.text_block(
            draw, (x, y + thumb_h + 14), f"{index}. {title}", canvas.font(26, bold=True), INK_SOFT,
            thumb_w,
        )
    return image
