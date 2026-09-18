"""Switch entities for Xiaomi Mi Smart Standing Fan 1C."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import Fan1CCoordinator
from .entity import Fan1CEntity


@dataclass(frozen=True, kw_only=True)
class Fan1CSwitchDescription(SwitchEntityDescription):
    """Describe a fan switch."""

    value_fn: Callable[[Any], bool]
    method: str


SWITCHES = (
    Fan1CSwitchDescription(
        key="led",
        translation_key="led",
        value_fn=lambda status: status.led,
        method="set_led",
    ),
    Fan1CSwitchDescription(
        key="buzzer",
        translation_key="buzzer",
        value_fn=lambda status: status.buzzer,
        method="set_buzzer",
    ),
    Fan1CSwitchDescription(
        key="child_lock",
        translation_key="child_lock",
        value_fn=lambda status: status.child_lock,
        method="set_child_lock",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[Fan1CCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up fan switches."""
    async_add_entities(
        Fan1CSwitch(entry.runtime_data, description) for description in SWITCHES
    )


class Fan1CSwitch(Fan1CEntity, SwitchEntity):
    """Representation of a fan setting switch."""

    entity_description: Fan1CSwitchDescription

    def __init__(
        self, coordinator: Fan1CCoordinator, description: Fan1CSwitchDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = self.entity_unique_id(description.key)

    @property
    def is_on(self) -> bool:
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_command(self.entity_description.method, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_command(self.entity_description.method, False)
