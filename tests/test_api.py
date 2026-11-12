#!/usr/bin/env python3
"""Tests du client UDP WiZ. Lecture seule sur l'ampoule réelle : rien n'est modifié.

    python3 tests/test_api.py            # WIZ_IP=192.168.1.21 par défaut
    WIZ_IP= autre python3 tests/test_api.py
"""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# api.py est chargé par chemin : le paquet __init__.py importe Home Assistant,
# absent ici, et ce module doit rester testable sans HA installé.
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "wiz_api", ROOT / "custom_components" / "wiz_advanced" / "api.py"
)
api = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(api)

DYNAMIC_SCENES = api.DYNAMIC_SCENES
NAME_TO_ID = api.NAME_TO_ID
SCENES = api.SCENES
WizBulb = api.WizBulb
WizError = api.WizError

HOST = os.environ.get("WIZ_IP", "192.168.1.21")


class TestSceneTable(unittest.TestCase):
    def test_seventeen_scenes(self):
        self.assertEqual(len(SCENES), 17)

    def test_dim_to_warm_present(self):
        self.assertEqual(SCENES[40], "Dim-to-warm")
        self.assertEqual(NAME_TO_ID["Dim-to-warm"], 40)

    def test_names_are_unique(self):
        self.assertEqual(len(set(SCENES.values())), len(SCENES))

    def test_dynamic_subset(self):
        self.assertEqual(DYNAMIC_SCENES, frozenset({31, 32, 33}))
        self.assertTrue(DYNAMIC_SCENES.issubset(set(SCENES)))


class TestUnreachable(unittest.TestCase):
    def test_unreachable_bulb_raises(self):
        bulb = WizBulb("192.0.2.1", timeout=0.3)  # TEST-NET-1, jamais joignable
        with self.assertRaises(WizError):
            bulb.get_pilot()


class TestLiveBulb(unittest.TestCase):
    def setUp(self):
        self.bulb = WizBulb(HOST, timeout=2.0)

    def test_pilot_fields(self):
        try:
            pilot = self.bulb.get_pilot()
        except WizError as err:
            self.skipTest(f"ampoule injoignable ({err})")
        for key in ("mac", "rssi", "state"):
            self.assertIn(key, pilot)
        # sceneId 0 = réglage manuel (blanc/intensité), hors table des scènes
        if pilot.get("sceneId"):
            self.assertIn(pilot["sceneId"], SCENES, "scène inconnue renvoyée par l'ampoule")

    def test_system_config_fields(self):
        try:
            cfg = self.bulb.get_system_config()
        except WizError as err:
            self.skipTest(f"ampoule injoignable ({err})")
        self.assertIn("moduleName", cfg)
        self.assertIn("fwVersion", cfg)


if __name__ == "__main__":
    unittest.main(verbosity=2)
