import smtplib
import types
from app.models.user import User, UserRole
from app.models.intervention import Intervention
from app.core.security import get_password_hash


def _ensure_admin_headers(client, db_session):
    admin = db_session.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            username="admin",
            full_name="Admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            role=UserRole.admin,
            is_active=True,
        )
        db_session.add(admin)
        db_session.commit()
    r = client.post("/api/v1/auth/token", data={"email": "admin@example.com", "password": "admin"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _ensure_intervention(db_session):
    intr = db_session.query(Intervention).first()
    if not intr:
        intr = Intervention(titre="notif test", type_intervention="corrective", statut="ouverte", urgence=False)
        db_session.add(intr)
        db_session.commit()
        db_session.refresh(intr)
    return intr


def test_notification_delete_404(client, db_session):
    headers = _ensure_admin_headers(client, db_session)
    intr = _ensure_intervention(db_session)
    # create one notification
    payload = {"type": "information", "canal": "log", "contenu": "m", "user_id": db_session.query(User).first().id, "intervention_id": intr.id}
    r = client.post("/api/v1/notifications/", json=payload, headers=headers)
    assert r.status_code in (200, 201), r.text
    notif_id = r.json()["id"]
    d1 = client.delete(f"/api/v1/notifications/{notif_id}", headers=headers)
    assert d1.status_code in (200, 204)
    d2 = client.delete(f"/api/v1/notifications/{notif_id}", headers=headers)
    assert d2.status_code == 404


def test_notification_smtp_best_effort(client, db_session, monkeypatch):
    headers = _ensure_admin_headers(client, db_session)
    intr = _ensure_intervention(db_session)

    def boom(*a, **k):
        raise smtplib.SMTPException("fail")
    monkeypatch.setattr(smtplib, "SMTP", lambda *a, **k: types.SimpleNamespace(starttls=lambda: None, login=lambda *a, **k: None, sendmail=boom, quit=lambda: None))

    user = db_session.query(User).first()
    payload = {"type":"information","canal":"email","contenu":"m","user_id":user.id,"intervention_id":intr.id}
    r = client.post("/api/v1/notifications/", json=payload, headers=headers)
    assert r.status_code in (200,201)
