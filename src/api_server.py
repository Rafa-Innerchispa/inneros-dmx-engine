"""
InnerOS DMX - Real-time REST API & Natural Intent Server.
Provides local HTTP endpoints for Voice Gateway (voz.pcdoctor.ai / Qwen), Home Assistant, and MCP.
"""

import json
import os
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from .effects_engine import DynamicEffectsRunner, parse_color

PORT = int(os.getenv("DMX_API_PORT", "8096"))
runner = DynamicEffectsRunner(
    target_ip=os.getenv("DMX_NODE_IP", "192.168.1.10"),
    universe=int(os.getenv("DMX_UNIVERSE", "0"))
)

class DMXAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_OPTIONS(self):
        self._send_json(200, {"ok": True})

    def do_GET(self):
        if self.path == "/health" or self.path == "/api/status":
            self._send_json(200, {
                "ok": True,
                "status": "online",
                "target_ip": runner.engine.node.target_ip,
                "universe": runner.engine.node.universe,
                "current_effect": runner.current_effect,
                "running": runner.running
            })
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

        if path == "/api/blackout":
            runner.blackout()
            self._send_json(200, {"ok": True, "action": "blackout"})

        elif path == "/api/effect" or path == "/api/scene":
            mode = body.get("mode") or body.get("effect", "rainbow")
            speed = float(body.get("speed", 1.0))
            runner.start_effect(mode, speed=speed)
            self._send_json(200, {"ok": True, "effect": mode, "speed": speed})

        elif path == "/api/color":
            color = body.get("color", "blanco")
            target = body.get("target", "todas")
            brightness = int(body.get("brightness", 255))
            runner.apply_static_scene(color_name=color, brightness=brightness, target=target)
            self._send_json(200, {"ok": True, "color": color, "target": target, "brightness": brightness})

        elif path == "/api/intent":
            # Parser semántico de lenguaje natural (en español)
            text = body.get("text", "").lower()
            resp = self._parse_intent(text)
            self._send_json(200, resp)

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

        # Detección de color estático y objetivo
        target = "todas"
        if "pulpo" in text:
            target = "pulpos"
        elif "beam" in text:
            target = "beams"
        elif "tacho" in text or "par" in text:
            target = "tachos"
        elif "bola" in text:
            target = "bola_disco"

        # Buscar color mencionado
        for col in ["rojo", "verde", "azul", "amarillo", "magenta", "fucsia", "cian", "celeste", "turquesa", "naranja", "ambar", "dorado", "violeta", "morado", "purpura", "rosa", "rosado", "lima", "blanco", "neon", "cyberpunk"]:
            if col in text:
                runner.apply_static_scene(color_name=col, brightness=255, target=target)
                return {"ok": True, "parsed_action": f"color:{col}", "target": target, "text": text}

        # Por defecto si no coincide color pero pide encender
        runner.apply_static_scene(color_name="blanco_calido", brightness=255, target=target)
        return {"ok": True, "parsed_action": "color:blanco_calido", "target": target, "text": text}


def start_server():
    server = HTTPServer(("0.0.0.0", PORT), DMXAPIHandler)
    print(f"[InnerOS DMX API] Servidor de efectos y voz escuchando en http://0.0.0.0:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    start_server()
