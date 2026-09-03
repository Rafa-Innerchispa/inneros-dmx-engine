"""
InnerOS DMX & Art-Net Core Controller.
Transmits standard Art-Net (ArtDmx) UDP packets to Pknight CR011R / standard nodes.
"""

import socket
import struct
import time
import math
from typing import Dict, List, Optional, Tuple
from .fixture_profiles import FIXTURES, FIXTURE_DICT, Fixture

ARTNET_PORT = 6454
ARTNET_HEADER = b"Art-Net\x00"
OP_OUTPUT = 0x5000  # OpOutput / OpDmx (Little-endian in packet: 0x00, 0x50)
PROTOCOL_VERSION = 14

class ArtNetNode:
    """Manages raw Art-Net frame generation and socket delivery."""

    def __init__(self, target_ip: str = "192.168.1.10", port: int = ARTNET_PORT, universe: int = 0):
        self.target_ip = target_ip
        self.port = port
        self.universe = universe
        self.sequence = 0
        self.buffer = bytearray(512)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def set_channel(self, channel: int, value: int):
        """Set DMX channel (1-indexed, 1-512) to value (0-255)."""
        if 1 <= channel <= 512:
            self.buffer[channel - 1] = max(0, min(255, int(value)))

    def get_channel(self, channel: int) -> int:
        if 1 <= channel <= 512:
            return self.buffer[channel - 1]
        return 0

    def blackout(self):
        """Set all 512 channels to 0."""
        self.buffer = bytearray(512)
        self.send()

    def build_packet(self) -> bytes:
        """Constructs an RFC-compliant ArtDmx packet."""
        self.sequence = (self.sequence + 1) % 256
        if self.sequence == 0:
            self.sequence = 1

        # Header: 'Art-Net\0' (8 bytes)
        # OpCode: 0x5000 (OpDmx, little-endian: 0x00, 0x50)
        # ProtVer: 14 (big-endian: 0x00, 0x0E)
        # Sequence: 1 byte
        # Physical: 0 (1 byte)
        # SubUni (Universe lower 8 bits): 1 byte
        # Net (Universe upper 7 bits): 1 byte
        # Length: 512 (big-endian: 0x02, 0x00)
        # Data: 512 bytes

        sub_uni = self.universe & 0xFF
        net = (self.universe >> 8) & 0x7F
        length = len(self.buffer)

        packet = struct.pack(
            "<8sHHBBBBH",
            ARTNET_HEADER,
            OP_OUTPUT,
            PROTOCOL_VERSION,  # Big endian in network protocol
            self.sequence,
            0,                 # Physical port
            sub_uni,
            net,
            struct.unpack(">H", struct.pack("<H", length))[0] # Convert to big-endian length
        ) + bytes(self.buffer)

        # Standard header format:
        # 8 bytes ID + 2 bytes OpCode (0x5000) + 2 bytes Version (0x000e) + 1 byte Seq + 1 byte Phys + 2 bytes Universe + 2 bytes Length (big-endian 512)
        full_packet = (
            ARTNET_HEADER +
            struct.pack("<H", OP_OUTPUT) +
            struct.pack(">H", PROTOCOL_VERSION) +
            struct.pack("BB", self.sequence, 0) +
            struct.pack("<H", self.universe) +
            struct.pack(">H", 512) +
            bytes(self.buffer)
        )
        return full_packet

    def send(self):
        """Sends the current DMX buffer via UDP."""
        packet = self.build_packet()
        try:
            self.sock.sendto(packet, (self.target_ip, self.port))
        except Exception as e:
            print(f"[ArtNet Error] Failed to send packet to {self.target_ip}: {e}")

    def close(self):
        self.sock.close()


class InnerOSDMXEngine:
    """High-level lighting & stage automation engine."""

    def __init__(self, target_ip: str = "192.168.1.10", universe: int = 0):
        self.node = ArtNetNode(target_ip=target_ip, universe=universe)
        self.fixtures = FIXTURE_DICT

    def set_fixture_rgb(self, fixture_id: str, r: int, g: int, b: int, master: int = 255):
        fix = self.fixtures.get(fixture_id)
        if not fix:
            return

        if "master" in fix.channels:
            self.node.set_channel(fix.channels["master"], master)

        if "red" in fix.channels:
            self.node.set_channel(fix.channels["red"], r)
            self.node.set_channel(fix.channels["green"], g)
            self.node.set_channel(fix.channels["blue"], b)

        # Multi-segment spiders / pulpos
        if "r1" in fix.channels:
            self.node.set_channel(fix.channels["r1"], r)
            self.node.set_channel(fix.channels["g1"], g)
            self.node.set_channel(fix.channels["b1"], b)
            self.node.set_channel(fix.channels["r2"], r)
            self.node.set_channel(fix.channels["g2"], g)
            self.node.set_channel(fix.channels["b2"], b)

    def set_fixture_rgbw(self, fixture_id: str, r: int, g: int, b: int, w: int = 0, master: int = 255):
        self.set_fixture_rgb(fixture_id, r, g, b, master)
        fix = self.fixtures.get(fixture_id)
        if not fix:
            return
        if "white" in fix.channels:
            self.node.set_channel(fix.channels["white"], w)
        if "w1" in fix.channels:
            self.node.set_channel(fix.channels["w1"], w)
            self.node.set_channel(fix.channels["w2"], w)

    def set_pulpo_position(self, pulpo_id: str, pan: int, tilt: int, speed: int = 0):
        fix = self.fixtures.get(pulpo_id)
        if not fix or fix.category != "moving_head":
            return
        self.node.set_channel(fix.channels["pan"], pan)
        self.node.set_channel(fix.channels["tilt"], tilt)
        self.node.set_channel(fix.channels["speed"], speed)

    def scene_all_color(self, r: int, g: int, b: int, w: int = 0, brightness: int = 255):
        """Sets every fixture to the specified color with given brightness."""
        for fix_id in self.fixtures:
            self.set_fixture_rgbw(fix_id, r, g, b, w, master=brightness)
        self.node.send()

    def scene_disco_party(self):
        """Dynamic vibrant party scene: beams pink, tachos cyan, pulpos moving & amber."""
        # Tachos: Cyan
        for tacho_id in ["tacho_escalera", "tacho_peces", "tacho_central", "tacho_plantas"]:
            self.set_fixture_rgb(tacho_id, 0, 220, 255, master=255)

        # Beams: Hot Magenta
        for beam_id in ["beam_01", "beam_02"]:
            self.set_fixture_rgbw(beam_id, 255, 0, 160, w=0, master=255)

        # Bola disco: Amber + Motor rotation
        self.set_fixture_rgbw("bola_disco", 255, 120, 0, w=50, master=255)
        self.node.set_channel(FIXTURE_DICT["bola_disco"].channels["motor"], 180)

        # Pulpos: Violet & Moving
        for pulpo_id in ["pulpo_01", "pulpo_02"]:
            self.set_pulpo_position(pulpo_id, pan=128, tilt=140, speed=10)
            self.set_fixture_rgbw(pulpo_id, 200, 0, 255, w=0, master=255)

        self.node.send()

    def scene_blackout(self):
        self.node.blackout()
