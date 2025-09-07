"""Minimal Climate platform for Bluestar Smart AC integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from .const import DOMAIN, MIN_TEMP, MAX_TEMP, DEFAULT_TEMP
from .coordinator import BluestarDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Minimal mappings for testing
HVAC_MODE_MAP = {
    0: HVACMode.FAN_ONLY,
    2: HVACMode.COOL,
}
HVAC_MODE_REVERSE_MAP = {v: k for k, v in HVAC_MODE_MAP.items()}

FAN_SPEED_MAP = {
    2: "low",
    7: "auto",
}
FAN_SPEED_REVERSE_MAP = {v: k for k, v in FAN_SPEED_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Bluestar AC climate platform."""
    _LOGGER.debug("CL1: Setting up climate platform for Bluestar AC")
    
    if DOMAIN not in hass.data:
        _LOGGER.error("CL2: Domain not found in hass.data. This should not happen.")
        return

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    if not coordinator:
        _LOGGER.error("CL3: Coordinator not found for entry_id: %s", config_entry.entry_id)
        return

    entities = []
    for device_id, device_data in coordinator.data.items():
        _LOGGER.debug("CL4: Creating climate entity for device: %s", device_id)
        entities.append(BluestarClimateEntity(coordinator, device_id, device_data))
    
    if entities:
        async_add_entities(entities)
        _LOGGER.info("CL5: Added %d Bluestar AC climate entities", len(entities))
    else:
        _LOGGER.warning("CL6: No Bluestar AC devices found to add as climate entities.")


class BluestarClimateEntity(CoordinatorEntity, ClimateEntity):
    """Representation of a Bluestar Smart AC climate entity."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = list(HVAC_MODE_MAP.values())
    _attr_fan_modes = list(FAN_SPEED_MAP.values())
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.HVAC_MODE
        | ClimateEntityFeature.TURN_ON_OFF
    )
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP

    def __init__(
        self,
        coordinator: BluestarDataUpdateCoordinator,
        device_id: str,
        device_data: dict[str, Any],
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_data = device_data
        self._attr_unique_id = f"{DOMAIN}_{device_id}_climate"
        self._attr_name = device_data.get("name", f"Bluestar AC {device_id[:8]}")
        _LOGGER.debug("CL7: Initialized climate entity for %s", self._attr_name)

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._attr_name,
            "manufacturer": "Bluestar",
            "model": "Smart AC",
            "via_device": (DOMAIN, self.coordinator.config_entry.entry_id),
        }

    @property
    def device_data(self) -> dict[str, Any]:
        """Return the device data from the coordinator."""
        return self.coordinator.data.get(self._device_id, {})

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        power_state = self.device_data.get("state", {}).get("pow", 0)
        if power_state == 0:
            return HVACMode.OFF
        
        mode = self.device_data.get("state", {}).get("mode", 2) # Default to Cool
        return HVAC_MODE_MAP.get(mode, HVACMode.COOL)

    @property
    def target_temperature(self) -> float:
        """Return the target temperature."""
        return float(self.device_data.get("state", {}).get("stemp", DEFAULT_TEMP))

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return float(self.device_data.get("state", {}).get("ctemp", DEFAULT_TEMP))

    @property
    def fan_mode(self) -> str:
        """Return the current fan mode."""
        fan_speed = self.device_data.get("state", {}).get("fspd", 2)
        return FAN_SPEED_MAP.get(fan_speed, "low")

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        _LOGGER.debug("CL8: Setting HVAC mode for %s to %s", self._attr_name, hvac_mode)
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
            return

        mode_value = HVAC_MODE_REVERSE_MAP.get(hvac_mode)
        if mode_value is None:
            _LOGGER.warning("CL9: Unsupported HVAC mode: %s", hvac_mode)
            return

        control_data = {"pow": 1, "mode": mode_value}
        await self.coordinator.api.async_control_device(self._device_id, control_data)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        _LOGGER.debug("CL10: Setting temperature for %s to %s", self._attr_name, temperature)
        control_data = {"stemp": int(temperature)}
        await self.coordinator.api.async_control_device(self._device_id, control_data)
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        _LOGGER.debug("CL11: Setting fan mode for %s to %s", self._attr_name, fan_mode)
        fan_speed_value = FAN_SPEED_REVERSE_MAP.get(fan_mode)
        if fan_speed_value is None:
            _LOGGER.warning("CL12: Unsupported fan mode: %s", fan_mode)
            return

        control_data = {"fspd": fan_speed_value}
        await self.coordinator.api.async_control_device(self._device_id, control_data)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn the AC on."""
        _LOGGER.debug("CL13: Turning on %s", self._attr_name)
        control_data = {"pow": 1}
        await self.coordinator.api.async_control_device(self._device_id, control_data)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the AC off."""
        _LOGGER.debug("CL14: Turning off %s", self._attr_name)
        control_data = {"pow": 0}
        await self.coordinator.api.async_control_device(self._device_id, control_data)
        await self.coordinator.async_request_refresh()