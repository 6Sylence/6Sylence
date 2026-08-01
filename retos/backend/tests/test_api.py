"""Pruebas de la API de punta a punta contra un Mongo en memoria."""


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["total_weeks"] == 12


# ==================== Cuenta del adulto ====================


def test_el_alta_abre_la_prueba_gratuita(client, auth):
    response = client.get("/api/auth/me", headers=auth)
    assert response.status_code == 200
    entitlement = response.json()["entitlement"]
    assert entitlement["status"] == "trialing"
    assert entitlement["active"] is True


def test_no_se_puede_repetir_el_correo(client, parent_token):
    response = client.post(
        "/api/auth/register",
        json={"email": "madre@ejemplo.com", "password": "otraclavelarga"},
    )
    assert response.status_code == 409


def test_la_contrasena_incorrecta_no_distingue_del_correo_inexistente(client, parent_token):
    mala_clave = client.post(
        "/api/auth/login",
        json={"email": "madre@ejemplo.com", "password": "noesesta"},
    )
    no_existe = client.post(
        "/api/auth/login",
        json={"email": "nadie@ejemplo.com", "password": "noesesta"},
    )
    assert mala_clave.status_code == no_existe.status_code == 401
    assert mala_clave.json()["detail"] == no_existe.json()["detail"]


def test_sin_token_no_hay_datos(client):
    assert client.get("/api/children").status_code == 401


# ==================== Borrado de cuenta (exigido por Google Play) ====================


def test_borrar_la_cuenta_invalida_la_sesion(client, auth, child_id):
    assert client.delete("/api/auth/me", headers=auth).status_code == 204
    assert client.get("/api/auth/me", headers=auth).status_code == 401


def test_borrar_la_cuenta_se_lleva_perfiles_progreso_e_hitos(client, auth, child_id):
    week = client.get(f"/api/children/{child_id}/weeks/current", headers=auth).json()
    for item in week["activities"][:2]:
        client.post(
            f"/api/children/{child_id}/weeks/1/activities/{item['activity']['activity_id']}/complete",
            json={"validated_by_parent": True},
            headers=auth,
        )

    client.delete("/api/auth/me", headers=auth)

    # Una cuenta nueva con el mismo correo no puede heredar nada de la anterior.
    nueva = client.post(
        "/api/auth/register",
        json={"email": "madre@ejemplo.com", "password": "unaclavelarga"},
    )
    assert nueva.status_code == 201
    headers = {"Authorization": f"Bearer {nueva.json()['access_token']}"}
    assert client.get("/api/children", headers=headers).json() == []
    assert client.get(f"/api/children/{child_id}/plan", headers=headers).status_code == 404


def test_borrar_una_cuenta_no_toca_la_de_al_lado(client, auth, child_id):
    otra = client.post(
        "/api/auth/register",
        json={"email": "vecino@ejemplo.com", "password": "unaclavelarga"},
    ).json()
    headers = {"Authorization": f"Bearer {otra['access_token']}"}
    client.post(
        "/api/children",
        json={"name": "Bruno", "age_band": "5-6", "avatar_key": "buho"},
        headers=headers,
    )

    client.delete("/api/auth/me", headers=auth)

    assert client.get("/api/auth/me", headers=headers).status_code == 200
    assert len(client.get("/api/children", headers=headers).json()) == 1


def test_sin_sesion_no_se_puede_borrar_una_cuenta(client):
    assert client.delete("/api/auth/me").status_code == 401


# ==================== Perfil del niño ====================


def test_el_perfil_guarda_franja_de_edad_y_nada_mas(client, auth, child_id):
    response = client.get(f"/api/children/{child_id}", headers=auth)
    assert response.status_code == 200
    body = response.json()
    assert body["age_band"] == "3-4"
    # Lo que no aparece es tan importante como lo que aparece.
    assert set(body) == {"child_id", "name", "age_band", "avatar_key", "enrolled_at"}


def test_un_perfil_ajeno_no_existe_para_otra_cuenta(client, auth, child_id):
    otra = client.post(
        "/api/auth/register",
        json={"email": "otro@ejemplo.com", "password": "unaclavelarga"},
    ).json()
    headers = {"Authorization": f"Bearer {otra['access_token']}"}
    assert client.get(f"/api/children/{child_id}", headers=headers).status_code == 404


def test_borrar_el_perfil_se_lleva_el_progreso(client, auth, child_id):
    week = client.get(f"/api/children/{child_id}/weeks/current", headers=auth).json()
    activity = week["activities"][0]["activity"]["activity_id"]
    client.post(
        f"/api/children/{child_id}/weeks/1/activities/{activity}/complete",
        json={"validated_by_parent": True},
        headers=auth,
    )

    assert client.delete(f"/api/children/{child_id}", headers=auth).status_code == 204
    assert client.get(f"/api/children/{child_id}/plan", headers=auth).status_code == 404


# ==================== Semana y validación ====================


def test_el_plan_empieza_en_la_semana_uno(client, auth, child_id):
    plan = client.get(f"/api/children/{child_id}/plan", headers=auth).json()
    assert plan["current_week"] == 1
    assert plan["unlocked_week"] == 1
    assert plan["completed_weeks"] == []
    assert plan["plan_finished"] is False


def test_la_semana_actual_trae_tres_actividades_sin_pantalla(client, auth, child_id):
    week = client.get(f"/api/children/{child_id}/weeks/current", headers=auth).json()
    assert week["week_index"] == 1
    assert week["accessible"] is True
    assert len(week["activities"]) == 3
    assert all(item["activity"]["screen_free"] for item in week["activities"])


def _complete(client, auth, child_id, week_index, activity_id):
    return client.post(
        f"/api/children/{child_id}/weeks/{week_index}/activities/{activity_id}/complete",
        json={"validated_by_parent": True},
        headers=auth,
    )


def test_la_semana_se_completa_con_dos_actividades(client, auth, child_id):
    week = client.get(f"/api/children/{child_id}/weeks/current", headers=auth).json()
    ids = [item["activity"]["activity_id"] for item in week["activities"]]

    primera = _complete(client, auth, child_id, 1, ids[0]).json()
    assert primera["week_completed"] is False
    assert primera["reward"]["unlocked"] is False

    segunda = _complete(client, auth, child_id, 1, ids[1]).json()
    assert segunda["week_completed"] is True
    assert segunda["reward"]["unlocked"] is True


def test_validar_dos_veces_la_misma_actividad_no_la_cuenta_dos_veces(client, auth, child_id):
    week = client.get(f"/api/children/{child_id}/weeks/current", headers=auth).json()
    activity = week["activities"][0]["activity"]["activity_id"]

    _complete(client, auth, child_id, 1, activity)
    repetida = _complete(client, auth, child_id, 1, activity).json()
    assert repetida["completed_count"] == 1
    assert repetida["week_completed"] is False


def test_sin_la_confirmacion_del_adulto_no_se_valida(client, auth, child_id):
    week = client.get(f"/api/children/{child_id}/weeks/current", headers=auth).json()
    activity = week["activities"][0]["activity"]["activity_id"]
    response = client.post(
        f"/api/children/{child_id}/weeks/1/activities/{activity}/complete",
        json={"validated_by_parent": False},
        headers=auth,
    )
    assert response.status_code == 400


def test_se_puede_deshacer_una_validacion(client, auth, child_id):
    week = client.get(f"/api/children/{child_id}/weeks/current", headers=auth).json()
    activity = week["activities"][0]["activity"]["activity_id"]

    _complete(client, auth, child_id, 1, activity)
    deshecha = client.delete(
        f"/api/children/{child_id}/weeks/1/activities/{activity}/complete", headers=auth
    ).json()
    assert deshecha["completed_count"] == 0


def test_una_actividad_inventada_no_cuela(client, auth, child_id):
    assert _complete(client, auth, child_id, 1, "no-existe").status_code == 404


def test_la_semana_dos_esta_cerrada_por_calendario(client, auth, child_id):
    week = client.get(f"/api/children/{child_id}/weeks/2", headers=auth).json()
    assert week["accessible"] is False
    assert "todavía no está disponible" in week["locked_reason"]

    bloqueada = _complete(client, auth, child_id, 2, "w02-a1")
    assert bloqueada.status_code == 403


# ==================== Recompensa ====================


def _finish_week_one(client, auth, child_id):
    week = client.get(f"/api/children/{child_id}/weeks/current", headers=auth).json()
    ids = [item["activity"]["activity_id"] for item in week["activities"]]
    _complete(client, auth, child_id, 1, ids[0])
    _complete(client, auth, child_id, 1, ids[1])
    return week["reward"]["options"]


def test_no_se_puede_elegir_premio_sin_terminar_la_semana(client, auth, child_id):
    week = client.get(f"/api/children/{child_id}/weeks/current", headers=auth).json()
    option = week["reward"]["options"][0]["option_id"]
    response = client.post(
        f"/api/children/{child_id}/weeks/1/reward",
        json={"option_id": option},
        headers=auth,
    )
    assert response.status_code == 409


def test_el_nino_elige_entre_tres_premios(client, auth, child_id):
    options = _finish_week_one(client, auth, child_id)
    assert len(options) == 3
    assert {o["kind"] for o in options} == {"personaje", "historia", "imprimible"}

    elegido = client.post(
        f"/api/children/{child_id}/weeks/1/reward",
        json={"option_id": options[2]["option_id"]},
        headers=auth,
    ).json()
    assert elegido["reward"]["claimed"] is True
    assert elegido["reward"]["chosen_option_id"] == options[2]["option_id"]


def test_el_premio_se_elige_una_sola_vez(client, auth, child_id):
    options = _finish_week_one(client, auth, child_id)
    body = {"option_id": options[0]["option_id"]}
    client.post(f"/api/children/{child_id}/weeks/1/reward", json=body, headers=auth)
    repetido = client.post(f"/api/children/{child_id}/weeks/1/reward", json=body, headers=auth)
    assert repetido.status_code == 409


def test_deshacer_no_le_quita_el_premio_ya_elegido(client, auth, child_id):
    options = _finish_week_one(client, auth, child_id)
    client.post(
        f"/api/children/{child_id}/weeks/1/reward",
        json={"option_id": options[0]["option_id"]},
        headers=auth,
    )
    week = client.get(f"/api/children/{child_id}/weeks/1", headers=auth).json()
    activity = week["activities"][0]["activity"]["activity_id"]

    tras_deshacer = client.delete(
        f"/api/children/{child_id}/weeks/1/activities/{activity}/complete", headers=auth
    ).json()
    assert tras_deshacer["reward"]["claimed"] is True


# ==================== Hitos ====================


def test_la_semana_uno_no_genera_envio(client, auth, child_id):
    _finish_week_one(client, auth, child_id)
    hitos = client.get(f"/api/children/{child_id}/milestones", headers=auth).json()
    assert hitos == []


# ==================== Contenido y facturación ====================


def test_el_catalogo_expone_las_doce_semanas(client):
    semanas = client.get("/api/content/weeks").json()
    assert len(semanas) == 12
    assert [s["week_index"] for s in semanas] == list(range(1, 13))


def test_el_webhook_de_facturacion_esta_cerrado_sin_secreto(client):
    response = client.post("/api/billing/webhook", json={"parent_id": "par_x", "status": "active"})
    assert response.status_code == 401
