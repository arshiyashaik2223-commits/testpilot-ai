from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Project

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def _get_owned_project_or_none(project_id: str, owner_id: str):
    """
    Looks up a project by id, but only returns it if it belongs to the
    current user. This is what stops User A from reading/editing User B's
    projects just by guessing an id.
    """
    return Project.query.filter_by(id=project_id, owner_id=owner_id).first()


@projects_bp.route("", methods=["POST"])
@jwt_required()
def create_project():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip() or None

    if not name:
        return _error("Project name is required.")
    if len(name) > 200:
        return _error("Project name must be 200 characters or fewer.")

    project = Project(name=name, description=description, owner_id=user_id)
    db.session.add(project)
    db.session.commit()

    return jsonify({"message": "Project created.", "project": project.to_dict()}), 201


@projects_bp.route("", methods=["GET"])
@jwt_required()
def list_projects():
    user_id = get_jwt_identity()
    projects = (
        Project.query.filter_by(owner_id=user_id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return jsonify({"projects": [p.to_dict() for p in projects]}), 200


@projects_bp.route("/<project_id>", methods=["GET"])
@jwt_required()
def get_project(project_id):
    user_id = get_jwt_identity()
    project = _get_owned_project_or_none(project_id, user_id)

    if project is None:
        return _error("Project not found.", status=404)

    return jsonify({"project": project.to_dict()}), 200


@projects_bp.route("/<project_id>", methods=["PUT"])
@jwt_required()
def update_project(project_id):
    user_id = get_jwt_identity()
    project = _get_owned_project_or_none(project_id, user_id)

    if project is None:
        return _error("Project not found.", status=404)

    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return _error("Project name cannot be empty.")
        if len(name) > 200:
            return _error("Project name must be 200 characters or fewer.")
        project.name = name

    if "description" in data:
        project.description = (data.get("description") or "").strip() or None

    db.session.commit()

    return jsonify({"message": "Project updated.", "project": project.to_dict()}), 200


@projects_bp.route("/<project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id):
    user_id = get_jwt_identity()
    project = _get_owned_project_or_none(project_id, user_id)

    if project is None:
        return _error("Project not found.", status=404)

    db.session.delete(project)
    db.session.commit()

    return jsonify({"message": "Project deleted."}), 200
