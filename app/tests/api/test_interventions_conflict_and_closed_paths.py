from fastapi import status
from app.core.security import create_access_token


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _ensure_equipement(client, db_session, token) -> int:
    from app.models.equipement import Equipement
    e = db_session.query(Equipement).first()
    if not e:
        e = Equipement(nom="E2", type="t", localisation="l", frequence_maintenance="mensuelle")
        db_session.add(e)
        db_session.commit()
        db_session.refresh(e)
    return e.id


essentials = {
    "titre": "X",
    "description": "",
    "type": "corrective",
    "statut": "ouverte",
    "priorite": "normale",
    "urgence": False,
}


def test_intervention_archive_conflict_then_close_then_archive_ok(client, db_session):
    # Create by responsable
    resp = create_access_token({"sub": "resp3@x", "role": "responsable"})
    tech = create_access_token({"sub": "tech3@x", "role": "technicien"})
    eid = _ensure_equipement(client, db_session, resp)

    create_r = client.post("/api/v1/interventions/", json={**essentials, "equipement_id": eid}, headers=_auth(resp))
    assert create_r.status_code == status.HTTP_200_OK
    iid = create_r.json()["id"]

    # Try archive directly -> 409
    r_conflict = client.patch(
        f"/api/v1/interventions/{iid}/statut",
        params={"statut": "archivee"},
        headers=_auth(tech),
    )
    assert r_conflict.status_code == status.HTTP_409_CONFLICT

    # Close it -> 200
    r_close = client.patch(
        f"/api/v1/interventions/{iid}/statut",
        params={"statut": "cloturee"},
        headers=_auth(tech),
    )
    assert r_close.status_code == status.HTTP_200_OK

    # Archive now -> service forbids any modification after closure -> 400
    r_arch = client.patch(
        f"/api/v1/interventions/{iid}/statut",
        params={"statut": "archivee"},
        headers=_auth(tech),
    )
    assert r_arch.status_code == status.HTTP_400_BAD_REQUEST


def test_intervention_modify_after_closed_raises_400(client, db_session):
    resp = create_access_token({"sub": "resp4@x", "role": "responsable"})
    tech = create_access_token({"sub": "tech4@x", "role": "technicien"})
    eid = _ensure_equipement(client, db_session, resp)

    create_r = client.post("/api/v1/interventions/", json={**essentials, "equipement_id": eid}, headers=_auth(resp))
    assert create_r.status_code == status.HTTP_200_OK
    iid = create_r.json()["id"]

    # Close it
    r_close = client.patch(
        f"/api/v1/interventions/{iid}/statut",
        params={"statut": "cloturee"},
        headers=_auth(tech),
    )
    assert r_close.status_code == status.HTTP_200_OK

    # Try to modify again -> 400
    r_again = client.patch(
        f"/api/v1/interventions/{iid}/statut",
        params={"statut": "en_cours"},
        headers=_auth(tech),
    )
    assert r_again.status_code == status.HTTP_400_BAD_REQUEST
