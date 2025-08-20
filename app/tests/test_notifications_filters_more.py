from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_password_hash
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.notification import Notification

client = TestClient(app)


def _admin_headers():
    db = next(get_db())
    admin = db.query(User).filter(User.email == "nf_admin@example.com").first()
    if not admin:
        admin = User(
            username="nf_admin",
            full_name="Admin",
            email="nf_admin@example.com",
            hashed_password=get_password_hash("admin"),
            role=UserRole.admin,
            is_active=True,
        )
        db.add(admin)
        db.commit()
    r = client.post("/api/v1/auth/token", data={"email": "nf_admin@example.com", "password": "admin"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_notifications_filter_by_intervention_and_user():
    headers = _admin_headers()
    db = next(get_db())
    n = db.query(Notification).first()
    if not n:
        # Create minimal related rows indirectly via service route
        from app.models.intervention import Intervention
        intr = db.query(Intervention).first()
        if not intr:
            intr = Intervention(titre="n", type="corrective", statut="ouverte", urgence=False)
            db.add(intr); db.commit(); db.refresh(intr)
        user = db.query(User).first()
        payload = {"type": "info", "canal": "email", "contenu": "x", "user_id": user.id, "intervention_id": intr.id}
        r = client.post("/api/v1/notifications/", json=payload, headers=headers)
        assert r.status_code in (200,201)
        n = r.json()
    q = client.get("/api/v1/notifications", params={"user_id": n["user_id"], "intervention_id": n["intervention_id"]}, headers=headers)
    assert q.status_code == 200
    assert isinstance(q.json(), list)
