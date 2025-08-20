import pytest
from pydantic import ValidationError

from app.schemas.stock import (
    PieceDetacheeBase,
    MouvementStockBase,
    TypeMouvement,
)


def test_piece_detachee_reference_and_stock_maximum_validators():
    # Invalid reference with forbidden character
    with pytest.raises(ValidationError):
        PieceDetacheeBase(
            nom="Piece",
            reference="BAD*REF",
            stock_minimum=1,
        )

    # Stock maximum lower than minimum triggers error
    with pytest.raises(ValidationError):
        PieceDetacheeBase(
            nom="Piece",
            reference="OK-REF",
            stock_minimum=5,
            stock_maximum=3,
        )

    # Valid instance
    ok = PieceDetacheeBase(
        nom="Piece",
        reference="OK-REF",
        stock_minimum=1,
        stock_maximum=10,
    )
    # Reference normalized to upper case by validator
    assert ok.reference == "OK-REF"


def test_mouvement_stock_quantite_validator():
    # Non-positive quantity invalid
    with pytest.raises(ValidationError):
        MouvementStockBase(
            type_mouvement=TypeMouvement.entree,
            quantite=0,
        )

    # Valid quantity passes
    ms = MouvementStockBase(type_mouvement=TypeMouvement.sortie, quantite=2)
    assert ms.quantite == 2
