import pytest
from app.models.user import User, UserRole
from app.models.intervention import Intervention
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


@pytest.mark.usefixtures("client", "db_session")
def test_notifications_filter_and_delete_404(client, db_session):
    headers = _login_admin(client, db_session)
    intr = db_session.query(Intervention).first()
    if not intr:
        intr = Intervention(titre="notif test", type="corrective", statut="ouverte", urgence=False)
        db_session.add(intr)
        db_session.commit()
        db_session.refresh(intr)
    payload = {
        "type": "information",
        "canal": "email",
        "contenu": "m",
        "user_id": db_session.query(User).first().id,
        "intervention_id": intr.id,
    }
    r = client.post("/notifications/", json=payload, headers=headers)
    assert r.status_code in (200, 201), r.text
    notif = r.json()
    q = client.get(
        "/notifications",
        params={"user_id": payload["user_id"], "limit": 1, "offset": 0},
        headers=headers,
    )
    assert q.status_code == 200 and isinstance(q.json(), list)
    d1 = client.delete(f"/notifications/{notif['id']}", headers=headers)
    assert d1.status_code in (200, 204)
    d2 = client.delete(f"/notifications/{notif['id']}", headers=headers)
    assert d2.status_code == 404
