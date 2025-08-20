import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.planning_service import create_planning, update_planning_dates, update_planning_frequence, delete_planning, get_all_plannings
from app.schemas.planning import PlanningCreate
from app.models.equipement import Equipement


def _mk_eq(db):
    e = Equipement(nom="E1", type_equipement="T", localisation="L")
    db.add(e); db.commit(); db.refresh(e)
    return e


def test_planning_crud_and_rules(db_session: Session):
    eq = _mk_eq(db_session)
    now = datetime.utcnow()
    # unknown equipment -> 404
    with pytest.raises(Exception):
        create_planning(db_session, PlanningCreate(equipement_id=99999, frequence="mensuel", prochaine_date=now))
    # invalid frequency -> 400
    with pytest.raises(Exception):
        create_planning(db_session, PlanningCreate(equipement_id=eq.id, frequence="unknown", prochaine_date=now))
    # create ok
    p = create_planning(db_session, PlanningCreate(equipement_id=eq.id, frequence="mensuelle", prochaine_date=now))
    # update dates
    nd = now + timedelta(days=30)
    p2 = update_planning_dates(db_session, p.id, nd)
    assert p2.derniere_date == now and p2.prochaine_date == nd
    # change frequency with normalization and fallback
    p3 = update_planning_frequence(db_session, p.id, "Trimestrielle")
    assert str(p3.frequence) in ("FrequencePlanning.trimestriel", "trimestriel")
    p4 = update_planning_frequence(db_session, p.id, "nope")
    # delete
    delete_planning(db_session, p.id)
    assert all(x.id != p.id for x in get_all_plannings(db_session))
