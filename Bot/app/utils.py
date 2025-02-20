"""Utilities for UI build"""

from telegram import InlineKeyboardButton
from app.constants import (
    SCHEDULE_PLAY_CALLBACK,
    PLAY_NOW_CALLBACK,
    DEVICE_MENU_CALLBACK,
    START_MENU_CALLBACK,
)

# Pre-calculate the bold unicode mapping
BOLD_MAP = {
    **{chr(i): chr(i + 0x1D400 - 65) for i in range(65, 91)},  # A-Z
    **{chr(i): chr(i + 0x1D41A - 97) for i in range(97, 123)},  # a-z
    **{chr(i): chr(i + 0x1D7CE - 48) for i in range(48, 58)},  # 0-9
}


def set_button_selection(text: str, select: bool) -> str:
    """Set button selection state."""
    if select:
        bold_text = "".join(BOLD_MAP.get(char, char) for char in text)
        return "✓" + bold_text
    en_space = "\u2002"  # Unicode for En Space
    hair_space = "\u200A"  # Unicode for Hair Space
    return en_space + text + hair_space + hair_space


def build_device_keyboard(devices):
    """Build allowed devices UI."""
    keyboard = [
        [
            InlineKeyboardButton(
                devices[i]["device_name"],
                callback_data=f'device_actions_{devices[i]["device_id"]}',
            ),
            InlineKeyboardButton(
                devices[i + 1]["device_name"],
                callback_data=f'device_actions_{devices[i+1]["device_id"]}',
            ),
        ]
        for i in range(0, len(devices) - 1, 2)
    ]

    # Handle odd number of devices by adding the last device to the last row if needed
    if len(devices) % 2 != 0:
        last_row = keyboard[-1] if keyboard else []
        last_row.append(
            InlineKeyboardButton(
                devices[-1]["device_name"],
                callback_data=f'device_actions_{devices[-1]["device_id"]}',
            )
        )
        if last_row != keyboard[-1]:
            keyboard.append(last_row)
    return keyboard


def get_sound_menu_keyboard():
    """Build sound menu UI."""
    keyboard = [
        [
            InlineKeyboardButton(
                "Schedule audio file for later play",
                callback_data=f"{SCHEDULE_PLAY_CALLBACK}",
            )
        ],
        [
            InlineKeyboardButton(
                "Play the file now", callback_data=f"{PLAY_NOW_CALLBACK}"
            )
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data=f"{DEVICE_MENU_CALLBACK}"),
            InlineKeyboardButton("🔁 Restart", callback_data=f"{START_MENU_CALLBACK}"),
        ],
    ]
    return keyboard
