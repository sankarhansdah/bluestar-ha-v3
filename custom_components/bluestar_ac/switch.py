"""Switch platform for Bluestar Smart AC integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BluestarDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Bluestar AC switch platform."""
    _LOGGER.info("Setting up Bluestar AC switch platform")
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    
    _LOGGER.info("SW1: Coordinator data keys: %s", list(coordinator.data.keys()))
    _LOGGER.info("SW2: Coordinator data: %s", coordinator.data)
    
    for device_id, device_data in coordinator.data.items():
        _LOGGER.info("SW3: Creating switch for device %s with data: %s", device_id, device_data)
        entities.append(BluestarACSwitch(coordinator, device_id, device_data))
    
    if entities:
        async_add_entities(entities)
        _LOGGER.info("Added %d Bluestar AC switch entities", len(entities))
    else:
        _LOGGER.warning("No devices found in coordinator data to create switch entities")


class BluestarACSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Bluestar Smart AC switch entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BluestarDataUpdateCoordinator, device_id: str, device_data: dict[str, Any]) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_data = device_data
        self._attr_unique_id = f"{DOMAIN}_{device_id}_switch"
        self._attr_name = device_data.get("name", f"Bluestar AC {device_id[:8]}")
        _LOGGER.info("SW5: Initialized switch entity %s with name %s", self._attr_unique_id, self._attr_name)

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._attr_name,
            "manufacturer": "Bluestar",
            "model": "Smart AC",
        }

    @property
    def device_data(self) -> dict[str, Any]:
        """Return the device data from the coordinator."""
        data = self.coordinator.data.get(self._device_id, {})
        _LOGGER.info("SW4: Device data for %s: %s", self._device_id, data)
        return data

    @property
    def is_on(self) -> bool:
        """Return true if the AC is on."""
        power_state = self.device_data.get("state", {}).get("pow", 0)
        return power_state == 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the AC on."""
        control_data = {"pow": 1}
        await self.coordinator.api.async_control_device(self._device_id, control_data)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the AC off."""
        control_data = {"pow": 0}
        await self.coordinator.api.async_control_device(self._device_id, control_data)
        await self.coordinator.async_request_refresh()
