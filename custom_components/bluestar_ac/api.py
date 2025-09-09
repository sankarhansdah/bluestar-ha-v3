"""Bluestar Smart AC API client."""

import asyncio
import base64
import json
import logging
import ssl
from typing import Any, Callable, Dict, List, Optional

import aiohttp
import paho.mqtt.client as mqtt

from .const import (
    BLUESTAR_BASE_URL,
    DEFAULT_HEADERS,
    DEFAULT_MQTT_TIMEOUT,
    DEFAULT_TIMEOUT,
    FORCE_FETCH_KEY,
    MQTT_CONTROL_TOPIC,
    MQTT_KEEPALIVE,
    MQTT_QOS,
    MQTT_RECONNECT_PERIOD,
    MQTT_STATE_UPDATE_TOPIC,
    SOURCE_KEY,
    SOURCE_VALUE,
)

_LOGGER = logging.getLogger(__name__)


class BluestarAPI:
    """Bluestar Smart AC API client."""

    def __init__(
        self,
        phone: str,
        password: str,
        base_url: str = BLUESTAR_BASE_URL,
        mqtt_endpoint: Optional[str] = None,
    ):
        """Initialize the API client."""
        self.phone = phone
        self.password = password
        self.base_url = base_url
        self.mqtt_endpoint = mqtt_endpoint
        self.session_token: Optional[str] = None
        self.mqtt_client: Optional[mqtt.Client] = None
        self.mqtt_credentials: Optional[Dict[str, str]] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._mqtt_connected = False
        self._mqtt_message_callback: Optional[Callable] = None

    async def login(self) -> None:
        """Login and extract credentials."""
        _LOGGER.debug("API1: Starting login process")
        
        if not self._session:
            self._session = aiohttp.ClientSession()

        try:
            # Prepare login payload
            login_payload = {
                "auth_id": self.phone,
                "auth_type": 1,  # Phone number
                "password": self.password,
            }

            headers = DEFAULT_HEADERS.copy()
            _LOGGER.debug("API2: Sending login request to %s/auth/login", self.base_url)

            async with self._session.post(
                f"{self.base_url}/auth/login",
                json=login_payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT),
            ) as response:
                if not response.ok:
                    error_text = await response.text()
                    _LOGGER.error("API3: Login failed with status %s: %s", response.status, error_text)
                    raise Exception(f"Login failed: {response.status}")

                login_data = await response.json()
                _LOGGER.debug("API4: Login successful, extracting credentials")

                # Extract session token
                self.session_token = login_data.get("session")
                if not self.session_token:
                    raise Exception("No session token in login response")

                # Extract AWS credentials from 'mi' field
                mi_field = login_data.get("mi")
                if not mi_field:
                    raise Exception("No 'mi' field in login response")

                # Decode Base64 credentials
                try:
                    decoded = base64.b64decode(mi_field).decode("utf-8")
                    parts = decoded.split("::")
                    if len(parts) != 3:
                        raise Exception(f"Invalid credential format. Expected 3 parts, got {len(parts)}")
                    
                    endpoint, access_key, secret_key = parts
                    self.mqtt_credentials = {
                        "endpoint": endpoint,
                        "access_key": access_key,
                        "secret_key": secret_key,
                        "session_id": self.session_token,
                    }
                    
                    # Update MQTT endpoint if not provided
                    if not self.mqtt_endpoint:
                        self.mqtt_endpoint = endpoint
                        
                    _LOGGER.debug("API5: Credentials extracted successfully")
                    _LOGGER.debug("API6: MQTT endpoint: %s", endpoint)
                    
                except Exception as e:
                    _LOGGER.error("API7: Failed to extract credentials: %s", e)
                    raise Exception(f"Failed to extract credentials: {e}")

        except Exception as e:
            _LOGGER.error("API8: Login error: %s", e)
            raise

    async def get_devices(self) -> List[Dict[str, Any]]:
        """Get list of devices."""
        _LOGGER.debug("API9: Fetching devices")
        
        if not self.session_token:
            raise Exception("Not logged in")

        headers = DEFAULT_HEADERS.copy()
        headers["X-APP-SESSION"] = self.session_token

        try:
            async with self._session.get(
                f"{self.base_url}/things",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT),
            ) as response:
                if not response.ok:
                    error_text = await response.text()
                    _LOGGER.error("API10: Failed to fetch devices: %s", error_text)
                    raise Exception(f"Failed to fetch devices: {response.status}")

                data = await response.json()
                _LOGGER.debug("API11: Devices fetched successfully")
                
                # Process devices data
                devices = []
                if "things" in data and "states" in data:
                    for thing in data["things"]:
                        device_id = thing["thing_id"]
                        state = data["states"].get(device_id, {})
                        
                        device = {
                            "id": device_id,
                            "name": thing.get("user_config", {}).get("name", "AC"),
                            "type": "ac",
                            "state": state.get("state", {}),
                            "connected": state.get("connected", False),
                        }
                        devices.append(device)
                        
                _LOGGER.debug("API12: Processed %d devices", len(devices))
                return devices

        except Exception as e:
            _LOGGER.error("API13: Error fetching devices: %s", e)
            raise

    async def get_device_state(self, device_id: str) -> Dict[str, Any]:
        """Get specific device state."""
        devices = await self.get_devices()
        for device in devices:
            if device["id"] == device_id:
                return device["state"]
        raise Exception(f"Device {device_id} not found")

    async def set_state(self, device_id: str, **kwargs) -> None:
        """Set device state using EXACT WEBAPP METHOD."""
        _LOGGER.debug("API14: Setting state for device %s: %s", device_id, kwargs)
        
        if not self.session_token:
            raise Exception("Not logged in")

        # Build control payload EXACTLY like webapp (DIRECT STRUCTURE)
        control_payload = {}
        
        # Map Home Assistant parameters to Bluestar parameters (EXACT WEBAPP STRUCTURE)
        if "hvac_mode" in kwargs:
            mode = kwargs["hvac_mode"]
            if mode == "off":
                control_payload["pow"] = 0
            else:
                control_payload["pow"] = 1
                # Map HA mode to Bluestar mode
                from .const import HA_MODES
                bluestar_mode = HA_MODES.get(mode, 2)
                control_payload["mode"] = {"value": bluestar_mode}
        
        if "target_temperature" in kwargs:
            control_payload["stemp"] = kwargs["target_temperature"]
            
        if "fan_mode" in kwargs:
            from .const import HA_FAN_SPEEDS
            fan_speed = HA_FAN_SPEEDS.get(kwargs["fan_mode"], 2)
            control_payload["fspd"] = fan_speed
            
        if "swing_mode" in kwargs:
            from .const import HA_SWING_MODES
            swing_value = HA_SWING_MODES.get(kwargs["swing_mode"], 0)
            control_payload["vswing"] = swing_value
            
        if "display" in kwargs:
            control_payload["display"] = 1 if kwargs["display"] else 0

        # Add timestamp and source (EXACT WEBAPP FORMAT)
        control_payload["ts"] = int(asyncio.get_event_loop().time() * 1000)
        control_payload[SOURCE_KEY] = SOURCE_VALUE

        _LOGGER.debug("API15: Control payload (EXACT WEBAPP): %s", control_payload)

        # EXACT WEBAPP ALGORITHM: HTTP ONLY FOR NOW (skip MQTT to isolate issue)
        success = False
        
        # Step 1: Try MQTT first (EXACT WEBAPP METHOD) - DISABLED FOR DEBUGGING
        _LOGGER.debug("API16: MQTT status - client: %s, connected: %s", 
                     self.mqtt_client is not None, self._mqtt_connected)
        
        # SKIP MQTT FOR NOW TO ISOLATE HTTP ISSUE
        _LOGGER.warning("API18: SKIPPING MQTT FOR DEBUGGING - going straight to HTTP")
        
        # Step 2: HTTP fallback (EXACT WEBAPP METHOD)
        try:
            _LOGGER.debug("API19: Attempting HTTP control with payload: %s", control_payload)
            await self._send_http_command(device_id, control_payload)
            success = True
            _LOGGER.debug("API20: HTTP command sent successfully")
        except Exception as e:
            _LOGGER.error("API21: HTTP command failed: %s", e)
            _LOGGER.error("API21: Full error details: %s", traceback.format_exc())

        if not success:
            raise Exception("All control methods failed")

    async def _publish_mqtt_command(self, device_id: str, payload: Dict[str, Any]) -> None:
        """Publish MQTT command."""
        if not self.mqtt_client or not self._mqtt_connected:
            raise Exception("MQTT not connected")

        # Create MQTT payload structure
        mqtt_payload = {
            "state": {
                "desired": payload
            }
        }

        topic = MQTT_STATE_UPDATE_TOPIC.format(device_id=device_id)
        
        # Publish in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.mqtt_client.publish,
            topic,
            json.dumps(mqtt_payload),
            MQTT_QOS
        )

    async def _send_http_command(self, device_id: str, payload: Dict[str, Any]) -> None:
        """Send HTTP command using EXACT WEBAPP METHOD."""
        headers = DEFAULT_HEADERS.copy()
        headers["X-APP-SESSION"] = self.session_token

        # EXACT WEBAPP METHOD: Get current device state to determine mode
        async with self._session.get(
            f"{self.base_url}/things",
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT),
        ) as response:
            if not response.ok:
                raise Exception(f"Failed to fetch device state: {response.status}")
            
            device_data = await response.json()
            current_state = None
            for device in device_data:
                if device["id"] == device_id:
                    current_state = device.get("state", {})
                    break
            
            if not current_state:
                raise Exception("Device not found")

        # Determine current mode (EXACT from webapp)
        current_mode = current_state.get("mode", 2)
        if "mode" in payload:
            if isinstance(payload["mode"], dict) and "value" in payload["mode"]:
                current_mode = int(payload["mode"]["value"])
            else:
                current_mode = int(payload["mode"])

        # Build mode-specific preferences structure (EXACT WEBAPP STRUCTURE)
        mode_config = {}
        
        # Add control parameters to mode configuration (EXACT from webapp)
        if "pow" in payload:
            mode_config["power"] = str(payload["pow"])
        if "mode" in payload:
            if isinstance(payload["mode"], dict) and "value" in payload["mode"]:
                mode_config["mode"] = str(payload["mode"]["value"])
            else:
                mode_config["mode"] = str(payload["mode"])
        if "stemp" in payload:
            mode_config["stemp"] = str(payload["stemp"])
        if "fspd" in payload:
            mode_config["fspd"] = str(payload["fspd"])
        if "vswing" in payload:
            mode_config["vswing"] = str(payload["vswing"])
        if "hswing" in payload:
            mode_config["hswing"] = str(payload["hswing"])
        if "display" in payload:
            mode_config["display"] = str(payload["display"])

        # EXACT NESTED STRUCTURE from webapp
        preferences_payload = {
            "preferences": {
                "mode": {
                    str(current_mode): mode_config
                }
            }
        }

        _LOGGER.debug("API22: Sending EXACT WEBAPP structure: %s", preferences_payload)
        _LOGGER.debug("API22: URL: %s", f"{self.base_url}/things/{device_id}/preferences")
        _LOGGER.debug("API22: Headers: %s", headers)

        async with self._session.post(
            f"{self.base_url}/things/{device_id}/preferences",
            json=preferences_payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT),
        ) as response:
            _LOGGER.debug("API22: Response status: %s", response.status)
            if not response.ok:
                error_text = await response.text()
                _LOGGER.error("API22: HTTP error response: %s", error_text)
                raise Exception(f"HTTP command failed: {response.status} - {error_text}")
            else:
                response_text = await response.text()
                _LOGGER.debug("API22: HTTP success response: %s", response_text)

    async def _force_sync_device(self, device_id: str) -> None:
        """Force sync device state (EXACT WEBAPP METHOD)."""
        if not self.mqtt_client or not self._mqtt_connected:
            raise Exception("MQTT not connected")

        # Create force sync payload (EXACT WEBAPP FORMAT)
        force_sync_payload = {FORCE_FETCH_KEY: 1}
        
        # Add source
        force_sync_payload[SOURCE_KEY] = SOURCE_VALUE
        
        # Create MQTT payload structure
        mqtt_payload = {
            "state": {
                "desired": force_sync_payload
            }
        }

        topic = MQTT_STATE_UPDATE_TOPIC.format(device_id=device_id)
        
        # Publish in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.mqtt_client.publish,
            topic,
            json.dumps(mqtt_payload),
            MQTT_QOS
        )

    async def connect_mqtt(self, on_message: Callable) -> None:
        """Connect to MQTT broker."""
        _LOGGER.debug("API19: Connecting to MQTT")
        
        if not self.mqtt_credentials:
            raise Exception("No MQTT credentials available")

        self._mqtt_message_callback = on_message

        # Create SSL context in executor
        loop = asyncio.get_event_loop()
        ssl_context = await loop.run_in_executor(None, ssl.create_default_context)

        # Create MQTT client
        client_id = f"u-{self.mqtt_credentials['session_id']}"
        self.mqtt_client = mqtt.Client(client_id=client_id)
        
        # Configure AWS IoT authentication
        self.mqtt_client.tls_set_context(ssl_context)
        self.mqtt_client.username_pw_set(
            self.mqtt_credentials["access_key"],
            self.mqtt_credentials["secret_key"]
        )

        # Set up event handlers
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
        self.mqtt_client.on_error = self._on_mqtt_error

        # Connect
        try:
            await loop.run_in_executor(
                None,
                self.mqtt_client.connect,
                self.mqtt_endpoint,
                443,
                MQTT_KEEPALIVE
            )
            
            # Start loop
            self.mqtt_client.loop_start()
            
            # Wait for connection
            await asyncio.sleep(1)
            if not self._mqtt_connected:
                raise Exception("MQTT connection timeout")
                
            _LOGGER.debug("API20: MQTT connected successfully")
            
        except Exception as e:
            _LOGGER.error("API21: MQTT connection failed: %s", e)
            raise

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Handle MQTT connect."""
        if rc == 0:
            self._mqtt_connected = True
            _LOGGER.debug("API22: MQTT connected")
        else:
            _LOGGER.error("API23: MQTT connection failed with code %s", rc)

    def _on_mqtt_message(self, client, userdata, msg):
        """Handle MQTT message."""
        try:
            payload = json.loads(msg.payload.decode())
            _LOGGER.debug("API24: MQTT message received: %s", payload)
            
            if self._mqtt_message_callback:
                self._mqtt_message_callback(payload)
                
        except Exception as e:
            _LOGGER.error("API25: Error processing MQTT message: %s", e)

    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnect."""
        self._mqtt_connected = False
        _LOGGER.debug("API26: MQTT disconnected")

    def _on_mqtt_error(self, client, userdata, error):
        """Handle MQTT error."""
        _LOGGER.error("API27: MQTT error: %s", error)

    async def disconnect_mqtt(self) -> None:
        """Disconnect from MQTT broker."""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self._mqtt_connected = False
            _LOGGER.debug("API28: MQTT disconnected")

    async def close(self) -> None:
        """Close the API client."""
        await self.disconnect_mqtt()
        if self._session:
            await self._session.close()
        _LOGGER.debug("API29: API client closed")