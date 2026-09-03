import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import api_server
from src.scene_registry import get_scene, load_scene_registry


class TestSceneRegistry(unittest.TestCase):
    def _write_registry(self, payload):
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(payload, handle)
        handle.close()
        return Path(handle.name)

    def test_default_demo_scene_is_discoverable(self):
        scenes, errors = load_scene_registry()
        self.assertEqual(errors, [])
        self.assertIn("flash_all_demo", scenes)
        self.assertEqual(scenes["flash_all_demo"]["steps"][0]["duration_ms"], 650)

    def test_hot_reload_reads_file_each_call(self):
        path = self._write_registry({
            "scenes": {
                "first_scene": {
                    "label": "First",
                    "loops": 1,
                    "steps": [{"target": "all", "color": "blanco", "brightness": 120, "duration_ms": 500}],
                }
            }
        })
        try:
            self.assertIsNotNone(get_scene("first_scene", path))
            path.write_text(json.dumps({
                "scenes": {
                    "second_scene": {
                        "label": "Second",
                        "loops": 1,
                        "steps": [{"target": "tachos", "color": "azul", "brightness": 100, "duration_ms": 200}],
                    }
                }
            }), encoding="utf-8")
            self.assertIsNone(get_scene("first_scene", path))
            self.assertIsNotNone(get_scene("second_scene", path))
        finally:
            path.unlink(missing_ok=True)

    def test_rejects_fast_full_stage_flash(self):
        path = self._write_registry({
            "scenes": {
                "unsafe_flash": {
                    "label": "Unsafe",
                    "loops": 4,
                    "steps": [
                        {"target": "all", "color": "blanco", "brightness": 255, "duration_ms": 100},
                        {"target": "all", "color": "blackout", "brightness": 0, "duration_ms": 100},
                    ],
                }
            }
        })
        try:
            scenes, errors = load_scene_registry(path)
            self.assertNotIn("unsafe_flash", scenes)
            self.assertTrue(errors)
            self.assertTrue(any("duration_below_500ms" in err for err in errors[0]["errors"]))
        finally:
            path.unlink(missing_ok=True)

    def test_status_exposes_dynamic_scene_for_webmcp_discovery(self):
        payload = api_server.status_payload()
        self.assertIn("flash_all_demo", payload["supported_scenes"])
        self.assertTrue(payload["dynamic_scenes"]["flash_all_demo"]["dynamic"])
        self.assertEqual(payload["dynamic_scenes"]["flash_all_demo"]["label"], "Flash All Demo")

    def test_dynamic_execution_uses_only_high_level_runner_calls(self):
        scene = {
            "label": "Bounded Test",
            "loops": 1,
            "steps": [
                {"target": "tachos", "color": "azul", "brightness": 90, "duration_ms": 150},
                {"target": "all", "color": "blackout", "brightness": 0, "duration_ms": 500},
            ],
        }
        with patch.object(api_server.runner, "stop_current_effect"), \
             patch.object(api_server.runner, "apply_static_scene") as apply_static, \
             patch.object(api_server.runner.engine, "scene_blackout") as blackout, \
             patch.object(api_server.time, "sleep"):
            result = api_server.execute_dynamic_scene("bounded_test", scene)

        self.assertTrue(result["ok"])
        self.assertEqual(result["executed_steps"], 2)
        apply_static.assert_called_once_with(color_name="azul", brightness=90, target="tachos")
        blackout.assert_called_once_with()
        self.assertFalse(api_server.runner.running)


if __name__ == "__main__":
    unittest.main()
