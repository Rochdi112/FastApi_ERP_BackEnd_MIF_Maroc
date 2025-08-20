import pytest

@pytest.fixture()
def equipement(client, responsable_token):
    headers = {"Authorization": f"Bearer {responsable_token}"}
    payload = {
        "nom": "Machine Test",
        "type": "électrique",
        "localisation": "Atelier A",
        "frequence_entretien": "30"
    }
    response = client.post("/api/v1/equipements/", json=payload, headers=headers)
    assert response.status_code == 200
    return response.json()

def test_create_intervention(client, responsable_token, equipement):
    headers = {"Authorization": f"Bearer {responsable_token}"}
    payload = {
        "titre": "Nouvelle Intervention",
        "description": "Création pour test",
        "type": "corrective",
        "statut": "ouverte",
        "urgence": True,
        "equipement_id": equipement["id"]
    }
    response = client.post("/api/v1/interventions/", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["titre"] == payload["titre"]
    assert data["type"] == "corrective"
    assert data["urgence"] is True

def test_get_intervention_by_id(client, responsable_token, equipement):
    headers = {"Authorization": f"Bearer {responsable_token}"}
    payload = {
        "titre": "À retrouver",
        "description": "Test get by id",
        "type": "corrective",
        "statut": "ouverte",
        "urgence": False,
        "equipement_id": equipement["id"]
    }
    create_resp = client.post("/api/v1/interventions/", json=payload, headers=headers)
    assert create_resp.status_code == 200
    interv_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/interventions/{interv_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == interv_id

def test_get_all_interventions(client, responsable_token):
    headers = {"Authorization": f"Bearer {responsable_token}"}
    response = client.get("/api/v1/interventions/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_intervention_statut(client, technicien_token, responsable_token, equipement):
    # Créer une intervention via responsable
    headers_resp = {"Authorization": f"Bearer {responsable_token}"}
    payload = {
        "titre": "Statut Update",
        "description": "Maj statut",
        "type": "corrective",
        "statut": "ouverte",
        "urgence": False,
        "equipement_id": equipement["id"]
    }
    create_resp = client.post("/api/v1/interventions/", json=payload, headers=headers_resp)
    assert create_resp.status_code == 200
    interv_id = create_resp.json()["id"]

    # Changer le statut via technicien (RBAC)
    headers_tech = {"Authorization": f"Bearer {technicien_token}"}
    response = client.patch(
        f"/api/v1/interventions/{interv_id}/statut",
        params={"statut": "en_cours", "remarque": "Passage en cours"},
        headers=headers_tech
    )
    assert response.status_code == 200
    assert response.json()["statut"] == "en_cours"
