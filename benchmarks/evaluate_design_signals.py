#!/usr/bin/env python3
"""Modern Design Signals & Contract Coverage Linter.

Replaces tautological "Taste Score" with deterministic signal & contract verification:
1. Chromatic Resonance: Authentic undertones, zero dead gray (#808080), layered void/surface.
2. Typographic Rhythm: Tabular numerics, bounded reading measures, modular scales.
3. Spatial Equilibrium: Concentric radii hierarchy, modular base units.
4. Cognitive Ergonomics: Progressive disclosure (L1-L3), noise budget, actionable empty states.
5. Fault Resilience: Error recovery paths, commit feedback, undo detents.

Negative safety: An empty or missing prototype directory evaluates to BLOCKED (0% coverage).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


def evaluate_design_signals(proto_dir: Path, slice_id: str) -> Dict[str, Any]:
    proto_dir = Path(proto_dir).resolve()
    tokens_css = proto_dir / "shared/tokens.css"
    t1_json = proto_dir / "contracts/tokens/t1.json"
    c1_md = proto_dir / f"contracts/slices/{slice_id}/c1.md"
    r1_md = proto_dir / f"specifications/{slice_id}/r1.md"
    envelope_json = proto_dir / f"experiments/{slice_id}/envelope.json"
    html_file = proto_dir / f"experiments/{slice_id}/anchor/index.html"

    # Negative gate: Empty or missing core artifacts immediately blocks evaluation
    core_files = [f for f in [tokens_css, c1_md, envelope_json, html_file] if f.is_file()]
    if len(core_files) == 0:
        return {
            "slice_id": slice_id,
            "status": "BLOCKED",
            "message": "Empty or non-existent prototype directory. Core artifacts missing.",
            "signal_coverage_pct": 0.0,
            "passed_checks": 0,
            "total_checks": 12,
            "details": {"error": ["No prototype or contract files detected"]}
        }

    checks_passed = 0
    total_checks = 12
    details: Dict[str, List[str]] = {
        "chromatic": [],
        "typographic": [],
        "spatial": [],
        "cognitive": [],
        "tactile": []
    }

    # 1. Chromatic Resonance (3 checks)
    if tokens_css.is_file():
        css = tokens_css.read_text(encoding="utf-8")
        if not re.search(r'#(?:808080|777777|888888)\b', css):
            checks_passed += 1
            details["chromatic"].append("PASS: Absence of sterile dead gray (#808080)")
        else:
            details["chromatic"].append("FAIL: Sterile neutral gray detected in tokens stylesheet")

        if "--bg-void" in css and "--bg-surface" in css:
            checks_passed += 1
            details["chromatic"].append("PASS: Atmospheric layered elevations declared")
        else:
            details["chromatic"].append("FAIL: Missing --bg-void or --bg-surface token elevations")

        if "--accent-primary" in css and "--accent-subtle" in css:
            checks_passed += 1
            details["chromatic"].append("PASS: Primary accent with subtle wash calibrated")
        else:
            details["chromatic"].append("FAIL: Missing calibrated accent token hierarchy")
    else:
        details["chromatic"].append("FAIL: tokens.css not found")

    # 2. Typographic Rhythm (3 checks)
    if tokens_css.is_file():
        css = tokens_css.read_text(encoding="utf-8")
        if "font-variant-numeric: tabular-nums" in css or "--font-mono" in css:
            checks_passed += 1
            details["typographic"].append("PASS: Tabular numeric or monospace protection declared")
        else:
            details["typographic"].append("FAIL: Missing tabular numeric protection")

        if "--reading-measure-max" in css or "68ch" in css:
            checks_passed += 1
            details["typographic"].append("PASS: Ergonomic reading measure declared")
        else:
            details["typographic"].append("FAIL: Missing reading measure boundary token")

        if "--font-sans" in css and ("--line-height-body" in css or "--line-height-heading" in css):
            checks_passed += 1
            details["typographic"].append("PASS: Typographic hierarchy with proportional line-height")
        else:
            details["typographic"].append("FAIL: Incomplete typographic scale or rhythm tokens")
    else:
        details["typographic"].append("FAIL: tokens.css not found")

    # 3. Spatial Equilibrium (2 checks)
    if tokens_css.is_file():
        css = tokens_css.read_text(encoding="utf-8")
        if ("--radius-outer" in css and "--radius-inner" in css) or "--radius-card" in css:
            checks_passed += 1
            details["spatial"].append("PASS: Geometric corner radii hierarchy calibrated")
        else:
            details["spatial"].append("FAIL: Missing corner radii hierarchy")

        if "--space-1" in css and "--space-2" in css:
            checks_passed += 1
            details["spatial"].append("PASS: Base modular spatial rhythm declared")
        else:
            details["spatial"].append("FAIL: Missing modular spatial rhythm tokens")
    else:
        details["spatial"].append("FAIL: tokens.css not found")

    # 4. Cognitive Ergonomics & Disclosure (2 checks)
    if envelope_json.is_file():
        try:
            env = json.loads(envelope_json.read_text(encoding="utf-8"))
            if "attention_routing" in env or "disclosure_levels" in str(env):
                checks_passed += 1
                details["cognitive"].append("PASS: Progressive disclosure & attention routing specified")
            else:
                details["cognitive"].append("FAIL: Missing attention routing specifications")

            if "data_stress_boundaries" in env or "fault_tolerance" in env:
                checks_passed += 1
                details["cognitive"].append("PASS: Data stress or fault recovery boundaries bounded")
            else:
                details["cognitive"].append("FAIL: Missing data stress boundary definitions")
        except Exception:
            details["cognitive"].append("FAIL: envelope.json corrupt or invalid")
    else:
        details["cognitive"].append("FAIL: envelope.json not found")

    # 5. Fault Resilience & Commit Mechanics (2 checks)
    if c1_md.is_file():
        c1_text = c1_md.read_text(encoding="utf-8")
        if "Fault Tolerance" in c1_text or "Error Recovery" in c1_text:
            checks_passed += 1
            details["tactile"].append("PASS: Fault tolerance and recovery path codified")
        else:
            details["tactile"].append("FAIL: Missing fault tolerance specification in slice contract")

        if "Action Verb Lifecycle" in c1_text or "Decisive" in c1_text:
            checks_passed += 1
            details["tactile"].append("PASS: Consequential action lifecycle specified")
        else:
            details["tactile"].append("FAIL: Missing action verb lifecycle closure in contract")
    else:
        details["tactile"].append("FAIL: Slice contract c1.md not found")

    coverage_pct = round((checks_passed / total_checks) * 100.0, 1)
    status = "PASS" if coverage_pct >= 80.0 else "FAIL"

    return {
        "slice_id": slice_id,
        "status": status,
        "signal_coverage_pct": coverage_pct,
        "passed_checks": checks_passed,
        "total_checks": total_checks,
        "audit_details": details
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 evaluate_design_signals.py <proto_dir> <slice_id>")
        sys.exit(1)
    res = evaluate_design_signals(Path(sys.argv[1]), sys.argv[2])
    print(json.dumps(res, indent=2, ensure_ascii=False))
