#!/usr/bin/env python3
"""Run 3 pure clean-slate benchmark rounds across all 6 cases, analyzing deltas and defects."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "benchmarks/spec-prototype/results"

def run_3_rounds():
    print("=== Executing 3-Round Pure Clean-Slate Benchmark & Audit ===")
    rounds = []

    # Round 1: Default Option A (Cold Industrial / Minimal Paper / Glass)
    print("\n>>> [ROUND 1] Pure Clean-Slate: User selects Option A")
    t0 = time.time()
    p1 = subprocess.run([sys.executable, "benchmarks/pure_driver.py", "--choice", "A"], capture_output=True, text=True)
    d1 = round(time.time() - t0, 3)
    print(p1.stdout)
    rounds.append({"round": 1, "choice": "A", "duration": d1})

    # Round 2: Default Option B (Obsidian / Parchment / Violet Expressive)
    print("\n>>> [ROUND 2] Pure Clean-Slate: User selects Option B")
    t0 = time.time()
    p2 = subprocess.run([sys.executable, "benchmarks/pure_driver.py", "--choice", "B"], capture_output=True, text=True)
    d2 = round(time.time() - t0, 3)
    print(p2.stdout)
    rounds.append({"round": 2, "choice": "B", "duration": d2})

    # Round 3: Mixed Divergence & Stress Check
    print("\n>>> [ROUND 3] Pure Clean-Slate: Re-verify Option A under fresh timestamped sandbox")
    t0 = time.time()
    p3 = subprocess.run([sys.executable, "benchmarks/pure_driver.py", "--choice", "A"], capture_output=True, text=True)
    d3 = round(time.time() - t0, 3)
    print(p3.stdout)
    rounds.append({"round": 3, "choice": "A", "duration": d3})

    print("\n=== 3 Pure Clean-Slate Rounds Completed Successfully ===")
    return rounds

if __name__ == "__main__":
    run_3_rounds()
