"""Is the bulb reachable on the LAN?"""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import WizConfigEntry
from .coordinator import WizCoordinator
from .entity import wiz_device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: WizConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([WizOnlineSensor(entry.runtime_data)])


class WizOnlineSensor(CoordinatorEntity[WizCoordinator], BinarySensorEntity):
    """Connectivity, straight from the polling result."""

    _attr_has_entity_name = True
    _attr_name = "En ligne"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: WizCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.mac}_online"
        self._attr_device_info = wiz_device_info(coordinator)

    @property
    def is_on(self) -> bool:
        return self.coordinator.last_update_success
