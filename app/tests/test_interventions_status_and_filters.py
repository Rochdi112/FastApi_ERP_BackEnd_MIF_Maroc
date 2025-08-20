import pytest
from app.models.user import User, UserRole
from app.models.equipement import Equipement
from app.core.security import get_password_hash


def _login_admin(client, db_session):
    admin = db_session.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            username="admin",
            full_name="Admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            role=UserRole.admin,
            is_active=True,
        )
        db_session.add(admin)
        db_session.commit()
    r = client.post("/auth/token", data={"email": "admin@example.com", "password": "admin"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _login_responsable(client, db_session):
    user = db_session.query(User).filter(User.email == "resp@example.com").first()
    if not user:
        user = User(
            username="resp",
            full_name="Responsable",
            email="resp@example.com",
            hashed_password=get_password_hash("resp"),
            role=UserRole.responsable,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
    r = client.post("/auth/token", data={"email": "resp@example.com", "password": "resp"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _login_technicien(client, db_session):
    user = db_session.query(User).filter(User.email == "tech@example.com").first()
    if not user:
        user = User(
            username="tech",
            full_name="Technicien",
            email="tech@example.com",
            hashed_password=get_password_hash("tech"),
            role=UserRole.technicien,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
    r = client.post("/auth/token", data={"email": "tech@example.com", "password": "tech"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.usefixtures("client", "db_session")
def test_patch_status_requires_query_then_ok(client, db_session):
    resp_headers = _login_responsable(client, db_session)
    tech_headers = _login_technicien(client, db_session)
    # Ensure equipement exists
    eq = db_session.query(Equipement).first()
    if not eq:
        eq = Equipement(nom="EQ1", type="machine", localisation="Site A")
        db_session.add(eq)
        db_session.commit()
        db_session.refresh(eq)
    new = {
        "titre": "X",
        "type": "corrective",
        "equipement_id": eq.id,
    }
    c = client.post("/interventions/", json=new, headers=resp_headers)
    assert c.status_code in (200, 201), c.text
    iid = c.json()["id"]
    r1 = client.patch(f"/interventions/{iid}/statut", headers=tech_headers)
    assert r1.status_code == 422
    r2 = client.patch(
        f"/interventions/{iid}/statut",
        params={"statut": "en_cours", "remarque": "go"},
        headers=tech_headers,
    )
    assert r2.status_code == 200


@pytest.mark.usefixtures("client", "db_session")
def test_filters_combinations(client, db_session):
    headers = _login_admin(client, db_session)
    q = client.get(
        "/api/v1/filters/interventions",
        params={"statut": "en_cours", "type": "corrective", "limit": 5, "offset": 0},
        headers=headers,
    )
    assert q.status_code == 200 and isinstance(q.json(), list)
