"""Bounded, hot-reloadable declarative scene registry for InnerOS DMX.

The registry is intentionally high level. Public/agent-created scenes can choose a
known fixture group, a validated color/brightness, and a bounded duration. They
cannot address raw DMX channels or arbitrary fixture IDs.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

DEFAULT_SCENES_PATH = Path(__file__).with_name("scenes.json")
SCENE_NAME_RE = re.compile(r"^[a-z0-9_]{1,48}$")
HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

ALLOWED_TARGETS = {"all", "todas", "tachos", "beams", "pulpos", "bola_disco"}
ALLOWED_COLORS = {
    "rojo", "verde", "azul", "amarillo", "magenta", "fucsia", "cian", "celeste",
    "turquesa", "naranja", "ambar", "dorado", "violeta", "morado", "purpura", "rosa",
    "rosado", "lima", "blanco", "blanco_calido", "blanco_frio", "neon", "cyberpunk",
    "blackout",
}
MAX_LOOPS = 8
MAX_STEPS = 24
MAX_TOTAL_DURATION_MS = 30_000
MIN_FULL_STAGE_STEP_MS = 500
MIN_GROUP_STEP_MS = 150


def registry_path(path: str | os.PathLike[str] | None = None) -> Path:
    override = path or os.getenv("DMX_SCENES_FILE")
    return Path(override) if override else DEFAULT_SCENES_PATH


def _validate_step(step: Any, index: int) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if not isinstance(step, dict):
        return None, [f"step_{index}:not_object"]

    allowed_keys = {"target", "color", "brightness", "duration_ms"}
    unknown = sorted(set(step) - allowed_keys)
    if unknown:
        errors.append(f"step_{index}:unknown_keys:{','.join(unknown)}")

    target = str(step.get("target", "")).strip().lower()
    if target not in ALLOWED_TARGETS:
        errors.append(f"step_{index}:invalid_target")

    color = str(step.get("color", "")).strip().lower()
    if color not in ALLOWED_COLORS and not HEX_COLOR_RE.fullmatch(color):
        errors.append(f"step_{index}:invalid_color")

    brightness = step.get("brightness")
    if not isinstance(brightness, int) or isinstance(brightness, bool) or not 0 <= brightness <= 255:
        errors.append(f"step_{index}:invalid_brightness")

    duration_ms = step.get("duration_ms")
    minimum = MIN_FULL_STAGE_STEP_MS if target in {"all", "todas"} else MIN_GROUP_STEP_MS
    if not isinstance(duration_ms, int) or isinstance(duration_ms, bool) or duration_ms < minimum:
        errors.append(f"step_{index}:duration_below_{minimum}ms")

    if errors:
        return None, errors
    return {
        "target": target,
        "color": color,
        "brightness": brightness,
        "duration_ms": duration_ms,
    }, []


def validate_scene(name: str, raw: Any) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if not SCENE_NAME_RE.fullmatch(name):
        return None, ["invalid_scene_name"]
    if not isinstance(raw, dict):
        return None, ["scene_not_object"]

    allowed_keys = {"label", "loops", "steps"}
    unknown = sorted(set(raw) - allowed_keys)
    if unknown:
        errors.append(f"unknown_scene_keys:{','.join(unknown)}")

    label = raw.get("label", name.replace("_", " ").title())
    if not isinstance(label, str) or not label.strip() or len(label) > 80:
        errors.append("invalid_label")

    loops = raw.get("loops", 1)
    if not isinstance(loops, int) or isinstance(loops, bool) or not 1 <= loops <= MAX_LOOPS:
        errors.append("invalid_loops")

    raw_steps = raw.get("steps")
    if not isinstance(raw_steps, list) or not 1 <= len(raw_steps) <= MAX_STEPS:
        errors.append("invalid_steps")
        raw_steps = []

    steps: list[dict[str, Any]] = []
    for index, step in enumerate(raw_steps):
        valid, step_errors = _validate_step(step, index)
        errors.extend(step_errors)
        if valid:
            steps.append(valid)

    if isinstance(loops, int) and not isinstance(loops, bool):
        total_ms = loops * sum(step["duration_ms"] for step in steps)
        if total_ms > MAX_TOTAL_DURATION_MS:
            errors.append("scene_duration_exceeds_30000ms")

    if errors:
        return None, errors
    return {"label": label.strip(), "loops": loops, "steps": steps}, []


def load_scene_registry(path: str | os.PathLike[str] | None = None) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    """Load from disk on every call so newly committed scenes are discoverable live."""
    file_path = registry_path(path)
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, []
    except Exception as exc:
        return {}, [{"scene": None, "errors": [f"registry_load_error:{type(exc).__name__}"]}]

    if not isinstance(raw, dict) or set(raw) - {"scenes"}:
        return {}, [{"scene": None, "errors": ["invalid_registry_root"]}]
    raw_scenes = raw.get("scenes", {})
    if not isinstance(raw_scenes, dict):
        return {}, [{"scene": None, "errors": ["scenes_not_object"]}]

    scenes: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, Any]] = []
    for raw_name, definition in raw_scenes.items():
        name = str(raw_name).strip().lower()
        valid, scene_errors = validate_scene(name, definition)
        if valid:
            scenes[name] = valid
        else:
            errors.append({"scene": name, "errors": scene_errors})
    return scenes, errors


def get_scene(name: str, path: str | os.PathLike[str] | None = None) -> dict[str, Any] | None:
    scenes, _ = load_scene_registry(path)
    return scenes.get(str(name).strip().lower())


def list_scene_names(path: str | os.PathLike[str] | None = None) -> list[str]:
    scenes, _ = load_scene_registry(path)
    return sorted(scenes)
