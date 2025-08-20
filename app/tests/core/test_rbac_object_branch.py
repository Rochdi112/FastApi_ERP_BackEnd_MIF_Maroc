import pytest
from types import SimpleNamespace
from fastapi import HTTPException
from app.core.rbac import require_roles


def test_require_roles_with_object_insufficient_role_raises_403():
    dep = require_roles("admin")
    with pytest.raises(HTTPException) as exc:
        dep(SimpleNamespace(role="client"))
    assert exc.value.status_code == 403


def test_require_roles_with_object_allowed_returns_user():
    dep = require_roles("admin", "responsable")
    user = SimpleNamespace(role="responsable")
    assert dep(user) is user
