from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.technicien import Technicien
from app.models.intervention import Intervention
from app.core.security import get_password_hash, create_access_token

client = TestClient(app)


def test_filter_with_technicien_id_param():
    db = next(get_db())
    # Ensure a technicien and an intervention linked
    u = User(username="tuser", email="tuser@example.com", hashed_password=get_password_hash("x"), role=UserRole.technicien, is_active=True)
    db.add(u); db.commit(); db.refresh(u)
    t = Technicien(user_id=u.id)
    db.add(t); db.commit(); db.refresh(t)
    intr = Intervention(titre="ft", type="corrective", statut="ouverte", urgence=False, technicien_id=t.id)
    db.add(intr); db.commit()
    token = create_access_token({"sub": u.email, "email": u.email, "role": "admin"})
    r = client.get(f"/api/v1/filters/interventions?technicien_id={t.id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert any(item["id"] == intr.id for item in r.json())
