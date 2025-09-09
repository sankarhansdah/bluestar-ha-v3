"""Bluestar Smart AC climate platform."""

import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.climate import ClimateEntity, HVACMode
from homeassistant.components.climate.const import ClimateEntityFeature, FanMode
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BLUESTAR_FAN_SPEEDS,
    BLUESTAR_MODES,
    BLUESTAR_SWING_MODES,
    DEFAULT_TEMP,
    DOMAIN,
    HA_FAN_SPEEDS,
    HA_MODES,
    HA_SWING_MODES,
    MAX_TEMP,
    MIN_TEMP,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Bluestar climate entities."""
    _LOGGER.debug("CL1: Setting up climate platform")
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    
    devices = coordinator.get_all_devices()
    _LOGGER.debug("CL2: Found %d devices", len(devices))
    
    entities = []
    for device_id, device_data in devices.items():
        _LOGGER.debug("CL3: Creating climate entity for device %s", device_id)
        entity = BluestarClimateEntity(coordinator, api, device_id, device_data)
        entities.append(entity)
    
    _LOGGER.debug("CL4: Adding %d climate entities", len(entities))
    async_add_entities(entities)


class BluestarClimateEntity(CoordinatorEntity, ClimateEntity):
    """Bluestar Smart AC climate entity."""

    _attr_temperature_unit = TEMP_CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.SWING_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator, api, device_id: str, device_data: Dict[str, Any]):
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self.device_data = device_data
        
        # Set unique ID
        self._attr_unique_id = f"bluestar_ac_{device_id}"
        
        # Set device name
        self._attr_name = device_data.get("name", "Bluestar AC")
        
        # Set device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=self._attr_name,
            manufacturer="Bluestar",
            model="Smart AC",
        )

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        state = self.coordinator.get_device_state(self.device_id)
        power = state.get("pow", 0)
        
        if power == 0:
            return HVACMode.OFF
            
        mode = state.get("mode", 2)
        ha_mode = BLUESTAR_MODES.get(mode, "cool")
        
        # Map to HA HVAC modes
        mode_mapping = {
            "fan": HVACMode.FAN_ONLY,
            "cool": HVACMode.COOL,
            "dry": HVACMode.DRY,
            "auto": HVACMode.AUTO,
        }
        
        return mode_mapping.get(ha_mode, HVACMode.COOL)

    @property
    def hvac_modes(self) -> List[HVACMode]:
        """Return list of available HVAC modes."""
        return [
            HVACMode.OFF,
            HVACMode.COOL,
            HVACMode.DRY,
            HVACMode.FAN_ONLY,
            HVACMode.AUTO,
        ]

    @property
    def current_temperature(self) -> Optional[float]:
        """Return current temperature."""
        state = self.coordinator.get_device_state(self.device_id)
        current_temp = state.get("ctemp")
        if current_temp:
            try:
                return float(current_temp)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def target_temperature(self) -> Optional[float]:
        """Return target temperature."""
        state = self.coordinator.get_device_state(self.device_id)
        target_temp = state.get("stemp")
        if target_temp:
            try:
                return float(target_temp)
            except (ValueError, TypeError):
                pass
        return DEFAULT_TEMP

    @property
    def temperature_step(self) -> float:
        """Return temperature step."""
        return 1.0

    @property
    def min_temp(self) -> float:
        """Return minimum temperature."""
        return MIN_TEMP

    @property
    def max_temp(self) -> float:
        """Return maximum temperature."""
        return MAX_TEMP

    @property
    def fan_mode(self) -> Optional[str]:
        """Return current fan mode."""
        state = self.coordinator.get_device_state(self.device_id)
        fan_speed = state.get("fspd", 2)
        return BLUESTAR_FAN_SPEEDS.get(fan_speed, "low")

    @property
    def fan_modes(self) -> List[str]:
        """Return list of available fan modes."""
        return list(HA_FAN_SPEEDS.keys())

    @property
    def swing_mode(self) -> Optional[str]:
        """Return current swing mode."""
        state = self.coordinator.get_device_state(self.device_id)
        vswing = state.get("vswing", 0)
        return BLUESTAR_SWING_MODES.get(vswing, "off")

    @property
    def swing_modes(self) -> List[str]:
        """Return list of available swing modes."""
        return list(HA_SWING_MODES.keys())

    @property
    def is_on(self) -> bool:
        """Return if the device is on."""
        state = self.coordinator.get_device_state(self.device_id)
        return state.get("pow", 0) == 1

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        _LOGGER.debug("CL5: Setting HVAC mode to %s", hvac_mode)
        
        if hvac_mode == HVACMode.OFF:
            await self.api.set_state(self.device_id, hvac_mode="off")
        else:
            # Map HA mode to Bluestar mode
            bluestar_mode = HA_MODES.get(hvac_mode.value, 2)
            await self.api.set_state(self.device_id, hvac_mode=hvac_mode.value)

    async def async_set_temperature(self, **kwargs) -> None:
        """Set target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is not None:
            _LOGGER.debug("CL6: Setting temperature to %s", temperature)
            await self.api.set_state(self.device_id, target_temperature=temperature)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan mode."""
        _LOGGER.debug("CL7: Setting fan mode to %s", fan_mode)
        await self.api.set_state(self.device_id, fan_mode=fan_mode)

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set swing mode."""
        _LOGGER.debug("CL8: Setting swing mode to %s", swing_mode)
        await self.api.set_state(self.device_id, swing_mode=swing_mode)

    async def async_turn_on(self) -> None:
        """Turn the device on."""
        _LOGGER.debug("CL9: Turning device on")
        await self.api.set_state(self.device_id, hvac_mode="cool")

    async def async_turn_off(self) -> None:
        """Turn the device off."""
        _LOGGER.debug("CL10: Turning device off")
        await self.api.set_state(self.device_id, hvac_mode="off")