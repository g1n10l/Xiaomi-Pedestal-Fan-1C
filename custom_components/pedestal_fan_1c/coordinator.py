"""Data coordinator for Xiaomi Mi Smart Standing Fan 1C."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from miio import DeviceException, Fan1C

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class Fan1CCoordinator(DataUpdateCoordinator[Any]):
    """Coordinate status updates and commands."""

    def __init__(self, hass: HomeAssistant, device: Fan1C) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.device = device

    async def _async_update_data(self) -> Any:
        try:
            return await self.hass.async_add_executor_job(self.device.status)
        except DeviceException as err:
            raise UpdateFailed(f"Unable to read fan status: {err}") from err

    async def async_command(self, method: str, *args: Any) -> None:
        """Run a device command and refresh all entities."""
        try:
            command = getattr(self.device, method)
            await self.hass.async_add_executor_job(command, *args)
        except (DeviceException, ValueError) as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="command_failed",
                translation_placeholders={"error": str(err)},
            ) from err
        await self.async_request_refresh()
