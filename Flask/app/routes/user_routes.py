"""
Module for handling user-related routes in the Flask application.
This module provides endpoints for managing users including creating,
reading, updating, and deleting user records.
"""

from flask import Blueprint, request, jsonify
from werkzeug.exceptions import NotFound, BadRequest
from app.logger import logger
from app.services.user_service import UserService

from app.services import (
    TableManagementError,
    UserServiceError,
    DatabaseError,
)


user_bp = Blueprint("users", __name__, url_prefix="/users")


# curl -X POST http://127.0.0.1:5000/users -H "Content-Type: application/json"
# -d '{"id": 1, "username": "example", "email": "example@example.com"}'
@user_bp.route("", methods=["POST"])
def create_user():
    """Endpoint to create a new user."""
    try:
        logger.info("Received request to create new user")
        data = request.get_json()
        if not data:
            logger.warning("Invalid request: missing data")
            raise BadRequest("No input data provided")

        # Validate required fields
        required_fields = ["id", "username", "email"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")

        # Validate id is integer
        try:
            data["id"] = int(data["id"])
        except (ValueError, TypeError) as exc:
            raise BadRequest("ID must be an integer") from exc

        result = UserService.create_user(data)
        logger.info("Successfully created new user with ID: %s", data["id"])
        return jsonify(result), 201
    except BadRequest as e:
        logger.error("Bad request error while creating user: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        logger.error("Validation error while creating user: %s", str(e))
        return jsonify({"error": str(e)}), 400


# curl -X GET http://127.0.0.1:5000/users/<user_id>
@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Endpoint to get a user by ID."""
    try:
        logger.info("Received request to get user with ID: %s", user_id)
        result = UserService.get_user(user_id)
        if not result:
            logger.warning("User with ID %s not found", user_id)
            raise NotFound(f"User with id {user_id} not found")
        logger.info("Successfully retrieved user with ID: %s", user_id)
        return jsonify(result), 200
    except NotFound as e:
        logger.error("Not found error while getting user: %s", str(e))
        return jsonify({"error": str(e)}), 404


# curl -X PUT http://127.0.0.1:5000/users/<user_id> -H "Content-Type: application/json"
# -d '{"username": "new_username", "email": "new_email@example.com"}'
@user_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """Endpoint to update a user by ID."""
    try:
        logger.info("Received request to update user with ID: %s", user_id)
        data = request.get_json()
        if not data:
            logger.warning("Invalid request: missing data")
            raise BadRequest("No input data provided")
        result = UserService.update_user(user_id, data)
        logger.info("Successfully updated user with ID: %s", user_id)
        return jsonify(result), 200
    except NotFound as e:
        logger.error("Not found error while updating user: %s", str(e))
        return jsonify({"error": str(e)}), 404
    except BadRequest as e:
        logger.error("Bad request error while updating user: %s", str(e))
        return jsonify({"error": str(e)}), 400


# curl -X DELETE http://127.0.0.1:5000/users/<user_id>
@user_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Endpoint to delete a user by ID."""
    try:
        logger.info("Received request to delete user with ID: %s", user_id)
        result = UserService.delete_user(user_id)
        logger.info("Successfully deleted user with ID: %s", user_id)
        return jsonify(result), 204
    except NotFound as e:
        logger.error("Not found error while deleting user: %s", str(e))
        return jsonify({"error": str(e)}), 404


# curl -X GET http://127.0.0.1:5000/users
@user_bp.route("", methods=["GET"])
def get_all_users():
    """Endpoint to get all users."""
    try:
        logger.info("Received request to get all users")
        result = UserService.get_all_users()
        logger.info("Successfully retrieved %s users", len(result))
        return jsonify(result), 200
    except (UserServiceError, DatabaseError) as e:
        logger.error(
            "Service or database error while getting users: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Internal server error"}), 500


# curl -X POST http://127.0.0.1:5000/users/table
@user_bp.route("/table", methods=["POST"])
def create_table():
    """Endpoint to create the users table."""
    try:
        logger.info("Received request to create users table")
        UserService.create_table()
        logger.info("Successfully created users table")
        return jsonify({"message": "Users table created successfully"}), 201
    except TableManagementError as e:
        logger.error("Error creating users table: %s", str(e))
        return jsonify({"error": str(e)}), 400


# curl -X DELETE http://127.0.0.1:5000/users/table
@user_bp.route("/table", methods=["DELETE"])
def drop_table():
    """Endpoint to drop the users table."""
    try:
        logger.info("Received request to drop users table")
        UserService.drop_table()
        logger.info("Successfully dropped users table")
        return jsonify({"message": "Users table dropped successfully"}), 200
    except TableManagementError as e:
        logger.error("Error dropping users table: %s", str(e))
        return jsonify({"error": str(e)}), 400


# curl -X GET http://127.0.0.1:5000/users/records
@user_bp.route("/records", methods=["GET"])
def get_all_records():
    """Endpoint to get all user records."""
    try:
        logger.info("Received request to get all user records")
        records = UserService.get_all_records()
        logger.info("Successfully retrieved %s user records", len(records))
        return (
            jsonify(
                [
                    {
                        "id": record.id,
                        "username": record.username,
                        "email": record.email,
                        "created_at": record.created_at,
                    }
                    for record in records
                ]
            ),
            200,
        )
    except (UserServiceError, DatabaseError) as e:
        logger.error(
            "Service or database error while getting user records: %s",
            str(e),
            exc_info=True,
        )
        return jsonify({"error": "An unexpected error occurred"}), 500
