"""
This module initializes the Flask application, sets up configurations, and defines routes.
"""

import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from app.logger import logger
from app.config import Config
from app.extensions import init_extensions
from app.extensions import db
from app.routes.user_routes import user_bp
from app.routes.cron_schedule_routes import cron_schedule_bp
from app.routes.device_routes import devices_bp
from app.routes.permission_routes import permission_bp
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


def test_db_connection():
    """
    Test the database connection using SQLAlchemy.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        # Test the connection - updated for SQLAlchemy 2.0
        logger.info("Testing database connection...")
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        logger.info("Database connection successful!")
        return True
    except SQLAlchemyError as e:
        logger.error("Database connection failed: %s", str(e))
        return False


def init_db_test():
    """
    Initialize minimal app configuration for database testing.

    Returns:
        bool: Result of the database connection test.
    """
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)
    init_extensions(app)
    with app.app_context():  # Activate app context
        return test_db_connection()


def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize logger
    logger.info("Initializing Flask application")

    init_extensions(app)

    @app.route("/", methods=["OPTIONS"])
    def options():
        """
        Handle OPTIONS requests for CORS preflight.

        Returns:
            Response: JSON response with CORS headers.
        """
        response = jsonify({"message": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "OPTIONS, GET, POST")
        return response

    @app.route("/test_db", methods=["GET"])
    def test_db_endpoint():
        """
        Endpoint to test the database connection.

        Returns:
            Response: JSON response indicating the result of the database connection test.
        """
        success = test_db_connection()
        if success:
            return jsonify({"message": "Database connection successful!"}), 200
        return jsonify({"error": "Database connection failed"}), 500

    app.register_blueprint(user_bp)
    app.register_blueprint(cron_schedule_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(permission_bp)

    logger.info("Application startup complete")
    return app
