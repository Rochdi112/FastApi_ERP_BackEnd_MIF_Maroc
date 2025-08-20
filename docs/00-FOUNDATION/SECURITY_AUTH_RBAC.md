---
title: "ERP MIF Maroc - Security, Authentication & RBAC"
path: "docs/00-FOUNDATION/SECURITY_AUTH_RBAC.md"
owner: "backend-team"
version: "0.1"
updated: "2025-01-27"
tags: ["security", "authentication", "authorization", "rbac", "jwt", "passwords"]
---

# ERP MIF Maroc - Security, Authentication & RBAC

## Security Overview

The ERP MIF Maroc system implements a comprehensive security framework built on **JWT (JSON Web Tokens)** for authentication and **Role-Based Access Control (RBAC)** for authorization. The security architecture ensures data protection, user authentication, and granular access control across all system components.

## Authentication Architecture

### JWT Token-Based Authentication

**Authentication Flow**
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant AuthService
    participant Database
    participant JWT

    Client->>API: POST /auth/token {email, password}
    API->>AuthService: authenticate_user()
    AuthService->>Database: Query user by email
    Database-->>AuthService: User record
    AuthService->>AuthService: Verify password hash
    alt Valid credentials
        AuthService->>JWT: create_access_token()
        JWT-->>AuthService: JWT token
        AuthService-->>API: TokenResponse
        API-->>Client: {access_token, token_type}
    else Invalid credentials
        AuthService-->>API: 401 Unauthorized
        API-->>Client: Authentication failed
    end
    
    Note over Client: Store token for subsequent requests
    
    Client->>API: Request with Authorization header
    API->>JWT: Verify and decode token
    JWT-->>API: User claims
    API->>Database: Get current user details
    Database-->>API: User profile
    API-->>Client: Protected resource
```

### Authentication Implementation

**JWT Token Structure**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user@example.com",    // Subject (user identifier)
    "user_id": 123,               // Internal user ID
    "role": "technicien",         // User role for RBAC
    "exp": 1640995200,            // Expiration timestamp
    "iat": 1640991600             // Issued at timestamp
  },
  "signature": "..." // HMAC-SHA256 signature
}
```

**Authentication Service (`app/services/auth_service.py`)**
```python
def authenticate_user(db: Session, email: str, password: str) -> TokenResponse:
    """
    Authenticate user with email and password.
    Returns JWT token if successful.
    """
    user = db.query(User).filter(User.email == email).first()

    # Verify user existence and password
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )

    # Create JWT token with user claims
    access_token = create_access_token(
        data={
            "sub": user.email,      # RFC 7519 standard subject
            "role": user.role,      # RBAC role
            "user_id": user.id      # Internal tracking ID
        }
    )

    return TokenResponse(access_token=access_token, token_type="bearer")

def authenticate_user_by_username(db: Session, username: str, password: str) -> TokenResponse:
    """Alternative authentication method using username instead of email."""
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou mot de passe incorrect"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
            "user_id": user.id
        }
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer")
```

**Security Configuration (`app/core/security.py`)**
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and verify JWT token."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token invalide ou expiré"
        )
```

## Role-Based Access Control (RBAC)

### User Roles Definition

| Role | Description | Permissions | Target Users |
|------|-------------|-------------|--------------|
| **admin** | System administrator | Full system access, user management, system configuration | IT administrators, system managers |
| **responsable** | Operations manager | Intervention oversight, planning, team management, reporting | Operations supervisors, team leaders |
| **technicien** | Field technician | Own interventions, equipment updates, time tracking, documentation | Field service technicians |
| **client** | External client | Own equipment view, intervention requests, document access | Customer organizations |

### Role Hierarchy and Permissions

```mermaid
graph TD
    subgraph "Permission Hierarchy"
        ADMIN[Admin<br/>Full Access]
        RESP[Responsable<br/>Operations Management]
        TECH[Technicien<br/>Field Operations]
        CLIENT[Client<br/>Self-Service]
    end
    
    subgraph "Permissions Matrix"
        A1[User Management] --> ADMIN
        A2[System Configuration] --> ADMIN
        A3[Global Reporting] --> ADMIN
        
        B1[Team Management] --> RESP
        B2[Intervention Assignment] --> RESP
        B3[Planning Oversight] --> RESP
        B4[Performance Analytics] --> RESP
        
        C1[Own Interventions] --> TECH
        C2[Equipment Updates] --> TECH
        C3[Time Tracking] --> TECH
        C4[Field Documentation] --> TECH
        
        D1[Equipment Viewing] --> CLIENT
        D2[Request Interventions] --> CLIENT
        D3[Document Access] --> CLIENT
        D4[Status Monitoring] --> CLIENT
    end
    
    ADMIN -.-> RESP
    RESP -.-> TECH
    TECH -.-> CLIENT
```

### RBAC Implementation

**RBAC Dependency Factory (`app/core/rbac.py`)**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Extract and validate current user from JWT token.
    
    Returns:
        dict: User information with role and permissions
    """
    payload = decode_token(token)
    role = payload.get("role")
    
    if not role:
        raise HTTPException(
            status_code=403, 
            detail="Rôle manquant dans le token"
        )
    
    # Extract user identifiers
    user_id = payload.get("user_id")
    sub = payload.get("sub")  # email or username
    
    # Try to load full user from database
    user_obj = None
    if user_id:
        try:
            user_obj = get_user_by_id(db, int(user_id))
        except Exception:
            pass
    elif sub:
        try:
            # Try as numeric ID first, then as email
            if str(sub).isdigit():
                user_obj = get_user_by_id(db, int(sub))
            else:
                user_obj = get_user_by_email(db, str(sub))
        except Exception:
            pass
    
    # Return user information for RBAC
    if user_obj:
        if not getattr(user_obj, "is_active", True):
            raise HTTPException(
                status_code=403, 
                detail="Utilisateur désactivé"
            )
        
        return {
            "user_id": user_obj.id,
            "email": user_obj.email,
            "role": user_obj.role,
            "is_active": True,
        }
    
    # Fallback for token-only validation
    return {
        "user_id": user_id,
        "email": sub if isinstance(sub, str) else None,
        "role": role,
        "is_active": True,
    }

def require_roles(*roles: str):
    """
    Factory function to create role-based dependencies.
    
    Args:
        *roles: Allowed roles for the endpoint
        
    Returns:
        Dependency function that validates user role
    """
    def role_dependency(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôles autorisés: {', '.join(roles)}"
            )
        return current_user
    
    return role_dependency

# Pre-configured role dependencies
admin_required = require_roles("admin")
responsable_required = require_roles("responsable")
technicien_required = require_roles("technicien")
client_required = require_roles("client")
auth_required = require_roles("admin", "responsable", "technicien", "client")
```

### Endpoint Protection Examples

**Admin-Only Endpoints**
```python
@router.get("/admin/users", dependencies=[Depends(admin_required)])
def list_all_users(db: Session = Depends(get_db)):
    """Only admin can view all users."""
    return db.query(User).all()

@router.delete("/admin/users/{user_id}", dependencies=[Depends(admin_required)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Only admin can delete users."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return {"message": "User deleted"}
```

**Role-Based Resource Access**
```python
@router.get("/interventions/")
def list_interventions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_required)
):
    """List interventions based on user role."""
    query = db.query(Intervention)
    
    if current_user["role"] == "admin":
        # Admin sees all interventions
        pass
    elif current_user["role"] == "responsable":
        # Responsable sees all interventions for management
        pass
    elif current_user["role"] == "technicien":
        # Technicien sees only assigned interventions
        query = query.filter(Intervention.technicien_id == current_user["user_id"])
    elif current_user["role"] == "client":
        # Client sees only their own interventions
        query = query.filter(Intervention.client_id == current_user["user_id"])
    
    return query.all()
```

**Multiple Role Access**
```python
@router.patch("/interventions/{intervention_id}/status")
def update_intervention_status(
    intervention_id: int,
    status: StatutIntervention,
    current_user: dict = Depends(require_roles("responsable", "technicien")),
    db: Session = Depends(get_db)
):
    """Responsables and techniciens can update intervention status."""
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    
    # Additional authorization checks
    if current_user["role"] == "technicien":
        # Technicien can only update their own interventions
        if intervention.technicien_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
    
    intervention.statut = status
    db.commit()
    return intervention
```

## Permission Matrix

### Detailed RBAC Matrix

| Resource/Action | Admin | Responsable | Technicien | Client |
|-----------------|-------|-------------|------------|--------|
| **Users** | | | | |
| Create user | ✅ | ❌ | ❌ | ❌ |
| View all users | ✅ | ✅ | ❌ | ❌ |
| View own profile | ✅ | ✅ | ✅ | ✅ |
| Update own profile | ✅ | ✅ | ✅ | ✅ |
| Delete user | ✅ | ❌ | ❌ | ❌ |
| Activate/deactivate | ✅ | ❌ | ❌ | ❌ |
| **Interventions** | | | | |
| View all interventions | ✅ | ✅ | ❌ | ❌ |
| View own interventions | ✅ | ✅ | ✅ | ✅ |
| Create intervention | ✅ | ✅ | ❌ | ✅ |
| Assign technician | ✅ | ✅ | ❌ | ❌ |
| Update status | ✅ | ✅ | ✅¹ | ❌ |
| Update details | ✅ | ✅ | ✅¹ | ❌ |
| Delete intervention | ✅ | ✅ | ❌ | ❌ |
| **Equipment** | | | | |
| View all equipment | ✅ | ✅ | ✅ | ❌ |
| View own equipment | ✅ | ✅ | ✅ | ✅ |
| Create equipment | ✅ | ✅ | ❌ | ❌ |
| Update equipment | ✅ | ✅ | ✅² | ❌ |
| Delete equipment | ✅ | ✅ | ❌ | ❌ |
| **Planning** | | | | |
| View all planning | ✅ | ✅ | ❌ | ❌ |
| View own planning | ✅ | ✅ | ✅ | ✅ |
| Create planning | ✅ | ✅ | ❌ | ❌ |
| Update planning | ✅ | ✅ | ✅³ | ❌ |
| Delete planning | ✅ | ✅ | ❌ | ❌ |
| **Documents** | | | | |
| Upload documents | ✅ | ✅ | ✅ | ✅⁴ |
| View all documents | ✅ | ✅ | ❌ | ❌ |
| View related documents | ✅ | ✅ | ✅ | ✅ |
| Delete documents | ✅ | ✅ | ✅¹ | ❌ |
| **Reports** | | | | |
| Generate system reports | ✅ | ✅ | ❌ | ❌ |
| View performance metrics | ✅ | ✅ | ❌ | ❌ |
| Export data | ✅ | ✅ | ❌ | ❌ |

**Notes:**
1. Only for assigned interventions
2. Only status updates during interventions
3. Only for assigned interventions
4. Only for own interventions

## Security Configuration

### JWT Configuration

**Environment Variables**
```bash
# JWT Security Settings
SECRET_KEY="your-256-bit-secret-key-here"  # CRITICAL: Change for production
ALGORITHM="HS256"                          # HMAC SHA-256
ACCESS_TOKEN_EXPIRE_MINUTES=60             # Token validity period

# Password Security
BCRYPT_ROUNDS=12                           # Cost factor for bcrypt hashing
```

**Token Security Best Practices**
```python
# app/core/config.py
class Settings(BaseSettings):
    SECRET_KEY: str = Field(default="insecure-test-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    @field_validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if v == "insecure-test-secret-key" and os.getenv("ENV") == "production":
            raise ValueError("SECRET_KEY must be changed for production")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
```

### Password Security

**Password Hashing with bcrypt**
```python
from passlib.context import CryptContext

# Configure password context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Cost factor (adjustable for performance/security balance)
)

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt with salt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password with salt
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against stored hash.
    
    Args:
        plain_password: User-provided password
        hashed_password: Stored password hash
        
    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)
```

**Password Policy Validation**
```python
import re
from typing import List

def validate_password_strength(password: str) -> List[str]:
    """
    Validate password meets security requirements.
    
    Returns:
        List[str]: List of validation errors (empty if valid)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character")
    
    # Check against common passwords
    common_passwords = ["password", "123456", "admin", "user"]
    if password.lower() in common_passwords:
        errors.append("Password is too common")
    
    return errors
```

## Security Headers & CORS

### CORS Configuration

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,  # Specific origins only
    allow_credentials=True,                      # Allow cookies/auth headers
    allow_methods=["*"],                        # All HTTP methods
    allow_headers=["*"],                        # All headers
)
```

**Environment-Specific CORS**
```bash
# Development
CORS_ALLOW_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Production
CORS_ALLOW_ORIGINS=["https://erp.your-domain.com"]

# Testing (NOT for production)
CORS_ALLOW_ORIGINS=["*"]
```

### Security Headers

**Security Middleware (Optional Enhancement)**
```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

# Add to FastAPI app
app.add_middleware(SecurityHeadersMiddleware)
```

## Authentication Endpoints

### Token Endpoints

**POST /api/v1/auth/token**
```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

email=user@example.com&password=userpassword
```

**Response**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**POST /api/v1/auth/login** (Username alternative)
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=userpassword
```

**GET /api/v1/auth/me** (Current user)
```http
GET /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**
```json
{
  "id": 123,
  "username": "johndoe",
  "email": "john.doe@example.com",
  "role": "technicien",
  "is_active": true,
  "created_at": "2025-01-27T10:00:00Z"
}
```

### Authentication Examples

**cURL Examples**
```bash
# Login with email
curl -X POST "http://localhost:8000/api/v1/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "email=admin@example.com&password=admin123"

# Use token for authenticated request
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/users/me"

# Access protected resource
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/interventions/"
```

**JavaScript/Frontend Example**
```javascript
// Login function
async function login(email, password) {
  const response = await fetch('/api/v1/auth/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      email: email,
      password: password
    })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data;
  } else {
    throw new Error('Login failed');
  }
}

// Authenticated API request
async function apiRequest(url, options = {}) {
  const token = localStorage.getItem('access_token');
  
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
}
```

## Security Testing

### Security Test Cases

**Authentication Tests**
```python
def test_login_valid_credentials():
    response = client.post("/api/v1/auth/token", data={
        "email": "test@example.com",
        "password": "validpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post("/api/v1/auth/token", data={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_access_protected_endpoint_without_token():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401

def test_access_with_invalid_token():
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 403
```

**RBAC Tests**
```python
def test_admin_can_access_admin_endpoint():
    token = create_test_token(role="admin")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 200

def test_technicien_cannot_access_admin_endpoint():
    token = create_test_token(role="technicien")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 403

def test_client_can_only_see_own_interventions():
    token = create_test_token(role="client", user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/interventions/", headers=headers)
    assert response.status_code == 200
    # Verify response only contains interventions for client_id = 1
```

## Security Monitoring & Auditing

### Audit Logging

**Security Event Logging**
```python
import logging
from datetime import datetime

security_logger = logging.getLogger("security")

def log_authentication_attempt(email: str, success: bool, ip_address: str):
    """Log authentication attempts for security monitoring."""
    event = {
        "event": "authentication_attempt",
        "email": email,
        "success": success,
        "ip_address": ip_address,
        "timestamp": datetime.utcnow().isoformat(),
        "user_agent": request.headers.get("User-Agent", "")
    }
    
    if success:
        security_logger.info("Authentication successful", extra=event)
    else:
        security_logger.warning("Authentication failed", extra=event)

def log_authorization_failure(user_id: int, endpoint: str, required_role: str):
    """Log authorization failures for security analysis."""
    security_logger.warning("Authorization failed", extra={
        "event": "authorization_failure",
        "user_id": user_id,
        "endpoint": endpoint,
        "required_role": required_role,
        "timestamp": datetime.utcnow().isoformat()
    })
```

### Security Best Practices

**Production Security Checklist**

- [ ] **Strong Secret Key**: Use cryptographically secure random key
- [ ] **HTTPS Only**: Force SSL/TLS in production
- [ ] **Token Expiration**: Set appropriate token lifetime
- [ ] **Rate Limiting**: Implement API rate limiting
- [ ] **Input Validation**: Validate all input data
- [ ] **SQL Injection Protection**: Use parameterized queries (ORM)
- [ ] **CORS Restrictions**: Limit allowed origins
- [ ] **Security Headers**: Implement security headers
- [ ] **Audit Logging**: Log security events
- [ ] **Regular Updates**: Keep dependencies updated
- [ ] **Password Policy**: Enforce strong passwords
- [ ] **Account Lockout**: Implement brute force protection

**Environment Security**
```bash
# Production environment variables
SECRET_KEY="$(openssl rand -base64 32)"  # Generate secure key
HTTPS_ONLY=true
SECURE_COOKIES=true
RATE_LIMIT_ENABLED=true
AUDIT_LOGGING=true
```

---

*This security documentation provides comprehensive coverage of authentication, authorization, and security best practices for the ERP MIF Maroc system. Regular security reviews and updates are recommended to maintain security posture.*