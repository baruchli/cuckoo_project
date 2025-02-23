"""
Flask application runner module.

This module provides functionality to run a Flask application, test database connection, 
and retrieve the local IP address.
"""

import os
import sys
import argparse
import socket
from app import create_app, init_db_test  # This import should now work correctly
from app.logger import logger


def get_client_ip():
    """
    Retrieve the IP address of the current machine.

    Returns:
        str: The IP address of the current machine
    """
    try:
        # Create a temporary socket to get the local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Doesn't actually send any data, just establishes a connection
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except (socket.error, socket.gaierror) as e:
        logger.error("Could not determine local IP address: %s", str(e))
        return "Unknown"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask application runner")
    parser.add_argument(
        "--db-test", action="store_true", help="Test database connection and exit"
    )
    args = parser.parse_args()

    try:
        if args.db_test:

            client_ip = get_client_ip()
            logger.info("Running database connection test from IP: %s", client_ip)

            logger.info("Running database connection test")
            if init_db_test():
                print("Database connection successful!")
                sys.exit(0)
            else:
                print("Database connection failed!")
                sys.exit(1)

        app = create_app()
        logger.info("Starting the Flask application")
        app.run(host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"), debug=False)
    except (ImportError, RuntimeError, socket.error) as e:
        logger.error("Failed to start application: %s", str(e), exc_info=True)
        sys.exit(1)
