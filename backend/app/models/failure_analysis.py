import uuid
from datetime import datetime, timezone

from app.extensions import db

FAILURE_CATEGORIES = (
    "BUG", "ENVIRONMENT_ISSUE", "TEST_SCRIPT_ISSUE", "NETWORK_ISSUE",
    "DEPENDENCY_ISSUE", "FLAKY_TEST", "PERFORMANCE_ISSUE", "SECURITY_ISSUE",
)
SEVERITY_LEVELS = ("Low", "Medium", "High", "Critical")


class FailureAnalysis(db.Model):
    __tablename__ = "failure_analyses"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # One analysis per test run.
    test_run_id = db.Column(
        db.String(36), db.ForeignKey("test_runs.id"), nullable=False, unique=True, index=True
    )

    explanation = db.Column(db.Text, nullable=False)
    likely_cause = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Integer, nullable=False)  # 0-100, AI's own confidence estimate
    category = db.Column(db.String(30), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    suggested_fix = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "explanation": self.explanation,
            "likely_cause": self.likely_cause,
            "confidence": self.confidence,
            "category": self.category,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
