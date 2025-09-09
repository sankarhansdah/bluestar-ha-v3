"""Bluestar Smart AC switch platform."""

import logging
from typing import Any, Dict

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Bluestar switch entities."""
    _LOGGER.debug("SW1: Setting up switch platform")
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    
    devices = coordinator.get_all_devices()
    _LOGGER.debug("SW2: Found %d devices for switches", len(devices))
    
    entities = []
    for device_id, device_data in devices.items():
        _LOGGER.debug("SW3: Creating switch entities for device %s", device_id)
        
        # Display switch
        display_entity = BluestarDisplaySwitch(coordinator, api, device_id, device_data)
        entities.append(display_entity)
    
    _LOGGER.debug("SW4: Adding %d switch entities", len(entities))
    async_add_entities(entities)


class BluestarDisplaySwitch(CoordinatorEntity, SwitchEntity):
    """Bluestar AC display switch."""

    def __init__(self, coordinator, api, device_id: str, device_data: Dict[str, Any]):
        """Initialize the display switch."""
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self.device_data = device_data
        
        # Set unique ID
        self._attr_unique_id = f"bluestar_ac_{device_id}_display"
        
        # Set name
        device_name = device_data.get("name", "Bluestar AC")
        self._attr_name = f"{device_name} Display"
        
        # Set device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="Bluestar",
            model="Smart AC",
        )

    @property
    def is_on(self) -> bool:
        """Return if the display is on."""
        state = self.coordinator.get_device_state(self.device_id)
        display = state.get("display", 1)
        return display != 0

    async def async_turn_on(self) -> None:
        """Turn the display on."""
        _LOGGER.debug("SW5: Turning display on for device %s", self.device_id)
        await self.api.set_state(self.device_id, display=True)

    async def async_turn_off(self) -> None:
        """Turn the display off."""
        _LOGGER.debug("SW6: Turning display off for device %s", self.device_id)
        await self.api.set_state(self.device_id, display=False)