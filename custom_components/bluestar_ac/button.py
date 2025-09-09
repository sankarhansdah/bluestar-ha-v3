"""Bluestar Smart AC button platform."""

import logging
from typing import Any, Dict

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Bluestar button entities."""
    _LOGGER.debug("BT1: Setting up button platform")
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    
    devices = coordinator.get_all_devices()
    _LOGGER.debug("BT2: Found %d devices for buttons", len(devices))
    
    entities = []
    for device_id, device_data in devices.items():
        _LOGGER.debug("BT3: Creating button entities for device %s", device_id)
        
        # Force sync button
        sync_entity = BluestarForceSyncButton(coordinator, api, device_id, device_data)
        entities.append(sync_entity)
    
    _LOGGER.debug("BT4: Adding %d button entities", len(entities))
    async_add_entities(entities)


class BluestarForceSyncButton(CoordinatorEntity, ButtonEntity):
    """Bluestar AC force sync button."""

    def __init__(self, coordinator, api, device_id: str, device_data: Dict[str, Any]):
        """Initialize the force sync button."""
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self.device_data = device_data
        
        # Set unique ID
        self._attr_unique_id = f"bluestar_ac_{device_id}_force_sync"
        
        # Set name
        device_name = device_data.get("name", "Bluestar AC")
        self._attr_name = f"{device_name} Force Sync"
        
        # Set device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="Bluestar",
            model="Smart AC",
        )

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.debug("BT5: Force sync button pressed for device %s", self.device_id)
        
        try:
            # Send force sync command
            if hasattr(self.api, 'mqtt_client') and self.api.mqtt_client:
                # Use MQTT force sync
                topic = f"things/{self.device_id}/control"
                payload = {"fpsh": 1}
                
                import json
                import asyncio
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    self.api.mqtt_client.publish,
                    topic,
                    json.dumps(payload),
                    0
                )
                _LOGGER.debug("BT6: Force sync sent via MQTT")
            else:
                # Fallback to HTTP
                await self.api.set_state(self.device_id, fpsh=1)
                _LOGGER.debug("BT7: Force sync sent via HTTP")
                
        except Exception as e:
            _LOGGER.error("BT8: Force sync failed: %s", e)
