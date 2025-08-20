from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole

client = TestClient(app)


def test_notifications_list_no_params():
    db = next(get_db())
    admin = db.query(User).filter(User.email == "notif_list_admin@example.com").first()
    if not admin:
        admin = User(username="na", email="notif_list_admin@example.com", hashed_password=get_password_hash("a"), role=UserRole.admin, is_active=True)
        db.add(admin); db.commit()
    r = client.post("/api/v1/auth/token", data={"email": "notif_list_admin@example.com", "password": "a"})
    assert r.status_code == 200
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    q = client.get("/api/v1/notifications", headers=h)
    assert q.status_code == 200 and isinstance(q.json(), list)
