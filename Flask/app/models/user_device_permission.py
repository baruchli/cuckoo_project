"""Module for managing user device permissions in the automated cuckoo system."""
# pylint: disable=too-few-public-methods
from app.extensions import db


class UserDevicePermission(db.Model):
    """
    Model representing permissions for users to access specific devices.

    Attributes:
        id (int): Primary key for the permission record
        user_id (int): Foreign key referencing the user
        device_id (int): Foreign key referencing the device
        count_used (int): Number of times the permission has been used
        date_assigned (Date): Date when the permission was assigned
    """

    __tablename__ = "user_device_permissions"
    __table_args__ = (
        db.UniqueConstraint("user_id", "device_id"),
        {"schema": "automated_cuckoo"},
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("automated_cuckoo.users.id"), nullable=False
    )
    device_id = db.Column(
        db.Integer, db.ForeignKey("automated_cuckoo.devices.id"), nullable=False
    )
    count_used = db.Column(db.Integer, nullable=False)
    date_assigned = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return (f"<UserDevicePermission(id={self.id}, "
                f"user_id={self.user_id}, "
                f"device_id={self.device_id})>")
