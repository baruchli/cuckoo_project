"""
Module for handling permission-related routes in the Flask application.
This module provides endpoints for managing user-device permissions including
creating, reading, updating, and deleting permissions.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.logger import logger
from app.services.permission_service import (
    UserDevicePermissionService,
    TableManagementError,
)


permission_bp = Blueprint("permissions", __name__, url_prefix="/permissions")


# curl -X POST http://127.0.0.1:5000/permissions -H "Content-Type: application/json"
#  -d '{"user_id": "value", "device_id": "value"}'
@permission_bp.route("", methods=["POST"])
def create_permission():
    """
    Create a new permission for a user-device pair.
    """
    try:
        logger.info("Received request to create new permission")
        data = request.get_json()
        if not data:
            logger.warning("Invalid request: missing data")
            return jsonify({"error": "No input data provided"}), 400

        user_id = data.get("user_id")
        device_id = data.get("device_id")

        if not user_id or not device_id:
            logger.warning("Invalid request: missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        permission = UserDevicePermissionService.create_permission(user_id, device_id)
        logger.info("Successfully created permission with ID: %s", permission.id)
        return jsonify({"id": permission.id}), 201
    except ValidationError as e:
        logger.error("Validation error while creating permission: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        logger.error(
            "Database error while creating permission: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error"}), 500


# curl -X GET http://127.0.0.1:5000/permissions/user/<user_id>
@permission_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_permissions(user_id):
    """
    Get all permissions for a specific user.
    """
    permissions = UserDevicePermissionService.get_permissions_for_user(user_id)
    return (
        jsonify(
            [
                {"id": perm.id, "user_id": perm.user_id, "device_id": perm.device_id}
                for perm in permissions
            ]
        ),
        200,
    )


# curl -X DELETE http://127.0.0.1:5000/permissions/<permission_id>
@permission_bp.route("/<int:permission_id>", methods=["DELETE"])
def delete_permission(permission_id):
    """
    Delete a specific permission by its ID.
    """
    if UserDevicePermissionService.delete_permission(permission_id):
        return jsonify({"message": "Permission deleted"}), 204
    return jsonify({"message": "Permission not found"}), 404


# curl -X PUT http://127.0.0.1:5000/permissions/<permission_id>
# -H "Content-Type: application/json"
# -d '{"user_id": "value", "device_id": "value"}'
@permission_bp.route("/<int:permission_id>", methods=["PUT"])
def update_permission(permission_id):
    """
    Update a specific permission by its ID.
    """
    try:
        logger.info("Received request to update permission with ID: %s", permission_id)
        data = request.get_json()
        if not data:
            logger.warning("Invalid request: missing data")
            return jsonify({"error": "No input data provided"}), 400

        user_id = data.get("user_id")
        device_id = data.get("device_id")

        if not user_id or not device_id:
            logger.warning("Invalid request: missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        permission = UserDevicePermissionService.update_permission(
            permission_id, user_id, device_id
        )
        if not permission:
            logger.warning("Permission with ID %s not found", permission_id)
            return jsonify({"error": "Permission not found"}), 404
        logger.info("Successfully updated permission with ID: %s", permission_id)
        return (
            jsonify(
                {
                    "id": permission.id,
                    "user_id": permission.user_id,
                    "device_id": permission.device_id,
                }
            ),
            200,
        )
    except ValidationError as e:
        logger.error("Validation error while updating permission: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        logger.error(
            "Database error while updating permission: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error"}), 500


# curl -X POST http://127.0.0.1:5000/permissions/table
@permission_bp.route("/table", methods=["POST"])
def create_table():
    """
    Create the permissions table in the database.
    """
    try:
        logger.info("Received request to create permissions table")
        UserDevicePermissionService.create_table()
        logger.info("Successfully created permissions table")
        return jsonify({"message": "Permissions table created successfully"}), 201
    except TableManagementError as e:
        logger.error("Error creating permissions table: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        logger.error(
            "Database error while creating permissions table: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error"}), 500


# curl -X DELETE http://127.0.0.1:5000/permissions/table
@permission_bp.route("/table", methods=["DELETE"])
def drop_table():
    """
    Drop the permissions table from the database.
    """
    try:
        logger.info("Received request to drop permissions table")
        UserDevicePermissionService.drop_table()
        logger.info("Successfully dropped permissions table")
        return jsonify({"message": "Permissions table dropped successfully"}), 200
    except TableManagementError as e:
        logger.error("Error dropping permissions table: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        logger.error(
            "Database error while dropping permissions table: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error"}), 500


# curl -X GET http://127.0.0.1:5000/permissions/records
@permission_bp.route("/records", methods=["GET"])
def get_all_records():
    """
    Get all permission records from the database.
    """
    try:
        logger.info("Received request to get all permission records")
        records = UserDevicePermissionService.get_all_records()
        logger.info("Successfully retrieved %s permission records", len(records))
        return (
            jsonify(
                [
                    {
                        "id": record.id,
                        "user_id": record.user_id,
                        "device_id": record.device_id,
                        "date_assigned": record.date_assigned,
                    }
                    for record in records
                ]
            ),
            200,
        )
    except SQLAlchemyError as e:
        logger.error(
            "Database error while getting permission records: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error"}), 500


# curl -X GET http://127.0.0.1:5000/permissions/accessible-devices/<user_id>
@permission_bp.route("/accessible-devices/<int:user_id>", methods=["GET"])
def get_accessible_devices(user_id):
    """
    Get all accessible devices for a specific user.
    """
    try:
        logger.info("Received request to get accessible devices for user: %s", user_id)
        devices = UserDevicePermissionService.get_accessible_devices(user_id)
        logger.info(
            "Successfully retrieved %s accessible devices for user %s",
            len(devices),
            user_id,
        )
        return (
            jsonify(
                [
                    {"device_id": device_id, "device_name": device_name}
                    for device_id, device_name in devices
                ]
            ),
            200,
        )
    except ValueError as e:
        logger.error("Error retrieving accessible devices: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        logger.error(
            "Database error while getting accessible devices: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error"}), 500
