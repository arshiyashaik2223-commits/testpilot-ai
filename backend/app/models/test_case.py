import uuid
from datetime import datetime, timezone

from app.extensions import db


class TestCase(db.Model):
    __tablename__ = "test_cases"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False, index=True)
    requirement_id = db.Column(db.String(36), db.ForeignKey("requirements.id"), nullable=False, index=True)

    scenario = db.Column(db.String(300), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)  # positive | negative | boundary | security | validation
    preconditions = db.Column(db.Text, nullable=True)

    # Stored as JSON so we keep the ordered list of steps without a separate table.
    steps = db.Column(db.JSON, nullable=False, default=list)

    test_data = db.Column(db.Text, nullable=True)
    expected_result = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="Medium")  # Low | Medium | High | Critical

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "requirement_id": self.requirement_id,
            "scenario": self.scenario,
            "test_type": self.test_type,
            "preconditions": self.preconditions,
            "steps": self.steps,
            "test_data": self.test_data,
            "expected_result": self.expected_result,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
