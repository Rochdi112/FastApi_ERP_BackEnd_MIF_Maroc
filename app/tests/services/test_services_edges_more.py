import io
import types
import pytest
from fastapi import UploadFile
from sqlalchemy.orm import Session

import app.services.document_service as ds
import app.services.notification_service as ns
from app.schemas.notification import NotificationCreate
from app.core.config import settings
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.models.intervention import Intervention, InterventionType
from app.services.intervention_service import update_statut_intervention
from app.models.intervention import StatutIntervention


def _mk_user(db):
    u = User(username="t", full_name="T", email="t@x.com", hashed_password=get_password_hash("x"), role=UserRole.technicien, is_active=True)
    db.add(u); db.commit(); db.refresh(u)
    return u


def _mk_intervention(db):
    it = Intervention(titre="t", description="d", type=InterventionType.corrective, urgence=False)
    db.add(it); db.commit(); db.refresh(it)
    return it


def test_document_io_disk_full(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "UPLOAD_DIRECTORY", str(tmp_path))
    up = UploadFile(filename="a.txt", file=io.BytesIO(b"x"))
    def boom(*a, **k):
        raise OSError("disk full")
    monkeypatch.setattr(ds, "open", boom, raising=False)
    with pytest.raises(Exception):
        ds.save_uploaded_file(up)


def test_smtp_connection_error(monkeypatch, db_session: Session):
    u = _mk_user(db_session)
    it = _mk_intervention(db_session)
    n = ns.create_notification(db_session, NotificationCreate(type="information", canal="log", contenu="x", user_id=u.id, intervention_id=it.id))

    class DummyT:  # template rendering ok
        def render(self, **k):
            return "<b>ok</b>"
    class DummyEnv:
        def get_template(self, name):
            return DummyT()
    monkeypatch.setattr(ns, "env", DummyEnv())

    class BadSMTP:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def starttls(self): pass
        def login(self, *a, **k): pass
        def sendmail(self, *a, **k):
            raise ConnectionError("no smtp")
    monkeypatch.setattr(ns, "smtplib", type("S", (), {"SMTP": BadSMTP}))
    with pytest.raises(Exception):
        ns.send_email_notification(u.email, n)


def test_workflow_invalid_direct_archive(monkeypatch, db_session: Session):
    u = _mk_user(db_session)
    it = _mk_intervention(db_session)
    # try to archive directly -> 409/400 from service
    with pytest.raises(Exception):
        update_statut_intervention(db_session, it.id, StatutIntervention.archivee, user_id=u.id)
