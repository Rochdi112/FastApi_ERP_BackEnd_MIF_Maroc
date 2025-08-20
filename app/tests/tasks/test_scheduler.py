import types
from app.tasks.scheduler import run_planning_generation


def test_scheduler_runs_without_crash(monkeypatch):
    calls = {"n": 0}
    def fake_create(db, plan):
        calls["n"] += 1
    # monkeypatch the function imported in scheduler module
    import app.tasks.scheduler as sched
    monkeypatch.setattr(sched, "create_intervention_from_planning", fake_create)
    # also monkeypatch SessionLocal to return dummy with expected API
    class DummySess:
        def query(self, model):
            return types.SimpleNamespace(filter=lambda *a, **k: types.SimpleNamespace(all=lambda: []))
        def close(self):
            pass
    monkeypatch.setattr(sched, "SessionLocal", lambda: DummySess())
    run_planning_generation()
    assert calls["n"] >= 0
