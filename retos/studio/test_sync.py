"""El estudio y el backend tienen que seguir hablando el mismo idioma.

El contenido está partido en dos sitios a propósito: los títulos en el backend
(los sirve la API) y los guiones aquí (son material de imprenta). El precio de
esa separación es que se pueden desincronizar. Estas pruebas son el seguro:
al añadir una semana 13 en el backend, fallan antes de que el generador
reviente a mitad de una tirada.
"""

import pytest

from app.content import WEEKS, animal_for_week
from app.engine import MILESTONE_WEEKS
from app.models import RewardKind
from fauna import ANIMALS
from generate import build_brief
from pages import Brief
from scripts import SCRIPTS

WEEK_INDEXES = [week.week_index for week in WEEKS]
SHEET_KINDS = {"colorear", "buscar", "trazos", "recortar", "dibujar"}


@pytest.mark.parametrize("index", WEEK_INDEXES)
def test_cada_semana_tiene_guion(index):
    assert index in SCRIPTS, f"falta el guion de la semana {index} en scripts.py"


def test_no_sobran_guiones():
    assert set(SCRIPTS) == set(WEEK_INDEXES)


@pytest.mark.parametrize("index", WEEK_INDEXES)
def test_el_animal_de_la_semana_se_sabe_dibujar(index):
    animal = animal_for_week(index)
    assert animal in ANIMALS, f"la semana {index} pide '{animal}' y fauna.py no lo tiene"


@pytest.mark.parametrize("index", WEEK_INDEXES)
def test_el_cuento_tiene_tres_paginas(index):
    assert len(SCRIPTS[index].pages) == 3


@pytest.mark.parametrize("index", WEEK_INDEXES)
def test_la_lamina_pide_un_tipo_que_existe(index):
    assert SCRIPTS[index].sheet.kind in SHEET_KINDS


@pytest.mark.parametrize("index", WEEK_INDEXES)
def test_el_brief_se_arma_con_los_titulos_del_backend(index):
    week = WEEKS[index - 1]
    brief = build_brief(week)
    rewards = {option.kind: option.title for option in week.reward_options}

    assert isinstance(brief, Brief)
    assert brief.character == rewards[RewardKind.CHARACTER]
    assert brief.story_title == rewards[RewardKind.STORY]
    assert brief.sheet_title == rewards[RewardKind.PRINTABLE]


def test_las_rutas_generadas_coinciden_con_el_asset_key():
    """`assets/w03/personaje.png` tiene que casar con el asset_key `w03/personaje`."""
    for week in WEEKS:
        for option in week.reward_options:
            assert option.asset_key == f"w{week.week_index:02d}/{option.kind.value}"


def test_hay_diploma_para_cada_hito():
    for index in MILESTONE_WEEKS:
        assert index in SCRIPTS, f"la semana de hito {index} no tiene contenido"


@pytest.mark.parametrize("animal", sorted(ANIMALS))
def test_ningun_animal_queda_sin_usar(animal):
    usados = {animal_for_week(index) for index in WEEK_INDEXES}
    assert animal in usados, f"'{animal}' está definido pero no lo usa ninguna semana"
