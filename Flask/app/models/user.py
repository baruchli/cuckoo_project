"""Module for managing user information in the automated cuckoo system."""
# pylint: disable=too-few-public-methods
from datetime import datetime, timezone
from app.extensions import db


class User(db.Model):
    """
    Model representing a user in the system.

    Attributes:
        id (int): Primary key for the user
        username (str): Unique username
        email (str): Unique email address
        created_at (datetime): Timestamp when the user was created
        schedules (relationship): Related cron schedules created by this user
        device_permissions (relationship): Related device permissions for this user
    """
    __tablename__ = "users"
    __table_args__ = {"schema": "automated_cuckoo"}

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    schedules = db.relationship("CronSchedule", backref="user", lazy=True)
    device_permissions = db.relationship(
        "UserDevicePermission", backref="user", lazy=True
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
