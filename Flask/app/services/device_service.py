"""
This module provides services for managing devices in the database.
It includes functionalities to create, retrieve, update, and delete devices,
as well as to manage the devices table schema.
"""

from sqlalchemy.exc import IntegrityError

from app.models.device import Device
from app.extensions import db
from app.logger import logger
from app.services import (
    ensure_database_structure,
    ensure_schema,
    TableManagementError,
    common_drop_table,
    get_table_contents,
)


class DeviceService:
    """
    Service class for managing devices in the database.
    """

    @staticmethod
    def create_device(device_id, device_name, device_type, public_use=False):
        """
        Creates a new device in the database.

        Args:
            device_id (str): The ID of the device.
            device_name (str): The name of the device.
            device_type (str): The type of the device.
            public_use (bool, optional): Whether the device is for public use. Defaults to False.

        Returns:
            Device: The created device object.

        Raises:
            ValueError: If a device with the same name already exists
            or there is a constraint violation.
        """
        ensure_database_structure(Device)
        logger.info("Creating new device with ID: %s, name: %s", device_id, device_name)
        new_device = Device(
            id=device_id,
            device_name=device_name,
            device_type=device_type,
            public_use=public_use,
        )
        db.session.add(new_device)
        try:
            db.session.commit()
            logger.info("Successfully created device with ID: %s", new_device.id)
            return new_device
        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to create device - integrity error with name: %s", device_name
            )
            raise ValueError(
                f"Device with name {device_name} already exists or constraint violation."
            ) from e

    @staticmethod
    def get_all_records():
        """
        Returns all records from the devices table.

        Returns:
            list: A list of all device records.
        """
        return get_table_contents(Device)

    @staticmethod
    def get_device_by_id(device_id):
        """
        Retrieves a device by its ID.

        Args:
            device_id (str): The ID of the device to retrieve.

        Returns:
            Device: The device object if found, else None.
        """
        ensure_database_structure(Device)
        logger.debug("Retrieving device with ID: %s", device_id)
        return Device.query.get(device_id)

    @staticmethod
    def update_device(device_id, device_name, device_type, public_use=None):
        """
        Updates an existing device in the database.

        Args:
            device_id (str): The ID of the device to update.
            device_name (str): The new name of the device.
            device_type (str): The new type of the device.
            public_use (bool, optional): The new public use status of the device. Defaults to None.

        Returns:
            Device: The updated device object if found, else None.

        Raises:
            ValueError: If a device with the same name already exists
              or there is a constraint violation.
        """
        ensure_database_structure(Device)
        logger.info("Updating device with ID: %s", device_id)
        device = Device.query.get(device_id)
        if device:
            device.device_name = device_name
            device.device_type = device_type
            if public_use is not None:
                device.public_use = public_use
            try:
                db.session.commit()
                logger.info("Successfully updated device with ID: %s", device_id)
                return device
            except IntegrityError as e:
                db.session.rollback()
                logger.error(
                    "Failed to update device - integrity error with name: %s",
                    device_name,
                )
                raise ValueError(
                    f"Device with name {device_name} already exists or constraint violation."
                ) from e
        logger.warning("Device with ID %s not found", device_id)
        return None

    @staticmethod
    def delete_device(device_id):
        """
        Deletes a device from the database.

        Args:
            device_id (str): The ID of the device to delete.

        Returns:
            dict: A message indicating the result of the deletion.

        Raises:
            ValueError: If the device is not found or there is an error during deletion.
        """
        ensure_database_structure(Device)
        logger.info("Deleting device with ID: %s", device_id)
        device = Device.query.get(device_id)
        if not device:
            logger.warning("Device with ID %s not found", device_id)
            raise ValueError("Device not found.")

        try:
            db.session.delete(device)
            db.session.commit()
            logger.info("Successfully deleted device with ID: %s", device_id)
            return {"message": "Device deleted successfully"}
        except Exception as e:
            db.session.rollback()
            logger.error("Failed to delete device %s: %s", device_id, str(e))
            raise ValueError(f"Error deleting device: {str(e)}") from e

    @staticmethod
    def create_table():
        """
        Creates the devices table in the database.

        Raises:
            TableManagementError: If there is an error creating the table.
        """
        ensure_schema()
        try:
            logger.info("Creating devices table")
            db.create_all()
            logger.info("Successfully created devices table")
        except Exception as e:
            logger.error("Failed to create devices table: %s", str(e))
            raise TableManagementError(f"Failed to create table: {str(e)}") from e

    @staticmethod
    def drop_table():
        """
        Drops the devices table from the database with CASCADE.

        Returns:
            str: A message indicating the result of the table drop.
        """
        return common_drop_table(Device, db, logger)
