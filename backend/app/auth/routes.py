import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validation_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # --- Input validation ---
    if not name:
        return _validation_error("Name is required.")
    if not email or not EMAIL_PATTERN.match(email):
        return _validation_error("A valid email is required.")
    if len(password) < 8:
        return _validation_error("Password must be at least 8 characters long.")

    if User.query.filter_by(email=email).first() is not None:
        return _validation_error("An account with this email already exists.", status=409)

    user = User(name=name, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)

    return jsonify({
        "message": "Account created successfully.",
        "user": user.to_dict(),
        "access_token": access_token,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return _validation_error("Email and password are required.")

    user = User.query.filter_by(email=email).first()

    # Same error message whether the email doesn't exist or the password is wrong.
    # This avoids leaking which emails are registered.
    if user is None or not user.check_password(password):
        return _validation_error("Invalid email or password.", status=401)

    access_token = create_access_token(identity=user.id)

    return jsonify({
        "message": "Login successful.",
        "user": user.to_dict(),
        "access_token": access_token,
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """A protected route to prove JWT auth is working end-to-end."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user is None:
        return _validation_error("User not found.", status=404)

    return jsonify({"user": user.to_dict()}), 200
