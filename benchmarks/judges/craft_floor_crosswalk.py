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

# SLOP ids with no craft-floor counterpart. Every emitted SLOP id must appear in
# BENCHMARK_ANCHORS or here — "not mapped" is a recorded status with a reason,
# not an omission, mirroring detect.py's prose_only `why` mechanism.
BENCHMARK_UNMAPPED = {
    "SLOP-002": "side stripes are a taste call; detect.py checks :active detent, not stripe widths",
    "SLOP-003": "ghost cards are declared-elevation judgement, prose-only on the craft floor",
    "SLOP-004": "nested cards are CRAFT-CARD-GRID-EARNED territory, which is prose_only by design",
    "SLOP-006": "transition: all is a hygiene rule with no craft-floor prose counterpart",
    "SLOP-007": "neutral tinting is palette judgement the craft floor owns by hand",
    "SLOP-008": "palette direction is a use-scene decision (CRAFT-THEME-ORIGIN), not detectable",
    "SLOP-010": "shadow-vs-border is declared-elevation judgement, prose-only",
    "SLOP-011": "uniform radii are a design decision; only concentric geometry is mechanised",
    "SLOP-012": "pill-on-container needs control-vs-container reading, prose_only",
    "SLOP-013": "texture needs canvas context; CRAFT-NO-EYEBROW-style content reading",
    "SLOP-014": "section ordinals are refused in craft-floor prose without a CRAFT id",
    "SLOP-021": "blur-as-decoration is a justification call, not a pattern",
    "SLOP-023": "font-stack taste lives in style vocabulary prose, not the floor",
    "SLOP-024": "inline hex is token-binding hygiene, enforced by verify_prototype_quality",
    "SLOP-025": "modal necessity is a task-level judgement, prose-only",
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
    # Coverage is total: every emitted id is either mapped or explicitly exempted.
    accounted = set(BENCHMARK_ANCHORS) | set(BENCHMARK_UNMAPPED)
    errors.extend(
        f"unaccounted benchmark rule {rule_id}: add it to BENCHMARK_ANCHORS "
        "or BENCHMARK_UNMAPPED with a reason"
        for rule_id in emitted - accounted
    )
    errors.extend(
        f"crosswalk lists {rule_id} but slop_detector never emits it"
        for rule_id in accounted - emitted
    )
    return errors
