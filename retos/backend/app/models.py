"""Modelos de dominio.

Principio que atraviesa todo el fichero: **minimización de datos del menor**.
El niño no es un usuario del sistema. No tiene cuenta, ni credenciales, ni
identificador estable fuera de la cuenta de su padre o madre. De él se guardan
dos cosas: un nombre (que puede ser un mote) y una franja de edad. Nunca fecha
de nacimiento, ni foto, ni ubicación, ni identificador publicitario.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ==================== Enumeraciones ====================


class AgeBand(str, Enum):
    """Franja de edad. Sustituye deliberadamente a la fecha de nacimiento."""

    B3_4 = "3-4"
    B5_6 = "5-6"


class SkillArea(str, Enum):
    """Áreas de desarrollo que cubre el contenido.

    Son descriptivas del tipo de actividad. No son un diagnóstico ni una
    medida clínica, y el copy de la app no debe presentarlas como tal.
    """

    MOTRICIDAD_FINA = "motricidad_fina"
    LENGUAJE = "lenguaje"
    LOGICA = "logica"
    ATENCION = "atencion"
    SOCIOEMOCIONAL = "socioemocional"


class RewardKind(str, Enum):
    """Tipos de recompensa semanal. Todas digitales: coste marginal cero."""

    CHARACTER = "personaje"
    STORY = "historia"
    PRINTABLE = "imprimible"


class EntitlementStatus(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    EXPIRED = "expired"
    NONE = "none"


class MilestoneStatus(str, Enum):
    PENDING = "pendiente"
    REDEEMED = "canjeado"


# ==================== Contenido (estático, versionado con el código) ====================


class Activity(BaseModel):
    activity_id: str
    title: str
    instructions: str
    skill_area: SkillArea
    materials: list[str] = []
    est_minutes: int = 10
    # Todas las actividades del MVP se hacen fuera de la pantalla. El campo es
    # explícito para que una futura actividad en pantalla sea una decisión
    # consciente y auditable, no un descuido.
    screen_free: bool = True


class RewardOption(BaseModel):
    option_id: str
    kind: RewardKind
    title: str
    description: str
    asset_key: str


class WeekTemplate(BaseModel):
    week_index: int = Field(ge=1)
    title: str
    subtitle: str
    age_bands: list[AgeBand] = [AgeBand.B3_4, AgeBand.B5_6]
    activities: list[Activity]
    reward_options: list[RewardOption]


# ==================== Persistido ====================


class Entitlement(BaseModel):
    status: EntitlementStatus = EntitlementStatus.NONE
    expires_at: Optional[datetime] = None
    # Origen de la titularidad. En producción lo escribe el webhook de Google
    # Play; nunca el cliente.
    source: Optional[str] = None
    product_id: Optional[str] = None


class Parent(BaseModel):
    parent_id: str = Field(default_factory=lambda: new_id("par"))
    email: EmailStr
    password_hash: str
    entitlement: Entitlement = Field(default_factory=Entitlement)
    created_at: datetime = Field(default_factory=utcnow)


class Child(BaseModel):
    child_id: str = Field(default_factory=lambda: new_id("kid"))
    parent_id: str
    name: str
    age_band: AgeBand
    avatar_key: str = "zorro"
    # Ancla del calendario: la semana N se desbloquea N-1 semanas después de
    # esta fecha. Anclar a la inscripción y no al lunes evita que quien se
    # apunta un domingo reciba semana nueva al día siguiente.
    enrolled_at: datetime = Field(default_factory=utcnow)
    created_at: datetime = Field(default_factory=utcnow)


class WeekProgress(BaseModel):
    """Progreso de un niño en una semana concreta.

    `completed_activity_ids` es la única huella de la validación. La foto que
    el padre hace para validar **no se envía ni se almacena**: se queda en el
    dispositivo y la API solo recibe la confirmación.
    """

    progress_id: str = Field(default_factory=lambda: new_id("prg"))
    child_id: str
    week_index: int
    completed_activity_ids: list[str] = []
    completed_at: Optional[datetime] = None
    reward_option_id: Optional[str] = None
    reward_claimed_at: Optional[datetime] = None
    started_at: datetime = Field(default_factory=utcnow)


class MilestoneReward(BaseModel):
    """Recompensa física de hito (semanas 4, 8 y 12).

    Nunca se compra dentro de la app: Google Play prohíbe usar su facturación
    para bienes físicos. La app entrega un código y el canje ocurre en la web,
    donde el adulto introduce la dirección de envío.
    """

    milestone_id: str = Field(default_factory=lambda: new_id("mil"))
    child_id: str
    parent_id: str
    week_index: int
    code: str
    status: MilestoneStatus = MilestoneStatus.PENDING
    created_at: datetime = Field(default_factory=utcnow)
    redeemed_at: Optional[datetime] = None


# ==================== Entrada de la API ====================


class ParentRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class ParentLoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChildCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    age_band: AgeBand
    avatar_key: str = "zorro"


class ChildUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=40)
    age_band: Optional[AgeBand] = None
    avatar_key: Optional[str] = None


class ActivityCompleteRequest(BaseModel):
    """Confirmación de que un adulto ha visto el reto hecho.

    Deliberadamente **no** existe un campo para la imagen. Si algún día se
    quiere conservar el recuerdo, debe guardarse en el dispositivo, no aquí.
    """

    validated_by_parent: bool = True


class RewardChoiceRequest(BaseModel):
    option_id: str


class MilestoneRedeemRequest(BaseModel):
    code: str


# ==================== Salida de la API ====================


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    parent_id: str


class EntitlementResponse(BaseModel):
    status: EntitlementStatus
    expires_at: Optional[datetime] = None
    active: bool


class ParentResponse(BaseModel):
    parent_id: str
    email: EmailStr
    entitlement: EntitlementResponse
    created_at: datetime


class ChildResponse(BaseModel):
    child_id: str
    name: str
    age_band: AgeBand
    avatar_key: str
    enrolled_at: datetime


class ActivityStatus(BaseModel):
    activity: Activity
    completed: bool


class RewardStatus(BaseModel):
    unlocked: bool
    claimed: bool
    options: list[RewardOption]
    chosen_option_id: Optional[str] = None


class WeekView(BaseModel):
    """Lo que la app necesita para pintar la pantalla del reto semanal."""

    week_index: int
    title: str
    subtitle: str
    activities: list[ActivityStatus]
    completed_count: int
    activities_required: int
    week_completed: bool
    accessible: bool
    locked_reason: Optional[str] = None
    reward: RewardStatus


class PlanView(BaseModel):
    child: ChildResponse
    total_weeks: int
    unlocked_week: int
    current_week: int
    catchup_weeks: list[int]
    completed_weeks: list[int]
    plan_finished: bool
    next_unlock_at: Optional[datetime] = None


class MilestoneResponse(BaseModel):
    milestone_id: str
    week_index: int
    code: str
    status: MilestoneStatus
    created_at: datetime
    redeemed_at: Optional[datetime] = None
