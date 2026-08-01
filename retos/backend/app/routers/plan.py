"""Plan semanal: ver la semana, validar actividades y elegir recompensa."""

from fastapi import APIRouter, Depends, HTTPException, status

from .. import engine
from ..content import get_week, total_weeks
from ..db import get_db
from ..models import (
    ActivityCompleteRequest,
    MilestoneRedeemRequest,
    MilestoneResponse,
    MilestoneStatus,
    Parent,
    PlanView,
    RewardChoiceRequest,
    WeekView,
    utcnow,
)
from ..security import current_parent
from ..services import (
    build_plan_view,
    build_week_view,
    get_or_create_progress,
    get_owned_child,
    grant_milestone_if_due,
)

router = APIRouter(prefix="/children/{child_id}", tags=["plan"])


@router.get("/plan", response_model=PlanView)
async def get_plan(child_id: str, parent: Parent = Depends(current_parent)):
    child = await get_owned_child(child_id, parent)
    return await build_plan_view(child, parent)


@router.get("/weeks/current", response_model=WeekView)
async def get_current_week(child_id: str, parent: Parent = Depends(current_parent)):
    """La semana que la app abre por defecto.

    Es la más antigua sin completar entre las desbloqueadas. Si el niño se
    saltó una semana, vuelve a ella en lugar de perderla.
    """
    child = await get_owned_child(child_id, parent)
    plan = await build_plan_view(child, parent)
    return await build_week_view(child, parent, plan.current_week)


@router.get("/weeks/{week_index}", response_model=WeekView)
async def get_week_view(child_id: str, week_index: int, parent: Parent = Depends(current_parent)):
    child = await get_owned_child(child_id, parent)
    return await build_week_view(child, parent, week_index)


async def _assert_week_playable(child, parent, week_index: int) -> None:
    now = utcnow()
    unlocked = engine.unlocked_week(child.enrolled_at, now, total_weeks())
    entitled = engine.has_entitlement(parent.entitlement, now)
    reason = engine.locked_reason(week_index, entitled, unlocked)
    if reason is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)


@router.post("/weeks/{week_index}/activities/{activity_id}/complete", response_model=WeekView)
async def complete_activity(
    child_id: str,
    week_index: int,
    activity_id: str,
    payload: ActivityCompleteRequest,
    parent: Parent = Depends(current_parent),
):
    """Marca una actividad como hecha.

    El adulto valida mirando: hace la foto si quiere, pero la foto **no viaja**.
    Aquí solo entra un booleano, y lo que se guarda es el identificador de la
    actividad y la fecha.
    """
    child = await get_owned_child(child_id, parent)
    template = get_week(week_index)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semana no encontrada")
    if activity_id not in {a.activity_id for a in template.activities}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")
    if not payload.validated_by_parent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Falta la validación del adulto"
        )
    await _assert_week_playable(child, parent, week_index)

    progress = await get_or_create_progress(child.child_id, week_index)
    completed = set(progress.completed_activity_ids) | {activity_id}
    updates: dict = {"completed_activity_ids": sorted(completed)}

    if progress.completed_at is None and engine.is_week_complete(
        completed, [a.activity_id for a in template.activities]
    ):
        updates["completed_at"] = utcnow()

    await get_db().week_progress.update_one(
        {"progress_id": progress.progress_id}, {"$set": updates}
    )

    if "completed_at" in updates:
        await grant_milestone_if_due(child, parent, week_index)

    return await build_week_view(child, parent, week_index)


@router.delete("/weeks/{week_index}/activities/{activity_id}/complete", response_model=WeekView)
async def undo_activity(
    child_id: str, week_index: int, activity_id: str, parent: Parent = Depends(current_parent)
):
    """Deshace una validación.

    Existe porque a esta edad se pulsa por error constantemente. Deshacer no
    revoca la recompensa ya elegida: quitarle algo al niño por un fallo del
    adulto sería exactamente el tipo de mecánica que este producto evita.
    """
    child = await get_owned_child(child_id, parent)
    progress = await get_or_create_progress(child.child_id, week_index)
    remaining = [a for a in progress.completed_activity_ids if a != activity_id]
    await get_db().week_progress.update_one(
        {"progress_id": progress.progress_id}, {"$set": {"completed_activity_ids": remaining}}
    )
    return await build_week_view(child, parent, week_index)


@router.post("/weeks/{week_index}/reward", response_model=WeekView)
async def choose_reward(
    child_id: str,
    week_index: int,
    payload: RewardChoiceRequest,
    parent: Parent = Depends(current_parent),
):
    """El niño elige una de las tres recompensas de la semana.

    Elegir es el momento importante del producto: es la única decisión que el
    niño toma solo. Una vez elegida no se cambia, para que la elección tenga
    peso.
    """
    child = await get_owned_child(child_id, parent)
    template = get_week(week_index)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semana no encontrada")
    if payload.option_id not in {o.option_id for o in template.reward_options}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recompensa no encontrada")

    progress = await get_or_create_progress(child.child_id, week_index)
    if progress.completed_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Todavía no has terminado la semana"
        )
    if progress.reward_claimed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ya elegiste la recompensa de esta semana"
        )

    await get_db().week_progress.update_one(
        {"progress_id": progress.progress_id},
        {"$set": {"reward_option_id": payload.option_id, "reward_claimed_at": utcnow()}},
    )
    return await build_week_view(child, parent, week_index)


@router.get("/milestones", response_model=list[MilestoneResponse])
async def list_milestones(child_id: str, parent: Parent = Depends(current_parent)):
    child = await get_owned_child(child_id, parent)
    cursor = get_db().milestone_rewards.find({"child_id": child.child_id}, {"_id": 0})
    return [MilestoneResponse(**doc) async for doc in cursor]


@router.post("/milestones/redeem", response_model=MilestoneResponse)
async def redeem_milestone(
    child_id: str, payload: MilestoneRedeemRequest, parent: Parent = Depends(current_parent)
):
    """Marca un código de hito como canjeado.

    Lo llama la web de la tienda cuando el adulto completa el envío, no la app.
    Aquí no se piden ni se guardan datos de envío.
    """
    child = await get_owned_child(child_id, parent)
    db = get_db()
    doc = await db.milestone_rewards.find_one(
        {"code": payload.code.strip().upper(), "child_id": child.child_id}, {"_id": 0}
    )
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Código no válido")
    milestone = MilestoneResponse(**doc)
    if milestone.status is MilestoneStatus.REDEEMED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ese código ya se canjeó")

    now = utcnow()
    await db.milestone_rewards.update_one(
        {"milestone_id": milestone.milestone_id},
        {"$set": {"status": MilestoneStatus.REDEEMED.value, "redeemed_at": now}},
    )
    return milestone.model_copy(update={"status": MilestoneStatus.REDEEMED, "redeemed_at": now})
