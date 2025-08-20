# app/tests/test_techniciens.py

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.technicien import Technicien, Competence

def create_user_with_role(db: Session, role: UserRole, suffix: str = "") -> User:
    user = User(
        username=f"user_{role}_{suffix}",
        full_name=f"{role.capitalize()} Test",
        email=f"{role}_{suffix}@example.com",
        hashed_password=get_password_hash("testpass123"),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_competence(db: Session, nom: str) -> Competence:
    comp = Competence(nom=nom, domaine="general")
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp

def test_create_technicien(client: TestClient, db_session: Session):
    """
    Vérifie qu'un responsable peut créer un technicien avec des compétences.
    """
    suffix = str(uuid.uuid4())[:6]
    responsable = create_user_with_role(db_session, UserRole.responsable, suffix)
    technicien_user = create_user_with_role(db_session, UserRole.technicien, suffix)
    comp1 = create_competence(db_session, f"mecanique_{suffix}")
    comp2 = create_competence(db_session, f"hydraulique_{suffix}")

    # Important : tout commit, sinon session pas vue par l'API
    db_session.commit()
    db_session.expire_all()

    token = create_access_token(data={
        "sub": responsable.email,
        "role": "responsable"
    })
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "user_id": technicien_user.id,
        "equipe": "Equipe A",
        "disponibilite": "Disponible",
        "competences_ids": [comp1.id, comp2.id]
    }

    response = client.post("/techniciens/", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["user"]["email"] == technicien_user.email
    assert len(data["competences"]) == 2

def test_get_technicien_by_id(client: TestClient, db_session: Session, admin_token):
    """
    Vérifie qu'un admin peut accéder au détail d'un technicien existant.
    """
    suffix = str(uuid.uuid4())[:6]
    user = create_user_with_role(db_session, UserRole.technicien, suffix)
    technicien = Technicien(user_id=user.id)
    db_session.add(technicien)
    db_session.commit()
    db_session.refresh(technicien)

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/techniciens/{technicien.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == technicien.id
    assert "user" in response.json()

def test_technicien_create_forbidden(client: TestClient, db_session: Session, technicien_token):
    """
    Vérifie qu'un technicien ne peut PAS créer un technicien (RBAC).
    """
    suffix = str(uuid.uuid4())[:6]
    user = create_user_with_role(db_session, UserRole.technicien, suffix)

    headers = {"Authorization": f"Bearer {technicien_token}"}
    payload = {
        "user_id": user.id,
        "equipe": "Equipe B",
        "disponibilite": "Indisponible",
        "competences_ids": []
    }
    response = client.post("/techniciens/", json=payload, headers=headers)
    assert response.status_code == 403
