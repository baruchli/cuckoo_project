"""
This module provides services for managing database tables and user operations.
It includes functions to ensure database structure, drop tables, and retrieve table contents.
Custom exceptions for table management, user service, and database errors are also defined.
"""

import logging
from sqlalchemy import inspect, text, select
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from app.extensions import db
from app.logger import logger
from app.models import DB_SCHEMA


# Get the existing formatter and modify it
console_formatter = logger.handlers[0].formatter
old_fmt = getattr(console_formatter, "_fmt")
logger.handlers[0].setFormatter(logging.Formatter("SERVICE: " + old_fmt))


class TableManagementError(Exception):
    """Custom exception for database table management errors."""


class UserServiceError(Exception):
    """Custom exception for user service errors."""


class DatabaseError(Exception):
    """Custom exception for database errors."""


def ensure_database_structure(model_class):
    """Ensures both schema and table exist before performing operations."""
    try:
        inspector = inspect(db.engine)
        # First check if schema exists
        schemas = inspector.get_schema_names()

        if DB_SCHEMA not in schemas:
            logger.info("Schema %s does not exist. Creating...", DB_SCHEMA)
            with current_app.app_context():
                with db.engine.begin() as connection:
                    connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}"))
                    connection.commit()

        # Then check if table exists in the schema
        if not inspector.has_table(model_class.__tablename__, schema=DB_SCHEMA):
            logger.info(
                "Table %s does not exist. Creating...", model_class.__tablename__
            )
            ensure_schema()  # Check schema before creating table
            with current_app.app_context():
                db.create_all()  # Create the table

        return True
    except Exception as e:
        logger.error("Error checking/creating schema or table: %s", str(e))
        raise TableManagementError(f"Schema/table check failed: {str(e)}") from e


def ensure_schema():
    """Ensures schema exists before performing operations."""
    try:
        inspector = inspect(db.engine)
        schemas = inspector.get_schema_names()

        if DB_SCHEMA not in schemas:
            logger.info("Schema %s does not exist. Creating...", DB_SCHEMA)
            with current_app.app_context():
                with db.engine.begin() as connection:
                    connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}"))
                    connection.commit()
        return True
    except Exception as e:
        logger.error("Error checking/creating schema: %s", str(e))
        raise TableManagementError(f"Schema check failed: {str(e)}") from e


def common_drop_table(model, db_par, logger_par):
    """Common method to drop a table with proper logging and error handling."""
    try:
        table_name = model.__table__.name
        schema_name = model.__table__.schema
        full_name = f"{schema_name}.{table_name}" if schema_name else table_name
        logger_par.info(f"Dropping {full_name} table with CASCADE")

        with current_app.app_context():
            # Using text() for raw SQL is still valid in SQLAlchemy 2.0
            stmt = text(f"DROP TABLE IF EXISTS {full_name} CASCADE")
            db_par.session.execute(stmt)
            db_par.session.commit()

        logger_par.info("Table dropped successfully")

    except SQLAlchemyError as e:
        logger_par.error(f"Failed to drop {table_name} table: {str(e)}")
        raise TableManagementError(f"Failed to drop table: {str(e)}") from e


def get_table_contents(model_class):
    """
    Retrieves all records from the specified table.

    Args:
        model_class: SQLAlchemy model class representing the table

    Returns:
        list: List of model instances representing table records

    Raises:
        TableManagementError: If there's an error accessing the table
    """
    try:
        # Ensure table exists before querying
        ensure_database_structure(model_class)

        logger.info("Fetching all records from table %s",model_class.__tablename__)
        with current_app.app_context():
            stmt = select(model_class)
            records = db.session.execute(stmt).scalars().all()
        logger.info(
            "Successfully retrieved %d records from %s", len(records), model_class.__tablename__
        )

        return records

    except Exception as e:
        error_msg = f"Error fetching records from {model_class.__tablename__}: {str(e)}"
        logger.error(error_msg)
        raise TableManagementError(error_msg) from e


# Export these items to be imported by other modules
__all__ = [
    "ensure_database_structure",
    "ensure_schema",
    "TableManagementError",
    "UserServiceError",
    "DatabaseError",
    "common_drop_table",
    "get_table_contents",
]
