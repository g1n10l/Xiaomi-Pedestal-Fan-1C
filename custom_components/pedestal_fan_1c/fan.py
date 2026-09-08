"""Fan entity for Xiaomi Mi Smart Standing Fan 1C."""

from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.percentage import ranged_value_to_percentage

from .const import PRESET_MODES, SPEED_RANGE
from .coordinator import Fan1CCoordinator
from .entity import Fan1CEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[Fan1CCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the fan entity."""
    async_add_entities([PedestalFan1C(entry.runtime_data)])


class PedestalFan1C(Fan1CEntity, FanEntity):
    """Representation of the pedestal fan."""

    _attr_name = None
    _attr_translation_key = "fan"
    _attr_supported_features = (
        FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.SET_SPEED
        | FanEntityFeature.OSCILLATE
        | FanEntityFeature.PRESET_MODE
    )
    _attr_preset_modes = PRESET_MODES
    _attr_speed_count = 3

    def __init__(self, coordinator: Fan1CCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = self.entity_unique_id("fan")

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.is_on

    @property
    def percentage(self) -> int:
        if not self.is_on:
            return 0
        return ranged_value_to_percentage(SPEED_RANGE, self.coordinator.data.speed)

    @property
    def oscillating(self) -> bool:
        return self.coordinator.data.oscillate

    @property
    def preset_mode(self) -> str:
        return self.coordinator.data.mode.value

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        if percentage == 0:
            await self.async_turn_off()
            return
        await self.coordinator.async_command("on")
        if percentage is not None:
            await self.async_set_percentage(percentage)
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_command("off")

    async def async_set_percentage(self, percentage: int) -> None:
        if percentage == 0:
            await self.async_turn_off()
            return
        speed = min(3, max(1, (percentage * 3 + 99) // 100))
        await self.coordinator.async_command("set_speed", speed)

    async def async_oscillate(self, oscillating: bool) -> None:
        await self.coordinator.async_command("set_oscillate", oscillating)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode not in PRESET_MODES:
            raise ValueError(f"Unsupported preset mode: {preset_mode}")
        mode_type = type(self.coordinator.data.mode)
        await self.coordinator.async_command("set_mode", mode_type(preset_mode))
