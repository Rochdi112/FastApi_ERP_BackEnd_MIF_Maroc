from app.core.exceptions import CredentialsException, NotFoundException, PermissionDeniedException


def test_exceptions_instantiation_and_fields():
    e1 = CredentialsException()
    assert e1.status_code == 401 and "WWW-Authenticate" in e1.headers
    e2 = NotFoundException("User")
    assert e2.status_code == 404 and "User introuvable" in e2.detail
    e3 = PermissionDeniedException()
    assert e3.status_code == 403
