"""API de Retos.

Aplicación independiente. No importa nada del marketplace ni comparte su base
de datos.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import CORSMiddleware

from .config import DEV_JWT_SECRET, settings
from .content import total_weeks
from .db import close_client, ensure_indexes
from .routers import auth, billing, children, content, plan

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("retos")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.jwt_secret == DEV_JWT_SECRET:
        logger.warning(
            "JWT_SECRET sigue siendo el de desarrollo. Genera uno propio antes de publicar."
        )
    try:
        await ensure_indexes()
    except Exception:  # la API arranca aunque Mongo aún no esté listo
        logger.exception("No se pudieron crear los índices")
    yield
    await close_client()


app = FastAPI(title="Retos API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")


@api_router.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "total_weeks": total_weeks()}


api_router.include_router(auth.router)
api_router.include_router(children.router)
api_router.include_router(plan.router)
api_router.include_router(content.router)
api_router.include_router(billing.router)

app.include_router(api_router)
