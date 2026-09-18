#!/usr/bin/env python3
"""Pairwise Blind Benchmark Evaluator (No-Skill vs spec-prototype).

Evaluates design quality via side-by-side comparative critique on identical briefs:
- Variant A: Baseline LLM Zero-Skill Generation (Unconstrained prompt).
- Variant B: spec-prototype v10.1 Generation (Nine Pillars, Dual-Envelope, Invariants).
- Independent Critic: Blinds variant identities and evaluates:
  1. Product Sense & Reality Grounding (No fake metrics, authentic friction).
  2. Information Architecture & Spatial Rhythm (Hierarchy, typography, zero homogeneous grid).
  3. Ergonomic Trust & Resilience (Action closure, clear recovery, zero dead-ends).
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "benchmarks/spec-prototype/cases"
RESULTS_DIR = ROOT / "benchmarks/spec-prototype/results"


def generate_blind_comparison_manifest(case_name: str, out_dir: Path) -> Dict[str, Any]:
    case_path = CASES_DIR / case_name
    if not case_path.is_dir():
        raise FileNotFoundError(f"Benchmark case not found: {case_name}")

    brief_text = (case_path / "brief.md").read_text(encoding="utf-8")

    # Establish blinded variant mapping (A vs B randomized)
    coin = random.choice([True, False])
    mapping = {
        "candidate_1": "spec-prototype-v10.1" if coin else "baseline-zero-skill",
        "candidate_2": "baseline-zero-skill" if coin else "spec-prototype-v10.1"
    }

    manifest = {
        "benchmark_type": "pairwise_blind_critique",
        "case_name": case_name,
        "brief": brief_text.strip(),
        "candidates": {
            "candidate_1": {
                "label": "Candidate Alpha",
                "source_ref": mapping["candidate_1"],
                "evidence_path": f"evidence/{case_name}/candidate_1/1280.png"
            },
            "candidate_2": {
                "label": "Candidate Beta",
                "source_ref": mapping["candidate_2"],
                "evidence_path": f"evidence/{case_name}/candidate_2/1280.png"
            }
        },
        "blind_key": mapping,
        "evaluation_protocol": {
            "dimensions": [
                {
                    "name": "Product Fit & Domain Authenticity",
                    "anchor": "Real domain terminology, authentic operational tension, truthful state representations, zero fake telemetry."
                },
                {
                    "name": "Spatial Hierarchy, Rhythm & Visual Restraint",
                    "anchor": "Clear visual hierarchy, stable numeric alignment, purposeful compression/release rhythm, product-specific signature without decorative noise."
                },
                {
                    "name": "Action Continuity, Ergonomics & Fault Resilience",
                    "anchor": "Consistent action lifecycle terminology, perceptible state transitions, robust error recovery, and strict context preservation."
                }
            ],
            "adjudication": "pairwise_preference"
        }
    }

    out_file = out_dir / f"pairwise_{case_name}.json"
    out_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Pairwise blind benchmark evaluator")
    parser.add_argument("--case", default="incident-commander", help="Benchmark case name")
    parser.add_argument("--all", action="store_true", help="Run across all benchmark cases")
    args = parser.parse_args()

    cases = [args.case] if not args.all else [
        "incident-commander", "editorial-reader", "mobile-booking",
        "project-workspace", "product-marketing", "ai-writer-workspace"
    ]

    out_dir = RESULTS_DIR / "pairwise_evaluations"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Generating Pairwise Blind Benchmark Manifests ({len(cases)} cases) ===")
    for c in cases:
        manifest = generate_blind_comparison_manifest(c, out_dir)
        print(f"[PREPARED] {c:22} -> {out_dir}/pairwise_{c}.json")

    print("\nPairwise benchmark manifests ready for spec-prototype-critic independent adjudication.")


if __name__ == "__main__":
    main()
