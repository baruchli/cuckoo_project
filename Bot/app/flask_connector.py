"""Utilities using flask services"""

from typing import Any
import requests
from telegram import User
from app.constants import (
    API_URL,
    API_PORT,
    ACCESSIBLE_DEVICES_ENDPOINT,
    CRON_SCHEDULES,
    USER_ENDPOINT,
    DEVICE_ENDPOINT,
)
from app.logger import logger


def get_user_devices(user: User) -> Any:
    """Get JSON of devices permited for user by user id"""
    # Prepare user registration JSON
    try:
        response = requests.get(
            f"http://{API_URL}:{API_PORT}/{ACCESSIBLE_DEVICES_ENDPOINT}/{user.id}",
            timeout=10,  # Timeout in seconds
        )
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the returned JSON devices list
        devices = response.json()
    except requests.exceptions.Timeout:
        logger.error("Request timed out while trying to reach the API.")
        devices = []
    except requests.exceptions.RequestException as e:
        logger.error("API call failed for user %s: %s", user.username, e)
        devices = []
    return devices


def create_cron_schedule(
    device_id: int, user_id: int, cron_string: str, sound_file: str
) -> Any:
    """
    Create a cron schedule for a specific device and user via API call.

    Args:
        device_id (int): The ID of the device
        user_id (int): The ID of the user
        cron_string (str): Cron schedule string (e.g., "0 8 * * *")
        sound_file (str): Path to the sound file

    Returns:
        The response from the API or an empty dictionary if the request fails
    """
    # Prepare the payload
    payload = {
        "device_id": device_id,
        "cron_string": cron_string,
        "user_id": user_id,
        "sound_file": sound_file,
    }

    try:
        response = requests.post(
            f"http://{API_URL}:{API_PORT}/{CRON_SCHEDULES}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,  # Timeout in seconds
        )
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Log the payload data in case of success
        logger.info("Successfully created cron schedule: %s", payload)

        # Return the response JSON if successful
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Request timed out while trying to reach the API.")
        return {}
    except requests.exceptions.RequestException as e:
        logger.error("API call failed for user %s: %s", user_id, e)
        return {}


def get_user_device_schedules(user_id: int, device_id: int) -> Any:
    """
    Retrieve cron schedules for a specific user and device via API call.

    Args:
        user_id (int): The ID of the user
        device_id (int): The ID of the device

    Returns:
        The response from the API or an empty list if the request fails
    """
    try:
        response = requests.get(
            f"http://{API_URL}:{API_PORT}/{CRON_SCHEDULES}/{USER_ENDPOINT}"
            f"/{user_id}/{DEVICE_ENDPOINT}/{device_id}",
            timeout=10,  # Timeout in seconds
        )
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Return the response JSON if successful
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Request timed out while trying to reach the API.")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(
            "API call failed for user %s and device %s: %s", user_id, device_id, e
        )
        return []


def get_schedule_details(schedule_id: int) -> Any:
    """
    Fetch schedule entry details by schedule ID

    Args:
        schedule_id (int): ID of the schedule entry

    Returns:
        dict: Schedule details if successful, empty list if failed
    """
    try:
        # Construct API endpoint URL
        url = f"http://{API_URL}:{API_PORT}/{CRON_SCHEDULES}/{schedule_id}"

        # Make GET request
        response = requests.get(
            url,
            timeout=10,  # Timeout in seconds
        )
        response.raise_for_status()

        # Return schedule data
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Request timed out while fetching schedule %d", schedule_id)
        return []
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch schedule %d: %s", schedule_id, str(e))
        return []


def get_schedule_file(schedule_id: int) -> bytes:
    """
    Fetch sound file for a schedule by schedule ID

    Args:
        schedule_id (int): ID of the schedule entry

    Returns:
        bytes: Sound file binary data if successful, empty bytes if failed
    """
    try:
        # Construct API endpoint URL
        url = f"http://{API_URL}:{API_PORT}/{CRON_SCHEDULES}/file/{schedule_id}"

        # Make GET request
        response = requests.get(
            url,
            timeout=10,  # Timeout in seconds
        )
        response.raise_for_status()

        # Return binary file data
        return response.content

    except requests.exceptions.Timeout:
        logger.error(
            "Request timed out while fetching sound file for schedule %d", schedule_id
        )
        return bytes()
    except requests.exceptions.RequestException as e:
        logger.error(
            "Failed to fetch sound file for schedule %d: %s", schedule_id, str(e)
        )
        return bytes()


def delete_schedule(schedule_id: int) -> Any:
    """
    Delete a schedule entry by schedule ID via API call.

    Args:
        schedule_id (int): The ID of the schedule entry to delete

    Returns:
        dict: Response from the API or an empty dictionary if the request fails
    """
    try:
        # Construct API endpoint URL
        url = f"http://{API_URL}:{API_PORT}/{CRON_SCHEDULES}/{schedule_id}"

        # Make DELETE request
        response = requests.delete(
            url,
            timeout=10,  # Timeout in seconds
        )
        response.raise_for_status()

        # Log the deletion in case of success
        logger.info("Successfully deleted schedule with ID: %s", schedule_id)

        # Check if the response status code is 204 (No Content)
        if response.status_code == 204:
            return {"message": "Schedule deleted"}
        if response.content:
            # Return the response JSON if the status code is not 204 and content is present
            return response.json()
        logger.info(
            "Empty response received with status code: %s", response.status_code
        )
        return {
            "message": f"Empty response received with status code: {response.status_code}"
        }

    except requests.exceptions.Timeout:
        logger.error("Request timed out while deleting schedule %d", schedule_id)
        return {"message": "Request timed out"}
    except requests.exceptions.RequestException as e:
        logger.error("Failed to delete schedule %d: %s", schedule_id, str(e))
        return {"message": f"Failed to delete schedule {schedule_id}: {str(e)}"}
