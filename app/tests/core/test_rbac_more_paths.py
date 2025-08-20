import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient
from app.main import app
from app.core.rbac import require_roles
from app.core.security import create_access_token, get_password_hash
from app.db.database import get_db
from app.models.user import User, UserRole

client = TestClient(app)


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_require_roles_accepts_object():
    dep = require_roles("admin")
    obj = SimpleNamespace(role="admin")
    assert dep(obj) is obj


def test_filters_invalid_token_raises_403():
    r = client.get("/api/v1/filters/interventions", headers=_auth("invalid"))
    assert r.status_code == 403


def test_filters_role_missing_in_token_raises_403():
    token = create_access_token({"sub": "x@y", "email": "x@y"})
    r = client.get("/api/v1/filters/interventions", headers=_auth(token))
    assert r.status_code == 403


def test_interventions_forbidden_when_user_inactive():
    db = next(get_db())
    u = db.query(User).filter(User.email == "inactive_rbac@example.com").first()
    if not u:
        u = User(
            username="inactive_rbac",
            full_name="Inactive RBAC",
            email="inactive_rbac@example.com",
            hashed_password=get_password_hash("x"),
            role=UserRole.client,
            is_active=False,
        )
        db.add(u); db.commit()
    token = create_access_token({"sub": u.email, "email": u.email, "role": "client"})
    r = client.get("/api/v1/interventions/", headers=_auth(token))
    assert r.status_code == 403


def test_interventions_with_numeric_sub_fallback_succeeds():
    # No user with id 424242, fallback path should still auth with role
    token = create_access_token({"sub": "424242", "role": "client"})
    r = client.get("/api/v1/interventions/", headers=_auth(token))
    assert r.status_code == 200
