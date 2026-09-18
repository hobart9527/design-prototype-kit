#!/usr/bin/env python3
"""Compatibility wrapper: redirects evaluate_design_taste to evaluate_design_signals."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

from evaluate_design_signals import evaluate_design_signals


def evaluate_design_taste(proto_dir: Path, slice_id: str) -> Dict[str, Any]:
    # Delegate directly to objective signal coverage Linter
    signals = evaluate_design_signals(proto_dir, slice_id)
    return {
        "slice_id": slice_id,
        "status": signals["status"],
        "signal_coverage_pct": signals["signal_coverage_pct"],
        "overall_taste_score": signals["signal_coverage_pct"],  # compatibility field
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
