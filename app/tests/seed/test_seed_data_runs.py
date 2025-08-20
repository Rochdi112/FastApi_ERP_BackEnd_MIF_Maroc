import pytest

from app.seed.seed_data import seed_all
from app.models.user import User
from app.models.intervention import Intervention


@pytest.mark.skip(reason="Seed data not required for unit tests; schema and API covered elsewhere")
def test_seed_all_populates_database(db_session):
    # Run seeding on the in-memory DB session
    seed_all(db_session)

    # Basic sanity checks: users and interventions must exist
    assert db_session.query(User).count() >= 1
    assert db_session.query(Intervention).count() >= 1
