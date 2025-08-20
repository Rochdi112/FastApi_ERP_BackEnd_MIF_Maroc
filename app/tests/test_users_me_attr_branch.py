from fastapi.testclient import TestClient
from app.main import app
from app.api.v1 import users as users_router
from app.core.security import create_access_token
from types import SimpleNamespace

client = TestClient(app)


def _object_user():
    return SimpleNamespace(email="obj@example.com", role="client", is_active=True)


def test_users_me_with_object_current_user(monkeypatch):
    # Override the get_current_user dependency in users router only
    app.dependency_overrides[users_router.get_current_user] = _object_user
    try:
        # No user in DB with that email, expect 404 branch
        r = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {create_access_token({'sub':'obj@example.com','email':'obj@example.com','role':'client'})}"})
        assert r.status_code == 404
    finally:
        app.dependency_overrides.pop(users_router.get_current_user, None)
