"""Paleta, tipografía y medidas del estudio de contenido.

Los colores base son los mismos que los de la app (`retos/app/src/theme.ts`):
si el premio que el niño ve en pantalla y la lámina que imprime no se parecen,
no parece el mismo producto.

Sobre la tipografía: DejaVu está en cualquier máquina Linux y sirve para
generar y revisar, pero **no es la fuente definitiva**. Para publicar hay que
sustituirla por una redondeada con licencia comercial (Nunito, Quicksand o
similar) y dejar el archivo en `studio/fonts/`. Es cambiar estas cuatro rutas.
"""

from pathlib import Path

# ==================== Colores ====================

CREAM = (255, 248, 240)
WHITE = (255, 255, 255)
INK = (42, 33, 24)
INK_SOFT = (122, 106, 88)
ORANGE = (242, 107, 58)
TEAL = (58, 166, 160)
GREEN = (63, 157, 87)
BORDER = (234, 223, 209)

# Línea de las láminas imprimibles. Ni negro puro (agresivo al imprimir) ni
# gris claro (se pierde en impresoras domésticas).
LINE = (60, 48, 38)

# Un acento por semana, para que doce láminas seguidas no parezcan la misma.
WEEK_ACCENT = [
    (242, 107, 58),   # 1  manos
    (126, 168, 74),   # 2  colores
    (232, 168, 56),   # 3  palabras
    (140, 108, 190),  # 4  tesoros
    (226, 122, 150),  # 5  emociones
    (58, 166, 160),   # 6  números
    (94, 176, 118),   # 7  cuerpo
    (86, 124, 196),   # 8  sonidos
    (214, 134, 72),   # 9  cocina
    (108, 158, 92),   # 10 naturaleza
    (198, 96, 116),   # 11 historias
    (72, 148, 184),   # 12 equipo
]


def accent(week_index: int) -> tuple[int, int, int]:
    return WEEK_ACCENT[(week_index - 1) % len(WEEK_ACCENT)]


def tint(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    """Mezcla un color con blanco. `amount` 0 = igual, 1 = blanco."""
    return tuple(int(c + (255 - c) * amount) for c in color)  # type: ignore[return-value]


# ==================== Tipografía ====================

FONT_DIR = Path(__file__).resolve().parent / "fonts"

_SYSTEM = Path("/usr/share/fonts/truetype/dejavu")
FONT_BOLD = FONT_DIR / "bold.ttf" if (FONT_DIR / "bold.ttf").exists() else _SYSTEM / "DejaVuSans-Bold.ttf"
FONT_REGULAR = FONT_DIR / "regular.ttf" if (FONT_DIR / "regular.ttf").exists() else _SYSTEM / "DejaVuSans.ttf"


# ==================== Medidas ====================

# A4 a 300 ppp. Es la resolución mínima para que una línea impresa no se vea
# escalonada en una impresora doméstica.
DPI = 300
A4 = (2480, 3508)

# Tarjeta de personaje: cuadrada, para que quepa igual en la app y en una
# ficha impresa.
CARD = (1200, 1200)

# Página de cuento: proporción 3:4, se lee en móvil en vertical.
STORY_PAGE = (1200, 1600)

# Margen de seguridad de la lámina. Muchas impresoras domésticas no imprimen
# el borde: nada importante debe caer aquí dentro.
A4_MARGIN = 190
