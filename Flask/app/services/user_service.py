"""
This module provides services for user management, including creating, updating,
retrieving, and deleting users, as well as managing the users table in the database.
"""

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.logger import logger
from app.models.user import User
from app.services import (
    ensure_database_structure,
    ensure_schema,
    TableManagementError,
    common_drop_table,
    get_table_contents,
)


class UserService:
    """
    A service class for managing users in the database.
    """

    @staticmethod
    def create_user(data):
        """
        Creates a new user in the database.

        Args:
            data (dict): A dictionary containing user data (id, username, email).

        Returns:
            dict: A dictionary containing a message and user details if successful.
            Raises ValueError if the user already exists.
        """
        ensure_database_structure(User)

        # Check if the user with the given ID already exists
        existing_user = User.query.filter_by(id=data["id"]).first()
        if existing_user:
            logger.info("User with id %s already exists.", data["id"])
            return {
                "message": "User already exists",
                "user": {
                    "id": existing_user.id,
                    "username": existing_user.username,
                    "email": existing_user.email,
                    "created_at": existing_user.created_at,
                },
            }
        new_user = User(id=data["id"], username=data["username"], email=data["email"])
        db.session.add(new_user)
        try:
            db.session.commit()
            return {
                "message": "User created successfully",
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "created_at": new_user.created_at,
                },
            }
        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to create user - integrity error with id: %s or username: %s",
                data["id"],
                data["username"],
            )
            raise ValueError(
                f"User with id {data['id']}, username {data['username']}"
                f"or email {data['email']} already exists."
            ) from e

    @staticmethod
    def get_user(user_id):
        """
        Retrieves a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            dict: A dictionary containing user details if found.
            tuple: A dictionary with a message and a 404 status code if not found.
        """
        ensure_database_structure(User)
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
        }

    @staticmethod
    def update_user(user_id, data):
        """
        Updates an existing user's details.

        Args:
            user_id (int): The ID of the user to update.
            data (dict): A dictionary containing updated user data (username, email).

        Returns:
            dict: A dictionary containing a success message if successful.
            Raises ValueError if the update fails due to integrity error.
        """
        ensure_database_structure(User)
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404
        user.username = data["username"]
        user.email = data["email"]
        try:
            db.session.commit()
            return {"message": "User updated successfully"}
        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to update user - integrity error with username: %s",
                data["username"],
            )
            raise ValueError(
                f"User with username {data['username']} or email {data['email']} already exists."
            ) from e

    @staticmethod
    def delete_user(user_id):
        """
        Deletes a user by their ID.

        Args:
            user_id (int): The ID of the user to delete.

        Returns:
            dict: A dictionary containing a success message if successful.
            Raises ValueError if the deletion fails.
        """
        ensure_database_structure(User)
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404
        try:
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully"}
        except Exception as e:
            db.session.rollback()
            logger.error("Failed to delete user %s: %s", user_id, str(e))
            raise ValueError(f"Error deleting user: {str(e)}") from e

    @staticmethod
    def get_all_users():
        """
        Retrieves all users from the database.

        Returns:
            list: A list of dictionaries, each containing user details.
            Raises ValueError if fetching users fails.
        """
        ensure_database_structure(User)
        try:
            users = User.query.all()
            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at,
                }
                for user in users
            ]
        except Exception as e:
            logger.error("Failed to fetch users: %s", str(e))
            raise ValueError(f"Error fetching users: {str(e)}") from e

    @staticmethod
    def create_table():
        """
        Creates the users table in the database.

        Raises:
            TableManagementError: If table creation fails.
        """
        ensure_schema()
        try:
            logger.info("Creating users table")
            db.create_all()
            logger.info("Successfully created users table")
        except Exception as e:
            logger.error("Failed to create users table: %s", str(e))
            raise TableManagementError(f"Failed to create table: {str(e)}") from e

    @staticmethod
    def drop_table():
        """
        Drops the users table from the database.

        Returns:
            bool: True if the table was successfully dropped, False otherwise.
        """
        return common_drop_table(User, db, logger)

    @staticmethod
    def get_all_records():
        """
        Retrieves all records from the users table.

        Returns:
            list: A list of dictionaries, each containing user details.
        """
        return get_table_contents(User)
