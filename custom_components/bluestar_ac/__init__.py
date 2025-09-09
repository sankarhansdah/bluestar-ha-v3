"""Bluestar Smart AC integration."""

import asyncio
import logging
import traceback
from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import BluestarAPI
from .const import DOMAIN
from .coordinator import BluestarCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.CLIMATE,
    Platform.SWITCH,
    Platform.SENSOR,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluestar Smart AC from a config entry."""
    _LOGGER.debug("B1: Starting setup for entry %s", entry.entry_id)
    
    hass.data.setdefault(DOMAIN, {})
    
    try:
        _LOGGER.debug("B2: Creating API client")
        api = BluestarAPI(
            phone=entry.data["phone"],
            password=entry.data["password"]
        )
        
        _LOGGER.debug("B3: Logging in")
        await api.login()
        
        _LOGGER.debug("B4: Creating coordinator")
        coordinator = BluestarCoordinator(hass, api)
        
        _LOGGER.debug("B5: Performing first refresh")
        await coordinator.async_config_entry_first_refresh()
        
        _LOGGER.debug("B6: Storing in hass.data")
        hass.data[DOMAIN][entry.entry_id] = {
            "api": api,
            "coordinator": coordinator,
        }
        
        _LOGGER.debug("B7: Setting up MQTT")
        try:
            await api.connect_mqtt(coordinator._async_update_data)
            _LOGGER.debug("B8: MQTT connected successfully")
        except Exception as e:
            _LOGGER.warning("B9: MQTT connection failed, continuing with HTTP only: %s", e)
        
        _LOGGER.debug("B10: Forwarding platform setups")
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        _LOGGER.debug("B11: Setup completed successfully")
        return True
        
    except asyncio.TimeoutError as e:
        _LOGGER.exception("B12: Timeout during setup")
        raise ConfigEntryNotReady from e
    except Exception as e:
        _LOGGER.error("B13: Fatal error during setup: %s", traceback.format_exc())
        raise


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading entry %s", entry.entry_id)
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        api = hass.data[DOMAIN][entry.entry_id]["api"]
        await api.close()
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok