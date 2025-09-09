"""Bluestar Smart AC select platform."""

import logging
from typing import Any, Dict, List

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BLUESTAR_SWING_MODES, DOMAIN, HA_SWING_MODES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Bluestar select entities."""
    _LOGGER.debug("SL1: Setting up select platform")
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    
    devices = coordinator.get_all_devices()
    _LOGGER.debug("SL2: Found %d devices for selects", len(devices))
    
    entities = []
    for device_id, device_data in devices.items():
        _LOGGER.debug("SL3: Creating select entities for device %s", device_id)
        
        # Vertical swing select
        vswing_entity = BluestarVerticalSwingSelect(coordinator, api, device_id, device_data)
        entities.append(vswing_entity)
        
        # Horizontal swing select
        hswing_entity = BluestarHorizontalSwingSelect(coordinator, api, device_id, device_data)
        entities.append(hswing_entity)
    
    _LOGGER.debug("SL4: Adding %d select entities", len(entities))
    async_add_entities(entities)


class BluestarVerticalSwingSelect(CoordinatorEntity, SelectEntity):
    """Bluestar AC vertical swing select."""

    def __init__(self, coordinator, api, device_id: str, device_data: Dict[str, Any]):
        """Initialize the vertical swing select."""
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self.device_data = device_data
        
        # Set unique ID
        self._attr_unique_id = f"bluestar_ac_{device_id}_vswing"
        
        # Set name
        device_name = device_data.get("name", "Bluestar AC")
        self._attr_name = f"{device_name} Vertical Swing"
        
        # Set device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="Bluestar",
            model="Smart AC",
        )

    @property
    def options(self) -> List[str]:
        """Return list of available options."""
        return list(HA_SWING_MODES.keys())

    @property
    def current_option(self) -> str:
        """Return current option."""
        state = self.coordinator.get_device_state(self.device_id)
        vswing = state.get("vswing", 0)
        return BLUESTAR_SWING_MODES.get(vswing, "off")

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        _LOGGER.debug("SL5: Setting vertical swing to %s", option)
        swing_value = HA_SWING_MODES.get(option, 0)
        await self.api.set_state(self.device_id, vswing=swing_value)


class BluestarHorizontalSwingSelect(CoordinatorEntity, SelectEntity):
    """Bluestar AC horizontal swing select."""

    def __init__(self, coordinator, api, device_id: str, device_data: Dict[str, Any]):
        """Initialize the horizontal swing select."""
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self.device_data = device_data
        
        # Set unique ID
        self._attr_unique_id = f"bluestar_ac_{device_id}_hswing"
        
        # Set name
        device_name = device_data.get("name", "Bluestar AC")
        self._attr_name = f"{device_name} Horizontal Swing"
        
        # Set device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="Bluestar",
            model="Smart AC",
        )

    @property
    def options(self) -> List[str]:
        """Return list of available options."""
        return list(HA_SWING_MODES.keys())

    @property
    def current_option(self) -> str:
        """Return current option."""
        state = self.coordinator.get_device_state(self.device_id)
        hswing = state.get("hswing", 0)
        return BLUESTAR_SWING_MODES.get(hswing, "off")

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        _LOGGER.debug("SL6: Setting horizontal swing to %s", option)
        swing_value = HA_SWING_MODES.get(option, 0)
        await self.api.set_state(self.device_id, hswing=swing_value)
