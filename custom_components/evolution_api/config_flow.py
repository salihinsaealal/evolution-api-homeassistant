"""Config flow for Evolution API integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    BooleanSelector,
)

from .api import EvolutionApiClient, EvolutionApiError, EvolutionApiAuthError
from .const import (
    CONF_API_KEY,
    CONF_INSTANCE_ID,
    CONF_SERVER_URL,
    CONF_VERIFY_SSL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def get_user_data_schema(
    defaults: dict[str, Any] | None = None
) -> vol.Schema:
    """Get the schema for user data with optional defaults."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_SERVER_URL,
                default=defaults.get(CONF_SERVER_URL, ""),
            ): TextSelector(
                TextSelectorConfig(type=TextSelectorType.URL)
            ),
            vol.Required(
                CONF_INSTANCE_ID,
                default=defaults.get(CONF_INSTANCE_ID, ""),
            ): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT)
            ),
            vol.Required(
                CONF_API_KEY,
                default=defaults.get(CONF_API_KEY, ""),
            ): TextSelector(
                TextSelectorConfig(type=TextSelectorType.PASSWORD)
            ),
            vol.Optional(
                CONF_VERIFY_SSL,
                default=defaults.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            ): BooleanSelector(),
        }
    )


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Evolution API."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check for duplicate entries
            await self.async_set_unique_id(
                f"{user_input[CONF_SERVER_URL]}_{user_input[CONF_INSTANCE_ID]}"
            )
            self._abort_if_unique_id_configured()

            # Validate the connection
            try:
                result = await self._test_connection(user_input)
                if result == "success":
                    return self.async_create_entry(
                        title=f"Evolution API ({user_input[CONF_INSTANCE_ID]})",
                        data=user_input,
                    )
                elif result == "auth_error":
                    errors["base"] = "invalid_auth"
                elif result == "not_connected":
                    errors["base"] = "instance_not_connected"
                else:
                    errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=get_user_data_schema(user_input),
            errors=errors,
            description_placeholders={
                "docs_url": "https://doc.evolution-api.com/v2/api-reference"
            },
        )

    async def _test_connection(self, user_input: dict[str, Any]) -> str:
        """Test if we can connect to the Evolution API."""
        session = async_get_clientsession(self.hass)
        client = EvolutionApiClient(
            session=session,
            server_url=user_input[CONF_SERVER_URL],
            instance_id=user_input[CONF_INSTANCE_ID],
            api_key=user_input[CONF_API_KEY],
            verify_ssl=user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
        )

        try:
            is_connected = await client.check_connection()
            if is_connected:
                return "success"
            return "not_connected"
        except EvolutionApiAuthError:
            return "auth_error"
        except EvolutionApiError as err:
            _LOGGER.error("Error connecting to Evolution API: %s", err)
            return "connection_error"
        except aiohttp.ClientError as err:
            _LOGGER.error("Client error connecting to Evolution API: %s", err)
            return "connection_error"

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Evolution API."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Merge with existing data
            new_data = {**self.config_entry.data, **user_input}
            
            # Test connection with new settings
            session = async_get_clientsession(self.hass)
            client = EvolutionApiClient(
                session=session,
                server_url=new_data[CONF_SERVER_URL],
                instance_id=new_data[CONF_INSTANCE_ID],
                api_key=new_data[CONF_API_KEY],
                verify_ssl=new_data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            )

            try:
                is_connected = await client.check_connection()
                if is_connected:
                    # Update the config entry data
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data=new_data,
                    )
                    return self.async_create_entry(title="", data={})
                errors["base"] = "instance_not_connected"
            except EvolutionApiAuthError:
                errors["base"] = "invalid_auth"
            except EvolutionApiError:
                errors["base"] = "cannot_connect"

        # Show form with current values
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SERVER_URL,
                        default=self.config_entry.data.get(CONF_SERVER_URL, ""),
                    ): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.URL)
                    ),
                    vol.Required(
                        CONF_INSTANCE_ID,
                        default=self.config_entry.data.get(CONF_INSTANCE_ID, ""),
                    ): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    ),
                    vol.Required(
                        CONF_API_KEY,
                        default=self.config_entry.data.get(CONF_API_KEY, ""),
                    ): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                    vol.Optional(
                        CONF_VERIFY_SSL,
                        default=self.config_entry.data.get(
                            CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL
                        ),
                    ): BooleanSelector(),
                }
            ),
            errors=errors,
        )
