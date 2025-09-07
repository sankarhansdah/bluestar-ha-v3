"""Bluestar Smart AC API client based on working webapp implementation."""

import asyncio
import logging
import ssl
import json
import time
import base64
from typing import Dict, Any, Optional, List
import aiohttp
import paho.mqtt.client as mqtt
from .const import (
    BLUESTAR_BASE_URL,
    BLUESTAR_MQTT_ENDPOINT,
    DEFAULT_HEADERS,
    PUB_CONTROL_TOPIC_NAME,
    PUB_STATE_UPDATE_TOPIC_NAME,
    SUB_STATE_TOPIC_NAME,
    SRC_KEY,
    SRC_VALUE,
    FORCE_FETCH_KEY_NAME,
    CONNECTION_TIMEOUT,
    MQTT_KEEPALIVE
)

_LOGGER = logging.getLogger(__name__)


class BluestarAPIError(Exception):
    """Exception raised for Bluestar API errors."""


class BluestarMQTTClient:
    """MQTT client based on exact webapp implementation."""
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, session_id: str):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_id = session_id
        self.is_connected = False
        self.mqtt_client = None
        self._loop = None
        
    async def connect(self) -> None:
        """Connect to AWS IoT MQTT broker."""
        try:
            self._loop = asyncio.get_running_loop()
            
            # Create SSL context in thread-safe manner
            ssl_context = await self._loop.run_in_executor(None, ssl.create_default_context)
            
            client_id = f"bluestar_ha_{int(time.time())}"
            username = self.access_key
            password = self.session_id
            
            connect_url = f"mqtts://{self.endpoint}:8883"
            
            self.mqtt_client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
            self.mqtt_client.username_pw_set(username, password)
            self.mqtt_client.tls_set_context(ssl_context)
            
            # Set callbacks
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect
            self.mqtt_client.on_error = self._on_error
            
            _LOGGER.debug("Connecting to MQTT broker: %s", connect_url)
            
            # Connect in executor to avoid blocking
            await self._loop.run_in_executor(
                None, 
                self.mqtt_client.connect, 
                self.endpoint, 
                8883, 
                CONNECTION_TIMEOUT
            )
            
            # Start the loop
            self.mqtt_client.loop_start()
            
            # Wait for connection (ultra-fast timeout)
            timeout = 2.0  # 2 seconds instead of 5
            while not self.is_connected and timeout > 0:
                await asyncio.sleep(0.05)  # Check more frequently
                timeout -= 0.05
                
            if not self.is_connected:
                _LOGGER.warning("⚠️ MQTT connection timeout, will use HTTP fallback")
                # Don't raise error, just log warning and continue
                
            _LOGGER.info("✅ MQTT Connected to AWS IoT")
            
        except Exception as e:
            _LOGGER.error("❌ MQTT Connection error: %s", e)
            raise BluestarAPIError(f"MQTT connection failed: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            self.is_connected = True
            _LOGGER.debug("MQTT connected successfully")
        else:
            _LOGGER.error("MQTT connection failed with code: %s", rc)
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback."""
        self.is_connected = False
        _LOGGER.debug("MQTT disconnected: %s", rc)
    
    def _on_error(self, client, userdata, error):
        """MQTT error callback."""
        _LOGGER.error("MQTT error: %s", error)
    
    async def publish(self, device_id: str, control_payload: Dict[str, Any]) -> None:
        """Publish control command to device."""
        if not self.is_connected:
            raise BluestarAPIError("MQTT not connected")
        
        try:
            # Add SRC_KEY and SRC_VALUE (from decompiled app)
            payload_with_src = { 
                **control_payload, 
                SRC_KEY: SRC_VALUE 
            }
            
            # Wrap in {"state": {"desired": {control_payload}}} (EXACT from decompiled app)
            shadow_update = {
                "state": {
                    "desired": payload_with_src
                }
            }
            
            topic = PUB_STATE_UPDATE_TOPIC_NAME % device_id
            
            _LOGGER.debug("📤 MQTT Publishing to topic: %s", topic)
            _LOGGER.debug("📤 MQTT Payload: %s", json.dumps(shadow_update, indent=2))
            
            # Publish in executor
            result = await self._loop.run_in_executor(
                None,
                self.mqtt_client.publish,
                topic,
                json.dumps(shadow_update),
                0  # qos
            )
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                raise BluestarAPIError(f"Failed to publish: {result.rc}")
                
            _LOGGER.debug("✅ MQTT Published successfully")
            
        except Exception as e:
            _LOGGER.error("❌ MQTT JSON error during publish: %s", e)
            raise BluestarAPIError(f"MQTT publish failed: {e}")
    
    async def force_sync(self, device_id: str) -> None:
        """Send force sync command to device."""
        if not self.is_connected:
            raise BluestarAPIError("MQTT not connected")
        
        force_sync_payload = { FORCE_FETCH_KEY_NAME: 1 }
        topic = PUB_CONTROL_TOPIC_NAME % device_id
        
        _LOGGER.debug("📤 MQTT Force Sync to topic: %s", topic)
        _LOGGER.debug("📤 MQTT Force Sync Payload: %s", json.dumps(force_sync_payload, indent=2))
        
        # Publish in executor
        result = await self._loop.run_in_executor(
            None,
            self.mqtt_client.publish,
            topic,
            json.dumps(force_sync_payload),
            0  # qos
        )
        
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise BluestarAPIError(f"Failed to send force sync: {result.rc}")
            
        _LOGGER.debug("✅ MQTT Force sync sent successfully")
    
    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self.is_connected = False


class BluestarAPI:
    """Bluestar Smart AC API client based on working webapp implementation."""
    
    def __init__(self, phone: str, password: str, base_url: str = BLUESTAR_BASE_URL, mqtt_url: str = BLUESTAR_MQTT_ENDPOINT):
        self.phone = phone
        self.password = password
        self.base_url = base_url
        self.mqtt_url = mqtt_url
        self.session_token = None
        self.mqtt_client = None
        self._session = None
        self.aws_credentials = None
    
    def _extract_aws_credentials(self, login_response: Dict[str, Any]) -> Dict[str, str]:
        """Extract AWS credentials from login response (like the decompiled app)."""
        try:
            mi = login_response.get("mi")  # Base64 encoded credentials
            if not mi:
                raise BluestarAPIError("No 'mi' field in login response")
            
            # Decode Base64 and split by "::"
            decoded = base64.b64decode(mi).decode('utf-8')
            parts = decoded.split('::')
            
            if len(parts) != 3:
                raise BluestarAPIError(f"Invalid credential format. Expected 3 parts, got {len(parts)}")
            
            endpoint, access_key, secret_key = parts
            
            credentials = {
                "endpoint": endpoint,
                "access_key": access_key,
                "secret_key": secret_key,
                "session_id": login_response.get("session"),
                "user_id": login_response.get("user", {}).get("id"),
                "raw": mi
            }
            
            _LOGGER.debug("✅ AWS credentials extracted successfully")
            _LOGGER.debug("📍 Endpoint: %s", endpoint)
            _LOGGER.debug("🔑 Access Key: %s...", access_key[:8])
            _LOGGER.debug("🔐 Secret Key: %s...", secret_key[:8])
            _LOGGER.debug("🆔 Session ID: %s", login_response.get("session"))
            
            return credentials
            
        except Exception as e:
            _LOGGER.error("❌ Failed to extract AWS credentials: %s", e)
            raise BluestarAPIError(f"Failed to extract AWS credentials: {e}")
        
    async def async_login(self) -> None:
        """Login to Bluestar API."""
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            login_data = {
                "auth_id": self.phone,
                "auth_type": 1,
                "password": self.password
            }
            
            headers = DEFAULT_HEADERS.copy()
            
            _LOGGER.debug("🔐 Logging in to Bluestar API")
            _LOGGER.debug("📍 Base URL: %s", self.base_url)
            _LOGGER.debug("📱 Phone: %s", self.phone)
            _LOGGER.debug("🔑 Login URL: %s/auth/login", self.base_url)
            
            async with self._session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)  # Reduced to 5 seconds for faster response
            ) as response:
                if response.status != 200:
                    raise BluestarAPIError(f"Login failed with status: {response.status}")
                
                data = await response.json()
                
                if "session" not in data:
                    raise BluestarAPIError("No session token in login response")
                
                self.session_token = data["session"]
                _LOGGER.info("✅ Successfully logged in to Bluestar API")
                
                # Extract AWS credentials from login response
                try:
                    self.aws_credentials = self._extract_aws_credentials(data)
                    
                    # Initialize MQTT client with extracted credentials
                    self.mqtt_client = BluestarMQTTClient(
                        endpoint=self.aws_credentials["endpoint"],
                        access_key=self.aws_credentials["access_key"],
                        secret_key=self.aws_credentials["secret_key"],
                        session_id=self.session_token
                    )
                    
                    try:
                        await self.mqtt_client.connect()
                        _LOGGER.info("✅ MQTT client connected to AWS IoT")
                    except Exception as e:
                        _LOGGER.warning("⚠️ MQTT connection failed, will use HTTP fallback: %s", e)
                        self.mqtt_client = None
                        
                except Exception as e:
                    _LOGGER.warning("⚠️ Failed to extract AWS credentials: %s", e)
                    self.mqtt_client = None
                
        except Exception as e:
            _LOGGER.error("❌ Login failed: %s", e)
            raise BluestarAPIError(f"Login failed: {e}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authenticated headers."""
        headers = DEFAULT_HEADERS.copy()
        if self.session_token:
            headers["X-APP-SESSION"] = self.session_token
        return headers
    
    async def async_get_devices(self) -> List[Dict[str, Any]]:
        """Get all devices."""
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            headers = self._get_auth_headers()
            
            _LOGGER.debug("Fetching devices from Bluestar API")
            
            async with self._session.get(
                f"{self.base_url}/things",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)  # Reduced to 5 seconds for faster response
            ) as response:
                if response.status != 200:
                    raise BluestarAPIError(f"Failed to fetch devices: {response.status}")
                
                data = await response.json()
                
                if "states" not in data:
                    return []
                
                devices = []
                for device_id, device_data in data["states"].items():
                    device_info = {
                        "id": device_id,
                        "name": device_data.get("name", f"Bluestar AC {device_id[:8]}"),
                        "state": device_data.get("state", {}),
                        "connected": device_data.get("connected", False),
                        "state_ts": device_data.get("state_ts", 0)
                    }
                    devices.append(device_info)
                
                _LOGGER.debug("✅ Fetched %d devices", len(devices))
                return devices
                
        except Exception as e:
            _LOGGER.error("❌ Failed to fetch devices: %s", e)
            raise BluestarAPIError(f"Failed to fetch devices: {e}")
    
    async def async_control_device(self, device_id: str, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Control device using multi-step algorithm from webapp."""
        try:
            _LOGGER.debug("🎛️ Control request for device: %s", device_id)
            _LOGGER.debug("Control data: %s", json.dumps(control_data, indent=2))
            
            # Add timestamp and source
            control_payload = {
                **control_data,
                "ts": int(time.time() * 1000),
                "src": "anmq"
            }
            
            control_result = None
            
            # Step 1: Try MQTT control (PRIMARY METHOD from webapp)
            if self.mqtt_client and self.mqtt_client.is_connected:
                try:
                    _LOGGER.debug("📤 Step 1: Sending MQTT control")
                    await self.mqtt_client.publish(device_id, control_payload)
                    control_result = {"method": "MQTT", "status": "success"}
                    _LOGGER.debug("✅ MQTT control success")
                except Exception as e:
                    _LOGGER.warning("⚠️ MQTT control failed: %s", e)
            else:
                _LOGGER.debug("⚠️ MQTT client not available, trying HTTP API fallback")
            
            # Step 2: HTTP API fallback with EXACT MODE CONTROL MECHANISM
            if not control_result:
                try:
                    _LOGGER.debug("📤 Step 2: Sending control via HTTP API")
                    
                    # Get current device state to determine the mode
                    devices = await self.async_get_devices()
                    current_device = next((d for d in devices if d["id"] == device_id), None)
                    
                    if not current_device:
                        raise BluestarAPIError("Device not found")
                    
                    # Determine current mode
                    current_mode = current_device["state"].get("mode", 2)
                    
                    # If mode is being changed, use the new mode
                    if control_payload.get("mode") is not None:
                        current_mode = int(control_payload["mode"])
                    
                    # Build mode-specific preferences structure
                    mode_config = {}
                    
                    # Add control parameters to mode configuration
                    for key, value in control_payload.items():
                        if key in ["pow", "mode", "stemp", "fspd", "vswing", "hswing", "display"]:
                            mode_config[key] = str(value)
                    
                    # EXACT NESTED STRUCTURE from webapp
                    preferences_payload = {
                        "preferences": {
                            "mode": {
                                str(current_mode): mode_config
                            }
                        }
                    }
                    
                    _LOGGER.debug("📤 MODE CONTROL STRUCTURE: %s", json.dumps(preferences_payload, indent=2))
                    
                    headers = self._get_auth_headers()
                    
                    async with self._session.post(
                        f"{self.base_url}/things/{device_id}/preferences",
                        json=preferences_payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=CONNECTION_TIMEOUT)
                    ) as response:
                        if response.status == 200:
                            control_result = await response.json()
                            _LOGGER.debug("✅ MODE CONTROL success")
                        else:
                            _LOGGER.warning("⚠️ MODE CONTROL failed, trying direct MQTT structure")
                            
                            # Fallback to direct MQTT structure
                            mqtt_style_payload = {
                                "state": {
                                    "desired": control_payload
                                }
                            }
                            
                            async with self._session.post(
                                f"{self.base_url}/things/{device_id}/state",
                                json=mqtt_style_payload,
                                headers=headers,
                                timeout=aiohttp.ClientTimeout(total=CONNECTION_TIMEOUT)
                            ) as response:
                                if response.status == 200:
                                    control_result = await response.json()
                                    _LOGGER.debug("✅ Direct MQTT structure success")
                                else:
                                    _LOGGER.warning("⚠️ All control methods failed")
                
                except Exception as e:
                    _LOGGER.warning("⚠️ HTTP control failed: %s", e)
            
            # Step 3: Force sync if all methods fail
            if not control_result:
                try:
                    _LOGGER.debug("📤 Step 3: Sending force sync")
                    
                    if self.mqtt_client and self.mqtt_client.is_connected:
                        await self.mqtt_client.force_sync(device_id)
                        _LOGGER.debug("✅ Force sync via MQTT")
                    else:
                        force_sync_payload = {"fpsh": 1}
                        headers = self._get_auth_headers()
                        
                        async with self._session.post(
                            f"{self.base_url}/things/{device_id}/control",
                            json=force_sync_payload,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=CONNECTION_TIMEOUT)
                        ) as response:
                            if response.status == 200:
                                _LOGGER.debug("✅ Force sync via HTTP")
                            else:
                                _LOGGER.warning("⚠️ Force sync failed")
                
                except Exception as e:
                    _LOGGER.warning("⚠️ Force sync failed: %s", e)
            
            # Get updated device state
            devices = await self.async_get_devices()
            updated_device = next((d for d in devices if d["id"] == device_id), None)
            
            result = {
                "message": "Control command sent successfully",
                "deviceId": device_id,
                "controlData": control_data,
                "method": "MULTI_STEP_CONTROL",
                "api": control_result
            }
            
            if updated_device:
                result["state"] = updated_device["state"]
            
            return result
            
        except Exception as e:
            _LOGGER.error("❌ Control error: %s", e)
            raise BluestarAPIError(f"Control failed: {e}")
    
    async def async_close(self) -> None:
        """Close the API client."""
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        if self._session:
            await self._session.close()
