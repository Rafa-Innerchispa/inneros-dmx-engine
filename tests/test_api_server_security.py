import importlib
import os
import unittest
from unittest.mock import patch

import src.api_server as api_server


class TestDMXAPISecurity(unittest.TestCase):
    def _reload(self, **env):
        values = {
            "DMX_API_HOST": "127.0.0.1",
            "DMX_API_PORT": "18796",
            "DMX_CORS_ORIGIN": "http://127.0.0.1",
            "DMX_EXPOSE_TOPOLOGY": "0",
        }
        values.update(env)
        with patch.dict(os.environ, values, clear=False):
            return importlib.reload(api_server)

    def test_safe_defaults_are_loopback_and_dedicated_port(self):
        module = self._reload()
        self.assertEqual(module.HOST, "127.0.0.1")
        self.assertEqual(module.PORT, 18796)
        self.assertNotEqual(module.CORS_ORIGIN, "*")

    def test_status_hides_topology_by_default(self):
        module = self._reload(DMX_EXPOSE_TOPOLOGY="0")
        payload = module.status_payload()
        self.assertTrue(payload["ok"])
        self.assertNotIn("target_ip", payload)
        self.assertNotIn("universe", payload)

    def test_topology_requires_explicit_opt_in(self):
        module = self._reload(DMX_EXPOSE_TOPOLOGY="1")
        payload = module.status_payload()
        self.assertIn("target_ip", payload)
        self.assertIn("universe", payload)

    def test_server_can_bind_loopback_ephemeral_port(self):
        module = self._reload()
        server = module.build_server(host="127.0.0.1", port=0)
        try:
            self.assertEqual(server.server_address[0], "127.0.0.1")
            self.assertGreater(server.server_address[1], 0)
        finally:
            server.server_close()


if __name__ == "__main__":
    unittest.main()
