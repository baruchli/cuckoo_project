"""
Module for user data dataclass.
"""

from dataclasses import dataclass, field, fields
from typing import Optional, List


@dataclass
class ScheduleConfig:
    """
    A dataclass representing cron-style schedule configuration.
    
    Stores schedule components (minute, hour, day, month, day_of_week) as lists of strings.
    Each component can contain specific values, ranges, or special characters (* / -).
    
    Attributes:
        minute (List[str]): Minutes (0-59)
        hour (List[str]): Hours (0-23)
        day (List[str]): Days of month (1-31)
        month (List[str]): Months (1-12)
        day_of_week (List[str]): Days of week (0-6, 0=Sunday)
        
    Example:
        >>> schedule = ScheduleConfig(
        ...     minute=["0", "30"],
        ...     hour=["9", "17"],
        ...     day=["*"],
        ...     month=["1-12"],
        ...     day_of_week=["1-5"]
        ... )
    """
    minute: List[str] = field(default_factory=list)
    hour: List[str] = field(default_factory=list)
    day: List[str] = field(default_factory=list)
    month: List[str] = field(default_factory=list)
    day_of_week: List[str] = field(default_factory=list)

    def is_set(self, component: str) -> bool:
        """
        Check if a specific schedule component is set (non-empty).

        Args:
            component (str): Name of the schedule component to check.

        Returns:
            bool: True if the component is non-empty, False otherwise.

        Raises:
            AttributeError: If the specified component does not exist.
        """
        if not hasattr(self, component):
            raise AttributeError(f"No such component: {component}")

        return bool(getattr(self, component))

    def is_complete(self) -> bool:
        """
        Check if all schedule components have been populated.

        Returns:
            bool: True if all schedule lists are non-empty, False otherwise.
        """
        return all([self.minute, self.hour, self.day, self.month, self.day_of_week])

    def get_set_fields(self) -> List[str]:
        """
        Returns a list of schedule components that have been populated.

        Returns:
            List[str]: List of schedule component names with non-empty lists
        """
        return [
            component
            for component, value in {
                "minute": self.minute,
                "hour": self.hour,
                "day": self.day,
                "month": self.month,
                "day_of_week": self.day_of_week,
            }.items()
            if value
        ]

    def reset(self) -> None:
        """
        Reset all fields to their default values.
        """
        self.minute = []
        self.hour = []
        self.day = []
        self.month = []
        self.day_of_week = []


@dataclass
class ScheduleEntry:
    """
    A dataclass representing a schedule entry.
    
    Stores information about a specific schedule entry including device ID, user ID,
    cron string, and optional sound file path.
    
    Attributes:
        device_id (int): ID of the device
        user_id (int): ID of the user
        cron_string (str): Cron string representing the schedule
        sound_file_path (Optional[str]): Path to the sound file to be played
        
    Example:
        >>> entry = ScheduleEntry(
        ...     device_id=1,
        ...     user_id=42,
        ...     cron_string="0 9 * * 1-5",
        ...     sound_file_path="/path/to/sound.mp3"
        ... )
    """
    device_id: int = field(default_factory=int)
    user_id: int = field(default_factory=int)
    cron_string: str = field(default_factory=str)
    sound_file_path: Optional[str] = field(default_factory=lambda: None)

    def is_set(self, field_name: str) -> bool:
        """
        Check if a specific field is set.

        Args:
            field_name (str): Name of the field to check.

        Returns:
            bool: True if the field is set, False otherwise.

        Raises:
            AttributeError: If the specified field does not exist.
        """
        if not hasattr(self, field_name):
            raise AttributeError(f"No such field: {field_name}")

        value = getattr(self, field_name)

        # Special handling for different types

        if isinstance(value, int):
            return value != 0

        if isinstance(value, str):
            return value != ""

        return value is not None

    def get_set_fields(self) -> List[str]:
        """
        Returns a list of fields that are set.

        Returns:
            List[str]: List of set field names
        """
        return [f.name for f in fields(self) if self.is_set(f.name)]

    def get_unset_fields(self) -> List[str]:
        """
        Returns a list of fields that are not set.

        Returns:
            List[str]: List of unset field names
        """
        return [f.name for f in fields(self) if not self.is_set(f.name)]

    def is_complete(self) -> bool:
        """
        Check if all fields are set.

        Returns:
            bool: True if all fields are set, False otherwise.
        """
        return len(self.get_unset_fields()) == 0

    def reset(self) -> None:
        """
        Reset all fields to their default values.
        """
        self.device_id = 0
        self.user_id = 0
        self.cron_string = ""
        self.sound_file_path = None
