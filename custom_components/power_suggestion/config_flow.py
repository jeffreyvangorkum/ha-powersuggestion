"""Config flow for Power Suggestion integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_DEVICE_NAME,
    CONF_POWER_ENTITY,
    CONF_AI_TASK_ENTITY,
    CONF_SMART_METER_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_SOLAR_FORECAST_ENTITY,
)

_LOGGER = logging.getLogger(__name__)

STATUS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_NAME): selector.TextSelector(),
        vol.Required(CONF_POWER_ENTITY): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor", device_class="power")
        ),
        vol.Required(CONF_AI_TASK_ENTITY): selector.EntitySelector(
            selector.EntitySelectorConfig()
        ),
        vol.Required(CONF_SMART_METER_ENTITY): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor", device_class="power")
        ),
        vol.Required(CONF_SOLAR_POWER_ENTITY): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor", device_class="power")
        ),
        vol.Required(CONF_SOLAR_FORECAST_ENTITY): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain="sensor", integration="forecast_solar", device_class="power"
            )
        ),
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Power Suggestion."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_DEVICE_NAME], data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=STATUS_SCHEMA, errors=errors
        )
