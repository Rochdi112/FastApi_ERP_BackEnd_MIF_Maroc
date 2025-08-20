from app.models.user import User, UserRole
from app.models.equipement import Equipement
from app.core.security import get_password_hash, create_access_token


def _headers_for(role: str, email: str):
    token = create_access_token({"sub": email, "role": role})
    return {"Authorization": f"Bearer {token}"}


def test_patch_status_422_then_ok(client, db_session):
    # responsable creates intervention
    resp_h = _headers_for("responsable", "resp@example.com")
    tech_h = _headers_for("technicien", "tech@example.com")

    # Ensure equipement exists
    eq = db_session.query(Equipement).first()
    if not eq:
        eq = Equipement(nom="EQ1", type="machine", localisation="Site A")
        db_session.add(eq)
        db_session.commit()
        db_session.refresh(eq)

    new = {"titre":"X","type":"corrective","equipement_id": eq.id}
    c = client.post("/api/v1/interventions/", json=new, headers=resp_h)
    assert c.status_code in (200,201), c.text
    itv_id = c.json()["id"]

    r1 = client.patch(f"/api/v1/interventions/{itv_id}/statut", headers=tech_h)
    assert r1.status_code == 422
    r2 = client.patch(f"/api/v1/interventions/{itv_id}/statut", params={"statut":"en_cours","remarque":"ok"}, headers=tech_h)
    assert r2.status_code == 200


def test_filters_combo_pagination(client):
    admin_h = _headers_for("admin", "admin@example.com")
    q = client.get("/api/v1/filters/interventions", params={"statut":"en_cours","type":"corrective","limit":5,"offset":0}, headers=admin_h)
    assert q.status_code == 200 and isinstance(q.json(), list)
