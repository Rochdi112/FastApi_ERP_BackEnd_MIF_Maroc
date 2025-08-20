import pytest
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.technicien import Competence
from app.core.security import get_password_hash
from app.services.technicien_service import create_technicien, get_technicien_by_id, create_competence, get_all_competences
from app.schemas.technicien import TechnicienCreate, CompetenceCreate


def _mk_user(db, role):
    u = User(username=f"u{role.value}", full_name="U", email=f"{role.value}@ex.com", hashed_password=get_password_hash("x"), role=role, is_active=True)
    db.add(u); db.commit(); db.refresh(u)
    return u


def test_technicien_creation_and_errors(db_session: Session):
    # missing user
    with pytest.raises(Exception):
        create_technicien(db_session, TechnicienCreate(user_id=99999, equipe="A"))
    # wrong role
    client = _mk_user(db_session, UserRole.client)
    with pytest.raises(Exception):
        create_technicien(db_session, TechnicienCreate(user_id=client.id, equipe="A"))
    # create competence and duplicate
    c1 = create_competence(db_session, CompetenceCreate(nom="Electricite"))
    with pytest.raises(Exception):
        create_competence(db_session, CompetenceCreate(nom="Electricite"))
    assert any(c.nom == "Electricite" for c in get_all_competences(db_session))
    # create technicien with messy availability and competences ok
    tech_user = _mk_user(db_session, UserRole.technicien)
    # missing competence id triggers 404
    with pytest.raises(Exception):
        create_technicien(db_session, TechnicienCreate(user_id=tech_user.id, equipe="A", disponibilite=" DISPONIBLE ", competences_ids=[c1.id, 9999]))
    # success path
    t = create_technicien(db_session, TechnicienCreate(user_id=tech_user.id, equipe="A", disponibilite=" DISPONIBLE ", competences_ids=[c1.id]))
    assert t.user_id == tech_user.id and len(t.competences) == 1
    # get missing
    with pytest.raises(Exception):
        get_technicien_by_id(db_session, 99999)
