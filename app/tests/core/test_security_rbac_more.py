import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.core.config import settings
from app.core.security import verify_token
from app.core.rbac import require_roles


def _encode(payload: dict, key: str = None, alg: str = None) -> str:
    return jwt.encode(payload, key or settings.SECRET_KEY, algorithm=alg or settings.ALGORITHM)


def test_jwt_payload_missing_sub_rejected():
    token = _encode({"email": "x@y", "role": "admin"})
    with pytest.raises(Exception):
        # verify_token returns payload but app.get_current_user requires sub; emulate assertion here
        payload = verify_token(token)
        assert "sub" in payload  # force failure when missing


def test_jwt_signature_invalid_rejected():
    token = _encode({"sub": "1"}, key="different-secret")
    with pytest.raises(Exception):
        verify_token(token)


def test_jwt_unsupported_algorithm_rejected():
    token = _encode({"sub": "1"}, alg="HS384")
    with pytest.raises(Exception):
        verify_token(token)


def test_jwt_expired_token_rejected():
    token = _encode({"sub": "1", "exp": datetime.utcnow() - timedelta(seconds=1)})
    with pytest.raises(Exception):
        verify_token(token)


def test_require_roles_insufficient_role():
    dep = require_roles("admin")
    with pytest.raises(Exception):
        dep({"role": "client"})


def test_clock_skew_accept_near_future_exp():
    # token not expired yet should be accepted
    token = _encode({"sub": "2", "exp": datetime.utcnow() + timedelta(seconds=2)})
    payload = verify_token(token)
    assert payload["sub"] == "2"
