"""Telegram bot logger"""

import os
import logging
from types import FrameType
from typing import cast
from logging.handlers import RotatingFileHandler
import inspect
from telegram.ext import ConversationHandler

# Create a logger
logger = logging.getLogger("TelegramBot")

# Set the log level based on environment variable
log_level = os.getenv("PYTHON_LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level))

# Create console handler and set level
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, log_level))

# Create file handler
LOG_DIRECTORY = "logs"
os.makedirs(LOG_DIRECTORY, exist_ok=True)
file_handler = RotatingFileHandler(os.path.join(LOG_DIRECTORY, "telegram_bot.log"))
file_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    """%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s""",
    datefmt="%H:%M:%S",
)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
# logger.addHandler(file_handler)

# Define an additional logger for the decorator
decorator_logger = logging.getLogger("DecoratorLogger")
decorator_handler = logging.StreamHandler()
decorator_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
)
decorator_logger.addHandler(decorator_handler)
decorator_logger.setLevel(logging.INFO)


def log_function_call(func):
    """Enter function log wrapper"""

    def wrapper(*args, **kwargs):
        frametype = cast(FrameType, inspect.currentframe())
        frame = frametype.f_back
        if frame is not None:
            file_name = os.path.basename(frame.f_code.co_filename)
            decorator_logger.info(
                "Entering %s in %s:%d", func.__name__, file_name, frame.f_lineno
            )
        else:
            decorator_logger.info("Entering %s", func.__name__)
        return func(*args, **kwargs)

    return wrapper


def callback_query_check(func):
    """Decorator to check callback query and user data"""

    async def wrapper(update, context, *args, **kwargs):
        if any(
            x is None
            for x in [context.user_data, update.callback_query, update.effective_user]
        ):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f"Unexpected termination due to invalid parameters of function {func.__name__}."
                    " Please restart process by command '/start'"
                ),
                reply_markup=None,
            )
            logger.error("user_data is None or query is None")
            return ConversationHandler.END
        return await func(update, context, *args, **kwargs)

    return wrapper

def callback_query_check_no_await(func):
    """Decorator to check callback query and user data"""

    def wrapper(update, context, *args, **kwargs):
        if any(
            x is None
            for x in [context.user_data, update.callback_query, update.effective_user]
        ):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f"Unexpected termination due to invalid parameters of function {func.__name__}."
                    " Please restart process by command '/start'"
                ),
                reply_markup=None,
            )
            logger.error("user_data is None or query is None")
            return ConversationHandler.END
        return func(update, context, *args, **kwargs)

    return wrapper

def callback_query_or_message_handler_check(func):
    """Decorator to check callback query and user data"""

    async def wrapper(update, context, *args, **kwargs):
        if all(x is None for x in [update.callback_query, update.message]):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f"Unexpected termination due to invalid parameters of function {func.__name__}."
                    " Please restart process by command '/start'"
                ),
                reply_markup=None,
            )
            logger.error("user_data is None or query is None")
            return ConversationHandler.END
        return await func(update, context, *args, **kwargs)

    return wrapper
