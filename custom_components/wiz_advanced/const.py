"""Constants for the WiZ Advanced integration."""
from __future__ import annotations

from .api import DYNAMIC_SCENES, NAME_TO_ID, SCENES

DOMAIN = "wiz_advanced"
SCAN_INTERVAL = 5  # secondes entre deux interrogations (getPilot)

__all__ = ["DOMAIN", "SCAN_INTERVAL", "SCENES", "NAME_TO_ID", "DYNAMIC_SCENES"]
