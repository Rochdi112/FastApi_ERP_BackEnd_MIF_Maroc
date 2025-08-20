import pytest
from sqlalchemy.orm import Session
from app.services.auth_service import authenticate_user, authenticate_user_by_username
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def _mk_user(db: Session, email: str, username: str, password: str, role=UserRole.admin, active=True) -> User:
    u = User(
        username=username,
        full_name=username,
        email=email,
        hashed_password=get_password_hash(password),
        role=role,
        is_active=active,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def test_authenticate_user_success_and_token_type(db_session: Session):
    _mk_user(db_session, "u1@example.com", "u1", "pw1", UserRole.responsable)
    tok = authenticate_user(db_session, "u1@example.com", "pw1")
    assert tok.token_type == "bearer"
    assert isinstance(tok.access_token, str) and len(tok.access_token) > 10


def test_authenticate_user_wrong_password_401(db_session: Session):
    _mk_user(db_session, "u2@example.com", "u2", "pw2")
    with pytest.raises(Exception) as ei:
        authenticate_user(db_session, "u2@example.com", "bad")
    assert "401" in str(ei.value)


def test_authenticate_user_inactive_403(db_session: Session):
    _mk_user(db_session, "u3@example.com", "u3", "pw3", active=False)
    with pytest.raises(Exception) as ei:
        authenticate_user(db_session, "u3@example.com", "pw3")
    assert "403" in str(ei.value)


def test_authenticate_by_username_paths(db_session: Session):
    _mk_user(db_session, "u4@example.com", "u4name", "pw4")
    tok = authenticate_user_by_username(db_session, "u4name", "pw4")
    assert tok.token_type == "bearer"
    with pytest.raises(Exception):
        authenticate_user_by_username(db_session, "u4name", "bad")
