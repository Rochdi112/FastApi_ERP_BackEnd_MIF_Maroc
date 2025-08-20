import io
from fastapi import status

from app.models.intervention import (
    Intervention,
    StatutIntervention,
    InterventionType,
    PrioriteIntervention,
)


def test_documents_upload_alias_success(client, db_session, auth_headers, tmp_path):
    # Create minimal intervention
    inter = Intervention(
        titre="Test",
        description="Desc",
        type_intervention=InterventionType.corrective,
        statut=StatutIntervention.ouverte,
    priorite=PrioriteIntervention.normale,
        urgence=False,
        technicien_id=None,
        equipement_id=None,
    )
    db_session.add(inter)
    db_session.commit()

    files = {"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")}
    r = client.post(f"/api/v1/documents/upload?intervention_id={inter.id}", headers=auth_headers, files=files)
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    assert data["path"].startswith("static/uploads/")
    assert data["filename"] == "test.txt"


def test_documents_upload_alias_404_when_intervention_missing(client, auth_headers):
    files = {"file": ("x.txt", io.BytesIO(b"hi"), "text/plain")}
    r = client.post("/api/v1/documents/upload?intervention_id=9999", headers=auth_headers, files=files)
    assert r.status_code == status.HTTP_404_NOT_FOUND
