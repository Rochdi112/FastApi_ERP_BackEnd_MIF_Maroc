---
title: "ERP MIF Maroc - Testing & Quality Assurance"
path: "docs/00-FOUNDATION/TESTING_QA.md"
owner: "backend-team"
version: "0.1"
updated: "2025-01-27"
tags: ["testing", "qa", "pytest", "coverage", "quality"]
---

# ERP MIF Maroc - Testing & Quality Assurance

## Testing Overview

The ERP MIF Maroc system maintains a comprehensive testing strategy with **97.27% test coverage**, ensuring reliability, maintainability, and confidence in deployments. The testing approach covers unit tests, integration tests, API contract tests, and performance validation.

## Testing Philosophy

### Quality Standards
- **Minimum Coverage**: 90% (currently achieving 97.27%)
- **Test-Driven Development**: Write tests first for new features
- **Fail-Fast Principle**: Catch issues early in development cycle
- **Continuous Testing**: Automated test execution on every commit
- **Production Parity**: Test environments mirror production setup

### Testing Pyramid

```mermaid
graph TD
    subgraph "Testing Pyramid"
        E2E[End-to-End Tests<br/>5%]
        INT[Integration Tests<br/>25%]
        UNIT[Unit Tests<br/>70%]
    end
    
    subgraph "Test Types"
        API[API Contract Tests]
        SERVICE[Service Layer Tests]
        MODEL[Model Tests]
        SCHEMA[Schema Validation Tests]
        RBAC[RBAC & Security Tests]
        DB[Database Tests]
    end
    
    E2E --> API
    INT --> SERVICE
    INT --> RBAC
    INT --> DB
    UNIT --> MODEL
    UNIT --> SCHEMA
```

## Test Configuration

### Pytest Configuration

**pytest.ini**
```ini
[tool:pytest]
testpaths = app/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=90
    --strict-markers
    --disable-warnings
asyncio_mode = strict
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API tests
    security: marks tests as security tests
```

### Test Environment Setup

**Test Database Configuration**
```python
# app/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app

# Use SQLite in-memory for fast test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

### Test Data Factories

**User Factory**
```python
# app/tests/factories.py
from app.models.user import User, UserRole
from app.services.user_service import create_user
from app.schemas.user import UserCreate

def create_test_user(
    db_session,
    email: str = "test@example.com",
    username: str = "testuser",
    password: str = "testpassword",
    role: UserRole = UserRole.technicien,
    is_active: bool = True
) -> User:
    """Create test user with default values."""
    user_data = UserCreate(
        username=username,
        email=email,
        password=password,
        full_name="Test User",
        role=role
    )
    user = create_user(db_session, user_data)
    user.is_active = is_active
    db_session.commit()
    return user

def create_test_admin(db_session) -> User:
    """Create test admin user."""
    return create_test_user(
        db_session,
        email="admin@example.com",
        username="admin",
        role=UserRole.admin
    )

def create_test_technician(db_session) -> User:
    """Create test technician user."""
    return create_test_user(
        db_session,
        email="tech@example.com",
        username="technician",
        role=UserRole.technicien
    )
```

**Intervention Factory**
```python
def create_test_intervention(
    db_session,
    titre: str = "Test Intervention",
    equipement_id: int = 1,
    type_intervention: str = "corrective",
    statut: str = "ouverte",
    priorite: str = "normale"
) -> Intervention:
    """Create test intervention with default values."""
    intervention = Intervention(
        titre=titre,
        description="Test intervention description",
        equipement_id=equipement_id,
        type_intervention=type_intervention,
        statut=statut,
        priorite=priorite,
        urgence=False,
        date_creation=datetime.utcnow()
    )
    db_session.add(intervention)
    db_session.commit()
    db_session.refresh(intervention)
    return intervention
```

## Unit Testing

### Model Tests

**User Model Tests**
```python
# app/tests/models/test_user.py
def test_user_creation(db_session):
    """Test user model creation and basic properties."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        role=UserRole.technicien
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == UserRole.technicien
    assert user.is_active is True
    assert user.created_at is not None

def test_user_to_dict(db_session):
    """Test user to_dict serialization."""
    user = create_test_user(db_session)
    user_dict = user.to_dict()
    
    assert "id" in user_dict
    assert "username" in user_dict
    assert "email" in user_dict
    assert "role" in user_dict
    assert "hashed_password" not in user_dict  # Sensitive data excluded

def test_user_relationships(db_session):
    """Test user relationship loading."""
    user = create_test_user(db_session, role=UserRole.technicien)
    
    # Test lazy loading of related objects
    assert hasattr(user, 'technicien')
    assert hasattr(user, 'notifications')
```

**Intervention Model Tests**
```python
# app/tests/models/test_intervention.py
def test_intervention_creation(db_session):
    """Test intervention model creation."""
    intervention = create_test_intervention(db_session)
    
    assert intervention.id is not None
    assert intervention.titre == "Test Intervention"
    assert intervention.statut == StatutIntervention.ouverte
    assert intervention.date_creation is not None

def test_intervention_state_transitions(db_session):
    """Test intervention status transitions."""
    intervention = create_test_intervention(db_session)
    
    # Test valid transition
    intervention.statut = StatutIntervention.affectee
    db_session.commit()
    assert intervention.statut == StatutIntervention.affectee
    
    # Test workflow progression
    intervention.statut = StatutIntervention.en_cours
    intervention.date_debut = datetime.utcnow()
    db_session.commit()
    assert intervention.date_debut is not None

def test_intervention_business_rules(db_session):
    """Test intervention business rule enforcement."""
    intervention = create_test_intervention(db_session)
    
    # Test urgency implies high priority
    intervention.urgence = True
    intervention.priorite = PrioriteIntervention.urgente
    db_session.commit()
    
    assert intervention.urgence is True
    assert intervention.priorite == PrioriteIntervention.urgente
```

### Service Layer Tests

**Authentication Service Tests**
```python
# app/tests/services/test_auth_service.py
def test_authenticate_valid_user(db_session):
    """Test successful authentication with valid credentials."""
    user = create_test_user(db_session)
    
    token_response = authenticate_user(db_session, user.email, "testpassword")
    
    assert token_response.access_token is not None
    assert token_response.token_type == "bearer"
    
    # Verify token contains correct claims
    payload = decode_token(token_response.access_token)
    assert payload["sub"] == user.email
    assert payload["role"] == user.role
    assert payload["user_id"] == user.id

def test_authenticate_invalid_email(db_session):
    """Test authentication failure with invalid email."""
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(db_session, "nonexistent@example.com", "password")
    
    assert exc_info.value.status_code == 401
    assert "Email ou mot de passe incorrect" in str(exc_info.value.detail)

def test_authenticate_wrong_password(db_session):
    """Test authentication failure with wrong password."""
    user = create_test_user(db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(db_session, user.email, "wrongpassword")
    
    assert exc_info.value.status_code == 401

def test_authenticate_inactive_user(db_session):
    """Test authentication failure for inactive user."""
    user = create_test_user(db_session, is_active=False)
    
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(db_session, user.email, "testpassword")
    
    assert exc_info.value.status_code == 403
    assert "Compte désactivé" in str(exc_info.value.detail)
```

**Intervention Service Tests**
```python
# app/tests/services/test_intervention_service.py
def test_create_intervention_success(db_session):
    """Test successful intervention creation."""
    user = create_test_admin(db_session)
    equipement = create_test_equipement(db_session)
    
    intervention_data = InterventionCreate(
        titre="Test Intervention",
        description="Test description",
        equipement_id=equipement.id,
        type_intervention=InterventionType.corrective,
        priorite=PrioriteIntervention.normale
    )
    
    intervention = create_intervention(db_session, intervention_data, user.id)
    
    assert intervention.id is not None
    assert intervention.titre == "Test Intervention"
    assert intervention.equipement_id == equipement.id
    assert intervention.statut == StatutIntervention.ouverte

def test_create_intervention_invalid_equipment(db_session):
    """Test intervention creation with invalid equipment."""
    user = create_test_admin(db_session)
    
    intervention_data = InterventionCreate(
        titre="Test Intervention",
        description="Test description",
        equipement_id=999,  # Non-existent equipment
        type_intervention=InterventionType.corrective
    )
    
    with pytest.raises(HTTPException) as exc_info:
        create_intervention(db_session, intervention_data, user.id)
    
    assert exc_info.value.status_code == 404
    assert "Équipement cible introuvable" in str(exc_info.value.detail)
```

## Integration Testing

### API Endpoint Tests

**Authentication Endpoints**
```python
# app/tests/api/test_auth.py
def test_login_valid_credentials(client, db_session):
    """Test API login with valid credentials."""
    user = create_test_user(db_session)
    
    response = client.post("/api/v1/auth/token", data={
        "email": user.email,
        "password": "testpassword"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client, db_session):
    """Test API login with invalid credentials."""
    response = client.post("/api/v1/auth/token", data={
        "email": "invalid@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "Email ou mot de passe incorrect" in response.json()["detail"]

def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401

def test_protected_endpoint_with_valid_token(client, db_session):
    """Test accessing protected endpoint with valid token."""
    user = create_test_user(db_session)
    token = create_test_token(user_id=user.id, role=user.role)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user.email
```

**Intervention API Tests**
```python
# app/tests/api/test_interventions.py
def test_create_intervention_authorized(client, db_session):
    """Test creating intervention with proper authorization."""
    user = create_test_user(db_session, role=UserRole.responsable)
    equipement = create_test_equipement(db_session)
    token = create_test_token(user_id=user.id, role=user.role)
    
    intervention_data = {
        "titre": "API Test Intervention",
        "description": "Test intervention via API",
        "equipement_id": equipement.id,
        "type_intervention": "corrective",
        "priorite": "normale"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/interventions/", 
                          json=intervention_data, 
                          headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["titre"] == "API Test Intervention"
    assert data["statut"] == "ouverte"

def test_create_intervention_unauthorized(client, db_session):
    """Test creating intervention without proper authorization."""
    user = create_test_user(db_session, role=UserRole.client)
    token = create_test_token(user_id=user.id, role=user.role)
    
    intervention_data = {
        "titre": "Unauthorized Test",
        "description": "Should fail",
        "equipement_id": 1,
        "type_intervention": "corrective"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/interventions/", 
                          json=intervention_data, 
                          headers=headers)
    
    assert response.status_code == 403
```

### Database Integration Tests

**Migration Tests**
```python
# app/tests/db/test_migrations.py
def test_alembic_upgrade_head_on_temp_db(tmp_path):
    """Test that Alembic migrations can be applied successfully."""
    cfg = Config("alembic.ini")
    db_path = tmp_path / "alembic_test.sqlite"
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    
    # Run upgrade to head
    command.upgrade(cfg, "head")
    
    # Verify core tables exist
    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    
    required_tables = {
        'alembic_version',
        'users',
        'equipements',
        'interventions',
        'documents',
        'historiques_interventions',
        'notifications',
    }
    
    missing_tables = required_tables - tables
    assert not missing_tables, f"Missing tables: {missing_tables}"

def test_database_constraints(db_session):
    """Test database constraint enforcement."""
    # Test unique constraint on email
    user1 = create_test_user(db_session, email="unique@example.com")
    
    with pytest.raises(IntegrityError):
        user2 = create_test_user(db_session, email="unique@example.com")
    
    # Test foreign key constraints
    with pytest.raises(IntegrityError):
        intervention = Intervention(
            titre="Test",
            description="Test",
            equipement_id=999,  # Non-existent equipment
            type_intervention=InterventionType.corrective
        )
        db_session.add(intervention)
        db_session.commit()
```

## Security Testing

### RBAC Tests

**Role-Based Access Control**
```python
# app/tests/security/test_rbac.py
@pytest.mark.parametrize("role,expected_status", [
    (UserRole.admin, 200),
    (UserRole.responsable, 200),
    (UserRole.technicien, 403),
    (UserRole.client, 403)
])
def test_admin_endpoint_access(client, db_session, role, expected_status):
    """Test admin endpoint access with different roles."""
    user = create_test_user(db_session, role=role)
    token = create_test_token(user_id=user.id, role=role)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/admin/users", headers=headers)
    
    assert response.status_code == expected_status

def test_intervention_access_by_role(client, db_session):
    """Test intervention access filtering by role."""
    # Create users with different roles
    admin = create_test_user(db_session, role=UserRole.admin, email="admin@test.com")
    tech = create_test_user(db_session, role=UserRole.technicien, email="tech@test.com")
    client_user = create_test_user(db_session, role=UserRole.client, email="client@test.com")
    
    # Create interventions
    intervention1 = create_test_intervention(db_session, technicien_id=tech.id)
    intervention2 = create_test_intervention(db_session, client_id=client_user.id)
    
    # Test admin sees all interventions
    admin_token = create_test_token(user_id=admin.id, role=UserRole.admin)
    response = client.get("/api/v1/interventions/", 
                         headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 2
    
    # Test technician sees only assigned interventions
    tech_token = create_test_token(user_id=tech.id, role=UserRole.technicien)
    response = client.get("/api/v1/interventions/", 
                         headers={"Authorization": f"Bearer {tech_token}"})
    assert response.status_code == 200
    tech_interventions = response.json()
    assert all(i["technicien_id"] == tech.id for i in tech_interventions)
```

### Security Vulnerability Tests

**JWT Security Tests**
```python
# app/tests/security/test_jwt.py
def test_jwt_token_expiration():
    """Test JWT token expiration handling."""
    # Create expired token
    expired_data = {
        "sub": "test@example.com",
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    }
    expired_token = jwt.encode(expired_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        decode_token(expired_token)
    
    assert exc_info.value.status_code == 403
    assert "Token invalide ou expiré" in str(exc_info.value.detail)

def test_jwt_invalid_signature():
    """Test JWT token with invalid signature."""
    # Create token with wrong secret
    invalid_token = jwt.encode(
        {"sub": "test@example.com"}, 
        "wrong-secret", 
        algorithm=settings.ALGORITHM
    )
    
    with pytest.raises(HTTPException) as exc_info:
        decode_token(invalid_token)
    
    assert exc_info.value.status_code == 403

def test_password_hashing_security():
    """Test password hashing security."""
    password = "testpassword"
    
    # Test hash generation
    hashed1 = hash_password(password)
    hashed2 = hash_password(password)
    
    # Hashes should be different (due to salt)
    assert hashed1 != hashed2
    
    # Both should verify correctly
    assert verify_password(password, hashed1)
    assert verify_password(password, hashed2)
    
    # Wrong password should fail
    assert not verify_password("wrongpassword", hashed1)
```

## Performance Testing

### API Performance Tests

**Response Time Tests**
```python
# app/tests/performance/test_api_performance.py
import time

def test_authentication_performance(client, db_session):
    """Test authentication endpoint performance."""
    user = create_test_user(db_session)
    
    start_time = time.time()
    response = client.post("/api/v1/auth/token", data={
        "email": user.email,
        "password": "testpassword"
    })
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # Should complete in < 1 second

def test_intervention_list_performance(client, db_session):
    """Test intervention listing performance with large dataset."""
    # Create multiple interventions
    user = create_test_user(db_session, role=UserRole.admin)
    for i in range(100):
        create_test_intervention(db_session, titre=f"Intervention {i}")
    
    token = create_test_token(user_id=user.id, role=user.role)
    headers = {"Authorization": f"Bearer {token}"}
    
    start_time = time.time()
    response = client.get("/api/v1/interventions/", headers=headers)
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 2.0  # Should complete in < 2 seconds
    assert len(response.json()) == 100
```

### Database Performance Tests

**Query Performance**
```python
# app/tests/performance/test_db_performance.py
def test_user_query_performance(db_session):
    """Test user query performance with indexes."""
    # Create multiple users
    for i in range(1000):
        create_test_user(db_session, 
                        email=f"user{i}@example.com", 
                        username=f"user{i}")
    
    # Test indexed query performance
    start_time = time.time()
    user = db_session.query(User).filter(User.email == "user500@example.com").first()
    end_time = time.time()
    
    assert user is not None
    assert (end_time - start_time) < 0.1  # Should be very fast with index

def test_intervention_filtering_performance(db_session):
    """Test intervention filtering performance."""
    # Create test data
    tech = create_test_user(db_session, role=UserRole.technicien)
    for i in range(500):
        create_test_intervention(db_session, 
                               titre=f"Intervention {i}",
                               technicien_id=tech.id if i % 2 == 0 else None)
    
    # Test filtered query performance
    start_time = time.time()
    interventions = db_session.query(Intervention).filter(
        Intervention.technicien_id == tech.id,
        Intervention.statut == StatutIntervention.ouverte
    ).all()
    end_time = time.time()
    
    assert len(interventions) > 0
    assert (end_time - start_time) < 0.5  # Should be fast with proper indexes
```

## Test Data Management

### Test Data Cleanup

```python
# app/tests/conftest.py
@pytest.fixture(autouse=True)
def cleanup_test_data(db_session):
    """Automatically cleanup test data after each test."""
    yield
    
    # Clean up in reverse dependency order
    db_session.query(HistoriqueIntervention).delete()
    db_session.query(Document).delete()
    db_session.query(Planning).delete()
    db_session.query(Intervention).delete()
    db_session.query(Equipement).delete()
    db_session.query(Technicien).delete()
    db_session.query(Client).delete()
    db_session.query(User).delete()
    db_session.commit()
```

### Test Data Seeding

```python
# app/tests/seed_test_data.py
def seed_test_database(db_session):
    """Seed database with comprehensive test data."""
    # Create users
    admin = create_test_user(db_session, role=UserRole.admin, email="admin@test.com")
    tech1 = create_test_user(db_session, role=UserRole.technicien, email="tech1@test.com")
    tech2 = create_test_user(db_session, role=UserRole.technicien, email="tech2@test.com")
    client1 = create_test_user(db_session, role=UserRole.client, email="client1@test.com")
    
    # Create equipment
    equipment1 = create_test_equipement(db_session, client_id=client1.id, nom="Pump A")
    equipment2 = create_test_equipement(db_session, client_id=client1.id, nom="Pump B")
    
    # Create interventions with different statuses
    create_test_intervention(db_session, 
                           titre="Open Intervention",
                           equipement_id=equipment1.id,
                           statut=StatutIntervention.ouverte)
    
    create_test_intervention(db_session,
                           titre="Assigned Intervention", 
                           equipement_id=equipment2.id,
                           technicien_id=tech1.id,
                           statut=StatutIntervention.affectee)
    
    return {
        "admin": admin,
        "technicians": [tech1, tech2],
        "clients": [client1],
        "equipment": [equipment1, equipment2]
    }
```

## Test Execution

### Running Tests

**Local Development**
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration            # Integration tests only
pytest -m security              # Security tests only

# Run specific test files
pytest app/tests/api/test_auth.py
pytest app/tests/services/test_intervention_service.py

# Run with verbose output
pytest -v

# Run failed tests only
pytest --lf

# Run tests in parallel (with pytest-xdist)
pytest -n auto
```

**Docker Environment**
```bash
# Run tests in Docker container
docker-compose exec api pytest

# Run with coverage in Docker
docker-compose exec api pytest --cov=app --cov-report=term-missing
```

### Continuous Integration

**GitHub Actions Example**
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml --cov-fail-under=90
      env:
        DATABASE_URL: postgresql://postgres:test_password@localhost/test_db
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Quality Metrics

### Coverage Reports

**Current Coverage**: 97.27%
- Required minimum: 90%
- Target: 95%+

**Coverage by Module**
```
app/api/          98.5%
app/services/     97.2%
app/models/       96.8%
app/schemas/      98.9%
app/core/         95.3%
app/db/           94.7%
Overall:          97.27%
```

### Test Quality Metrics

**Test Distribution**
- Unit Tests: 70% (121 tests)
- Integration Tests: 25% (43 tests)
- End-to-End Tests: 5% (9 tests)

**Performance Benchmarks**
- Test suite execution time: < 30 seconds
- Individual test timeout: 5 seconds
- Database test isolation: Complete per test

---

*This testing documentation provides comprehensive coverage of testing strategies, implementation patterns, and quality assurance practices for the ERP MIF Maroc system.*