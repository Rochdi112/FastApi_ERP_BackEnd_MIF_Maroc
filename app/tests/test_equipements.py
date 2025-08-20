import pytest

@pytest.fixture()
def equipement_payload():
    return {
        "nom": "Pompe 3000",
        "type": "Pompe",
        "localisation": "Usine A",
        "frequence_entretien": "30"
    }

def test_create_equipement(client, responsable_token, equipement_payload):
    headers = {"Authorization": f"Bearer {responsable_token}"}
    response = client.post(
        "/api/v1/equipements/",
        json=equipement_payload,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nom"] == equipement_payload["nom"]
    assert data["frequence_entretien"] == equipement_payload["frequence_entretien"]
    client.delete(f"/api/v1/equipements/{data['id']}", headers=headers)

def test_get_equipement_by_id(client, responsable_token, equipement_payload):
    headers = {"Authorization": f"Bearer {responsable_token}"}
    create_resp = client.post(
        "/api/v1/equipements/",
        json=equipement_payload,
        headers=headers
    )
    assert create_resp.status_code == 200
    eq_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/equipements/{eq_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == eq_id
    client.delete(f"/api/v1/equipements/{eq_id}", headers=headers)

def test_get_all_equipements(client, responsable_token, equipement_payload):
    headers = {"Authorization": f"Bearer {responsable_token}"}
    create_resp = client.post(
        "/api/v1/equipements/",
        json=equipement_payload,
        headers=headers
    )
    assert create_resp.status_code == 200
    eq_id = create_resp.json()["id"]
    response = client.get("/api/v1/equipements/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert any(eq["id"] == eq_id for eq in data)
    client.delete(f"/api/v1/equipements/{eq_id}", headers=headers)

def test_delete_equipement_independant(client, responsable_token):
    headers = {"Authorization": f"Bearer {responsable_token}"}
    payload = {
        "nom": "À Supprimer",
        "type": "Filtre",
        "localisation": "Stock",
        "frequence_entretien": "10"
    }
    create_resp = client.post(
        "/api/v1/equipements/",
        json=payload,
        headers=headers
    )
    assert create_resp.status_code == 200
    eq_id = create_resp.json()["id"]
    delete_resp = client.delete(f"/api/v1/equipements/{eq_id}", headers=headers)
    assert delete_resp.status_code == 200
