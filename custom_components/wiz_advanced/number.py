"""Speed of the animated scenes (Pulse, Steampunk, Diwali)."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import WizConfigEntry
from .coordinator import WizCoordinator
from .entity import wiz_device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: WizConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([WizSpeedNumber(entry.runtime_data)])


class WizSpeedNumber(CoordinatorEntity[WizCoordinator], NumberEntity):
    """Animation speed reported by the bulb."""

    _attr_has_entity_name = True
    _attr_name = "Vitesse"
    _attr_icon = "mdi:speedometer"
    _attr_native_min_value = 20
    _attr_native_max_value = 200
    _attr_native_step = 10
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: WizCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.mac}_speed"
        self._attr_device_info = wiz_device_info(coordinator)

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get("speed")

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_speed(int(value))
