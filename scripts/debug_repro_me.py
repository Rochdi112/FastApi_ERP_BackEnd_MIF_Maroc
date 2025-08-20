from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.core.security import create_access_token

# Setup in-memory test DB
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

admin_token = create_access_token({"sub":"admin@test.com","email":"admin@test.com","role":"admin"})

new_user_payload = {
    "username": "jdoe",
    "full_name": "John Doe",
    "email": "jdoe@example.com",
    "role": "client",
    "password": "secret123",
}

r = client.post("/api/v1/users/", json=new_user_payload, headers={"Authorization": f"Bearer {admin_token}"})
print("create status:", r.status_code, r.text)
created = r.json()

user_token = create_access_token({"sub": created["email"], "email": created["email"], "role": created["role"]})

r2 = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {user_token}"})
print("/me status:", r2.status_code, r2.text)
