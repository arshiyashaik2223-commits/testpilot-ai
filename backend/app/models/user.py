import uuid
from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, plain_password: str) -> None:
        """Hashes the password before storing it. We never store plain text passwords."""
        self.password_hash = generate_password_hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        return check_password_hash(self.password_hash, plain_password)

    def to_dict(self) -> dict:
        """Safe representation for API responses — never includes password_hash."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
