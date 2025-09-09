"""Constants for Bluestar Smart AC integration."""

DOMAIN = "bluestar_ac"

# API Configuration
BLUESTAR_BASE_URL = "https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod"
BLUESTAR_MQTT_ENDPOINT = "a1b2c3d4e5f6g7-ats.iot.ap-south-1.amazonaws.com"  # Will be extracted from login

# Default Configuration
DEFAULT_POLL_SECONDS = 30
DEFAULT_TIMEOUT = 10
DEFAULT_MQTT_TIMEOUT = 5

# MQTT Configuration
MQTT_KEEPALIVE = 30
MQTT_RECONNECT_PERIOD = 1000
MQTT_QOS = 0

# MQTT Topics
MQTT_STATE_UPDATE_TOPIC = "$aws/things/{device_id}/shadow/update"
MQTT_CONTROL_TOPIC = "things/{device_id}/control"

# Control Parameters
FORCE_FETCH_KEY = "fpsh"
SOURCE_KEY = "src"
SOURCE_VALUE = "anmq"

# Bluestar Mode Mappings
BLUESTAR_MODES = {
    0: "fan",      # Fan Only
    2: "cool",     # Cool
    3: "dry",      # Dry
    4: "auto"      # Auto
}

# Home Assistant Mode Mappings
HA_MODES = {
    "off": 0,      # Off
    "fan_only": 0, # Fan Only
    "cool": 2,     # Cool
    "dry": 3,      # Dry
    "auto": 4      # Auto
}

# Fan Speed Mappings
BLUESTAR_FAN_SPEEDS = {
    2: "low",
    3: "medium", 
    4: "high",
    6: "turbo",
    7: "auto"
}

HA_FAN_SPEEDS = {
    "low": 2,
    "medium": 3,
    "high": 4,
    "turbo": 6,
    "auto": 7
}

# Swing Mappings
BLUESTAR_SWING_MODES = {
    0: "off",
    1: "15°",
    2: "30°", 
    3: "45°",
    4: "60°",
    -1: "auto"
}

HA_SWING_MODES = {
    "off": 0,
    "15°": 1,
    "30°": 2,
    "45°": 3,
    "60°": 4,
    "auto": -1
}

# Temperature Range (Fahrenheit - matching webapp)
MIN_TEMP = 60
MAX_TEMP = 86
DEFAULT_TEMP = 75

# Device Configuration
DEFAULT_DEVICE_ID = "24587ca091f8"  # From webapp

# Headers
DEFAULT_HEADERS = {
    "X-APP-VER": "v4.11.4-133",
    "X-OS-NAME": "Android", 
    "X-OS-VER": "v13-33",
    "User-Agent": "com.bluestarindia.bluesmart",
    "Content-Type": "application/json"
}