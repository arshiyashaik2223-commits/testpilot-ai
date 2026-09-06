from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Created here (empty) and initialized inside create_app() in __init__.py.
# This pattern avoids circular imports between app/__init__.py and the models/routes
# that need to import `db` or `jwt`.
db = SQLAlchemy()
jwt = JWTManager()
