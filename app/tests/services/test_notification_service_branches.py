import importlib
from fastapi import HTTPException
import types

from app.schemas.notification import NotificationCreate


def test_send_email_notification_missing_template(monkeypatch):
    # Build a fake Notification object minimal shape
    notif = types.SimpleNamespace(
        type_notification=types.SimpleNamespace(value="inconnue"),
        contenu="X",
    )

    svc = importlib.import_module("app.services.notification_service")

    # Force SMTP settings to something harmless
    monkeypatch.setattr(svc.settings, "SMTP_HOST", "localhost", raising=True)
    monkeypatch.setattr(svc.settings, "SMTP_PORT", 25, raising=True)
    monkeypatch.setattr(svc.settings, "SMTP_USER", "user", raising=True)
    monkeypatch.setattr(svc.settings, "SMTP_PASSWORD", "pwd", raising=True)
    monkeypatch.setattr(svc.settings, "EMAILS_FROM_EMAIL", "no-reply@example.com", raising=True)

    # Expect HTTPException 500 because template doesn't exist for type 'inconnue'
    try:
        svc.send_email_notification("to@example.com", notif)
        assert False, "Expected HTTPException"
    except HTTPException as e:
        assert e.status_code == 500
        assert "Template" in e.detail


def test_notification_create_email_path_skips_in_pytest(monkeypatch, db_session):
    # Create a user to target
    from app.models.user import User, UserRole
    u = User(username="u1", full_name="U", email="u1@example.com", hashed_password="x", role=UserRole.technicien, is_active=True)
    db_session.add(u)
    db_session.commit()

    svc = importlib.import_module("app.services.notification_service")

    data = NotificationCreate(type="information", canal="email", contenu="Hello", user_id=u.id, intervention_id=123)

    # Patch SMTP to ensure if called it's controlled, but code should skip in pytest
    calls = []
    def fake_send(email, notif):
        calls.append((email, notif))
    monkeypatch.setattr(svc, "send_email_notification", fake_send, raising=True)

    notif = svc.create_notification(db_session, data)
    assert notif.id is not None
    # In pytest environment, email path shouldn't call send_email_notification
    assert calls == []
