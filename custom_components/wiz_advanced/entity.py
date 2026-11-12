"""Shared entity plumbing."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .coordinator import WizCoordinator


def wiz_device_info(coordinator: WizCoordinator) -> DeviceInfo:
    system = coordinator.system or {}
    return DeviceInfo(
        identifiers={(DOMAIN, coordinator.mac)},
        manufacturer="WiZ",
        name=f"WiZ {coordinator.mac[-6:].upper()}" if coordinator.mac else "WiZ",
        model=system.get("moduleName"),
        sw_version=system.get("fwVersion"),
        configuration_url=f"http://{coordinator.host}",
    )
