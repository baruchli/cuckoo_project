"""Module for managing device information in the automated cuckoo system."""

# pylint: disable=too-few-public-methods
from datetime import datetime, timezone
from app.extensions import db


class Device(db.Model):
    """
    Model representing a device in the system.

    Attributes:
        id (int): Primary key for the device
        device_name (str): Name of the device
        device_type (str): Type/category of the device
        created_at (datetime): Timestamp when the device was created
        public_use (bool): Flag indicating if device is available for public use
        schedules (relationship): Related cron schedules for this device
        user_permissions (relationship): Related user permissions for this device
    """

    __tablename__ = "devices"
    __table_args__ = {"schema": "automated_cuckoo"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    device_name = db.Column(db.String(255), nullable=False)
    device_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    public_use = db.Column(db.Boolean, default=False)

    # Relationships
    schedules = db.relationship("CronSchedule", backref="device", lazy=True)
    user_permissions = db.relationship(
        "UserDevicePermission", backref="device", lazy=True
    )

    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.device_name}', type='{self.device_type}')>"
