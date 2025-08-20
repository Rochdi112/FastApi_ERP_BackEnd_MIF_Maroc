import importlib
import pytest
from fastapi import HTTPException


def test_get_current_user_inactive_user_raises(monkeypatch, db_session):
    rbac = importlib.import_module("app.core.rbac")
    from app.models.user import User, UserRole

    u = User(username="inactive", full_name="Z", email="z@example.com", hashed_password="x", role=UserRole.client, is_active=False)
    db_session.add(u)
    db_session.commit()

    # Forge token payload to resolve by email
    monkeypatch.setattr(rbac, "decode_token", lambda t: {"sub": u.email, "role": u.role.value}, raising=True)

    with pytest.raises(HTTPException) as ei:
        rbac.get_current_user(token="t", db=db_session)
    assert ei.value.status_code == 403
    assert "désactivé" in ei.value.detail
