"""Invalid requests must never become a full-brightness stage command."""
import json
import threading
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src import api_server


class TestControlValidation(unittest.TestCase):
    def setUp(self):
        self.fake = MagicMock()
        self.fake.engine.fixtures = {"tacho_peces": object(), "pulpo_01": object()}
        self.patch = patch.object(api_server, "runner", self.fake)
        self.patch.start()
        self.server = api_server.build_server(host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = "http://127.0.0.1:" + str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.patch.stop()

    def send(self, path, body):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        request = Request(self.url + path, data=data, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=2) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.load(error)

    def assert_no_control(self):
        self.fake.apply_static_scene.assert_not_called()
        self.fake.start_effect.assert_not_called()
        self.fake.blackout.assert_not_called()
        self.fake.engine.scene_blackout.assert_not_called()

    def test_malformed_array_null_and_empty_objects_cannot_default_to_white_or_rainbow(self):
        for path in ("/api/color", "/api/effect", "/api/scene", "/api/intent"):
            for body in (b'{"color":bad}', [], None, {}):
                with self.subTest(path=path, body=body):
                    code, payload = self.send(path, body)
                    self.assertEqual(code, 400)
                    self.assertFalse(payload["ok"])
                    self.assert_no_control()

    def test_color_target_and_brightness_must_all_be_explicit_and_valid(self):
        valid = {"color": "verde", "target": "tacho_peces", "brightness": 64}
        for key in valid:
            value = {k: v for k, v in valid.items() if k != key}
            self.assertEqual(self.send('/api/color', value)[0], 400)
        for overrides in ({"color": "unknown"}, {"target": "unknown"}, {"target": []},
                          {"brightness": True}, {"brightness": 256}, {"brightness": -1}, {"brightness": "255"}):
            self.assertEqual(self.send('/api/color', valid | overrides)[0], 400)
        self.assert_no_control()

    def test_valid_static_color_and_zero_cleanup_preserve_explicit_target(self):
        for level in (64, 0):
            status, result = self.send('/api/color', {"color": "verde", "target": "pulpo_01", "brightness": level})
            self.assertEqual(status, 200)
            self.assertEqual(result['target'], 'pulpo_01')
            self.fake.apply_static_scene.assert_called_with(color_name='verde', brightness=level, target='pulpo_01')
        self.fake.start_effect.assert_not_called()

    def test_unknown_intent_cannot_turn_everything_on(self):
        status, payload = self.send('/api/intent', {'text': 'tell me about wifi'})
        self.assertEqual(status, 422)
        self.assertFalse(payload['ok'])
        self.assert_no_control()

    def test_invalid_scene_speed_is_rejected_before_actuation(self):
        for speed in ('nan', 'inf', -1, 0, 20, []):
            status, payload = self.send('/api/scene', {'mode': 'rainbow', 'speed': speed})
            self.assertEqual(status, 400)
            self.assertFalse(payload['ok'])
        self.assert_no_control()


if __name__ == '__main__':
    unittest.main()
