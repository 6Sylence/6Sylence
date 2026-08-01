"""Motor de retos.

Funciones puras: sin base de datos, sin red, sin reloj implícito. `now` siempre
se pasa como argumento. Esto es lo que permite probar todas las reglas de
producto sin levantar Mongo, y lo que evita que la lógica se disperse por los
endpoints.

Las tres reglas que definen el producto viven aquí:

1. **Cadencia semanal.** La semana N se desbloquea N-1 semanas después de la
   inscripción. No se puede correr hacia adelante: el ritmo es parte de la
   propuesta.
2. **Sin castigo por semana perdida.** Una semana no completada no caduca ni
   rompe nada. Sigue disponible y es la que se muestra al volver. No hay
   rachas, ni contadores de días fallados, ni penalizaciones.
3. **La semana 1 es gratis.** A partir de la 2 hace falta suscripción activa.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Optional

from .models import Entitlement, EntitlementStatus

# Una semana se da por completada con 2 de 3 actividades. Exigir las 3 castiga
# a la familia que tuvo una semana mala y es la principal causa de abandono en
# este tipo de producto.
ACTIVITIES_REQUIRED = 2

# Semanas accesibles sin suscripción.
FREE_WEEKS = 1

# Semanas que además desbloquean recompensa física, canjeable fuera de la app.
MILESTONE_WEEKS = (4, 8, 12)


def weeks_elapsed(enrolled_at: datetime, now: datetime) -> int:
    """Semanas completas transcurridas desde la inscripción."""
    delta = now - enrolled_at
    if delta.days < 0:
        return 0
    return delta.days // 7


def unlocked_week(enrolled_at: datetime, now: datetime, total_weeks: int) -> int:
    """Índice de la semana más alta desbloqueada por calendario."""
    if total_weeks <= 0:
        return 0
    return min(total_weeks, weeks_elapsed(enrolled_at, now) + 1)


def next_unlock_at(
    enrolled_at: datetime, now: datetime, total_weeks: int
) -> Optional[datetime]:
    """Cuándo se desbloquea la siguiente semana, o None si el plan ha terminado."""
    unlocked = unlocked_week(enrolled_at, now, total_weeks)
    if unlocked >= total_weeks:
        return None
    return enrolled_at + timedelta(days=7 * unlocked)


def is_week_complete(completed_activity_ids: Iterable[str], week_activity_ids: Iterable[str]) -> bool:
    """Una semana está completa al validar `ACTIVITIES_REQUIRED` actividades suyas."""
    week_ids = set(week_activity_ids)
    hits = len(week_ids & set(completed_activity_ids))
    return hits >= min(ACTIVITIES_REQUIRED, len(week_ids))


def has_entitlement(entitlement: Entitlement, now: datetime) -> bool:
    """Si la suscripción (o la prueba gratuita) sigue vigente."""
    if entitlement.status not in (EntitlementStatus.ACTIVE, EntitlementStatus.TRIALING):
        return False
    if entitlement.expires_at is None:
        return entitlement.status == EntitlementStatus.ACTIVE
    return entitlement.expires_at > now


def is_week_accessible(week_index: int, entitled: bool) -> bool:
    """La semana 1 es abierta; el resto exige titularidad vigente."""
    if week_index <= FREE_WEEKS:
        return True
    return entitled


def locked_reason(week_index: int, entitled: bool, unlocked: int) -> Optional[str]:
    """Motivo por el que una semana no es jugable, en texto para la app."""
    if week_index > unlocked:
        return "Esta semana todavía no está disponible."
    if not is_week_accessible(week_index, entitled):
        return "Necesitas una suscripción activa para continuar a partir de la semana 2."
    return None


def milestone_for_week(week_index: int) -> bool:
    """Si completar esta semana desbloquea recompensa física de hito."""
    return week_index in MILESTONE_WEEKS


class PlanState:
    """Estado del plan de un niño en un instante dado.

    - `current_week`: la semana que la app debe mostrar al abrirse. Es la más
      antigua sin completar entre las desbloqueadas; si están todas completas,
      la última desbloqueada.
    - `catchup_weeks`: semanas atrasadas que siguen disponibles. Se ofrecen,
      no se reclaman.
    """

    def __init__(
        self,
        unlocked: int,
        current_week: int,
        catchup_weeks: list[int],
        completed_weeks: list[int],
        total_weeks: int,
        next_unlock_at: Optional[datetime],
    ) -> None:
        self.unlocked = unlocked
        self.current_week = current_week
        self.catchup_weeks = catchup_weeks
        self.completed_weeks = completed_weeks
        self.total_weeks = total_weeks
        self.next_unlock_at = next_unlock_at

    @property
    def plan_finished(self) -> bool:
        return self.unlocked >= self.total_weeks and not self.catchup_weeks and (
            self.current_week in self.completed_weeks
        )

    @property
    def awaiting_next_week(self) -> bool:
        """Todo lo disponible está hecho y toca esperar al siguiente desbloqueo."""
        return (
            not self.catchup_weeks
            and self.current_week in self.completed_weeks
            and self.unlocked < self.total_weeks
        )


def compute_plan_state(
    enrolled_at: datetime,
    now: datetime,
    total_weeks: int,
    completed_weeks: Iterable[int],
) -> PlanState:
    completed = sorted(set(completed_weeks))
    unlocked = unlocked_week(enrolled_at, now, total_weeks)

    incomplete = [w for w in range(1, unlocked + 1) if w not in completed]
    if incomplete:
        current, catchup = incomplete[0], incomplete[1:]
    else:
        current, catchup = unlocked, []

    return PlanState(
        unlocked=unlocked,
        current_week=current,
        catchup_weeks=catchup,
        completed_weeks=[w for w in completed if w <= unlocked],
        total_weeks=total_weeks,
        next_unlock_at=next_unlock_at(enrolled_at, now, total_weeks),
    )
