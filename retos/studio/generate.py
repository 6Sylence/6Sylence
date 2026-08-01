#!/usr/bin/env python3
"""Genera los premios de las 12 semanas.

    python generate.py                 # todo
    python generate.py --week 3        # solo la semana 3
    python generate.py --only sheets   # solo las láminas
    python generate.py --contact       # además, la hoja de control

Los títulos no se escriben aquí: se leen del contenido del backend
(`retos/backend/app/content/weeks.py`), que es la única fuente de verdad. Así
el nombre que la app muestra como premio y el que sale impreso en la lámina no
pueden separarse.

La salida va a `retos/assets/`, que está fuera del control de versiones: son
archivos derivados y se regeneran en un segundo. Lo que se versiona es el
generador.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

STUDIO_DIR = Path(__file__).resolve().parent
BACKEND_DIR = STUDIO_DIR.parent / "backend"
ASSETS_DIR = STUDIO_DIR.parent / "assets"

sys.path.insert(0, str(STUDIO_DIR))
sys.path.insert(0, str(BACKEND_DIR))

import canvas  # noqa: E402
from app.content import WEEKS, animal_for_week  # noqa: E402
from app.engine import MILESTONE_WEEKS  # noqa: E402
from app.models import RewardKind  # noqa: E402
from pages import Brief, character_card, contact_sheet, diploma, printable_sheet, story_pages  # noqa: E402
from scripts import get_script  # noqa: E402


def build_brief(week) -> Brief:
    rewards = {option.kind: option for option in week.reward_options}
    return Brief(
        index=week.week_index,
        theme=week.title,
        subtitle=week.subtitle,
        character=rewards[RewardKind.CHARACTER].title,
        story_title=rewards[RewardKind.STORY].title,
        sheet_title=rewards[RewardKind.PRINTABLE].title,
        animal=animal_for_week(week.week_index),
        script=get_script(week.week_index),
    )


def generate_week(brief: Brief, only: str) -> list[Path]:
    """Genera los archivos de una semana. Las rutas replican `asset_key`."""
    out = ASSETS_DIR / f"w{brief.index:02d}"
    written: list[Path] = []

    if only in ("all", "characters"):
        written.append(canvas.save_png(character_card(brief), out / "personaje.png"))
    if only in ("all", "stories"):
        written.append(canvas.save_pdf(story_pages(brief), out / "historia.pdf"))
    if only in ("all", "sheets"):
        written.append(canvas.save_pdf([printable_sheet(brief)], out / "imprimible.pdf"))
    if only in ("all", "diplomas") and brief.index in MILESTONE_WEEKS:
        written.append(
            canvas.save_pdf([diploma(brief)], ASSETS_DIR / "hitos" / f"diploma-s{brief.index:02d}.pdf")
        )
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera los premios de Retos.")
    parser.add_argument("--week", type=int, help="Solo esta semana (1-12).")
    parser.add_argument(
        "--only",
        default="all",
        choices=["all", "characters", "stories", "sheets", "diplomas"],
        help="Genera solo un tipo de premio.",
    )
    parser.add_argument("--contact", action="store_true", help="Añade la hoja de control.")
    args = parser.parse_args()

    weeks = [w for w in WEEKS if args.week is None or w.week_index == args.week]
    if not weeks:
        print(f"No existe la semana {args.week}. Hay {len(WEEKS)}.", file=sys.stderr)
        return 1

    total = 0
    for week in weeks:
        brief = build_brief(week)
        written = generate_week(brief, args.only)
        total += len(written)
        for path in written:
            print(f"  {path.relative_to(ASSETS_DIR.parent)}")

    if args.contact:
        sheets = [
            (w.week_index, build_brief(w).sheet_title, printable_sheet(build_brief(w))) for w in WEEKS
        ]
        path = canvas.save_png(contact_sheet(sheets), STUDIO_DIR / "muestra.png", palette=128)
        print(f"  {path.relative_to(STUDIO_DIR.parent)}")
        total += 1

    print(f"\n{total} archivos generados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
