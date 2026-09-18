"""Xiaomi Mi Smart Standing Fan 1C integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from miio import Fan1C

from .const import CONF_TOKEN, MODEL, PLATFORMS
from .coordinator import Fan1CCoordinator

type Fan1CConfigEntry = ConfigEntry[Fan1CCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: Fan1CConfigEntry) -> bool:
    """Set up the fan from a config entry."""
    device = Fan1C(
        entry.data[CONF_HOST],
        entry.data[CONF_TOKEN],
        model=MODEL,
    )
    coordinator = Fan1CCoordinator(hass, device)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(
        entry, [Platform(platform) for platform in PLATFORMS]
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: Fan1CConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(
        entry, [Platform(platform) for platform in PLATFORMS]
    )
