"""Configuración leída del entorno.

El proyecto es independiente del marketplace: usa su propia base de datos y su
propio secreto de firma. No compartir `DB_NAME` entre ambos.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


# Valor de relleno para desarrollo. Tiene longitud suficiente para no disparar
# el aviso de PyJWT, pero no debe llegar a producción: `main.py` avisa si sigue
# puesto al arrancar.
DEV_JWT_SECRET = "desarrollo-cambiame-en-produccion-32bytes"


class Settings:
    mongo_url: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name: str = os.environ.get("DB_NAME", "retos_dev")

    jwt_secret: str = os.environ.get("JWT_SECRET", DEV_JWT_SECRET)
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = int(os.environ.get("JWT_EXPIRE_DAYS", "30"))

    trial_days: int = int(os.environ.get("TRIAL_DAYS", "7"))

    @property
    def cors_origins(self) -> list[str]:
        raw = os.environ.get("CORS_ORIGINS", "*")
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


settings = Settings()
