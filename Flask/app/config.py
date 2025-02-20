"""
This module contains the configuration settings for the Flask application.
"""

import os


class Config:
    # pylint: disable=too-few-public-methods
    """
    Configuration class for the Flask application.

    Attributes:
        SQLALCHEMY_DATABASE_URI (str): Database URI for SQLAlchemy.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Flag to track modifications in SQLAlchemy.
    """

    SQLALCHEMY_DATABASE_URI = (f"postgresql://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}" 
    f"@postgres:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
