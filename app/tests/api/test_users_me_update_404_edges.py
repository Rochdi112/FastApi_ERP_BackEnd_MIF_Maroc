import pytest
from fastapi import status
from app.core.security import create_access_token


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_users_me_404_when_email_missing_in_token(client):
    # Token with explicit user_id and no sub/email -> get_current_user(email=None)
    token = create_access_token({"user_id": 99999, "role": "client"})
    r = client.get("/api/v1/users/me", headers=_auth(token))
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_users_me_404_when_email_unknown_in_db(client):
    # Token with sub as non-email string -> email set to 'unknown', lookup returns None -> 404
    token = create_access_token({"sub": "unknown@example.invalid", "role": "client"})
    r = client.get("/api/v1/users/me", headers=_auth(token))
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_users_update_404_when_email_missing_in_token(client):
    token = create_access_token({"user_id": 424242, "role": "client"})
    r = client.put(
        "/api/v1/users/update",
        json={"full_name": "Nobody"},
        headers=_auth(token),
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_users_update_404_when_email_unknown(client):
    # Email present but not in DB -> branch after lookup
    token = create_access_token({"sub": "ghost@example.invalid", "role": "client"})
    r = client.put(
        "/api/v1/users/update",
        json={"full_name": "Ghost"},
        headers=_auth(token),
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND
