import pytest
from pydantic import ValidationError

from app.schemas.client import ClientBase, ClientCreate, ClientUpdate


def test_clientbase_valid_and_invalid_fields():
    # Valid case hits happy branches
    c = ClientBase(
        nom_entreprise="Acme Corp",
        secteur_activite="industrie",
        numero_siret="12345678901234",
        contact_principal="John Doe",
        email="john@example.com",
        telephone="+33 1 23 45 67 89",
        telephone_mobile="0123456789",
        adresse="1 rue de Paris",
        code_postal="75001",
        ville="Paris",
        pays="France",
    )
    assert c.numero_siret == "12345678901234"

    # Invalid SIRET (non-digit) triggers validator error
    with pytest.raises(ValidationError):
        ClientBase(
            nom_entreprise="Bad SIRET",
            contact_principal="Jane",
            email="jane@example.com",
            numero_siret="ABC45678901234",
        )

    # Invalid phone too short triggers validator error
    with pytest.raises(ValidationError):
        ClientBase(
            nom_entreprise="Bad Phone",
            contact_principal="Jane",
            email="jane@example.com",
            telephone="12",
        )


def test_clientcreate_user_id_validator():
    # Positive user_id ok
    ok = ClientCreate(
        nom_entreprise="XY",
        contact_principal="YZ",
        email="x@y.z",
        user_id=1,
    )
    assert ok.user_id == 1

    # Negative user_id invalid
    with pytest.raises(ValidationError):
        ClientCreate(
            nom_entreprise="X",
            contact_principal="Y",
            email="x@y.z",
            user_id=-1,
        )
