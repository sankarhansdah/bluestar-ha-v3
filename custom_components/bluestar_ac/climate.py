"""Climate platform for Bluestar Smart AC integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    FanMode,
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

# Fan Speed mapping
FAN_SPEED_MAP = {
    2: FanMode.LOW,        # Low
    3: FanMode.MEDIUM,     # Medium
    4: FanMode.HIGH,       # High
    6: FanMode.TURBO,      # Turbo
    7: FanMode.AUTO,       # Auto
}

FAN_SPEED_REVERSE_MAP = {v: k for k, v in FAN_SPEED_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bluestar climate entities."""
    _LOGGER.debug("CL1 climate module imported")
    
    # Safety check - verify coordinator exists
    if config_entry.entry_id not in hass.data[DOMAIN]:
        _LOGGER.error("CLX Coordinator not found in hass.data for entry %s", config_entry.entry_id)
        return
    
    coordinator: BluestarDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    
    _LOGGER.debug("CL2 climate async_setup_entry() start")
    
    try:
        # Get devices from coordinator
        devices = coordinator.data.get("devices", {})
        
        if not devices:
            _LOGGER.warning("CL3 No devices found in coordinator data")
            return
        
        # Create climate entities for each device
        entities = []
        for device_id, device_data in devices.items():
            try:
                entity = BluestarClimateEntity(coordinator, api, device_id, device_data)
                entities.append(entity)
                _LOGGER.debug("CL4 Created climate entity for device %s", device_id)
            except Exception as e:
                _LOGGER.exception("CL5 Failed to create climate entity for device %s: %s", device_id, e)
        
        _LOGGER.debug("CL6 adding %d climate entities", len(entities))
        async_add_entities(entities, update_before_add=True)
        _LOGGER.debug("CL7 climate async_setup_entry() done")
        
    except Exception as e:
        _LOGGER.exception("CLX climate setup failed: %s", e)
        raise


class BluestarClimateEntity(CoordinatorEntity, ClimateEntity):
    """Representation of a Bluestar Smart AC climate entity."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.HVAC_MODE
        | ClimateEntityFeature.SWING_MODE
    )

    def __init__(
        self,
        coordinator: BluestarDataUpdateCoordinator,
        api,
        device_id: str,
        device_data: dict[str, Any],
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._api = api
        self._device_id = device_id
        self._device_data = device_data
        
        # Set unique ID
        self._attr_unique_id = f"bluestar_ac_{device_id}"
        
        # Set device name
        self._attr_name = device_data.get("name", f"Bluestar AC {device_id[:8]}")
        
        # Set supported modes
        self._attr_hvac_modes = list(HVAC_MODE_REVERSE_MAP.keys())
        self._attr_fan_modes = list(FAN_SPEED_REVERSE_MAP.keys())
        
        # Set swing modes
        self._attr_swing_modes = [
            "off",
            "15°",
            "30°",
            "45°",
            "60°",
            "auto"
        ]
        
        # Set temperature range
        self._attr_min_temp = MIN_TEMP
        self._attr_max_temp = MAX_TEMP
        self._attr_target_temperature_step = 1.0

    @property
    def device_data(self) -> dict[str, Any]:
        """Get device data from coordinator."""
        devices = self.coordinator.data.get("devices", {})
        return devices.get(self._device_id, {})

    @property
    def device_name(self) -> str:
        """Get device name."""
        return self.device_data.get("name", f"Bluestar AC {self._device_id[:8]}")

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        current_temp = self.device_data.get("state", {}).get("current_temp", "25.0")
        try:
            return float(current_temp)
        except (ValueError, TypeError):
            return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        target_temp = self.device_data.get("state", {}).get("temperature", "26.0")
        try:
            return float(target_temp)
        except (ValueError, TypeError):
            return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        mode = self.device_data.get("state", {}).get("mode", 2)
        return HVAC_MODE_MAP.get(mode, HVACMode.COOL)

    @property
    def fan_mode(self) -> str:
        """Return the current fan mode."""
        fan_speed = self.device_data.get("state", {}).get("fan_speed", 2)
        return FAN_SPEED_MAP.get(fan_speed, FanMode.LOW)

    @property
    def swing_mode(self) -> str:
        """Return the current swing mode."""
        vswing = self.device_data.get("state", {}).get("vertical_swing", 0)
        
        if vswing == 0:
            return "off"
        elif vswing == 1:
            return "15°"
        elif vswing == 2:
            return "30°"
        elif vswing == 3:
            return "45°"
        elif vswing == 4:
            return "60°"
        elif vswing == -1:
            return "auto"
        else:
            return "off"

    @property
    def is_on(self) -> bool:
        """Return if the device is on."""
        return self.device_data.get("state", {}).get("power", False)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        
        control_data = {"stemp": str(temperature)}
        await self._send_control_command(control_data)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target HVAC mode."""
        mode = HVAC_MODE_REVERSE_MAP.get(hvac_mode, 2)
        control_data = {"mode": mode}
        await self._send_control_command(control_data)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        fan_speed = FAN_SPEED_REVERSE_MAP.get(fan_mode, 2)
        control_data = {"fspd": fan_speed}
        await self._send_control_command(control_data)

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set new target swing mode."""
        swing_map = {
            "off": 0,
            "15°": 1,
            "30°": 2,
            "45°": 3,
            "60°": 4,
            "auto": -1,
        }
        vswing = swing_map.get(swing_mode, 0)
        control_data = {"vswing": vswing}
        await self._send_control_command(control_data)

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        control_data = {"pow": 1}
        await self._send_control_command(control_data)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        control_data = {"pow": 0}
        await self._send_control_command(control_data)

    async def _send_control_command(self, control_data: dict[str, Any]) -> None:
        """Send control command to the device."""
        try:
            _LOGGER.debug("Sending control command to device %s: %s", self._device_id, control_data)
            await self._api.async_control_device(self._device_id, control_data)
            
            # Refresh coordinator data
            await self.coordinator.async_request_refresh()
            
        except Exception as e:
            _LOGGER.error("Failed to send control command: %s", e)
            raise
