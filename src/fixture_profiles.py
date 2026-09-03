"""
InnerOS DMX & Art-Net Engine - Fixture Profiles and Channel Definitions.
Mapped for Pknight CR011R Node (192.168.1.10) - Universe 0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class ChannelMap:
    name: str
    offset: int # 0-indexed relative to fixture base channel
    default_val: int = 0
    description: str = ""

@dataclass
class Fixture:
    id: str
    name: str
    base_channel: int # 1-indexed (1-512)
    num_channels: int
    category: str # "moving_head", "beam", "par_rgb", "par_rgbw", "effect"
    channels: Dict[str, int] = field(default_factory=dict)
    description: str = ""

# Hardware fixtures inventory on Universe 0
FIXTURES: List[Fixture] = [
    # 1. Pulpo 1 (Eurolite EL-LMH1240WB, 19ch | Base: 1)
    Fixture(
        id="pulpo_01",
        name="Pulpo 1 (Eurolite EL-LMH1240WB)",
        base_channel=1,
        num_channels=19,
        category="moving_head",
        channels={
            "pan": 1, "pan_fine": 2, "tilt": 3, "tilt_fine": 4,
            "tilt_inf": 5, "speed": 6, "master": 7, "strobe": 8,
            "r1": 9, "g1": 10, "b1": 11, "w1": 12,
            "r2": 13, "g2": 14, "b2": 15, "w2": 16,
            "effect": 17, "effect_speed": 18, "reset": 19
        },
        description="Moving head spider bar with 2 tiltable bars, 8x RGBW LEDs, continuous rotation"
    ),

    # 2. Beam 01 (Mini Beam RGBW 12W 4-in-1, 6ch | Base: 20)
    Fixture(
        id="beam_01",
        name="Mini Beam 01 RGBW",
        base_channel=20,
        num_channels=6,
        category="beam",
        channels={
            "master": 20, "strobe": 21, "red": 22, "green": 23, "blue": 24, "white": 25
        },
        description="Concentrated pinspot beam 12W 4-in-1 RGBW"
    ),

    # 3. Tacho Escalera (LED PAR 18x1W RGB, 7ch Modo d | Base: 26)
    Fixture(
        id="tacho_escalera",
        name="Tacho Escalera (LED PAR 18x1W RGB)",
        base_channel=26,
        num_channels=7,
        category="par_rgb",
        channels={
            "master": 26, "red": 27, "green": 28, "blue": 29,
            "strobe": 30, "macro": 31, "speed": 32
        },
        description="Par LED 18x1W illumination for stairs area"
    ),

    # 4. Tacho Peces (LED PAR 18x1W RGB, 7ch Modo d | Base: 33)
    Fixture(
        id="tacho_peces",
        name="Tacho Peces (LED PAR 18x1W RGB)",
        base_channel=33,
        num_channels=7,
        category="par_rgb",
        channels={
            "master": 33, "red": 34, "green": 35, "blue": 36,
            "strobe": 37, "macro": 38, "speed": 39
        },
        description="Par LED 18x1W illumination for aquarium/peces area"
    ),

    # 5. Tacho Central (Mini PAR 3x4W RGBW + Flash SMD, 8ch Modo A | Base: 40)
    Fixture(
        id="tacho_central",
        name="Tacho Central (Mini PAR RGBW + Flash SMD)",
        base_channel=40,
        num_channels=8,
        category="par_rgbw",
        channels={
            "master": 40, "red": 41, "green": 42, "blue": 43, "white": 44,
            "strobe_mode": 45, "strobe_speed": 46, "auto_mode": 47
        },
        description="Center ambient PAR RGBW with integrated SMD flash ring"
    ),

    # 6. Tacho Plantas (LED PAR 18x1W RGB, 7ch Modo d | Base: 48)
    Fixture(
        id="tacho_plantas",
        name="Tacho Plantas (LED PAR 18x1W RGB)",
        base_channel=48,
        num_channels=7,
        category="par_rgb",
        channels={
            "master": 48, "red": 49, "green": 50, "blue": 51,
            "strobe": 52, "macro": 53, "speed": 54
        },
        description="Par LED 18x1W illumination for plants area"
    ),

    # 7. Bola Disco (Crystal LED Magic Ball, 8ch Modo A | Base: 55)
    Fixture(
        id="bola_disco",
        name="Bola Disco Magic Ball",
        base_channel=55,
        num_channels=8,
        category="effect",
        channels={
            "master": 55, "red": 56, "green": 57, "blue": 58, "white": 59,
            "motor": 60, "strobe": 61, "macro": 62
        },
        description="Multi-beam crystal disco ball with motorized rotation"
    ),

    # 8. Beam 02 (Mini Beam RGBW 12W 4-in-1, 6ch | Base: 63)
    Fixture(
        id="beam_02",
        name="Mini Beam 02 RGBW",
        base_channel=63,
        num_channels=6,
        category="beam",
        channels={
            "master": 63, "strobe": 64, "red": 65, "green": 66, "blue": 67, "white": 68
        },
        description="Concentrated pinspot beam 12W 4-in-1 RGBW (Unit 2)"
    ),

    # 9. Pulpo 2 (Eurolite EL-LMH1240WB, 19ch | Base: 69)
    Fixture(
        id="pulpo_02",
        name="Pulpo 2 (Eurolite EL-LMH1240WB)",
        base_channel=69,
        num_channels=19,
        category="moving_head",
        channels={
            "pan": 69, "pan_fine": 70, "tilt": 71, "tilt_fine": 72,
            "tilt_inf": 73, "speed": 74, "master": 75, "strobe": 76,
            "r1": 77, "g1": 78, "b1": 79, "w1": 80,
            "r2": 81, "g2": 82, "b2": 83, "w2": 84,
            "effect": 85, "effect_speed": 86, "reset": 87
        },
        description="Moving head spider bar with 2 tiltable bars, 8x RGBW LEDs (Unit 2)"
    )
]

FIXTURE_DICT: Dict[str, Fixture] = {f.id: f for f in FIXTURES}
