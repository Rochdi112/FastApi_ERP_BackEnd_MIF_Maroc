from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)


def _h(tok: str) -> dict:
    return {"Authorization": f"Bearer {tok}"}


def test_auth_with_numeric_user_id_payload_fallback_ok():
    token = create_access_token({"user_id": 123, "role": "client"})
    r = client.get("/api/v1/interventions/", headers=_h(token))
    assert r.status_code == 200


def test_auth_with_invalid_user_id_string_still_fallbacks():
    token = create_access_token({"user_id": "abc", "role": "client"})
    r = client.get("/api/v1/interventions/", headers=_h(token))
    assert r.status_code == 200
