"""Perfiles de niño.

Un perfil no es una cuenta: cuelga del adulto, no tiene credenciales y guarda
lo mínimo (nombre y franja de edad).
"""

from fastapi import APIRouter, Depends, status

from ..db import get_db
from ..models import (
    Child,
    ChildCreateRequest,
    ChildResponse,
    ChildUpdateRequest,
    Parent,
)
from ..security import current_parent
from ..services import child_response, get_owned_child

router = APIRouter(prefix="/children", tags=["children"])


@router.post("", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
async def create_child(payload: ChildCreateRequest, parent: Parent = Depends(current_parent)):
    child = Child(
        parent_id=parent.parent_id,
        name=payload.name,
        age_band=payload.age_band,
        avatar_key=payload.avatar_key,
    )
    await get_db().children.insert_one(child.model_dump())
    return child_response(child)


@router.get("", response_model=list[ChildResponse])
async def list_children(parent: Parent = Depends(current_parent)):
    cursor = get_db().children.find({"parent_id": parent.parent_id}, {"_id": 0})
    return [child_response(Child(**doc)) async for doc in cursor]


@router.get("/{child_id}", response_model=ChildResponse)
async def get_child(child_id: str, parent: Parent = Depends(current_parent)):
    return child_response(await get_owned_child(child_id, parent))


@router.patch("/{child_id}", response_model=ChildResponse)
async def update_child(
    child_id: str, payload: ChildUpdateRequest, parent: Parent = Depends(current_parent)
):
    child = await get_owned_child(child_id, parent)
    changes = payload.model_dump(exclude_none=True)
    if changes:
        await get_db().children.update_one({"child_id": child.child_id}, {"$set": changes})
        child = child.model_copy(update=changes)
    return child_response(child)


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child(child_id: str, parent: Parent = Depends(current_parent)):
    """Borrado real, no lógico.

    Se lleva por delante el progreso y los hitos del perfil. Es la vía por la
    que el adulto ejerce el derecho de supresión sobre los datos del menor, así
    que no debe dejar rastro ni banderas de "borrado".
    """
    child = await get_owned_child(child_id, parent)
    db = get_db()
    await db.week_progress.delete_many({"child_id": child.child_id})
    await db.milestone_rewards.delete_many({"child_id": child.child_id})
    await db.children.delete_one({"child_id": child.child_id})
