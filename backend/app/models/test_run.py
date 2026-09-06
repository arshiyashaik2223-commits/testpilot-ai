import uuid
from datetime import datetime, timezone

from app.extensions import db

VALID_STATUSES = ("passed", "failed", "error")


class TestRun(db.Model):
    __tablename__ = "test_runs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False, index=True)
    test_case_id = db.Column(db.String(36), db.ForeignKey("test_cases.id"), nullable=False, index=True)

    # "passed" / "failed" (assertions failed, exit code 1) / "error" (crashed,
    # timed out, or blocked before it could even run)
    status = db.Column(db.String(20), nullable=False)
    output = db.Column(db.Text, nullable=True)  # combined stdout/stderr, truncated
    duration_ms = db.Column(db.Integer, nullable=True)

    executed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "test_case_id": self.test_case_id,
            "status": self.status,
            "output": self.output,
            "duration_ms": self.duration_ms,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }
