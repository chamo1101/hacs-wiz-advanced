"""State polling for a WiZ bulb."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WizBulb, WizError
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class WizCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls getPilot and caches the static system config."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        self.host = host
        self.bulb = WizBulb(host)
        self.system: dict[str, Any] = {}
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    @property
    def mac(self) -> str:
        return str(self.data.get("mac") or self.host)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.hass.async_add_executor_job(self.bulb.get_pilot)
        except WizError as err:
            raise UpdateFailed(str(err)) from err
        if not self.system:
            try:
                self.system = await self.hass.async_add_executor_job(self.bulb.get_system_config)
            except WizError:
                self.system = {}
        return data

    async def async_set_scene(self, scene_id: int, speed: int | None = None) -> None:
        await self.hass.async_add_executor_job(self.bulb.set_scene, scene_id, speed)
        await self.async_request_refresh()

    async def async_set_speed(self, speed: int) -> None:
        await self.hass.async_add_executor_job(self.bulb.set_speed, speed)
        await self.async_request_refresh()
