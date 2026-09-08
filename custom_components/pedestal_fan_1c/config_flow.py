"""Config flow for Xiaomi Mi Smart Standing Fan 1C."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers import selector
from miio import DeviceException, Fan1C

from .const import CONF_TOKEN, DOMAIN, MODEL, TOKEN_LENGTH


class Fan1CConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the integration setup flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure a fan by its local address and token."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            token = user_input[CONF_TOKEN].strip().lower()
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            try:
                token_bytes = bytes.fromhex(token)
            except ValueError:
                token_bytes = b""

            if len(token) != TOKEN_LENGTH or len(token_bytes) != TOKEN_LENGTH // 2:
                errors[CONF_TOKEN] = "invalid_token"
            else:
                try:
                    device = Fan1C(host, token, model=MODEL)
                    await self.hass.async_add_executor_job(device.status)
                except DeviceException:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(
                        title="Mi Smart Standing Fan 1C",
                        data={CONF_HOST: host, CONF_TOKEN: token},
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Required(CONF_TOKEN): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
