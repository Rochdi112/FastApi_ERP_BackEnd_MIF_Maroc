from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash

client = TestClient(app)


def _login(email, password):
    r = client.post("/auth/token", data={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_users_list_forbidden_for_non_admin():
    # Seed a technicien if missing
    db = next(get_db())
    user = db.query(User).filter(User.email == "technicien@example.com").first()
    if not user:
        user = User(
            username="technicien",
            full_name="Tech",
            email="technicien@example.com",
            hashed_password=get_password_hash("password"),
            role=UserRole.technicien,
            is_active=True,
        )
        db.add(user)
        db.commit()
    headers = _login("technicien@example.com", "password")
    r = client.get("/users/", headers=headers)
    assert r.status_code == 403
