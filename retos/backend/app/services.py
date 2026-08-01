"""Servicios que unen el motor (puro) con la base de datos."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status

from . import engine
from .config import settings
from .content import get_week, total_weeks
from .db import get_db
from .models import (
    ActivityStatus,
    Child,
    ChildResponse,
    Entitlement,
    EntitlementResponse,
    EntitlementStatus,
    MilestoneReward,
    Parent,
    PlanView,
    RewardStatus,
    WeekProgress,
    WeekView,
    utcnow,
)

_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin caracteres ambiguos


def new_trial_entitlement(now: datetime | None = None) -> Entitlement:
    now = now or utcnow()
    return Entitlement(
        status=EntitlementStatus.TRIALING,
        expires_at=now + timedelta(days=settings.trial_days),
        source="trial",
    )


def entitlement_response(parent: Parent, now: datetime | None = None) -> EntitlementResponse:
    now = now or utcnow()
    return EntitlementResponse(
        status=parent.entitlement.status,
        expires_at=parent.entitlement.expires_at,
        active=engine.has_entitlement(parent.entitlement, now),
    )


def child_response(child: Child) -> ChildResponse:
    return ChildResponse(
        child_id=child.child_id,
        name=child.name,
        age_band=child.age_band,
        avatar_key=child.avatar_key,
        enrolled_at=child.enrolled_at,
    )


async def get_owned_child(child_id: str, parent: Parent) -> Child:
    """Carga un niño comprobando que pertenece a quien pregunta.

    Devolver 404 y no 403 cuando el niño existe pero es de otra cuenta es
    deliberado: no confirmamos la existencia de perfiles ajenos.
    """
    doc = await get_db().children.find_one(
        {"child_id": child_id, "parent_id": parent.parent_id}, {"_id": 0}
    )
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    return Child(**doc)


async def load_progress(child_id: str) -> dict[int, WeekProgress]:
    cursor = get_db().week_progress.find({"child_id": child_id}, {"_id": 0})
    return {doc["week_index"]: WeekProgress(**doc) async for doc in cursor}


async def get_or_create_progress(child_id: str, week_index: int) -> WeekProgress:
    db = get_db()
    doc = await db.week_progress.find_one(
        {"child_id": child_id, "week_index": week_index}, {"_id": 0}
    )
    if doc is not None:
        return WeekProgress(**doc)
    progress = WeekProgress(child_id=child_id, week_index=week_index)
    await db.week_progress.insert_one(progress.model_dump())
    return progress


def completed_week_indexes(progress_by_week: dict[int, WeekProgress]) -> list[int]:
    return [index for index, progress in progress_by_week.items() if progress.completed_at is not None]


async def build_plan_view(child: Child, parent: Parent, now: datetime | None = None) -> PlanView:
    now = now or utcnow()
    progress_by_week = await load_progress(child.child_id)
    state = engine.compute_plan_state(
        enrolled_at=child.enrolled_at,
        now=now,
        total_weeks=total_weeks(),
        completed_weeks=completed_week_indexes(progress_by_week),
    )
    return PlanView(
        child=child_response(child),
        total_weeks=state.total_weeks,
        unlocked_week=state.unlocked,
        current_week=state.current_week,
        catchup_weeks=state.catchup_weeks,
        completed_weeks=state.completed_weeks,
        plan_finished=state.plan_finished,
        next_unlock_at=state.next_unlock_at,
    )


async def build_week_view(
    child: Child, parent: Parent, week_index: int, now: datetime | None = None
) -> WeekView:
    now = now or utcnow()
    template = get_week(week_index)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semana no encontrada")

    progress_by_week = await load_progress(child.child_id)
    progress = progress_by_week.get(week_index)
    completed_ids = set(progress.completed_activity_ids) if progress else set()

    entitled = engine.has_entitlement(parent.entitlement, now)
    unlocked = engine.unlocked_week(child.enrolled_at, now, total_weeks())
    accessible = week_index <= unlocked and engine.is_week_accessible(week_index, entitled)

    week_completed = progress is not None and progress.completed_at is not None
    reward_claimed = progress is not None and progress.reward_claimed_at is not None

    return WeekView(
        week_index=week_index,
        title=template.title,
        subtitle=template.subtitle,
        activities=[
            ActivityStatus(activity=activity, completed=activity.activity_id in completed_ids)
            for activity in template.activities
        ],
        completed_count=len(completed_ids),
        activities_required=min(engine.ACTIVITIES_REQUIRED, len(template.activities)),
        week_completed=week_completed,
        accessible=accessible,
        locked_reason=engine.locked_reason(week_index, entitled, unlocked),
        reward=RewardStatus(
            unlocked=week_completed,
            claimed=reward_claimed,
            options=template.reward_options,
            chosen_option_id=progress.reward_option_id if progress else None,
        ),
    )


def _new_milestone_code() -> str:
    body = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(8))
    return f"RT-{body[:4]}-{body[4:]}"


async def grant_milestone_if_due(child: Child, parent: Parent, week_index: int) -> MilestoneReward | None:
    """Crea la recompensa física de hito si toca y no existe ya.

    El código se canjea en la web, nunca dentro de la app: Google Play prohíbe
    su facturación para bienes físicos, y pedir una dirección postal dentro de
    una app infantil es justo lo que no queremos hacer.
    """
    if not engine.milestone_for_week(week_index):
        return None

    db = get_db()
    existing = await db.milestone_rewards.find_one(
        {"child_id": child.child_id, "week_index": week_index}, {"_id": 0}
    )
    if existing is not None:
        return MilestoneReward(**existing)

    milestone = MilestoneReward(
        child_id=child.child_id,
        parent_id=parent.parent_id,
        week_index=week_index,
        code=_new_milestone_code(),
    )
    await db.milestone_rewards.insert_one(milestone.model_dump())
    return milestone
