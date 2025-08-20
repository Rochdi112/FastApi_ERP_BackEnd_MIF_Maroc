import pytest
from app.main import app
from app.models.equipement import Equipement
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.api.v1 import interventions as interventions_router


def _override(dep_map: dict):
    app.dependency_overrides.update(dep_map)


def _clear_overrides(keys):
    for k in keys:
        app.dependency_overrides.pop(k, None)


@pytest.mark.usefixtures("client", "db_session")
def test_create_intervention_branch_user_id_present(client, db_session):
    # Ensure an equipement exists
    eq = db_session.query(Equipement).first()
    if not eq:
        eq = Equipement(nom="B1", type="machine", localisation="Z")
        db_session.add(eq)
        db_session.commit()
        db_session.refresh(eq)

    # Create a real user; we will pass its id via overridden current_user
    u = db_session.query(User).filter(User.email == "branch_resp@example.com").first()
    if not u:
        u = User(
            username="br",
            full_name="Branch Resp",
            email="branch_resp@example.com",
            hashed_password=get_password_hash("x"),
            role=UserRole.responsable,
            is_active=True,
        )
        db_session.add(u)
        db_session.commit()
        db_session.refresh(u)

    # Override RBAC and current user to hit the branch where user_id is already present
    deps = {
        interventions_router.responsable_required: lambda: None,
        interventions_router.get_current_user: lambda: {
            "user_id": u.id,
            "email": None,
            "role": "responsable",
            "is_active": True,
        },
    }
    _override(deps)
    try:
        payload = {"titre": "b", "type": "corrective", "equipement_id": eq.id}
        r = client.post("/api/v1/interventions/", json=payload)
        assert r.status_code in (200, 201), r.text
    finally:
        _clear_overrides(list(deps.keys()))


@pytest.mark.usefixtures("client", "db_session")
def test_patch_statut_branch_user_id_present(client, db_session):
    # Ensure an equipement exists
    eq = db_session.query(Equipement).first()
    if not eq:
        eq = Equipement(nom="B2", type="machine", localisation="Z")
        db_session.add(eq)
        db_session.commit()
        db_session.refresh(eq)

    # Ensure a real responsable user exists for creation
    u = db_session.query(User).filter(User.email == "branch_resp2@example.com").first()
    if not u:
        u = User(
            username="br2",
            full_name="Branch Resp2",
            email="branch_resp2@example.com",
            hashed_password=get_password_hash("x"),
            role=UserRole.responsable,
            is_active=True,
        )
        db_session.add(u)
        db_session.commit()
        db_session.refresh(u)

    # Create an intervention with responsable bypass
    deps_create = {
        interventions_router.responsable_required: lambda: None,
        interventions_router.get_current_user: lambda: {
            "user_id": u.id,
            "email": None,
            "role": "responsable",
            "is_active": True,
        },
    }
    _override(deps_create)
    try:
        new_payload = {"titre": "c", "type": "corrective", "equipement_id": eq.id}
        c = client.post("/api/v1/interventions/", json=new_payload)
        assert c.status_code in (200, 201), c.text
        iid = c.json()["id"]
    finally:
        _clear_overrides(list(deps_create.keys()))

    # Create a technicien user for the patch path
    t = db_session.query(User).filter(User.email == "branch_tech@example.com").first()
    if not t:
        t = User(
            username="bt",
            full_name="Branch Tech",
            email="branch_tech@example.com",
            hashed_password=get_password_hash("x"),
            role=UserRole.technicien,
            is_active=True,
        )
        db_session.add(t)
        db_session.commit()
        db_session.refresh(t)

    # Patch statut with technicien bypass and user_id present path
    deps_patch = {
        interventions_router.technicien_required: lambda: None,
        interventions_router.get_current_user: lambda: {
            "user_id": t.id,
            "email": None,
            "role": "technicien",
            "is_active": True,
        },
    }
    _override(deps_patch)
    try:
        r1 = client.patch(f"/api/v1/interventions/{iid}/statut", params={"statut": "en_cours", "remarque": "go"})
        assert r1.status_code == 200, r1.text
    finally:
        _clear_overrides(list(deps_patch.keys()))
