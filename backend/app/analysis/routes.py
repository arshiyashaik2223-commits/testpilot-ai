from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Project, TestCase, TestRun, GeneratedTestCode, FailureAnalysis
from app.ai.factory import get_ai_provider

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api/test-runs")


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def _get_owned_test_run_or_none(test_run_id: str, owner_id: str):
    """A test run is only accessible if its project belongs to the current user."""
    return (
        TestRun.query
        .join(Project, TestRun.project_id == Project.id)
        .filter(TestRun.id == test_run_id, Project.owner_id == owner_id)
        .first()
    )


@analysis_bp.route("/<test_run_id>/analyze", methods=["POST"])
@jwt_required()
def analyze_failure(test_run_id):
    user_id = get_jwt_identity()
    test_run = _get_owned_test_run_or_none(test_run_id, user_id)
    if test_run is None:
        return _error("Test run not found.", status=404)

    if test_run.status == "passed":
        return _error("This test run passed — nothing to analyze.", status=400)

    test_case = TestCase.query.get(test_run.test_case_id)
    if test_case is None:
        return _error("Associated test case no longer exists.", status=404)

    generated_code = GeneratedTestCode.query.filter_by(test_case_id=test_case.id).first()
    code = generated_code.code if generated_code else "(no generated code found)"

    try:
        provider = get_ai_provider()
        result = provider.analyze_failure(
            scenario=test_case.scenario,
            expected_result=test_case.expected_result,
            code=code,
            output=test_run.output or "(no output captured)",
        )
    except ValueError as exc:
        return _error(f"AI analysis failed: {exc}", status=502)
    except Exception as exc:
        return _error(f"AI provider error: {exc}", status=502)

    existing = FailureAnalysis.query.filter_by(test_run_id=test_run.id).first()
    if existing:
        existing.explanation = result["explanation"]
        existing.likely_cause = result["likely_cause"]
        existing.confidence = result["confidence"]
        existing.category = result["category"]
        existing.severity = result["severity"]
        existing.suggested_fix = result["suggested_fix"]
        analysis = existing
    else:
        analysis = FailureAnalysis(
            test_run_id=test_run.id,
            explanation=result["explanation"],
            likely_cause=result["likely_cause"],
            confidence=result["confidence"],
            category=result["category"],
            severity=result["severity"],
            suggested_fix=result["suggested_fix"],
        )
        db.session.add(analysis)

    db.session.commit()

    return jsonify({"message": "Failure analyzed.", "analysis": analysis.to_dict()}), 200


@analysis_bp.route("/<test_run_id>/analysis", methods=["GET"])
@jwt_required()
def get_analysis(test_run_id):
    user_id = get_jwt_identity()
    test_run = _get_owned_test_run_or_none(test_run_id, user_id)
    if test_run is None:
        return _error("Test run not found.", status=404)

    analysis = FailureAnalysis.query.filter_by(test_run_id=test_run.id).first()
    if analysis is None:
        return _error("No analysis for this test run yet.", status=404)

    return jsonify({"analysis": analysis.to_dict()}), 200
