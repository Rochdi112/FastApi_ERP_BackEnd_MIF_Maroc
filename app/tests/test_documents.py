import os
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
def user_and_token(db):
    """Crée un utilisateur admin actif et retourne son token"""
    user = User(
        username="docuser",
        email="docuser@example.com",
        hashed_password=get_password_hash("docpass"),
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "docuser", "password": "docpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = response.json()["access_token"]
    yield {"Authorization": f"Bearer {token}"}, user
    db.delete(user)
    db.commit()

@pytest.fixture(scope="module")
def intervention(db):
    """Crée une intervention à lier à un document"""
    intervention = Intervention(
        titre="Test Intervention",
        description="Intervention avec document",
        statut="ouverte",
        type="corrective",
        urgence=False
    )
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    yield intervention
    db.delete(intervention)
    db.commit()

def test_upload_document(user_and_token, intervention):
    """Upload d’un document lié à une intervention"""
    headers, _ = user_and_token
    intervention_id = intervention.id

    # Crée un fichier temporaire à uploader
    test_file_path = "app/tests/test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("Contenu de test")

    with open(test_file_path, "rb") as file:
        response = client.post(
            f"/api/v1/documents/upload?intervention_id={intervention_id}",
            files={"file": ("test_upload.txt", file, "text/plain")},
            headers=headers
        )

    os.remove(test_file_path)

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test_upload.txt"
    assert data["intervention_id"] == intervention_id

def test_get_documents_by_intervention(user_and_token, intervention):
    """Récupération des documents liés à une intervention"""
    headers, _ = user_and_token
    response = client.get(
        f"/api/v1/documents/{intervention.id}",
        headers=headers
    )
    assert response.status_code == 200
    documents = response.json()
    assert isinstance(documents, list)
    assert any(doc["intervention_id"] == intervention.id for doc in documents)

def test_get_documents_empty_list(user_and_token, db):
    """Test récupération sur intervention sans documents"""
    headers, _ = user_and_token
    empty_intervention = Intervention(
        titre="Empty Intervention",
        description="Sans documents",
        statut="ouverte",
        type="préventive",
        urgence=False
    )
    db.add(empty_intervention)
    db.commit()
    db.refresh(empty_intervention)

    response = client.get(
        f"/api/v1/documents/{empty_intervention.id}",
        headers=headers
    )
    db.delete(empty_intervention)
    db.commit()

    assert response.status_code == 200
    assert response.json() == []
