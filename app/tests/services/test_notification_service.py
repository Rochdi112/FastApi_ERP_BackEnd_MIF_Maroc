import pytest
from sqlalchemy.orm import Session
from app.services.notification_service import create_notification, send_email_notification
from app.schemas.notification import NotificationCreate
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.models.intervention import Intervention, InterventionType


def _mk_user(db):
    u = User(username="u", full_name="U", email="u@ex.com", hashed_password=get_password_hash("x"), role=UserRole.client, is_active=True)
    db.add(u); db.commit(); db.refresh(u)
    return u

def _mk_intervention(db):
    it = Intervention(titre="t", description="d", type=InterventionType.corrective, urgence=False)
    db.add(it); db.commit(); db.refresh(it)
    return it


def test_create_notification_user_404(db_session: Session):
    with pytest.raises(Exception):
        create_notification(
            db_session,
            NotificationCreate(
                type="alerte",
                canal="email",
                contenu="x",
                user_id=9999,
                intervention_id=1,
            ),
        )


def test_create_notification_email_under_pytest_no_smtp(db_session: Session):
    u = _mk_user(db_session)
    it = _mk_intervention(db_session)
    n = create_notification(db_session, NotificationCreate(type="information", canal="email", contenu="x", user_id=u.id, intervention_id=it.id))
    assert n.user_id == u.id and n.canal == "email"


def test_send_email_template_missing(monkeypatch, db_session: Session):
    u = _mk_user(db_session)
    it = _mk_intervention(db_session)
    n = create_notification(db_session, NotificationCreate(type="alerte", canal="log", contenu="x", user_id=u.id, intervention_id=it.id))
    # monkeypatch env.get_template to raise TemplateNotFound
    from jinja2 import TemplateNotFound
    import app.services.notification_service as ns
    def raise_notfound(name):
        raise TemplateNotFound(name)
    monkeypatch.setattr(ns, "env", type("E", (), {"get_template": staticmethod(raise_notfound)}))
    with pytest.raises(Exception):
        send_email_notification(u.email, n)


def test_send_email_success_and_failure(monkeypatch, db_session: Session):
    u = _mk_user(db_session)
    it = _mk_intervention(db_session)
    n = create_notification(db_session, NotificationCreate(type="information", canal="log", contenu="hello", user_id=u.id, intervention_id=it.id))
    # Mock template env
    import app.services.notification_service as ns
    class DummyT:
        def render(self, **kw):
            return "<b>ok</b>"
    class DummyEnv:
        def get_template(self, name):
            return DummyT()
    monkeypatch.setattr(ns, "env", DummyEnv())
    # Mock SMTP
    class DummySMTP:
        def __init__(self, host, port): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def starttls(self): self._s = True
        def login(self, u, p): self._l = (u, p)
        def sendmail(self, a, b, c): self._m = (a, b, c)
    monkeypatch.setattr(ns, "smtplib", type("S", (), {"SMTP": DummySMTP}))
    send_email_notification(u.email, n)
    # Failure path
    class FailingSMTP(DummySMTP):
        def sendmail(self, *a, **k):
            raise RuntimeError("smtp down")
    monkeypatch.setattr(ns, "smtplib", type("S", (), {"SMTP": FailingSMTP}))
    with pytest.raises(Exception):
        send_email_notification(u.email, n)
