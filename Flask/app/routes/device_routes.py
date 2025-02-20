"""
Module for handling device-related routes in the Flask application.
This module provides endpoints for managing devices including creating,
reading, updating, and deleting device records.
"""

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from app.services.device_service import DeviceService, TableManagementError
from app.logger import logger


devices_bp = Blueprint("devices", __name__, url_prefix="/devices")


# curl -X POST http://127.0.0.1:5000/devices -H "Content-Type: application/json"
# -d '{"id": "1", "device_name": "value", "device_type": "value"}'
@devices_bp.route("", methods=["POST"])
def create_device():
    """
    Create a new device.
    Expects JSON data with 'id', 'device_name', and 'device_type'.
    Returns the created device details.
    """
    try:
        logger.info("Received request to create new device")
        data = request.get_json()
        if not data:
            logger.warning("Invalid request: missing data")
            return jsonify({"error": "No input data provided"}), 400

        device_id = data.get("id")
        device_name = data.get("device_name")
        device_type = data.get("device_type")

        if not device_id or not device_name or not device_type:
            logger.warning("Invalid request: missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        device = DeviceService.create_device(device_id, device_name, device_type)
        logger.info("Successfully created device with ID: %s", device.id)
        return (
            jsonify(
                {
                    "id": device.id,
                    "device_name": device.device_name,
                    "device_type": device.device_type,
                    "public_use": device.public_use,
                }
            ),
            201,
        )
    except ValidationError as e:
        logger.error("Validation error while creating device: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        logger.error("Database error while creating device: %s", str(e), exc_info=True)
        return jsonify({"error": "Database error"}), 500
    except HTTPException as e:
        logger.error("HTTP error while creating device: %s", str(e), exc_info=True)
        return jsonify({"error": "HTTP error"}), e.code or 500


# curl -X GET http://127.0.0.1:5000/devices/<device_id>
@devices_bp.route("/<int:device_id>", methods=["GET"])
def get_device(device_id):
    """
    Get a device by its ID.
    Returns the device details if found.
    """
    logger.info("Received request to get device with ID: %s", device_id)
    device = DeviceService.get_device_by_id(device_id)
    if device:
        logger.info("Successfully retrieved device with ID: %s", device_id)
        return (
            jsonify(
                {
                    "id": device.id,
                    "device_name": device.device_name,
                    "device_type": device.device_type,
                    "public_use": device.public_use,
                }
            ),
            200,
        )
    logger.warning("Device with ID %s not found", device_id)
    return jsonify({"error": "Device not found"}), 404


# curl -X PUT http://127.0.0.1:5000/devices/<device_id> -H "Content-Type: application/json"
# -d '{"device_name": "value", "device_type": "value", "public_use": true}'
@devices_bp.route("/<int:device_id>", methods=["PUT"])
def update_device(device_id):
    """
    Update an existing device.
    Expects JSON data with 'device_name', 'device_type', and 'public_use'.
    Returns the updated device details.
    """
    try:
        logger.info("Received request to update device with ID: %s", device_id)
        data = request.get_json()
        if not data:
            logger.warning("Invalid request: missing data")
            return jsonify({"error": "No input data provided"}), 400

        device_name = data.get("device_name")
        device_type = data.get("device_type")
        public_use = data.get("public_use")

        device = DeviceService.update_device(
            device_id, device_name, device_type, public_use
        )
        if not device:
            logger.warning("Device with ID %s not found", device_id)
            return jsonify({"error": "Device not found"}), 404
        logger.info("Successfully updated device with ID: %s", device_id)
        return (
            jsonify(
                {
                    "id": device.id,
                    "device_name": device.device_name,
                    "device_type": device.device_type,
                    "public_use": device.public_use,
                }
            ),
            200,
        )
    except ValidationError as e:
        logger.error("Validation error while updating device: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        logger.error("Database error while updating device: %s", str(e), exc_info=True)
        return jsonify({"error": "Database error"}), 500
    except HTTPException as e:
        logger.error("HTTP error while updating device: %s", str(e), exc_info=True)
        return jsonify({"error": "HTTP error"}), e.code or 500


# curl -X DELETE http://127.0.0.1:5000/devices/<device_id>
@devices_bp.route("/<int:device_id>", methods=["DELETE"])
def delete_device(device_id):
    """
    Delete a device by its ID.
    Returns a success message if the device is deleted.
    """
    device = DeviceService.delete_device(device_id)
    if device:
        return jsonify({"message": "Device deleted successfully"}), 204
    return jsonify({"error": "Device not found"}), 404


# curl -X POST http://127.0.0.1:5000/devices/table
@devices_bp.route("/table", methods=["POST"])
def create_table():
    """
    Create the devices table.
    Returns a success message if the table is created.
    """
    try:
        logger.info("Received request to create devices table")
        DeviceService.create_table()
        logger.info("Successfully created devices table")
        return jsonify({"message": "Devices table created successfully"}), 201
    except TableManagementError as e:
        logger.error("Error creating devices table: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        logger.error(
            "Database error while creating devices table: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error"}), 500
    except HTTPException as e:
        logger.error(
            "HTTP error while creating devices table: %s", str(e), exc_info=True
        )
        return jsonify({"error": "HTTP error"}), e.code or 500


# curl -X DELETE http://127.0.0.1:5000/devices/table
@devices_bp.route("/table", methods=["DELETE"])
def drop_table():
    """
    Drop the devices table.
    Returns a success message if the table is dropped.
    """
    try:
        logger.info("Received request to drop devices table")
        DeviceService.drop_table()
        logger.info("Successfully dropped devices table")
        return jsonify({"message": "Devices table dropped successfully"}), 200
    except TableManagementError as e:
        logger.error("Error dropping devices table: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        logger.error(
            "Database error while dropping devices table: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error"}), 500
    except HTTPException as e:
        logger.error(
            "HTTP error while dropping devices table: %s", str(e), exc_info=True
        )
        return jsonify({"error": "HTTP error"}), e.code or 500


# curl -X GET http://127.0.0.1:5000/devices/records
@devices_bp.route("/records", methods=["GET"])
def get_all_records():
    """
    Get all device records.
    Returns a list of all devices.
    """
    try:
        logger.info("Received request to get all device records")
        records = DeviceService.get_all_records()
        logger.info("Successfully retrieved %s device records", len(records))
        return (
            jsonify(
                [
                    {
                        "id": record.id,
                        "device_name": record.device_name,
                        "device_type": record.device_type,
                        "public_use": record.public_use,
                    }
                    for record in records
                ]
            ),
            200,
        )
    except SQLAlchemyError as e:
        logger.error(
            "Database error while getting device records: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error"}), 500
    except HTTPException as e:
        logger.error(
            "HTTP error while getting device records: %s", str(e), exc_info=True
        )
        return jsonify({"error": "HTTP error"}), e.code or 500
