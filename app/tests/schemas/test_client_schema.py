from app.schemas.client import ClientBase


def test_client_schema_minimal():
    c = ClientBase(nom_entreprise="ACME", contact_principal="Alice", email="acme@example.com")
    assert c.nom_entreprise == "ACME"
