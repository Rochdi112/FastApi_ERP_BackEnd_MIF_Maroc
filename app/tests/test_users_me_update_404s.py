from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_users_me_404_when_email_missing_from_token():
    token = create_access_token({"sub": "123", "role": "client"})
    r = client.get("/api/v1/users/me", headers=_auth_header(token))
    assert r.status_code == 404


def test_users_update_404_when_email_missing_from_token():
    token = create_access_token({"sub": "123", "role": "client"})
    r = client.put("/api/v1/users/update", json={"full_name": "x"}, headers=_auth_header(token))
    assert r.status_code == 404


def test_users_me_404_when_email_not_found_in_db():
    token = create_access_token({"sub": "ghost@example.com", "email": "ghost@example.com", "role": "client"})
    r = client.get("/api/v1/users/me", headers=_auth_header(token))
    assert r.status_code == 404


def test_users_update_404_when_email_not_found_in_db():
    token = create_access_token({"sub": "ghost@example.com", "email": "ghost@example.com", "role": "client"})
    r = client.put("/api/v1/users/update", json={"full_name": "y"}, headers=_auth_header(token))
    assert r.status_code == 404
