"""Timer entity for Xiaomi Mi Smart Standing Fan 1C."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import Fan1CCoordinator
from .entity import Fan1CEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[Fan1CCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the timer entity."""
    async_add_entities([Fan1CTimer(entry.runtime_data)])


class Fan1CTimer(Fan1CEntity, NumberEntity):
    """Fan delayed shutoff timer."""

    _attr_translation_key = "delay_off"
    _attr_native_min_value = 0
    _attr_native_max_value = 480
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: Fan1CCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = self.entity_unique_id("delay_off")

    @property
    def native_value(self) -> float:
        return self.coordinator.data.delay_off_countdown

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_command("delay_off", int(value))
