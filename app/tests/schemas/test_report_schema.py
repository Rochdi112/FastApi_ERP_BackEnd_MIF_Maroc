from app.schemas.report import ReportRequest, ReportOut, ReportMetadata, ReportType
from datetime import datetime


def test_report_schema():
    req = ReportRequest(type=ReportType.INTERVENTIONS)
    assert req.type == ReportType.INTERVENTIONS
    meta = ReportMetadata(
        id=1,
        title="R",
        type=ReportType.INTERVENTIONS,
        format="pdf",
        file_path="/tmp/r.pdf",
        file_size=10,
        created_at=datetime.utcnow(),
        created_by_id=1,
    )
    out = ReportOut(metadata=meta, download_url="/d/1")
    assert out.metadata.id == 1
