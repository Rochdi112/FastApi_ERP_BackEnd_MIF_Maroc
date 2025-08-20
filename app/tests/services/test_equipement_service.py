import pytest
from sqlalchemy.orm import Session
from app.services.equipement_service import create_equipement, get_equipement_by_id, get_all_equipements, delete_equipement
from app.schemas.equipement import EquipementCreate


def test_create_and_duplicate_and_delete(db_session: Session):
    data = EquipementCreate(nom="EQA", type="T", localisation="L", frequence_entretien="7")
    e1 = create_equipement(db_session, data)
    assert e1.frequence_entretien_jours == 7
    # duplicate
    with pytest.raises(Exception):
        create_equipement(db_session, data)
    # None frequency path
    data2 = EquipementCreate(nom="EQB", type="T", localisation="L", frequence_entretien=None)
    e2 = create_equipement(db_session, data2)
    assert e2.frequence_entretien_jours is None
    # delete and ensure removed
    all1 = get_all_equipements(db_session)
    delete_equipement(db_session, e2.id)
    all2 = get_all_equipements(db_session)
    assert len(all1) == len(all2) + 1
    # get missing -> NotFoundException
    from app.core.exceptions import NotFoundException
    with pytest.raises(NotFoundException):
        get_equipement_by_id(db_session, 99999)
