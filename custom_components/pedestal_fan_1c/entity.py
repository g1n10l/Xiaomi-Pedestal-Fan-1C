"""Base entity for Xiaomi Mi Smart Standing Fan 1C."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Fan1CCoordinator


class Fan1CEntity(CoordinatorEntity[Fan1CCoordinator]):
    """Base class for fan entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: Fan1CCoordinator) -> None:
        super().__init__(coordinator)
        host = coordinator.device.ip
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            manufacturer="Xiaomi",
            model="Mi Smart Standing Fan 1C",
            name="Mi Smart Standing Fan 1C",
        )

    def entity_unique_id(self, key: str) -> str:
        """Build a unique ID for one entity of this fan."""
        return f"{self.coordinator.device.ip}_{key}"
