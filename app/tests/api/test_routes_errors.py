import io
import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token


def _auth(t: str) -> dict:
    return {"Authorization": f"Bearer {t}"}


def test_422_on_create_equipement_invalid_nom(client: TestClient):
    # missing required field 'nom' should trigger 422 validation error
    token = create_access_token({"sub": "resp@test.com", "email": "resp@test.com", "role": "responsable"})
    payload = {"type": "pompe", "localisation": "A", "frequence_entretien": "10"}
    r = client.post("/api/v1/equipements/", json=payload, headers=_auth(token))
    assert r.status_code == 422


def test_intervention_read_missing_404(client: TestClient):
    token = create_access_token({"sub": "u@test.com", "email": "u@test.com", "role": "client"})
    r = client.get("/api/v1/interventions/999999", headers=_auth(token))
    assert r.status_code == 404


def test_delete_equipement_in_use_conflict(client: TestClient):
    resp = create_access_token({"sub": "resp2@test.com", "email": "resp2@test.com", "role": "responsable"})
    tech = create_access_token({"sub": "tech@test.com", "email": "tech@test.com", "role": "technicien"})

    # create equipement
    eq_payload = {"nom": "EQ-InUse", "type": "x", "localisation": "Z", "frequence_entretien": "7"}
    c = client.post("/api/v1/equipements/", json=eq_payload, headers=_auth(resp))
    assert c.status_code in (200, 201)
    eq_id = c.json()["id"]

    # create intervention referencing equipement (responsable)
    it_payload = {
        "titre": "Check",
        "description": None,
        "type": "corrective",
        "statut": "ouverte",
        "priorite": "normale",
        "urgence": False,
        "technicien_id": None,
        "equipement_id": eq_id,
    }
    i = client.post("/api/v1/interventions/", json=it_payload, headers=_auth(resp))
    assert i.status_code in (200, 201), i.text

    # deletion should now be blocked
    d = client.delete(f"/api/v1/equipements/{eq_id}", headers=_auth(resp))
    assert d.status_code in (400, 409)


def test_users_me_accessible_and_consistent(client: TestClient):
    # create user as admin
    admin = create_access_token({"sub": "admin@test.com", "email": "admin@test.com", "role": "admin"})
    payload = {
        "username": "alice",
        "full_name": "Alice",
        "email": "alice@example.com",
        "role": "client",
        "password": "pw",
    }
    r = client.post("/api/v1/users/", json=payload, headers=_auth(admin))
    assert r.status_code == 201, r.text
    u = r.json()

    # call /users/me with user's own token
    tok = create_access_token({"sub": u["email"], "email": u["email"], "role": u["role"]})
    me = client.get("/api/v1/users/me", headers=_auth(tok))
    assert me.status_code == 200
    assert me.json()["email"] == u["email"]
