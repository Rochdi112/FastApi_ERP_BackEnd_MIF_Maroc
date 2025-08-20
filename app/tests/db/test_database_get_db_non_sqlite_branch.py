import importlib


def test_get_db_non_sqlite_branch(monkeypatch):
    dbmod = importlib.import_module("app.db.database")

    class URLProxy:
        def __init__(self, real):
            self._real = real
        def get_backend_name(self):
            return "postgresql"

    monkeypatch.setattr(dbmod, "engine", type("E", (), {"url": URLProxy(dbmod.engine.url)})())

    gen = dbmod.get_db()
    s = next(gen)
    s.close()
    gen.close()
