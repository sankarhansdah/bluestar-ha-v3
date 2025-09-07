"""Data update coordinator for Bluestar Smart AC integration."""

import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .api import BluestarAPI, BluestarAPIError

_LOGGER = logging.getLogger(__name__)


class BluestarDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Bluestar API."""

    def __init__(self, hass, api: BluestarAPI):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="BluestarCoordinator",
            update_interval=timedelta(seconds=30),
        )
        self.api = api

    async def _async_update_data(self):
        """Update data via library."""
        _LOGGER.debug("C1 coordinator _async_update_data() start")
        
        try:
            # Fetch devices from API
            devices = await self.api.async_get_devices()
            
            if devices is None:
                raise UpdateFailed("Received None from API")
            
            _LOGGER.debug("C2 coordinator got %d devices", len(devices))
            
            # Process device data
            processed_devices = {}
            for device in devices:
                device_id = device["id"]
                device_state = device["state"]
                
                # Convert state to Home Assistant format
                processed_state = {
                    "power": device_state.get("pow", 0) == 1,
                    "mode": device_state.get("mode", 2),
                    "temperature": device_state.get("stemp", "26.0"),
                    "current_temp": device_state.get("ctemp", "25.0"),
                    "fan_speed": device_state.get("fspd", 2),
                    "vertical_swing": device_state.get("vswing", 0),
                    "horizontal_swing": device_state.get("hswing", 0),
                    "display": device_state.get("display", 1),
                    "connected": device.get("connected", False),
                    "timestamp": device.get("state_ts", 0),
                    "rssi": device_state.get("rssi", 0),
                    "error": device_state.get("err", 0),
                    "source": device_state.get("src", "api")
                }
                
                processed_devices[device_id] = {
                    "id": device_id,
                    "name": device["name"],
                    "state": processed_state,
                    "connected": device.get("connected", False),
                    "timestamp": device.get("state_ts", 0)
                }
            
            _LOGGER.debug("C3 coordinator processed %d devices", len(processed_devices))
            
            return {
                "devices": processed_devices,
                "last_update": self.api.session_token
            }
            
        except BluestarAPIError as err:
            _LOGGER.exception("C4 coordinator BluestarAPIError: %s", err)
            raise UpdateFailed(f"Bluestar API error: {err}")
        except Exception as err:
            _LOGGER.exception("C5 coordinator general error: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}")
