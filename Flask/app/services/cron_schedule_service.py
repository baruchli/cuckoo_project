"""
This module provides the CronScheduleService class for managing cron schedule operations.

The CronScheduleService class includes methods for creating, retrieving, updating, and deleting
cron schedules, as well as handling associated file operations and database interactions.
"""

import os
from sqlalchemy.exc import IntegrityError
from flask import jsonify

from app.models.cron_schedule import CronSchedule
from app.extensions import db
from app.logger import logger
from app.services import (
    ensure_database_structure,
    ensure_schema,
    TableManagementError,
    common_drop_table,
    get_table_contents,
)


class CronScheduleService:
    """Service class for managing cron schedule operations.

    This class provides methods to create, manage and handle cron schedules
    including file operations and database interactions.
    """

    @staticmethod
    def create_cron_schedule(data):
        """Create a new cron schedule with associated sound file.

        Args:
            data (dict): Dictionary containing schedule data including:
                - sound_file (str): Path to the sound file to be used

        Returns:
            CronSchedule|None: Created schedule object or None if operation fails

        Raises:
            Exception: If file operations or database operations fail
        """
        ensure_database_structure(CronSchedule)
        logger.info("Creating new cron schedule")
        sound_file_path = data.get("sound_file")
        binary_data = None

        # Verify file exists
        if not os.path.exists(sound_file_path):
            logger.error("Can find a file at location %s", sound_file_path)
            return None
        try:
            with open(sound_file_path, "rb") as file:
                binary_data = file.read()
                logger.info("Opened file %s", sound_file_path)
        except OSError as e:
            db.session.rollback()
            logger.error("Error: %s", str(e))
            return jsonify({"error": str(e)}), 500
        new_schedule = CronSchedule(
            device_id=data["device_id"],
            cron_string=data["cron_string"],
            user_id=data["user_id"],
            activation_timestamp=data.get("activation_timestamp"),
            sound_file=binary_data,
        )
        db.session.add(new_schedule)
        try:
            db.session.commit()
            logger.info(
                "Successfully created cron schedule with ID: %s", new_schedule.id
            )
            return new_schedule
        except IntegrityError as e:
            db.session.rollback()
            logger.error("Failed to create cron schedule - integrity error")
            raise ValueError(
                "Invalid foreign key references or constraint violation."
            ) from e

    @staticmethod
    def get_cron_schedule(schedule_id):
        """Retrieve a cron schedule by its ID.

        Args:
            schedule_id (int): ID of the cron schedule to retrieve

        Returns:
            CronSchedule|None: The retrieved cron schedule or None if not found
        """
        ensure_database_structure(CronSchedule)
        logger.debug("Retrieving cron schedule with ID: %s", schedule_id)
        return CronSchedule.query.get(schedule_id)

    @staticmethod
    def update_cron_schedule(schedule_id, data):
        """Update an existing cron schedule.

        Args:
            schedule_id (int): ID of the cron schedule to update
            data (dict): Dictionary containing updated schedule data

        Returns:
            CronSchedule|None: The updated schedule object or None if not found

        Raises:
            ValueError: If there is an integrity error during the update
        """
        ensure_database_structure(CronSchedule)
        logger.info("Updating cron schedule with ID: %s", schedule_id)
        schedule = CronSchedule.query.get(schedule_id)
        if schedule:
            schedule.device_id = data.get("device_id", schedule.device_id)
            schedule.cron_string = data.get("cron_string", schedule.cron_string)
            schedule.activation_timestamp = data.get(
                "activation_timestamp", schedule.activation_timestamp
            )
            schedule.sound_file = data.get("sound_file", schedule.sound_file)
            try:
                db.session.commit()
                logger.info(
                    "Successfully updated cron schedule with ID: %s", schedule_id
                )
                return schedule
            except IntegrityError as e:
                db.session.rollback()
                logger.error("Failed to update cron schedule - integrity error")
                raise ValueError(
                    "Invalid foreign key references or constraint violation."
                ) from e
        logger.warning("Cron schedule with ID %s not found", schedule_id)
        return None

    @staticmethod
    def delete_cron_schedule(schedule_id):
        """Delete a cron schedule by its ID.

        Args:
            schedule_id (int): ID of the cron schedule to delete

        Returns:
            bool: True if the schedule was deleted, False if not found
        """
        ensure_database_structure(CronSchedule)
        logger.info("Deleting cron schedule with ID: %s", schedule_id)
        schedule = CronSchedule.query.get(schedule_id)
        if schedule:
            db.session.delete(schedule)
            db.session.commit()
            logger.info("Successfully deleted cron schedule with ID: %s", schedule_id)
            return True
        logger.warning("Cron schedule with ID %s not found", schedule_id)
        return False

    @staticmethod
    def get_all_cron_schedules():
        """Retrieve all cron schedules.

        Returns:
            list: List of all cron schedules
        """
        ensure_database_structure(CronSchedule)
        logger.debug("Retrieving all cron schedules")
        return CronSchedule.query.all()

    @staticmethod
    def create_table():
        """Create the cron schedules table."""
        ensure_schema()
        try:
            logger.info("Creating cron schedules table")
            db.create_all()
            logger.info("Successfully created cron schedules table")
        except Exception as e:
            logger.error("Failed to create cron schedules table: %s", str(e))
            raise TableManagementError(f"Failed to create table: {str(e)}") from e

    @staticmethod
    def drop_table():
        """Drop the cron schedules table with CASCADE."""
        return common_drop_table(CronSchedule, db, logger)

    @staticmethod
    def get_all_records():
        """Retrieve all records from the cron schedules table.

        Returns:
            list: List of all records from the cron schedules table
        """
        return get_table_contents(CronSchedule)

    @staticmethod
    def get_user_device_schedules(user_id, device_id):
        """Get all cron schedules for a specific user and device.

        Args:
            user_id (int): ID of the user
            device_id (int): ID of the device

        Returns:
            list: List of CronSchedule objects matching the criteria

        Raises:
            Exception: If database query fails
        """
        logger.info(
            "Fetching schedules for user_id=%s and device_id=%s", user_id, device_id
        )
        try:
            schedules = CronSchedule.query.filter_by(
                user_id=user_id, device_id=device_id
            ).all()
            logger.info("Found %d schedules", len(schedules))
            return schedules
        except Exception as e:
            logger.error("Error fetching schedules: %s", str(e))
            raise
