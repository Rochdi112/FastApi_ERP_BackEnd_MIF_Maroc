import pytest
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
from app.core.security import verify_token


def test_verify_token_expired():
    payload = {"sub": "1", "exp": datetime.utcnow() - timedelta(seconds=1)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(Exception):
        verify_token(token)


def test_verify_token_wrong_alg():
    token = jwt.encode({"sub": "1"}, settings.SECRET_KEY, algorithm="HS512")
    with pytest.raises(Exception):
        verify_token(token)
