"""
This module sets up logging for the automated_cuckoo application.
It configures both console and file handlers with rotating file support.
The log level and log file path can be set via environment variables.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

# Get log level from environment variable, default to INFO if not set
log_level = os.getenv("PYTHON_LOG_LEVEL", "INFO").upper()

# Create a logger
logger = logging.getLogger("automated_cuckoo")

# Convert string log level to logging constant
numeric_level = getattr(logging, log_level, logging.INFO)
logger.setLevel(numeric_level)

# Create formatters
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d]"
    " - %(message)s", datefmt="%d/%m %H:%M"
)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d]"
    " - %(message)s", datefmt="%d/%m %H:%M"
)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(numeric_level)
console_handler.setFormatter(console_formatter)

# Create file handler
log_file = os.getenv("LOG_FILE", "app.log")
file_handler = RotatingFileHandler(
    log_file, maxBytes=10485760, backupCount=5
)  # 10MB per file, keep 5 backups
file_handler.setLevel(numeric_level)
file_handler.setFormatter(file_formatter)

# Add handlers to logger
logger.addHandler(console_handler)
# logger.addHandler(file_handler)

# Prevent logging from propagating to the root logger
logger.propagate = False
