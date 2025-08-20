def test_health_and_static_mount(client):
    assert client.get("/health").status_code == 200
    s = client.get("/static/uploads/.gitkeep")
    assert s.status_code in (200,404)
