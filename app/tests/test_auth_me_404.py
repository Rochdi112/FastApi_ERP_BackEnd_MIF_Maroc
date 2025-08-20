import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token


client = TestClient(app)


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_auth_me_returns_404_when_user_missing():
    token = create_access_token({"sub": "missing@example.com", "email": "missing@example.com", "role": "admin"})
    r = client.get("/api/v1/auth/me", headers=_auth_header(token))
    assert r.status_code == 404
