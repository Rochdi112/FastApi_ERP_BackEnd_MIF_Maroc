import pytest
from sqlalchemy.orm import Session
from app.services.user_service import create_user, deactivate_user, reactivate_user, update_user, get_user_by_id, get_user_by_email, ensure_user_for_email
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import UserRole, User
from app.db import database as dbmod


def test_user_collisions_and_updates(monkeypatch, db_session: Session):
    # create base user
    u = create_user(db_session, UserCreate(username="u1", full_name="U1", email="u1@ex.com", password="pwd", role=UserRole.client))
    # email duplicate -> 409
    with pytest.raises(Exception):
        create_user(db_session, UserCreate(username="u2", full_name="U2", email="u1@ex.com", password="pwd", role=UserRole.client))
    # username duplicate -> 409
    with pytest.raises(Exception):
        create_user(db_session, UserCreate(username="u1", full_name="U3", email="u3@ex.com", password="pwd", role=UserRole.client))
    # fallback exists forces 409 for other email
    monkeypatch.setattr("app.services.user_service._check_exists_in_fallback", lambda **kw: True)
    with pytest.raises(Exception):
        create_user(db_session, UserCreate(username="uX", full_name="UX", email="ux@ex.com", password="pwd", role=UserRole.client))
    # deactivate/reactivate
    deactivate_user(db_session, u.id)
    assert get_user_by_id(db_session, u.id).is_active is False
    reu = reactivate_user(db_session, u.id)
    assert reu.is_active is True
    # updates
    u2 = update_user(db_session, u.id, UserUpdate(full_name="New"))
    assert u2.full_name == "New"
    u3 = update_user(db_session, u.id, UserUpdate(password="newpass"))
    assert u3.hashed_password != "newpass"
    u4 = update_user(db_session, u.id, UserUpdate(full_name="NN", password="ppp"))
    assert u4.full_name == "NN"


def test_get_user_fallback_by_email(monkeypatch, db_session: Session):
    # No user in primary session; fallback SessionLocal returns one
    class DummySess:
        def __enter__(self):
            from app.core.security import get_password_hash
            self._s = dbmod.SessionLocal()
            self.u = User(username="fb", full_name="FB", email="fb@ex.com", hashed_password=get_password_hash("x"), role=UserRole.client, is_active=True)
            self._s.add(self.u); self._s.commit(); self._s.refresh(self.u)
            return self._s
        def __exit__(self, *a):
            self._s.close()
    monkeypatch.setattr("app.services.user_service.SessionLocal", lambda: DummySess())
    got = get_user_by_email(db_session, "fb@ex.com")
    assert got and got.email == "fb@ex.com"


def test_ensure_user_for_email(db_session: Session):
    from app.models.user import User
    before = db_session.query(User).count()
    u = ensure_user_for_email(db_session, email="nouveau@ex.com", role=UserRole.technicien)
    after = db_session.query(User).count()
    assert after == before + 1 and u.email == "nouveau@ex.com"
