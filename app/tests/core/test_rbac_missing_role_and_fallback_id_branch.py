import importlib
from fastapi import HTTPException
from types import SimpleNamespace


def test_get_current_user_missing_role_raises(monkeypatch):
    rbac = importlib.import_module("app.core.rbac")

    # Monkeypatch decode_token to return payload without role
    monkeypatch.setattr(rbac, "decode_token", lambda t: {"sub": "x@y.z"}, raising=True)

    with rbac.get_db.override(lambda: iter(())) if hasattr(rbac.get_db, 'override') else monkeypatch.context() as ctx:
        try:
            rbac.get_current_user(token="t", db=None)
            assert False, "Expected HTTPException"
        except HTTPException as e:
            assert e.status_code == 403
            assert "Rôle manquant" in e.detail


def test_get_current_user_fallback_id_digit_sub(monkeypatch):
    rbac = importlib.import_module("app.core.rbac")

    # Payload with numeric sub should set fallback_id
    monkeypatch.setattr(rbac, "decode_token", lambda t: {"sub": "123", "role": "admin"}, raising=True)

    user = rbac.get_current_user(token="t", db=None)
    assert user["user_id"] == 123
    assert user["role"] == "admin"
