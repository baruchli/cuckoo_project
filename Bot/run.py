# pylint: disable=unused-argument, redefined-outer-name
"""Implementtion of Telegram bot"""

import os
from telegram.error import InvalidToken, NetworkError, TimedOut

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from app.logger import logger
from app.constants import (
    DEVICE_ACTIONS_RE,
    RECORD_OR_UPLOAD_SOUND_CALLBACK,
    START_MENU_CALLBACK,
    DEVICE_MENU_CALLBACK,
    SCHEDULE_PLAY_CALLBACK,
    PLAY_NOW_CALLBACK,
    MONTH_SELECT,
    DAY_OF_MONTH_SELECT,
    DAY_OF_WEEK_SELECT,
    HOUR_SELECT,
    MINUTE_SELECT,
    COMMIT_SCHEDULE_CALLBACK,
    CANCEL_SELECT,
    START_MENU,
    DEVICE_MENU,
    RECORD_OR_UPLOAD_SOUND_MENU,
    LIST_SCHEDULED_ENTRIES_CALLBACK,
    SUBMITTED_SCHEDULES_EDIT_MENU,
    EDIT_STORED_SCHEDULE_MENU,
    SCHEDULE_PLAY_MENU,
    SET_SCHED_VALUE_MENU,
    FILE_MENU,
    Constants,
)
from app.first_level_menu import (
    start,
    device_actions_list,
    record_or_upload_sound,
    handle_audio,
    build_sound_menu,
    end_conversation,
    list_scheduled_entries,
    edit_stored_sched_entry,
    download_sound_file,
    delete_sched_file,
)
from app.second_level_menu import (
    display_schedule_menu,
    set_for_play_now,
    cron_parameters_dialog,
    add_schedule_record,
    set_sched_parameter_value,
)


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "None")


def main():
    """
    Initializes and starts the Telegram Bot application.
    This function performs the following steps:
    1. Logs a warning message indicating the initialization of the Telegram Bot.
    2. Checks if the BOT_TOKEN is set to "None" and returns if it is.
    3. Attempts to build the application using the provided BOT_TOKEN.
    4. Configures the conversation handler with various states and their corresponding handlers.
    5. Adds the conversation handler to the application.
    6. Logs a debug message indicating the completion of the bot configuration.
    7. Starts polling to handle incoming updates.
    If an error occurs during the initialization or polling process,
    it logs a critical error message.
    Exceptions:
        InvalidToken: Raised if the provided BOT_TOKEN is invalid.
        NetworkError: Raised if there is a network-related error.
        TimedOut: Raised if the operation times out.
    """
    logger.warning("Initializing Telegram Bot...")
    if BOT_TOKEN == "None":
        return

    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()

        # Conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                START_MENU: [
                    CallbackQueryHandler(
                        device_actions_list, pattern=f"{DEVICE_ACTIONS_RE}"
                    ),
                ],
                DEVICE_MENU: [
                    CallbackQueryHandler(
                        record_or_upload_sound,
                        pattern=f"^{RECORD_OR_UPLOAD_SOUND_CALLBACK}$",
                    ),
                    CallbackQueryHandler(
                        list_scheduled_entries,
                        pattern=f"^{LIST_SCHEDULED_ENTRIES_CALLBACK}$",
                    ),
                    CallbackQueryHandler(start, pattern=f"^{START_MENU_CALLBACK}$"),
                ],
                SUBMITTED_SCHEDULES_EDIT_MENU: [
                    CallbackQueryHandler(
                        edit_stored_sched_entry,
                        pattern=Constants.get_sched_edit_entry_re_pattern(),
                    ),
                    CallbackQueryHandler(
                        device_actions_list, pattern=f"^{DEVICE_MENU_CALLBACK}$"
                    ),
                ],
                EDIT_STORED_SCHEDULE_MENU: [
                    CallbackQueryHandler(
                        download_sound_file,
                        pattern=Constants.get_download_sound_re_pattern(),
                    ),
                    CallbackQueryHandler(
                        delete_sched_file,
                        pattern=Constants.get_delete_file_re_pattern(),
                    ),
                    CallbackQueryHandler(
                        list_scheduled_entries,
                        pattern=f"^{LIST_SCHEDULED_ENTRIES_CALLBACK}$",
                    ),
                ],
                RECORD_OR_UPLOAD_SOUND_MENU: [
                    MessageHandler(
                        filters=filters.VOICE | filters.AUDIO, callback=handle_audio
                    ),
                    CallbackQueryHandler(start, pattern=f"^{START_MENU_CALLBACK}$"),
                    CallbackQueryHandler(
                        device_actions_list, pattern=f"^{DEVICE_MENU_CALLBACK}$"
                    ),
                    CallbackQueryHandler(
                        display_schedule_menu, pattern=f"^{SCHEDULE_PLAY_CALLBACK}$"
                    ),
                    CallbackQueryHandler(
                        set_for_play_now, pattern=f"^{PLAY_NOW_CALLBACK}$"
                    ),
                ],
                SCHEDULE_PLAY_MENU: [
                    CallbackQueryHandler(
                        cron_parameters_dialog,
                        pattern=f"^{MONTH_SELECT}$|^{DAY_OF_MONTH_SELECT}$|^{DAY_OF_WEEK_SELECT}$|"
                        f"^{HOUR_SELECT}$|^{MINUTE_SELECT}$",
                    ),
                    CallbackQueryHandler(
                        add_schedule_record, pattern=f"^{COMMIT_SCHEDULE_CALLBACK}$"
                    ),
                    CallbackQueryHandler(
                        build_sound_menu, pattern=f"^{CANCEL_SELECT}$"
                    ),
                    CallbackQueryHandler(start, pattern=f"^{START_MENU_CALLBACK}$"),
                    CallbackQueryHandler(
                        device_actions_list, pattern=f"^{DEVICE_MENU_CALLBACK}$"
                    ),
                ],
                SET_SCHED_VALUE_MENU: [
                    CallbackQueryHandler(
                        set_sched_parameter_value,
                        pattern=f"{Constants.get_all_re_patterns_or_conditioned()}",
                    ),
                    CallbackQueryHandler(
                        display_schedule_menu, pattern=f"^back$|^{CANCEL_SELECT}$"
                    ),
                    CallbackQueryHandler(start, pattern=f"^{START_MENU_CALLBACK}$"),
                ],
                FILE_MENU: [],
            },
            fallbacks=[
                CommandHandler("start", start),
                CallbackQueryHandler(end_conversation, pattern="^end$"),
            ],
        )

        application.add_handler(conv_handler)

        logger.debug("Bot configuration completed. Starting polling...")
        application.run_polling()
    except (
        InvalidToken,
        NetworkError,
        TimedOut,
    ) as e:
        logger.critical("Failed to start bot: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
