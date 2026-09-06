from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Project, Requirement, TestCase
from app.ai.factory import get_ai_provider

testcases_bp = Blueprint("testcases", __name__, url_prefix="/api/projects")


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def _get_owned_project_or_none(project_id: str, owner_id: str):
    return Project.query.filter_by(id=project_id, owner_id=owner_id).first()


@testcases_bp.route("/<project_id>/requirements", methods=["POST"])
@jwt_required()
def create_requirement_and_generate_test_cases(project_id):
    """
    The core MVP flow: take a requirement, generate AI test cases for it,
    save both, and return them together.
    """
    user_id = get_jwt_identity()
    project = _get_owned_project_or_none(project_id, user_id)
    if project is None:
        return _error("Project not found.", status=404)

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return _error("Requirement text is required.")
    if len(text) > 5000:
        return _error("Requirement text must be 5000 characters or fewer.")

    requirement = Requirement(project_id=project.id, text=text)
    db.session.add(requirement)
    db.session.flush()  # assigns requirement.id without committing yet

    try:
        provider = get_ai_provider()
        generated = provider.generate_test_cases(text)
    except ValueError as exc:
        # AI returned something we couldn't parse/validate — don't save a
        # requirement with no test cases attached.
        db.session.rollback()
        return _error(f"AI generation failed: {exc}", status=502)
    except Exception as exc:  # e.g. missing API key, network/provider error
        db.session.rollback()
        return _error(f"AI provider error: {exc}", status=502)

    test_cases = []
    for item in generated:
        tc = TestCase(
            project_id=project.id,
            requirement_id=requirement.id,
            scenario=item["scenario"],
            test_type=item["test_type"],
            preconditions=item.get("preconditions"),
            steps=item["steps"],
            test_data=item.get("test_data"),
            expected_result=item["expected_result"],
            priority=item["priority"],
        )
        db.session.add(tc)
        test_cases.append(tc)

    db.session.commit()

    return jsonify({
        "message": f"Generated {len(test_cases)} test cases.",
        "requirement": requirement.to_dict(),
        "test_cases": [tc.to_dict() for tc in test_cases],
    }), 201


@testcases_bp.route("/<project_id>/requirements", methods=["GET"])
@jwt_required()
def list_requirements(project_id):
    user_id = get_jwt_identity()
    project = _get_owned_project_or_none(project_id, user_id)
    if project is None:
        return _error("Project not found.", status=404)

    requirements = (
        Requirement.query.filter_by(project_id=project.id)
        .order_by(Requirement.created_at.desc())
        .all()
    )
    return jsonify({"requirements": [r.to_dict() for r in requirements]}), 200


@testcases_bp.route("/<project_id>/test-cases", methods=["GET"])
@jwt_required()
def list_test_cases(project_id):
    user_id = get_jwt_identity()
    project = _get_owned_project_or_none(project_id, user_id)
    if project is None:
        return _error("Project not found.", status=404)

    query = TestCase.query.filter_by(project_id=project.id)

    requirement_id = request.args.get("requirement_id")
    if requirement_id:
        query = query.filter_by(requirement_id=requirement_id)

    test_cases = query.order_by(TestCase.created_at.desc()).all()
    return jsonify({"test_cases": [tc.to_dict() for tc in test_cases]}), 200
