# Retos — MVP

App de retos semanales para niños de 3 a 6 años. La app **propone** el reto, el niño lo
hace **fuera de la pantalla**, el padre lo valida, y al completar la semana el niño
**elige** su recompensa.

> Proyecto independiente. No comparte código, base de datos ni despliegue con el
> marketplace que vive en `backend/` y `frontend/` en la raíz del repositorio.

## Estructura

```
retos/
  backend/        API FastAPI + MongoDB (base de datos propia)
    app/
      engine.py   Motor de retos — lógica pura, sin dependencias de I/O
      routers/    Endpoints HTTP
      content/    Contenido de las 12 semanas (semilla)
    tests/        Tests del motor (no requieren Mongo)
  app/            Aplicación Expo (React Native, expo-router)
```

## Decisiones de producto codificadas

Estas reglas están implementadas, no son documentación aspiracional:

| Decisión | Dónde vive |
|---|---|
| La cuenta es **del padre**. El niño no tiene cuenta, credenciales ni login. | `models.py` — `Child` cuelga de `Parent` |
| **Ninguna foto sale del dispositivo.** El endpoint de validación recibe un booleano. | `routers/progress.py` |
| Del niño se guarda **nombre y franja de edad**, nunca fecha de nacimiento. | `models.py` — `Child.age_band` |
| **Semana perdida no se castiga**: queda pendiente y se puede retomar. | `engine.py` — `compute_week_state` |
| Semana completa con **2 de 3** actividades, no 3 de 3. | `engine.py` — `ACTIVITIES_REQUIRED` |
| **Semana 1 gratis**, de la 2 en adelante requiere suscripción. | `engine.py` — `is_week_accessible` |
| Recompensa semanal **digital** (coste marginal cero). | `content/weeks.py` — `RewardOption` |
| Recompensa física solo en **hitos** (semanas 4, 8, 12) y **por código canjeable fuera de la app**. | `engine.py` — `milestone_for_week` |
| Sin rachas, sin contadores de días perdidos, sin notificaciones al niño. | Ausencia deliberada en todo el modelo |

## Arrancar

### Backend

```bash
cd retos/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # ajusta MONGO_URL
uvicorn app.main:app --reload --port 8001
```

Documentación interactiva en `http://localhost:8001/docs`.

Para cargar las 12 semanas de contenido en la base de datos:

```bash
curl -X POST http://localhost:8001/api/content/seed
```

### App

```bash
cd retos/app
yarn install
cp .env.example .env          # ajusta EXPO_PUBLIC_API_URL
yarn start
```

### Tests

```bash
cd retos/backend
pip install -r requirements-dev.txt
pytest
```

51 tests. Los del motor son puros; los de la API corren contra un Mongo en memoria
(`mongomock-motor`), así que la suite entera funciona sin levantar nada.

```bash
cd retos/app && npx tsc --noEmit   # la app se comprueba con el typechecker
```

## Estado

MVP esqueleto: navegación, modelos, motor de retos y endpoints funcionando de punta a
punta con contenido de ejemplo.

Verificado: 51 tests en verde, typecheck de la app limpio y la API arranca y responde
(`/api/health`, `/docs`) aunque Mongo no esté disponible. No se ha ejecutado la app en un
dispositivo ni en emulador.

Pendiente y deliberadamente fuera de este esqueleto:

- **Contenido real de las 12 semanas** y las ilustraciones de recompensa (fase B).
- **Facturación**: integración con Google Play Billing / RevenueCat. El backend ya
  modela la titularidad (`entitlement`) y expone un webhook, pero no valida recibos.
- Canje de la recompensa física contra la tienda.
