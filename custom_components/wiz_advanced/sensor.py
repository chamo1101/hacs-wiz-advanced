"""Real state of the bulb: scene, brightness, white temperature, speed, signal."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import WizConfigEntry
from .const import SCENES
from .coordinator import WizCoordinator
from .entity import wiz_device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: WizConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([WizStateSensor(entry.runtime_data)])


class WizStateSensor(CoordinatorEntity[WizCoordinator], SensorEntity):
    """Everything the bulb reports about itself."""

    _attr_has_entity_name = True
    _attr_name = "État"
    _attr_icon = "mdi:lightbulb-on-outline"

    def __init__(self, coordinator: WizCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.mac}_state"
        self._attr_device_info = wiz_device_info(coordinator)

    @property
    def native_value(self) -> str | None:
        return SCENES.get(self.coordinator.data.get("sceneId"), "Personnalisé")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        return {
            "allumee": data.get("state"),
            "scene_id": data.get("sceneId"),
            "intensite": data.get("dimming"),
            "temperature_blanc": data.get("temp"),
            "vitesse": data.get("speed"),
            "rssi": data.get("rssi"),
            "ip": self.coordinator.host,
        }
