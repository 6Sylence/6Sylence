"""Titularidad de la suscripción.

Esqueleto. La suscripción digital **tiene que** pasar por Google Play Billing
(la comisión es del 15% del primer millón anual); no se puede cobrar con Stripe
dentro de la app. Lo que falta aquí es la validación del recibo contra la API
de Google Play Developer, normalmente vía RevenueCat.

Lo que sí está resuelto: el cliente nunca escribe su propia titularidad. Solo
lee. Quien la cambia es el webhook.
"""

import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from ..db import get_db
from ..models import EntitlementResponse, EntitlementStatus, Parent
from ..security import current_parent
from ..services import entitlement_response

router = APIRouter(prefix="/billing", tags=["billing"])

# Secreto compartido con el emisor del webhook. Sin él configurado, el endpoint
# queda cerrado en lugar de abierto.
WEBHOOK_SECRET = os.environ.get("BILLING_WEBHOOK_SECRET", "")


@router.get("/entitlement", response_model=EntitlementResponse)
async def get_entitlement(parent: Parent = Depends(current_parent)):
    return entitlement_response(parent)


@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def billing_webhook(request: Request, x_webhook_secret: str = Header(default="")):
    """Recibe cambios de estado de la suscripción.

    TODO (antes de publicar): validar el recibo contra Google Play en lugar de
    fiarse del cuerpo del mensaje. Tal cual está, un secreto filtrado permite
    regalar suscripciones.
    """
    if not WEBHOOK_SECRET or x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Webhook no autorizado")

    payload = await request.json()
    parent_id = payload.get("parent_id")
    new_status = payload.get("status")
    if not parent_id or new_status not in {s.value for s in EntitlementStatus}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payload no válido")

    result = await get_db().parents.update_one(
        {"parent_id": parent_id},
        {
            "$set": {
                "entitlement.status": new_status,
                "entitlement.expires_at": payload.get("expires_at"),
                "entitlement.source": "google_play",
                "entitlement.product_id": payload.get("product_id"),
            }
        },
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta no encontrada")
    return {"ok": True}
