import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token


def _auth(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_user_service_duplicate_email_conflict(client: TestClient):
    admin = create_access_token({"sub": "admin@test.com", "email": "admin@test.com", "role": "admin"})

    payload = {
        "username": "dup1",
        "full_name": "Dup One",
        "email": "dup@example.com",
        "role": "client",
        "password": "a",
    }
    r1 = client.post("/api/v1/users/", json=payload, headers=_auth(admin))
    assert r1.status_code == 201

    # duplicate email
    payload2 = {
        "username": "dup2",
        "full_name": "Dup Two",
        "email": "dup@example.com",
        "role": "client",
        "password": "a",
    }
    r2 = client.post("/api/v1/users/", json=payload2, headers=_auth(admin))
    assert r2.status_code == 409


def test_user_service_update_ok(client: TestClient):
    admin = create_access_token({"sub": "admin@test.com", "email": "admin@test.com", "role": "admin"})

    payload = {
        "username": "up1",
        "full_name": "Up One",
        "email": "up1@example.com",
        "role": "client",
        "password": "a",
    }
    r = client.post("/api/v1/users/", json=payload, headers=_auth(admin))
    assert r.status_code == 201
    user = r.json()

    # self update via PUT /update (uses service update_user)
    token = create_access_token({"sub": str(user["id"]), "email": user["email"], "role": user["role"]})
    resp = client.put("/api/v1/users/update", json={"full_name": "Up One Edited"}, headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Up One Edited"
