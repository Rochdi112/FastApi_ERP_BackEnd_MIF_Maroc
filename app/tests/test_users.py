import pytest
import uuid
from fastapi.testclient import TestClient
from app.db.database import get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def test_create_user_success(client: TestClient, admin_token):
    """
    ✅ Création réussie d’un utilisateur par un admin
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    unique = str(uuid.uuid4())[:8]
    data = {
        "username": f"newuser_{unique}",
        "full_name": "New User",
        "email": f"newuser_{unique}@example.com",
        "password": "newpass123",
        "role": "technicien"
    }
    response = client.post("/users/", json=data, headers=headers)
    # Si ta route POST retourne 201, adapte ici :
    assert response.status_code in (200, 201)
    result = response.json()
    assert result["email"] == data["email"]
    assert result["role"] == data["role"]
    assert result["username"] == data["username"]
    assert result["full_name"] == data["full_name"]
    assert result["is_active"] is True

def test_create_user_duplicate_email(client: TestClient, admin_token):
    """
    ❌ Erreur si email déjà utilisé
    """
    db = next(get_db())
    unique = str(uuid.uuid4())[:8]
    email = f"duplicate_{unique}@example.com"
    username = f"userdup_{unique}"

    db.add(User(
        username=username,
        full_name="Dup User",
        email=email,
        hashed_password=get_password_hash("pass"),
        role=UserRole.client,
        is_active=True
    ))
    db.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "username": f"another_{unique}",
        "full_name": "Another User",
        "email": email,  # même email
        "password": "pass123",
        "role": "client"
    }

    response = client.post("/users/", json=data, headers=headers)
    assert response.status_code in (400, 409)
    assert "Email déjà utilisé" in response.text

def test_get_user_by_id(client: TestClient, admin_token):
    """
    ✅ Lecture utilisateur par ID
    """
    db = next(get_db())
    unique = str(uuid.uuid4())[:8]
    user = User(
        username=f"lookup_{unique}",
        full_name="Lookup User",
        email=f"lookup_{unique}@example.com",
        hashed_password=get_password_hash("pass"),
        role=UserRole.client,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/users/{user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == user.email
    assert response.json()["username"] == user.username

def test_get_all_users(client: TestClient, admin_token):
    """
    ✅ Lecture de tous les utilisateurs
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_user_access_forbidden_for_non_admin(client: TestClient, technicien_token):
    """
    ❌ Refus d’accès si non-admin
    """
    headers = {"Authorization": f"Bearer {technicien_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 403
