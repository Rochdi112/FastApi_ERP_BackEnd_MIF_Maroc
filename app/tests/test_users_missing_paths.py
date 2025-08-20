import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_users_crud_and_me_and_update(client: TestClient):
    # Admin token for admin-protected endpoints (use email in sub to avoid DB id collision)
    admin_token = create_access_token({"sub": "admin@test.com", "email": "admin@test.com", "role": "admin"})

    # 1) POST /api/v1/users/ (admin required)
    new_user_payload = {
        "username": "jdoe",
        "full_name": "John Doe",
        "email": "jdoe@example.com",
        "role": "client",
        "password": "secret123",
    }
    r = client.post("/api/v1/users/", json=new_user_payload, headers=_auth_header(admin_token))
    assert r.status_code == 201, r.text
    created = r.json()
    user_id = created["id"]
    assert created["email"] == "jdoe@example.com"
    assert created["is_active"] is True

    # 2) GET /api/v1/users/{id}
    r = client.get(f"/api/v1/users/{user_id}", headers=_auth_header(admin_token))
    assert r.status_code == 200
    assert r.json()["id"] == user_id

    # 3) GET /api/v1/users/me (with the user's own token)
    user_token = create_access_token({"sub": created["email"], "email": created["email"], "role": created["role"]})
    r = client.get("/api/v1/users/me", headers=_auth_header(user_token))
    assert r.status_code == 200
    assert r.json()["email"] == created["email"]

    # 4) PUT /api/v1/users/update (self-update full_name/password)
    update_payload = {"full_name": "John X. Doe", "password": "newpass"}
    r = client.put("/api/v1/users/update", json=update_payload, headers=_auth_header(user_token))
    assert r.status_code == 200
    assert r.json()["full_name"] == "John X. Doe"

    # 5) DELETE /api/v1/users/{id} (soft disable)
    r = client.delete(f"/api/v1/users/{user_id}", headers=_auth_header(admin_token))
    assert r.status_code == 204

    # 6) PATCH /api/v1/users/{id}/activate
    r = client.patch(f"/api/v1/users/{user_id}/activate", headers=_auth_header(admin_token))
    assert r.status_code == 200
    assert r.json()["is_active"] is True


def test_users_get_missing_404(client: TestClient):
    admin_token = create_access_token({"sub": "admin@test.com", "email": "admin@test.com", "role": "admin"})
    r = client.get("/api/v1/users/999999", headers=_auth_header(admin_token))
    assert r.status_code == 404
