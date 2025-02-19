"""
Module for handling schedule buttons.
"""

from typing import List

from telegram import InlineKeyboardButton

from app.constants import Constants

from app.utils import (
    set_button_selection,
)
from app.user_data_dataclass import ScheduleConfig
from app.constants import ALL_VALUES, NO_VALUES


def inline_day_of_week_buttons(
    schedule_info: ScheduleConfig,
) -> List[List[InlineKeyboardButton]]:
    """
    Generate inline buttons for selecting days of the week.

    Args:
        schedule_info (ScheduleConfig): The schedule configuration.

    Returns:
        List[List[InlineKeyboardButton]]: Inline buttons for days of the week.
    """
    day_of_week_buttons = [
        [InlineKeyboardButton("Any day of week", callback_data=ALL_VALUES)],
        [InlineKeyboardButton("Clear day of week", callback_data=NO_VALUES)],
    ]
    for i in range(0, len(Constants.get_day_of_week_names()) - 1, 2):
        dow_button_seria = []
        for j in range(2):
            day_of_week_names_index = i + j
            day_of_week_name = Constants.get_day_of_week_names()[
                day_of_week_names_index
            ]
            select = day_of_week_name in schedule_info.day_of_week
            day_of_week_name = set_button_selection(day_of_week_name, select)
            dow_button_seria.append(
                InlineKeyboardButton(
                    day_of_week_name,
                    callback_data=Constants.get_day_of_week_names()[
                        day_of_week_names_index
                    ],
                )
            )
        day_of_week_buttons.append(dow_button_seria)
    day_of_week_name = Constants.get_day_of_week_names()[-1]
    select = day_of_week_name in schedule_info.day_of_week
    day_of_week_name = set_button_selection(day_of_week_name, select)
    day_of_week_buttons.append(
        [
            InlineKeyboardButton(
                day_of_week_name,
                callback_data=Constants.get_day_of_week_names()[-1],
            )
        ]
    )
    day_of_week_buttons.append(
        [InlineKeyboardButton("« Accept setting", callback_data="back")]
    )
    return day_of_week_buttons


def inline_month_buttons(
    schedule_info: ScheduleConfig,
) -> List[List[InlineKeyboardButton]]:
    """
    Generate inline buttons for selecting months.

    Args:
        schedule_info (ScheduleConfig): The schedule configuration.

    Returns:
        List[List[InlineKeyboardButton]]: Inline buttons for months.
    """
    month_buttons = [
        [InlineKeyboardButton("Any month", callback_data=ALL_VALUES)],
        [InlineKeyboardButton("Clear month selection", callback_data=NO_VALUES)],
    ]
    for i in range(0, len(Constants.get_month_names()), 3):
        month_button_seria = []
        for j in range(3):
            month_name_index = i + j
            month_name = Constants.get_month_names()[month_name_index]
            select = month_name in schedule_info.month
            month_name = set_button_selection(month_name, select)
            month_button_seria.append(
                InlineKeyboardButton(
                    month_name,
                    callback_data=Constants.get_month_names()[month_name_index],
                )
            )
        month_buttons.append(month_button_seria)
    month_buttons.append(
        [InlineKeyboardButton("« Accept setting", callback_data="back")]
    )
    return month_buttons


def inline_select_day_of_month_buttons(
    schedule_info: ScheduleConfig,
) -> List[List[InlineKeyboardButton]]:
    """
    Generate inline buttons for selecting days of the month.

    Args:
        schedule_info (ScheduleConfig): The schedule configuration.

    Returns:
        List[List[InlineKeyboardButton]]: Inline buttons for days of the month.
    """
    day_buttons = [
        [InlineKeyboardButton("Any day of the month", callback_data=ALL_VALUES)],
        [InlineKeyboardButton("No day of the month", callback_data=NO_VALUES)],
    ]
    for week in range(5):
        week_buttons = []
        for day in range(1, 8):
            date = week * 7 + day
            if date <= 31:
                day_of_mounth_name = str(date)
                select = day_of_mounth_name in schedule_info.day
                day_of_mounth_name = set_button_selection(day_of_mounth_name, select)
                week_buttons.append(
                    InlineKeyboardButton(
                        day_of_mounth_name,
                        callback_data=str(date),
                    )
                )  # , parse_mode="MarkdownV2"  not supported in 13.15
        day_buttons.append(week_buttons)
    day_buttons.append([InlineKeyboardButton("« Accept setting", callback_data="back")])
    return day_buttons


def inline_select_hour_buttons(
    schedule_info: ScheduleConfig,
) -> List[List[InlineKeyboardButton]]:
    """
    Generate inline buttons for selecting hours.

    Args:
        schedule_info (ScheduleConfig): The schedule configuration.

    Returns:
        List[List[InlineKeyboardButton]]: Inline buttons for hours.
    """
    hour_buttons = [
        [InlineKeyboardButton("Any hour", callback_data=ALL_VALUES)],
        [InlineKeyboardButton("No hour", callback_data=NO_VALUES)],
    ]
    for i in range(4):
        line_hours_buttons = []
        for j in range(6):
            hour_index = i * 6 + j
            hour_name = str(hour_index)
            select = hour_name in schedule_info.hour
            hour_name = set_button_selection(hour_name, select)
            line_hours_buttons.append(
                InlineKeyboardButton(
                    hour_name,
                    callback_data="hour_" + str(hour_index),
                )
            )
        hour_buttons.append(line_hours_buttons)
    hour_buttons.append(
        [InlineKeyboardButton("« Accept setting", callback_data="back")]
    )
    return hour_buttons


def inline_select_minute_buttons(
    schedule_info: ScheduleConfig,
) -> List[List[InlineKeyboardButton]]:
    """
    Generate inline buttons for selecting minutes.

    Args:
        schedule_info (ScheduleConfig): The schedule configuration.

    Returns:
        List[List[InlineKeyboardButton]]: Inline buttons for minutes.
    """
    minute_buttons = [
        [InlineKeyboardButton("Any minute", callback_data=ALL_VALUES)],
        [InlineKeyboardButton("No minute", callback_data=NO_VALUES)],
    ]
    for i in range(10):
        line_minutes_buttons = []
        for j in range(6):
            minute_index = i * 6 + j
            minute_name = str(minute_index)
            select = minute_name in schedule_info.minute
            minute_name = set_button_selection(minute_name, select)
            line_minutes_buttons.append(
                InlineKeyboardButton(
                    minute_name,
                    callback_data="minute_" + str(minute_index),
                )
            )
        minute_buttons.append(line_minutes_buttons)
    minute_buttons.append(
        [InlineKeyboardButton("« Accept setting", callback_data="back")]
    )
    return minute_buttons
