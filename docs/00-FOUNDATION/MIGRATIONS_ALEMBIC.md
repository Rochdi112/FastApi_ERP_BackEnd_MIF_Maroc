---
title: "ERP MIF Maroc - Alembic Migrations Guide"
path: "docs/00-FOUNDATION/MIGRATIONS_ALEMBIC.md"
owner: "backend-team"
version: "0.1"
updated: "2025-01-27"
tags: ["alembic", "migrations", "database", "schema", "versioning"]
---

# ERP MIF Maroc - Alembic Migrations Guide

## Migration Overview

The ERP MIF Maroc system uses **Alembic** for database schema versioning and migrations. Alembic provides a structured approach to evolving the database schema while maintaining data integrity and enabling rollbacks when necessary.

## Alembic Configuration

### Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `alembic.ini` | Main Alembic configuration | Project root |
| `env.py` | Migration environment setup | `app/db/migrations/env.py` |
| `script.py.mako` | Migration script template | `app/db/migrations/script.py.mako` |

### Alembic.ini Configuration

```ini
[alembic]
# Migration scripts location
script_location = app/db/migrations

# Database URL (can be overridden by environment variable)
sqlalchemy.url = postgresql+psycopg2://erp_user:erp_pass@db:5432/erp_db

# Migration file naming pattern
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d%%(second).2d_%%(slug)s

# Timezone for timestamps
timezone = UTC

# Truncate slug to reasonable length
truncate_slug_length = 40

# Output encoding
output_encoding = utf-8

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### Environment Configuration (env.py)

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Add project root to path for app imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base and all models for auto-detection
from app.db.database import Base
from app import models  # Imports all models

# Target metadata for autogenerate
target_metadata = Base.metadata

# Override database URL from environment
db_url_env = os.getenv("DATABASE_URL")
if db_url_env:
    config.set_main_option("sqlalchemy.url", db_url_env)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (without database connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,      # Compare column types
        compare_server_default=True,  # Compare default values
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with database connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# Run migrations based on context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Migration Commands

### Basic Migration Commands

```bash
# Check current migration status
alembic current

# Show migration history
alembic history --verbose

# Show pending migrations
alembic show head

# Create new migration (auto-generate from models)
alembic revision --autogenerate -m "Description of changes"

# Create empty migration (manual)
alembic revision -m "Custom migration description"

# Apply migrations to latest version
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Rollback to previous migration
alembic downgrade -1

# Rollback to specific migration
alembic downgrade <revision_id>

# Show SQL without executing
alembic upgrade head --sql

# Show differences between current DB and models
alembic diff
```

### Environment-Specific Commands

**Development Environment**
```bash
# Using Docker Compose
docker-compose exec api alembic current
docker-compose exec api alembic upgrade head
docker-compose exec api alembic revision --autogenerate -m "Add new feature"

# Using local environment
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/erp_db"
alembic upgrade head
```

**Testing Environment**
```bash
# Use SQLite for tests
export DATABASE_URL="sqlite:///./test.db"
alembic upgrade head

# Or use in-memory database
export DATABASE_URL="sqlite:///:memory:"
alembic upgrade head
```

**Production Environment**
```bash
# Always backup before production migrations
pg_dump -h prod-host -U prod_user -d erp_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Apply migrations
DATABASE_URL="postgresql+psycopg2://prod_user:prod_pass@prod-host:5432/erp_prod" \
alembic upgrade head
```

## Migration Workflow

### Development Workflow

```mermaid
flowchart TD
    A[Modify SQLAlchemy Models] --> B[Generate Migration]
    B --> C[Review Generated Migration]
    C --> D{Migration Correct?}
    D -->|No| E[Edit Migration Manually]
    D -->|Yes| F[Test Migration]
    E --> F
    F --> G[Apply to Development DB]
    G --> H[Run Tests]
    H --> I{Tests Pass?}
    I -->|No| J[Fix Issues]
    I -->|Yes| K[Commit Migration]
    J --> C
    K --> L[Deploy to Staging]
    L --> M[Deploy to Production]
```

### Step-by-Step Migration Process

**1. Modify Models**
```python
# Example: Add new column to interventions table
class Intervention(Base):
    __tablename__ = "interventions"
    
    # Existing columns...
    satisfaction_client = Column(Integer)  # New column
    notes_internes = Column(Text)          # New column
```

**2. Generate Migration**
```bash
alembic revision --autogenerate -m "Add satisfaction and internal notes to interventions"
```

**3. Review Generated Migration**
```python
"""Add satisfaction and internal notes to interventions

Revision ID: abc123def456
Revises: previous_revision_id
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('interventions', sa.Column('satisfaction_client', sa.Integer(), nullable=True))
    op.add_column('interventions', sa.Column('notes_internes', sa.Text(), nullable=True))
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('interventions', 'notes_internes')
    op.drop_column('interventions', 'satisfaction_client')
    # ### end Alembic commands ###
```

**4. Manual Migration Adjustments (if needed)**
```python
def upgrade() -> None:
    # Add columns
    op.add_column('interventions', sa.Column('satisfaction_client', sa.Integer(), nullable=True))
    op.add_column('interventions', sa.Column('notes_internes', sa.Text(), nullable=True))
    
    # Add constraint for satisfaction rating
    op.create_check_constraint(
        'ck_satisfaction_range',
        'interventions',
        'satisfaction_client >= 1 AND satisfaction_client <= 5'
    )
    
    # Create index for performance
    op.create_index('idx_intervention_satisfaction', 'interventions', ['satisfaction_client'])

def downgrade() -> None:
    # Drop in reverse order
    op.drop_index('idx_intervention_satisfaction', 'interventions')
    op.drop_constraint('ck_satisfaction_range', 'interventions')
    op.drop_column('interventions', 'notes_internes')
    op.drop_column('interventions', 'satisfaction_client')
```

## Common Migration Patterns

### Adding Columns

```python
def upgrade() -> None:
    # Add nullable column
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    
    # Add non-nullable column with default
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
```

### Modifying Columns

```python
def upgrade() -> None:
    # Change column type
    op.alter_column('users', 'phone', type_=sa.String(50))
    
    # Add NOT NULL constraint
    op.alter_column('users', 'email', nullable=False)
    
    # Rename column
    op.alter_column('users', 'old_name', new_column_name='new_name')
```

### Adding Indexes

```python
def upgrade() -> None:
    # Single column index
    op.create_index('idx_user_email', 'users', ['email'])
    
    # Composite index
    op.create_index('idx_intervention_status_date', 'interventions', ['statut', 'date_creation'])
    
    # Unique index
    op.create_index('idx_user_username_unique', 'users', ['username'], unique=True)
    
    # Partial index
    op.execute("""
        CREATE INDEX idx_active_users ON users(role) WHERE is_active = TRUE
    """)
```

### Adding Foreign Key Constraints

```python
def upgrade() -> None:
    # Add foreign key
    op.create_foreign_key(
        'fk_intervention_technicien',
        'interventions', 'techniciens',
        ['technicien_id'], ['id'],
        ondelete='SET NULL'
    )
```

### Data Migrations

```python
def upgrade() -> None:
    # Schema change
    op.add_column('users', sa.Column('full_name', sa.String(255), nullable=True))
    
    # Data migration
    connection = op.get_bind()
    connection.execute("""
        UPDATE users 
        SET full_name = CONCAT(first_name, ' ', last_name)
        WHERE first_name IS NOT NULL AND last_name IS NOT NULL
    """)
    
    # Remove old columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
```

## Migration History

### Current Migration Files

| File | Revision | Description | Date |
|------|----------|-------------|------|
| `bb94288d88f3_initial_full_migration_from_models.py` | bb94288d88f3 | Initial schema creation | 2025-01-01 |
| `5bd306f33b2b_add_username_to_user_model.py` | 5bd306f33b2b | Add username field to users | 2025-01-15 |
| `e576b04091b6_add_is_active_column_to_users.py` | e576b04091b6 | Add is_active flag to users | 2025-01-20 |
| `df44b376bc8a_ensure_all_timestamps_columns_exist.py` | df44b376bc8a | Ensure all tables have timestamps | 2025-01-22 |
| `2a1f3c8d7c1b_create_clients_and_contrats.py` | 2a1f3c8d7c1b | Add clients and contracts tables | 2025-01-25 |

### Migration Dependency Tree

```mermaid
graph TD
    A[bb94288d88f3<br/>Initial Schema] --> B[5bd306f33b2b<br/>Add Username]
    B --> C[e576b04091b6<br/>Add is_active]
    C --> D[df44b376bc8a<br/>Ensure Timestamps]
    D --> E[2a1f3c8d7c1b<br/>Clients & Contracts]
    E --> F[HEAD<br/>Current State]
```

## Testing Migrations

### Migration Testing Strategy

**1. Test in Development**
```bash
# Reset to clean state
alembic downgrade base
alembic upgrade head

# Verify schema
python -c "
from app.db.database import engine
from sqlalchemy import inspect
insp = inspect(engine)
print('Tables:', insp.get_table_names())
"
```

**2. Test Forward and Backward**
```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test upgrade again
alembic upgrade head
```

**3. Test with Data**
```python
# Create test migration script
def test_migration_with_data():
    # Apply migration
    alembic.command.upgrade(alembic_cfg, "head")
    
    # Insert test data
    db = next(get_db())
    user = User(username="test", email="test@example.com")
    db.add(user)
    db.commit()
    
    # Verify data integrity
    assert db.query(User).count() == 1
```

### Automated Migration Testing

**Test Migration in CI/CD**
```bash
#!/bin/bash
# Test migrations in CI pipeline

# Start test database
docker run -d --name test-postgres \
  -e POSTGRES_DB=test_erp \
  -e POSTGRES_USER=test_user \
  -e POSTGRES_PASSWORD=test_pass \
  -p 5433:5432 postgres:16

# Wait for database
sleep 10

# Run migrations
export DATABASE_URL="postgresql+psycopg2://test_user:test_pass@localhost:5433/test_erp"
alembic upgrade head

# Run tests
python -m pytest app/tests/db/test_migrations.py

# Cleanup
docker rm -f test-postgres
```

## Troubleshooting Migrations

### Common Issues and Solutions

**1. Migration Conflict**
```bash
# Error: Multiple heads found
alembic heads

# Solution: Merge migrations
alembic merge -m "Merge migrations" head1 head2
```

**2. Schema Out of Sync**
```bash
# Error: Table already exists
# Solution: Mark migration as applied without running
alembic stamp head
```

**3. Failed Migration**
```bash
# Error during migration
# Check current state
alembic current

# Manually fix database if needed
psql -d erp_db -c "ALTER TABLE ..."

# Mark as successful
alembic stamp <revision_id>
```

**4. Data Loss Prevention**
```python
# Always backup before destructive operations
def upgrade() -> None:
    # Create backup table before dropping column
    op.execute("""
        CREATE TABLE users_backup AS 
        SELECT * FROM users
    """)
    
    # Perform migration
    op.drop_column('users', 'old_column')
    
    # Note: Cleanup backup table manually after verification
```

### Migration Best Practices

**1. Always Review Generated Migrations**
- Check for unintended changes
- Verify column types and constraints
- Ensure proper indexes are created

**2. Test Thoroughly**
- Test both upgrade and downgrade paths
- Test with real data
- Verify application functionality

**3. Use Descriptive Names**
```bash
# Good
alembic revision --autogenerate -m "Add user email verification system"

# Bad
alembic revision --autogenerate -m "Update users"
```

**4. Handle Data Carefully**
```python
# Good: Safe data migration
def upgrade() -> None:
    # Add new column
    op.add_column('users', sa.Column('status', sa.String(20), nullable=True))
    
    # Set default value for existing records
    op.execute("UPDATE users SET status = 'active' WHERE status IS NULL")
    
    # Make column non-nullable
    op.alter_column('users', 'status', nullable=False)

# Bad: Direct constraint addition
def upgrade() -> None:
    op.add_column('users', sa.Column('status', sa.String(20), nullable=False))
```

**5. Document Complex Migrations**
```python
def upgrade() -> None:
    """
    Migrate user roles from simple string to enum type.
    
    This migration:
    1. Creates new role_enum type
    2. Adds new role_new column
    3. Migrates data from old role column
    4. Drops old column and renames new one
    
    Data mapping:
    - 'admin' -> 'admin'
    - 'user' -> 'client'
    - 'tech' -> 'technicien'
    """
    # Implementation...
```

## Production Migration Checklist

### Pre-Migration Checklist

- [ ] **Backup created** and verified
- [ ] **Migration tested** in staging environment
- [ ] **Rollback plan** prepared and tested
- [ ] **Downtime window** scheduled (if required)
- [ ] **Application compatibility** verified
- [ ] **Monitoring** prepared for post-migration

### Migration Execution

```bash
# 1. Create backup
pg_dump -h prod-host -U prod_user erp_prod > migration_backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Check current state
alembic current

# 3. Show what will be applied
alembic upgrade head --sql

# 4. Apply migration
alembic upgrade head

# 5. Verify application health
curl http://api-host/health
```

### Post-Migration Validation

```sql
-- Verify table structure
\d+ interventions

-- Check data integrity
SELECT COUNT(*) FROM users WHERE email IS NULL;

-- Verify constraints
SELECT conname FROM pg_constraint WHERE conrelid = 'users'::regclass;

-- Check indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'interventions';
```

---

*This migration guide provides comprehensive coverage of Alembic usage, migration patterns, and best practices for the ERP MIF Maroc database schema evolution.*