from datetime import timedelta
import pytest
from jose import JWTError
from app.core.security import get_password_hash, verify_password, create_access_token, verify_token


def test_password_hash_and_verify_true_false():
    pwd = "s3cr3t!"
    hashed = get_password_hash(pwd)
    assert hashed and hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_access_token_exp_and_verify_payload():
    token = create_access_token({"sub": "42", "email": "u@x.com", "role": "admin"}, expires_delta=timedelta(seconds=1))
    payload = verify_token(token)
    assert payload["sub"] == "42"
    assert payload["email"] == "u@x.com"
    assert payload["role"] == "admin"


def test_verify_token_invalid_raises_http_exc():
    with pytest.raises(Exception):
        # deliberately malformed token
        verify_token("invalid.token.value")
