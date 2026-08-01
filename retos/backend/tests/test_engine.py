"""Tests del motor de retos.

Prueban reglas de producto, no implementación. Si alguno de estos falla, lo que
se ha roto es una promesa hecha a las familias, no un detalle técnico.

No necesitan Mongo: el motor es puro.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app import engine
from app.models import Entitlement, EntitlementStatus

ENROLLED = datetime(2026, 1, 5, 10, 0, tzinfo=timezone.utc)
TOTAL = 12


def at(days: int) -> datetime:
    return ENROLLED + timedelta(days=days)


# ==================== Cadencia semanal ====================


def test_el_primer_dia_solo_hay_una_semana_desbloqueada():
    assert engine.unlocked_week(ENROLLED, at(0), TOTAL) == 1


def test_la_semana_no_se_desbloquea_hasta_cumplir_siete_dias():
    assert engine.unlocked_week(ENROLLED, at(6), TOTAL) == 1
    assert engine.unlocked_week(ENROLLED, at(7), TOTAL) == 2


def test_el_desbloqueo_se_detiene_al_final_del_plan():
    assert engine.unlocked_week(ENROLLED, at(7 * 50), TOTAL) == TOTAL


def test_no_se_puede_ir_hacia_atras_en_el_tiempo():
    assert engine.unlocked_week(ENROLLED, at(-30), TOTAL) == 1


def test_el_siguiente_desbloqueo_es_exactamente_una_semana_despues():
    assert engine.next_unlock_at(ENROLLED, at(0), TOTAL) == at(7)
    assert engine.next_unlock_at(ENROLLED, at(10), TOTAL) == at(14)


def test_al_terminar_el_plan_ya_no_hay_siguiente_desbloqueo():
    assert engine.next_unlock_at(ENROLLED, at(7 * 20), TOTAL) is None


# ==================== Completar una semana ====================


def test_la_semana_se_completa_con_dos_de_tres():
    ids = ["w01-a1", "w01-a2", "w01-a3"]
    assert not engine.is_week_complete(["w01-a1"], ids)
    assert engine.is_week_complete(["w01-a1", "w01-a3"], ids)


def test_las_actividades_de_otra_semana_no_cuentan():
    ids = ["w02-a1", "w02-a2", "w02-a3"]
    assert not engine.is_week_complete(["w01-a1", "w01-a2"], ids)


def test_una_semana_corta_no_exige_mas_actividades_de_las_que_tiene():
    assert engine.is_week_complete(["w01-a1"], ["w01-a1"])


# ==================== Sin castigo por semana perdida ====================


def test_la_semana_saltada_sigue_siendo_la_actual():
    # Cuatro semanas desbloqueadas, la 2 sin hacer: es a la que se vuelve.
    state = engine.compute_plan_state(ENROLLED, at(21), TOTAL, completed_weeks=[1, 3])
    assert state.unlocked == 4
    assert state.current_week == 2
    assert state.catchup_weeks == [4]


def test_las_semanas_atrasadas_no_caducan_nunca():
    state = engine.compute_plan_state(ENROLLED, at(7 * 11), TOTAL, completed_weeks=[1])
    assert state.current_week == 2
    assert state.catchup_weeks == list(range(3, 13))


def test_con_todo_hecho_se_espera_al_siguiente_desbloqueo():
    state = engine.compute_plan_state(ENROLLED, at(7), TOTAL, completed_weeks=[1, 2])
    assert state.current_week == 2
    assert state.catchup_weeks == []
    assert state.awaiting_next_week is True
    assert state.plan_finished is False


def test_el_plan_termina_al_completar_la_ultima_semana():
    state = engine.compute_plan_state(
        ENROLLED, at(7 * 11), TOTAL, completed_weeks=list(range(1, 13))
    )
    assert state.plan_finished is True
    assert state.awaiting_next_week is False


def test_no_se_puede_correr_por_delante_del_calendario():
    # Aunque haya progreso guardado en semanas futuras, no se muestran.
    state = engine.compute_plan_state(ENROLLED, at(0), TOTAL, completed_weeks=[1, 5, 6])
    assert state.unlocked == 1
    assert state.completed_weeks == [1]
    assert state.catchup_weeks == []


# ==================== Suscripción ====================


def test_la_prueba_gratuita_cuenta_como_titularidad():
    entitlement = Entitlement(status=EntitlementStatus.TRIALING, expires_at=at(7))
    assert engine.has_entitlement(entitlement, at(3)) is True
    assert engine.has_entitlement(entitlement, at(8)) is False


def test_la_suscripcion_caducada_no_da_acceso():
    entitlement = Entitlement(status=EntitlementStatus.EXPIRED, expires_at=at(60))
    assert engine.has_entitlement(entitlement, at(1)) is False


def test_la_suscripcion_activa_sin_caducidad_es_valida():
    entitlement = Entitlement(status=EntitlementStatus.ACTIVE, expires_at=None)
    assert engine.has_entitlement(entitlement, at(999)) is True


def test_la_primera_semana_es_gratis_y_la_segunda_no():
    assert engine.is_week_accessible(1, entitled=False) is True
    assert engine.is_week_accessible(2, entitled=False) is False
    assert engine.is_week_accessible(2, entitled=True) is True


def test_el_motivo_de_bloqueo_distingue_calendario_de_suscripcion():
    assert engine.locked_reason(1, entitled=False, unlocked=1) is None
    assert "todavía no está disponible" in engine.locked_reason(3, entitled=True, unlocked=2)
    assert "suscripción" in engine.locked_reason(2, entitled=False, unlocked=4)


# ==================== Hitos físicos ====================


@pytest.mark.parametrize("week", [4, 8, 12])
def test_las_semanas_de_hito_dan_recompensa_fisica(week):
    assert engine.milestone_for_week(week) is True


@pytest.mark.parametrize("week", [1, 2, 3, 5, 7, 11])
def test_el_resto_de_semanas_no_generan_envio(week):
    assert engine.milestone_for_week(week) is False
