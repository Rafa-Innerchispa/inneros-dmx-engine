#!/usr/bin/env python3
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.artnet_controller import InnerOSDMXEngine

def activate_pulpos():
    print("[InnerOS DMX] Activating Pulpos (Eurolite EL-LMH1240WB)...")
    engine = InnerOSDMXEngine(target_ip="192.168.1.10", universe=0)

    # Pulpo 1 (CH 1-19)
    # CH1: Pan=128 (centro), CH3: Tilt=135, CH6: Speed=10, CH7: Master Dimmer=255, CH8: Strobe=0
    engine.node.set_channel(1, 128)  # Pan
    engine.node.set_channel(2, 0)    # Pan fine
    engine.node.set_channel(3, 135)  # Tilt
    engine.node.set_channel(4, 0)    # Tilt fine
    engine.node.set_channel(5, 0)    # Tilt infinite rot
    engine.node.set_channel(6, 10)   # Motor speed
    engine.node.set_channel(7, 255)  # Master Dimmer
    engine.node.set_channel(8, 0)    # Strobe open

    # Barra 1: Magenta (R:255, G:0, B:200, W:0)
    engine.node.set_channel(9, 255)
    engine.node.set_channel(10, 0)
    engine.node.set_channel(11, 200)
    engine.node.set_channel(12, 0)

    # Barra 2: Cyan Brillante (R:0, G:255, B:255, W:100)
    engine.node.set_channel(13, 0)
    engine.node.set_channel(14, 255)
    engine.node.set_channel(15, 255)
    engine.node.set_channel(16, 100)

    # Pulpo 2 (CH 69-87)
    engine.node.set_channel(69, 128) # Pan
    engine.node.set_channel(70, 0)   # Pan fine
    engine.node.set_channel(71, 135) # Tilt
    engine.node.set_channel(72, 0)   # Tilt fine
    engine.node.set_channel(73, 0)   # Tilt infinite rot
    engine.node.set_channel(74, 10)  # Motor speed
    engine.node.set_channel(75, 255) # Master Dimmer
    engine.node.set_channel(76, 0)   # Strobe open

    # Barra 1: Cyan Brillante
    engine.node.set_channel(77, 0)
    engine.node.set_channel(78, 255)
    engine.node.set_channel(79, 255)
    engine.node.set_channel(80, 100)

    # Barra 2: Magenta
    engine.node.set_channel(81, 255)
    engine.node.set_channel(82, 0)
    engine.node.set_channel(83, 200)
    engine.node.set_channel(84, 0)

    # Enviar trama
    engine.node.send()
    print("[SUCCESS] Pulpo 1 y Pulpo 2 activados: Motores posicionados, Master Dimmer al 100%, Barras LED en Magenta y Cian.")

if __name__ == "__main__":
    activate_pulpos()
