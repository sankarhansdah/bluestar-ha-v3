"""Bluestar Smart AC coordinator."""

import logging
from datetime import timedelta
from typing import Any, Dict

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BluestarAPI

_LOGGER = logging.getLogger(__name__)


class BluestarCoordinator(DataUpdateCoordinator):
    """Bluestar Smart AC data coordinator."""

    def __init__(self, hass, api: BluestarAPI):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="BluestarCoordinator",
            update_interval=timedelta(seconds=30),
        )
        self.api = api

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from API."""
        _LOGGER.debug("C1: Starting data update")
        
        try:
            devices = await self.api.get_devices()
            if not devices:
                _LOGGER.warning("C2: No devices returned from API")
                return {}
                
            # Convert devices list to dict keyed by device ID
            data = {}
            for device in devices:
                device_id = device["id"]
                data[device_id] = device
                
            _LOGGER.debug("C3: Data update successful, %d devices", len(data))
            _LOGGER.debug("C4: First 300 chars of data: %s", str(data)[:300])
            
            return data
            
        except Exception as e:
            _LOGGER.exception("C5: Data update failed: %s", e)
            raise UpdateFailed(f"Failed to update data: {e}") from e

    def get_device(self, device_id: str) -> Dict[str, Any]:
        """Get specific device data."""
        return self.data.get(device_id, {})

    def get_all_devices(self) -> Dict[str, Any]:
        """Get all devices data."""
        return self.data or {}

    def get_device_state(self, device_id: str) -> Dict[str, Any]:
        """Get device state."""
        device = self.get_device(device_id)
        return device.get("state", {})

    def is_device_connected(self, device_id: str) -> bool:
        """Check if device is connected."""
        device = self.get_device(device_id)
        return device.get("connected", False)