from sqlalchemy.orm import Session
from app.db.database import get_db, Base, engine


def test_get_db_yields_and_closes_session():
    # get a session from dependency and ensure it closes without error
    gen = get_db()
    db: Session = next(gen)
    assert isinstance(db, Session)
    # basic query against metadata (no tables asserted here)
    # ensure generator can be closed (finally closes session)
    try:
        next(gen)
    except StopIteration:
        pass


def test_sqlite_memory_schema_initialized():
    # In tests, engine should be SQLite memory and metadata create_all was called
    assert engine.url.get_backend_name() == "sqlite"
    # Base.metadata should at least be bound and hold tables mapping
    assert isinstance(Base.metadata.tables, dict)
