#!/usr/bin/env python3
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.effects_engine import DynamicEffectsRunner

def run():
    print("[InnerOS DMX] Probando Modo Arcoíris / Rainbow Wave durante 6 segundos...")
    runner = DynamicEffectsRunner(target_ip="192.168.1.10", universe=0)
    runner.start_effect("rainbow", speed=1.5)
    time.sleep(6)
    print("[InnerOS DMX] Prueba de arcoíris completada con éxito.")

if __name__ == "__main__":
    run()
