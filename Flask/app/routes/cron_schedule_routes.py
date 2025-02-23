"""
Module for handling cron schedule-related routes in the Flask application.
This module provides endpoints for managing cron schedules including creating,
reading, updating, and deleting schedule records.
"""

from io import BytesIO

from flask import Blueprint, jsonify, request, send_file, abort
from marshmallow import ValidationError
from sqlalchemy.exc import DatabaseError

from app.logger import logger
from app.services.cron_schedule_service import (
    CronScheduleService,
    TableManagementError,
    CronSchedule,
)


cron_schedule_bp = Blueprint("cron_schedule", __name__, url_prefix="/cron_schedules")


# curl -X POST http://127.0.0.1:5000/cron_schedules -H "Content-Type:
# application/json" -d '{"key": "value"}'
@cron_schedule_bp.route("", methods=["POST"])
def create_cron_schedule():
    """
    Create a new cron schedule.

    Expects a JSON payload with schedule details in the request body.

    Returns:
        tuple: JSON response with created schedule ID and HTTP status code
               201 on success, 400 on validation error, 500 on server error
    """
    try:
        logger.info("Received request to create new cron schedule")
        data = request.get_json()
        if not data:
            logger.warning("Invalid request: missing data")
            return jsonify({"error": "No input data provided"}), 400

        new_schedule: CronSchedule = CronScheduleService.create_cron_schedule(data)
        if new_schedule:
            logger.info(
                "Successfully created cron schedule with ID: %s", new_schedule.id
            )
            return jsonify({"id": new_schedule.id}), 201
        return jsonify({"error": "Internal server error"}), 500
    except ValidationError as e:
        logger.error("Validation error while creating cron schedule: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        logger.error(
            "Database error while creating cron schedule: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error occurred"}), 500
    except RuntimeError as e:
        logger.error(
            "Runtime error while creating cron schedule: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Application error occurred"}), 500


# curl -X GET http://127.0.0.1:5000/cron_schedules/<schedule_id>
@cron_schedule_bp.route("/<int:schedule_id>", methods=["GET"])
def get_cron_schedule(schedule_id):
    """
    Retrieve a specific cron schedule by ID.

    Args:
        schedule_id (int): The ID of the schedule to retrieve

    Returns:
        tuple: JSON response with schedule details and HTTP status code
               200 on success, 404 if schedule not found
    """
    logger.info("Received request to get cron schedule with ID: %s", schedule_id)
    schedule = CronScheduleService.get_cron_schedule(schedule_id)
    if schedule:
        logger.info("Successfully retrieved cron schedule with ID: %s", schedule_id)
        return (
            jsonify(
                {
                    "id": schedule.id,
                    "device_id": schedule.device_id,
                    "cron_string": schedule.cron_string,
                    "creation_timestamp": schedule.creation_timestamp,
                    "user_id": schedule.user_id,
                    "activation_timestamp": schedule.activation_timestamp,
                }
            ),
            200,
        )
    logger.warning("Cron schedule with ID %s not found", schedule_id)
    return jsonify({"error": "Schedule not found"}), 404


# curl -X PUT http://127.0.0.1:5000/cron_schedules/<schedule_id>
# -H "Content-Type: application/json" -d '{"key": "value"}'
@cron_schedule_bp.route("/<int:schedule_id>", methods=["PUT"])
def update_cron_schedule(schedule_id):
    """
    Update an existing cron schedule.

    Args:
        schedule_id (int): The ID of the schedule to update

    Expects a JSON payload with updated schedule details in the request body.

    Returns:
        tuple: JSON response with updated schedule ID and HTTP status code
               200 on success, 404 if not found, 400 on validation error,
               500 on server error
    """
    try:
        logger.info("Received request to update cron schedule with ID: %s", schedule_id)
        data = request.get_json()
        if not data:
            logger.warning("Invalid request: missing data")
            return jsonify({"error": "No input data provided"}), 400

        updated_schedule = CronScheduleService.update_cron_schedule(schedule_id, data)
        if not updated_schedule:
            logger.warning("Cron schedule with ID %s not found", schedule_id)
            return jsonify({"error": "Schedule not found"}), 404
        logger.info("Successfully updated cron schedule with ID: %s", schedule_id)
        return jsonify({"id": updated_schedule.id}), 200
    except ValidationError as e:
        logger.error("Validation error while updating cron schedule: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        logger.error(
            "Database error while updating cron schedule: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error occurred"}), 500
    except RuntimeError as e:
        logger.error(
            "Runtime error while updating cron schedule: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Application error occurred"}), 500


# curl -X DELETE http://127.0.0.1:5000/cron_schedules/<schedule_id>
@cron_schedule_bp.route("/<int:schedule_id>", methods=["DELETE"])
def delete_cron_schedule(schedule_id):
    """
    Delete a specific cron schedule.

    Args:
        schedule_id (int): The ID of the schedule to delete

    Returns:
        tuple: JSON response and HTTP status code
               204 on successful deletion, 404 if schedule not found
    """
    logger.info("Received request to delete cron schedule with ID: %s", schedule_id)
    if CronScheduleService.delete_cron_schedule(schedule_id):
        logger.info("Successfully deleted cron schedule with ID: %s", schedule_id)
        return jsonify({"message": "Schedule deleted"}), 204
    logger.warning("Cron schedule with ID %s not found", schedule_id)
    return jsonify({"error": "Schedule not found"}), 404


# curl -X GET http://127.0.0.1:5000/cron_schedules
@cron_schedule_bp.route("", methods=["GET"])
def get_all_cron_schedules():
    """
    Retrieve all cron schedules.

    Returns:
        tuple: JSON response with list of all schedules and HTTP status code 200
    """
    logger.info("Received request to get all cron schedules")
    schedules = CronScheduleService.get_all_cron_schedules()
    logger.info("Successfully retrieved %s cron schedules", len(schedules))
    return (
        jsonify(
            [
                {
                    "id": schedule.id,
                    "device_id": schedule.device_id,
                    "cron_string": schedule.cron_string,
                    "creation_timestamp": schedule.creation_timestamp,
                    "user_id": schedule.user_id,
                    "activation_timestamp": schedule.activation_timestamp,
                }
                for schedule in schedules
            ]
        ),
        200,
    )


# curl -X POST http://127.0.0.1:5000/cron_schedules/table
@cron_schedule_bp.route("/table", methods=["POST"])
def create_table():
    """
    Create the cron schedules database table.

    Returns:
        tuple: JSON response and HTTP status code
               201 on successful creation, 400 on table error,
               500 on server error
    """
    try:
        logger.info("Received request to create cron schedules table")
        CronScheduleService.create_table()
        logger.info("Successfully created cron schedules table")
        return jsonify({"message": "Cron schedules table created successfully"}), 201
    except TableManagementError as e:
        logger.error("Error creating cron schedules table: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        logger.error("Database error while creating table: %s", str(e), exc_info=True)
        return jsonify({"error": "Database error occurred"}), 500
    except RuntimeError as e:
        logger.error("Runtime error while creating table: %s", str(e), exc_info=True)
        return jsonify({"error": "Application error occurred"}), 500


# curl -X DELETE http://127.0.0.1:5000/cron_schedules/table
@cron_schedule_bp.route("/table", methods=["DELETE"])
def drop_table():
    """
    Drop the cron schedules database table.

    Returns:
        tuple: JSON response and HTTP status code
               200 on successful deletion, 400 on table error,
               500 on server error
    """
    try:
        logger.info("Received request to drop cron schedules table")
        CronScheduleService.drop_table()
        logger.info("Successfully dropped cron schedules table")
        return jsonify({"message": "Cron schedules table dropped successfully"}), 200
    except TableManagementError as e:
        logger.error("Error dropping cron schedules table: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        logger.error("Database error while dropping table: %s", str(e), exc_info=True)
        return jsonify({"error": "Database error occurred"}), 500
    except RuntimeError as e:
        logger.error("Runtime error while dropping table: %s", str(e), exc_info=True)
        return jsonify({"error": "Application error occurred"}), 500


# curl -X GET http://127.0.0.1:5000/cron_schedules/records
@cron_schedule_bp.route("/records", methods=["GET"])
def get_all_records():
    """
    Retrieve all cron schedule records from the database.

    Returns:
        tuple: JSON response with list of all schedule records and HTTP status code
               200 on success, 500 on server error
    """
    try:
        logger.info("Received request to get all cron schedule records")
        records = CronScheduleService.get_all_records()
        logger.info("Successfully retrieved %s cron schedule records", len(records))
        return (
            jsonify(
                [
                    {
                        "id": record.id,
                        "device_id": record.device_id,
                        "cron_string": record.cron_string,
                        "creation_timestamp": record.creation_timestamp,
                        "user_id": record.user_id,
                        "activation_timestamp": record.activation_timestamp,
                    }
                    for record in records
                ]
            ),
            200,
        )
    except DatabaseError as e:
        logger.error(
            "Database error while retrieving records: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error occurred"}), 500
    except RuntimeError as e:
        logger.error(
            "Runtime error while retrieving records: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Application error occurred"}), 500


# curl -X GET http://127.0.0.1:5000/cron_schedules/user/<user_id>/device/<device_id>
@cron_schedule_bp.route("/user/<int:user_id>/device/<int:device_id>", methods=["GET"])
def get_user_device_schedules(user_id, device_id):
    """
    Retrieve cron schedules for a specific user and device.

    Args:
        user_id (int): The ID of the user
        device_id (int): The ID of the device

    Returns:
        tuple: JSON response with list of schedules and HTTP status code
               200 on success, 404 if no schedules found, 500 on server error
    """
    try:
        logger.info(
            "Received request to get cron schedules for user ID %s and device ID %s",
            user_id,
            device_id,
        )
        schedules = CronScheduleService.get_user_device_schedules(user_id, device_id)
        if schedules:
            logger.info(
                "Successfully retrieved %s cron schedules for user ID %s and device ID %s",
                len(schedules),
                user_id,
                device_id,
            )
            return (
                jsonify(
                    [
                        {
                            "id": schedule.id,
                            "device_id": schedule.device_id,
                            "cron_string": schedule.cron_string,
                            "creation_timestamp": schedule.creation_timestamp,
                            "user_id": schedule.user_id,
                            "activation_timestamp": schedule.activation_timestamp,
                        }
                        for schedule in schedules
                    ]
                ),
                200,
            )
        logger.warning(
            "No cron schedules found for user ID %s and device ID %s",
            user_id,
            device_id,
        )
        return jsonify({"error": "No schedules found"}), 404
    except DatabaseError as e:
        logger.error(
            "Database error while retrieving schedules: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Database error occurred"}), 500
    except RuntimeError as e:
        logger.error(
            "Runtime error while retrieving schedules: %s", str(e), exc_info=True
        )
        return jsonify({"error": "Application error occurred"}), 500


# curl -X GET http://127.0.0.1:5000/cron_schedules/file/<schedule_id>
@cron_schedule_bp.route("/file/<int:schedule_id>", methods=["GET"])
def get_cron_schedule_file(schedule_id):
    """
    Retrieve the sound_file for a specific cron schedule by ID.

    Args:
        schedule_id (int): The ID of the schedule to retrieve the file for

    Returns:
        Response: File response if found, 404 if not found, 500 on server error
    """
    try:
        schedule = CronScheduleService.get_cron_schedule(schedule_id)
        if not schedule or not schedule.sound_file:
            logger.warning("File not found for cron schedule with ID %s", schedule_id)
            abort(404, description="File not found")

        return send_file(
            BytesIO(schedule.sound_file),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=f'schedule_{schedule_id}_file.bin'
        )
    except (DatabaseError, IOError, ValueError) as e:
        logger.error("Error retrieving file for cron schedule with ID %s: %s", schedule_id, str(e))
        abort(500, description=str(e))
