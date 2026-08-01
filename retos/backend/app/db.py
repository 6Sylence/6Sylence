"""Acceso a MongoDB.

Las colecciones viven en una base de datos propia (`DB_NAME`), separada de
cualquier otro proyecto del repositorio.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        # tz_aware=True no es opcional: sin él, Mongo devuelve las fechas sin
        # zona horaria y el motor de retos revienta al compararlas con un
        # `now` con zona (enrolled_at, expires_at).
        # serverSelectionTimeoutMS acotado: con el valor por defecto (30 s) la
        # API tarda medio minuto en responder cuando Mongo no está levantado,
        # en lugar de arrancar y fallar rápido.
        _client = AsyncIOMotorClient(
            settings.mongo_url, tz_aware=True, serverSelectionTimeoutMS=5000
        )
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[settings.db_name]


async def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


async def ensure_indexes() -> None:
    db = get_db()
    await db.parents.create_index("email", unique=True)
    await db.children.create_index("parent_id")
    await db.week_progress.create_index([("child_id", 1), ("week_index", 1)], unique=True)
    await db.milestone_rewards.create_index("code", unique=True)
    await db.milestone_rewards.create_index([("child_id", 1), ("week_index", 1)], unique=True)
    await db.week_templates.create_index("week_index", unique=True)
