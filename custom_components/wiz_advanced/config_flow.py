"""Config flow: ask for the bulb IP, then verify it answers."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST

from .api import WizBulb, WizError
from .const import DOMAIN


class WizAdvancedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WiZ Advanced."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                pilot = await self.hass.async_add_executor_job(WizBulb(host).get_pilot)
            except WizError:
                errors["base"] = "cannot_connect"
            else:
                unique = str(pilot.get("mac") or host)
                await self.async_set_unique_id(unique)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(
                    title=f"WiZ {unique[-6:].upper()}", data={CONF_HOST: host}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )
