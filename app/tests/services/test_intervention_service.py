import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.intervention_service import create_intervention, update_statut_intervention, add_historique, create_intervention_from_planning
from app.schemas.intervention import InterventionCreate
from app.models.intervention import StatutIntervention
from app.models.user import User, UserRole
from app.models.technicien import Technicien
from app.models.equipement import Equipement
from app.models.planning import Planning
from app.core.security import get_password_hash


def _mk_user(db, role=UserRole.responsable):
    u = User(username=f"u{role.value}", full_name="U", email=f"{role.value}@ex.com", hashed_password=get_password_hash("x"), role=role, is_active=True)
    db.add(u); db.commit(); db.refresh(u)
    return u


def _mk_eq(db):
    e = Equipement(nom="E1", type_equipement="T", localisation="L")
    db.add(e); db.commit(); db.refresh(e)
    return e


def test_create_intervention_and_edges(db_session: Session):
    eq = _mk_eq(db_session)
    # technicien unknown -> 404
    with pytest.raises(Exception):
        create_intervention(db_session, InterventionCreate(titre="t", description="d", type_intervention="corrective", statut=StatutIntervention.ouverte, priorite="basse", urgence=False, equipement_id=eq.id, technicien_id=999), user_id=1)
    # equipment unknown -> 404
    with pytest.raises(Exception):
        create_intervention(db_session, InterventionCreate(titre="t", description="d", type_intervention="corrective", statut=StatutIntervention.ouverte, priorite="basse", urgence=False, equipement_id=9999, technicien_id=None), user_id=1)
    # success + historique with creator id
    creator = _mk_user(db_session)
    inter = create_intervention(db_session, InterventionCreate(titre="t", description="d", type_intervention="corrective", statut=StatutIntervention.ouverte, priorite="basse", urgence=False, equipement_id=eq.id, technicien_id=None), user_id=creator.id)
    # update status edges
    # unknown user -> 404
    with pytest.raises(Exception):
        update_statut_intervention(db_session, inter.id, StatutIntervention.en_cours, 99999)
    # closing writes date_cloture and historique
    tech = _mk_user(db_session, UserRole.technicien)
    updated = update_statut_intervention(db_session, inter.id, StatutIntervention.cloturee, tech.id, remarque="done")
    assert updated.date_cloture is not None
    # already closed -> 400
    with pytest.raises(Exception):
        update_statut_intervention(db_session, inter.id, StatutIntervention.en_cours, tech.id)


def test_add_historique_direct(db_session: Session):
    eq = _mk_eq(db_session)
    creator = _mk_user(db_session)
    inter = create_intervention(db_session, InterventionCreate(titre="t2", description="d2", type_intervention="corrective", statut=StatutIntervention.ouverte, priorite="basse", urgence=False, equipement_id=eq.id, technicien_id=None), user_id=creator.id)
    add_historique(db_session, inter.id, creator.id, StatutIntervention.en_cours, "note")


def test_create_from_planning_paths(db_session: Session, monkeypatch):
    # missing equipment -> 404
    p = Planning(equipement_id=99999, frequence="mensuel", prochaine_date=datetime.utcnow())
    with pytest.raises(Exception):
        create_intervention_from_planning(db_session, p)
    # success path
    eq = _mk_eq(db_session)
    p2 = Planning(equipement_id=eq.id, frequence="mensuel", prochaine_date=datetime.utcnow())
    db_session.add(p2); db_session.commit(); db_session.refresh(p2)
    called = {"x": False}
    def fake_update():
        called["x"] = True
    monkeypatch.setattr(Planning, "mettre_a_jour_prochaine_date", lambda self: fake_update())
    inter = create_intervention_from_planning(db_session, p2)
    assert inter.equipement_id == eq.id and called["x"] is True and p2.derniere_date is not None
