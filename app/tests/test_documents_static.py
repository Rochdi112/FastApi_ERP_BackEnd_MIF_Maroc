import io
import pytest
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.intervention import Intervention
from app.core.security import get_password_hash


def _login_admin(client, db_session):
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
    r = client.post("/auth/token", data={"email": "admin@example.com", "password": "admin"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.usefixtures("client", "db_session")
def test_upload_and_static_serving(client, db_session):
    headers = _login_admin(client, db_session)
    # Ensure minimal intervention exists
    intr = db_session.query(Intervention).first()
    if not intr:
        intr = Intervention(titre="doc test", type="corrective", statut="ouverte", urgence=False)
        db_session.add(intr)
        db_session.commit()
        db_session.refresh(intr)
    file_bytes = io.BytesIO(b"hello")
    files = {"file": ("hello.txt", file_bytes, "text/plain")}
    r = client.post("/documents/upload", params={"intervention_id": intr.id}, files=files, headers=headers)
    assert r.status_code in (200, 201), r.text
    path = r.json().get("path")
    assert path and path.startswith("static/uploads/")
    s = client.get("/" + path)
    assert s.status_code == 200
