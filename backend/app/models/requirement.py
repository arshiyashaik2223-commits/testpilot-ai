import uuid
from datetime import datetime, timezone

from app.extensions import db


class Requirement(db.Model):
    __tablename__ = "requirements"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "text": self.text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
