import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.core.security import create_access_token
from app.models.user import UserRole

# ----------- CONFIG BDD TEST EN MÉMOIRE -----------
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # Critique : pour garder la même BDD mémoire sur toute la durée des tests
)

# Création tables au démarrage des tests
Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# ----------- SESSION DB ISOLÉE PAR TEST -----------

@pytest.fixture(scope="function")
def db_session():
    """
    Fournit une session DB isolée avec rollback après chaque test.
    Évite toute persistance accidentelle d'un test à l'autre.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

# ----------- CLIENT FASTAPI AVEC DB OVERRIDE -----------

@pytest.fixture(scope="function")
def client(db_session):
    """
    Fournit un client FastAPI avec la dépendance get_db overridée
    pour pointer sur la session de test.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# ----------- FIXTURES TOKENS POUR RBAC -----------

@pytest.fixture
def admin_token():
    """JWT valide pour un admin (hardcodé pour tests rapides)"""
    return create_access_token(data={"sub": "admin@test.com", "role": UserRole.admin})

@pytest.fixture
def responsable_token():
    """JWT valide pour un responsable"""
    return create_access_token(data={"sub": "resp@test.com", "role": UserRole.responsable})

@pytest.fixture
def technicien_token():
    """JWT valide pour un technicien"""
    return create_access_token(data={"sub": "tech@test.com", "role": UserRole.technicien})

@pytest.fixture
def client_token():
    """JWT valide pour un client lambda"""
    return create_access_token(data={"sub": "client@test.com", "role": UserRole.client})

# ----------- UTILITAIRES BONUS -----------

@pytest.fixture
def auth_headers(admin_token):
    """Headers d'authentification Bearer prêts à l'emploi (admin par défaut)"""
    return {"Authorization": f"Bearer {admin_token}"}

# Ajoute d'autres headers/fonctions utilitaires pour d'autres rôles si besoin
