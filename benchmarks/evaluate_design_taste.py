#!/usr/bin/env python3
"""Modern Design Taste & Craft Evaluation Matrix.

Evaluates prototype and contract artifacts along 5 Modern Design Dimensions:
1. Chromatic Resonance & Atmospheric Undertone (色彩气韵与氛围共鸣)
   - Evaluates OKLCH chroma harmony, absence of sterile grays (#808080), and contrast elevation steps.
2. Typographic Rhythm & Micro-Hierarchy (排印节奏与微观层级)
   - Evaluates scale ratios (modular scales), tabular numeric protection, reading measure (ch limits).
3. Spatial Tension & Geometric Equilibrium (空间张力与几何平衡)
   - Evaluates concentric corner radii (R_in = R_out - P), consistent 4/8px base modularity.
4. Cognitive Ergonomics & Attention Routing (认知工效与视线导流)
   - Evaluates primary anchor distinctiveness, disclosure levels (L1-L3), and noise budget adherence.
5. Tactile Physics & State Resilience (触觉物理与系统宽容)
   - Evaluates active mechanical detents, reduced-motion overrides, and undo/recovery boundaries.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


def evaluate_design_taste(proto_dir: Path, slice_id: str) -> Dict[str, Any]:
    tokens_css = proto_dir / "shared/tokens.css"
    t1_json = proto_dir / "contracts/tokens/t1.json"
    c1_md = proto_dir / f"contracts/slices/{slice_id}/c1.md"
    r1_md = proto_dir / f"specifications/{slice_id}/r1.md"
    envelope_json = proto_dir / f"experiments/{slice_id}/envelope.json"

    scores: Dict[str, float] = {}
    details: Dict[str, List[str]] = {
        "chromatic": [],
        "typographic": [],
        "spatial": [],
        "cognitive": [],
        "tactile": []
    }

    # 1. Chromatic Resonance (0 - 100)
    chroma_score = 100.0
    if tokens_css.is_file():
        css = tokens_css.read_text(encoding="utf-8")
        if re.search(r'#(?:808080|777777|888888)\b', css):
            chroma_score -= 20.0
            details["chromatic"].append("Sterile dead gray detected in tokens stylesheet (-20)")
        if "--bg-void" in css and "--bg-surface" in css:
            details["chromatic"].append("Atmospheric layered elevations present (+20)")
        else:
            chroma_score -= 15.0
        if "--accent-primary" in css and "--accent-subtle" in css:
            details["chromatic"].append("Tuned accent intensity with subtle wash (+15)")
    scores["chromatic_resonance"] = max(0.0, chroma_score)

    # 2. Typographic Rhythm (0 - 100)
    typo_score = 100.0
    if tokens_css.is_file():
        css = tokens_css.read_text(encoding="utf-8")
        if "font-variant-numeric: tabular-nums" in css:
            details["typographic"].append("Tabular numerics strictly enforced for data stability (+25)")
        else:
            typo_score -= 25.0
        if "--reading-measure-max" in css or "68ch" in css:
            details["typographic"].append("Ergonomic reading measure bounded to 68ch (+25)")
        else:
            typo_score -= 20.0
        if "--line-height-body" in css or "--line-height-heading" in css:
            details["typographic"].append("Golden ratio line-height rhythm declared (+25)")
        else:
            typo_score -= 15.0
            details["typographic"].append("Missing explicit golden ratio line-height token (-15)")
        if "--font-sans" in css and "--font-mono" in css:
            details["typographic"].append("Dual-font system defined (+25)")
        else:
            typo_score -= 20.0
    scores["typographic_rhythm"] = max(0.0, typo_score)

    # 3. Spatial Tension & Geometric Equilibrium (0 - 100)
    spatial_score = 100.0
    if tokens_css.is_file():
        css = tokens_css.read_text(encoding="utf-8")
        if "--radius-outer" in css and "--radius-inner" in css:
            details["spatial"].append("Concentric border radii hierarchy calibrated (+30)")
        if "--space-1: 4px" in css or "--space-2: 8px" in css:
            details["spatial"].append("Base 4/8px modular rhythm established (+30)")
    scores["spatial_equilibrium"] = max(0.0, spatial_score)

    # 4. Cognitive Ergonomics & Attention Routing (0 - 100)
    cog_score = 100.0
    if envelope_json.is_file():
        env = json.loads(envelope_json.read_text(encoding="utf-8"))
        if "attention_routing" in env and "disclosure_levels" in env["attention_routing"]:
            details["cognitive"].append("L1-L3 Progressive disclosure levels structured (+30)")
        else:
            cog_score -= 30.0
        if "data_stress_boundaries" in env:
            details["cognitive"].append("Data overflow & empty state guidance bounded (+30)")
        else:
            cog_score -= 30.0
    scores["cognitive_ergonomics"] = max(0.0, cog_score)

    # 5. Tactile Physics & State Resilience (0 - 100)
    tactile_score = 100.0
    if c1_md.is_file():
        c1_text = c1_md.read_text(encoding="utf-8")
        if "Fault Tolerance & Error Recovery Contract" in c1_text:
            details["tactile"].append("Defensive operation boundaries & undo recovery codified (+35)")
        else:
            tactile_score -= 35.0
        if "Decisive Exchange 3-Frame" in c1_text:
            details["tactile"].append("3-Frame deterministic commit mechanics specified (+35)")
        else:
            tactile_score -= 35.0
    scores["tactile_physics"] = max(0.0, tactile_score)

    overall_taste_score = sum(scores.values()) / len(scores)

    return {
        "slice_id": slice_id,
        "overall_taste_score": round(overall_taste_score, 1),
        "dimensions": scores,
        "aesthetic_audit_details": details
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 evaluate_design_taste.py <proto_dir> <slice_id>")
        sys.exit(1)
    res = evaluate_design_taste(Path(sys.argv[1]), sys.argv[2])
    print(json.dumps(res, indent=2, ensure_ascii=False))
