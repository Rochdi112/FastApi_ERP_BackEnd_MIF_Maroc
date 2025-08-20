from fastapi import status
from app.core.security import create_access_token


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


essential_payload = {
    "titre": "NumID",
    "description": "",
    "type": "corrective",
    "statut": "ouverte",
    "priorite": "normale",
    "urgence": False,
    "date_limite": None,
}


def _ensure_equipement(db):
    from app.models.equipement import Equipement
    e = db.query(Equipement).first()
    if not e:
        e = Equipement(nom="E1", type="t", localisation="l", frequence_maintenance="mensuelle")
        db.add(e)
        db.commit()
        db.refresh(e)
    return e


def test_create_intervention_with_numeric_user_id_in_token(client, db_session):
    e = _ensure_equipement(db_session)
    token = create_access_token({"sub": "123", "role": "responsable"})
    payload = dict(essential_payload)
    payload["equipement_id"] = e.id
    r = client.post("/api/v1/interventions/", json=payload, headers=_auth(token))
    assert r.status_code == status.HTTP_200_OK, r.text


def test_change_statut_with_numeric_user_id_in_token(client, db_session):
    # Create first
    e = _ensure_equipement(db_session)
    # Use an email sub so the route ensures a user (avoid 404 user not found)
    token = create_access_token({"sub": "tech456@example.com", "role": "technicien"})
    payload = dict(essential_payload)
    payload["equipement_id"] = e.id
    create_r = client.post("/api/v1/interventions/", json=payload, headers=_auth(create_access_token({"sub": "resp@x", "role": "responsable"})))
    assert create_r.status_code == status.HTTP_200_OK
    iid = create_r.json()["id"]

    # Change statut (technicien required dep is satisfied by role)
    r = client.patch(
        f"/api/v1/interventions/{iid}/statut",
        params={"statut": "en_cours", "remarque": "go"},
        headers=_auth(token),
    )
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["statut"] in ("en_cours", "ouverte")
