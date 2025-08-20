# app/tests/test_dummy.py

def test_dummy(client):
    response = client.get("/docs")
    assert response.status_code == 200
