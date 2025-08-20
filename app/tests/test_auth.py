import pytest
from fastapi.testclient import TestClient
from app.db.database import get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.main import app  # Importe ton FastAPI principal

# ======= CLIENT GLOBAL =======
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# ======= FIXTURES UTILISATEURS TEST =======

@pytest.fixture
def create_test_user():
    """
    Crée un utilisateur actif admin dans la base de test.
    """
    db = next(get_db())
    existing = db.query(User).filter(User.email == "admin@test.com").first()
    if existing:
        db.delete(existing)
        db.commit()

    user = User(
        username="admin",
        full_name="Admin Test",
        email="admin@test.com",
        hashed_password=get_password_hash("secret123"),
        role=UserRole.admin,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def create_inactive_user():
    """
    Crée un utilisateur inactif pour tester l'échec de connexion.
    """
    db = next(get_db())
    existing = db.query(User).filter(User.email == "inactive@test.com").first()
    if existing:
        db.delete(existing)
        db.commit()

    user = User(
        username="inactive",
        full_name="Inactive User",
        email="inactive@test.com",
        hashed_password=get_password_hash("secret123"),
        role=UserRole.technicien,
        is_active=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ============ TESTS AUTHENTIFICATION ============

def test_login_success(client, create_test_user):
    """
    Connexion réussie avec email + mot de passe correct.
    """
    response = client.post("/auth/token", data={
        "email": "admin@test.com",         # ⚠️ Correction : c'est bien 'email', pas 'username' !
        "password": "secret123"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, create_test_user):
    """
    Connexion échoue si mauvais mot de passe.
    """
    response = client.post("/auth/token", data={
        "email": "admin@test.com",
        "password": "wrongpass"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401

def test_login_unknown_email(client):
    """
    Connexion échoue si email inconnu.
    """
    response = client.post("/auth/token", data={
        "email": "notfound@test.com",
        "password": "secret123"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401

def test_login_inactive_user(client, create_inactive_user):
    """
    Connexion échoue si user inactif.
    """
    response = client.post("/auth/token", data={
        "email": "inactive@test.com",
        "password": "secret123"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 403

# ============ BONUS : TESTE LE FLUX /auth/me ============
def test_me_route(client, create_test_user):
    """
    Teste la récupération du profil utilisateur courant via /auth/me avec JWT.
    """
    # 1. Authentification pour obtenir le token
    login_resp = client.post("/auth/token", data={
        "email": "admin@test.com",
        "password": "secret123"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 2. Appel de /auth/me avec le JWT récupéré
    me_resp = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"
    assert data["is_active"] is True

