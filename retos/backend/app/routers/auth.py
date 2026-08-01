"""Alta y sesión del adulto."""

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from ..db import get_db
from ..models import (
    Parent,
    ParentLoginRequest,
    ParentRegisterRequest,
    ParentResponse,
    TokenResponse,
)
from ..security import create_access_token, current_parent, hash_password, verify_password
from ..services import entitlement_response, new_trial_entitlement

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: ParentRegisterRequest):
    parent = Parent(
        email=payload.email,
        password_hash=hash_password(payload.password),
        entitlement=new_trial_entitlement(),
    )
    try:
        await get_db().parents.insert_one(parent.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ese correo ya está registrado"
        )
    return TokenResponse(access_token=create_access_token(parent.parent_id), parent_id=parent.parent_id)


@router.post("/login", response_model=TokenResponse)
async def login(payload: ParentLoginRequest):
    doc = await get_db().parents.find_one({"email": payload.email}, {"_id": 0})
    # Mismo mensaje para correo inexistente y contraseña incorrecta: no
    # revelamos qué correos están dados de alta.
    if doc is None or not verify_password(payload.password, doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña incorrectos"
        )
    parent = Parent(**doc)
    return TokenResponse(access_token=create_access_token(parent.parent_id), parent_id=parent.parent_id)


@router.get("/me", response_model=ParentResponse)
async def me(parent: Parent = Depends(current_parent)):
    return ParentResponse(
        parent_id=parent.parent_id,
        email=parent.email,
        entitlement=entitlement_response(parent),
        created_at=parent.created_at,
    )
