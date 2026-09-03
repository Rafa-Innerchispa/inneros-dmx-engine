"""
Unit tests for InnerOS DMX & Art-Net Engine.
"""

import unittest
from src.artnet_controller import ArtNetNode, InnerOSDMXEngine, ARTNET_HEADER, OP_OUTPUT
from src.fixture_profiles import FIXTURES, FIXTURE_DICT

class TestArtNetEngine(unittest.TestCase):
    def setUp(self):
        self.node = ArtNetNode(target_ip="127.0.0.1", port=6454, universe=0)
        self.engine = InnerOSDMXEngine(target_ip="127.0.0.1", universe=0)

    def test_fixture_integrity(self):
        self.assertEqual(len(FIXTURES), 9)
        self.assertIn("pulpo_01", FIXTURE_DICT)
        self.assertIn("pulpo_02", FIXTURE_DICT)
        self.assertIn("beam_01", FIXTURE_DICT)
        self.assertIn("bola_disco", FIXTURE_DICT)

    def test_packet_structure(self):
        self.node.set_channel(1, 255)
        self.node.set_channel(20, 128)
        packet = self.node.build_packet()
        
        # Verify Header (8 bytes)
        self.assertTrue(packet.startswith(ARTNET_HEADER))
        # Verify length is header (18 bytes) + 512 bytes = 530 bytes
        self.assertEqual(len(packet), 530)
        # Check channel 1 data byte (index 18)
        self.assertEqual(packet[18], 255)
        # Check channel 20 data byte (index 18 + 19 = 37)
        self.assertEqual(packet[37], 128)

    def test_blackout(self):
        self.node.set_channel(1, 255)
        self.node.blackout()
        self.assertEqual(self.node.get_channel(1), 0)
        self.assertEqual(sum(self.node.buffer), 0)

if __name__ == "__main__":
    unittest.main()
