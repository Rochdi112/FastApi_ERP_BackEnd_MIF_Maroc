from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.technicien import Competence

client = TestClient(app)


def test_list_competences_endpoint():
    db = next(get_db())
    # ensure at least one competence
    if not db.query(Competence).first():
        db.add(Competence(nom="c1", domaine="general")); db.commit()
    # ensure an admin user for auth
    admin = db.query(User).filter(User.email == "tech_list_admin@example.com").first()
    if not admin:
        admin = User(username="ta", email="tech_list_admin@example.com", hashed_password=get_password_hash("a"), role=UserRole.admin, is_active=True)
        db.add(admin); db.commit()
    r = client.post("/api/v1/auth/token", data={"email": "tech_list_admin@example.com", "password": "a"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    q = client.get("/api/v1/techniciens/competences", headers=h)
    assert q.status_code == 200 and isinstance(q.json(), list)
