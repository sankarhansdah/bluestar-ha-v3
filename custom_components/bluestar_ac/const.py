"""Constants for the Bluestar Smart AC integration."""

DOMAIN = "bluestar_ac"
PLATFORMS = ["switch", "sensor", "button", "select"]  # Temporarily remove climate

# API Configuration
BLUESTAR_BASE_URL = "https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod"
BLUESTAR_MQTT_ENDPOINT = "a1b2c3d4e5f6g7-ats.iot.ap-south-1.amazonaws.com"  # Will be replaced with actual endpoint from login

# Headers
DEFAULT_HEADERS = {
    "X-APP-VER": "v4.11.4-133",
    "X-OS-NAME": "Android",
    "X-OS-VER": "v13-33",
    "User-Agent": "com.bluestarindia.bluesmart",
    "Content-Type": "application/json"
}

# MQTT Topics (from decompiled app)
PUB_CONTROL_TOPIC_NAME = "things/%1$s/control"
PUB_STATE_UPDATE_TOPIC_NAME = "$aws/things/%1$s/shadow/update"
SUB_STATE_TOPIC_NAME = "$aws/things/%1$s/shadow/update/accepted"

# Control Parameters
SRC_KEY = "src"
SRC_VALUE = "anmq"
FORCE_FETCH_KEY_NAME = "fpsh"

# Device States
POWER_ON = 1
POWER_OFF = 0

# Modes
MODE_FAN = 0
MODE_COOL = 2
MODE_DRY = 3
MODE_AUTO = 4

# Fan Speeds
FAN_LOW = 2
FAN_MEDIUM = 3
FAN_HIGH = 4
FAN_TURBO = 6
FAN_AUTO = 7

# Swing Modes
SWING_OFF = 0
SWING_15 = 1
SWING_30 = 2
SWING_45 = 3
SWING_60 = 4
SWING_AUTO = -1

# Display
DISPLAY_OFF = 0
DISPLAY_ON = 1

# Temperature Range
MIN_TEMP = 16
MAX_TEMP = 30
DEFAULT_TEMP = 26

# Update Intervals
UPDATE_INTERVAL = 30  # seconds
CONNECTION_TIMEOUT = 5  # seconds (reduced from 10 to 5)
MQTT_KEEPALIVE = 60  # seconds
