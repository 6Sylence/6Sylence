"""Catálogo de contenido.

Las semanas viven en el código (`app/content/weeks.py`), no en la base de
datos: son contenido versionado, se revisan en un pull request y no deben poder
cambiarse en caliente. El volcado a Mongo es solo para inspección.
"""

from fastapi import APIRouter

from ..content import WEEKS, total_weeks
from ..db import get_db
from ..models import WeekTemplate

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/weeks", response_model=list[WeekTemplate])
async def list_weeks():
    return WEEKS


@router.post("/seed")
async def seed_weeks():
    db = get_db()
    for week in WEEKS:
        await db.week_templates.update_one(
            {"week_index": week.week_index}, {"$set": week.model_dump()}, upsert=True
        )
    return {"seeded_weeks": total_weeks()}
