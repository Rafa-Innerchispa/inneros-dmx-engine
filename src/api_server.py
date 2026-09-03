"""
InnerOS DMX - Real-time REST API & Natural Intent Server.
Provides local HTTP endpoints for Voice Gateway, Home Assistant, and MCP.

The API is loopback-only by default. Public consumers must go through the
sanitized InnerOS MCP/WebMCP bridge rather than talking to the DMX node directly.

Dynamic scenes are declarative and hot-reloaded from src/scenes.json on every
status/apply call. They can use only bounded high-level lighting primitives.
"""

import json
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from .effects_engine import DynamicEffectsRunner
from .scene_registry import get_scene, load_scene_registry, register_scene

HOST = os.getenv("DMX_API_HOST", "127.0.0.1").strip() or "127.0.0.1"
PORT = int(os.getenv("DMX_API_PORT", "18796"))
CORS_ORIGIN = os.getenv("DMX_CORS_ORIGIN", "http://127.0.0.1").strip() or "http://127.0.0.1"
EXPOSE_TOPOLOGY = os.getenv("DMX_EXPOSE_TOPOLOGY", "0").strip().lower() in {"1", "true", "yes"}

# Public-safe built-ins. Raw DMX channels and fast strobe effects are intentionally
# not exposed as public scene names.
PUBLIC_BUILTIN_SCENES = [
    "rainbow",
    "frenzy",
    "police",
    "fire",
    "chill_lounge",
    "morado_uv",
    "rojo_sangre",
    "blackout",
]
STATIC_SCENE_ALIASES = {
    "morado_uv": ("morado", "todas", 255),
    "rojo_sangre": ("rojo", "todas", 255),
}
RUNNER_EFFECTS = {"rainbow", "frenzy", "police", "fire", "chill_lounge"}

runner = DynamicEffectsRunner(
    target_ip=os.getenv("DMX_NODE_IP", "192.168.1.10"),
    universe=int(os.getenv("DMX_UNIVERSE", "0")),
)


def scene_catalog() -> tuple[list[str], dict, list[dict]]:
    dynamic, errors = load_scene_registry()
    names = list(PUBLIC_BUILTIN_SCENES)
    for name in sorted(dynamic):
        if name not in names:
            names.append(name)
    catalog = {
        name: {
            "label": dynamic[name].get("label", name.replace("_", " ").title()),
            "dynamic": True,
        }
        for name in dynamic
    }
    return names, catalog, errors


def status_payload() -> dict:
    """Return health and hot-reloaded capabilities with topology hidden by default."""
    supported_scenes, dynamic_catalog, registry_errors = scene_catalog()
    payload = {
        "ok": True,
        "status": "online",
        "current_effect": runner.current_effect,
        "running": runner.running,
        "fixture_count": len(runner.engine.fixtures),
        "supported_scenes": supported_scenes,
        "dynamic_scenes": dynamic_catalog,
        "scene_registry_ok": not registry_errors,
    }
    if registry_errors:
        payload["scene_registry_errors"] = registry_errors
    if EXPOSE_TOPOLOGY:
        payload["target_ip"] = runner.engine.node.target_ip
        payload["universe"] = runner.engine.node.universe
    return payload


def execute_dynamic_scene(scene_name: str, definition: dict) -> dict:
    """Execute a previously validated declarative scene synchronously and bounded."""
    runner.stop_current_effect()
    runner.current_effect = scene_name
    runner.running = True
    executed_steps = 0
    try:
        for _ in range(int(definition["loops"])):
            for step in definition["steps"]:
                color = step["color"]
                brightness = int(step["brightness"])
                target = step["target"]
                if color == "blackout" or brightness <= 0:
                    runner.engine.scene_blackout()
                else:
                    runner.apply_static_scene(
                        color_name=color,
                        brightness=brightness,
                        target=target,
                    )
                    # apply_static_scene stops background effects; this scene is the
                    # active synchronous execution, so restore truthful running state.
                    runner.current_effect = scene_name
                    runner.running = True
                executed_steps += 1
                time.sleep(int(step["duration_ms"]) / 1000.0)
    finally:
        runner.running = False
    return {
        "ok": True,
        "effect": scene_name,
        "dynamic": True,
        "executed_steps": executed_steps,
        "label": definition.get("label", scene_name),
    }


class DMXAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", CORS_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def log_message(self, format, *args):
        # Keep the local service quiet; systemd captures startup/runtime errors.
        return

    def do_OPTIONS(self):
        self._send_json(200, {"ok": True})

    def do_GET(self):
        if self.path in {"/health", "/api/status"}:
            self._send_json(200, status_payload())
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            body = json.loads(post_data)
        except Exception:
            body = {}

        path = self.path.split("?")[0]

        if path == "/api/scenes/register":
            name = str(body.get("name", "")).strip().lower()
            definition = body.get("scene")
            if name in PUBLIC_BUILTIN_SCENES:
                self._send_json(409, {"ok": False, "error": "reserved_scene_name", "scene": name})
                return
            result = register_scene(name, definition, overwrite=False)
            if not result.get("ok"):
                status = 409 if result.get("error") == "scene_already_exists" else 400
                self._send_json(status, result)
                return
            supported, catalog, _ = scene_catalog()
            self._send_json(201, {
                "ok": True,
                "action": "scene_registered",
                "scene": result["scene"],
                "definition": result["definition"],
                "supported_scenes": supported,
                "dynamic_scenes": catalog,
            })

        elif path == "/api/blackout":
            runner.blackout()
            self._send_json(200, {"ok": True, "action": "blackout"})

        elif path in {"/api/effect", "/api/scene"}:
            mode = str(body.get("mode") or body.get("effect", "rainbow")).strip().lower()
            speed = float(body.get("speed", 1.0))

            dynamic = get_scene(mode)
            if dynamic:
                self._send_json(200, execute_dynamic_scene(mode, dynamic))
            elif mode == "blackout":
                runner.blackout()
                self._send_json(200, {"ok": True, "effect": "blackout", "dynamic": False})
            elif mode in STATIC_SCENE_ALIASES:
                color, target, brightness = STATIC_SCENE_ALIASES[mode]
                runner.apply_static_scene(color_name=color, target=target, brightness=brightness)
                self._send_json(200, {"ok": True, "effect": mode, "dynamic": False})
            elif mode in RUNNER_EFFECTS:
                runner.start_effect(mode, speed=speed)
                self._send_json(200, {"ok": True, "effect": mode, "speed": speed, "dynamic": False})
            else:
                supported, _, _ = scene_catalog()
                self._send_json(400, {"ok": False, "error": "scene_not_supported", "supported_scenes": supported})

        elif path == "/api/color":
            color = body.get("color", "blanco")
            target = body.get("target", "todas")
            brightness = int(body.get("brightness", 255))
            runner.apply_static_scene(color_name=color, brightness=brightness, target=target)
            self._send_json(200, {"ok": True, "color": color, "target": target, "brightness": brightness})

        elif path == "/api/intent":
            text = body.get("text", "").lower()
            self._send_json(200, self._parse_intent(text))

        else:
            self._send_json(404, {"error": "Invalid POST endpoint"})

    def _parse_intent(self, text: str) -> dict:
        """Interpreta intenciones habladas en español."""
        if any(w in text for w in ["apaga", "apagar", "blackout", "oscuro"]):
            runner.blackout()
            return {"ok": True, "parsed_action": "blackout", "text": text}

        if any(w in text for w in ["arcoiris", "arco iris", "rainbow"]):
            runner.start_effect("rainbow", speed=1.0)
            return {"ok": True, "parsed_action": "effect:rainbow", "text": text}

        if any(w in text for w in ["fiesta", "frenzy", "disco", "loco", "bailar"]):
            runner.start_effect("frenzy", speed=1.0)
            return {"ok": True, "parsed_action": "effect:frenzy", "text": text}

        if any(w in text for w in ["policia", "policial", "patrulla", "alarma", "emergencia"]):
            runner.start_effect("police")
            return {"ok": True, "parsed_action": "effect:police", "text": text}

        if any(w in text for w in ["fuego", "chimenea", "fogata", "flama"]):
            runner.start_effect("fire")
            return {"ok": True, "parsed_action": "effect:fire", "text": text}

        if any(w in text for w in ["relax", "lounge", "tranquilo", "suave", "chill"]):
            runner.start_effect("chill_lounge")
            return {"ok": True, "parsed_action": "effect:chill_lounge", "text": text}

        target = "todas"
        if "pulpo" in text:
            target = "pulpos"
        elif "beam" in text:
            target = "beams"
        elif "tacho" in text or "par" in text:
            target = "tachos"
        elif "bola" in text:
            target = "bola_disco"

        for col in [
            "rojo", "verde", "azul", "amarillo", "magenta", "fucsia", "cian", "celeste",
            "turquesa", "naranja", "ambar", "dorado", "violeta", "morado", "purpura", "rosa",
            "rosado", "lima", "blanco", "neon", "cyberpunk",
        ]:
            if col in text:
                runner.apply_static_scene(color_name=col, brightness=255, target=target)
                return {"ok": True, "parsed_action": f"color:{col}", "target": target, "text": text}

        runner.apply_static_scene(color_name="blanco_calido", brightness=255, target=target)
        return {"ok": True, "parsed_action": "color:blanco_calido", "target": target, "text": text}


def build_server(host: str | None = None, port: int | None = None) -> HTTPServer:
    return HTTPServer((host or HOST, port if port is not None else PORT), DMXAPIHandler)


def start_server():
    server = build_server()
    print(f"[InnerOS DMX API] Servidor local escuchando en http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    start_server()
