import pytest
from app.core.rbac import require_roles


def test_require_roles_forbidden():
    dep = require_roles("admin")
    with pytest.raises(Exception):
        dep({"role": "client"})
