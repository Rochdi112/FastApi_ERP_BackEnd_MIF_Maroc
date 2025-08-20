import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token


def _auth(token: str):
    return {"Authorization": f"Bearer {token}"}


def _seed_equipement(client: TestClient, token: str) -> int:
    eq_payload = {"nom": "Pump A", "type": "pompe", "localisation": "A1", "frequence_entretien": "15"}
    r = client.post("/api/v1/equipements/", json=eq_payload, headers=_auth(token))
    assert r.status_code in (200, 201, 400)  # some implementations return 200 on upsert
    if r.status_code == 201:
        return r.json()["id"]
    # fetch list and find id
    lr = client.get("/api/v1/equipements")
    assert lr.status_code == 200
    eq = next((e for e in lr.json() if e["nom"] == "Pump A"), None)
    assert eq
    return eq["id"]


def test_intervention_statut_transitions_and_refus(client: TestClient):
    resp_token = create_access_token({"sub": "resp@test.com", "email": "resp@test.com", "role": "responsable"})
    tech_token = create_access_token({"sub": "tech@test.com", "email": "tech@test.com", "role": "technicien"})

    eq_id = _seed_equipement(client, resp_token)

    # create intervention as responsable
    payload = {
        "titre": "Leak",
        "description": "Minor leak",
        "type": "corrective",
        "statut": "ouverte",
        "priorite": "normale",
        "urgence": False,
        "technicien_id": None,
        "equipement_id": eq_id,
    }
    r = client.post("/api/v1/interventions/", json=payload, headers=_auth(resp_token))
    assert r.status_code in (200, 201), r.text
    inter = r.json()
    iid = inter["id"]

    # valid transition by technicien
    r1 = client.patch(f"/api/v1/interventions/{iid}/statut", params={"statut": "en_cours"}, headers=_auth(tech_token))
    assert r1.status_code == 200

    # refuse update when already cloturee
    r2 = client.patch(f"/api/v1/interventions/{iid}/statut", params={"statut": "cloturee"}, headers=_auth(tech_token))
    assert r2.status_code == 200
    r3 = client.patch(f"/api/v1/interventions/{iid}/statut", params={"statut": "en_attente"}, headers=_auth(tech_token))
    assert r3.status_code == 400


def test_intervention_create_with_missing_technicien_404(client: TestClient):
    resp_token = create_access_token({"sub": "12", "email": "resp2@test.com", "role": "responsable"})
    eq_id = _seed_equipement(client, resp_token)

    payload = {
        "titre": "Test",
        "description": None,
        "type": "corrective",
        "statut": "ouverte",
        "priorite": "normale",
        "urgence": False,
        "technicien_id": 999999,
        "equipement_id": eq_id,
    }
    r = client.post("/api/v1/interventions/", json=payload, headers=_auth(resp_token))
    assert r.status_code == 404
