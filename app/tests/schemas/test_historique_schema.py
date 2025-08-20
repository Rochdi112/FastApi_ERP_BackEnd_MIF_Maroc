from datetime import datetime
from app.schemas.historique import HistoriqueOut
from app.schemas.user import UserOut, UserRole


def test_historique_out_schema():
    now = datetime.utcnow()
    u = UserOut(id=1, username="u", full_name="U", email="u@ex.com", role=UserRole.client, is_active=True)
    h = HistoriqueOut(id=1, statut="ouverte", remarque="r", horodatage=now, user=u, intervention_id=2)
    assert h.id == 1 and h.user.id == 1 and h.intervention_id == 2
