from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config, validate_config
from app.extensions import db, jwt


def create_app():
    validate_config()  # fail fast if DATABASE_URL etc. are missing

    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow the React frontend (running on a different port during development) to call the API
    CORS(app)

    db.init_app(app)
    jwt.init_app(app)

    # Import models here (after db.init_app) so SQLAlchemy knows about them
    # before create_all()/migrations run.
    from app.models import (  # noqa: F401
        User, Project, Requirement, TestCase,
        GeneratedTestCode, TestRun, FailureAnalysis,
    )

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.projects.routes import projects_bp
    app.register_blueprint(projects_bp)

    from app.testcases.routes import testcases_bp
    app.register_blueprint(testcases_bp)

    from app.testruns.routes import testruns_bp
    app.register_blueprint(testruns_bp)

    from app.analysis.routes import analysis_bp
    app.register_blueprint(analysis_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "TestPilot AI backend"}), 200

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"error": "Internal server error."}), 500

    return app
