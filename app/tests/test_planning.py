import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.user import User
from app.models.equipement import Equipement
from app.models.planning import Planning
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def admin_token_and_equipement(db):
    """Crée un utilisateur admin + équipement"""
    user = User(
        username="planningadmin",
        email="planadmin@example.com",
        hashed_password=get_password_hash("planpass"),
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "planningadmin", "password": "planpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    equipement = Equipement(
        nom="Pompe N7",
        type="Pompe",
        localisation="Zone A",
        frequence_maintenance="mensuelle"
    )
    db.add(equipement)
    db.commit()
    db.refresh(equipement)

    return headers, equipement

@pytest.fixture()
def created_planning(admin_token_and_equipement):
    """Crée un planning temporaire"""
    headers, equipement = admin_token_and_equipement
    response = client.post(
        "/api/v1/planning/",
        json={
            "equipement_id": equipement.id,
            "date_prevue": "2025-08-01",
            "frequence": "mensuelle",
            "remarques": "Entretien standard"
        },
        headers=headers
    )
    assert response.status_code == 201
    planning = response.json()
    yield headers, planning
    client.delete(f"/api/v1/planning/{planning['id']}", headers=headers)

def test_create_planning(admin_token_and_equipement):
    """Création simple d’un planning"""
    headers, equipement = admin_token_and_equipement
    response = client.post(
        "/api/v1/planning/",
        json={
            "equipement_id": equipement.id,
            "date_prevue": "2025-08-15",
            "frequence": "mensuelle",
            "remarques": "Vérification initiale"
        },
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["frequence"] == "mensuelle"

    # Nettoyage
    client.delete(f"/api/v1/planning/{data['id']}", headers=headers)

def test_get_all_planning(created_planning):
    """Liste tous les plannings"""
    headers, _ = created_planning
    response = client.get("/api/v1/planning/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_planning_by_id(created_planning):
    """Récupération par ID"""
    headers, planning = created_planning
    response = client.get(f"/api/v1/planning/{planning['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == planning["id"]

def test_update_planning(created_planning):
    """Modification fréquence"""
    headers, planning = created_planning
    response = client.put(
        f"/api/v1/planning/{planning['id']}",
        json={"frequence": "trimestrielle"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["frequence"] == "trimestrielle"

def test_delete_planning_independent(admin_token_and_equipement):
    """Création et suppression isolée"""
    headers, equipement = admin_token_and_equipement
    response = client.post(
        "/api/v1/planning/",
        json={
            "equipement_id": equipement.id,
            "date_prevue": "2025-09-01",
            "frequence": "mensuelle",
            "remarques": "Planning à supprimer"
        },
        headers=headers
    )
    assert response.status_code == 201
    planning_id = response.json()["id"]

    delete_resp = client.delete(f"/api/v1/planning/{planning_id}", headers=headers)
    assert delete_resp.status_code == 204
