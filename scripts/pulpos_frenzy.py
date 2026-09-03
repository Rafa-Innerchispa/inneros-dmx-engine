#!/usr/bin/env python3
"""
InnerOS DMX - Pulpos Multicolor & Fast Random Pan/Tilt Generator.
"""
import sys
import os
import time
import random
import signal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.artnet_controller import InnerOSDMXEngine

# Colores vivos RGBW
COLORS = [
    (255, 0, 0, 0),     # Rojo
    (0, 255, 0, 0),     # Verde
    (0, 0, 255, 0),     # Azul
    (255, 255, 0, 0),   # Amarillo
    (255, 0, 255, 0),   # Magenta
    (0, 255, 255, 0),   # Cian
    (255, 100, 0, 0),   # Naranja
    (128, 0, 255, 0),   # Púrpura
    (0, 255, 128, 0),   # Verde Lima
    (255, 0, 100, 100), # Rosa Brillante
    (0, 0, 0, 255),     # Blanco Puro
    (255, 255, 255, 100)# Full Blast
]

running = True
def sig_handler(signum, frame):
    global running
    running = False

signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

def run():
    print("[InnerOS DMX] Iniciando modo FRENZY Multicolor y Giro Rápido para Pulpos...")
    engine = InnerOSDMXEngine(target_ip="192.168.1.10", universe=0)

    # Master dimmer al 100% y velocidad máxima de motores (0 = fastest)
    engine.node.set_channel(7, 255)   # Pulpo 1 Master Dimmer
    engine.node.set_channel(6, 0)     # Pulpo 1 Max Speed
    engine.node.set_channel(8, 0)     # Pulpo 1 Strobe Open

    engine.node.set_channel(75, 255)  # Pulpo 2 Master Dimmer
    engine.node.set_channel(74, 0)    # Pulpo 2 Max Speed
    engine.node.set_channel(76, 0)    # Pulpo 2 Strobe Open

    # Activar rotación infinita rápida de Tilt (CH 5 y 73 en valor alto 200+)
    engine.node.set_channel(5, 220)   # Pulpo 1 Tilt Fast Continuous Rotation
    engine.node.set_channel(73, 220)  # Pulpo 2 Tilt Fast Continuous Rotation

    try:
        step = 0
        while running:
            # 1. Movimiento aleatorio rápido de Pan y Tilt
            p1_pan = random.randint(10, 245)
            p1_tilt = random.randint(20, 235)
            p2_pan = random.randint(10, 245)
            p2_tilt = random.randint(20, 235)

            engine.node.set_channel(1, p1_pan)
            engine.node.set_channel(3, p1_tilt)
            engine.node.set_channel(69, p2_pan)
            engine.node.set_channel(71, p2_tilt)

            # 2. Selección de colores aleatorios e independientes por cada barra LED
            c1 = random.choice(COLORS)
            c2 = random.choice(COLORS)
            c3 = random.choice(COLORS)
            c4 = random.choice(COLORS)

            # Pulpo 1 Barra 1 (CH 9-12)
            engine.node.set_channel(9, c1[0])
            engine.node.set_channel(10, c1[1])
            engine.node.set_channel(11, c1[2])
            engine.node.set_channel(12, c1[3])

            # Pulpo 1 Barra 2 (CH 13-16)
            engine.node.set_channel(13, c2[0])
            engine.node.set_channel(14, c2[1])
            engine.node.set_channel(15, c2[2])
            engine.node.set_channel(16, c2[3])

            # Pulpo 2 Barra 1 (CH 77-80)
            engine.node.set_channel(77, c3[0])
            engine.node.set_channel(78, c3[1])
            engine.node.set_channel(79, c3[2])
            engine.node.set_channel(80, c3[3])

            # Pulpo 2 Barra 2 (CH 81-84)
            engine.node.set_channel(81, c4[0])
            engine.node.set_channel(82, c4[1])
            engine.node.set_channel(83, c4[2])
            engine.node.set_channel(84, c4[3])

            # Enviar trama DMX
            engine.node.send()

            step += 1
            # Cambio rápido a 8-10 Hz (cada 120ms)
            time.sleep(0.12)

    except KeyboardInterrupt:
        pass
    finally:
        print("[InnerOS DMX] Deteniendo modo frenzy...")

if __name__ == "__main__":
    run()
