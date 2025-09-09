"""Bluestar Smart AC config flow."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import BluestarAPI
from .const import DOMAIN

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
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("CF1: Starting config flow")
        
        if user_input is None:
            _LOGGER.debug("CF2: Showing form")
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            _LOGGER.debug("CF3: Validating credentials")
            await self._test_credentials(user_input["phone"], user_input["password"])
            _LOGGER.debug("CF4: Credentials validated successfully")
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("CF5: Unexpected error during config flow")
            errors["base"] = "unknown"

        if not errors:
            _LOGGER.debug("CF6: Creating config entry")
            return self.async_create_entry(
                title=f"Bluestar AC ({user_input['phone']})", data=user_input
            )

        _LOGGER.debug("CF7: Showing form with errors: %s", errors)
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def _test_credentials(self, phone: str, password: str) -> None:
        """Test credentials by attempting to login."""
        _LOGGER.debug("CF8: Testing credentials for phone %s", phone)
        
        api = BluestarAPI(phone, password)
        try:
            await api.login()
            _LOGGER.debug("CF9: Login successful")
        except Exception as e:
            _LOGGER.error("CF10: Login failed: %s", e)
            if "Login failed" in str(e):
                raise InvalidAuth from e
            else:
                raise CannotConnect from e
        finally:
            await api.close()


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect to the host."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""