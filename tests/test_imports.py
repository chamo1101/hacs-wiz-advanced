#!/usr/bin/env python3
"""Import smoke test: stubs Home Assistant so every platform module is really imported.

This catches the failure mode that matters most for a custom integration installed by HACS:
a typo in an import or a wrong base class makes HA refuse to load the platform ("Invalid config").
Run:  python3 tests/test_imports.py
"""
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def module(name):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


class Base:
    _attr_has_entity_name = False

    def __init__(self, *args, **kwargs):
        self.coordinator = args[0] if args else None

    def __class_getitem__(cls, item):  # ConfigEntry[X], CoordinatorEntity[X]
        return cls


class Platform:
    BINARY_SENSOR = "binary_sensor"
    NUMBER = "number"
    SELECT = "select"
    SENSOR = "sensor"


class NumberMode:
    SLIDER = "slider"
    BOX = "box"


class BinarySensorDeviceClass:
    CONNECTIVITY = "connectivity"


class UpdateFailed(Exception):
    pass


class ConfigFlowStub(Base):
    """ConfigFlow accepts a `domain=` class keyword in HA."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()


def mk(name="Stub"):
    """Distinct class per stub, so an entity can subclass two different real bases."""
    return type(name, (Base,), {})


class Schema:
    def __init__(self, schema=None):
        self.schema = schema


def Required(key, default=None):
    return key


# --- stub the modules actually imported by the component
module("homeassistant")
ce = module("homeassistant.config_entries")
ce.ConfigEntry = Base
ce.ConfigFlow = ConfigFlowStub
ce.ConfigFlowResult = dict
cst = module("homeassistant.const")
cst.CONF_HOST = "host"
cst.PERCENTAGE = "%"
cst.Platform = Platform
core = module("homeassistant.core")
core.HomeAssistant = Base
core.callback = lambda f: f
comp = module("homeassistant.components")
sel = module("homeassistant.components.select")
sel.SelectEntity = mk("SelectEntity")
num = module("homeassistant.components.number")
num.NumberEntity = mk("NumberEntity")
num.NumberMode = NumberMode
sen = module("homeassistant.components.sensor")
sen.SensorEntity = mk("SensorEntity")
bs = module("homeassistant.components.binary_sensor")
bs.BinarySensorEntity = mk("BinarySensorEntity")
bs.BinarySensorDeviceClass = BinarySensorDeviceClass
helpers = module("homeassistant.helpers")
ep = module("homeassistant.helpers.entity_platform")
ep.AddEntitiesCallback = mk("AddEntitiesCallback")
uc = module("homeassistant.helpers.update_coordinator")
uc.CoordinatorEntity = mk("CoordinatorEntity")
uc.DataUpdateCoordinator = mk("DataUpdateCoordinator")
uc.UpdateFailed = UpdateFailed
dr = module("homeassistant.helpers.device_registry")
dr.DeviceInfo = dict
for name in ("homeassistant.components", "homeassistant.helpers"):
    pass
vol = module("voluptuous")
vol.Schema = Schema
vol.Required = Required

FAILED = []

for name in (
    "api",
    "const",
    "coordinator",
    "entity",
    "select",
    "number",
    "sensor",
    "binary_sensor",
    "config_flow",
    "__init__",
):
    full = f"custom_components.wiz_advanced.{name}"
    try:
        __import__(full)
        print(f"  OK    {full}")
    except Exception as err:  # noqa: BLE001
        FAILED.append((full, err))
        print(f"  ECHEC {full}: {type(err).__name__}: {err}")

# sanity: the scene table is complete
from custom_components.wiz_advanced import api  # noqa: E402

assert len(api.SCENES) == 17, f"attendu 17 scènes, trouvé {len(api.SCENES)}"
assert api.SCENES[40] == "Dim-to-warm"
assert api.NAME_TO_ID["Dim-to-warm"] == 40
assert api.DYNAMIC_SCENES == frozenset({31, 32, 33})
print(f"  OK    table des scènes: {len(api.SCENES)} entrées, Dim-to-warm = 40")

if FAILED:
    sys.exit(f"{len(FAILED)} module(s) en échec")
print("Tous les modules s'importent correctement.")
