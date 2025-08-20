from app.schemas.dashboard import DashboardResponse, ChartData


def test_dashboard_schema_basic():
    chart = ChartData(labels=["A", "B"], datasets=[{"label": "X", "data": [1, 2]}], title="T")
    d = DashboardResponse(user_role="admin", graphiques=[chart], kpis={"interventions_ouvertes": 5})
    assert d.user_role == "admin"
    assert d.graphiques[0].title == "T"
