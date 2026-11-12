"""Scene selection: 17 firmware scenes, including Dim-to-warm."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import WizConfigEntry
from .const import NAME_TO_ID, SCENES
from .coordinator import WizCoordinator
from .entity import wiz_device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: WizConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([WizSceneSelect(entry.runtime_data)])


class WizSceneSelect(CoordinatorEntity[WizCoordinator], SelectEntity):
    """The scene currently programmed on the bulb."""

    _attr_has_entity_name = True
    _attr_name = "Scène"
    _attr_icon = "mdi:lightbulb-group"
    _attr_options = list(SCENES.values())

    def __init__(self, coordinator: WizCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.mac}_scene"
        self._attr_device_info = wiz_device_info(coordinator)

    @property
    def current_option(self) -> str | None:
        return SCENES.get(self.coordinator.data.get("sceneId"))

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_scene(
            NAME_TO_ID[option], self.coordinator.data.get("speed")
        )
