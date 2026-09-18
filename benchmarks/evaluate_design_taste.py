#!/usr/bin/env python3
"""Compatibility wrapper: redirects evaluate_design_taste to evaluate_design_signals.

DEPRECATION NOTICE (v10.1):
The concept of a synthetic 'Taste Score' has been formally deprecated.
Design quality is evaluated qualitatively via independent Critic and Empirical Task Traces,
while static automated checks measure objective 'signal_coverage_pct' (Linter Coverage).
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path
from typing import Any, Dict

from evaluate_design_signals import evaluate_design_signals


def evaluate_design_taste(proto_dir: Path, slice_id: str) -> Dict[str, Any]:
    warnings.warn(
        "evaluate_design_taste is deprecated since v10.1. Use evaluate_design_signals for objective signal coverage.",
        DeprecationWarning,
        stacklevel=2,
    )
    # Delegate directly to objective signal coverage Linter
    signals = evaluate_design_signals(proto_dir, slice_id)
    return {
        "slice_id": slice_id,
        "status": signals["status"],
        "signal_coverage_pct": signals["signal_coverage_pct"],
        "deprecation_notice": "Taste Score deprecated in v10.1; refer to signal_coverage_pct and Critic reviews.",
        "dimensions": {
            "chromatic_resonance": 100.0 if any("PASS" in s for s in signals["audit_details"].get("chromatic", [])) else 0.0,
            "typographic_rhythm": 100.0 if any("PASS" in s for s in signals["audit_details"].get("typographic", [])) else 0.0,
            "spatial_equilibrium": 100.0 if any("PASS" in s for s in signals["audit_details"].get("spatial", [])) else 0.0,
            "cognitive_ergonomics": 100.0 if any("PASS" in s for s in signals["audit_details"].get("cognitive", [])) else 0.0,
            "tactile_physics": 100.0 if any("PASS" in s for s in signals["audit_details"].get("tactile", [])) else 0.0,
        },
        "aesthetic_audit_details": signals["audit_details"]
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 evaluate_design_taste.py <proto_dir> <slice_id>")
        sys.exit(1)
    res = evaluate_design_taste(Path(sys.argv[1]), sys.argv[2])
    print(json.dumps(res, indent=2, ensure_ascii=False))
