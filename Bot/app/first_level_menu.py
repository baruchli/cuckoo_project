# pylint: disable=unused-argument, redefined-outer-name

"""First level menu"""

import os
import re
from typing import Dict, Any, cast
from pprint import pformat
from pydub import AudioSegment
import pydub.exceptions
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    User,
    CallbackQuery,
    Message,
    error,
)
from telegram.ext import ConversationHandler, CallbackContext, ContextTypes
from telegram.constants import ParseMode
from app.logger import (
    logger,
    log_function_call,
    callback_query_check,
    callback_query_or_message_handler_check,
)

# from app.constants import *
from app.utils import build_device_keyboard, get_sound_menu_keyboard
from app.flask_connector import (
    get_user_devices,
    get_user_device_schedules,
    get_schedule_details,
    get_schedule_file,
    delete_schedule,
)
from app.user_data_dataclass import ScheduleConfig, ScheduleEntry
from app.constants import (
    USER_DATA_RETURN_SESSION,
    USER_DATA_DEVICE_MAP,
    USER_DATA_SCHEDULE_INFO,
    USER_DATA_SCHEDULE_ENTRY,
    USER_DATA_SELECTED_DEVICE_NAME,
    USER_DATA_LAST_MESSAGE_ID,
    USER_DATA_SECOND_MESSAGE_ID,
    START_MENU,
    DEVICE_MENU,
    RECORD_OR_UPLOAD_SOUND_MENU,
    DEVICE_ACTIONS_RE,
    SHARE_DIR,
    START_MENU_CALLBACK,
    DEVICE_MENU_CALLBACK,
    RECORD_OR_UPLOAD_SOUND_CALLBACK,
    LIST_SCHEDULED_ENTRIES_CALLBACK,
    SUBMITTED_SCHEDULES_EDIT_MENU,
    USER_DATA_CURRENT_DEVICE_ID,
    EDIT_STORED_SCHEDULE_MENU,
    DOWNLOAD_SOUND_PREFIX,
    DELETE_FILE_PREFIX,
)


@log_function_call
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the /start command and register user.
    This function handles the /start command initiated by the user. It retrieves the user's devices,
    creates a keyboard with device buttons, and sends a message or
    edits an existing message with the device selection options.
    Args:
        update (Update): The update object that contains the user's message or callback query.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains user data.
    Returns:
        int: The next state in the conversation, which is START_MENU.
    """
    user = update.effective_user
    if not user:
        logger.error("User is None")
        return ConversationHandler.END

    logger.debug("Start command initiated by user: %s (ID: %s)", user.username, user.id)

    # Parse the returned JSON devices list
    devices = get_user_devices(user)
    device_map = {device["device_id"]: device["device_name"] for device in devices}
    user_data = context.user_data
    if user_data is None:
        user_data = context.user_data = {}

    user_data.setdefault(USER_DATA_RETURN_SESSION, "No")
    user_data.setdefault(USER_DATA_DEVICE_MAP, None)
    user_data[USER_DATA_DEVICE_MAP] = device_map
    user_data[USER_DATA_SCHEDULE_INFO] = ScheduleConfig()
    user_data[USER_DATA_SCHEDULE_ENTRY] = ScheduleEntry()
    user_data[USER_DATA_CURRENT_DEVICE_ID] = None
    schedule_entry: ScheduleEntry = user_data[USER_DATA_SCHEDULE_ENTRY]
    schedule_entry.user_id = user.id

    logger.debug(
        "Successfully retrieved %d devices for user %s", len(devices), user.username
    )
    formatted_devices = pformat(devices)
    formatted_device_map = pformat(device_map)
    logger.debug("Devices dump: %s", formatted_devices)
    logger.debug("Devices map dump: %s", formatted_device_map)

    # Create device buttons two per row
    keyboard = build_device_keyboard(devices)

    # Add the "Pair with new device" button on a separate row
    # keyboard.append(
    #     [
    #         InlineKeyboardButton(
    #             "Pair with new device", callback_data="DEVICE_PAIR_CALLBACK"
    #         )
    #     ]
    # )

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Check if it's a message or a callback query
    if update.message:
        if devices:
            # noqa: WPS305
            await update.message.reply_text(
                f"Welcome, {user.first_name}! Select a device:",
                reply_markup=reply_markup,
            )
            logger.debug("Sent device selection to user %s via message", user.username)
        else:
            # noqa: WPS305
            await update.message.reply_text(
                f"Welcome, {user.first_name}! No devices found.",
            )
            logger.warning("No devices found for user %s", user.username)
    elif update.callback_query:
        query = cast(CallbackQuery, update.callback_query)
        await query.answer()
        user_data["Return_session"] = "Yes"
        if devices:
            await query.edit_message_text(
                f"Welcome back, {user.first_name}! Select a device:",
                reply_markup=reply_markup,
            )
            logger.debug(
                "Sent device selection to user %s via callback query", user.username
            )
        else:
            await query.edit_message_text(
                f"Welcome back, {user.first_name}! No devices found.",
            )
            logger.warning("No devices found for user %s", user.username)
    else:
        logger.error("Unexpected update type in start method")
        return ConversationHandler.END

    return START_MENU


@callback_query_check
@log_function_call
async def device_actions_list(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Implement Action list menu"""
    logger.info("Device actions list initiated")
    user_data = context.user_data
    if user_data is None:
        user_data = context.user_data = {}
        # Get device ID from callback data to check schedules
    if not update.callback_query:
        logger.error("No callback query")
        return ConversationHandler.END
    query = cast(CallbackQuery, update.callback_query)
    await query.answer()
    if update.callback_query.data:
        logger.info("Callback query data: %s", update.callback_query.data)
        if re.match(DEVICE_ACTIONS_RE, update.callback_query.data):
            device_id = int(update.callback_query.data.split("_")[-1])
            user_data[USER_DATA_CURRENT_DEVICE_ID] = device_id
        else:
            device_id = user_data[USER_DATA_CURRENT_DEVICE_ID]
        logger.debug("Device id: %s", device_id)
    else:
        logger.error("No callback query or data")
        return ConversationHandler.END
    if not device_id:
        logger.error("Device ID is None")
        return ConversationHandler.END

    schedule_entry: ScheduleEntry = user_data[USER_DATA_SCHEDULE_ENTRY]
    schedule_entry.device_id = int(device_id)

    keyboard = [
        [
            InlineKeyboardButton(
                "Record or upload sound",
                callback_data=f"{RECORD_OR_UPLOAD_SOUND_CALLBACK}",
            )
        ]
    ]

    # cast is to make Pylance happy
    device_schedules = get_user_device_schedules(
        cast(User, update.effective_user).id, device_id
    )
    if device_schedules:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "List and edit scheduled entries",
                    callback_data=f"{LIST_SCHEDULED_ENTRIES_CALLBACK}",
                )
            ]
        )

    keyboard.append(
        [InlineKeyboardButton("🔙 Back", callback_data=f"{START_MENU_CALLBACK}")]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    schedule_entry.cron_string = ""
    device_map = user_data[USER_DATA_DEVICE_MAP]
    logger.debug("Device map: %s", pformat(device_map) if device_map else "None")
    if not device_map:
        logger.error("Did not succeed to get device_map")
        return ConversationHandler.END
    device_name = (device_map or {}).get(int(device_id), "Unknown Device")
    user_data[USER_DATA_SELECTED_DEVICE_NAME] = device_name
    if device_name == "Unknown Device":
        logger.error("Faild to get device name")
        await query.edit_message_text("Faild to get device name")
        return ConversationHandler.END
    await query.edit_message_text(
        f"Availbale actions for device <i>{device_name}</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )

    return DEVICE_MENU


@callback_query_check
@log_function_call
async def record_or_upload_sound(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Implement sound recording and uploading."""
    user_data = context.user_data
    if not user_data:
        logger.error("Can't get user data")
        return ConversationHandler.END
    keyboard = [
        [
            InlineKeyboardButton("🔙 Back", callback_data=f"{DEVICE_MENU_CALLBACK}"),
            InlineKeyboardButton("🔁 Restart", callback_data=f"{START_MENU_CALLBACK}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = cast(CallbackQuery, update.callback_query)
    logger.debug("Handling record sound via callback query")

    await query.answer()
    edited_message = await query.edit_message_text(
        (
            "Please press and hold microphone icon 🎙️ to record "
            "sound or use paperclip icon 📎 to upload sound file "
            f"for device <i>{user_data[USER_DATA_SELECTED_DEVICE_NAME]}</i>"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )
    if not isinstance(edited_message, bool):
        user_data[USER_DATA_LAST_MESSAGE_ID] = edited_message.message_id
    else:
        logger.error("Failed to send a message")
        return ConversationHandler.END

    return RECORD_OR_UPLOAD_SOUND_MENU


@log_function_call
async def handle_audio(update: Update, context: CallbackContext):
    """Handling Telegram record action"""
    user_data = context.user_data
    if not user_data or not update.effective_chat:
        logger.error("Can't get user data of update.effective_chat")
        return ConversationHandler.END
    file_id = None
    if not update.message:
        return
    if update.message.voice is not None:
        logger.debug("update.message.voice.file_id is %s", update.message.voice.file_id)
        file_id = update.message.voice.file_id
    elif update.message.audio is not None:
        logger.debug("update.message.audio.file_id is %s", update.message.audio.file_id)
        file_id = update.message.audio.file_id
    if file_id is None:
        logger.error("file_id is None")
        return ConversationHandler.END
    audio_file = await context.bot.get_file(file_id)
    audio_file_full_path = os.path.join(SHARE_DIR, f"{file_id}.ogg")
    await audio_file.download_to_drive(audio_file_full_path)
    if update.message.from_user:
        logger.info(
            "File of uer %s has been saved at path: %s, now converting to mp3...",
            update.message.from_user.full_name,
            audio_file_full_path,
        )
    upload_progress_message = await update.message.reply_text(
        "Auploading and converting audio file to mp3..."
    )
    user_data[USER_DATA_SECOND_MESSAGE_ID] = upload_progress_message.message_id
    if convert_ogg_to_mp3(audio_file_full_path, user_data):
        logger.info("Audio file has been converted to mp3")
    return await build_sound_menu(update, context)


@callback_query_or_message_handler_check
@log_function_call
async def build_sound_menu(update: Update, context: CallbackContext):
    """Build sound menu for the user."""
    user_data = cast(Dict[str, Any], context.user_data)
    if not update.effective_chat:
        logger.error("Can't get update.effective_chat")
        return ConversationHandler.END
    markup = InlineKeyboardMarkup(get_sound_menu_keyboard())
    if update.message:  # Called by MessageHandler
        # noqa: WPS305
        await update.message.reply_text(
            (
                f"Audio file has been saved on a host for device "
                f"<i>{user_data[USER_DATA_SELECTED_DEVICE_NAME]}</i>\n"
                "Please choose the option"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=user_data[USER_DATA_LAST_MESSAGE_ID],
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=user_data[USER_DATA_SECOND_MESSAGE_ID],
        )
    elif update.callback_query:  # Called by CallbackQueryHandler
        query = cast(CallbackQuery, update.callback_query)
        logger.debug("Handling device pare via callback query")

        await query.answer()
        await query.edit_message_text(
            "Please choose the option for uploaded audio file",
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )
    return RECORD_OR_UPLOAD_SOUND_MENU


@callback_query_check
@log_function_call
async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the current conversation."""

    query = cast(CallbackQuery, update.callback_query)
    await query.answer()
    await query.edit_message_text("Conversation ended. Use /start to begin again.")

    return ConversationHandler.END


def convert_ogg_to_mp3(input_file: str, user_data: Dict[str, Any]) -> bool:
    """Convert .ogg audio file to .mp3 format.

    This function takes an input .ogg file and converts it to .mp3 format using pydub AudioSegment.

    Args:
        input_file (str): Path to the input .ogg file

    Returns:
        bool: True if conversion was successful, False otherwise

    Raises:
        OSError: If there are issues with file operations
        IOError: If there are issues reading/writing files
        pydub.exceptions.CouldntEncodeError: If there are encoding issues during conversion
    """
    # Check if input file exists
    if not os.path.exists(input_file):
        logger.error("Input ile %s does not exist", input_file)
        return False

    # Generate output file path by replacing .ogg extension with .mp3
    output_file = os.path.splitext(input_file)[0] + ".mp3"

    try:
        # Load the .ogg file
        audio = AudioSegment.from_file(input_file, format="ogg")
        # Export as .mp3
        try:
            audio.export(output_file, format="mp3")
        except (pydub.exceptions.CouldntEncodeError,) as e:
            logger.error("Audio conversion error: %s", e)
            return False
        logger.info("Saved conversion file %s  into %s", input_file, output_file)
        try:
            os.remove(input_file)
            logger.info("Successfully removed input file: %s", input_file)
        except OSError as e:
            logger.error("Error removing input file %s: %s", input_file, e)
        schedule_entry: ScheduleEntry = user_data[USER_DATA_SCHEDULE_ENTRY]
        schedule_entry.sound_file_path = output_file
        logger.info("Converted audio file path %s saved in user_data", output_file)
        return True
    except (OSError, IOError) as e:
        logger.error("An error occurred: %s", e)
        return False


@callback_query_check
@log_function_call
async def list_scheduled_entries(update: Update, context: CallbackContext) -> int:
    """
    Display a list of scheduled entries for a specific device.
    This function retrieves and displays all scheduled sound entries for a selected device,
    showing them as interactive buttons in a Telegram message. Each schedule is displayed
    with its timing description (either "immediate" or the cron schedule).
    Args:
        update (Update): The update object from Telegram
        context (CallbackContext): The context object for the callback
    Returns:
        int: SUBMITTED_SCHEDULES_EDIT_MENU state or ConversationHandler.END if there's an error
    Note:
        For InlineKeyboardButton with long text, consider the following:
        - Use '\n' for line breaks in the button text
        - Keep total text under 100 characters
        - Text will be automatically wrapped, but may look different on different devices
    """
    query = cast(CallbackQuery, update.callback_query)
    await query.answer()

    user_data = context.user_data
    if not user_data:
        logger.error("No user data available")
        return ConversationHandler.END

    device_id = user_data.get(USER_DATA_CURRENT_DEVICE_ID)
    if not device_id:
        logger.error("No device ID found in user data")
        return ConversationHandler.END

    device_schedules = None
    if update.effective_user and update.effective_user.id:
        device_schedules = get_user_device_schedules(update.effective_user.id, device_id)
    keyboard = []

    if not device_schedules:
        keyboard.append(
            [InlineKeyboardButton("🔙 Back", callback_data=DEVICE_MENU_CALLBACK)]
        )
        await query.edit_message_text(
            "No scheduled entries found for device "
            f"{user_data.get(USER_DATA_SELECTED_DEVICE_NAME, 'Unknown Device')}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return SUBMITTED_SCHEDULES_EDIT_MENU

    device_name = user_data.get(USER_DATA_SELECTED_DEVICE_NAME, "Unknown Device")
    for schedule in device_schedules:
        schedule_text = (
            "immediate"
            if schedule["cron_string"] == "0 0 0 0 0"
            else schedule["cron_string"]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"Sound played\n {schedule_text}",
                    callback_data=f"{schedule['id']}_sched_edit",
                )
            ]
        )

    keyboard.append(
        [InlineKeyboardButton("🔙 Back", callback_data=DEVICE_MENU_CALLBACK)]
    )

    await query.edit_message_text(
        f"Scheduled entries for device {device_name}:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return SUBMITTED_SCHEDULES_EDIT_MENU


@callback_query_check
@log_function_call
async def edit_stored_sched_entry(update: Update, context: CallbackContext) -> int:
    """Handles the editing of a stored schedule entry in the bot's menu system.
    This function displays options for managing a specific schedule entry, including downloading
    associated sound files and deleting the entry. It retrieves schedule details from the database
    and presents them in an interactive menu format.
    Args:
        update (Update): The update object containing information about the user's interaction.
                        The callback_query is guaranteed to be present 
                        due to the @callback_query_check decorator.
        context (CallbackContext): The context object containing bot and user-specific data.
    Returns:
        int: EDIT_STORED_SCHEDULE_MENU state for the conversation handler, 
        or ConversationHandler.END if an error occurs.
    Note:
        The function assumes callback_query is not None 
        as it's decorated with @callback_query_check.
        This can be indicated to Pylance using one of these methods:
        1. Use assert update.callback_query is not None at the start
        2. Type hint the decorator: @callback_query_check # type: ignore
        3. Use typing.cast(CallbackQuery, update.callback_query)
    Raises:
        None, but logs errors if schedule details cannot be retrieved or user data is missing.
    """
    # if not update.callback_query:
    #     logger.error("No callback query")
    #     return ConversationHandler.END

    query = cast(CallbackQuery, update.callback_query)
    await query.answer()

    if not query.data:
        logger.error("No callback data")
        return ConversationHandler.END

    schedule_id = int(query.data.split("_")[0])
    schedule_details = get_schedule_details(schedule_id)
    if not schedule_details:
        logger.error("Failed to get schedule details")
        return ConversationHandler.END

    cron_string = schedule_details.get("cron_string", "")
    device_id = schedule_details.get("device_id", "")
    sched_id = schedule_details.get("id", "")
    user_id = schedule_details.get("user_id", "")

    logger.debug(
        "Schedule details: cron=%s, device=%s, id=%s, user=%s",
        cron_string,
        device_id,
        sched_id,
        user_id,
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "Download Sound", callback_data=f"{DOWNLOAD_SOUND_PREFIX}{schedule_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "Delete Schedule entry",
                callback_data=f"{DELETE_FILE_PREFIX}{schedule_id}",
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back", callback_data=f"{LIST_SCHEDULED_ENTRIES_CALLBACK}"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user_data = context.user_data
    if not user_data:
        logger.error("No user data")
        return ConversationHandler.END
    device_map = user_data[USER_DATA_DEVICE_MAP]
    device_name = (device_map or {}).get(int(device_id), "Unknown Device")

    await query.edit_message_text(
        f"Edit stored schedule entry for device <i>{device_name}</i>",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML,
    )
    return EDIT_STORED_SCHEDULE_MENU


@callback_query_check
@log_function_call
async def delete_sched_file(update: Update, context: CallbackContext) -> int:
    """
    Handles the deletion of a scheduled file based on the callback query data.
    Args:
        update (Update): The update object that contains the callback query.
        context (CallbackContext): The context object that contains additional data.
    Returns:
        int: The next state in the conversation handler, 
        or ConversationHandler.END if the operation fails.
    This function performs the following steps:
    1. Answers the callback query.
    2. Checks if the callback query data is present.
    3. Extracts the schedule ID from the callback query data.
    4. Deletes the schedule from the database.
    5. Edits the message text to confirm deletion.
    6. Lists the remaining scheduled entries.
    """

    query = cast(CallbackQuery, update.callback_query)
    await query.answer()

    if not query.data:
        logger.error("No callback data")
        return ConversationHandler.END

    schedule_id = int(query.data.split("_")[-1])
    logger.debug("Delete schedule file for schedule ID: %s", schedule_id)

    # Delete schedule from database
    if not delete_schedule(schedule_id):
        logger.error("Failed to delete schedule %s", schedule_id)
        return ConversationHandler.END

    await query.edit_message_text("Schedule entry deleted successfully!")
    return await list_scheduled_entries(update, context)


@log_function_call
async def download_sound_file(update: Update, context: CallbackContext) -> int:
    """
    Handle sound file download request.
    """
    query = cast(CallbackQuery,update.callback_query)
    query_data = cast(str, query.data)
    schedule_id = int(query_data.split("_")[-1])
    message = cast(Message, query.message)
    logger.debug("Download sound file for schedule ID: %s", schedule_id)

    # Get file binary data
    file_data = get_schedule_file(schedule_id)
    if not file_data:
        await message.reply_text(
            "❌ Failed to download sound file"
        )
        return EDIT_STORED_SCHEDULE_MENU

    # Get schedule details for filename
    schedule_details = get_schedule_details(schedule_id)
    logger.debug("Schedule details: %s", schedule_details)
    filename = f"schedule_{schedule_id}_file.mp3"

    try:
        # Send audio file to user
        if query.message:
            await message.reply_audio(
                audio=file_data, filename=filename, caption="🎵 Here's your sound file"
            )
            await query.answer("Sound file downloaded successfully!")
        else:
            logger.error("No message found")
            await query.answer("❌ Failed to send sound file")
    except (error.TelegramError, OSError) as e:
        logger.error("Failed to send sound file: %s", str(e))
        await message.reply_text("❌ Failed to send sound file")

    return EDIT_STORED_SCHEDULE_MENU
