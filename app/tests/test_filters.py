import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.user import User
from app.models.intervention import Intervention
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def filter_user_and_token(db):
    """Crée un utilisateur admin pour les filtres"""
    user = User(
        username="filteruser",
        email="filteruser@example.com",
        hashed_password=get_password_hash("filterpass"),
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    login = client.post(
        "/api/v1/auth/login",
        data={"username": "filteruser", "password": "filterpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def seed_interventions(db):
    """Insère des interventions variées"""
    interventions = [
        Intervention(titre="Corrective urgente", type="corrective", urgence=True, statut="ouverte"),
        Intervention(titre="Préventive planifiée", type="préventive", urgence=False, statut="clôturée"),
        Intervention(titre="Corrective en attente", type="corrective", urgence=False, statut="en_attente"),
    ]
    db.add_all(interventions)
    db.commit()
    yield interventions
    for i in interventions:
        db.delete(i)
    db.commit()

def test_filter_by_type(filter_user_and_token, seed_interventions):
    """Filtre par type d’intervention"""
    headers = filter_user_and_token
    response = client.get("/api/v1/filters/interventions?type=corrective", headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert all(interv["type"] == "corrective" for interv in results)

def test_filter_by_statut(filter_user_and_token, seed_interventions):
    """Filtre par statut"""
    headers = filter_user_and_token
    response = client.get("/api/v1/filters/interventions?statut=en_attente", headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert all(interv["statut"] == "en_attente" for interv in results)

def test_filter_by_urgence(filter_user_and_token, seed_interventions):
    """Filtre par urgence booléenne"""
    headers = filter_user_and_token
    response = client.get("/api/v1/filters/interventions?urgence=true", headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert all(interv["urgence"] is True for interv in results)

def test_filter_combined(filter_user_and_token, seed_interventions):
    """Filtre combiné type + urgence + statut"""
    headers = filter_user_and_token
    response = client.get(
        "/api/v1/filters/interventions?type=corrective&urgence=false&statut=en_attente",
        headers=headers
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    intervention = results[0]
    assert intervention["type"] == "corrective"
    assert intervention["urgence"] is False
    assert intervention["statut"] == "en_attente"
