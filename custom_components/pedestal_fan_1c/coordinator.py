"""Data coordinator for Xiaomi Mi Smart Standing Fan 1C."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from miio import DeviceException, Fan1C

from .const import DOMAIN, MODEL, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

COMMAND_STATE_FIELDS = {
    "on": "is_on",
    "off": "is_on",
    "set_speed": "speed",
    "set_oscillate": "oscillate",
    "set_led": "led",
    "set_buzzer": "buzzer",
    "set_child_lock": "child_lock",
    "delay_off": "delay_off_countdown",
    "set_mode": "mode",
}

COMMAND_ATTEMPTS = 2
RETRY_DELAY = 1
ACK_TIMEOUT_CHECKS = 3
ACK_TIMEOUT_DELAY = 2


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
        self._host = device.ip
        self._token = device.token
        self.device.retry_count = 0
        self._device_lock = asyncio.Lock()

    async def _async_update_data(self) -> Any:
        async with self._device_lock:
            try:
                return await self.hass.async_add_executor_job(self.device.status)
            except DeviceException:
                self._reset_device()
                try:
                    return await self.hass.async_add_executor_job(self.device.status)
                except DeviceException as err:
                    raise UpdateFailed(f"Unable to read fan status: {err}") from err

    async def async_command(self, method: str, *args: Any) -> None:
        """Run a device command and refresh all entities."""
        last_error: DeviceException | ValueError | None = None
        status = None

        async with self._device_lock:
            for attempt in range(COMMAND_ATTEMPTS):
                try:
                    command = getattr(self.device, method)
                    await self.hass.async_add_executor_job(command, *args)
                    last_error = None
                    status = None
                    break
                except ValueError as err:
                    last_error = err
                    break
                except DeviceException as err:
                    last_error = err
                    self._reset_device()

                    if self._is_ack_timeout(err):
                        status = await self._async_wait_for_command(method, args)
                    else:
                        await asyncio.sleep(RETRY_DELAY)
                        status = await self._async_status_after_failed_command()
                    if status is not None and self._command_succeeded(
                        status, method, args
                    ):
                        _LOGGER.debug(
                            "The %s command succeeded despite a missing response",
                            method,
                        )
                        last_error = None
                        break

                    if attempt + 1 < COMMAND_ATTEMPTS:
                        _LOGGER.debug(
                            "Retrying the %s command after no response", method
                        )

        if last_error is not None and self._is_ack_timeout(last_error):
            _LOGGER.warning(
                "The fan did not acknowledge the %s command; its state will be "
                "checked again during the next update",
                method,
            )
            await self.async_request_refresh()
            return

        if last_error is not None:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="command_failed",
                translation_placeholders={"error": str(last_error)},
            ) from last_error

        if status is not None:
            self.async_set_updated_data(status)
        else:
            await self.async_request_refresh()

    def _reset_device(self) -> None:
        """Replace a protocol instance that could not recover from a timeout."""
        self.device = Fan1C(self._host, self._token, model=MODEL)
        self.device.retry_count = 0

    async def _async_status_after_failed_command(self) -> Any | None:
        """Read status without failing an otherwise recoverable command."""
        try:
            return await self.hass.async_add_executor_job(self.device.status)
        except DeviceException:
            return None

    async def _async_wait_for_command(
        self, method: str, args: tuple[Any, ...]
    ) -> Any | None:
        """Wait for a command whose acknowledgement timed out."""
        for _ in range(ACK_TIMEOUT_CHECKS):
            await asyncio.sleep(ACK_TIMEOUT_DELAY)
            self._reset_device()
            status = await self._async_status_after_failed_command()
            if status is not None and self._command_succeeded(status, method, args):
                return status
        return None

    @staticmethod
    def _is_ack_timeout(error: BaseException) -> bool:
        """Check an exception chain for Xiaomi error code -9999."""
        current: BaseException | None = error
        while current is not None:
            if getattr(current, "code", None) == -9999:
                return True
            if "Unable to recover failed command" in str(current):
                return True
            current = current.__cause__ or current.__context__
        return False

    @staticmethod
    def _command_succeeded(status: Any, method: str, args: tuple[Any, ...]) -> bool:
        """Check whether a command took effect after its response was lost."""
        field = COMMAND_STATE_FIELDS.get(method)
        if field is None:
            return False

        expected = False if method == "off" else True if method == "on" else args[0]
        return getattr(status, field, None) == expected
