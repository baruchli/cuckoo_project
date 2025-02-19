"""
Module containing constants used in the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Contsants for conversation management
NO_VALUES = "-1"
ALL_VALUES = "0"

# Bot states for conversation management
(
    START_MENU,
    DEVICE_MENU,
    DEVICE_PAIR_MENU,
    RECORD_OR_UPLOAD_SOUND_MENU,
    FILE_MENU,
    SCHEDULE_PLAY_MENU,
    SUBMITTED_SCHEDULES_EDIT_MENU,
    EDIT_STORED_SCHEDULE_MENU,
    SET_SCHED_VALUE_MENU,
) = range(9)

(
    PLAY_NOW_SELECT,
    REMOVE_FILE_SELECT,
    MONTH_SELECT,
    DAY_OF_MONTH_SELECT,
    DAY_OF_WEEK_SELECT,
    HOUR_SELECT,
    MINUTE_SELECT,
    CANCEL_SELECT,
) = map(chr, range(9, 17))

(
    START_MENU_CALLBACK,
    DEVICE_MENU_CALLBACK,
    SCHEDULE_PLAY_CALLBACK,
    COMMIT_SCHEDULE_CALLBACK,
    DEVICE_PAIR_CALLBACK,
    RECORD_OR_UPLOAD_SOUND_CALLBACK,
    LIST_SCHEDULED_ENTRIES_CALLBACK,
    PLAY_NOW_CALLBACK,
) = map(chr, range(17, 25))


# Read configuration from environment variables

API_URL = os.getenv("API_URL")
API_PORT = os.getenv("API_PORT")
ACCESSIBLE_DEVICES_ENDPOINT = os.getenv("ACCESSIBLE_DEVICES_ENDPOINT")
SHARE_DIR = os.getenv("SHARE_DIR", "/shared")
CRON_SCHEDULES = os.getenv("CRON_SCHEDULES")
USER_ENDPOINT = os.getenv("USER_ENDPOINT")
DEVICE_ENDPOINT = os.getenv("DEVICE_ENDPOINT")

DEVICE_ACTIONS_RE = r"^device_actions_\d+$"

# User data keys
USER_DATA_RETURN_SESSION = "Return_session"
USER_DATA_DEVICE_MAP = "Device_map"
USER_DATA_SCHEDULE_INFO = "ScheduleInfo"
USER_DATA_SCHEDULE_ENTRY = "ScheduleEntry"
USER_DATA_CURRENT_DEVICE_ID = "Current_device_id"
USER_DATA_SELECTED_DEVICE_NAME = "Selected_device_name"
USER_DATA_LAST_MESSAGE_ID = "last_message_id"
USER_DATA_SECOND_MESSAGE_ID = "second_message_id"
USER_DATA_SELECTED_SCHED_PART = "Selected_sched_part"
DOWNLOAD_SOUND_PREFIX = "download_sound_"
DELETE_FILE_PREFIX = "delete_file_"


class Constants:
    """
    Class representing some constants.
    """

    _minutes_gap = 1
    _month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    _day_of_week_names = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    day_of_week_names = list(_day_of_week_names)
    month_names = list(_month_names)

    _days_re_pattern = r"^(-1|[0-9]|1?[0-9]|2[0-9]|3[0-1])$"
    _days_of_week_re_pattern = r"^-1$|^0$|" + "|".join(
        "^" + dow + "$" for dow in _day_of_week_names
    )
    _months_re_pattern = r"^-1$|^0$|" + "|".join(
        "^" + month + "$" for month in _month_names
    )
    _minutes_re_pattern = r"^-1$|^0$|" + r"^minute_(?:[0-9]|[1-5][0-9]|60)$"
    _hours_re_pattern = r"^-1$|^0$|" + r"^hour_(?:[0-9]|1[0-9]|2[0-3])$"
    _sced_edit_entry_re_pattern = r"^[1-9]\d*_sched_edit$"
    _download_soubnd_re_pattern = rf"^{DOWNLOAD_SOUND_PREFIX}[1-9]\d*$"
    _delete_file_re_pattern = rf"^{DELETE_FILE_PREFIX}[1-9]\d*$"

    _value_pattern_dict = {
        "day": _days_re_pattern,
        "day_of_week": _days_of_week_re_pattern,
        "month": _months_re_pattern,
        "hour": _hours_re_pattern,
        "minute": _minutes_re_pattern,
    }

    _full_range_dict = {
        "day": [str(i) for i in range(1, 32)],
        "day_of_week": list(_day_of_week_names),
        "month": list(_month_names),
        "hour": [str(i) for i in range(0, 25)],
        "minute": [str(i) for i in range(0, 61, _minutes_gap)],
    }

    @classmethod
    def get_month_names(cls):
        """Get month names."""
        return cls._month_names

    @classmethod
    def get_day_of_week_names(cls):
        """Get day of week names."""
        return cls._day_of_week_names

    @classmethod
    def get_all_re_patterns_or_conditioned(cls):
        """Get all regex patterns or conditioned."""
        return (
            f"{cls._days_re_pattern}|{cls._months_re_pattern}|{cls._days_of_week_re_pattern}|"
            f"{cls._minutes_re_pattern}|{cls._hours_re_pattern}"
        )

    @classmethod
    def get_value_pattern_dict(cls):
        """Get value pattern dictionary."""
        return cls._value_pattern_dict

    @classmethod
    def get_full_range_dict(cls):
        """Get full range dictionary."""
        return cls._full_range_dict

    @classmethod
    def get_minutes_gap(cls):
        """Get minutes gap."""
        return cls._minutes_gap

    @classmethod
    def get_sched_edit_entry_re_pattern(cls):
        """Get scheduled edit entry regex pattern."""
        return cls._sced_edit_entry_re_pattern

    @classmethod
    def get_download_sound_re_pattern(cls):
        """Get download sound regex pattern."""
        return cls._download_soubnd_re_pattern

    @classmethod
    def get_delete_file_re_pattern(cls):
        """Get delete file regex pattern."""
        return cls._delete_file_re_pattern

    @classmethod
    def get_minutes_rows(cls):
        """Get minutes rows."""
        return 6

    @classmethod
    def get_minutes_lines(cls):
        """Get minutes lines."""
        return 10
