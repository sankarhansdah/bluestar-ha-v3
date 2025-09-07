"""Config flow for Bluestar Smart AC integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, BLUESTAR_BASE_URL, BLUESTAR_MQTT_ENDPOINT
from .api import BluestarAPI, BluestarAPIError

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("phone"): str,
        vol.Required("password"): str,
    }
)


class BluestarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bluestar Smart AC."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            await self._test_credentials(user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected error")
            errors["base"] = "unknown"

        if not errors:
            return self.async_create_entry(
                title=f"Bluestar AC ({user_input['phone']})", data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def _test_credentials(self, user_input: dict[str, Any]) -> None:
        """Test credentials by attempting to login and fetch devices."""
        _LOGGER.debug("CF1 validate_input() start")
        
        try:
            # Create API client
            _LOGGER.debug("CF2 creating API client")
            api = BluestarAPI(
                phone=user_input["phone"],
                password=user_input["password"],
                base_url=BLUESTAR_BASE_URL,
                mqtt_url=BLUESTAR_MQTT_ENDPOINT,
            )
            
            # Test login
            _LOGGER.debug("CF3 testing login")
            await api.async_login()
            
            # Test device fetch
            _LOGGER.debug("CF4 testing device fetch")
            devices = await api.async_get_devices()
            
            if not devices:
                raise InvalidAuth("No devices found")
            
            _LOGGER.debug("CF5 validation successful, found %d devices", len(devices))
            
            # Close API client
            await api.async_close()
            
        except BluestarAPIError as e:
            _LOGGER.error("CF6 BluestarAPIError during validation: %s", e)
            if "login" in str(e).lower() or "auth" in str(e).lower():
                raise InvalidAuth from e
            else:
                raise CannotConnect from e
        except Exception as e:
            _LOGGER.error("CF7 General error during validation: %s", e)
            raise CannotConnect from e


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
