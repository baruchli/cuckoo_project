"""Schedule menu module for handling schedule-related operations"""

import re
import os
import datetime
from typing import Dict, Any, cast

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ConversationHandler, CallbackContext
from telegram.constants import ParseMode
from cron_descriptor import get_description

from app.logger import (
    logger,
    log_function_call,
    callback_query_check,
    callback_query_check_no_await,
)
from app.constants import (
    NO_VALUES,
    ALL_VALUES,
    USER_DATA_SCHEDULE_INFO,
    USER_DATA_SCHEDULE_ENTRY,
    USER_DATA_SELECTED_SCHED_PART,
    USER_DATA_SELECTED_DEVICE_NAME,
    MONTH_SELECT,
    DAY_OF_MONTH_SELECT,
    DAY_OF_WEEK_SELECT,
    HOUR_SELECT,
    MINUTE_SELECT,
    CANCEL_SELECT,
    SET_SCHED_VALUE_MENU,
    SCHEDULE_PLAY_MENU,
    START_MENU_CALLBACK,
    COMMIT_SCHEDULE_CALLBACK,
    DEVICE_MENU_CALLBACK,
    RECORD_OR_UPLOAD_SOUND_MENU,
    Constants,
)
from app.cuckoo_cron_build import bld_cron_token_schedule_info
from app.sched_buttons import (
    inline_day_of_week_buttons,
    inline_month_buttons,
    inline_select_day_of_month_buttons,
    inline_select_hour_buttons,
    inline_select_minute_buttons,
)
from app.user_data_dataclass import ScheduleConfig, ScheduleEntry
from app.flask_connector import create_cron_schedule
from app.utils import set_button_selection, get_sound_menu_keyboard


input_strings = {
    DAY_OF_MONTH_SELECT: "Day of Month",
    MONTH_SELECT: "Month",
    DAY_OF_WEEK_SELECT: "Day of week",
    HOUR_SELECT: "Hour",
    MINUTE_SELECT: "minute",
}

user_action_keys = {
    DAY_OF_MONTH_SELECT: "day",
    DAY_OF_WEEK_SELECT: "day_of_week",
    MONTH_SELECT: "month",
    HOUR_SELECT: "hour",
    MINUTE_SELECT: "minute",
}


@callback_query_check
@log_function_call
async def display_schedule_menu(update: Update, context: CallbackContext) -> int:
    """Display Schedule menu with configurable time options.

    Args:
        update: Telegram update object
        context: Callback context containing user data

    Returns:
        int: Conversation state identifier

    Raises:
        KeyError: If required user data is missing
    """

    user_data = cast(Dict[str, Any], context.user_data)
    query = cast(CallbackQuery,update.callback_query)
    schedule_info = get_schedule_info(user_data)
    user_data[USER_DATA_SCHEDULE_INFO] = schedule_info

    button_keys, button_labels, button_callbacks = get_button_keys_labels_callbacks()
    cron_string = build_cron_string(schedule_info, button_keys)
    keyboard = create_buttons(
        schedule_info, button_keys, button_labels, button_callbacks
    )

    can_schedule = schedule_info.is_complete()
    if can_schedule:
        schedule_entry: ScheduleEntry = user_data[USER_DATA_SCHEDULE_ENTRY]
        schedule_entry.cron_string = cron_string
    logger.warning("can_schedule is %s", can_schedule)
    if can_schedule and schedule_info.is_complete():
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Commit the schedule", callback_data=f"{COMMIT_SCHEDULE_CALLBACK}"
                )
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton("🔙 Back", callback_data=CANCEL_SELECT),
            InlineKeyboardButton("🔁 Restart", callback_data=f"{START_MENU_CALLBACK}"),
        ]
    )
    markup = InlineKeyboardMarkup(keyboard)
    sched_description = (
        "Scheduler settings incomplete"
        if not can_schedule
        else get_description(cron_string)
    )
    await query.edit_message_text(
        sched_description,
        reply_markup=markup,
    )
    return SCHEDULE_PLAY_MENU


def get_schedule_info(user_data: dict) -> ScheduleConfig:
    """Retrieve and process schedule information from user data."""
    schedule_info = user_data[USER_DATA_SCHEDULE_INFO]
    if isinstance(schedule_info, dict):
        schedule_info = ScheduleConfig(**schedule_info)
    return schedule_info


def get_button_keys_labels_callbacks() -> tuple:
    """Return button keys, labels, and callbacks for the schedule menu."""
    button_keys = ["minute", "hour", "day", "month", "day_of_week"]
    button_labels = [
        " Minute",
        " Hour",
        " Day of the month",
        " Month",
        " Day of the week",
    ]
    button_callbacks = [
        MINUTE_SELECT,
        HOUR_SELECT,
        DAY_OF_MONTH_SELECT,
        MONTH_SELECT,
        DAY_OF_WEEK_SELECT,
    ]
    return button_keys, button_labels, button_callbacks


def build_cron_string(schedule_info: ScheduleConfig, button_keys: list) -> str:
    """Build the cron string from schedule information."""
    cron_string = ""
    for key in button_keys:
        cron_string += bld_cron_token_schedule_info(schedule_info, key) + " "
    return cron_string.rstrip(" ")


def create_buttons(
    schedule_info: ScheduleConfig,
    button_keys: list,
    button_labels: list,
    button_callbacks: list,
) -> list:
    """Create buttons for the schedule menu."""
    keyboard = []
    for key, label, callback in zip(button_keys, button_labels, button_callbacks):
        values_list = getattr(schedule_info, key)
        if not values_list:
            button_text = f"{label}: not set"
        elif len(values_list) == 1:
            button_text = f"{label}: " + str(values_list[0])
        elif sorted(values_list) == sorted(Constants.get_full_range_dict()[key]):
            button_text = f"{label}: any {key.replace('_', ' ')}"
        else:
            button_text = f"{label}: " + bld_cron_token_schedule_info(
                schedule_info, key
            )

        if values_list:
            button_text = set_button_selection(button_text, True)

        keyboard.append(
            [
                InlineKeyboardButton(button_text, callback_data=callback),
            ]
        )
    return keyboard


@callback_query_check
@log_function_call
async def cron_parameters_dialog(update: Update, context: CallbackContext):
    """Handle cron parameters dialog.

    Args:
        update: Telegram update object
        context: Callback context containing user data

    Returns:
        int: Conversation state identifier
    """
    # user_data = cast(Dict[str, Any], context.user_data)
    query = cast(CallbackQuery,update.callback_query)
    query_data = cast(str, query.data)
    user_data = cast(Dict[str, Any], context.user_data)
    if not input_strings[query_data]:
        logger.error("input_strings[query.data] is None")
        return ConversationHandler.END
    user_data[USER_DATA_SELECTED_SCHED_PART] = query_data
    inline_keyboard = select_inline_keyboard(update, context, query_data)
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    logger.info(
        "query.data is %s input_strings[query.data] is %s",
        query.data,
        input_strings[query_data],
    )
    await query.edit_message_text(
        f"Please input {input_strings[query_data]} value", reply_markup=reply_markup
    )
    return SET_SCHED_VALUE_MENU


@callback_query_check_no_await
@log_function_call
def select_inline_keyboard(
    update: Update,  # pylint: disable=unused-argument
    context: CallbackContext,
    selection: str,
) -> list[list[InlineKeyboardButton]]:
    """Select inline keyboard based on user selection.

    Args:
        update: Telegram update object
        context: Callback context containing user data
        selection: User selection string

    Returns:
        list[list[InlineKeyboardButton]]: Inline keyboard buttons
    """
    default_keyboard = [[InlineKeyboardButton("Error", callback_data="stop")]]
    user_data = cast(Dict[str, Any], context.user_data)
    schedule_info: ScheduleConfig = user_data[USER_DATA_SCHEDULE_INFO]
    if isinstance(schedule_info, dict):
        schedule_info = ScheduleConfig(**schedule_info)
        user_data[USER_DATA_SCHEDULE_INFO] = schedule_info

    keyboard_mapping = {
        DAY_OF_MONTH_SELECT: inline_select_day_of_month_buttons,
        MONTH_SELECT: inline_month_buttons,
        DAY_OF_WEEK_SELECT: inline_day_of_week_buttons,
        HOUR_SELECT: inline_select_hour_buttons,
        MINUTE_SELECT: inline_select_minute_buttons,
    }

    keyboard_func = keyboard_mapping.get(selection)
    return keyboard_func(schedule_info) if keyboard_func else default_keyboard


@callback_query_check
@log_function_call
async def set_sched_parameter_value(update: Update, context: CallbackContext):
    """Set schedule parameter value based on user input.

    Args:
        update: Telegram update object
        context: Callback context containing user data

    Returns:
        int: Conversation state identifier
    """

    query = cast(CallbackQuery,update.callback_query)
    query_data = cast(str, query.data)
    user_data = cast(Dict[str, Any], context.user_data)
    schedule_info = user_data[USER_DATA_SCHEDULE_INFO]
    if isinstance(schedule_info, dict):
        schedule_info = ScheduleConfig(**schedule_info)
        user_data[USER_DATA_SCHEDULE_INFO] = schedule_info

    if user_data[USER_DATA_SELECTED_SCHED_PART] in [
        DAY_OF_MONTH_SELECT,
        MONTH_SELECT,
        DAY_OF_WEEK_SELECT,
        HOUR_SELECT,
        MINUTE_SELECT,
    ]:
        user_set_key = user_action_keys[user_data[USER_DATA_SELECTED_SCHED_PART]]
        await query.answer()
        pattern = Constants.get_value_pattern_dict()[
            user_set_key
        ]  # We filter out `back`
        if re.match(pattern, query_data):
            if query.data == NO_VALUES:
                getattr(schedule_info, user_set_key).clear()
            elif query.data == ALL_VALUES:
                setattr(
                    schedule_info,
                    user_set_key,
                    Constants.get_full_range_dict()[user_set_key].copy(),
                )
            else:
                accepted_data = re.sub(r"^(hour_|minute_)", "", query_data)
                logger.info("accepted_data is %s", accepted_data)
                values_list = getattr(schedule_info, user_set_key)
                if accepted_data in values_list:
                    values_list.remove(accepted_data)
                else:
                    values_list.append(accepted_data)
            inline_keyboard = select_inline_keyboard(
                update, context, user_data[USER_DATA_SELECTED_SCHED_PART]
            )
            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            logger.info(
                "query.data is %s input_strings[user_data[USER_DATA_SELECTED_SCHED_PART]] is %s",
                query.data,
                input_strings[user_data[USER_DATA_SELECTED_SCHED_PART]],
            )
            await query.edit_message_text(
                f"Please input {input_strings[user_data[USER_DATA_SELECTED_SCHED_PART]]} value",
                reply_markup=reply_markup,
            )
        else:
            logger.info("query.data %s does not match %s", query.data, pattern)
    return SET_SCHED_VALUE_MENU


@callback_query_check
@log_function_call
async def add_schedule_record(update: Update, context: CallbackContext):
    """Add schedule record.

    Args:
        update: Telegram update object
        context: Callback context containing user data
    """
    user_data = cast(Dict[str, Any], context.user_data)
    query = update.callback_query
    schedule_entry: ScheduleEntry = user_data[USER_DATA_SCHEDULE_ENTRY]
    if not schedule_entry:
        logger.error("schedule_entry is None")
        return ConversationHandler.END
    if not schedule_entry.is_complete():
        logger.error("schedule_entry is incomplete")
        return ConversationHandler.END
    if schedule_entry.sound_file_path is None:
        logger.error("sound_file_path is None")
        return ConversationHandler.END
    if not query:
        logger.error("query is None")
        return ConversationHandler.END
    await query.answer()
    if create_cron_schedule(
        schedule_entry.device_id,
        schedule_entry.user_id,
        schedule_entry.cron_string,
        schedule_entry.sound_file_path,
    ):

        logger.info("Schedule added successfully")
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔙 Back", callback_data=f"{DEVICE_MENU_CALLBACK}"
                ),
                InlineKeyboardButton(
                    "🔁 Restart", callback_data=f"{START_MENU_CALLBACK}"
                ),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            query = update.callback_query
            await query.edit_message_text(
                (
                    "Next scedule play has been added for device "
                    f"<i>{user_data[USER_DATA_SELECTED_DEVICE_NAME]}</i>:\n"
                    f"{get_description(schedule_entry.cron_string)}"
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )
        schedule_info: ScheduleConfig = user_data[USER_DATA_SCHEDULE_INFO]
        schedule_info.reset()

    else:
        logger.error("Failed to add schedule")  # noqa: WPS305
        if update.callback_query:
            query = update.callback_query
            await query.edit_message_text("Failed to add schedule")

    return SCHEDULE_PLAY_MENU


@callback_query_check
@log_function_call
async def set_for_play_now(update: Update, context: CallbackContext):
    """Set schedule for immediate play.
    This function sets up a schedule entry for immediate execution of a sound file.
    It performs various checks to ensure that the necessary data is present and valid.
    If all checks pass, it creates a cron schedule for immediate execution and sends
    a confirmation message to the user. If any check fails, it logs an error and sends
    an appropriate message to the user.

    Args:
        update (Update): Telegram update object containing the message and user data.
        context (CallbackContext): Callback context containing user data.

    Returns:
        int: The next state in the conversation handler, or
        ConversationHandler.END if an error occurs.
    """
    result = None
    query = cast(CallbackQuery,update.callback_query)
    await query.answer()
    user_data = context.user_data
    if not user_data:
        logger.error("user_data is None")
        result = ConversationHandler.END
        return result
    schedule_entry: ScheduleEntry = user_data[USER_DATA_SCHEDULE_ENTRY]
    if not schedule_entry:
        logger.error("schedule_entry is None")
        result = ConversationHandler.END
        return result
    if not schedule_entry.sound_file_path:
        logger.error("sound_file_path is None")
        result = ConversationHandler.END
        return result
    if not os.path.exists(schedule_entry.sound_file_path):
        await query.edit_message_text("Sound file does not exist")
        result = ConversationHandler.END

    if not schedule_entry.user_id or not schedule_entry.device_id:
        await query.edit_message_text("User ID or Device ID not set")
        result = ConversationHandler.END

    # Set for immediate execution
    schedule_entry.cron_string = "0 0 0 0 0"
    # Create schedule
    if create_cron_schedule(
        schedule_entry.device_id,
        schedule_entry.user_id,
        schedule_entry.cron_string,
        schedule_entry.sound_file_path,
    ):

        markup = InlineKeyboardMarkup(get_sound_menu_keyboard())
        await query.edit_message_text(
            f"Sound file was submitted for immediate play at <i>"
            f"{datetime.datetime.now().strftime('%M:%S')}</i> "
            f"on device <i>{user_data[USER_DATA_SELECTED_DEVICE_NAME]}</i>.\n"
            "Please select an option below:",
            reply_markup=markup,
            parse_mode=ParseMode.HTML,
        )

        # Reset cron string
        schedule_entry.cron_string = ""
        result = RECORD_OR_UPLOAD_SOUND_MENU
        return result

    logger.error("Failed to create immediate schedule")
    await query.edit_message_text("Failed to create immediate schedule")
    return result
