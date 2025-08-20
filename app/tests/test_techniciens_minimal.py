from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def _headers(role: str, email: str):
    token = create_access_token({"sub": email, "role": role})
    return {"Authorization": f"Bearer {token}"}


def test_list_and_get_techniciens(client, db_session):
    # Seed a responsable and a technicien
    resp = db_session.query(User).filter(User.email=="resp@example.com").first()
    if not resp:
        resp = User(username="resp", full_name="Resp", email="resp@example.com", hashed_password=get_password_hash("resp"), role=UserRole.responsable, is_active=True)
        db_session.add(resp)
    tech_u = db_session.query(User).filter(User.email=="t1@example.com").first()
    if not tech_u:
        tech_u = User(username="t1", full_name="T1", email="t1@example.com", hashed_password=get_password_hash("t1"), role=UserRole.technicien, is_active=True)
        db_session.add(tech_u)
    db_session.commit()

    # create technicien entity via API
    headers = _headers("responsable", "resp@example.com")
    payload = {"user_id": tech_u.id, "equipe":"A", "disponibilite":"Disponible", "competences_ids": []}
    c = client.post("/api/v1/techniciens/", json=payload, headers=headers)
    assert c.status_code == 200, c.text
    t_id = c.json()["id"]

    # list
    r1 = client.get("/api/v1/techniciens/", headers=headers)
    assert r1.status_code == 200 and any(x["id"]==t_id for x in r1.json())
    # get
    r2 = client.get(f"/api/v1/techniciens/{t_id}", headers=headers)
    assert r2.status_code == 200 and r2.json()["id"] == t_id
