"""Benchmark-owned mapping from benchmark findings to craft-floor rules."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = ROOT / "skills" / "spec-prototype" / "scripts"
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))

import detect  # noqa: E402

BENCHMARK_ANCHORS = {
    "SLOP-001": "CRAFT-NO-GRADIENT-TEXT",
    "SLOP-009": "CRAFT-NO-EMOJI-ICON",
    "SLOP-017": "CRAFT-SELECTION",
    "SLOP-018": "CRAFT-PRESS-DETENT",
    "SLOP-019": "CRAFT-TABULAR-NUMS",
    "SLOP-026": "CRAFT-KINETIC-SPRING",
}


def validate_crosswalk() -> list[str]:
    """Return mapping errors without coupling benchmark ids to delivery code."""
    errors = [f"{slop_id} maps to missing craft rule {rule_id}"
              for slop_id, rule_id in BENCHMARK_ANCHORS.items()
              if rule_id not in detect.RULES]
    source = (Path(__file__).with_name("slop_detector.py").read_text(encoding="utf-8"))
    emitted = set(re.findall(r"SLOP-\d{3}", source))
    errors.extend(f"crosswalk references absent benchmark rule {rule_id}"
                  for rule_id in BENCHMARK_ANCHORS if rule_id not in emitted)
    return errors
