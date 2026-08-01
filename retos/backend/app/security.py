"""Autenticación del adulto.

Solo hay un tipo de credencial en el sistema: la del padre o madre. El niño no
inicia sesión nunca, por diseño.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings
from .db import get_db
from .models import Parent

_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(parent_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": parent_id,
        "iat": now,
        "exp": now + timedelta(days=settings.jwt_expire_days),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión no válida"
        )
    parent_id = payload.get("sub")
    if not parent_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión no válida"
        )
    return parent_id


async def current_parent(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> Parent:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta la sesión"
        )
    parent_id = decode_access_token(credentials.credentials)
    doc = await get_db().parents.find_one({"parent_id": parent_id}, {"_id": 0})
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión no válida"
        )
    return Parent(**doc)
