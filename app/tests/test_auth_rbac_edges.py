from app.models.user import User, UserRole
from app.core.security import get_password_hash


def test_login_bad_creds(client):
    r = client.post("/api/v1/auth/token", data={"email":"no@user","password":"x"})
    assert r.status_code in (400,401)


essential_role = UserRole.technicien if hasattr(UserRole, 'technicien') else 'technicien'

def test_rbac_forbidden_non_admin(client, db_session):
    user = db_session.query(User).filter(User.email == "tech1@example.com").first()
    if not user:
        user = User(
            username="tech1",
            full_name="Tech 1",
            email="tech1@example.com",
            hashed_password=get_password_hash("password"),
            role=essential_role,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    tok = client.post("/api/v1/auth/token", data={"email":user.email,"password":"password"})
    assert tok.status_code in (200, 201), tok.text
    h = {"Authorization": f"Bearer {tok.json()['access_token']}"}
    r = client.get("/api/v1/users/", headers=h)
    assert r.status_code == 403
