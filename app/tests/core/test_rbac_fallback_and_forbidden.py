import pytest
from fastapi import HTTPException
from app.core.rbac import require_roles


def test_require_roles_forbidden_message_contains_roles():
    dep = require_roles("admin", "responsable")
    with pytest.raises(HTTPException) as exc:
        dep({"role": "client"})
    assert exc.value.status_code == 403
    assert "admin" in exc.value.detail and "responsable" in exc.value.detail
