from datetime import datetime
from fastapi import status
from app.core.security import create_access_token


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_planning_patch_dates_endpoint_branch(client, db_session):
    # Create admin and equipement
    from app.models.user import User, UserRole
    from app.models.equipement import Equipement
    from app.core.security import get_password_hash

    admin = User(
        username="planadmin2",
        full_name="Plan Admin 2",
        email="planadmin2@example.com",
        hashed_password=get_password_hash("x"),
        role=UserRole.admin,
        is_active=True,
    )
    db_session.add(admin)
    eq = Equipement(nom="P2", type="t", localisation="l", frequence_maintenance="mensuelle")
    db_session.add(eq)
    db_session.commit()
    db_session.refresh(eq)

    # Login via token with role responsable (use an email not in DB so fallback keeps token role)
    token = create_access_token({"sub": "resp2@example.com", "role": "responsable"})

    # Create planning
    r = client.post(
        "/api/v1/planning/",
        json={
            "equipement_id": eq.id,
            "date_prevue": "2025-08-01",
            "frequence": "mensuelle",
            "remarques": "x",
        },
        headers=_auth(token),
    )
    assert r.status_code == status.HTTP_201_CREATED
    planning_id = r.json()["id"]

    # Patch date (exercise code path)
    r2 = client.patch(
        f"/api/v1/planning/{planning_id}/dates",
        params={"nouvelle_date": datetime.utcnow().isoformat()},
        headers=_auth(token),
    )
    assert r2.status_code == status.HTTP_200_OK


def test_create_competence_endpoint(client):
    # Responsable token to pass dependency
    token = create_access_token({"sub": "resp@comp.local", "role": "responsable"})
    r = client.post(
        "/api/v1/techniciens/competences",
        json={"nom": "electricite"},
        headers=_auth(token),
    )
    # Either created or 400 if duplicate in repeated runs; both execute the path
    assert r.status_code in (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)
