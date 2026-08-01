"""Infraestructura de pruebas.

La API se prueba contra un Mongo en memoria. Se sustituye `get_client`, no
`get_db`: los routers importan `get_db` por referencia, pero `get_db` resuelve
`get_client` en el módulo en cada llamada, así que este es el único punto que
hay que tocar.
"""

import pytest
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient

from app import db as db_module


@pytest.fixture
def client(monkeypatch):
    mock_client = AsyncMongoMockClient(tz_aware=True)
    monkeypatch.setattr(db_module, "get_client", lambda: mock_client)

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def parent_token(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "madre@ejemplo.com", "password": "unaclavelarga"},
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


@pytest.fixture
def auth(parent_token):
    return {"Authorization": f"Bearer {parent_token}"}


@pytest.fixture
def child_id(client, auth):
    response = client.post(
        "/api/children",
        json={"name": "Lucía", "age_band": "3-4", "avatar_key": "zorro"},
        headers=auth,
    )
    assert response.status_code == 201, response.text
    return response.json()["child_id"]
