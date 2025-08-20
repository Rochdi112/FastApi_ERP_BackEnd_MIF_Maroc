import importlib
from app.schemas.notification import NotificationCreate


def test_create_notification_triggers_email_outside_pytest(monkeypatch, db_session):
    svc = importlib.import_module("app.services.notification_service")
    from app.models.user import User, UserRole

    u = User(username="mailu", full_name="U", email="u@example.com", hashed_password="x", role=UserRole.technicien, is_active=True)
    db_session.add(u)
    db_session.commit()

    # Make environment think pytest is not running
    monkeypatch.delitem(svc.sys.modules, 'pytest', raising=False)

    calls = []
    def fake_send(email, notif):
        calls.append((email, notif))
        # Also raise to hit the except logging branch
        raise RuntimeError("smtp down")

    monkeypatch.setattr(svc, "send_email_notification", fake_send, raising=True)

    data = NotificationCreate(type="information", canal="email", contenu="Hello", user_id=u.id, intervention_id=1)
    notif = svc.create_notification(db_session, data)

    assert notif.id is not None
    assert calls and calls[0][0] == u.email
