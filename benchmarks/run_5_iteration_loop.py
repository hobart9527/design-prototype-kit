#!/usr/bin/env python3
"""Run 5 continuous cycles of simulation, design taste audit, defect hunting, and verification."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "benchmarks/spec-prototype/results"

CASES = [
    "incident-commander",
    "project-workspace",
    "editorial-reader",
    "mobile-booking",
    "product-marketing",
    "ai-writer-workspace",
]

def run_5_iterations():
    print("=== Starting 5-Cycle Continuous Modern Design Optimization Loop ===")
    cycle_reports = []

    for cycle in range(1, 6):
        print(f"\n─────────────────────────────────────────────────────────────────")
        print(f"  CYCLE {cycle} / 5: Simulation & Deep Design Taste Audit")
        print(f"─────────────────────────────────────────────────────────────────")
        
        # Alternate choices to test aesthetic versatility (Cycle 1, 3, 5 -> Choice A; Cycle 2, 4 -> Choice B)
        choice = "A" if cycle % 2 != 0 else "B"
        
        # 1. Run simulation
        t0 = time.time()
        proc = subprocess.run([
            sys.executable, "benchmarks/run_authentic_simulation.py",
            "--choice", choice
        ], capture_output=True, text=True)
        dur = round(time.time() - t0, 3)

        # Locate latest result directory
        subdirs = sorted(RESULTS_DIR.glob("authentic_simulation_*"), key=lambda p: p.stat().st_mtime, reverse=True)
        latest_dir = subdirs[0]

        # 2. Evaluate design taste across all 6 cases
        case_scores = {}
        for c in CASES:
            case_subdirs = list(latest_dir.glob(f"{c}_choice_*"))
            if case_subdirs:
                proto_dir = case_subdirs[0] / "prototype"
                eval_proc = subprocess.run([
                    sys.executable, "benchmarks/evaluate_design_taste.py",
                    str(proto_dir), c
                ], capture_output=True, text=True)
                try:
                    res_taste = json.loads(eval_proc.stdout)
                    case_scores[c] = res_taste["overall_taste_score"]
                except Exception:
                    case_scores[c] = 0.0

        avg_taste = sum(case_scores.values()) / len(case_scores) if case_scores else 0.0
        print(f"  Cycle {cycle} complete in {dur}s | Choice: Option {choice} | Avg Design Taste Score: {avg_taste:.1f} / 100")
        for c, s in case_scores.items():
            print(f"    - {c:22}: Taste Score = {s:.1f}")

        cycle_reports.append({
            "cycle": cycle,
            "choice": choice,
            "duration_s": dur,
            "avg_taste_score": avg_taste,
            "case_scores": case_scores,
            "results_dir": str(latest_dir)
        })

    summary_file = RESULTS_DIR / "5_cycle_optimization_summary.json"
    summary_file.write_text(json.dumps(cycle_reports, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n=== 5-Cycle Optimization Loop Completed. Summary saved to: {summary_file} ===")
    return cycle_reports

if __name__ == "__main__":
    run_5_iterations()
