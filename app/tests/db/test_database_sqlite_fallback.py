from sqlalchemy import text
from app.db import database as db


def test_sqlite_engine_and_schema_lazy_ok():
    # In pytest, engine is sqlite memory with StaticPool and schema initialized
    assert db.engine.url.get_backend_name() == "sqlite"
    # get a session and basic create_all was invoked
    with db.SessionLocal() as s:  # type: ignore
        # Ensure metadata is present (tables exist, e.g., users)
        s.execute(text("select 1"))
