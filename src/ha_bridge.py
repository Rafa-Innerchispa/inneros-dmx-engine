"""
InnerOS DMX - Home Assistant Integration Bridge.
Communicates with Home Assistant at http://192.168.1.4:8123 via REST API.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List

DEFAULT_HA_URL = os.getenv("HOME_ASSISTANT_URL", "http://192.168.1.4:8123")
DEFAULT_HA_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN", "")

class HomeAssistantBridge:
    def __init__(self, base_url: str = DEFAULT_HA_URL, token: str = DEFAULT_HA_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def ping(self) -> bool:
        """Verifies connection with Home Assistant API."""
        url = f"{self.base_url}/api/"
        req = urllib.request.Request(url, headers=self._headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                return data.get("message") == "API running."
        except Exception:
            return False

    def call_service(self, domain: str, service: str, service_data: Dict[str, Any]) -> bool:
        """Invokes a Home Assistant service (e.g. light.turn_on)."""
        url = f"{self.base_url}/api/services/{domain}/{service}"
        payload = json.dumps(service_data).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=self._headers(), method="POST")
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                return resp.status == 200
        except Exception as e:
            print(f"[HA Bridge Error] Failed service call {domain}.{service}: {e}")
            return False

    def set_light_state(self, entity_id: str, brightness: Optional[int] = None,
                        rgb_color: Optional[List[int]] = None, transition: float = 0.0) -> bool:
        data: Dict[str, Any] = {"entity_id": entity_id}
        if brightness is not None:
            data["brightness"] = max(0, min(255, brightness))
        if rgb_color:
            data["rgb_color"] = rgb_color
        if transition > 0:
            data["transition"] = transition
        return self.call_service("light", "turn_on", data)

    def turn_off(self, entity_id: str, transition: float = 0.0) -> bool:
        data: Dict[str, Any] = {"entity_id": entity_id}
        if transition > 0:
            data["transition"] = transition
        return self.call_service("light", "turn_off", data)
