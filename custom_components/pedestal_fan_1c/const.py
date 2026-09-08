"""Constants for Xiaomi Mi Smart Standing Fan 1C."""

from datetime import timedelta

DOMAIN = "pedestal_fan_1c"
MODEL = "dmaker.fan.1c"
PLATFORMS = ["fan", "number", "switch"]
SCAN_INTERVAL = timedelta(seconds=30)

CONF_TOKEN = "token"
TOKEN_LENGTH = 32

PRESET_NORMAL = "normal"
PRESET_NATURE = "nature"
PRESET_MODES = [PRESET_NORMAL, PRESET_NATURE]

SPEED_RANGE = (1, 3)
