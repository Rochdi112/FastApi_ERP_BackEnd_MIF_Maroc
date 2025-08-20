---
title: "ERP MIF Maroc - Database Structure & Management"
path: "docs/00-FOUNDATION/DATABASE.md"
owner: "backend-team"
version: "0.1"
updated: "2025-01-27"
tags: ["database", "postgresql", "sqlalchemy", "schema", "performance"]
---

# ERP MIF Maroc - Database Structure & Management

## Database Overview

The ERP MIF Maroc system uses **PostgreSQL 16+** as the primary database with **SQLAlchemy 2.x** as the ORM layer. The database design follows Domain-Driven Design (DDD) principles with clear entity boundaries and optimized relationships for maintenance management workflows.

## Database Architecture

### Connection & Configuration

**SQLAlchemy Engine Configuration**
```python
# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,         # Verify connections before use
    pool_size=20,               # Connection pool size
    max_overflow=30,            # Maximum overflow connections
    pool_recycle=3600,          # Recycle connections hourly
    echo=False                  # Set to True for SQL logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

**Database URL Configuration**
```bash
# Development
DATABASE_URL=postgresql+psycopg2://erp_user:erp_pass@db:5432/erp_db

# Production
DATABASE_URL=postgresql+psycopg2://prod_user:secure_pass@prod-host:5432/erp_prod

# Testing
DATABASE_URL=sqlite:///:memory:
```

## Entity Relationship Model

### Complete ERD

```mermaid
erDiagram
    users {
        int id PK
        string username UK
        string email UK
        string hashed_password
        enum role
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    techniciens {
        int id PK
        int user_id FK,UK
        string specialite
        enum disponibilite
        string equipe
        string zone_geographique
        text notes_competences
        datetime date_embauche
    }
    
    clients {
        int id PK
        int user_id FK,UK
        string nom_entreprise
        string secteur_activite
        enum type_client
        enum niveau_service
        string adresse
        string ville
        string telephone
        string contact_principal
        text notes_commerciales
    }
    
    equipements {
        int id PK
        int client_id FK
        string nom
        string modele
        string fabricant
        string numero_serie
        date date_installation
        enum statut
        enum criticite
        string localisation
        text specifications_techniques
        datetime derniere_maintenance
    }
    
    interventions {
        int id PK
        int equipement_id FK
        int technicien_id FK
        int client_id FK
        enum type_intervention
        enum statut
        enum priorite
        boolean urgence
        string titre
        text description
        text diagnostic
        text solution
        datetime date_creation
        datetime date_planifiee
        datetime date_debut
        datetime date_fin
        decimal duree_estimee
        decimal duree_reelle
        decimal cout_estime
        decimal cout_reel
    }
    
    planning {
        int id PK
        int intervention_id FK,UK
        datetime date_debut
        datetime date_fin
        string créneau
        text notes_planning
        boolean confirme
        datetime date_creation
        datetime date_modification
    }
    
    documents {
        int id PK
        int intervention_id FK
        string nom_fichier
        string chemin
        string type_document
        int taille
        datetime date_upload
        int uploaded_by FK
    }
    
    notifications {
        int id PK
        int user_id FK
        string titre
        text message
        enum type_notification
        boolean lu
        datetime date_envoi
        datetime date_lu
    }
    
    competences {
        int id PK
        string nom
        string description
        enum niveau_requis
        string certification
    }
    
    historiques_interventions {
        int id PK
        int intervention_id FK
        int user_id FK
        enum action
        text description
        json ancienne_valeur
        json nouvelle_valeur
        datetime horodatage
    }
    
    contrats {
        int id PK
        int client_id FK
        string numero_contrat
        enum type_contrat
        enum statut
        date date_debut
        date date_fin
        decimal montant
        text conditions
    }
    
    pieces_detachees {
        int id PK
        string reference
        string nom
        string description
        decimal prix_unitaire
        int stock_actuel
        int stock_minimum
        string fournisseur
    }
    
    mouvements_stock {
        int id PK
        int piece_id FK
        int intervention_id FK
        int user_id FK
        enum type_mouvement
        int quantite
        decimal prix_unitaire
        datetime date_mouvement
        text commentaire
    }
    
    reports {
        int id PK
        string nom
        enum type_report
        enum format
        json parametres
        datetime date_generation
        int generated_by FK
        string chemin_fichier
    }
    
    %% Relations principales
    users ||--o{ techniciens : "1:0..1"
    users ||--o{ clients : "1:0..1"
    users ||--o{ notifications : "1:many"
    users ||--o{ historiques_interventions : "1:many"
    users ||--o{ documents : uploads
    users ||--o{ mouvements_stock : performs
    users ||--o{ reports : generates
    
    techniciens ||--o{ interventions : performs
    techniciens }o--o{ competences : has
    
    clients ||--o{ equipements : owns
    clients ||--o{ contrats : has
    clients ||--o{ interventions : requests
    
    equipements ||--o{ interventions : requires
    
    interventions ||--o{ planning : scheduled_in
    interventions ||--o{ documents : documented_by
    interventions ||--o{ historiques_interventions : tracked_by
    interventions ||--o{ mouvements_stock : consumes
    
    pieces_detachees ||--o{ mouvements_stock : moved
    
    contrats ||--o{ interventions : covers
```

## Core Database Tables

### User Management Tables

#### users
**Purpose**: Central authentication and user management
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX idx_user_email_active ON users(email, is_active);
CREATE INDEX idx_user_username_role ON users(username, role);
CREATE INDEX idx_user_role_active ON users(role, is_active);
CREATE INDEX idx_user_created_role ON users(created_at, role);
```

**User Roles Enum**:
```sql
CREATE TYPE user_role AS ENUM ('admin', 'responsable', 'technicien', 'client');
```

#### techniciens
**Purpose**: Technician profiles and competencies
```sql
CREATE TABLE techniciens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    specialite VARCHAR(100),
    disponibilite disponibilite_technicien DEFAULT 'disponible',
    equipe VARCHAR(100),
    zone_geographique VARCHAR(100),
    notes_competences TEXT,
    date_embauche DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE disponibilite_technicien AS ENUM (
    'disponible', 'occupe', 'conge', 'formation', 'indisponible'
);

-- Performance indexes
CREATE INDEX idx_technicien_disponibilite ON techniciens(disponibilite);
CREATE INDEX idx_technicien_equipe_zone ON techniciens(equipe, zone_geographique);
```

#### clients
**Purpose**: Client organizations and commercial relationships
```sql
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nom_entreprise VARCHAR(255) NOT NULL,
    secteur_activite VARCHAR(100),
    type_client type_client_enum DEFAULT 'standard',
    niveau_service niveau_service_enum DEFAULT 'standard',
    adresse TEXT,
    ville VARCHAR(100),
    code_postal VARCHAR(20),
    telephone VARCHAR(50),
    email_commercial VARCHAR(255),
    contact_principal VARCHAR(255),
    notes_commerciales TEXT,
    instructions_particulieres TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE type_client_enum AS ENUM ('premium', 'standard', 'basic');
CREATE TYPE niveau_service_enum AS ENUM ('platinum', 'gold', 'standard', 'basic');

-- Performance indexes
CREATE INDEX idx_client_type_niveau ON clients(type_client, niveau_service);
CREATE INDEX idx_client_ville_secteur ON clients(ville, secteur_activite);
```

### Equipment & Assets Tables

#### equipements
**Purpose**: Equipment inventory and asset management
```sql
CREATE TABLE equipements (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    nom VARCHAR(255) NOT NULL,
    modele VARCHAR(100),
    fabricant VARCHAR(100),
    numero_serie VARCHAR(100) UNIQUE,
    date_installation DATE,
    statut statut_equipement DEFAULT 'operationnel',
    criticite criticite_equipement DEFAULT 'normale',
    localisation VARCHAR(255),
    specifications_techniques TEXT,
    manuel_utilisation TEXT,
    derniere_maintenance TIMESTAMP,
    prochaine_maintenance DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE statut_equipement AS ENUM (
    'operationnel', 'maintenance', 'panne', 'retire'
);

CREATE TYPE criticite_equipement AS ENUM (
    'critique', 'haute', 'normale', 'basse'
);

-- Performance indexes
CREATE INDEX idx_equipement_client_statut ON equipements(client_id, statut);
CREATE INDEX idx_equipement_criticite_maintenance ON equipements(criticite, prochaine_maintenance);
CREATE INDEX idx_equipement_numero_serie ON equipements(numero_serie);
```

### Intervention Management Tables

#### interventions
**Purpose**: Core maintenance intervention management
```sql
CREATE TABLE interventions (
    id SERIAL PRIMARY KEY,
    equipement_id INTEGER NOT NULL REFERENCES equipements(id) ON DELETE CASCADE,
    technicien_id INTEGER REFERENCES techniciens(id) ON DELETE SET NULL,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    type_intervention intervention_type NOT NULL,
    statut statut_intervention DEFAULT 'ouverte',
    priorite priorite_intervention DEFAULT 'normale',
    urgence BOOLEAN DEFAULT FALSE,
    titre VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    diagnostic TEXT,
    solution TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_planifiee TIMESTAMP,
    date_debut TIMESTAMP,
    date_fin TIMESTAMP,
    duree_estimee DECIMAL(5,2), -- in hours
    duree_reelle DECIMAL(5,2),  -- in hours
    cout_estime DECIMAL(10,2),
    cout_reel DECIMAL(10,2),
    notes_techniques TEXT,
    satisfaction_client INTEGER CHECK (satisfaction_client BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE intervention_type AS ENUM (
    'corrective', 'preventive', 'ameliorative', 'diagnostic'
);

CREATE TYPE statut_intervention AS ENUM (
    'ouverte', 'affectee', 'en_cours', 'en_attente', 'cloturee', 'annulee', 'archivee'
);

CREATE TYPE priorite_intervention AS ENUM (
    'urgente', 'haute', 'normale', 'basse', 'programmee'
);

-- Performance indexes
CREATE INDEX idx_intervention_statut_date ON interventions(statut, date_creation);
CREATE INDEX idx_intervention_technicien_statut ON interventions(technicien_id, statut);
CREATE INDEX idx_intervention_equipement_date ON interventions(equipement_id, date_creation);
CREATE INDEX idx_intervention_client_type ON interventions(client_id, type_intervention);
CREATE INDEX idx_intervention_priorite_urgence ON interventions(priorite, urgence);
```

#### planning
**Purpose**: Intervention scheduling and calendar management
```sql
CREATE TABLE planning (
    id SERIAL PRIMARY KEY,
    intervention_id INTEGER UNIQUE NOT NULL REFERENCES interventions(id) ON DELETE CASCADE,
    date_debut TIMESTAMP NOT NULL,
    date_fin TIMESTAMP NOT NULL,
    creneau VARCHAR(50), -- "08:00-12:00", "14:00-18:00", etc.
    notes_planning TEXT,
    confirme BOOLEAN DEFAULT FALSE,
    rappel_envoye BOOLEAN DEFAULT FALSE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT planning_dates_valid CHECK (date_fin > date_debut)
);

-- Performance indexes
CREATE INDEX idx_planning_dates ON planning(date_debut, date_fin);
CREATE INDEX idx_planning_intervention ON planning(intervention_id);
```

### Document & Communication Tables

#### documents
**Purpose**: File uploads and document management
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    intervention_id INTEGER REFERENCES interventions(id) ON DELETE CASCADE,
    nom_fichier VARCHAR(255) NOT NULL,
    chemin VARCHAR(500) NOT NULL,
    type_document VARCHAR(50), -- "photo", "rapport", "manuel", "certificat"
    taille INTEGER, -- file size in bytes
    description TEXT,
    date_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Performance indexes
CREATE INDEX idx_document_intervention ON documents(intervention_id);
CREATE INDEX idx_document_type_date ON documents(type_document, date_upload);
```

#### notifications
**Purpose**: Real-time messaging and alerts
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    titre VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type_notification type_notification_enum DEFAULT 'info',
    lu BOOLEAN DEFAULT FALSE,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_lu TIMESTAMP,
    intervention_id INTEGER REFERENCES interventions(id) ON DELETE SET NULL,
    metadata JSONB -- Additional notification data
);

CREATE TYPE type_notification_enum AS ENUM (
    'info', 'warning', 'error', 'success', 'intervention', 'planning'
);

-- Performance indexes
CREATE INDEX idx_notification_user_lu ON notifications(user_id, lu);
CREATE INDEX idx_notification_date_type ON notifications(date_envoi, type_notification);
```

### Audit & History Tables

#### historiques_interventions
**Purpose**: Complete audit trail for interventions
```sql
CREATE TABLE historiques_interventions (
    id SERIAL PRIMARY KEY,
    intervention_id INTEGER NOT NULL REFERENCES interventions(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action action_historique NOT NULL,
    description TEXT NOT NULL,
    ancienne_valeur JSONB,
    nouvelle_valeur JSONB,
    horodatage TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    adresse_ip INET,
    user_agent TEXT
);

CREATE TYPE action_historique AS ENUM (
    'creation', 'modification', 'affectation', 'changement_statut', 
    'debut_intervention', 'fin_intervention', 'ajout_commentaire',
    'upload_document', 'planification', 'annulation'
);

-- Performance indexes
CREATE INDEX idx_historique_intervention_date ON historiques_interventions(intervention_id, horodatage);
CREATE INDEX idx_historique_user_action ON historiques_interventions(user_id, action);
```

## Database Performance Optimization

### Indexing Strategy

**Primary Indexes (Automatically Created)**
- Primary keys on all tables
- Unique constraints on email, username, numero_serie

**Composite Indexes for Common Queries**
```sql
-- User authentication and role queries
CREATE INDEX idx_user_email_active ON users(email, is_active);
CREATE INDEX idx_user_role_active ON users(role, is_active);

-- Intervention status and assignment queries
CREATE INDEX idx_intervention_statut_date ON interventions(statut, date_creation);
CREATE INDEX idx_intervention_technicien_statut ON interventions(technicien_id, statut);

-- Equipment management queries
CREATE INDEX idx_equipement_client_statut ON equipements(client_id, statut);
CREATE INDEX idx_equipement_criticite_maintenance ON equipements(criticite, prochaine_maintenance);

-- Planning and scheduling queries
CREATE INDEX idx_planning_dates ON planning(date_debut, date_fin);

-- Notification filtering
CREATE INDEX idx_notification_user_lu ON notifications(user_id, lu);
```

**Partial Indexes for Specific Conditions**
```sql
-- Only index active users
CREATE INDEX idx_active_users ON users(role) WHERE is_active = TRUE;

-- Only index open interventions
CREATE INDEX idx_open_interventions ON interventions(priorite, date_creation) 
WHERE statut IN ('ouverte', 'affectee', 'en_cours');

-- Only index unread notifications
CREATE INDEX idx_unread_notifications ON notifications(user_id, date_envoi) 
WHERE lu = FALSE;
```

### Query Optimization

**Connection Pooling Configuration**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Base connection pool size
    max_overflow=30,        # Additional connections under load
    pool_pre_ping=True,     # Validate connections before use
    pool_recycle=3600,      # Recycle connections every hour
    echo=False              # Disable SQL logging in production
)
```

**Lazy Loading Strategies**
```python
# For large collections - use dynamic loading
interventions = relationship(
    "Intervention", 
    back_populates="client",
    lazy="dynamic",  # Load as query object, not list
    order_by="desc(Intervention.date_creation)"
)

# For single objects - use select loading
equipement = relationship(
    "Equipement", 
    back_populates="interventions",
    lazy="select"  # Load immediately with SELECT
)

# For rarely accessed data - use lazy loading
documents = relationship(
    "Document",
    back_populates="intervention",
    lazy="select"  # Load when first accessed
)
```

## Database Maintenance

### Backup Strategy

**Daily Automated Backups**
```bash
#!/bin/bash
# Daily backup script
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="erp_db"

# Create backup with compression
pg_dump -h localhost -U erp_user -d $DB_NAME | gzip > $BACKUP_DIR/erp_backup_$DATE.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "erp_backup_*.sql.gz" -mtime +30 -delete
```

**Point-in-Time Recovery Setup**
```bash
# Enable WAL archiving in postgresql.conf
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
wal_level = replica
```

### Performance Monitoring

**Common Performance Queries**
```sql
-- Check database size
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
ORDER BY idx_scan ASC;

-- Check slow queries (requires pg_stat_statements)
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
```

### Data Retention Policies

**Automatic Cleanup Jobs**
```sql
-- Archive old closed interventions (older than 2 years)
UPDATE interventions 
SET statut = 'archivee' 
WHERE statut = 'cloturee' 
AND date_fin < CURRENT_DATE - INTERVAL '2 years';

-- Clean up old notifications (older than 6 months)
DELETE FROM notifications 
WHERE date_envoi < CURRENT_DATE - INTERVAL '6 months' 
AND lu = TRUE;

-- Clean up old audit logs (older than 3 years)
DELETE FROM historiques_interventions 
WHERE horodatage < CURRENT_DATE - INTERVAL '3 years';
```

## Database Security

### Access Control

**Role-Based Database Access**
```sql
-- Create application-specific database user
CREATE USER erp_app WITH PASSWORD 'secure_password';

-- Grant necessary permissions
GRANT CONNECT ON DATABASE erp_db TO erp_app;
GRANT USAGE ON SCHEMA public TO erp_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO erp_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO erp_app;

-- Create read-only user for reporting
CREATE USER erp_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE erp_db TO erp_readonly;
GRANT USAGE ON SCHEMA public TO erp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO erp_readonly;
```

**Row-Level Security (if needed)**
```sql
-- Enable RLS for client data isolation
ALTER TABLE interventions ENABLE ROW LEVEL SECURITY;

-- Policy to allow clients to see only their own interventions
CREATE POLICY client_interventions_policy ON interventions
    FOR ALL TO erp_app
    USING (client_id = current_setting('app.current_client_id')::INTEGER);
```

### Data Encryption

**Sensitive Data Handling**
```python
# Password hashing with bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

## Database Validation & Health Checks

### Data Integrity Checks

**Automated Validation Queries**
```sql
-- Check for orphaned records
SELECT 'orphaned_techniciens' as issue, COUNT(*) as count
FROM techniciens t 
LEFT JOIN users u ON t.user_id = u.id 
WHERE u.id IS NULL;

-- Check for invalid intervention states
SELECT 'invalid_intervention_dates' as issue, COUNT(*) as count
FROM interventions 
WHERE date_fin < date_debut;

-- Check for equipment without maintenance dates
SELECT 'equipment_no_maintenance' as issue, COUNT(*) as count
FROM equipements 
WHERE derniere_maintenance IS NULL 
AND statut = 'operationnel';
```

### Health Check Endpoint

**Database Connectivity Validation**
```python
@app.get("/health/database")
def database_health_check():
    try:
        db = next(get_db())
        # Simple query to verify connectivity
        result = db.execute(text("SELECT 1")).scalar()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

---

*This database documentation provides comprehensive coverage of the PostgreSQL schema design, performance optimization, and maintenance procedures for the ERP MIF Maroc system.*