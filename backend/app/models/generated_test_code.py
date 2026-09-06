import uuid
from datetime import datetime, timezone

from app.extensions import db


class GeneratedTestCode(db.Model):
    __tablename__ = "generated_test_code"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # One-to-one with TestCase: each test case has exactly one current code version.
    test_case_id = db.Column(
        db.String(36), db.ForeignKey("test_cases.id"), nullable=False, unique=True, index=True
    )
    code = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "test_case_id": self.test_case_id,
            "code": self.code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
