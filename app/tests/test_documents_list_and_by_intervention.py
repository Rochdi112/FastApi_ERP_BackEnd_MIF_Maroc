from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_password_hash
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.intervention import Intervention
from app.models.document import Document

client = TestClient(app)


def _admin_headers():
    db = next(get_db())
    admin = db.query(User).filter(User.email == "docs_admin@example.com").first()
    if not admin:
        admin = User(
            username="docs_admin",
            full_name="Docs Admin",
            email="docs_admin@example.com",
            hashed_password=get_password_hash("admin"),
            role=UserRole.admin,
            is_active=True,
        )
        db.add(admin); db.commit()
    r = client.post("/api/v1/auth/token", data={"email": "docs_admin@example.com", "password": "admin"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_list_documents_and_by_intervention():
    headers = _admin_headers()
    db = next(get_db())
    intr = db.query(Intervention).first()
    if not intr:
        intr = Intervention(titre="d", type="corrective", statut="ouverte", urgence=False)
        db.add(intr); db.commit(); db.refresh(intr)
    # ensure at least one document row exists even without file content path
    doc = db.query(Document).first()
    if not doc:
        doc = Document(nom_fichier="a.txt", chemin="static/uploads/a.txt", intervention_id=intr.id)
        db.add(doc); db.commit(); db.refresh(doc)
    r1 = client.get("/api/v1/documents/", headers=headers)
    assert r1.status_code == 200
    r2 = client.get(f"/api/v1/documents/{intr.id}", headers=headers)
    assert r2.status_code == 200
