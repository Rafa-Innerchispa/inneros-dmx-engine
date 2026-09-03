#!/usr/bin/env python3
"""
InnerOS DMX - Escena Morado Profundo UV / Blacklight para todas las luces.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.artnet_controller import InnerOSDMXEngine
from src.fixture_profiles import FIXTURE_DICT

def set_uv_purple():
    print("[InnerOS DMX] Configurando escena Morado UV / Blacklight en todas las luces...")
    engine = InnerOSDMXEngine(target_ip="192.168.1.10", universe=0)

    # Color Morado UV Profundo (R:45, G:0, B:255, W:0)
    R_UV = 45
    G_UV = 0
    B_UV = 255
    W_UV = 0

    # 1. TACHOS (Escalera, Peces, Central, Plantas)
    for tid in ["tacho_escalera", "tacho_peces", "tacho_central", "tacho_plantas"]:
        engine.set_fixture_rgbw(tid, R_UV, G_UV, B_UV, w=W_UV, master=255)

    # 2. BEAMS 01 y 02
    for bid in ["beam_01", "beam_02"]:
        engine.set_fixture_rgbw(bid, R_UV, G_UV, B_UV, w=W_UV, master=255)
        # Estrobo cerrado/continuo
        engine.node.set_channel(FIXTURE_DICT[bid].channels["strobe"], 0)

    # 3. BOLA DISCO
    engine.set_fixture_rgbw("bola_disco", R_UV, G_UV, B_UV, w=W_UV, master=255)
    engine.node.set_channel(FIXTURE_DICT["bola_disco"].channels["motor"], 30) # Rotación lenta sutil

    # 4. PULPOS 1 y 2
    for pid in ["pulpo_01", "pulpo_02"]:
        fix = FIXTURE_DICT[pid]
        engine.node.set_channel(fix.channels["master"], 255)
        engine.node.set_channel(fix.channels["strobe"], 0)
        engine.node.set_channel(fix.channels["pan"], 128)      # Centrado
        engine.node.set_channel(fix.channels["tilt"], 135)     # Ángulo cenital
        engine.node.set_channel(fix.channels["tilt_inf"], 0)   # Detener rotación continua
        engine.node.set_channel(fix.channels["speed"], 20)     # Suave

        # Barra 1 en UV
        engine.node.set_channel(fix.channels["r1"], R_UV)
        engine.node.set_channel(fix.channels["g1"], G_UV)
        engine.node.set_channel(fix.channels["b1"], B_UV)
        engine.node.set_channel(fix.channels["w1"], W_UV)

        # Barra 2 en UV
        engine.node.set_channel(fix.channels["r2"], R_UV)
        engine.node.set_channel(fix.channels["g2"], G_UV)
        engine.node.set_channel(fix.channels["b2"], B_UV)
        engine.node.set_channel(fix.channels["w2"], W_UV)

    # Enviar trama DMX Art-Net (enviamos 3 veces seguidas para asegurar latch)
    for _ in range(3):
        engine.node.send()

    print("[SUCCESS] Todas las luces DMX, Tachos, Beams, Bola y Pulpos fijados en Morado UV Fluorescente!")

if __name__ == "__main__":
    set_uv_purple()
