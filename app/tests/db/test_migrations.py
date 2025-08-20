import os
import tempfile
import types
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.db.database import Base


def test_alembic_upgrade_head_on_temp_db(tmp_path):
    # Create a temp PostgreSQL-like URL using SQLite for test isolation
    # Alembic config requires sqlalchemy.url; override at runtime
    cfg = Config("alembic.ini")
    # Use SQLite file DB for visibility after upgrade
    db_path = tmp_path / "alembic_test.sqlite"
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    # Run upgrade head
    command.upgrade(cfg, "head")

    # Verify tables exist - require a representative subset to avoid coupling to all models
    eng = create_engine(f"sqlite:///{db_path}")
    insp = inspect(eng)
    tables = set(insp.get_table_names())
    required = {
        'alembic_version',
        'users',
        'equipements',
        'interventions',
        'documents',
        'historiques_interventions',
        'notifications',
    }
    missing = required - tables
    assert not missing, f"Missing tables after upgrade: {sorted(missing)}; have={sorted(tables)}"
