"""
Module for building cron schedules.
"""

from typing import List
from app.logger import logger, log_function_call
from app.constants import Constants
from app.user_data_dataclass import ScheduleConfig


def bld_num_list_minutes(minutes: List[str]) -> List[int]:
    """Convert a list of minute strings to a list of integers."""
    try:
        return [int(minute) for minute in minutes]
    except ValueError as e:
        logger.error("Invalid minute format: %s", e)
        raise ValueError("Minutes must be valid integers") from e


def bld_num_list_hours(hours: List[str]) -> List[int]:
    """Convert a list of hour strings to a list of integers."""
    try:
        return [int(hour) for hour in hours]
    except ValueError as e:
        logger.error("Invalid hour format: %s", e)
        raise ValueError("Hours must be valid integers") from e


def bld_num_list_day_of_months(doms: List[str]) -> List[int]:
    """Convert a list of day of month strings to a list of integers."""
    return [int(dom) for dom in doms]


def bld_num_list_months(months: List[str]) -> List[int]:
    """Convert a list of month strings to a list of integers."""
    return [Constants.get_month_names().index(month) + 1 for month in months]


def bld_num_list_day_of_week(dows: List[str]) -> List[int]:
    """Convert a list of day of week strings to a list of integers."""
    return [Constants.get_day_of_week_names().index(dow) for dow in dows]


bld_num_list_methods = {
    "minute": bld_num_list_minutes,
    "hour": bld_num_list_hours,
    "day": bld_num_list_day_of_months,
    "month": bld_num_list_months,
    "day_of_week": bld_num_list_day_of_week,
}


@log_function_call
def bld_cron_token_schedule_info(schedule_info: ScheduleConfig, key: str) -> str:
    """
    Build cron token schedule information.

    Args:
        schedule_info (ScheduleConfig): Schedule configuration object.
        key (str): The key for which to build the cron token.

    Returns:
        str: The cron token for the specified key.
    """
    try:
        values_list = getattr(schedule_info, key)
        if sorted(values_list) == sorted(Constants.get_full_range_dict()[key]):
            return "*"
        return bld_cron_token_from_num_list(bld_num_list_methods[key](values_list))
    except AttributeError as e:
        logger.error("Invalid schedule info key: %s", key)
        raise KeyError(
            f"Invalid schedule key. Must be one of: {list(bld_num_list_methods.keys())}"
        ) from e


@log_function_call
def bld_cron_token_from_num_list(numbers: List[int]) -> str:
    """Build a cron token from a list of numbers."""
    if not numbers:
        return "not set"
    numbers.sort()
    current_start = current_end = numbers[0]
    sequences_and_singles = []

    for num in numbers[1:]:
        if num == current_end + 1:
            current_end = num
        else:
            if current_start == current_end:
                sequences_and_singles.append(current_start)
            else:
                sequences_and_singles.append((current_start, current_end))
            current_start = current_end = num

    if current_start == current_end:
        sequences_and_singles.append(current_start)
    else:
        sequences_and_singles.append((current_start, current_end))
    output_string = ""
    for item in sequences_and_singles:
        if isinstance(item, tuple):
            output_string += f"{item[0]}-{item[1]},"
        else:
            output_string += f"{item},"

    # Remove the trailing comma
    output_string = output_string.rstrip(",")
    return output_string
