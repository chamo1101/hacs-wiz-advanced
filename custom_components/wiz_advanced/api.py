"""Minimal local API client for WiZ bulbs (UDP 38899). No Home Assistant imports here,
so this module is testable standalone."""
from __future__ import annotations

import json
import socket
from typing import Any

PORT = 38899

# Scenes actually implemented by tunable-white (SHTW) modules.
SCENES: dict[int, str] = {
    6: "Cozy",
    9: "Wake-up",
    10: "Bedtime",
    11: "Warm white",
    12: "Daylight",
    13: "Cool white",
    14: "Night light",
    15: "Focus",
    16: "Relax",
    18: "TV time",
    29: "Candlelight",
    30: "Golden white",
    31: "Pulse",
    32: "Steampunk",
    33: "Diwali",
    35: "Alarm",
    40: "Dim-to-warm",
}
NAME_TO_ID: dict[str, int] = {name: sid for sid, name in SCENES.items()}

# Scenes whose speed parameter actually changes what you see.
DYNAMIC_SCENES: frozenset[int] = frozenset({31, 32, 33})


class WizError(Exception):
    """Raised when the bulb does not answer or rejects a command."""


class WizBulb:
    """Blocking UDP client. Call it from an executor thread."""

    def __init__(self, host: str, timeout: float = 2.0) -> None:
        self.host = host
        self.timeout = timeout

    def _call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"method": method}
        if params is not None:
            payload["params"] = params
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        try:
            sock.sendto(json.dumps(payload).encode(), (self.host, PORT))
            raw, _ = sock.recvfrom(8192)
        except OSError as err:
            raise WizError(f"{self.host}: {err}") from err
        finally:
            sock.close()
        try:
            return json.loads(raw)
        except ValueError as err:
            raise WizError(f"invalid answer from {self.host}") from err

    # ------------------------------------------------------------------ reads
    def get_pilot(self) -> dict[str, Any]:
        """Current state: state, sceneId, dimming, temp, speed, rssi, mac."""
        answer = self._call("getPilot")
        result = answer.get("result")
        if not isinstance(result, dict):
            raise WizError(f"getPilot failed: {answer.get('error')}")
        return result

    def get_system_config(self) -> dict[str, Any]:
        answer = self._call("getSystemConfig")
        result = answer.get("result")
        return result if isinstance(result, dict) else {}

    # ----------------------------------------------------------------- writes
    def set_scene(self, scene_id: int, speed: int | None = None) -> None:
        """Apply a scene. The bulb switches itself on; power state is not forced here."""
        params: dict[str, Any] = {"sceneId": scene_id}
        if speed is not None and scene_id in DYNAMIC_SCENES:
            params["speed"] = speed
        answer = self._call("setPilot", params)
        if not answer.get("result", {}).get("success"):
            raise WizError(f"setPilot(sceneId={scene_id}) rejected: {answer.get('error')}")

    def set_speed(self, speed: int) -> None:
        """Change the speed of the scene currently running."""
        answer = self._call("setPilot", {"speed": speed})
        if not answer.get("result", {}).get("success"):
            raise WizError(f"setPilot(speed={speed}) rejected: {answer.get('error')}")

    def set_power(self, on: bool) -> None:
        answer = self._call("setPilot", {"state": on})
        if not answer.get("result", {}).get("success"):
            raise WizError("setPilot(state) rejected")

    def set_brightness(self, percent: int) -> None:
        answer = self._call("setPilot", {"dimming": max(1, min(100, percent))})
        if not answer.get("result", {}).get("success"):
            raise WizError("setPilot(dimming) rejected")

    def set_white(self, kelvin: int) -> None:
        answer = self._call("setPilot", {"temp": kelvin})
        if not answer.get("result", {}).get("success"):
            raise WizError("setPilot(temp) rejected")
