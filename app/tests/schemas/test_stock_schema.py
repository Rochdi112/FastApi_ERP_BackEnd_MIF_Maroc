from app.schemas.stock import PieceDetacheeBase, MouvementStockOut, TypeMouvement
from datetime import datetime


def test_stock_schemas():
    a = PieceDetacheeBase(reference="R1", nom="N1")
    assert a.reference == "R1"
    m = MouvementStockOut(
        id=1,
        piece_detachee_id=1,
        quantite=1,
        type_mouvement=TypeMouvement.entree,
        stock_avant=0,
        stock_apres=1,
        date_mouvement=datetime.utcnow(),
    )
    assert m.type_mouvement == TypeMouvement.entree
