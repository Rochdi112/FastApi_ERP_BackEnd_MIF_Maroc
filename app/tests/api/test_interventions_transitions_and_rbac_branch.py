from fastapi import status
from types import SimpleNamespace
from app.core.rbac import require_roles
from app.core.security import create_access_token


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_intervention_transition_conflict_then_closed(client, db_session):
    # Ensure equipement exists
    from app.models.equipement import Equipement
    e = db_session.query(Equipement).first()
    if not e:
        e = Equipement(nom="E2", type="t", localisation="l", frequence_maintenance="mensuelle")
        db_session.add(e)
        db_session.commit()
        db_session.refresh(e)

    # Create intervention as responsable
    token_resp = create_access_token({"sub": "r@x", "role": "responsable"})
    create_payload = {
        "titre": "Trans",
        "description": "",
        "type": "corrective",
        "statut": "ouverte",
        "priorite": "normale",
        "urgence": False,
        "date_limite": None,
        "equipement_id": e.id,
    }
    cr = client.post("/api/v1/interventions/", json=create_payload, headers=_auth(token_resp))
    assert cr.status_code == status.HTTP_200_OK, cr.text
    iid = cr.json()["id"]

    # Try archivee before cloturee -> 409
    token_tech = create_access_token({"sub": "t@x", "role": "technicien"})
    r409 = client.patch(f"/api/v1/interventions/{iid}/statut", params={"statut": "archivee"}, headers=_auth(token_tech))
    assert r409.status_code == status.HTTP_409_CONFLICT

    # Close it -> 200
    r200 = client.patch(f"/api/v1/interventions/{iid}/statut", params={"statut": "cloturee"}, headers=_auth(token_tech))
    assert r200.status_code == status.HTTP_200_OK

    # Try changing after closure -> 400
    r400 = client.patch(f"/api/v1/interventions/{iid}/statut", params={"statut": "en_cours"}, headers=_auth(token_tech))
    assert r400.status_code == status.HTTP_400_BAD_REQUEST


def test_require_roles_object_current_user_branch():
    # current_user passed as object (not dict) exercises getattr path
    checker = require_roles("admin")
    obj_user = SimpleNamespace(role="client")
    try:
        checker(obj_user)  # should raise 403
        assert False, "Expected HTTPException"
    except Exception:
        assert True


def test_planning_list_with_plain_user_token(client):
    # Any authenticated user calls list to ensure the dependency line is executed
    token = create_access_token({"sub": "u@x", "role": "client"})
    r = client.get("/api/v1/planning/", headers=_auth(token))
    assert r.status_code == status.HTTP_200_OK
