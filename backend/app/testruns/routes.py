import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Project, TestCase, GeneratedTestCode, TestRun
from app.ai.factory import get_ai_provider
from app.execution.security import find_forbidden_pattern
from app.execution.runner import run_pytest_code

testruns_bp = Blueprint("testruns", __name__, url_prefix="/api/test-cases")


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def _get_owned_test_case_or_none(test_case_id: str, owner_id: str):
    """
    A test case is only accessible if its project belongs to the current user.
    Joins TestCase -> Project to check ownership in one query.
    """
    return (
        TestCase.query
        .join(Project, TestCase.project_id == Project.id)
        .filter(TestCase.id == test_case_id, Project.owner_id == owner_id)
        .first()
    )


@testruns_bp.route("/<test_case_id>", methods=["GET"])
@jwt_required()
def get_test_case(test_case_id):
    user_id = get_jwt_identity()
    test_case = _get_owned_test_case_or_none(test_case_id, user_id)
    if test_case is None:
        return _error("Test case not found.", status=404)

    return jsonify({"test_case": test_case.to_dict()}), 200


@testruns_bp.route("/<test_case_id>/generate-code", methods=["POST"])
@jwt_required()
def generate_code(test_case_id):
    user_id = get_jwt_identity()
    test_case = _get_owned_test_case_or_none(test_case_id, user_id)
    if test_case is None:
        return _error("Test case not found.", status=404)

    try:
        provider = get_ai_provider()
        code = provider.generate_test_code(test_case.to_dict())
    except ValueError as exc:
        return _error(f"AI code generation failed: {exc}", status=502)
    except Exception as exc:
        return _error(f"AI provider error: {exc}", status=502)

    existing = GeneratedTestCode.query.filter_by(test_case_id=test_case.id).first()
    if existing:
        existing.code = code
        generated = existing
    else:
        generated = GeneratedTestCode(test_case_id=test_case.id, code=code)
        db.session.add(generated)

    db.session.commit()

    return jsonify({"message": "Test code generated.", "generated_code": generated.to_dict()}), 200


@testruns_bp.route("/<test_case_id>/code", methods=["GET"])
@jwt_required()
def get_code(test_case_id):
    user_id = get_jwt_identity()
    test_case = _get_owned_test_case_or_none(test_case_id, user_id)
    if test_case is None:
        return _error("Test case not found.", status=404)

    generated = GeneratedTestCode.query.filter_by(test_case_id=test_case.id).first()
    if generated is None:
        return _error("No code generated for this test case yet.", status=404)

    return jsonify({"generated_code": generated.to_dict()}), 200


@testruns_bp.route("/<test_case_id>/code", methods=["PUT"])
@jwt_required()
def update_code(test_case_id):
    """Lets the user edit the AI-generated code before running it."""
    user_id = get_jwt_identity()
    test_case = _get_owned_test_case_or_none(test_case_id, user_id)
    if test_case is None:
        return _error("Test case not found.", status=404)

    data = request.get_json(silent=True) or {}
    code = data.get("code")
    if not code or not code.strip():
        return _error("Code is required.")

    forbidden = find_forbidden_pattern(code)
    if forbidden:
        return _error(
            f"Code contains a disallowed pattern ('{forbidden}') and cannot be saved.",
            status=422,
        )

    generated = GeneratedTestCode.query.filter_by(test_case_id=test_case.id).first()
    if generated is None:
        generated = GeneratedTestCode(test_case_id=test_case.id, code=code)
        db.session.add(generated)
    else:
        generated.code = code

    db.session.commit()

    return jsonify({"message": "Code updated.", "generated_code": generated.to_dict()}), 200


@testruns_bp.route("/<test_case_id>/execute", methods=["POST"])
@jwt_required()
def execute_test(test_case_id):
    user_id = get_jwt_identity()
    test_case = _get_owned_test_case_or_none(test_case_id, user_id)
    if test_case is None:
        return _error("Test case not found.", status=404)

    generated = GeneratedTestCode.query.filter_by(test_case_id=test_case.id).first()
    if generated is None:
        return _error("Generate test code before executing.", status=400)

    data = request.get_json(silent=True) or {}
    api_base_url = data.get("api_base_url") or os.environ.get("DEFAULT_API_BASE_URL")

    result = run_pytest_code(generated.code, api_base_url=api_base_url)

    test_run = TestRun(
        project_id=test_case.project_id,
        test_case_id=test_case.id,
        status=result["status"],
        output=result["output"],
        duration_ms=result["duration_ms"],
    )
    db.session.add(test_run)
    db.session.commit()

    return jsonify({"message": "Execution complete.", "test_run": test_run.to_dict()}), 200


@testruns_bp.route("/<test_case_id>/runs", methods=["GET"])
@jwt_required()
def list_runs(test_case_id):
    user_id = get_jwt_identity()
    test_case = _get_owned_test_case_or_none(test_case_id, user_id)
    if test_case is None:
        return _error("Test case not found.", status=404)

    runs = (
        TestRun.query.filter_by(test_case_id=test_case.id)
        .order_by(TestRun.executed_at.desc())
        .all()
    )
    return jsonify({"test_runs": [r.to_dict() for r in runs]}), 200
