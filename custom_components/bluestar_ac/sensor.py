"""Bluestar Smart AC sensor platform."""

import logging
from typing import Any, Dict

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Bluestar sensor entities."""
    _LOGGER.debug("SE1: Setting up sensor platform")
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    
    devices = coordinator.get_all_devices()
    _LOGGER.debug("SE2: Found %d devices for sensors", len(devices))
    
    entities = []
    for device_id, device_data in devices.items():
        _LOGGER.debug("SE3: Creating sensor entities for device %s", device_id)
        
        # RSSI sensor
        rssi_entity = BluestarRSSISensor(coordinator, api, device_id, device_data)
        entities.append(rssi_entity)
        
        # Error sensor
        error_entity = BluestarErrorSensor(coordinator, api, device_id, device_data)
        entities.append(error_entity)
        
        # Connection status sensor
        connection_entity = BluestarConnectionSensor(coordinator, api, device_id, device_data)
        entities.append(connection_entity)
    
    _LOGGER.debug("SE4: Adding %d sensor entities", len(entities))
    async_add_entities(entities)


class BluestarRSSISensor(CoordinatorEntity, SensorEntity):
    """Bluestar AC RSSI sensor."""

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    def __init__(self, coordinator, api, device_id: str, device_data: Dict[str, Any]):
        """Initialize the RSSI sensor."""
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self.device_data = device_data
        
        # Set unique ID
        self._attr_unique_id = f"bluestar_ac_{device_id}_rssi"
        
        # Set name
        device_name = device_data.get("name", "Bluestar AC")
        self._attr_name = f"{device_name} Signal Strength"
        
        # Set device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="Bluestar",
            model="Smart AC",
        )

    @property
    def native_value(self) -> int:
        """Return RSSI value."""
        state = self.coordinator.get_device_state(self.device_id)
        return state.get("rssi", -45)


class BluestarErrorSensor(CoordinatorEntity, SensorEntity):
    """Bluestar AC error sensor."""

    def __init__(self, coordinator, api, device_id: str, device_data: Dict[str, Any]):
        """Initialize the error sensor."""
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self.device_data = device_data
        
        # Set unique ID
        self._attr_unique_id = f"bluestar_ac_{device_id}_error"
        
        # Set name
        device_name = device_data.get("name", "Bluestar AC")
        self._attr_name = f"{device_name} Error Code"
        
        # Set device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="Bluestar",
            model="Smart AC",
        )

    @property
    def native_value(self) -> int:
        """Return error code."""
        state = self.coordinator.get_device_state(self.device_id)
        return state.get("err", 0)


class BluestarConnectionSensor(CoordinatorEntity, SensorEntity):
    """Bluestar AC connection status sensor."""

    def __init__(self, coordinator, api, device_id: str, device_data: Dict[str, Any]):
        """Initialize the connection sensor."""
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self.device_data = device_data
        
        # Set unique ID
        self._attr_unique_id = f"bluestar_ac_{device_id}_connection"
        
        # Set name
        device_name = device_data.get("name", "Bluestar AC")
        self._attr_name = f"{device_name} Connection Status"
        
        # Set device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="Bluestar",
            model="Smart AC",
        )

    @property
    def native_value(self) -> str:
        """Return connection status."""
        device = self.coordinator.get_device(self.device_id)
        connected = device.get("connected", False)
        return "Connected" if connected else "Disconnected"
