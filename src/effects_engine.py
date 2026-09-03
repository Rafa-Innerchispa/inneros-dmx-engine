"""
InnerOS DMX Universal Procedural Effects & Intent Engine.
Generates dynamic procedural light shows, sine sweeps, color chases,
and natural language intent parsing for all 9 fixtures.
"""

import math
import time
import random
import colorsys
import threading
from typing import Dict, List, Tuple, Optional, Any
from .artnet_controller import InnerOSDMXEngine
from .fixture_profiles import FIXTURES, FIXTURE_DICT

# Diccionario semántico de colores naturales (RGBW)
COLOR_PALETTE = {
    # Básicos
    "rojo": (255, 0, 0, 0),
    "verde": (0, 255, 0, 0),
    "azul": (0, 0, 255, 0),
    "amarillo": (255, 255, 0, 0),
    "magenta": (255, 0, 200, 0),
    "fucsia": (255, 0, 180, 0),
    "cian": (0, 255, 255, 0),
    "celeste": (0, 180, 255, 50),
    "turquesa": (0, 255, 180, 0),
    "naranja": (255, 100, 0, 0),
    "ambar": (255, 140, 0, 0),
    "dorado": (255, 180, 20, 30),
    "violeta": (140, 0, 255, 0),
    "morado": (120, 0, 220, 0),
    "purpura": (160, 0, 255, 0),
    "rosa": (255, 80, 150, 50),
    "rosado": (255, 100, 160, 50),
    "lima": (80, 255, 0, 0),
    "blanco": (0, 0, 0, 255),
    "blanco_calido": (255, 200, 80, 200),
    "blanco_frio": (180, 220, 255, 255),
    "neon": (0, 255, 150, 100),
    "cyberpunk": (255, 0, 128, 0)
}

def parse_color(color_str: str) -> Tuple[int, int, int, int]:
    """Interpreta texto de color en español, HEX (#RRGGBB) o tupla RGB."""
    c = color_str.strip().lower().replace(" ", "_")
    if c in COLOR_PALETTE:
        return COLOR_PALETTE[c]
    if c.startswith("#") and len(c) == 7:
        try:
            r = int(c[1:3], 16)
            g = int(c[3:5], 16)
            b = int(c[5:7], 16)
            return (r, g, b, 0)
        except ValueError:
            pass
    return (255, 255, 255, 255)


class DynamicEffectsRunner:
    """Ejecutor de hilos para efectos dinámicos continuos y transiciones en tiempo real."""

    def __init__(self, target_ip: str = "192.168.1.10", universe: int = 0):
        self.engine = InnerOSDMXEngine(target_ip=target_ip, universe=universe)
        self.current_effect: Optional[str] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.params: Dict[str, Any] = {}

    def stop_current_effect(self):
        with self.lock:
            self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)

    def start_effect(self, effect_name: str, **params):
        """Inicia un generador de efectos en segundo plano."""
        self.stop_current_effect()
        with self.lock:
            self.current_effect = effect_name
            self.running = True
            self.params = params
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        effect = self.current_effect
        if effect == "rainbow":
            self._loop_rainbow()
        elif effect == "frenzy":
            self._loop_frenzy()
        elif effect == "police":
            self._loop_police()
        elif effect == "fire":
            self._loop_fire()
        elif effect == "sine_wave":
            self._loop_sine_wave()
        elif effect == "strobe_burst":
            self._loop_strobe_burst()
        elif effect == "chill_lounge":
            self._loop_chill_lounge()

    # --------------------------------------------------------------------------
    # EFECTO 1: ARCOÍRIS DINÁMICO (RAINBOW CHASE / WAVE)
    # --------------------------------------------------------------------------
    def _loop_rainbow(self):
        speed = self.params.get("speed", 1.0)
        t = 0.0
        while self.running:
            # Encender Master de todos los equipos
            for fix_id, fix in FIXTURE_DICT.items():
                if "master" in fix.channels:
                    self.engine.node.set_channel(fix.channels["master"], 255)

            # Ondas de color HSV desfasadas por fixture
            hue_base = (t * 0.1 * speed) % 1.0
            
            # Tachos con barrido cromático
            tacho_keys = ["tacho_escalera", "tacho_peces", "tacho_central", "tacho_plantas"]
            for idx, tid in enumerate(tacho_keys):
                h = (hue_base + (idx * 0.15)) % 1.0
                r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
                self.engine.set_fixture_rgb(tid, r, g, b, master=255)

            # Beams en fase complementaria
            for idx, bid in enumerate(["beam_01", "beam_02"]):
                h = (hue_base + 0.5 + (idx * 0.2)) % 1.0
                r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
                self.engine.set_fixture_rgbw(bid, r, g, b, w=0, master=255)

            # Pulpos en movimiento suave con color arcoíris
            for idx, pid in enumerate(["pulpo_01", "pulpo_02"]):
                pan_val = int(128 + 90 * math.sin(t * 0.8 * speed + idx))
                tilt_val = int(128 + 60 * math.cos(t * 1.2 * speed + idx))
                self.engine.set_pulpo_position(pid, pan_val, tilt_val, speed=5)
                h1 = (hue_base + 0.25) % 1.0
                h2 = (hue_base + 0.75) % 1.0
                r1, g1, b1 = [int(x * 255) for x in colorsys.hsv_to_rgb(h1, 1.0, 1.0)]
                r2, g2, b2 = [int(x * 255) for x in colorsys.hsv_to_rgb(h2, 1.0, 1.0)]
                # Barra 1
                fix = FIXTURE_DICT[pid]
                self.engine.node.set_channel(fix.channels["r1"], r1)
                self.engine.node.set_channel(fix.channels["g1"], g1)
                self.engine.node.set_channel(fix.channels["b1"], b1)
                # Barra 2
                self.engine.node.set_channel(fix.channels["r2"], r2)
                self.engine.node.set_channel(fix.channels["g2"], g2)
                self.engine.node.set_channel(fix.channels["b2"], b2)

            # Bola disco
            self.engine.set_fixture_rgbw("bola_disco", 255, 255, 255, w=100, master=200)
            self.engine.node.set_channel(FIXTURE_DICT["bola_disco"].channels["motor"], 120)

            self.engine.node.send()
            t += 0.05
            time.sleep(0.04)

    # --------------------------------------------------------------------------
    # EFECTO 2: FUEGO Y BRASAS (FIRE / WARM FLICKER)
    # --------------------------------------------------------------------------
    def _loop_fire(self):
        while self.running:
            for fix_id in FIXTURE_DICT:
                r = random.randint(220, 255)
                g = random.randint(30, 110)
                b = 0
                w = random.randint(0, 40)
                dim = random.randint(160, 255)
                self.engine.set_fixture_rgbw(fix_id, r, g, b, w=w, master=dim)

            # Pulpos posicionados hacia arriba con balanceo sutil
            tilt = random.randint(90, 130)
            for pid in ["pulpo_01", "pulpo_02"]:
                self.engine.set_pulpo_position(pid, 128, tilt, speed=20)

            self.engine.node.send()
            time.sleep(random.uniform(0.06, 0.14))

    # --------------------------------------------------------------------------
    # EFECTO 3: POLICIAL / ALERTA (POLICE EMERGENCY)
    # --------------------------------------------------------------------------
    def _loop_police(self):
        while self.running:
            # Fase Azul (Flashing)
            for _ in range(3):
                if not self.running: break
                for tid in ["tacho_escalera", "tacho_central", "beam_01", "pulpo_01"]:
                    self.engine.set_fixture_rgbw(tid, 0, 0, 255, w=0, master=255)
                for tid in ["tacho_peces", "tacho_plantas", "beam_02", "pulpo_02"]:
                    self.engine.set_fixture_rgbw(tid, 0, 0, 0, w=0, master=0)
                self.engine.node.send()
                time.sleep(0.08)
                self.engine.node.blackout()
                time.sleep(0.05)

            # Fase Roja (Flashing)
            for _ in range(3):
                if not self.running: break
                for tid in ["tacho_escalera", "tacho_central", "beam_01", "pulpo_01"]:
                    self.engine.set_fixture_rgbw(tid, 0, 0, 0, w=0, master=0)
                for tid in ["tacho_peces", "tacho_plantas", "beam_02", "pulpo_02"]:
                    self.engine.set_fixture_rgbw(tid, 255, 0, 0, w=0, master=255)
                self.engine.node.send()
                time.sleep(0.08)
                self.engine.node.blackout()
                time.sleep(0.05)

    # --------------------------------------------------------------------------
    # EFECTO 4: CHILL LOUNGE / AMBIENTE RELAJADO
    # --------------------------------------------------------------------------
    def _loop_chill_lounge(self):
        t = 0.0
        while self.running:
            # Tonos cálidos ámbar/dorado respirando lentamente
            brightness = int(140 + 70 * math.sin(t * 0.5))
            for tid in ["tacho_escalera", "tacho_peces", "tacho_central", "tacho_plantas"]:
                self.engine.set_fixture_rgbw(tid, 255, 140, 20, w=80, master=brightness)

            # Beams apuntados al suelo en violeta suave
            for bid in ["beam_01", "beam_02"]:
                self.engine.set_fixture_rgbw(bid, 100, 0, 180, w=0, master=100)

            # Pulpos fijos en ángulo cenital cálido
            for pid in ["pulpo_01", "pulpo_02"]:
                self.engine.set_pulpo_position(pid, 128, 110, speed=50)
                self.engine.set_fixture_rgbw(pid, 255, 120, 10, w=50, master=120)

            self.engine.node.send()
            t += 0.05
            time.sleep(0.05)

    # --------------------------------------------------------------------------
    # EFECTO 5: FRENZY FIESTA RÁPIDA
    # --------------------------------------------------------------------------
    def _loop_frenzy(self):
        colors = list(COLOR_PALETTE.values())
        while self.running:
            # Pulpos locos
            for pid in ["pulpo_01", "pulpo_02"]:
                self.engine.node.set_channel(FIXTURE_DICT[pid].channels["master"], 255)
                self.engine.node.set_channel(FIXTURE_DICT[pid].channels["speed"], 0)
                self.engine.node.set_channel(FIXTURE_DICT[pid].channels["pan"], random.randint(10, 245))
                self.engine.node.set_channel(FIXTURE_DICT[pid].channels["tilt"], random.randint(20, 235))
                self.engine.node.set_channel(FIXTURE_DICT[pid].channels["tilt_inf"], 220)
                c1, c2 = random.choice(colors), random.choice(colors)
                fix = FIXTURE_DICT[pid]
                self.engine.node.set_channel(fix.channels["r1"], c1[0])
                self.engine.node.set_channel(fix.channels["g1"], c1[1])
                self.engine.node.set_channel(fix.channels["b1"], c1[2])
                self.engine.node.set_channel(fix.channels["r2"], c2[0])
                self.engine.node.set_channel(fix.channels["g2"], c2[1])
                self.engine.node.set_channel(fix.channels["b2"], c2[2])

            # Beams y Tachos sincronizados
            for tid in ["tacho_escalera", "tacho_peces", "tacho_central", "tacho_plantas", "beam_01", "beam_02", "bola_disco"]:
                c = random.choice(colors)
                self.engine.set_fixture_rgbw(tid, c[0], c[1], c[2], w=c[3], master=255)

            self.engine.node.send()
            time.sleep(0.12)

    # --------------------------------------------------------------------------
    # COMANDO ESTÁTICO / INTENCIÓN DIRECTA
    # --------------------------------------------------------------------------
    def apply_static_scene(self, color_name: str = "blanco", brightness: int = 255, target: str = "todas"):
        self.stop_current_effect()
        r, g, b, w = parse_color(color_name)
        
        if target == "todas" or target == "all":
            self.engine.scene_all_color(r, g, b, w, brightness=brightness)
        elif target in ["tachos", "par"]:
            for tid in ["tacho_escalera", "tacho_peces", "tacho_central", "tacho_plantas"]:
                self.engine.set_fixture_rgbw(tid, r, g, b, w, master=brightness)
            self.engine.node.send()
        elif target in ["beams", "beam"]:
            for bid in ["beam_01", "beam_02"]:
                self.engine.set_fixture_rgbw(bid, r, g, b, w, master=brightness)
            self.engine.node.send()
        elif target in ["pulpos", "spiders"]:
            for pid in ["pulpo_01", "pulpo_02"]:
                self.engine.set_fixture_rgbw(pid, r, g, b, w, master=brightness)
                self.engine.node.set_channel(FIXTURE_DICT[pid].channels["tilt_inf"], 0)
            self.engine.node.send()
        elif target in FIXTURE_DICT:
            self.engine.set_fixture_rgbw(target, r, g, b, w, master=brightness)
            self.engine.node.send()

    def blackout(self):
        self.stop_current_effect()
        self.engine.scene_blackout()
