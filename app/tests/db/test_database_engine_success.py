import types


def test_create_default_engine_success_branch(monkeypatch):
    import app.db.database as dbmod

    class FakeConn:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeEngine:
        class _URL:
            @staticmethod
            def get_backend_name():
                return 'postgresql'
        url = _URL()
        def connect(self):
            return FakeConn()

    # Remove pytest key to force non-pytest branch
    fake_modules = dict(dbmod.sys.modules)
    fake_modules.pop('pytest', None)
    monkeypatch.setattr(dbmod, 'sys', types.SimpleNamespace(modules=fake_modules), raising=False)

    calls = {}
    def fake_create_engine(url):
        calls['url'] = url
        return FakeEngine()
    monkeypatch.setattr(dbmod, 'create_engine', fake_create_engine, raising=True)

    eng = dbmod._create_default_engine()
    assert isinstance(eng, FakeEngine)
    assert '://' in calls['url']
