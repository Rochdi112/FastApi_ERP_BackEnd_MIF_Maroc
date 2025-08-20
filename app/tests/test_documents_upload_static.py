import io
from app.models.user import User, UserRole
from app.models.intervention import Intervention
from app.core.security import get_password_hash


def _admin_headers(client, db_session):
    admin = db_session.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            username="admin",
            full_name="Admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            role=UserRole.admin,
            is_active=True,
        )
        db_session.add(admin)
        db_session.commit()
    r = client.post("/api/v1/auth/token", data={"email": "admin@example.com", "password": "admin"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_upload_and_serve_static(client, db_session):
    headers = _admin_headers(client, db_session)
    # Ensure minimal intervention exists
    intr = db_session.query(Intervention).first()
    if not intr:
        intr = Intervention(titre="doc test", type_intervention="corrective", statut="ouverte", urgence=False)
        db_session.add(intr)
        db_session.commit()
        db_session.refresh(intr)
    f = {"file": ("x.txt", io.BytesIO(b"hello"), "text/plain")}
    r = client.post("/api/v1/documents/upload", params={"intervention_id": intr.id}, files=f, headers=headers)
    assert r.status_code in (200,201), r.text
    path = r.json().get("path")
    s = client.get("/"+path)
    assert s.status_code == 200
