"""Minimal Climate platform for Bluestar Smart AC integration - Test Version."""

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

# HVAC Mode mapping
HVAC_MODE_MAP = {
    0: HVACMode.FAN_ONLY,  # Fan
    2: HVACMode.COOL,       # Cool
    3: HVACMode.DRY,       # Dry
    4: HVACMode.AUTO,      # Auto
}

HVAC_MODE_REVERSE_MAP = {v: k for k, v in HVAC_MODE_MAP.items()}

# Fan Speed mapping (using strings instead of FanMode)
FAN_SPEED_MAP = {
    2: "low",        # Low
    3: "medium",     # Medium
    4: "high",       # High
    6: "turbo",      # Turbo
    7: "auto",       # Auto
}

FAN_SPEED_REVERSE_MAP = {v: k for k, v in FAN_SPEED_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bluestar climate entities from a config entry."""
    _LOGGER.info("🔧 Setting up Bluestar climate entities")
    
    try:
        # Get coordinator
        coordinator: BluestarDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
        
        # Create entities for each device
        entities = []
        devices = coordinator.data.get("devices", {})
        
        _LOGGER.info("📱 Found %d devices", len(devices))
        
        for device_id, device_data in devices.items():
            entity = BluestarClimateEntity(coordinator, device_id, device_data)
            entities.append(entity)
            _LOGGER.info("✅ Created climate entity for device: %s", device_id)
        
        if entities:
            async_add_entities(entities)
            _LOGGER.info("🎉 Successfully added %d climate entities", len(entities))
        else:
            _LOGGER.warning("⚠️ No devices found to create entities")
            
    except Exception as e:
        _LOGGER.error("❌ Error setting up climate entities: %s", e)
        raise


class BluestarClimateEntity(CoordinatorEntity, ClimateEntity):
    """Representation of a Bluestar AC climate entity."""

    def __init__(self, coordinator: BluestarDataUpdateCoordinator, device_id: str, device_data: dict):
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self.device_data = device_data
        self.device_name = device_data.get("name", f"Bluestar AC {device_id[:8]}")
        self._attr_unique_id = f"bluestar_ac_{device_id}"
        self._attr_name = self.device_name

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self.device_name,
            "manufacturer": "Bluestar",
            "model": "Smart AC",
        }

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return the list of supported features."""
        return (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.HVAC_MODE
        )

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        mode = self.device_data.get("state", {}).get("mode", 2)
        return HVAC_MODE_MAP.get(mode, HVACMode.COOL)

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available HVAC modes."""
        return [HVACMode.COOL, HVACMode.DRY, HVACMode.FAN_ONLY, HVACMode.AUTO]

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return float(self.device_data.get("state", {}).get("current_temp", 25.0))

    @property
    def target_temperature(self) -> float:
        """Return the target temperature."""
        return float(self.device_data.get("state", {}).get("temperature", DEFAULT_TEMP))

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return MIN_TEMP

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return MAX_TEMP

    @property
    def fan_mode(self) -> str:
        """Return the current fan mode."""
        fan_speed = self.device_data.get("state", {}).get("fan_speed", 2)
        return FAN_SPEED_MAP.get(fan_speed, "low")

    @property
    def fan_modes(self) -> list[str]:
        """Return the list of available fan modes."""
        return ["low", "medium", "high", "turbo", "auto"]

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target HVAC mode."""
        mode_value = HVAC_MODE_REVERSE_MAP.get(hvac_mode, 2)
        await self.coordinator.api.async_control_device(self._device_id, {"mode": mode_value})

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is not None:
            await self.coordinator.api.async_control_device(self._device_id, {"stemp": int(temperature)})

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        fan_speed = FAN_SPEED_REVERSE_MAP.get(fan_mode, 2)
        await self.coordinator.api.async_control_device(self._device_id, {"fspd": fan_speed})
