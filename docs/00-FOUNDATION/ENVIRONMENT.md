---
title: "ERP MIF Maroc - Environment Setup & Configuration"
path: "docs/00-FOUNDATION/ENVIRONMENT.md"
owner: "backend-team"
version: "0.1"
updated: "2025-01-27"
tags: ["environment", "configuration", "setup", "docker", "development"]
---

# ERP MIF Maroc - Environment Setup & Configuration

## Environment Overview

The ERP MIF Maroc backend supports multiple deployment environments with flexible configuration management through environment variables and Docker Compose. This document covers setup procedures for development, testing, and production environments.

## Quick Start Guide

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Docker** | 20.0+ | Container runtime |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **Python** | 3.11+ | Runtime environment (local development) |
| **PostgreSQL** | 16+ | Database server (production) |
| **Git** | 2.30+ | Version control |

### Development Setup (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/Rochdi112/FastApi_ERP_BackEnd_MIF_Maroc.git
cd FastApi_ERP_BackEnd_MIF_Maroc

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Start with Docker Compose
docker-compose up -d

# 4. Verify deployment
curl http://localhost:8000/health
# Expected: {"status": "ok"}

# 5. Access documentation
open http://localhost:8000/docs
```

## Environment Configuration

### Configuration Files

| File | Purpose | Environment |
|------|---------|-------------|
| `.env.example` | Template with default values | All |
| `.env` | Local development configuration | Development |
| `.env.prod.example` | Production template | Production |
| `docker-compose.yml` | Development orchestration | Development |
| `alembic.ini` | Database migration settings | All |

### Environment Variables Reference

#### Core Application Settings

```bash
# Project Configuration
PROJECT_NAME="ERP Interventions"
API_V1_STR="/api/v1"

# Security Configuration
SECRET_KEY="your-secret-key-here"  # REQUIRED: Use strong random key
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS Configuration
CORS_ALLOW_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

#### Database Configuration

```bash
# PostgreSQL Settings
POSTGRES_USER="erp_user"
POSTGRES_PASSWORD="erp_pass"           # REQUIRED: Change for production
POSTGRES_DB="erp_db"
POSTGRES_HOST="db"                     # Use "localhost" for local PostgreSQL
POSTGRES_PORT=5432

# Auto-generated (do not edit manually)
# DATABASE_URL=postgresql+psycopg2://erp_user:erp_pass@db:5432/erp_db
```

#### File Storage Configuration

```bash
# Upload Directory
UPLOAD_DIRECTORY="app/static/uploads"  # Relative to project root

# Docker host ports
POSTGRES_HOST_PORT=5432
API_HOST_PORT=8000
```

#### Email & Notifications

```bash
# SMTP Configuration
SMTP_HOST="mailhog"                    # Use mailhog for development
SMTP_PORT=1025                         # 587 for production SMTP
SMTP_USER="user"
SMTP_PASSWORD="password"
EMAILS_FROM_EMAIL="no-reply@example.com"
```

#### Optional Features

```bash
# Background Tasks
ENABLE_SCHEDULER=false                 # Set to true to enable APScheduler

# Redis (if implemented)
REDIS_URL="redis://localhost:6379/0"
```

## Environment-Specific Configurations

### Development Environment

**Docker Compose Setup** (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "${API_HOST_PORT:-8000}:8000"
    environment:
      - DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:${POSTGRES_PORT}/${POSTGRES_DB}
    depends_on:
      - db
      - mailhog
    volumes:
      - ./app:/app/app:ro  # Hot reload for development
      - ./static:/app/static
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "${POSTGRES_HOST_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migration.sql:/docker-entrypoint-initdb.d/init.sql:ro
    restart: unless-stopped

  mailhog:
    image: mailhog/mailhog:latest
    ports:
      - "8025:8025"  # Web UI
      - "1025:1025"  # SMTP
    restart: unless-stopped

volumes:
  postgres_data:
```

**Development Features:**
- Hot reload with volume mounting
- MailHog for email testing
- PostgreSQL with persistent data
- Exposed ports for direct access

### Testing Environment

**Pytest Configuration** (`pytest.ini`)
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
asyncio_mode = strict
```

**Test Database Configuration:**
```python
# app/tests/conftest.py
@pytest.fixture
def test_db():
    # Use SQLite in-memory for test isolation
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    # ...
```

**Test Environment Variables:**
```bash
# Override for testing
DATABASE_URL="sqlite:///:memory:"
SECRET_KEY="test-secret-key"
ENABLE_SCHEDULER=false
SMTP_HOST="localhost"
```

### Production Environment

**Production Configuration Template** (`.env.prod.example`)
```bash
# Production Security - CHANGE ALL DEFAULTS
PROJECT_NAME="ERP Interventions - Production"
SECRET_KEY="CHANGE-TO-STRONG-RANDOM-KEY-256-BITS"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Production Database
POSTGRES_USER="erp_prod_user"
POSTGRES_PASSWORD="STRONG-DATABASE-PASSWORD"
POSTGRES_DB="erp_production"
POSTGRES_HOST="your-postgres-host.com"
POSTGRES_PORT=5432

# Production CORS (restrict to your frontend domain)
CORS_ALLOW_ORIGINS=["https://your-frontend-domain.com"]

# Production SMTP
SMTP_HOST="your-smtp-server.com"
SMTP_PORT=587
SMTP_USER="your-smtp-username"
SMTP_PASSWORD="your-smtp-password"
EMAILS_FROM_EMAIL="noreply@your-domain.com"

# Production File Storage
UPLOAD_DIRECTORY="/var/app/uploads"

# Enable background tasks
ENABLE_SCHEDULER=true
```

**Production Deployment Considerations:**
- Use managed PostgreSQL service
- Configure proper SSL/TLS certificates
- Set up proper logging and monitoring
- Use container orchestration (Kubernetes, Docker Swarm)
- Configure backup strategies

## Development Workflow

### Local Development Options

#### Option A: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head

# Run tests
docker-compose exec api python -m pytest

# Stop services
docker-compose down
```

#### Option B: Local Python Environment

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up local PostgreSQL
# Install PostgreSQL locally and create database

# 4. Configure environment
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/erp_db"
export SECRET_KEY="your-secret-key"

# 5. Run migrations
alembic upgrade head

# 6. Seed data (optional)
python -m app.seed.seed_data

# 7. Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option C: VS Code Tasks (Windows)

**VS Code Tasks Configuration** (`.vscode/tasks.json`)
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start API",
            "type": "shell",
            "command": "uvicorn",
            "args": ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "python",
            "args": ["-m", "pytest", "app/tests/", "-v"],
            "group": "test"
        }
    ]
}
```

## Database Environment Setup

### Migration Management

```bash
# Check current migration status
alembic current

# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Show migration history
alembic history --verbose
```

### Data Seeding

```bash
# Run seed data for development
python -m app.seed.seed_data

# Custom seeding for testing
python -c "
from app.seed.seed_data import create_test_data
from app.db.database import get_db
db = next(get_db())
create_test_data(db)
"
```

## Health Checks & Validation

### Environment Validation Script

```bash
# Validate environment configuration
python validate_env.py

# Expected output:
# ✅ All environment variables are properly configured
# ✅ Database connection successful
# ✅ SMTP configuration valid
```

### Health Check Endpoints

| Endpoint | Purpose | Expected Response |
|----------|---------|-------------------|
| `GET /` | Root endpoint | Project information |
| `GET /health` | Health status | `{"status": "ok"}` |
| `GET /docs` | API documentation | Swagger UI |
| `GET /redoc` | Alternative docs | ReDoc interface |

### Application Health Validation

```bash
# Test database connectivity
curl http://localhost:8000/health

# Test authentication flow
curl -X POST http://localhost:8000/api/v1/auth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "email=admin@example.com&password=admin123"

# Test RBAC protection
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/users/me
```

## Security Configuration

### JWT Secret Key Generation

```bash
# Generate secure secret key
python -c "
import secrets
print('SECRET_KEY=' + secrets.token_urlsafe(32))
"

# Alternative with openssl
openssl rand -base64 32
```

### CORS Configuration Examples

```bash
# Development (allow local frontend)
CORS_ALLOW_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Production (restrict to specific domains)
CORS_ALLOW_ORIGINS=["https://erp.your-domain.com","https://app.your-domain.com"]

# Testing (allow all - NOT for production)
CORS_ALLOW_ORIGINS=["*"]
```

## Troubleshooting Common Issues

### Database Connection Issues

**Problem**: `connection to server at "db" failed`
```bash
# Check PostgreSQL status
docker-compose ps db

# View database logs
docker-compose logs db

# Verify environment variables
docker-compose exec api env | grep POSTGRES
```

**Solution**: Ensure database service is running and environment variables match

### File Upload Issues

**Problem**: File uploads failing
```bash
# Check upload directory permissions
ls -la static/uploads/

# Create upload directory if missing
mkdir -p static/uploads
chmod 755 static/uploads
```

### Authentication Issues

**Problem**: JWT token validation failing
```bash
# Check secret key configuration
echo $SECRET_KEY

# Verify token format
python -c "
from jose import jwt
token = 'your-token-here'
print(jwt.get_unverified_claims(token))
"
```

### Performance Issues

**Problem**: Slow database queries
```bash
# Check database connections
docker-compose exec db psql -U erp_user -d erp_db -c "\dp"

# Analyze slow queries
docker-compose exec db psql -U erp_user -d erp_db -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;
"
```

## Environment Migration

### Development to Production Checklist

- [ ] Update all default passwords and secret keys
- [ ] Configure production CORS origins
- [ ] Set up managed PostgreSQL instance
- [ ] Configure production SMTP server
- [ ] Set up SSL/TLS certificates
- [ ] Configure proper logging levels
- [ ] Set up monitoring and alerting
- [ ] Implement backup strategies
- [ ] Test disaster recovery procedures
- [ ] Configure auto-scaling if needed

### Configuration Validation

```python
# Environment validation script
from app.core.config import settings

def validate_production_config():
    errors = []
    
    if settings.SECRET_KEY == "insecure-test-secret-key":
        errors.append("SECRET_KEY must be changed for production")
    
    if "localhost" in settings.CORS_ALLOW_ORIGINS:
        errors.append("CORS origins should not include localhost in production")
    
    if settings.POSTGRES_PASSWORD == "erp_pass":
        errors.append("Database password must be changed for production")
    
    return errors
```

---

*This environment documentation provides comprehensive setup instructions for all deployment scenarios. For specific deployment automation, refer to the CI/CD documentation.*