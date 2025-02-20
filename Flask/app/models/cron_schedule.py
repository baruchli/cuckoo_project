"""Module for managing cron schedules in the automated cuckoo system."""
# pylint: disable=too-few-public-methods
from datetime import datetime, timezone
from app.extensions import db


class CronSchedule(db.Model):
    """
    Model representing a cron schedule for device automation.

    Attributes:
        id (int): Primary key for the schedule
        device_id (int): Foreign key referencing the device
        cron_string (str): Cron expression defining the schedule
        creation_timestamp (datetime): When the schedule was created
        user_id (int): Foreign key referencing the user who created the schedule
        activation_timestamp (datetime): When the schedule was last activated
        sound_file (LargeBinary): Binary data for associated sound file
    """

    __tablename__ = "cron_schedules"
    __table_args__ = {"schema": "automated_cuckoo"}

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(
        db.Integer, db.ForeignKey("automated_cuckoo.devices.id"), nullable=False
    )
    cron_string = db.Column(db.String(255), nullable=False)
    creation_timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(
        db.Integer, db.ForeignKey("automated_cuckoo.users.id"), nullable=False
    )
    activation_timestamp = db.Column(db.DateTime)
    sound_file = db.Column(db.LargeBinary)

    def __repr__(self):
        return (
            f"<CronSchedule(id={self.id}, "
            f"device_id={self.device_id}, "
            f"cron='{self.cron_string}')>"
        )
