import io
from fastapi import status
from app.core.security import create_access_token


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_documents_root_upload_success(client, db_session):
    # Prepare an admin token and a minimal intervention
    from app.models.intervention import Intervention, StatutIntervention, InterventionType, PrioriteIntervention

    inter = Intervention(
        titre="DocRoot",
        description="",
        type_intervention=InterventionType.corrective,
        statut=StatutIntervention.ouverte,
        priorite=PrioriteIntervention.normale,
        urgence=False,
        technicien_id=None,
        equipement_id=None,
    )
    db_session.add(inter)
    db_session.commit()

    token = create_access_token({"sub": "admin@doc.test", "role": "admin"})
    files = {"file": ("root.txt", io.BytesIO(b"abc"), "text/plain")}
    r = client.post(
        f"/documents/?intervention_id={inter.id}",
        headers=_auth(token),
        files=files,
    )
    assert r.status_code == status.HTTP_201_CREATED, r.text
    j = r.json()
    assert j["filename"] == "root.txt"


def test_list_competences_endpoint_hits_branch(client):
    # Ensure the GET /techniciens/competences path is executed
    token = create_access_token({"sub": "admin@comp.test", "role": "admin"})
    r = client.get("/api/v1/techniciens/competences", headers=_auth(token))
    # Even if empty list, path is executed
    assert r.status_code == status.HTTP_200_OK
    assert isinstance(r.json(), list)
