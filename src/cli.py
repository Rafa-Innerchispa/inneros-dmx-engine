"""
InnerOS DMX & Art-Net Engine CLI.
Provides command line diagnostics, live fixture control, and scene firing.
"""

import sys
import argparse
import time
from .artnet_controller import InnerOSDMXEngine
from .fixture_profiles import FIXTURES, FIXTURE_DICT

def main():
    parser = argparse.ArgumentParser(description="InnerOS DMX & Art-Net Controller")
    parser.add_argument("--ip", default="192.168.1.10", help="Target Art-Net node IP")
    parser.add_argument("--universe", type=int, default=0, help="DMX universe (default 0)")
    
    subparsers = parser.add_subparsers(dest="command")

    # Command: list
    subparsers.add_parser("list", help="List all registered DMX fixtures")

    # Command: blackout
    subparsers.add_parser("blackout", help="Blackout all fixtures")

    # Command: party
    subparsers.add_parser("party", help="Run vibrant disco party scene")

    # Command: color
    color_parser = subparsers.add_parser("color", help="Set uniform color across fixtures")
    color_parser.add_argument("--r", type=int, required=True, help="Red 0-255")
    color_parser.add_argument("--g", type=int, required=True, help="Green 0-255")
    color_parser.add_argument("--b", type=int, required=True, help="Blue 0-255")
    color_parser.add_argument("--w", type=int, default=0, help="White 0-255")
    color_parser.add_argument("--brightness", type=int, default=255, help="Brightness 0-255")

    # Command: test-fixture
    test_parser = subparsers.add_parser("test", help="Test specific fixture")
    test_parser.add_argument("fixture_id", choices=list(FIXTURE_DICT.keys()))

    args = parser.parse_args()

    if not args.command or args.command == "list":
        print("=== InnerOS DMX Fixtures on Universe 0 ===")
        for f in FIXTURES:
            print(f"[{f.id:15s}] Base: CH {f.base_channel:2d} | CHs: {f.num_channels:2d} | {f.name}")
        return

    engine = InnerOSDMXEngine(target_ip=args.ip, universe=args.universe)

    if args.command == "blackout":
        print("Executing Blackout...")
        engine.scene_blackout()
        print("Done.")

    elif args.command == "party":
        print("Triggering Disco Party Scene...")
        engine.scene_disco_party()
        print("Done.")

    elif args.command == "color":
        print(f"Setting color R:{args.r} G:{args.g} B:{args.b} W:{args.w}...")
        engine.scene_all_color(args.r, args.g, args.b, args.w, args.brightness)
        print("Done.")

    elif args.command == "test":
        fix = FIXTURE_DICT[args.fixture_id]
        print(f"Testing fixture: {fix.name} at CH {fix.base_channel}...")
        engine.set_fixture_rgbw(fix.id, 255, 0, 0, w=0, master=255)
        engine.node.send()
        time.sleep(1)
        engine.set_fixture_rgbw(fix.id, 0, 255, 0, w=0, master=255)
        engine.node.send()
        time.sleep(1)
        engine.set_fixture_rgbw(fix.id, 0, 0, 255, w=0, master=255)
        engine.node.send()
        time.sleep(1)
        engine.set_fixture_rgbw(fix.id, 0, 0, 0, w=0, master=0)
        engine.node.send()
        print(f"Test completed for {fix.name}.")

if __name__ == "__main__":
    main()
