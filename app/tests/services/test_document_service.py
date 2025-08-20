import io
import os
import uuid
import pytest
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.services.document_service import create_document, save_uploaded_file
from app.core.config import settings
from app.models.intervention import Intervention


def _mk_intervention(db: Session) -> Intervention:
    from app.models.equipement import Equipement
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash

    eq = Equipement(nom=f"eq-{uuid.uuid4().hex[:6]}", type_equipement="type", localisation="loc")
    db.add(eq)
    db.commit(); db.refresh(eq)
    i = Intervention(titre="t", description="d", type_intervention="corrective", priorite="basse", urgence=False,
                     statut="ouverte", equipement_id=eq.id)
    db.add(i); db.commit(); db.refresh(i)
    return i


def test_save_uploaded_file_valid_and_path(monkeypatch, tmp_path):
    # Redirect uploads dir
    ud = tmp_path / "uploads"
    monkeypatch.setattr(settings, "UPLOAD_DIRECTORY", str(ud))
    data = io.BytesIO(b"hello")
    up = UploadFile(filename="note.txt", file=data)
    rel = save_uploaded_file(up)
    assert rel.startswith("static/uploads/") and rel.endswith(".txt")
    # File exists on disk
    fn = os.path.join(settings.UPLOAD_DIRECTORY, rel.split("/")[-1])
    assert os.path.exists(fn)


def test_save_uploaded_file_no_ext_400(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "UPLOAD_DIRECTORY", str(tmp_path))
    up = UploadFile(filename="noext", file=io.BytesIO(b"x"))
    with pytest.raises(Exception):
        save_uploaded_file(up)


def test_create_document_intervention_404(monkeypatch, db_session: Session, tmp_path):
    monkeypatch.setattr(settings, "UPLOAD_DIRECTORY", str(tmp_path))
    up = UploadFile(filename="a.png", file=io.BytesIO(b"png"))
    with pytest.raises(Exception):
        create_document(db_session, up, 99999)


def test_create_document_success(monkeypatch, db_session: Session, tmp_path):
    monkeypatch.setattr(settings, "UPLOAD_DIRECTORY", str(tmp_path))
    inter = _mk_intervention(db_session)
    up = UploadFile(filename="a.jpg", file=io.BytesIO(b"jpegdata"))
    doc = create_document(db_session, up, inter.id)
    assert doc.chemin.startswith("static/uploads/") and doc.nom_fichier == "a.jpg"
