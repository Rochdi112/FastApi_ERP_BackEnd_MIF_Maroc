import contextlib

import importlib


def test_get_db_schema_init_error_branch(monkeypatch):
    # Import module fresh
    dbmod = importlib.import_module("app.db.database")

    # Force schema not initialized and make create_all raise to hit except branch
    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(dbmod.Base.metadata, "create_all", boom, raising=True)
    dbmod._schema_initialized = False

    gen = dbmod.get_db()
    # Should not raise thanks to internal try/except; we still need to advance the generator
    session = next(gen)
    # Clean up
    session.close()
    with contextlib.suppress(Exception):
        gen.close()


def test_sessionlocal_schema_error_branch(monkeypatch):
    dbmod = importlib.import_module("app.db.database")

    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(dbmod.Base.metadata, "create_all", boom, raising=True)
    dbmod._schema_initialized = False

    # Should not raise due to internal try/except
    s = dbmod.SessionLocal()
    s.close()
