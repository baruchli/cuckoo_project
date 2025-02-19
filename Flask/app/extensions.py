"""
This module initializes and configures Flask extensions.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_extensions(app):
    """
    Initialize Flask extensions with the given application.

    Args:
        app (Flask): The Flask application instance.
    """
    db.init_app(app)
