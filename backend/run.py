from dotenv import load_dotenv

load_dotenv()  # must happen before `create_app` reads env vars

from app import create_app
from app.extensions import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # For the MVP we use create_all() for simplicity. Once the schema
        # stabilizes, switch to Flask-Migrate/Alembic for proper migrations.
        db.create_all()
    app.run(debug=True, port=5000)
