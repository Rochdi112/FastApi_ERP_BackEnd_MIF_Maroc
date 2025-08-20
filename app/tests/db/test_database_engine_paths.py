import importlib
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool


def test_create_default_engine_fallback_without_pytest(monkeypatch):
    import app.db.database as dbmod
    # simulate non-pytest context for this module only
    fake_modules = dict(dbmod.sys.modules)
    fake_modules.pop('pytest', None)
    monkeypatch.setattr(dbmod, 'DATABASE_URL', 'postgresql+psycopg2://u:p@localhost/x', raising=False)
    monkeypatch.setattr(dbmod, 'sys', type('S', (), {'modules': fake_modules}))
    eng = dbmod._create_default_engine()
    assert eng.url.get_backend_name() == 'sqlite'


def test_get_db_schema_init_and_sessionlocal(monkeypatch):
    import app.db.database as dbmod
    # Use isolated in-memory engine
    eng = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    monkeypatch.setattr(dbmod, 'engine', eng, raising=False)
    # mark not initialized to force create_all path
    monkeypatch.setattr(dbmod, '_schema_initialized', False, raising=False)

    # get_db should create schema then yield a session
    gen = dbmod.get_db()
    session = next(gen)
    try:
        # simple smoke: metadata has tables
        assert len(dbmod.Base.metadata.tables) > 0
    finally:
        try:
            next(gen)
        except StopIteration:
            pass

    # SessionLocal should also ensure schema when sqlite
    dbmod._schema_initialized = False
    sess2 = dbmod.SessionLocal()
    sess2.close()
    assert dbmod._schema_initialized is True
