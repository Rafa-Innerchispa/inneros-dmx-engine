#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.artnet_controller import InnerOSDMXEngine

def run():
    print("[InnerOS DMX] Connecting to Pknight CR011R (192.168.1.10:6454)...")
    engine = InnerOSDMXEngine(target_ip="192.168.1.10", universe=0)
    
    # 1. Tachos en Dorado / Ámbar Cálido
    print("[1/3] Setting Tachos to Warm Amber (R:255, G:140, B:0)...")
    for tacho_id in ["tacho_escalera", "tacho_peces", "tacho_central", "tacho_plantas"]:
        engine.set_fixture_rgb(tacho_id, 255, 140, 0, master=255)

    # 2. Beams en Cian Eléctrico
    print("[2/3] Setting Beams to Electric Cyan (R:0, G:255, B:255)...")
    for beam_id in ["beam_01", "beam_02"]:
        engine.set_fixture_rgbw(beam_id, 0, 255, 255, w=0, master=255)

    # 3. Bola Disco en Rojo Fuego
    print("[3/3] Setting Bola Disco to Fire Red (R:255, G:0, B:50)...")
    engine.set_fixture_rgbw("bola_disco", 255, 0, 50, w=0, master=255)

    # 4. Transmisión DMX Art-Net
    engine.node.send()
    print("[SUCCESS] DMX Art-Net Frame transmitted over network to 192.168.1.10!")

if __name__ == "__main__":
    run()
