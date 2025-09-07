"""The Bluestar Smart AC integration."""

from __future__ import annotations

import logging
import traceback
from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.typing import ConfigType
import asyncio

from .const import DOMAIN, PLATFORMS, BLUESTAR_BASE_URL, BLUESTAR_MQTT_ENDPOINT
from .coordinator import BluestarDataUpdateCoordinator
from .api import BluestarAPI, BluestarAPIError

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Bluestar Smart AC component."""
    _LOGGER.debug("B1 async_setup() called")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluestar Smart AC from a config entry."""
    _LOGGER.debug("B2 async_setup_entry() start for entry_id=%s title=%s", entry.entry_id, entry.title)
    
    hass.data.setdefault(DOMAIN, {})
    
    try:
        # Create API client
        _LOGGER.debug("B3 creating API client")
        api = BluestarAPI(
            phone=entry.data.get("phone"),
            password=entry.data.get("password"),
            base_url=BLUESTAR_BASE_URL,
            mqtt_url=BLUESTAR_MQTT_ENDPOINT,
        )
        
        # Login to API
        _LOGGER.debug("B4 logging in to API")
        await api.async_login()
        
        # Create coordinator
        _LOGGER.debug("B5 creating coordinator")
        coordinator = BluestarDataUpdateCoordinator(hass, api)
        
        # First refresh
        _LOGGER.debug("B6 first refresh start")
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.debug("B7 first refresh OK")
        
        # Store in hass.data
        hass.data[DOMAIN][entry.entry_id] = {
            "api": api,
            "coordinator": coordinator,
        }
        _LOGGER.debug("B8 stored hass.data for entry")
        
        # Forward to platforms
        _LOGGER.debug("B9 forward_entry_setups -> %s", PLATFORMS)
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.debug("B10 all platforms forwarded")
        
        # Register update listener
        _LOGGER.debug("B11 registering update listener")
        entry.async_on_unload(entry.add_update_listener(_async_update_listener))
        _LOGGER.debug("B12 async_setup_entry() done")
        
        return True
        
    except asyncio.TimeoutError as e:
        _LOGGER.exception("TMO: Timeout during setup at breadcrumb above. %s", e)
        raise ConfigEntryNotReady from e
    except BluestarAPIError as e:
        _LOGGER.error("API: Bluestar API error during setup: %s", e)
        raise ConfigEntryNotReady from e
    except Exception as e:
        _LOGGER.error(
            "FATAL in async_setup_entry at breadcrumb above: %s\n%s",
            e, traceback.format_exc()
        )
        raise ConfigEntryNotReady from e


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.debug("U1 _async_update_listener() called -> reloading entry")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("X1 async_unload_entry() start")
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        _LOGGER.debug("X2 platforms unloaded; cleaning hass.data")
        
        # Close API client
        if entry.entry_id in hass.data[DOMAIN]:
            api = hass.data[DOMAIN][entry.entry_id].get("api")
            if api:
                await api.async_close()
        
        hass.data[DOMAIN].pop(entry.entry_id, None)
        _LOGGER.debug("X3 async_unload_entry() done -> %s", unload_ok)
    
    return unload_ok
