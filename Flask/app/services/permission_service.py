"""
This module provides services for managing user-device permissions in the database.
It includes functionalities to create, retrieve, update, and delete permissions,
as well as to manage the permissions table schema.
"""

import datetime
from typing import List, Tuple
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app.models.user_device_permission import UserDevicePermission
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


class UserDevicePermissionService:
    """
    Service class for managing user-device permissions in the database.
    """

    @staticmethod
    def create_permission(user_id, device_id):
        """
        Creates a new permission for a user and a device in the database.

        Args:
            user_id (int): The ID of the user.
            device_id (int): The ID of the device.

        Returns:
            UserDevicePermission: The created permission object.

        Raises:
            ValueError: If a permission already exists or there is a constraint violation.
        """
        ensure_database_structure(UserDevicePermission)
        logger.info(
            "Creating new permission for user %s and device %s", user_id, device_id
        )
        permission = UserDevicePermission(
            user_id=user_id,
            device_id=device_id,
            count_used=0,
            date_assigned=datetime.date.today(),
        )
        db.session.add(permission)
        try:
            db.session.commit()
            logger.info("Successfully created permission with ID: %s", permission.id)
            return permission
        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to create permission - integrity error for user_id: %s, device_id: %s",
                user_id,
                device_id,
            )
            raise ValueError(
                "Permission already exists or invalid user/device IDs."
            ) from e

    @staticmethod
    def get_permissions_for_user(user_id):
        """
        Retrieves all permissions for a given user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: A list of all permissions for the user.
        """
        ensure_database_structure(UserDevicePermission)
        logger.debug("Retrieving permissions for user: %s", user_id)
        return UserDevicePermission.query.filter_by(user_id=user_id).all()

    @staticmethod
    def delete_permission(permission_id):
        """
        Deletes a permission from the database.

        Args:
            permission_id (int): The ID of the permission to delete.

        Returns:
            bool: True if the permission was successfully deleted, False otherwise.
        """
        ensure_database_structure(UserDevicePermission)
        logger.info("Deleting permission with ID: %s", permission_id)
        permission = UserDevicePermission.query.get(permission_id)
        if permission:
            db.session.delete(permission)
            db.session.commit()
            logger.info("Successfully deleted permission with ID: %s", permission_id)
            return True
        logger.warning("Permission with ID %s not found", permission_id)
        return False

    @staticmethod
    def update_permission(permission_id, user_id, device_id):
        """
        Updates an existing permission in the database.

        Args:
            permission_id (int): The ID of the permission to update.
            user_id (int): The new user ID for the permission.
            device_id (int): The new device ID for the permission.

        Returns:
            UserDevicePermission: The updated permission object if found, else None.

        Raises:
            ValueError: If there is a constraint violation or invalid user/device IDs.
        """
        ensure_database_structure(UserDevicePermission)
        logger.info("Updating permission with ID: %s", permission_id)
        permission = UserDevicePermission.query.get(permission_id)
        if permission:
            permission.user_id = user_id
            permission.device_id = device_id
            permission.count_used = 0  # Reset count to 0
            permission.date_assigned = (
                datetime.date.today()
            )  # Set to current date without time
            try:
                db.session.commit()
                logger.info(
                    "Successfully updated permission with ID: %s", permission_id
                )
                return permission
            except IntegrityError as e:
                db.session.rollback()
                logger.error(
                    "Failed to update permission - integrity error for user_id: %s, device_id: %s",
                    user_id,
                    device_id,
                )
                raise ValueError(
                    "Invalid user/device IDs or constraint violation."
                ) from e
        logger.warning("Permission with ID %s not found", permission_id)
        return None

    @staticmethod
    def create_table():
        """
        Creates the permissions table in the database.

        Raises:
            TableManagementError: If there is an error creating the table.
        """
        ensure_schema()
        try:
            logger.info("Creating permissions table")
            db.create_all()
            logger.info("Successfully created permissions table")
        except Exception as e:
            logger.error("Failed to create permissions table: %s",{str(e)})
            raise TableManagementError(f"Failed to create table: {str(e)}") from e

    @staticmethod
    def drop_table():
        """
        Drops the permissions table with CASCADE.

        Returns:
            str: A message indicating the result of the table drop.
        """
        return common_drop_table(UserDevicePermission, db, logger)

    @staticmethod
    def get_all_records():
        """
        Returns all records from the permissions table.

        Returns:
            list: A list of all permission records.
        """
        return get_table_contents(UserDevicePermission)

    @staticmethod
    def get_accessible_devices(user_id: int) -> List[Tuple[int, str]]:
        """
        Retrieve devices that are either public or specifically assigned to a user.

        Args:
            user_id (int): The ID of the user to check permissions for.

        Returns:
            List[Tuple[int, str]]: List of tuples containing device IDs and names
                that the user has access to either through public access or specific permissions.
        """
        ensure_database_structure(UserDevicePermission)
        ensure_database_structure(Device)

        logger.debug("Retrieving accessible devices for user: %s", user_id)

        try:
            devices = (
                db.session.query(Device.id, Device.device_name)
                .distinct()
                .outerjoin(UserDevicePermission)
                .filter(
                    or_(
                        Device.public_use.is_(True),
                        UserDevicePermission.user_id == user_id,
                    )
                )
                .all()
            )

            logger.debug(
                "Found %d accessible devices for user %d", len(devices), user_id
            )
            return devices

        except Exception as e:
            logger.error(
                "Error retrieving accessible devices for user %d: %s", user_id, str(e)
            )
            raise ValueError(f"Failed to retrieve accessible devices: {str(e)}") from e
