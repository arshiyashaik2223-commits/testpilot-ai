import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    All configuration is read from environment variables.
    Never hard-code secrets or connection strings here.
    """

    # Flask secret key — used to sign sessions/cookies
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # PostgreSQL connection string, e.g.:
    # postgresql://testpilot_user:password@localhost:5432/testpilot_db
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT settings
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  # 24 hours, in seconds


def validate_config():
    """Called once at startup so missing config fails fast with a clear message."""
    if not Config.SQLALCHEMY_DATABASE_URI:
        raise RuntimeError(
            "DATABASE_URL is not set. Add it to your .env file. "
            "Example: DATABASE_URL=postgresql://testpilot_user:password@localhost:5432/testpilot_db"
        )
